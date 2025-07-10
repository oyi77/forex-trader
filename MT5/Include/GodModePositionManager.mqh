//+------------------------------------------------------------------+
//|                                   GodModePositionManager.mqh    |
//|                                    Copyright 2025, oyi77        |
//|                      https://github.com/oyi77/forex-trader      |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, oyi77"
#property link      "https://github.com/oyi77/forex-trader"
#property version   "1.00"

#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| Position Information Structure                                   |
//+------------------------------------------------------------------+
struct PositionData
{
    ulong             ticket;
    string            symbol;
    string            strategy;
    ENUM_POSITION_TYPE type;
    double            volume;
    double            openPrice;
    double            currentPrice;
    double            stopLoss;
    double            takeProfit;
    double            profit;
    datetime          openTime;
    double            confidence;
    bool              trailingActive;
    double            trailingStop;
    double            highestPrice;
    double            lowestPrice;
    bool              partialClosed;
    double            originalVolume;
    int               holdTime;
    double            maxProfit;
    double            maxLoss;
};

//+------------------------------------------------------------------+
//| God Mode Position Manager Class                                 |
//| Advanced position management for extreme trading strategies     |
//+------------------------------------------------------------------+
class CGodModePositionManager
{
private:
    CTrade            m_trade;
    int               m_magicNumber;
    string            m_tradeComment;
    double            m_slippage;
    
    // Position tracking
    PositionData      m_positions[];
    int               m_positionCount;
    double            m_totalProfit;
    double            m_totalLoss;
    double            m_totalVolume;
    
    // Trailing stop settings
    bool              m_useTrailingStop;
    double            m_trailingStopPips;
    double            m_trailingStepPips;
    double            m_trailingStartPips;
    
    // Partial close settings
    bool              m_usePartialClose;
    double            m_partialClosePercent;
    double            m_partialCloseProfitPips;
    double            m_partialCloseLevel2Percent;
    double            m_partialCloseLevel2Pips;
    
    // Time-based management
    bool              m_useTimeBasedExit;
    int               m_maxHoldTimeSeconds;
    int               m_scalpMaxHoldTime;
    
    // Profit protection
    bool              m_useProfitProtection;
    double            m_profitProtectionLevel;
    double            m_profitProtectionTrail;
    
    // Correlation management
    bool              m_useCorrelationFilter;
    double            m_maxCorrelation;
    
    // Statistics
    int               m_totalTrades;
    int               m_winningTrades;
    int               m_losingTrades;
    double            m_largestWin;
    double            m_largestLoss;
    double            m_averageWin;
    double            m_averageLoss;
    
public:
    //--- Constructor
    CGodModePositionManager(int magicNumber, double slippage, string comment)
    {
        m_magicNumber = magicNumber;
        m_slippage = slippage;
        m_tradeComment = comment;
        
        m_trade.SetExpertMagicNumber(magicNumber);
        m_trade.SetDeviationInPoints((int)(slippage * 10));
        m_trade.SetTypeFilling(ORDER_FILLING_FOK);
        
        // Initialize arrays
        ArrayResize(m_positions, 100);
        m_positionCount = 0;
        
        // Initialize counters
        m_totalProfit = 0.0;
        m_totalLoss = 0.0;
        m_totalVolume = 0.0;
        
        // Default settings
        m_useTrailingStop = true;
        m_trailingStopPips = 10.0;
        m_trailingStepPips = 5.0;
        m_trailingStartPips = 15.0;
        
        m_usePartialClose = true;
        m_partialClosePercent = 50.0;
        m_partialCloseProfitPips = 20.0;
        m_partialCloseLevel2Percent = 25.0;
        m_partialCloseLevel2Pips = 40.0;
        
        m_useTimeBasedExit = true;
        m_maxHoldTimeSeconds = 3600; // 1 hour
        m_scalpMaxHoldTime = 300;    // 5 minutes for scalping
        
        m_useProfitProtection = true;
        m_profitProtectionLevel = 30.0; // Protect after 30 pips profit
        m_profitProtectionTrail = 10.0; // Trail by 10 pips
        
        m_useCorrelationFilter = true;
        m_maxCorrelation = 0.8;
        
        // Initialize statistics
        m_totalTrades = 0;
        m_winningTrades = 0;
        m_losingTrades = 0;
        m_largestWin = 0.0;
        m_largestLoss = 0.0;
        m_averageWin = 0.0;
        m_averageLoss = 0.0;
        
        Print("God Mode Position Manager initialized");
    }
    
    //--- Destructor
    ~CGodModePositionManager() {}
    
    //+------------------------------------------------------------------+
    //| Set trailing stop parameters                                    |
    //+------------------------------------------------------------------+
    void SetTrailingStop(bool enabled, double stopPips, double stepPips, double startPips = 0)
    {
        m_useTrailingStop = enabled;
        m_trailingStopPips = stopPips;
        m_trailingStepPips = stepPips;
        if(startPips > 0)
            m_trailingStartPips = startPips;
        
        Print("Trailing stop configured: ", enabled ? "ENABLED" : "DISABLED", 
              " | Stop: ", stopPips, " | Step: ", stepPips, " | Start: ", m_trailingStartPips);
    }
    
    //+------------------------------------------------------------------+
    //| Set partial close parameters                                    |
    //+------------------------------------------------------------------+
    void SetPartialClose(bool enabled, double percent1, double pips1, double percent2 = 0, double pips2 = 0)
    {
        m_usePartialClose = enabled;
        m_partialClosePercent = percent1;
        m_partialCloseProfitPips = pips1;
        
        if(percent2 > 0 && pips2 > 0)
        {
            m_partialCloseLevel2Percent = percent2;
            m_partialCloseLevel2Pips = pips2;
        }
        
        Print("Partial close configured: ", enabled ? "ENABLED" : "DISABLED", 
              " | Level 1: ", percent1, "% at ", pips1, " pips");
    }
    
    //+------------------------------------------------------------------+
    //| Set time-based exit parameters                                  |
    //+------------------------------------------------------------------+
    void SetTimeBasedExit(bool enabled, int maxHoldSeconds, int scalpHoldSeconds = 0)
    {
        m_useTimeBasedExit = enabled;
        m_maxHoldTimeSeconds = maxHoldSeconds;
        if(scalpHoldSeconds > 0)
            m_scalpMaxHoldTime = scalpHoldSeconds;
        
        Print("Time-based exit configured: ", enabled ? "ENABLED" : "DISABLED", 
              " | Max hold: ", maxHoldSeconds, "s | Scalp: ", m_scalpMaxHoldTime, "s");
    }
    
    //+------------------------------------------------------------------+
    //| Open new position                                               |
    //+------------------------------------------------------------------+
    bool OpenPosition(ENUM_ORDER_TYPE orderType, double volume, double stopLoss, 
                     double takeProfit, string strategy, double confidence, string symbol = "")
    {
        if(symbol == "")
            symbol = _Symbol;
        
        // Check correlation if enabled
        if(m_useCorrelationFilter && !CheckCorrelation(symbol, orderType))
        {
            Print("Position rejected due to correlation limit: ", symbol);
            return false;
        }
        
        // Prepare trade request
        MqlTradeRequest request = {};
        MqlTradeResult result = {};
        
        double price = (orderType == ORDER_TYPE_BUY) ? 
                       SymbolInfoDouble(symbol, SYMBOL_ASK) : 
                       SymbolInfoDouble(symbol, SYMBOL_BID);
        
        request.action = TRADE_ACTION_DEAL;
        request.symbol = symbol;
        request.volume = volume;
        request.type = orderType;
        request.price = price;
        request.sl = stopLoss;
        request.tp = takeProfit;
        request.deviation = (int)(m_slippage * 10);
        request.magic = m_magicNumber;
        request.comment = StringFormat("%s_%s_%.0f%%", m_tradeComment, strategy, confidence);
        
        // Send order
        if(OrderSend(request, result))
        {
            if(result.retcode == TRADE_RETCODE_DONE)
            {
                // Add to position tracking
                AddPositionToTracking(result.deal, symbol, strategy, orderType, volume, 
                                    price, stopLoss, takeProfit, confidence);
                
                Print("Position opened: ", symbol, " | ", EnumToString(orderType), 
                      " | Volume: ", volume, " | Strategy: ", strategy, 
                      " | Confidence: ", confidence, "%");
                
                return true;
            }
            else
            {
                Print("Order failed: ", result.retcode, " - ", result.comment);
            }
        }
        
        return false;
    }
    
    //+------------------------------------------------------------------+
    //| Manage all positions                                            |
    //+------------------------------------------------------------------+
    void ManageAllPositions()
    {
        UpdatePositionData();
        
        for(int i = 0; i < m_positionCount; i++)
        {
            if(m_positions[i].ticket > 0)
            {
                ManagePosition(i);
            }
        }
        
        // Clean up closed positions
        CleanupClosedPositions();
    }
    
    //+------------------------------------------------------------------+
    //| Close all positions                                             |
    //+------------------------------------------------------------------+
    void CloseAllPositions(string reason = "Manual close")
    {
        Print("Closing all positions - Reason: ", reason);
        
        for(int i = PositionsTotal() - 1; i >= 0; i--)
        {
            if(PositionGetSymbol(i) != "" && PositionGetInteger(POSITION_MAGIC) == m_magicNumber)
            {
                ulong ticket = PositionGetInteger(POSITION_TICKET);
                m_trade.PositionClose(ticket);
            }
        }
        
        // Clear tracking
        m_positionCount = 0;
        // Reset all position data manually (ArrayInitialize doesn't work with structs)
        for(int i = 0; i < ArraySize(m_positions); i++)
        {
            m_positions[i].ticket = 0;
            m_positions[i].symbol = "";
            m_positions[i].strategy = "";
            m_positions[i].type = POSITION_TYPE_BUY;
            m_positions[i].volume = 0.0;
            m_positions[i].openPrice = 0.0;
            m_positions[i].currentPrice = 0.0;
            m_positions[i].stopLoss = 0.0;
            m_positions[i].takeProfit = 0.0;
            m_positions[i].profit = 0.0;
            m_positions[i].openTime = 0;
            m_positions[i].confidence = 0.0;
            m_positions[i].trailingActive = false;
            m_positions[i].trailingStop = 0.0;
            m_positions[i].highestPrice = 0.0;
            m_positions[i].lowestPrice = 0.0;
            m_positions[i].partialClosed = false;
            m_positions[i].originalVolume = 0.0;
            m_positions[i].holdTime = 0;
            m_positions[i].maxProfit = 0.0;
            m_positions[i].maxLoss = 0.0;
        }
    }
    
    //+------------------------------------------------------------------+
    //| Close positions by strategy                                     |
    //+------------------------------------------------------------------+
    void ClosePositionsByStrategy(string strategy, string reason = "Strategy close")
    {
        Print("Closing positions for strategy: ", strategy, " - Reason: ", reason);
        
        for(int i = 0; i < m_positionCount; i++)
        {
            if(m_positions[i].ticket > 0 && m_positions[i].strategy == strategy)
            {
                m_trade.PositionClose(m_positions[i].ticket);
            }
        }
    }
    
    //+------------------------------------------------------------------+
    //| Get total positions count                                       |
    //+------------------------------------------------------------------+
    int GetPositionsCount()
    {
        int count = 0;
        for(int i = 0; i < PositionsTotal(); i++)
        {
            if(PositionGetSymbol(i) != "" && PositionGetInteger(POSITION_MAGIC) == m_magicNumber)
                count++;
        }
        return count;
    }
    
    //+------------------------------------------------------------------+
    //| Get positions count by strategy                                 |
    //+------------------------------------------------------------------+
    int GetPositionsCountByStrategy(string strategy)
    {
        int count = 0;
        for(int i = 0; i < m_positionCount; i++)
        {
            if(m_positions[i].ticket > 0 && m_positions[i].strategy == strategy)
                count++;
        }
        return count;
    }
    
    //+------------------------------------------------------------------+
    //| Get total profit                                                |
    //+------------------------------------------------------------------+
    double GetTotalProfit()
    {
        double totalProfit = 0.0;
        for(int i = 0; i < PositionsTotal(); i++)
        {
            if(PositionGetSymbol(i) != "" && PositionGetInteger(POSITION_MAGIC) == m_magicNumber)
            {
                totalProfit += PositionGetDouble(POSITION_PROFIT);
            }
        }
        return totalProfit;
    }
    
    //+------------------------------------------------------------------+
    //| Get total volume                                                |
    //+------------------------------------------------------------------+
    double GetTotalVolume()
    {
        double totalVolume = 0.0;
        for(int i = 0; i < PositionsTotal(); i++)
        {
            if(PositionGetSymbol(i) != "" && PositionGetInteger(POSITION_MAGIC) == m_magicNumber)
            {
                totalVolume += PositionGetDouble(POSITION_VOLUME);
            }
        }
        return totalVolume;
    }
    
    //+------------------------------------------------------------------+
    //| Print position statistics                                       |
    //+------------------------------------------------------------------+
    void PrintPositionStatistics()
    {
        Print("=== POSITION MANAGER STATISTICS ===");
        Print("Total Trades: ", m_totalTrades);
        Print("Winning Trades: ", m_winningTrades);
        Print("Losing Trades: ", m_losingTrades);
        Print("Win Rate: ", (m_totalTrades > 0) ? (double)m_winningTrades / m_totalTrades * 100 : 0, "%");
        Print("Largest Win: ", m_largestWin);
        Print("Largest Loss: ", m_largestLoss);
        Print("Average Win: ", m_averageWin);
        Print("Average Loss: ", m_averageLoss);
        Print("Current Positions: ", GetPositionsCount());
        Print("Total Profit: ", GetTotalProfit());
        Print("Total Volume: ", GetTotalVolume());
        Print("==================================");
    }
    
private:
    //+------------------------------------------------------------------+
    //| Add position to tracking system                                 |
    //+------------------------------------------------------------------+
    void AddPositionToTracking(ulong ticket, string symbol, string strategy, 
                              ENUM_ORDER_TYPE orderType, double volume, double openPrice,
                              double stopLoss, double takeProfit, double confidence)
    {
        // Find empty slot or resize array
        int index = -1;
        for(int i = 0; i < m_positionCount; i++)
        {
            if(m_positions[i].ticket == 0)
            {
                index = i;
                break;
            }
        }
        
        if(index == -1)
        {
            if(m_positionCount >= ArraySize(m_positions))
                ArrayResize(m_positions, ArraySize(m_positions) + 50);
            index = m_positionCount;
            m_positionCount++;
        }
        
        // Fill position data
        m_positions[index].ticket = ticket;
        m_positions[index].symbol = symbol;
        m_positions[index].strategy = strategy;
        m_positions[index].type = (orderType == ORDER_TYPE_BUY) ? POSITION_TYPE_BUY : POSITION_TYPE_SELL;
        m_positions[index].volume = volume;
        m_positions[index].openPrice = openPrice;
        m_positions[index].currentPrice = openPrice;
        m_positions[index].stopLoss = stopLoss;
        m_positions[index].takeProfit = takeProfit;
        m_positions[index].profit = 0.0;
        m_positions[index].openTime = TimeCurrent();
        m_positions[index].confidence = confidence;
        m_positions[index].trailingActive = false;
        m_positions[index].trailingStop = stopLoss;
        m_positions[index].highestPrice = openPrice;
        m_positions[index].lowestPrice = openPrice;
        m_positions[index].partialClosed = false;
        m_positions[index].originalVolume = volume;
        m_positions[index].holdTime = 0;
        m_positions[index].maxProfit = 0.0;
        m_positions[index].maxLoss = 0.0;
    }
    
    //+------------------------------------------------------------------+
    //| Update position data from market                                |
    //+------------------------------------------------------------------+
    void UpdatePositionData()
    {
        for(int i = 0; i < m_positionCount; i++)
        {
            if(m_positions[i].ticket > 0)
            {
                if(PositionSelectByTicket(m_positions[i].ticket))
                {
                    m_positions[i].currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
                    m_positions[i].profit = PositionGetDouble(POSITION_PROFIT);
                    m_positions[i].volume = PositionGetDouble(POSITION_VOLUME);
                    m_positions[i].stopLoss = PositionGetDouble(POSITION_SL);
                    m_positions[i].takeProfit = PositionGetDouble(POSITION_TP);
                    
                    // Update price extremes
                    if(m_positions[i].currentPrice > m_positions[i].highestPrice)
                        m_positions[i].highestPrice = m_positions[i].currentPrice;
                    if(m_positions[i].currentPrice < m_positions[i].lowestPrice)
                        m_positions[i].lowestPrice = m_positions[i].currentPrice;
                    
                    // Update profit extremes
                    if(m_positions[i].profit > m_positions[i].maxProfit)
                        m_positions[i].maxProfit = m_positions[i].profit;
                    if(m_positions[i].profit < m_positions[i].maxLoss)
                        m_positions[i].maxLoss = m_positions[i].profit;
                    
                    // Update hold time
                    m_positions[i].holdTime = (int)(TimeCurrent() - m_positions[i].openTime);
                }
                else
                {
                    // Position closed, record statistics
                    RecordClosedPosition(i);
                    m_positions[i].ticket = 0; // Mark as closed
                }
            }
        }
    }
    
    //+------------------------------------------------------------------+
    //| Manage individual position                                      |
    //+------------------------------------------------------------------+
    void ManagePosition(int index)
    {
        if(m_positions[index].ticket == 0)
            return;
        
        // Time-based exit
        if(m_useTimeBasedExit)
            CheckTimeBasedExit(index);
        
        // Trailing stop
        if(m_useTrailingStop)
            UpdateTrailingStop(index);
        
        // Partial close
        if(m_usePartialClose && !m_positions[index].partialClosed)
            CheckPartialClose(index);
        
        // Profit protection
        if(m_useProfitProtection)
            CheckProfitProtection(index);
    }
    
    //+------------------------------------------------------------------+
    //| Check time-based exit                                          |
    //+------------------------------------------------------------------+
    void CheckTimeBasedExit(int index)
    {
        int maxHoldTime = m_maxHoldTimeSeconds;
        
        // Use shorter time for scalping strategies
        if(StringFind(m_positions[index].strategy, "Scalp") >= 0 || 
           StringFind(m_positions[index].strategy, "God_Mode") >= 0)
        {
            maxHoldTime = m_scalpMaxHoldTime;
        }
        
        if(m_positions[index].holdTime > maxHoldTime)
        {
            Print("Closing position by time: ", m_positions[index].ticket, 
                  " | Hold time: ", m_positions[index].holdTime, "s");
            m_trade.PositionClose(m_positions[index].ticket);
        }
    }
    
    //+------------------------------------------------------------------+
    //| Update trailing stop                                           |
    //+------------------------------------------------------------------+
    void UpdateTrailingStop(int index)
    {
        double pipSize = SymbolInfoDouble(m_positions[index].symbol, SYMBOL_POINT) * 10;
        double trailDistance = m_trailingStopPips * pipSize;
        double stepDistance = m_trailingStepPips * pipSize;
        double startDistance = m_trailingStartPips * pipSize;
        
        double newSL = 0;
        bool shouldUpdate = false;
        
        if(m_positions[index].type == POSITION_TYPE_BUY)
        {
            // Check if we should start trailing
            if(!m_positions[index].trailingActive)
            {
                if(m_positions[index].currentPrice >= m_positions[index].openPrice + startDistance)
                {
                    m_positions[index].trailingActive = true;
                    m_positions[index].trailingStop = m_positions[index].currentPrice - trailDistance;
                }
            }
            
            if(m_positions[index].trailingActive)
            {
                newSL = m_positions[index].currentPrice - trailDistance;
                
                if(newSL > m_positions[index].trailingStop + stepDistance)
                {
                    shouldUpdate = true;
                    m_positions[index].trailingStop = newSL;
                }
            }
        }
        else // SELL position
        {
            // Check if we should start trailing
            if(!m_positions[index].trailingActive)
            {
                if(m_positions[index].currentPrice <= m_positions[index].openPrice - startDistance)
                {
                    m_positions[index].trailingActive = true;
                    m_positions[index].trailingStop = m_positions[index].currentPrice + trailDistance;
                }
            }
            
            if(m_positions[index].trailingActive)
            {
                newSL = m_positions[index].currentPrice + trailDistance;
                
                if(newSL < m_positions[index].trailingStop - stepDistance)
                {
                    shouldUpdate = true;
                    m_positions[index].trailingStop = newSL;
                }
            }
        }
        
        // Update stop loss if needed
        if(shouldUpdate && newSL != m_positions[index].stopLoss)
        {
            if(m_trade.PositionModify(m_positions[index].ticket, newSL, m_positions[index].takeProfit))
            {
                Print("Trailing stop updated: ", m_positions[index].ticket, " | New SL: ", newSL);
            }
        }
    }
    
    //+------------------------------------------------------------------+
    //| Check partial close conditions                                  |
    //+------------------------------------------------------------------+
    void CheckPartialClose(int index)
    {
        double pipSize = SymbolInfoDouble(m_positions[index].symbol, SYMBOL_POINT) * 10;
        double profitPips = 0;
        
        if(m_positions[index].type == POSITION_TYPE_BUY)
            profitPips = (m_positions[index].currentPrice - m_positions[index].openPrice) / pipSize;
        else
            profitPips = (m_positions[index].openPrice - m_positions[index].currentPrice) / pipSize;
        
        // Check first level partial close
        if(profitPips >= m_partialCloseProfitPips)
        {
            double closeVolume = m_positions[index].volume * (m_partialClosePercent / 100.0);
            closeVolume = NormalizeDouble(closeVolume, 2);
            
            if(closeVolume >= SymbolInfoDouble(m_positions[index].symbol, SYMBOL_VOLUME_MIN))
            {
                if(m_trade.PositionClosePartial(m_positions[index].ticket, closeVolume))
                {
                    m_positions[index].partialClosed = true;
                    Print("Partial close executed: ", m_positions[index].ticket, 
                          " | Volume: ", closeVolume, " | Profit: ", profitPips, " pips");
                }
            }
        }
        
        // Check second level partial close
        if(m_partialCloseLevel2Percent > 0 && profitPips >= m_partialCloseLevel2Pips)
        {
            double closeVolume = m_positions[index].volume * (m_partialCloseLevel2Percent / 100.0);
            closeVolume = NormalizeDouble(closeVolume, 2);
            
            if(closeVolume >= SymbolInfoDouble(m_positions[index].symbol, SYMBOL_VOLUME_MIN))
            {
                if(m_trade.PositionClosePartial(m_positions[index].ticket, closeVolume))
                {
                    Print("Second level partial close: ", m_positions[index].ticket, 
                          " | Volume: ", closeVolume, " | Profit: ", profitPips, " pips");
                }
            }
        }
    }
    
    //+------------------------------------------------------------------+
    //| Check profit protection                                         |
    //+------------------------------------------------------------------+
    void CheckProfitProtection(int index)
    {
        double pipSize = SymbolInfoDouble(m_positions[index].symbol, SYMBOL_POINT) * 10;
        double profitPips = 0;
        
        if(m_positions[index].type == POSITION_TYPE_BUY)
            profitPips = (m_positions[index].currentPrice - m_positions[index].openPrice) / pipSize;
        else
            profitPips = (m_positions[index].openPrice - m_positions[index].currentPrice) / pipSize;
        
        if(profitPips >= m_profitProtectionLevel)
        {
            double protectionSL = 0;
            double trailDistance = m_profitProtectionTrail * pipSize;
            
            if(m_positions[index].type == POSITION_TYPE_BUY)
                protectionSL = m_positions[index].currentPrice - trailDistance;
            else
                protectionSL = m_positions[index].currentPrice + trailDistance;
            
            // Only move SL if it's better than current
            bool shouldUpdate = false;
            if(m_positions[index].type == POSITION_TYPE_BUY && protectionSL > m_positions[index].stopLoss)
                shouldUpdate = true;
            else if(m_positions[index].type == POSITION_TYPE_SELL && protectionSL < m_positions[index].stopLoss)
                shouldUpdate = true;
            
            if(shouldUpdate)
            {
                if(m_trade.PositionModify(m_positions[index].ticket, protectionSL, m_positions[index].takeProfit))
                {
                    Print("Profit protection activated: ", m_positions[index].ticket, 
                          " | New SL: ", protectionSL, " | Profit: ", profitPips, " pips");
                }
            }
        }
    }
    
    //+------------------------------------------------------------------+
    //| Check correlation with existing positions                       |
    //+------------------------------------------------------------------+
    bool CheckCorrelation(string symbol, ENUM_ORDER_TYPE orderType)
    {
        // Simple correlation check - can be enhanced with actual correlation data
        int sameDirectionCount = 0;
        
        for(int i = 0; i < m_positionCount; i++)
        {
            if(m_positions[i].ticket > 0)
            {
                // Check if same direction
                bool sameDirection = false;
                if(orderType == ORDER_TYPE_BUY && m_positions[i].type == POSITION_TYPE_BUY)
                    sameDirection = true;
                else if(orderType == ORDER_TYPE_SELL && m_positions[i].type == POSITION_TYPE_SELL)
                    sameDirection = true;
                
                if(sameDirection)
                {
                    // Check if correlated pairs (simplified)
                    if(IsCorrelatedPair(symbol, m_positions[i].symbol))
                        sameDirectionCount++;
                }
            }
        }
        
        return sameDirectionCount < 3; // Allow max 3 correlated positions
    }
    
    //+------------------------------------------------------------------+
    //| Check if symbol is a mini contract                               |
    //+------------------------------------------------------------------+
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
    
    //+------------------------------------------------------------------+
    //| Get base symbol from mini contract                               |
    //+------------------------------------------------------------------+
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
    
    //+------------------------------------------------------------------+
    //| Check if two symbols are correlated                            |
    //+------------------------------------------------------------------+
    bool IsCorrelatedPair(string symbol1, string symbol2)
    {
        // Simplified correlation check
        if(symbol1 == symbol2)
            return true;
        
        // Get base symbols for mini contracts
        string baseSymbol1 = GetBaseSymbol(symbol1);
        string baseSymbol2 = GetBaseSymbol(symbol2);
        
        // Check if base symbols are the same (for mini contracts)
        if(baseSymbol1 == baseSymbol2)
            return true;
        
        // EUR pairs correlation
        if((StringFind(baseSymbol1, "EUR") >= 0 && StringFind(baseSymbol2, "EUR") >= 0) ||
           (StringFind(baseSymbol1, "GBP") >= 0 && StringFind(baseSymbol2, "GBP") >= 0) ||
           (StringFind(baseSymbol1, "USD") >= 0 && StringFind(baseSymbol2, "USD") >= 0))
            return true;
        
        // Commodity correlation
        if((StringFind(baseSymbol1, "XAU") >= 0 && StringFind(baseSymbol2, "XAG") >= 0) ||
           (StringFind(baseSymbol1, "XAG") >= 0 && StringFind(baseSymbol2, "XAU") >= 0))
            return true;
        
        return false;
    }
    
    //+------------------------------------------------------------------+
    //| Record closed position statistics                               |
    //+------------------------------------------------------------------+
    void RecordClosedPosition(int index)
    {
        m_totalTrades++;
        
        if(m_positions[index].profit > 0)
        {
            m_winningTrades++;
            m_totalProfit += m_positions[index].profit;
            
            if(m_positions[index].profit > m_largestWin)
                m_largestWin = m_positions[index].profit;
            
            m_averageWin = m_totalProfit / m_winningTrades;
        }
        else
        {
            m_losingTrades++;
            m_totalLoss += MathAbs(m_positions[index].profit);
            
            if(MathAbs(m_positions[index].profit) > MathAbs(m_largestLoss))
                m_largestLoss = m_positions[index].profit;
            
            if(m_losingTrades > 0)
                m_averageLoss = m_totalLoss / m_losingTrades;
        }
        
        Print("Position closed: ", m_positions[index].ticket, 
              " | Strategy: ", m_positions[index].strategy,
              " | Profit: ", m_positions[index].profit,
              " | Hold time: ", m_positions[index].holdTime, "s");
    }
    
    //+------------------------------------------------------------------+
    //| Clean up closed positions from tracking                         |
    //+------------------------------------------------------------------+
    void CleanupClosedPositions()
    {
        for(int i = m_positionCount - 1; i >= 0; i--)
        {
            if(m_positions[i].ticket == 0)
            {
                // Shift array elements
                for(int j = i; j < m_positionCount - 1; j++)
                {
                    m_positions[j] = m_positions[j + 1];
                }
                m_positionCount--;
            }
        }
    }
};

//+------------------------------------------------------------------+

