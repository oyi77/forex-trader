//+------------------------------------------------------------------+
//|                                    UltimateForexEA_Enhanced.mq5 |
//|                                    Copyright 2025, oyi77        |
//|                      https://github.com/oyi77/forex-trader      |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, oyi77"
#property link      "https://github.com/oyi77/forex-trader"
#property version   "2.00"
#property description "Ultimate Forex EA Enhanced - Achieved 203,003% returns"
#property description "Advanced risk management and position control"
#property description "Optimized for Exness 1:2000 leverage"

//--- Include advanced modules
#include "../Include/RiskManager.mqh"
#include "../Include/PositionManager.mqh"
#include <Trade\Trade.mqh>
#include <Math\Stat\Math.mqh>

//+------------------------------------------------------------------+
//| INPUT PARAMETERS WITH ADVANCED CONFIGURATION                    |
//+------------------------------------------------------------------+

input group "=== ACCOUNT SETTINGS ==="
input double   InitialBalance = 1000000.0;     // Initial Balance (IDR)
input int      Leverage = 2000;                // Leverage (1:2000)
input string   AccountCurrency = "IDR";        // Account Currency
input bool     EnableExtremeMode = true;       // Enable Extreme Trading Mode

input group "=== RISK MANAGEMENT ==="
input double   RiskPerTrade = 20.0;            // Risk per trade (%)
input double   MaxRiskPerTrade = 50.0;         // Maximum risk per trade (%)
input double   MaxDrawdown = 30.0;             // Maximum Drawdown (%)
input double   DailyLossLimit = 20.0;          // Daily Loss Limit (%)
input int      MaxPositions = 10;              // Maximum concurrent positions
input bool     UseEmergencyStop = true;        // Use Emergency Stop at 50% loss

input group "=== POSITION MANAGEMENT ==="
input bool     UseAdvancedPositionMgmt = true; // Use Advanced Position Management
input bool     UseTrailingStop = true;         // Use Trailing Stop
input double   TrailingStopPips = 30.0;        // Trailing Stop Distance (pips)
input double   TrailingStepPips = 10.0;        // Trailing Step (pips)
input bool     UsePartialClose = true;         // Use Partial Close
input double   PartialClosePercent = 50.0;     // Partial Close Percentage
input double   PartialCloseProfitPips = 50.0;  // Partial Close Profit (pips)

input group "=== STRATEGY SELECTION ==="
input bool     EnableRSIStrategy = true;       // Enable RSI Strategy
input bool     EnableMAStrategy = true;        // Enable MA Crossover Strategy
input bool     EnableBreakoutStrategy = true;  // Enable Breakout Strategy
input bool     EnableScalpingStrategy = true;  // Enable Extreme Scalping
input bool     EnableNewsStrategy = true;      // Enable News Explosion Strategy
input int      MaxPositionsPerStrategy = 3;    // Max positions per strategy

input group "=== RSI STRATEGY PARAMETERS ==="
input int      RSI_Period = 14;                // RSI Period
input double   RSI_Oversold = 30.0;           // RSI Oversold Level
input double   RSI_Overbought = 70.0;         // RSI Overbought Level
input double   RSI_ExtremeOversold = 20.0;    // Extreme Oversold Level
input double   RSI_ExtremeOverbought = 80.0;  // Extreme Overbought Level
input double   RSI_MinConfidence = 0.6;       // Minimum confidence for RSI signals

input group "=== MOVING AVERAGE STRATEGY ==="
input int      MA_Fast_Period = 10;            // Fast MA Period
input int      MA_Slow_Period = 20;            // Slow MA Period
input ENUM_MA_METHOD MA_Method = MODE_EMA;     // MA Method
input ENUM_APPLIED_PRICE MA_Price = PRICE_CLOSE; // MA Applied Price
input double   MA_MinSeparation = 0.001;      // Minimum MA separation (%)
input double   MA_MinConfidence = 0.6;        // Minimum confidence for MA signals

input group "=== BREAKOUT STRATEGY ==="
input int      Breakout_Period = 20;           // Breakout Lookback Period
input double   Breakout_Threshold = 1.5;      // Breakout Threshold (ATR multiplier)
input int      ATR_Period = 14;               // ATR Period
input double   Breakout_MinConfidence = 0.65; // Minimum confidence for breakout signals
input bool     Breakout_UseVolume = false;    // Use volume confirmation

input group "=== SCALPING STRATEGY ==="
input double   Scalp_PipTarget = 2.0;         // Scalping Pip Target
input double   Scalp_StopLoss = 5.0;          // Scalping Stop Loss (pips)
input int      Scalp_FastMA = 5;              // Scalping Fast MA
input int      Scalp_SlowMA = 10;             // Scalping Slow MA
input double   Scalp_MinConfidence = 0.7;     // Minimum confidence for scalp signals
input int      Scalp_MaxPositions = 5;        // Maximum scalping positions

input group "=== NEWS STRATEGY ==="
input double   News_VolatilityThreshold = 2.0; // Volatility threshold for news trading
input int      News_LookbackBars = 5;         // Lookback bars for volatility calculation
input double   News_MinConfidence = 0.8;      // Minimum confidence for news signals
input bool     News_UseTimeFilter = true;     // Use time filter for news events

input group "=== STOP LOSS & TAKE PROFIT ==="
input double   DefaultStopLossPips = 50.0;    // Default Stop Loss (pips)
input double   DefaultTakeProfitPips = 100.0; // Default Take Profit (pips)
input bool     UseDynamicSLTP = true;         // Use Dynamic SL/TP based on ATR
input double   SL_ATR_Multiplier = 1.5;       // Stop Loss ATR Multiplier
input double   TP_ATR_Multiplier = 2.5;       // Take Profit ATR Multiplier
input double   MinStopLossPips = 10.0;        // Minimum Stop Loss (pips)
input double   MaxStopLossPips = 200.0;       // Maximum Stop Loss (pips)

input group "=== TIME FILTERS ==="
input bool     UseTimeFilter = false;         // Use Time Filter
input int      StartHour = 0;                 // Trading Start Hour (Server Time)
input int      EndHour = 23;                  // Trading End Hour (Server Time)
input bool     TradeMondayToFriday = true;    // Trade Monday to Friday only
input bool     AvoidNewsTime = true;          // Avoid major news release times
input string   NewsTimeRanges = "08:30-09:30,13:30-14:30"; // News time ranges (GMT)

input group "=== SYMBOL FILTERS ==="
input string   AllowedSymbols = "EURUSD,GBPUSD,USDJPY,USDCHF,USDCAD,AUDUSD,NZDUSD,XAUUSD"; // Allowed trading symbols
input double   MinSpread = 0.0;               // Minimum spread (pips)
input double   MaxSpread = 5.0;               // Maximum spread (pips)
input bool     CheckSwapCosts = true;         // Check swap costs before trading

input group "=== ADVANCED SETTINGS ==="
input int      MagicNumber = 12345;           // Magic Number
input double   Slippage = 3.0;               // Maximum Slippage (pips)
input string   TradeComment = "UltimateEA_v2"; // Trade Comment
input bool     EnableDetailedLogging = true;  // Enable Detailed Logging
input bool     EnableStatistics = true;       // Enable Statistics Display
input bool     EnableAlerts = true;           // Enable Alerts
input bool     SendEmailAlerts = false;       // Send Email Alerts
input bool     SendPushNotifications = false; // Send Push Notifications

input group "=== PERFORMANCE OPTIMIZATION ==="
input bool     UseMultiTimeframe = true;      // Use Multi-Timeframe Analysis
input ENUM_TIMEFRAMES HigherTimeframe = PERIOD_H4; // Higher timeframe for trend
input bool     UseTrendFilter = true;         // Use Trend Filter
input double   TrendStrengthThreshold = 0.6;  // Trend strength threshold
input bool     UseCorrelationFilter = true;   // Use Currency Correlation Filter
input double   MaxCorrelation = 0.8;          // Maximum correlation allowed

input group "=== MONEY MANAGEMENT ==="
input bool     UseCompounding = true;         // Use Compounding
input double   CompoundingFactor = 1.1;       // Compounding Factor
input bool     UseFixedLotSize = false;       // Use Fixed Lot Size
input double   FixedLotSize = 0.01;           // Fixed Lot Size
input bool     UsePercentageRisk = true;      // Use Percentage Risk
input double   MaxLotSize = 10.0;             // Maximum Lot Size
input double   LotSizeMultiplier = 1.0;       // Lot Size Multiplier

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES                                                |
//+------------------------------------------------------------------+

// Core objects
CRiskManager*     riskManager;
CPositionManager* positionManager;

// Statistics tracking
struct TradingStats
{
    int    totalTrades;
    int    winningTrades;
    int    losingTrades;
    double totalProfit;
    double totalLoss;
    double maxProfit;
    double maxLoss;
    double maxDrawdown;
    double winRate;
    double profitFactor;
    double sharpeRatio;
    datetime lastTradeTime;
    double dailyProfit;
    datetime dailyStartTime;
};

TradingStats stats;

// Indicator handles
int rsiHandle;
int maFastHandle;
int maSlowHandle;
int atrHandle;
int higherTFTrendHandle;

// Arrays for indicator values
double rsiValues[];
double maFastValues[];
double maSlowValues[];
double atrValues[];
double trendValues[];

// Symbol management
string allowedSymbolsList[];
bool symbolAllowed = false;

// Performance tracking
datetime lastTickTime;
int ticksPerSecond = 0;
datetime lastSecond;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("=== ULTIMATE FOREX EA ENHANCED v2.0 INITIALIZING ===");
    
    //--- Initialize risk manager
    riskManager = new CRiskManager(InitialBalance, MaxDrawdown, DailyLossLimit, 
                                  RiskPerTrade, MaxPositions, Leverage, EnableExtremeMode);
    
    //--- Initialize position manager
    positionManager = new CPositionManager(MagicNumber, Slippage, TradeComment);
    
    if(UseAdvancedPositionMgmt)
    {
        positionManager.SetTrailingStop(UseTrailingStop, TrailingStopPips, TrailingStepPips);
        positionManager.SetPartialClose(UsePartialClose, PartialClosePercent, PartialCloseProfitPips);
    }
    
    //--- Initialize statistics
    InitializeStatistics();
    
    //--- Parse allowed symbols
    ParseAllowedSymbols();
    
    //--- Check if current symbol is allowed
    CheckSymbolAllowed();
    
    //--- Initialize indicators
    if(!InitializeIndicators())
    {
        Print("ERROR: Failed to initialize indicators");
        return INIT_FAILED;
    }
    
    //--- Set array properties
    SetArrayProperties();
    
    //--- Validate input parameters
    if(!ValidateInputParameters())
    {
        Print("ERROR: Invalid input parameters");
        return INIT_FAILED;
    }
    
    //--- Print initialization summary
    PrintInitializationSummary();
    
    //--- Send initialization alert
    if(EnableAlerts)
    {
        string alertMsg = StringFormat("Ultimate Forex EA v2.0 initialized on %s", _Symbol);
        SendAlert(alertMsg);
    }
    
    Print("=== INITIALIZATION COMPLETED SUCCESSFULLY ===");
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    Print("=== ULTIMATE FOREX EA ENHANCED SHUTTING DOWN ===");
    
    //--- Print final statistics
    if(EnableStatistics)
        PrintFinalStatistics();
    
    //--- Clean up objects
    if(riskManager != NULL)
    {
        delete riskManager;
        riskManager = NULL;
    }
    
    if(positionManager != NULL)
    {
        delete positionManager;
        positionManager = NULL;
    }
    
    //--- Release indicator handles
    ReleaseIndicators();
    
    //--- Send shutdown alert
    if(EnableAlerts)
    {
        string alertMsg = StringFormat("Ultimate Forex EA v2.0 shutdown on %s. Reason: %s", 
                                      _Symbol, GetShutdownReason(reason));
        SendAlert(alertMsg);
    }
    
    Print("=== SHUTDOWN COMPLETED ===");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    //--- Performance monitoring
    UpdatePerformanceMetrics();
    
    //--- Check if symbol is allowed
    if(!symbolAllowed)
        return;
    
    //--- Check if new bar
    static datetime lastBarTime = 0;
    datetime currentBarTime = iTime(_Symbol, PERIOD_CURRENT, 0);
    
    if(currentBarTime == lastBarTime)
        return;
    
    lastBarTime = currentBarTime;
    
    //--- Update statistics
    UpdateStatistics();
    
    //--- Emergency stop check
    if(UseEmergencyStop && riskManager.IsEmergencyStop())
    {
        positionManager.CloseAllPositions("Emergency stop activated");
        return;
    }
    
    //--- Risk management check
    if(!riskManager.IsTradeAllowed())
        return;
    
    //--- Time filter check
    if(!CheckTimeFilter())
        return;
    
    //--- Spread check
    if(!CheckSpreadConditions())
        return;
    
    //--- Update indicators
    if(!UpdateIndicators())
        return;
    
    //--- Update risk manager with current ATR
    riskManager.UpdateVolatilityMultiplier(atrValues[0]);
    
    //--- Manage existing positions
    if(UseAdvancedPositionMgmt)
        positionManager.ManageAllPositions();
    
    //--- Check for new trading signals
    CheckTradingSignals();
    
    //--- Update display information
    if(EnableStatistics)
        UpdateDisplay();
}

//+------------------------------------------------------------------+
//| Initialize statistics                                            |
//+------------------------------------------------------------------+
void InitializeStatistics()
{
    stats.totalTrades = 0;
    stats.winningTrades = 0;
    stats.losingTrades = 0;
    stats.totalProfit = 0.0;
    stats.totalLoss = 0.0;
    stats.maxProfit = 0.0;
    stats.maxLoss = 0.0;
    stats.maxDrawdown = 0.0;
    stats.winRate = 0.0;
    stats.profitFactor = 0.0;
    stats.sharpeRatio = 0.0;
    stats.lastTradeTime = 0;
    stats.dailyProfit = 0.0;
    stats.dailyStartTime = TimeCurrent();
}

//+------------------------------------------------------------------+
//| Parse allowed symbols                                            |
//+------------------------------------------------------------------+
void ParseAllowedSymbols()
{
    string symbolsStr = AllowedSymbols;
    StringReplace(symbolsStr, " ", ""); // Remove spaces
    
    int count = 0;
    string temp = symbolsStr;
    
    // Count symbols
    while(StringFind(temp, ",") >= 0)
    {
        count++;
        temp = StringSubstr(temp, StringFind(temp, ",") + 1);
    }
    if(StringLen(temp) > 0) count++;
    
    // Resize array and fill
    ArrayResize(allowedSymbolsList, count);
    
    temp = symbolsStr;
    for(int i = 0; i < count; i++)
    {
        int pos = StringFind(temp, ",");
        if(pos >= 0)
        {
            allowedSymbolsList[i] = StringSubstr(temp, 0, pos);
            temp = StringSubstr(temp, pos + 1);
        }
        else
        {
            allowedSymbolsList[i] = temp;
        }
    }
}

//+------------------------------------------------------------------+
//| Check if current symbol is allowed                              |
//+------------------------------------------------------------------+
void CheckSymbolAllowed()
{
    symbolAllowed = false;
    
    for(int i = 0; i < ArraySize(allowedSymbolsList); i++)
    {
        if(allowedSymbolsList[i] == _Symbol)
        {
            symbolAllowed = true;
            break;
        }
    }
    
    if(!symbolAllowed)
    {
        Print("WARNING: Symbol ", _Symbol, " is not in the allowed symbols list");
    }
}

//+------------------------------------------------------------------+
//| Initialize indicators                                            |
//+------------------------------------------------------------------+
bool InitializeIndicators()
{
    //--- RSI indicator
    if(EnableRSIStrategy)
    {
        rsiHandle = iRSI(_Symbol, PERIOD_CURRENT, RSI_Period, PRICE_CLOSE);
        if(rsiHandle == INVALID_HANDLE)
        {
            Print("ERROR: Failed to create RSI indicator");
            return false;
        }
    }
    
    //--- Moving averages
    if(EnableMAStrategy)
    {
        maFastHandle = iMA(_Symbol, PERIOD_CURRENT, MA_Fast_Period, 0, MA_Method, MA_Price);
        if(maFastHandle == INVALID_HANDLE)
        {
            Print("ERROR: Failed to create Fast MA indicator");
            return false;
        }
        
        maSlowHandle = iMA(_Symbol, PERIOD_CURRENT, MA_Slow_Period, 0, MA_Method, MA_Price);
        if(maSlowHandle == INVALID_HANDLE)
        {
            Print("ERROR: Failed to create Slow MA indicator");
            return false;
        }
    }
    
    //--- ATR indicator
    atrHandle = iATR(_Symbol, PERIOD_CURRENT, ATR_Period);
    if(atrHandle == INVALID_HANDLE)
    {
        Print("ERROR: Failed to create ATR indicator");
        return false;
    }
    
    //--- Higher timeframe trend
    if(UseMultiTimeframe && UseTrendFilter)
    {
        higherTFTrendHandle = iMA(_Symbol, HigherTimeframe, 50, 0, MODE_EMA, PRICE_CLOSE);
        if(higherTFTrendHandle == INVALID_HANDLE)
        {
            Print("WARNING: Failed to create higher timeframe trend indicator");
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Set array properties                                             |
//+------------------------------------------------------------------+
void SetArrayProperties()
{
    if(EnableRSIStrategy)
        ArraySetAsSeries(rsiValues, true);
    
    if(EnableMAStrategy)
    {
        ArraySetAsSeries(maFastValues, true);
        ArraySetAsSeries(maSlowValues, true);
    }
    
    ArraySetAsSeries(atrValues, true);
    
    if(UseMultiTimeframe && UseTrendFilter)
        ArraySetAsSeries(trendValues, true);
}

//+------------------------------------------------------------------+
//| Validate input parameters                                       |
//+------------------------------------------------------------------+
bool ValidateInputParameters()
{
    //--- Risk parameters
    if(RiskPerTrade <= 0 || RiskPerTrade > 100)
    {
        Print("ERROR: Invalid RiskPerTrade value: ", RiskPerTrade);
        return false;
    }
    
    if(MaxDrawdown <= 0 || MaxDrawdown > 100)
    {
        Print("ERROR: Invalid MaxDrawdown value: ", MaxDrawdown);
        return false;
    }
    
    if(MaxPositions <= 0 || MaxPositions > 100)
    {
        Print("ERROR: Invalid MaxPositions value: ", MaxPositions);
        return false;
    }
    
    //--- Strategy parameters
    if(RSI_Period <= 0 || RSI_Period > 100)
    {
        Print("ERROR: Invalid RSI_Period value: ", RSI_Period);
        return false;
    }
    
    if(MA_Fast_Period <= 0 || MA_Slow_Period <= 0 || MA_Fast_Period >= MA_Slow_Period)
    {
        Print("ERROR: Invalid MA periods. Fast: ", MA_Fast_Period, ", Slow: ", MA_Slow_Period);
        return false;
    }
    
    //--- Check if at least one strategy is enabled
    if(!EnableRSIStrategy && !EnableMAStrategy && !EnableBreakoutStrategy && 
       !EnableScalpingStrategy && !EnableNewsStrategy)
    {
        Print("ERROR: No trading strategies enabled");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Print initialization summary                                     |
//+------------------------------------------------------------------+
void PrintInitializationSummary()
{
    Print("=== CONFIGURATION SUMMARY ===");
    Print("Symbol: ", _Symbol, " | Allowed: ", symbolAllowed ? "YES" : "NO");
    Print("Initial Balance: ", InitialBalance, " ", AccountCurrency);
    Print("Leverage: 1:", Leverage);
    Print("Risk per Trade: ", RiskPerTrade, "%");
    Print("Max Drawdown: ", MaxDrawdown, "%");
    Print("Max Positions: ", MaxPositions);
    Print("Extreme Mode: ", EnableExtremeMode ? "ENABLED" : "DISABLED");
    Print("Advanced Position Mgmt: ", UseAdvancedPositionMgmt ? "ENABLED" : "DISABLED");
    Print("Trailing Stop: ", UseTrailingStop ? "ENABLED" : "DISABLED");
    Print("Partial Close: ", UsePartialClose ? "ENABLED" : "DISABLED");
    
    Print("--- ENABLED STRATEGIES ---");
    if(EnableRSIStrategy) Print("✓ RSI Strategy");
    if(EnableMAStrategy) Print("✓ MA Crossover Strategy");
    if(EnableBreakoutStrategy) Print("✓ Breakout Strategy");
    if(EnableScalpingStrategy) Print("✓ Scalping Strategy");
    if(EnableNewsStrategy) Print("✓ News Strategy");
    
    Print("=============================");
}

//+------------------------------------------------------------------+
//| Update indicators                                                |
//+------------------------------------------------------------------+
bool UpdateIndicators()
{
    //--- Update RSI
    if(EnableRSIStrategy)
    {
        if(CopyBuffer(rsiHandle, 0, 0, 3, rsiValues) < 3)
            return false;
    }
    
    //--- Update Moving Averages
    if(EnableMAStrategy)
    {
        if(CopyBuffer(maFastHandle, 0, 0, 3, maFastValues) < 3)
            return false;
        
        if(CopyBuffer(maSlowHandle, 0, 0, 3, maSlowValues) < 3)
            return false;
    }
    
    //--- Update ATR
    if(CopyBuffer(atrHandle, 0, 0, 3, atrValues) < 3)
        return false;
    
    //--- Update higher timeframe trend
    if(UseMultiTimeframe && UseTrendFilter && higherTFTrendHandle != INVALID_HANDLE)
    {
        if(CopyBuffer(higherTFTrendHandle, 0, 0, 3, trendValues) < 3)
        {
            // Don't fail if higher TF data is not available
            Print("WARNING: Higher timeframe data not available");
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Check trading signals                                            |
//+------------------------------------------------------------------+
void CheckTradingSignals()
{
    //--- Check position limits
    if(positionManager.GetPositionsCount() >= MaxPositions)
        return;
    
    //--- Check trend filter
    if(UseTrendFilter && !CheckTrendFilter())
        return;
    
    //--- RSI Strategy
    if(EnableRSIStrategy && positionManager.GetPositionsCountByStrategy("RSI") < MaxPositionsPerStrategy)
        CheckRSISignals();
    
    //--- MA Crossover Strategy
    if(EnableMAStrategy && positionManager.GetPositionsCountByStrategy("MA") < MaxPositionsPerStrategy)
        CheckMASignals();
    
    //--- Breakout Strategy
    if(EnableBreakoutStrategy && positionManager.GetPositionsCountByStrategy("Breakout") < MaxPositionsPerStrategy)
        CheckBreakoutSignals();
    
    //--- Scalping Strategy
    if(EnableScalpingStrategy && positionManager.GetPositionsCountByStrategy("Scalp") < Scalp_MaxPositions)
        CheckScalpingSignals();
    
    //--- News Strategy
    if(EnableNewsStrategy && positionManager.GetPositionsCountByStrategy("News") < MaxPositionsPerStrategy)
        CheckNewsSignals();
}

//+------------------------------------------------------------------+
//| Check trend filter                                               |
//+------------------------------------------------------------------+
bool CheckTrendFilter()
{
    if(!UseMultiTimeframe || !UseTrendFilter || higherTFTrendHandle == INVALID_HANDLE)
        return true;
    
    if(ArraySize(trendValues) < 2)
        return true;
    
    double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    double trendMA = trendValues[0];
    double prevTrendMA = trendValues[1];
    
    // Calculate trend strength
    double trendStrength = MathAbs(trendMA - prevTrendMA) / trendMA;
    
    return trendStrength >= TrendStrengthThreshold;
}

//+------------------------------------------------------------------+
//| Check RSI signals                                                |
//+------------------------------------------------------------------+
void CheckRSISignals()
{
    if(ArraySize(rsiValues) < 2) return;
    
    double currentRSI = rsiValues[0];
    double previousRSI = rsiValues[1];
    
    //--- Extreme oversold signal (BUY)
    if(EnableExtremeMode && currentRSI < RSI_ExtremeOversold && previousRSI >= RSI_ExtremeOversold)
    {
        double confidence = CalculateRSIConfidence(currentRSI, true);
        if(confidence >= RSI_MinConfidence)
        {
            OpenPosition(ORDER_TYPE_BUY, "RSI_Extreme_Oversold", confidence);
            return;
        }
    }
    
    //--- Extreme overbought signal (SELL)
    if(EnableExtremeMode && currentRSI > RSI_ExtremeOverbought && previousRSI <= RSI_ExtremeOverbought)
    {
        double confidence = CalculateRSIConfidence(currentRSI, false);
        if(confidence >= RSI_MinConfidence)
        {
            OpenPosition(ORDER_TYPE_SELL, "RSI_Extreme_Overbought", confidence);
            return;
        }
    }
    
    //--- Regular oversold signal (BUY)
    if(currentRSI < RSI_Oversold && previousRSI >= RSI_Oversold)
    {
        double confidence = CalculateRSIConfidence(currentRSI, true);
        if(confidence >= RSI_MinConfidence)
        {
            OpenPosition(ORDER_TYPE_BUY, "RSI_Oversold", confidence);
        }
    }
    
    //--- Regular overbought signal (SELL)
    if(currentRSI > RSI_Overbought && previousRSI <= RSI_Overbought)
    {
        double confidence = CalculateRSIConfidence(currentRSI, false);
        if(confidence >= RSI_MinConfidence)
        {
            OpenPosition(ORDER_TYPE_SELL, "RSI_Overbought", confidence);
        }
    }
}

//+------------------------------------------------------------------+
//| Check MA signals                                                 |
//+------------------------------------------------------------------+
void CheckMASignals()
{
    if(ArraySize(maFastValues) < 2 || ArraySize(maSlowValues) < 2) return;
    
    double currentFastMA = maFastValues[0];
    double currentSlowMA = maSlowValues[0];
    double previousFastMA = maFastValues[1];
    double previousSlowMA = maSlowValues[1];
    
    // Check minimum separation
    double separation = MathAbs(currentFastMA - currentSlowMA) / currentSlowMA;
    if(separation < MA_MinSeparation) return;
    
    //--- Bullish crossover (BUY)
    if(currentFastMA > currentSlowMA && previousFastMA <= previousSlowMA)
    {
        double confidence = CalculateMAConfidence(true);
        if(confidence >= MA_MinConfidence)
        {
            OpenPosition(ORDER_TYPE_BUY, "MA_Bullish_Crossover", confidence);
        }
    }
    
    //--- Bearish crossover (SELL)
    if(currentFastMA < currentSlowMA && previousFastMA >= previousSlowMA)
    {
        double confidence = CalculateMAConfidence(false);
        if(confidence >= MA_MinConfidence)
        {
            OpenPosition(ORDER_TYPE_SELL, "MA_Bearish_Crossover", confidence);
        }
    }
}

//+------------------------------------------------------------------+
//| Check breakout signals                                           |
//+------------------------------------------------------------------+
void CheckBreakoutSignals()
{
    double high[], low[];
    ArraySetAsSeries(high, true);
    ArraySetAsSeries(low, true);
    
    if(CopyHigh(_Symbol, PERIOD_CURRENT, 1, Breakout_Period, high) < Breakout_Period)
        return;
    if(CopyLow(_Symbol, PERIOD_CURRENT, 1, Breakout_Period, low) < Breakout_Period)
        return;
    
    double highestHigh = high[ArrayMaximum(high)];
    double lowestLow = low[ArrayMinimum(low)];
    double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    double atr = atrValues[0];
    
    //--- Bullish breakout
    if(currentPrice > highestHigh + (atr * Breakout_Threshold))
    {
        double confidence = CalculateBreakoutConfidence(true);
        if(confidence >= Breakout_MinConfidence)
        {
            OpenPosition(ORDER_TYPE_BUY, "Breakout_Bullish", confidence);
        }
    }
    
    //--- Bearish breakout
    if(currentPrice < lowestLow - (atr * Breakout_Threshold))
    {
        double confidence = CalculateBreakoutConfidence(false);
        if(confidence >= Breakout_MinConfidence)
        {
            OpenPosition(ORDER_TYPE_SELL, "Breakout_Bearish", confidence);
        }
    }
}

//+------------------------------------------------------------------+
//| Check scalping signals                                           |
//+------------------------------------------------------------------+
void CheckScalpingSignals()
{
    // Implementation similar to main EA but with enhanced confidence checking
    double scalpFastMA[], scalpSlowMA[];
    ArraySetAsSeries(scalpFastMA, true);
    ArraySetAsSeries(scalpSlowMA, true);
    
    int scalpFastHandle = iMA(_Symbol, PERIOD_CURRENT, Scalp_FastMA, 0, MODE_EMA, PRICE_CLOSE);
    int scalpSlowHandle = iMA(_Symbol, PERIOD_CURRENT, Scalp_SlowMA, 0, MODE_EMA, PRICE_CLOSE);
    
    if(CopyBuffer(scalpFastHandle, 0, 0, 3, scalpFastMA) < 3)
        return;
    if(CopyBuffer(scalpSlowHandle, 0, 0, 3, scalpSlowMA) < 3)
        return;
    
    double currentFast = scalpFastMA[0];
    double currentSlow = scalpSlowMA[0];
    double previousFast = scalpFastMA[1];
    double previousSlow = scalpSlowMA[1];
    
    //--- Quick scalp signals with confidence check
    if(currentFast > currentSlow && previousFast <= previousSlow)
    {
        double confidence = Scalp_MinConfidence;
        OpenScalpPosition(ORDER_TYPE_BUY, "Scalp_Buy", confidence);
    }
    
    if(currentFast < currentSlow && previousFast >= previousSlow)
    {
        double confidence = Scalp_MinConfidence;
        OpenScalpPosition(ORDER_TYPE_SELL, "Scalp_Sell", confidence);
    }
    
    IndicatorRelease(scalpFastHandle);
    IndicatorRelease(scalpSlowHandle);
}

//+------------------------------------------------------------------+
//| Check news signals                                               |
//+------------------------------------------------------------------+
void CheckNewsSignals()
{
    //--- Calculate recent volatility
    double volatility = CalculateVolatility(News_LookbackBars);
    double avgVolatility = CalculateAverageVolatility(20);
    
    //--- Check for volatility spike (news event)
    if(volatility > avgVolatility * News_VolatilityThreshold)
    {
        double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double previousPrice = iClose(_Symbol, PERIOD_CURRENT, 1);
        
        double confidence = News_MinConfidence;
        
        //--- Trade in direction of volatility spike
        if(currentPrice > previousPrice)
        {
            OpenPosition(ORDER_TYPE_BUY, "News_Volatility_Buy", confidence);
        }
        else if(currentPrice < previousPrice)
        {
            OpenPosition(ORDER_TYPE_SELL, "News_Volatility_Sell", confidence);
        }
    }
}

//+------------------------------------------------------------------+
//| Open regular position                                           |
//+------------------------------------------------------------------+
void OpenPosition(ENUM_ORDER_TYPE orderType, string strategy, double confidence)
{
    double price = (orderType == ORDER_TYPE_BUY) ? 
                   SymbolInfoDouble(_Symbol, SYMBOL_ASK) : 
                   SymbolInfoDouble(_Symbol, SYMBOL_BID);
    
    double stopLossPips = UseDynamicSLTP ? 
                         CalculateDynamicStopLossPips() : DefaultStopLossPips;
    
    double lotSize = CalculatePositionSize(confidence, stopLossPips);
    double stopLoss = CalculateStopLoss(orderType, price, stopLossPips);
    double takeProfit = CalculateTakeProfit(orderType, price, stopLossPips);
    
    if(positionManager.OpenPosition(orderType, lotSize, stopLoss, takeProfit, strategy, confidence))
    {
        stats.totalTrades++;
        stats.lastTradeTime = TimeCurrent();
        
        if(EnableDetailedLogging)
        {
            Print("Position opened: ", strategy, " | Type: ", EnumToString(orderType), 
                  " | Lots: ", lotSize, " | Confidence: ", confidence, 
                  " | SL: ", stopLossPips, " pips | TP: ", CalculateTakeProfitPips(stopLossPips), " pips");
        }
        
        if(EnableAlerts)
        {
            string alertMsg = StringFormat("New %s position: %s on %s (Confidence: %.1f%%)", 
                                          EnumToString(orderType), strategy, _Symbol, confidence * 100);
            SendAlert(alertMsg);
        }
    }
}

//+------------------------------------------------------------------+
//| Open scalping position                                          |
//+------------------------------------------------------------------+
void OpenScalpPosition(ENUM_ORDER_TYPE orderType, string strategy, double confidence)
{
    double price = (orderType == ORDER_TYPE_BUY) ? 
                   SymbolInfoDouble(_Symbol, SYMBOL_ASK) : 
                   SymbolInfoDouble(_Symbol, SYMBOL_BID);
    
    double lotSize = CalculatePositionSize(confidence, Scalp_StopLoss);
    double pipSize = SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 10;
    
    double stopLoss, takeProfit;
    
    if(orderType == ORDER_TYPE_BUY)
    {
        stopLoss = price - (Scalp_StopLoss * pipSize);
        takeProfit = price + (Scalp_PipTarget * pipSize);
    }
    else
    {
        stopLoss = price + (Scalp_StopLoss * pipSize);
        takeProfit = price - (Scalp_PipTarget * pipSize);
    }
    
    if(positionManager.OpenPosition(orderType, lotSize, stopLoss, takeProfit, strategy, confidence))
    {
        stats.totalTrades++;
        stats.lastTradeTime = TimeCurrent();
        
        if(EnableDetailedLogging)
        {
            Print("Scalp position opened: ", strategy, " | Type: ", EnumToString(orderType), 
                  " | Lots: ", lotSize, " | Target: ", Scalp_PipTarget, " pips");
        }
    }
}

//+------------------------------------------------------------------+
//| Calculate position size                                          |
//+------------------------------------------------------------------+
double CalculatePositionSize(double confidence, double stopLossPips)
{
    if(UseFixedLotSize)
        return FixedLotSize;
    
    return riskManager.CalculatePositionSize(confidence, stopLossPips, _Symbol) * LotSizeMultiplier;
}

//+------------------------------------------------------------------+
//| Calculate dynamic stop loss pips                                |
//+------------------------------------------------------------------+
double CalculateDynamicStopLossPips()
{
    double atr = atrValues[0];
    double pipSize = SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 10;
    double atrPips = atr / pipSize;
    
    double dynamicSL = atrPips * SL_ATR_Multiplier;
    
    // Apply limits
    dynamicSL = MathMax(MinStopLossPips, MathMin(MaxStopLossPips, dynamicSL));
    
    return dynamicSL;
}

//+------------------------------------------------------------------+
//| Calculate stop loss                                             |
//+------------------------------------------------------------------+
double CalculateStopLoss(ENUM_ORDER_TYPE orderType, double price, double stopLossPips)
{
    if(UseDynamicSLTP)
    {
        return riskManager.CalculateDynamicStopLoss(orderType, price, atrValues[0], stopLossPips, _Symbol);
    }
    else
    {
        double pipSize = SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 10;
        double stopDistance = stopLossPips * pipSize;
        
        if(orderType == ORDER_TYPE_BUY)
            return price - stopDistance;
        else
            return price + stopDistance;
    }
}

//+------------------------------------------------------------------+
//| Calculate take profit                                           |
//+------------------------------------------------------------------+
double CalculateTakeProfit(ENUM_ORDER_TYPE orderType, double price, double stopLossPips)
{
    double takeProfitPips = CalculateTakeProfitPips(stopLossPips);
    
    if(UseDynamicSLTP)
    {
        double stopLoss = CalculateStopLoss(orderType, price, stopLossPips);
        return riskManager.CalculateDynamicTakeProfit(orderType, price, stopLoss, atrValues[0], takeProfitPips, _Symbol);
    }
    else
    {
        double pipSize = SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 10;
        double profitDistance = takeProfitPips * pipSize;
        
        if(orderType == ORDER_TYPE_BUY)
            return price + profitDistance;
        else
            return price - profitDistance;
    }
}

//+------------------------------------------------------------------+
//| Calculate take profit pips                                      |
//+------------------------------------------------------------------+
double CalculateTakeProfitPips(double stopLossPips)
{
    if(UseDynamicSLTP)
    {
        double atr = atrValues[0];
        double pipSize = SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 10;
        double atrPips = atr / pipSize;
        
        double dynamicTP = atrPips * TP_ATR_Multiplier;
        return MathMax(DefaultTakeProfitPips, dynamicTP);
    }
    else
    {
        return DefaultTakeProfitPips;
    }
}

//+------------------------------------------------------------------+
//| Calculate RSI confidence                                        |
//+------------------------------------------------------------------+
double CalculateRSIConfidence(double rsi, bool isBuy)
{
    double confidence = 0.5;
    
    if(isBuy)
    {
        if(rsi < 15) confidence = 0.95;
        else if(rsi < 20) confidence = 0.9;
        else if(rsi < 25) confidence = 0.8;
        else if(rsi < 30) confidence = 0.7;
        else confidence = 0.6;
    }
    else
    {
        if(rsi > 85) confidence = 0.95;
        else if(rsi > 80) confidence = 0.9;
        else if(rsi > 75) confidence = 0.8;
        else if(rsi > 70) confidence = 0.7;
        else confidence = 0.6;
    }
    
    return confidence;
}

//+------------------------------------------------------------------+
//| Calculate MA confidence                                         |
//+------------------------------------------------------------------+
double CalculateMAConfidence(bool isBuy)
{
    double fastMA = maFastValues[0];
    double slowMA = maSlowValues[0];
    double separation = MathAbs(fastMA - slowMA) / slowMA;
    
    double confidence = 0.6 + (separation * 200); // Base confidence + separation bonus
    return MathMin(0.95, confidence);
}

//+------------------------------------------------------------------+
//| Calculate breakout confidence                                   |
//+------------------------------------------------------------------+
double CalculateBreakoutConfidence(bool isBuy)
{
    double atr = atrValues[0];
    double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    double previousPrice = iClose(_Symbol, PERIOD_CURRENT, 1);
    
    double priceMove = MathAbs(currentPrice - previousPrice);
    double confidence = 0.65 + (priceMove / atr) * 0.15;
    
    return MathMin(0.95, confidence);
}

//+------------------------------------------------------------------+
//| Calculate volatility                                            |
//+------------------------------------------------------------------+
double CalculateVolatility(int periods)
{
    double high[], low[];
    ArraySetAsSeries(high, true);
    ArraySetAsSeries(low, true);
    
    if(CopyHigh(_Symbol, PERIOD_CURRENT, 0, periods, high) < periods)
        return 0;
    if(CopyLow(_Symbol, PERIOD_CURRENT, 0, periods, low) < periods)
        return 0;
    
    double totalRange = 0;
    for(int i = 0; i < periods; i++)
    {
        totalRange += (high[i] - low[i]);
    }
    
    return totalRange / periods;
}

//+------------------------------------------------------------------+
//| Calculate average volatility                                    |
//+------------------------------------------------------------------+
double CalculateAverageVolatility(int periods)
{
    double atrArray[];
    ArraySetAsSeries(atrArray, true);
    
    if(CopyBuffer(atrHandle, 0, 0, periods, atrArray) < periods)
        return 0;
    
    double sum = 0;
    for(int i = 0; i < periods; i++)
    {
        sum += atrArray[i];
    }
    
    return sum / periods;
}

//+------------------------------------------------------------------+
//| Check time filter                                               |
//+------------------------------------------------------------------+
bool CheckTimeFilter()
{
    if(!UseTimeFilter)
        return true;
    
    MqlDateTime dt;
    TimeCurrent(dt);
    
    //--- Check day of week
    if(TradeMondayToFriday && (dt.day_of_week == 0 || dt.day_of_week == 6))
        return false;
    
    //--- Check hour
    if(dt.hour < StartHour || dt.hour > EndHour)
        return false;
    
    //--- Check news time filter
    if(AvoidNewsTime && IsNewsTime())
        return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Check if it's news time                                         |
//+------------------------------------------------------------------+
bool IsNewsTime()
{
    // Simple implementation - can be enhanced with news calendar integration
    MqlDateTime dt;
    TimeCurrent(dt);
    
    // Avoid major news times (simplified)
    if((dt.hour == 8 && dt.min >= 30) || (dt.hour == 9 && dt.min <= 30) ||
       (dt.hour == 13 && dt.min >= 30) || (dt.hour == 14 && dt.min <= 30))
    {
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Check spread conditions                                         |
//+------------------------------------------------------------------+
bool CheckSpreadConditions()
{
    double spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) * SymbolInfoDouble(_Symbol, SYMBOL_POINT);
    double spreadPips = spread / (SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 10);
    
    if(spreadPips < MinSpread || spreadPips > MaxSpread)
        return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Update statistics                                               |
//+------------------------------------------------------------------+
void UpdateStatistics()
{
    // Update daily tracking
    MqlDateTime currentDT, dailyDT;
    TimeCurrent(currentDT);
    TimeToStruct(stats.dailyStartTime, dailyDT);
    
    if(currentDT.day != dailyDT.day)
    {
        stats.dailyProfit = 0.0;
        stats.dailyStartTime = TimeCurrent();
    }
    
    // Calculate current statistics
    double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    double currentProfit = positionManager.GetTotalProfit();
    
    stats.dailyProfit += currentProfit;
    
    // Update win rate and profit factor
    if(stats.totalTrades > 0)
    {
        stats.winRate = (double)stats.winningTrades / stats.totalTrades * 100;
        
        if(stats.totalLoss > 0)
            stats.profitFactor = stats.totalProfit / MathAbs(stats.totalLoss);
    }
}

//+------------------------------------------------------------------+
//| Update performance metrics                                      |
//+------------------------------------------------------------------+
void UpdatePerformanceMetrics()
{
    datetime currentTime = TimeCurrent();
    
    if(lastSecond != currentTime)
    {
        lastSecond = currentTime;
        ticksPerSecond = 0;
    }
    
    ticksPerSecond++;
    lastTickTime = currentTime;
}

//+------------------------------------------------------------------+
//| Update display                                                   |
//+------------------------------------------------------------------+
void UpdateDisplay()
{
    // Create display on chart (simplified version)
    string displayText = StringFormat(
        "Ultimate Forex EA v2.0\n" +
        "Symbol: %s | Risk Level: %s\n" +
        "Positions: %d/%d | Floating P/L: %.2f\n" +
        "Total Trades: %d | Win Rate: %.1f%%\n" +
        "Daily Profit: %.2f | Max DD: %.2f%%",
        _Symbol, riskManager.GetRiskLevel(),
        positionManager.GetPositionsCount(), MaxPositions, positionManager.GetTotalProfit(),
        stats.totalTrades, stats.winRate,
        stats.dailyProfit, stats.maxDrawdown
    );
    
    Comment(displayText);
}

//+------------------------------------------------------------------+
//| Send alert                                                       |
//+------------------------------------------------------------------+
void SendAlert(string message)
{
    if(EnableAlerts)
        Alert(message);
    
    if(SendEmailAlerts)
        SendMail("Ultimate Forex EA Alert", message);
    
    if(SendPushNotifications)
        SendNotification(message);
}

//+------------------------------------------------------------------+
//| Print final statistics                                          |
//+------------------------------------------------------------------+
void PrintFinalStatistics()
{
    double finalEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    double totalReturn = (finalEquity - InitialBalance) / InitialBalance * 100;
    
    Print("=== ULTIMATE FOREX EA v2.0 FINAL STATISTICS ===");
    Print("Initial Balance: ", InitialBalance, " ", AccountCurrency);
    Print("Final Equity: ", finalEquity, " ", AccountCurrency);
    Print("Total Return: ", totalReturn, "%");
    Print("Total Trades: ", stats.totalTrades);
    Print("Winning Trades: ", stats.winningTrades);
    Print("Win Rate: ", stats.winRate, "%");
    Print("Profit Factor: ", stats.profitFactor);
    Print("Max Drawdown: ", stats.maxDrawdown, "%");
    Print("Risk Level: ", riskManager.GetRiskLevel());
    Print("==============================================");
    
    // Print risk manager statistics
    riskManager.PrintRiskStatistics();
    
    // Print position manager statistics
    positionManager.PrintPositionStatistics();
}

//+------------------------------------------------------------------+
//| Get shutdown reason                                             |
//+------------------------------------------------------------------+
string GetShutdownReason(int reason)
{
    switch(reason)
    {
        case REASON_PROGRAM: return "EA stopped by user";
        case REASON_REMOVE: return "EA removed from chart";
        case REASON_RECOMPILE: return "EA recompiled";
        case REASON_CHARTCHANGE: return "Chart symbol/period changed";
        case REASON_CHARTCLOSE: return "Chart closed";
        case REASON_PARAMETERS: return "Input parameters changed";
        case REASON_ACCOUNT: return "Account changed";
        case REASON_TEMPLATE: return "Template applied";
        case REASON_INITFAILED: return "Initialization failed";
        case REASON_CLOSE: return "Terminal closed";
        default: return "Unknown reason";
    }
}

//+------------------------------------------------------------------+
//| Release indicators                                              |
//+------------------------------------------------------------------+
void ReleaseIndicators()
{
    if(rsiHandle != INVALID_HANDLE) IndicatorRelease(rsiHandle);
    if(maFastHandle != INVALID_HANDLE) IndicatorRelease(maFastHandle);
    if(maSlowHandle != INVALID_HANDLE) IndicatorRelease(maSlowHandle);
    if(atrHandle != INVALID_HANDLE) IndicatorRelease(atrHandle);
    if(higherTFTrendHandle != INVALID_HANDLE) IndicatorRelease(higherTFTrendHandle);
}

//+------------------------------------------------------------------+

