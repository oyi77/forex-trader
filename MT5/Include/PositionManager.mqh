//+------------------------------------------------------------------+
//|                                           PositionManager.mqh   |
//|                                    Copyright 2025, oyi77        |
//|                      https://github.com/oyi77/forex-trader      |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, oyi77"
#property link      "https://github.com/oyi77/forex-trader"

#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| Position Management Class                                        |
//+------------------------------------------------------------------+
class CPositionManager
{
private:
    CTrade            m_trade;
    int               m_magicNumber;
    double            m_slippage;
    string            m_tradeComment;
    
    // Position tracking
    struct PositionInfo
    {
        ulong          ticket;
        double         maxProfit;
        double         maxLoss;
        datetime       openTime;
        string         strategy;
        double         confidence;
        bool           trailingActive;
    };
    
    PositionInfo      m_positions[];
    
    // Trailing stop settings
    bool              m_useTrailingStop;
    double            m_trailingStopPips;
    double            m_trailingStepPips;
    
    // Partial close settings
    bool              m_usePartialClose;
    double            m_partialClosePercent;
    double            m_partialCloseProfitPips;

public:
    //--- Constructor
    CPositionManager(int magicNumber, double slippage, string tradeComment)
    {
        m_magicNumber = magicNumber;
        m_slippage = slippage;
        m_tradeComment = tradeComment;
        
        m_trade.SetExpertMagicNumber(m_magicNumber);
        m_trade.SetDeviationInPoints((int)(m_slippage * 10));
        m_trade.SetTypeFilling(ORDER_FILLING_FOK);
        
        // Default settings
        m_useTrailingStop = true;
        m_trailingStopPips = 30.0;
        m_trailingStepPips = 10.0;
        
        m_usePartialClose = true;
        m_partialClosePercent = 50.0;
        m_partialCloseProfitPips = 50.0;
        
        ArrayResize(m_positions, 0);
    }
    
    //--- Set trailing stop parameters
    void SetTrailingStop(bool enable, double trailingPips, double stepPips)
    {
        m_useTrailingStop = enable;
        m_trailingStopPips = trailingPips;
        m_trailingStepPips = stepPips;
    }
    
    //--- Set partial close parameters
    void SetPartialClose(bool enable, double percent, double profitPips)
    {
        m_usePartialClose = enable;
        m_partialClosePercent = percent;
        m_partialCloseProfitPips = profitPips;
    }
    
    //--- Open position with advanced management
    bool OpenPosition(ENUM_ORDER_TYPE orderType, double lotSize, double stopLoss, 
                     double takeProfit, string strategy, double confidence, string symbol = "")
    {
        if(symbol == "") symbol = _Symbol;
        
        double price = (orderType == ORDER_TYPE_BUY) ? 
                       SymbolInfoDouble(symbol, SYMBOL_ASK) : 
                       SymbolInfoDouble(symbol, SYMBOL_BID);
        
        string comment = StringFormat("%s|%s|Conf:%.2f", m_tradeComment, strategy, confidence);
        
        if(m_trade.PositionOpen(symbol, orderType, lotSize, price, stopLoss, takeProfit, comment))
        {
            ulong ticket = m_trade.ResultOrder();
            AddPositionToTracking(ticket, strategy, confidence);
            
            Print("Position opened: ", strategy, " | Ticket: ", ticket, 
                  " | Type: ", EnumToString(orderType), " | Lots: ", lotSize, 
                  " | Confidence: ", confidence);
            
            return true;
        }
        else
        {
            Print("Failed to open position: ", m_trade.ResultRetcode(), 
                  " - ", m_trade.ResultRetcodeDescription());
            return false;
        }
    }
    
    //--- Manage all positions
    void ManageAllPositions()
    {
        UpdatePositionTracking();
        
        for(int i = ArraySize(m_positions) - 1; i >= 0; i--)
        {
            if(PositionSelectByTicket(m_positions[i].ticket))
            {
                ManagePosition(i);
            }
            else
            {
                // Position closed, remove from tracking
                RemovePositionFromTracking(i);
            }
        }
    }
    
    //--- Close all positions
    void CloseAllPositions(string reason = "")
    {
        for(int i = ArraySize(m_positions) - 1; i >= 0; i--)
        {
            if(PositionSelectByTicket(m_positions[i].ticket))
            {
                m_trade.PositionClose(m_positions[i].ticket);
            }
        }
        
        ArrayResize(m_positions, 0);
        
        if(reason != "")
            Print("All positions closed: ", reason);
    }
    
    //--- Close positions by strategy
    void ClosePositionsByStrategy(string strategy)
    {
        for(int i = ArraySize(m_positions) - 1; i >= 0; i--)
        {
            if(m_positions[i].strategy == strategy)
            {
                if(PositionSelectByTicket(m_positions[i].ticket))
                {
                    m_trade.PositionClose(m_positions[i].ticket);
                }
                RemovePositionFromTracking(i);
            }
        }
    }
    
    //--- Get positions count
    int GetPositionsCount()
    {
        return ArraySize(m_positions);
    }
    
    //--- Get positions count by strategy
    int GetPositionsCountByStrategy(string strategy)
    {
        int count = 0;
        for(int i = 0; i < ArraySize(m_positions); i++)
        {
            if(m_positions[i].strategy == strategy)
                count++;
        }
        return count;
    }
    
    //--- Get total profit
    double GetTotalProfit()
    {
        double totalProfit = 0.0;
        for(int i = 0; i < ArraySize(m_positions); i++)
        {
            if(PositionSelectByTicket(m_positions[i].ticket))
            {
                totalProfit += PositionGetDouble(POSITION_PROFIT);
            }
        }
        return totalProfit;
    }
    
    //--- Get floating profit/loss
    double GetFloatingPL()
    {
        return GetTotalProfit();
    }
    
    //--- Check if symbol has open positions
    bool HasOpenPosition(string symbol = "")
    {
        if(symbol == "") symbol = _Symbol;
        
        for(int i = 0; i < ArraySize(m_positions); i++)
        {
            if(PositionSelectByTicket(m_positions[i].ticket))
            {
                if(PositionGetString(POSITION_SYMBOL) == symbol)
                    return true;
            }
        }
        return false;
    }
    
    //--- Get position statistics
    void PrintPositionStatistics()
    {
        int totalPositions = ArraySize(m_positions);
        double totalProfit = GetTotalProfit();
        
        Print("=== POSITION STATISTICS ===");
        Print("Total Positions: ", totalPositions);
        Print("Total Floating P/L: ", totalProfit);
        
        // Count by strategy
        string strategies[];
        int strategyCounts[];
        
        for(int i = 0; i < totalPositions; i++)
        {
            string strategy = m_positions[i].strategy;
            bool found = false;
            
            for(int j = 0; j < ArraySize(strategies); j++)
            {
                if(strategies[j] == strategy)
                {
                    strategyCounts[j]++;
                    found = true;
                    break;
                }
            }
            
            if(!found)
            {
                ArrayResize(strategies, ArraySize(strategies) + 1);
                ArrayResize(strategyCounts, ArraySize(strategyCounts) + 1);
                strategies[ArraySize(strategies) - 1] = strategy;
                strategyCounts[ArraySize(strategyCounts) - 1] = 1;
            }
        }
        
        for(int i = 0; i < ArraySize(strategies); i++)
        {
            Print(strategies[i], ": ", strategyCounts[i], " positions");
        }
        
        Print("===========================");
    }

private:
    //--- Add position to tracking
    void AddPositionToTracking(ulong ticket, string strategy, double confidence)
    {
        int size = ArraySize(m_positions);
        ArrayResize(m_positions, size + 1);
        
        m_positions[size].ticket = ticket;
        m_positions[size].maxProfit = 0.0;
        m_positions[size].maxLoss = 0.0;
        m_positions[size].openTime = TimeCurrent();
        m_positions[size].strategy = strategy;
        m_positions[size].confidence = confidence;
        m_positions[size].trailingActive = false;
    }
    
    //--- Remove position from tracking
    void RemovePositionFromTracking(int index)
    {
        int size = ArraySize(m_positions);
        if(index < 0 || index >= size) return;
        
        for(int i = index; i < size - 1; i++)
        {
            m_positions[i] = m_positions[i + 1];
        }
        
        ArrayResize(m_positions, size - 1);
    }
    
    //--- Update position tracking data
    void UpdatePositionTracking()
    {
        for(int i = 0; i < ArraySize(m_positions); i++)
        {
            if(PositionSelectByTicket(m_positions[i].ticket))
            {
                double currentProfit = PositionGetDouble(POSITION_PROFIT);
                
                // Update max profit
                if(currentProfit > m_positions[i].maxProfit)
                    m_positions[i].maxProfit = currentProfit;
                
                // Update max loss
                if(currentProfit < m_positions[i].maxLoss)
                    m_positions[i].maxLoss = currentProfit;
            }
        }
    }
    
    //--- Manage individual position
    void ManagePosition(int index)
    {
        if(!PositionSelectByTicket(m_positions[index].ticket))
            return;
        
        double currentProfit = PositionGetDouble(POSITION_PROFIT);
        double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
        ENUM_POSITION_TYPE posType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
        string symbol = PositionGetString(POSITION_SYMBOL);
        
        // Partial close management
        if(m_usePartialClose && !m_positions[index].trailingActive)
        {
            CheckPartialClose(index, currentProfit, openPrice, posType, symbol);
        }
        
        // Trailing stop management
        if(m_useTrailingStop)
        {
            UpdateTrailingStop(index, openPrice, posType, symbol);
        }
        
        // Strategy-specific management
        CheckStrategySpecificRules(index, currentProfit);
    }
    
    //--- Check for partial close
    void CheckPartialClose(int index, double currentProfit, double openPrice, 
                          ENUM_POSITION_TYPE posType, string symbol)
    {
        double currentPrice = (posType == POSITION_TYPE_BUY) ? 
                             SymbolInfoDouble(symbol, SYMBOL_BID) : 
                             SymbolInfoDouble(symbol, SYMBOL_ASK);
        
        double pipSize = SymbolInfoDouble(symbol, SYMBOL_POINT) * 10;
        double profitPips = MathAbs(currentPrice - openPrice) / pipSize;
        
        if(profitPips >= m_partialCloseProfitPips && currentProfit > 0)
        {
            double currentLots = PositionGetDouble(POSITION_VOLUME);
            double closeLots = currentLots * (m_partialClosePercent / 100.0);
            
            // Normalize close lots
            double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
            double lotStep = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
            closeLots = MathMax(minLot, MathRound(closeLots / lotStep) * lotStep);
            
            if(closeLots < currentLots)
            {
                if(m_trade.PositionClosePartial(m_positions[index].ticket, closeLots))
                {
                    m_positions[index].trailingActive = true;
                    Print("Partial close executed: ", closeLots, " lots at ", profitPips, " pips profit");
                }
            }
        }
    }
    
    //--- Update trailing stop
    void UpdateTrailingStop(int index, double openPrice, ENUM_POSITION_TYPE posType, string symbol)
    {
        double currentPrice = (posType == POSITION_TYPE_BUY) ? 
                             SymbolInfoDouble(symbol, SYMBOL_BID) : 
                             SymbolInfoDouble(symbol, SYMBOL_ASK);
        
        double currentSL = PositionGetDouble(POSITION_SL);
        double currentTP = PositionGetDouble(POSITION_TP);
        
        double pipSize = SymbolInfoDouble(symbol, SYMBOL_POINT) * 10;
        double trailDistance = m_trailingStopPips * pipSize;
        double stepDistance = m_trailingStepPips * pipSize;
        
        double newSL = 0;
        bool updateSL = false;
        
        if(posType == POSITION_TYPE_BUY)
        {
            newSL = currentPrice - trailDistance;
            
            // Only update if new SL is better and moves by step distance
            if(newSL > currentSL && (newSL - currentSL) >= stepDistance && newSL > openPrice)
            {
                updateSL = true;
            }
        }
        else // SELL position
        {
            newSL = currentPrice + trailDistance;
            
            // Only update if new SL is better and moves by step distance
            if((newSL < currentSL || currentSL == 0) && 
               (currentSL == 0 || (currentSL - newSL) >= stepDistance) && 
               newSL < openPrice)
            {
                updateSL = true;
            }
        }
        
        if(updateSL)
        {
            if(m_trade.PositionModify(m_positions[index].ticket, newSL, currentTP))
            {
                Print("Trailing stop updated: Ticket ", m_positions[index].ticket, 
                      " | New SL: ", newSL);
            }
        }
    }
    
    //--- Check if symbol is a mini contract
    bool IsMiniContract(string symbol)
    {
        if(symbol == "")
            symbol = _Symbol;
        
        // Check for 'm' suffix indicating mini contract
        if(StringFind(symbol, "m") >= 0 && StringLen(symbol) > 0)
        {
            string baseSymbol = StringSubstr(symbol, 0, StringLen(symbol) - 1);
            // Verify it's a valid mini contract by checking if base symbol exists
            if(SymbolInfoInteger(baseSymbol, SYMBOL_SELECT))
                return true;
        }
        
        return false;
    }
    
    //--- Get base symbol from mini contract
    string GetBaseSymbol(string symbol)
    {
        if(symbol == "")
            symbol = _Symbol;
        
        if(IsMiniContract(symbol))
        {
            return StringSubstr(symbol, 0, StringLen(symbol) - 1);
        }
        
        return symbol;
    }
    
    //--- Check strategy-specific rules
    void CheckStrategySpecificRules(int index, double currentProfit)
    {
        string strategy = m_positions[index].strategy;
        
        // Get symbol for mini contract adjustments
        string symbol = "";
        if(PositionSelectByTicket(m_positions[index].ticket))
        {
            symbol = PositionGetString(POSITION_SYMBOL);
        }
        
        // Mini contract adjustments
        double profitThreshold = 10.0;
        double lossThreshold = -50.0;
        
        if(IsMiniContract(symbol))
        {
            // Mini contracts have lower risk, so adjust thresholds
            profitThreshold *= 0.5; // Lower profit threshold for mini contracts
            lossThreshold *= 0.5;   // Lower loss threshold for mini contracts
        }
        
        // Scalping strategy - quick profit taking
        if(StringFind(strategy, "Scalp") >= 0)
        {
            if(currentProfit > 0)
            {
                // Close scalping positions quickly when profitable
                if(currentProfit > profitThreshold)
                {
                    m_trade.PositionClose(m_positions[index].ticket);
                    Print("Scalping position closed at profit: ", currentProfit, 
                          " | Symbol: ", symbol, " | Mini: ", IsMiniContract(symbol));
                }
            }
        }
        
        // News strategy - quick exit on reversal
        if(StringFind(strategy, "News") >= 0)
        {
            // Close news positions if they turn negative quickly
            if(currentProfit < lossThreshold)
            {
                m_trade.PositionClose(m_positions[index].ticket);
                Print("News position closed at loss: ", currentProfit,
                      " | Symbol: ", symbol, " | Mini: ", IsMiniContract(symbol));
            }
        }
        
        // RSI strategy - hold for reversal
        if(StringFind(strategy, "RSI") >= 0)
        {
            // RSI positions can be held longer for reversal
            // No special exit rules for now
        }
        
        // Breakout strategy - momentum continuation
        if(StringFind(strategy, "Breakout") >= 0)
        {
            // Let breakout positions run with trailing stops
            // No special exit rules for now
        }
    }
};

//+------------------------------------------------------------------+

