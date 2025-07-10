//+------------------------------------------------------------------+
//|                                        GodModeRiskManager.mqh   |
//|                                    Copyright 2025, oyi77        |
//|                      https://github.com/oyi77/forex-trader      |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, oyi77"
#property link      "https://github.com/oyi77/forex-trader"
#property version   "1.00"

//+------------------------------------------------------------------+
//| God Mode Risk Manager Class                                     |
//| Handles extreme risk calculations for 203,003% return target   |
//+------------------------------------------------------------------+
class CGodModeRiskManager
{
private:
    double            m_initialBalance;
    double            m_currentBalance;
    double            m_targetDailyReturn;
    double            m_maxAccountRisk;
    double            m_maxDrawdown;
    double            m_currentDrawdown;
    double            m_dailyLossLimit;
    double            m_leverage;
    bool              m_godModeEnabled;
    bool              m_emergencyStop;
    
    // Risk tracking
    double            m_todayStartBalance;
    double            m_todayProfit;
    double            m_todayLoss;
    datetime          m_todayStart;
    double            m_peakBalance;
    
    // Position risk
    int               m_maxPositions;
    int               m_currentPositions;
    double            m_totalExposure;
    double            m_correlationLimit;
    
    // Volatility adjustment
    double            m_volatilityMultiplier;
    double            m_atrMultiplier;
    double            m_marketConditionFactor;
    
    // Performance tracking
    double            m_totalReturn;
    double            m_sharpeRatio;
    double            m_profitFactor;
    int               m_consecutiveLosses;
    int               m_maxConsecutiveLosses;
    
public:
    //--- Constructor
    CGodModeRiskManager(double initialBalance, double targetDaily, double maxRisk, 
                       double maxDD, double leverage, bool godMode = true)
    {
        m_initialBalance = initialBalance;
        m_currentBalance = initialBalance;
        m_targetDailyReturn = targetDaily;
        m_maxAccountRisk = maxRisk;
        m_maxDrawdown = maxDD;
        m_leverage = leverage;
        m_godModeEnabled = godMode;
        
        m_currentDrawdown = 0.0;
        m_dailyLossLimit = 30.0; // 30% daily loss limit
        m_emergencyStop = false;
        
        m_todayStartBalance = initialBalance;
        m_todayProfit = 0.0;
        m_todayLoss = 0.0;
        m_todayStart = TimeCurrent();
        m_peakBalance = initialBalance;
        
        m_maxPositions = 20;
        m_currentPositions = 0;
        m_totalExposure = 0.0;
        m_correlationLimit = 0.8;
        
        m_volatilityMultiplier = 1.0;
        m_atrMultiplier = 1.0;
        m_marketConditionFactor = 1.0;
        
        m_totalReturn = 0.0;
        m_sharpeRatio = 0.0;
        m_profitFactor = 1.0;
        m_consecutiveLosses = 0;
        m_maxConsecutiveLosses = 5;
        
        Print("God Mode Risk Manager initialized - Target: ", targetDaily, "% daily");
    }
    
    //--- Destructor
    ~CGodModeRiskManager() {}
    
    //+------------------------------------------------------------------+
    //| Calculate position size based on extreme risk parameters        |
    //+------------------------------------------------------------------+
    double CalculatePositionSize(string strategy, double riskPercent, double confidence, 
                               double stopLossPips, string symbol)
    {
        // Update current balance
        UpdateBalance();
        
        // Check if trading is allowed
        if(!IsTradeAllowed())
            return 0.0;
        
        // Base risk calculation
        double baseRisk = m_currentBalance * (riskPercent / 100.0);
        
        // God Mode multiplier
        double godModeMultiplier = 1.0;
        if(m_godModeEnabled)
        {
            // Extreme multiplier based on target return
            godModeMultiplier = 1.0 + (m_targetDailyReturn / 100.0);
            
            // Additional boost for high confidence
            if(confidence > 80)
                godModeMultiplier *= 1.2;
            
            // Desperation multiplier if behind target
            double currentDailyReturn = GetCurrentDailyReturn();
            if(currentDailyReturn < m_targetDailyReturn * 0.5)
                godModeMultiplier *= 1.5; // 50% boost if behind
        }
        
        // Confidence multiplier
        double confidenceMultiplier = confidence / 100.0;
        
        // Volatility adjustment
        double volatilityAdjustment = m_volatilityMultiplier * m_atrMultiplier;
        
        // Market condition adjustment
        double marketAdjustment = m_marketConditionFactor;
        
        // Strategy-specific multiplier
        double strategyMultiplier = GetStrategyMultiplier(strategy);
        
        // Calculate adjusted risk
        double adjustedRisk = baseRisk * godModeMultiplier * confidenceMultiplier * 
                             volatilityAdjustment * marketAdjustment * strategyMultiplier;
        
        // Apply leverage
        double leveragedRisk = adjustedRisk * (m_leverage / 100.0);
        
        // Calculate position size
        double pipValue = GetPipValue(symbol);
        if(pipValue == 0) pipValue = 1.0; // Fallback
        
        // Mini contract adjustment
        double miniContractMultiplier = GetMiniContractMultiplier(symbol);
        if(IsMiniContract(symbol))
        {
            // For mini contracts, we can use larger position sizes due to lower risk
            // Adjust pip value for mini contracts
            pipValue *= miniContractMultiplier;
            Print("Mini contract detected: ", symbol, " | Multiplier: ", miniContractMultiplier);
        }
        
        double positionSize = leveragedRisk / (stopLossPips * pipValue);
        
        // Apply position limits
        double minLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
        double maxLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
        double lotStep = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
        
        // God Mode: Allow larger positions
        if(m_godModeEnabled)
            maxLot = MathMin(maxLot * 2, 100.0); // Double the normal max
        
        // Mini contract: Allow even larger positions due to lower risk
        if(IsMiniContract(symbol))
        {
            maxLot = MathMin(maxLot * 3, 200.0); // Triple the normal max for mini contracts
        }
        
        positionSize = MathMax(minLot, MathMin(maxLot, positionSize));
        positionSize = MathRound(positionSize / lotStep) * lotStep;
        
        // Final safety check
        if(positionSize * pipValue * stopLossPips > m_currentBalance * (m_maxAccountRisk / 100.0))
        {
            positionSize = (m_currentBalance * (m_maxAccountRisk / 100.0)) / (pipValue * stopLossPips);
            positionSize = MathRound(positionSize / lotStep) * lotStep;
        }
        
        return positionSize;
    }
    
    //+------------------------------------------------------------------+
    //| Check if trade is allowed based on risk parameters              |
    //+------------------------------------------------------------------+
    bool IsTradeAllowed()
    {
        // Emergency stop check
        if(m_emergencyStop)
        {
            Print("EMERGENCY STOP ACTIVE - No new trades allowed");
            return false;
        }
        
        // Update daily tracking
        UpdateDailyTracking();
        
        // God Mode: More aggressive trading rules
        if(m_godModeEnabled)
        {
            // God Mode: Relax most restrictions when behind target
            double currentDailyReturn = GetCurrentDailyReturn();
            if(currentDailyReturn < m_targetDailyReturn * 0.5) // If less than 50% of target
            {
                Print("God Mode: Relaxing restrictions - Behind target (", currentDailyReturn, "% vs ", m_targetDailyReturn, "%)");
                
                // Only check emergency stop and position limits in God Mode
                if(m_currentPositions >= m_maxPositions)
                {
                    Print("Maximum positions reached: ", m_currentPositions);
                    return false;
                }
                
                return true; // Override most restrictions in God Mode
            }
            
            // Even if ahead of target, be more aggressive
            if(m_currentPositions >= m_maxPositions)
            {
                Print("Maximum positions reached: ", m_currentPositions);
                return false;
            }
            
            // Allow higher exposure in God Mode
            if(m_totalExposure > m_currentBalance * (m_maxAccountRisk * 1.5 / 100.0))
            {
                Print("Maximum exposure reached (God Mode): ", m_totalExposure);
                return false;
            }
            
            return true;
        }
        else
        {
            // Conservative mode - original restrictions
            if(m_todayLoss > m_currentBalance * (m_dailyLossLimit / 100.0))
            {
                Print("Daily loss limit reached: ", m_todayLoss);
                return false;
            }
            
            if(m_currentDrawdown > m_maxDrawdown)
            {
                Print("Maximum drawdown exceeded: ", m_currentDrawdown, "%");
                m_emergencyStop = true;
                return false;
            }
            
            if(m_currentPositions >= m_maxPositions)
            {
                Print("Maximum positions reached: ", m_currentPositions);
                return false;
            }
            
            if(m_totalExposure > m_currentBalance * (m_maxAccountRisk / 100.0))
            {
                Print("Maximum exposure reached: ", m_totalExposure);
                return false;
            }
            
            if(m_consecutiveLosses >= m_maxConsecutiveLosses)
            {
                Print("Too many consecutive losses: ", m_consecutiveLosses);
                return false;
            }
        }
        
        return true;
    }
    
    //+------------------------------------------------------------------+
    //| Calculate dynamic stop loss based on market conditions          |
    //+------------------------------------------------------------------+
    double CalculateDynamicStopLoss(ENUM_ORDER_TYPE orderType, double entryPrice, 
                                   double atr, double baseSLPips, string symbol)
    {
        double pipSize = GetPipSize(symbol);
        
        // Base stop loss
        double stopLossPips = baseSLPips;
        
        // ATR adjustment
        double atrPips = atr / pipSize;
        stopLossPips = MathMax(stopLossPips, atrPips * 0.5); // Minimum 0.5 ATR
        
        // Volatility adjustment
        stopLossPips *= m_volatilityMultiplier;
        
        // God Mode: Tighter stops for more aggressive trading
        if(m_godModeEnabled)
        {
            stopLossPips *= 0.7; // 30% tighter stops
            stopLossPips = MathMax(5.0, stopLossPips); // Minimum 5 pips
        }
        
        // Market condition adjustment
        stopLossPips *= m_marketConditionFactor;
        
        // Apply limits
        stopLossPips = MathMax(3.0, MathMin(200.0, stopLossPips));
        
        // Calculate actual stop loss price
        double stopDistance = stopLossPips * pipSize;
        
        if(orderType == ORDER_TYPE_BUY)
            return entryPrice - stopDistance;
        else
            return entryPrice + stopDistance;
    }
    
    //+------------------------------------------------------------------+
    //| Calculate dynamic take profit                                   |
    //+------------------------------------------------------------------+
    double CalculateDynamicTakeProfit(ENUM_ORDER_TYPE orderType, double entryPrice, 
                                     double stopLoss, double atr, double baseTPPips, string symbol)
    {
        double pipSize = GetPipSize(symbol);
        
        // Calculate stop loss distance
        double slDistance = MathAbs(entryPrice - stopLoss);
        double slPips = slDistance / pipSize;
        
        // Base take profit
        double takeProfitPips = baseTPPips;
        
        // God Mode: Smaller take profits for higher frequency
        if(m_godModeEnabled)
        {
            takeProfitPips = MathMax(2.0, slPips * 0.5); // 0.5:1 risk/reward for frequency
        }
        else
        {
            takeProfitPips = MathMax(takeProfitPips, slPips * 1.5); // 1.5:1 risk/reward
        }
        
        // ATR adjustment
        double atrPips = atr / pipSize;
        takeProfitPips = MathMin(takeProfitPips, atrPips * 2.0); // Maximum 2 ATR
        
        // Volatility adjustment
        takeProfitPips *= m_volatilityMultiplier;
        
        // Apply limits
        takeProfitPips = MathMax(1.0, MathMin(500.0, takeProfitPips));
        
        // Calculate actual take profit price
        double profitDistance = takeProfitPips * pipSize;
        
        if(orderType == ORDER_TYPE_BUY)
            return entryPrice + profitDistance;
        else
            return entryPrice - profitDistance;
    }
    
    //+------------------------------------------------------------------+
    //| Update volatility multiplier based on market conditions        |
    //+------------------------------------------------------------------+
    void UpdateVolatilityMultiplier(double currentATR)
    {
        static double previousATR = 0;
        static double avgATR = 0;
        static int atrCount = 0;
        
        if(previousATR == 0)
        {
            previousATR = currentATR;
            avgATR = currentATR;
            atrCount = 1;
            return;
        }
        
        // Update average ATR
        atrCount++;
        avgATR = ((avgATR * (atrCount - 1)) + currentATR) / atrCount;
        
        // Calculate volatility multiplier
        if(avgATR > 0)
        {
            m_volatilityMultiplier = currentATR / avgATR;
            m_volatilityMultiplier = MathMax(0.5, MathMin(3.0, m_volatilityMultiplier));
        }
        
        // ATR trend multiplier
        if(currentATR > previousATR * 1.2)
            m_atrMultiplier = 1.3; // Increase risk in high volatility
        else if(currentATR < previousATR * 0.8)
            m_atrMultiplier = 0.8; // Decrease risk in low volatility
        else
            m_atrMultiplier = 1.0;
        
        previousATR = currentATR;
    }
    
    //+------------------------------------------------------------------+
    //| Update market condition factor                                   |
    //+------------------------------------------------------------------+
    void UpdateMarketCondition(double trendStrength, double momentum)
    {
        // Base factor
        m_marketConditionFactor = 1.0;
        
        // Trend strength adjustment
        if(trendStrength > 0.7)
            m_marketConditionFactor *= 1.2; // Strong trend
        else if(trendStrength < 0.3)
            m_marketConditionFactor *= 0.8; // Weak trend
        
        // Momentum adjustment
        if(momentum > 0.6)
            m_marketConditionFactor *= 1.1; // Strong momentum
        else if(momentum < 0.4)
            m_marketConditionFactor *= 0.9; // Weak momentum
        
        // Apply limits
        m_marketConditionFactor = MathMax(0.5, MathMin(2.0, m_marketConditionFactor));
    }
    
    //+------------------------------------------------------------------+
    //| Record trade result for risk tracking                           |
    //+------------------------------------------------------------------+
    void RecordTradeResult(double profit, bool isWin)
    {
        // Update daily tracking
        if(profit > 0)
            m_todayProfit += profit;
        else
            m_todayLoss += MathAbs(profit);
        
        // Update consecutive losses
        if(isWin)
            m_consecutiveLosses = 0;
        else
            m_consecutiveLosses++;
        
        // Update balance and drawdown
        UpdateBalance();
        UpdateDrawdown();
        
        // Check for emergency conditions
        CheckEmergencyConditions();
    }
    
    //+------------------------------------------------------------------+
    //| Get current daily return percentage                             |
    //+------------------------------------------------------------------+
    double GetCurrentDailyReturn()
    {
        UpdateDailyTracking();
        double dailyProfit = m_todayProfit - m_todayLoss;
        return (dailyProfit / m_todayStartBalance) * 100.0;
    }
    
    //+------------------------------------------------------------------+
    //| Get risk level description                                       |
    //+------------------------------------------------------------------+
    string GetRiskLevel()
    {
        if(m_godModeEnabled)
            return "GOD MODE (EXTREME)";
        else if(m_maxAccountRisk > 80)
            return "EXTREME";
        else if(m_maxAccountRisk > 60)
            return "AGGRESSIVE";
        else if(m_maxAccountRisk > 40)
            return "MODERATE";
        else
            return "CONSERVATIVE";
    }
    
    //+------------------------------------------------------------------+
    //| Check if emergency stop should be activated                     |
    //+------------------------------------------------------------------+
    bool IsEmergencyStop()
    {
        return m_emergencyStop;
    }
    
    //+------------------------------------------------------------------+
    //| Reset emergency stop (use with caution)                         |
    //+------------------------------------------------------------------+
    void ResetEmergencyStop()
    {
        m_emergencyStop = false;
        Print("Emergency stop reset - Trading resumed");
    }
    
    //+------------------------------------------------------------------+
    //| Force reset emergency stop for God Mode                         |
    //+------------------------------------------------------------------+
    void ForceResetEmergencyStop()
    {
        if(m_godModeEnabled)
        {
            m_emergencyStop = false;
            Print("GOD MODE: Emergency stop force reset - Extreme trading resumed");
            Alert("GOD MODE: Emergency stop reset - Trading resumed");
        }
        else
        {
            Print("Force reset only available in God Mode");
        }
    }
    
    //+------------------------------------------------------------------+
    //| Print risk statistics                                           |
    //+------------------------------------------------------------------+
    void PrintRiskStatistics()
    {
        Print("=== RISK MANAGER STATISTICS ===");
        Print("God Mode: ", m_godModeEnabled ? "ENABLED" : "DISABLED");
        Print("Target Daily Return: ", m_targetDailyReturn, "%");
        Print("Current Daily Return: ", GetCurrentDailyReturn(), "%");
        Print("Current Drawdown: ", m_currentDrawdown, "%");
        Print("Max Account Risk: ", m_maxAccountRisk, "%");
        Print("Current Positions: ", m_currentPositions, "/", m_maxPositions);
        Print("Total Exposure: ", m_totalExposure);
        Print("Consecutive Losses: ", m_consecutiveLosses);
        Print("Emergency Stop: ", m_emergencyStop ? "ACTIVE" : "INACTIVE");
        Print("Volatility Multiplier: ", m_volatilityMultiplier);
        Print("Market Condition Factor: ", m_marketConditionFactor);
        Print("===============================");
    }
    
private:
    //+------------------------------------------------------------------+
    //| Update current balance                                           |
    //+------------------------------------------------------------------+
    void UpdateBalance()
    {
        m_currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
        
        // Update peak balance
        if(m_currentBalance > m_peakBalance)
            m_peakBalance = m_currentBalance;
        
        // Calculate total return
        m_totalReturn = ((m_currentBalance - m_initialBalance) / m_initialBalance) * 100.0;
    }
    
    //+------------------------------------------------------------------+
    //| Update drawdown calculation                                      |
    //+------------------------------------------------------------------+
    void UpdateDrawdown()
    {
        double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
        
        if(m_peakBalance > 0)
        {
            m_currentDrawdown = ((m_peakBalance - currentEquity) / m_peakBalance) * 100.0;
            m_currentDrawdown = MathMax(0, m_currentDrawdown);
        }
    }
    
    //+------------------------------------------------------------------+
    //| Update daily tracking                                           |
    //+------------------------------------------------------------------+
    void UpdateDailyTracking()
    {
        MqlDateTime currentDT, todayDT;
        TimeCurrent(currentDT);
        TimeToStruct(m_todayStart, todayDT);
        
        // Check if new day
        if(currentDT.day != todayDT.day)
        {
            // Reset daily counters
            m_todayStartBalance = m_currentBalance;
            m_todayProfit = 0.0;
            m_todayLoss = 0.0;
            m_todayStart = TimeCurrent();
            
            Print("New trading day started - Daily counters reset");
        }
    }
    
    //+------------------------------------------------------------------+
    //| Get strategy-specific multiplier                                |
    //+------------------------------------------------------------------+
    double GetStrategyMultiplier(string strategy)
    {
        if(strategy == "God_Mode_Scalping")
            return 1.5; // Higher risk for scalping
        else if(strategy == "Extreme_RSI")
            return 1.3;
        else if(strategy == "Volatility_Explosion")
            return 1.4;
        else if(strategy == "News_Impact")
            return 1.6; // Highest risk for news
        else if(strategy == "Momentum_Surge")
            return 1.2;
        else if(strategy == "Grid_Recovery")
            return 0.8; // Lower risk for grid
        else
            return 1.0;
    }
    
    //+------------------------------------------------------------------+
    //| Get pip value for symbol                                         |
    //+------------------------------------------------------------------+
    double GetPipValue(string symbol)
    {
        if(symbol == "")
            symbol = _Symbol;
        
        double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
        double tickSize = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
        double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
        
        double pipSize = GetPipSize(symbol);
        double pipValue = (tickValue / tickSize) * pipSize;
        
        // Mini contract adjustment
        if(IsMiniContract(symbol))
        {
            pipValue *= 0.1; // Mini contracts have 0.1x the value
        }
        
        return pipValue;
    }
    
    //+------------------------------------------------------------------+
    //| Get proper pip size for symbol                                   |
    //+------------------------------------------------------------------+
    double GetPipSize(string symbol)
    {
        if(symbol == "")
            symbol = _Symbol;
        
        double point = SymbolInfoDouble(symbol, SYMBOL_POINT);
        double pipSize = 0;
        
        // Special handling for different symbol types
        if(StringFind(symbol, "XAU") >= 0) // Gold
        {
            pipSize = point * 10; // Gold uses 10 * point for pip
        }
        else if(StringFind(symbol, "XAG") >= 0) // Silver
        {
            pipSize = point * 10; // Silver uses 10 * point for pip
        }
        else if(StringFind(symbol, "JPY") >= 0) // JPY pairs
        {
            pipSize = point * 100; // JPY pairs use 100 * point for pip
        }
        else // Other forex pairs
        {
            pipSize = point * 10; // Standard forex pairs use 10 * point for pip
        }
        
        return pipSize;
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
    //| Get mini contract multiplier (usually 0.1 for mini contracts)    |
    //+------------------------------------------------------------------+
    double GetMiniContractMultiplier(string symbol)
    {
        if(!IsMiniContract(symbol))
            return 1.0;
        
        // Mini contracts typically have 0.1x the value of standard contracts
        // This can be adjusted based on broker specifications
        return 0.1;
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
    //| Check for emergency conditions                                   |
    //+------------------------------------------------------------------+
    void CheckEmergencyConditions()
    {
        // God Mode: More aggressive thresholds for extreme returns
        if(m_godModeEnabled)
        {
            // Only stop if account is completely blown (95% loss)
            if(m_currentBalance < m_initialBalance * 0.05) // 95% loss
            {
                m_emergencyStop = true;
                Print("EMERGENCY STOP: Catastrophic loss detected (God Mode)");
                Alert("EMERGENCY STOP: Account down 95%");
            }
            
            // Allow extreme drawdown in God Mode (90% drawdown)
            if(m_currentDrawdown > 90.0) // 90% drawdown
            {
                m_emergencyStop = true;
                Print("EMERGENCY STOP: Extreme drawdown detected (God Mode)");
                Alert("EMERGENCY STOP: Drawdown exceeds 90%");
            }
            
            // Allow extreme daily loss in God Mode (80% daily loss)
            if(m_todayLoss > m_todayStartBalance * 0.8) // 80% daily loss
            {
                m_emergencyStop = true;
                Print("EMERGENCY STOP: Excessive daily loss (God Mode)");
                Alert("EMERGENCY STOP: Daily loss exceeds 80%");
            }
        }
        else
        {
            // Conservative thresholds for non-God Mode
            if(m_currentBalance < m_initialBalance * 0.1) // 90% loss
            {
                m_emergencyStop = true;
                Print("EMERGENCY STOP: Catastrophic loss detected");
                Alert("EMERGENCY STOP: Account down 90%");
            }
            
            if(m_currentDrawdown > 80.0) // 80% drawdown
            {
                m_emergencyStop = true;
                Print("EMERGENCY STOP: Extreme drawdown detected");
                Alert("EMERGENCY STOP: Drawdown exceeds 80%");
            }
            
            if(m_todayLoss > m_todayStartBalance * 0.5) // 50% daily loss
            {
                m_emergencyStop = true;
                Print("EMERGENCY STOP: Excessive daily loss");
                Alert("EMERGENCY STOP: Daily loss exceeds 50%");
            }
        }
    }
};

//+------------------------------------------------------------------+

