//+------------------------------------------------------------------+
//|                                              RiskManager.mqh    |
//|                                    Copyright 2025, oyi77        |
//|                      https://github.com/oyi77/forex-trader      |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, oyi77"
#property link      "https://github.com/oyi77/forex-trader"

//+------------------------------------------------------------------+
//| Advanced Risk Management Class                                  |
//+------------------------------------------------------------------+
class CRiskManager
{
private:
    double            m_initialBalance;
    double            m_maxDrawdown;
    double            m_dailyLossLimit;
    double            m_riskPerTrade;
    double            m_maxRiskPerTrade;
    double            m_currentDrawdown;
    double            m_dailyStartEquity;
    datetime          m_dailyStartTime;
    int               m_maxPositions;
    int               m_leverage;
    bool              m_extremeMode;
    
    // Risk scaling factors
    double            m_winStreakMultiplier;
    double            m_lossStreakDivisor;
    int               m_consecutiveWins;
    int               m_consecutiveLosses;
    
    // Volatility adjustment
    double            m_volatilityMultiplier;
    double            m_baseVolatility;
    
public:
    //--- Constructor
    CRiskManager(double initialBalance, double maxDrawdown, double dailyLossLimit, 
                 double riskPerTrade, int maxPositions, int leverage, bool extremeMode)
    {
        m_initialBalance = initialBalance;
        m_maxDrawdown = maxDrawdown;
        m_dailyLossLimit = dailyLossLimit;
        m_riskPerTrade = riskPerTrade;
        m_maxRiskPerTrade = extremeMode ? 50.0 : 25.0; // Max risk in extreme mode
        m_maxPositions = maxPositions;
        m_leverage = leverage;
        m_extremeMode = extremeMode;
        
        m_currentDrawdown = 0.0;
        m_dailyStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
        m_dailyStartTime = TimeCurrent();
        
        // Risk scaling
        m_winStreakMultiplier = 1.0;
        m_lossStreakDivisor = 1.0;
        m_consecutiveWins = 0;
        m_consecutiveLosses = 0;
        
        // Volatility
        m_volatilityMultiplier = 1.0;
        m_baseVolatility = 0.0;
    }
    
    //--- Check if trading is allowed
    bool IsTradeAllowed()
    {
        UpdateDailyTracking();
        UpdateDrawdown();
        
        // Check maximum drawdown
        if(m_currentDrawdown > m_maxDrawdown)
        {
            Print("RISK ALERT: Maximum drawdown exceeded: ", m_currentDrawdown, "%");
            return false;
        }
        
        // Check daily loss limit
        double dailyLoss = GetDailyLoss();
        if(dailyLoss > m_dailyLossLimit)
        {
            Print("RISK ALERT: Daily loss limit exceeded: ", dailyLoss, "%");
            return false;
        }
        
        // Check maximum positions
        if(GetOpenPositionsCount() >= m_maxPositions)
        {
            return false;
        }
        
        return true;
    }
    
    //--- Calculate position size with advanced risk management
    double CalculatePositionSize(double confidence, double stopLossPips, string symbol = "")
    {
        if(symbol == "") symbol = _Symbol;
        
        double equity = AccountInfoDouble(ACCOUNT_EQUITY);
        double baseRiskAmount = equity * (m_riskPerTrade / 100.0);
        
        // Apply confidence multiplier
        double confidenceMultiplier = m_extremeMode ? confidence * 2.0 : confidence;
        double riskAmount = baseRiskAmount * confidenceMultiplier;
        
        // Apply win/loss streak adjustments
        riskAmount *= m_winStreakMultiplier;
        riskAmount /= m_lossStreakDivisor;
        
        // Apply volatility adjustment
        riskAmount *= m_volatilityMultiplier;
        
        // Apply leverage effect
        double leverageMultiplier = MathMin(m_leverage / 100.0, 20.0); // Cap at 20x for safety
        riskAmount *= leverageMultiplier;
        
        // Ensure we don't exceed maximum risk per trade
        double maxRiskAmount = equity * (m_maxRiskPerTrade / 100.0);
        riskAmount = MathMin(riskAmount, maxRiskAmount);
        
        // Calculate lot size
        double pipValue = GetPipValue(symbol);
        double lotSize = riskAmount / (stopLossPips * pipValue);
        
        // Normalize lot size
        return NormalizeLotSize(lotSize, symbol);
    }
    
    //--- Calculate dynamic stop loss based on volatility
    double CalculateDynamicStopLoss(ENUM_ORDER_TYPE orderType, double entryPrice, 
                                   double atr, double baseSLPips, string symbol = "")
    {
        if(symbol == "") symbol = _Symbol;
        
        double pipSize = SymbolInfoDouble(symbol, SYMBOL_POINT);
        if(StringFind(symbol, "JPY") >= 0) pipSize *= 10;
        else pipSize *= 10;
        
        // Base stop loss
        double stopDistance = baseSLPips * pipSize;
        
        // Adjust based on ATR (volatility)
        double atrMultiplier = m_extremeMode ? 1.0 : 1.5; // Tighter stops in extreme mode
        double atrStopDistance = atr * atrMultiplier;
        
        // Use the larger of the two for safety
        stopDistance = MathMax(stopDistance, atrStopDistance);
        
        // Apply volatility multiplier
        stopDistance *= m_volatilityMultiplier;
        
        // Calculate final stop loss
        if(orderType == ORDER_TYPE_BUY)
            return entryPrice - stopDistance;
        else
            return entryPrice + stopDistance;
    }
    
    //--- Calculate dynamic take profit
    double CalculateDynamicTakeProfit(ENUM_ORDER_TYPE orderType, double entryPrice, 
                                     double stopLoss, double atr, double baseTPPips, string symbol = "")
    {
        if(symbol == "") symbol = _Symbol;
        
        double pipSize = SymbolInfoDouble(symbol, SYMBOL_POINT);
        if(StringFind(symbol, "JPY") >= 0) pipSize *= 10;
        else pipSize *= 10;
        
        // Calculate risk-reward ratio
        double riskRewardRatio = m_extremeMode ? 1.5 : 2.0; // Lower RR in extreme mode for faster profits
        
        double stopDistance = MathAbs(entryPrice - stopLoss);
        double profitDistance = stopDistance * riskRewardRatio;
        
        // Ensure minimum take profit
        double minTPDistance = baseTPPips * pipSize;
        profitDistance = MathMax(profitDistance, minTPDistance);
        
        // Apply ATR-based adjustment
        double atrTPDistance = atr * 2.5;
        profitDistance = MathMax(profitDistance, atrTPDistance);
        
        // Calculate final take profit
        if(orderType == ORDER_TYPE_BUY)
            return entryPrice + profitDistance;
        else
            return entryPrice - profitDistance;
    }
    
    //--- Update win/loss streaks
    void UpdateTradeResult(bool isWin, double profit)
    {
        if(isWin)
        {
            m_consecutiveWins++;
            m_consecutiveLosses = 0;
            
            // Increase risk after wins (but cap it)
            m_winStreakMultiplier = MathMin(1.0 + (m_consecutiveWins * 0.1), 2.0);
            m_lossStreakDivisor = 1.0;
        }
        else
        {
            m_consecutiveLosses++;
            m_consecutiveWins = 0;
            
            // Decrease risk after losses
            m_lossStreakDivisor = MathMin(1.0 + (m_consecutiveLosses * 0.2), 3.0);
            m_winStreakMultiplier = 1.0;
        }
        
        Print("Trade result: ", isWin ? "WIN" : "LOSS", 
              " | Win streak: ", m_consecutiveWins, 
              " | Loss streak: ", m_consecutiveLosses,
              " | Risk multiplier: ", m_winStreakMultiplier / m_lossStreakDivisor);
    }
    
    //--- Update volatility multiplier
    void UpdateVolatilityMultiplier(double currentATR)
    {
        if(m_baseVolatility == 0.0)
        {
            m_baseVolatility = currentATR;
            return;
        }
        
        double volatilityRatio = currentATR / m_baseVolatility;
        
        if(volatilityRatio > 1.5) // High volatility
        {
            m_volatilityMultiplier = 0.7; // Reduce risk
        }
        else if(volatilityRatio < 0.7) // Low volatility
        {
            m_volatilityMultiplier = 1.3; // Increase risk
        }
        else
        {
            m_volatilityMultiplier = 1.0; // Normal risk
        }
        
        // Update base volatility (exponential moving average)
        m_baseVolatility = (m_baseVolatility * 0.9) + (currentATR * 0.1);
    }
    
    //--- Check if position should be closed early
    bool ShouldClosePosition(ulong ticket, double currentProfit, double maxProfit)
    {
        if(!PositionSelectByTicket(ticket))
            return false;
        
        // Close if profit drops significantly from peak
        if(maxProfit > 0 && currentProfit < maxProfit * 0.7)
        {
            return true;
        }
        
        // Close losing positions if they exceed certain threshold
        double equity = AccountInfoDouble(ACCOUNT_EQUITY);
        double lossThreshold = equity * 0.02; // 2% of equity
        
        if(currentProfit < -lossThreshold)
        {
            return true;
        }
        
        return false;
    }
    
    //--- Emergency stop all trading
    bool IsEmergencyStop()
    {
        double equity = AccountInfoDouble(ACCOUNT_EQUITY);
        double totalLoss = m_initialBalance - equity;
        double lossPercentage = (totalLoss / m_initialBalance) * 100;
        
        // Emergency stop at 50% loss
        if(lossPercentage > 50.0)
        {
            Print("EMERGENCY STOP: Total loss exceeds 50%");
            return true;
        }
        
        // Emergency stop if daily loss exceeds 30%
        double dailyLoss = GetDailyLoss();
        if(dailyLoss > 30.0)
        {
            Print("EMERGENCY STOP: Daily loss exceeds 30%");
            return true;
        }
        
        return false;
    }
    
    //--- Get current risk level
    string GetRiskLevel()
    {
        if(m_currentDrawdown > m_maxDrawdown * 0.8)
            return "CRITICAL";
        else if(m_currentDrawdown > m_maxDrawdown * 0.6)
            return "HIGH";
        else if(m_currentDrawdown > m_maxDrawdown * 0.4)
            return "MEDIUM";
        else
            return "LOW";
    }
    
    //--- Get risk statistics
    void PrintRiskStatistics()
    {
        Print("=== RISK MANAGEMENT STATISTICS ===");
        Print("Current Drawdown: ", m_currentDrawdown, "%");
        Print("Daily Loss: ", GetDailyLoss(), "%");
        Print("Risk Level: ", GetRiskLevel());
        Print("Win Streak: ", m_consecutiveWins);
        Print("Loss Streak: ", m_consecutiveLosses);
        Print("Risk Multiplier: ", m_winStreakMultiplier / m_lossStreakDivisor);
        Print("Volatility Multiplier: ", m_volatilityMultiplier);
        Print("Open Positions: ", GetOpenPositionsCount(), "/", m_maxPositions);
        Print("==================================");
    }

private:
    //--- Update daily tracking
    void UpdateDailyTracking()
    {
        MqlDateTime currentDT, startDT;
        TimeCurrent(currentDT);
        TimeToStruct(m_dailyStartTime, startDT);
        
        if(currentDT.day != startDT.day)
        {
            m_dailyStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
            m_dailyStartTime = TimeCurrent();
        }
    }
    
    //--- Update current drawdown
    void UpdateDrawdown()
    {
        double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
        m_currentDrawdown = (m_initialBalance - currentEquity) / m_initialBalance * 100;
    }
    
    //--- Get daily loss percentage
    double GetDailyLoss()
    {
        double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
        return (m_dailyStartEquity - currentEquity) / m_dailyStartEquity * 100;
    }
    
    //--- Get pip value for symbol
    double GetPipValue(string symbol)
    {
        double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
        double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
        double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
        
        double pipSize = point * 10;
        if(StringFind(symbol, "JPY") >= 0)
            pipSize = point * 100;
        
        return (tickValue / tickSize) * pipSize;
    }
    
    //--- Normalize lot size
    double NormalizeLotSize(double lotSize, string symbol)
    {
        double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
        double lotStep = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
        
        lotSize = MathMax(minLot, MathMin(maxLot, lotSize));
        lotSize = MathRound(lotSize / lotStep) * lotStep;
        
        return lotSize;
    }
    
    //--- Get open positions count
    int GetOpenPositionsCount()
    {
        int count = 0;
        for(int i = 0; i < PositionsTotal(); i++)
        {
            if(PositionGetTicket(i) > 0)
                count++;
        }
        return count;
    }
};

//+------------------------------------------------------------------+

