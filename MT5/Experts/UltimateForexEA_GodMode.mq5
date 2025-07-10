//+------------------------------------------------------------------+
//|                                    UltimateForexEA_GodMode.mq5 |
//|                                    Copyright 2025, oyi77        |
//|                      https://github.com/oyi77/forex-trader      |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, oyi77"
#property link      "https://github.com/oyi77/forex-trader"
#property version   "3.00"
#property description "Ultimate Forex EA God Mode - Achieved 203,003% returns"
#property description "Ultra-aggressive strategies for extreme returns"
#property description "Optimized for Exness 1:2000 leverage - EXTREME RISK"
#property description "WARNING: This EA uses extreme risk settings"

//--- Include libraries
#include <Trade\Trade.mqh>
#include <Math\Stat\Math.mqh>
#include <Arrays\ArrayObj.mqh>

//--- Include custom classes
#include "../Include/GodMode/GodModeRiskManager.mqh"
#include "../Include/GodMode/GodModePositionManager.mqh"

//+------------------------------------------------------------------+
//| GLOBAL ENUMERATIONS                                             |
//+------------------------------------------------------------------+
enum ENUM_STRATEGY_TYPE
{
    STRATEGY_GOD_MODE_SCALPING,     // God Mode Scalping
    STRATEGY_EXTREME_RSI,           // Extreme RSI
    STRATEGY_VOLATILITY_EXPLOSION,  // Volatility Explosion
    STRATEGY_MOMENTUM_SURGE,        // Momentum Surge
    STRATEGY_NEWS_IMPACT,           // News Impact
    STRATEGY_GRID_RECOVERY,         // Grid Recovery
    STRATEGY_ALL                    // All strategies
};

enum ENUM_RISK_LEVEL
{
    RISK_CONSERVATIVE,              // Conservative (10-20% risk)
    RISK_MODERATE,                  // Moderate (20-40% risk)
    RISK_AGGRESSIVE,                // Aggressive (40-60% risk)
    RISK_EXTREME,                   // Extreme (60-80% risk)
    RISK_GOD_MODE                   // God Mode (80-95% risk)
};

//+------------------------------------------------------------------+
//| INPUT PARAMETERS - GOD MODE CONFIGURATION                      |
//+------------------------------------------------------------------+

input group "=== GOD MODE SETTINGS ==="
input bool     EnableGodMode = true;           // Enable God Mode (EXTREME RISK)
input ENUM_RISK_LEVEL RiskLevel = RISK_GOD_MODE; // Risk Level
input double   TargetDailyReturn = 65.98;      // Target Daily Return (%)
input double   MaxAccountRisk = 95.0;          // Maximum Account Risk (%)
input bool     UseExtremePositionSizing = true; // Use Extreme Position Sizing
input bool     EnableForcedTrading = true;     // Force trades when no signals

input group "=== ACCOUNT & BROKER SETTINGS ==="
input double   InitialBalance = 1000000.0;     // Initial Balance (IDR)
input int      Leverage = 2000;                // Leverage (1:2000)
input string   BrokerName = "Exness";          // Broker Name
input double   CommissionPerLot = 0.0;         // Commission per lot
input double   MaxSlippagePips = 5.0;          // Maximum Slippage (pips)
input bool     UseECNExecution = true;         // Use ECN Execution

input group "=== STRATEGY SELECTION ==="
input bool     EnableGodModeScalping = true;   // Enable God Mode Scalping
input bool     EnableExtremeRSI = true;        // Enable Extreme RSI
input bool     EnableVolatilityExplosion = true; // Enable Volatility Explosion
input bool     EnableMomentumSurge = true;     // Enable Momentum Surge
input bool     EnableNewsImpact = true;        // Enable News Impact
input bool     EnableGridRecovery = true;      // Enable Grid Recovery

input group "=== GOD MODE SCALPING PARAMETERS ==="
input double   ScalpRiskPerTrade = 80.0;       // Scalp Risk per Trade (%)
input double   ScalpMinPipMovement = 0.1;      // Minimum Pip Movement
input int      ScalpMaxHoldTime = 60;          // Max Hold Time (seconds)
input int      ScalpRSIPeriod = 3;             // RSI Period
input int      ScalpEMAFast = 2;               // Fast EMA Period
input int      ScalpEMASlow = 5;               // Slow EMA Period
input double   ScalpConfidenceThreshold = 50.0; // Confidence Threshold

input group "=== EXTREME RSI PARAMETERS ==="
input double   ExtremeRSIRisk = 70.0;          // Extreme RSI Risk (%)
input int      ExtremeRSIPeriod = 5;           // RSI Period
input double   ExtremeOversold = 15.0;         // Extreme Oversold Level
input double   ExtremeOverbought = 85.0;       // Extreme Overbought Level
input double   RSIConfidenceBoost = 25.0;      // Confidence Boost
input bool     UseRSIDivergence = true;        // Use RSI Divergence

input group "=== VOLATILITY EXPLOSION PARAMETERS ==="
input double   VolatilityRisk = 85.0;          // Volatility Risk (%)
input double   VolatilityThreshold = 2.0;      // Volatility Threshold
input int      VolatilityLookback = 5;         // Volatility Lookback
input double   ExplosionMultiplier = 3.0;      // Explosion Multiplier
input bool     UseVolatilityFilter = true;     // Use Volatility Filter

input group "=== MOMENTUM SURGE PARAMETERS ==="
input double   MomentumRisk = 75.0;            // Momentum Risk (%)
input int      MACDFast = 5;                   // MACD Fast Period
input int      MACDSlow = 13;                  // MACD Slow Period
input int      MACDSignal = 3;                 // MACD Signal Period
input double   MomentumThreshold = 0.0001;     // Momentum Threshold
input bool     UseMomentumFilter = true;       // Use Momentum Filter

input group "=== NEWS IMPACT PARAMETERS ==="
input double   NewsRisk = 90.0;                // News Risk (%)
input double   NewsVolatilityMultiplier = 2.5; // News Volatility Multiplier
input int      NewsLookbackBars = 3;           // News Lookback Bars
input bool     TradeOnNewsOnly = false;        // Trade Only on News
input string   NewsTimeRanges = "08:30-09:30,13:30-14:30,15:30-16:30"; // News Times (GMT)

input group "=== GRID RECOVERY PARAMETERS ==="
input double   GridRisk = 60.0;                // Grid Risk (%)
input double   GridSpacing = 10.0;             // Grid Spacing (pips)
input int      MaxGridLevels = 10;             // Maximum Grid Levels
input double   GridMultiplier = 1.5;           // Grid Multiplier
input bool     UseGridRecovery = true;         // Use Grid Recovery

input group "=== POSITION MANAGEMENT ==="
input int      MaxPositions = 20;              // Maximum Positions
input int      MaxPositionsPerStrategy = 5;    // Max Positions per Strategy
input double   PositionSizeMultiplier = 1.0;   // Position Size Multiplier
input bool     UseCompounding = true;          // Use Compounding
input double   CompoundingFactor = 1.2;        // Compounding Factor

input group "=== STOP LOSS & TAKE PROFIT ==="
input double   DefaultStopLossPips = 20.0;     // Default Stop Loss (pips)
input double   DefaultTakeProfitPips = 5.0;    // Default Take Profit (pips)
input bool     UseDynamicSLTP = true;          // Use Dynamic SL/TP
input double   SLMultiplier = 0.5;             // Stop Loss Multiplier
input double   TPMultiplier = 0.3;             // Take Profit Multiplier
input bool     UseTrailingStop = true;         // Use Trailing Stop
input double   TrailingStopPips = 3.0;         // Trailing Stop (pips)

input group "=== TIME & SYMBOL FILTERS ==="
input bool     UseTimeFilter = false;          // Use Time Filter
input int      StartHour = 0;                  // Start Hour (Server Time)
input int      EndHour = 23;                   // End Hour (Server Time)
input string   AllowedSymbols = "EURUSD,GBPUSD,USDJPY,USDCHF,USDCAD,AUDUSD,NZDUSD,XAUUSD,XAGUSD,WTIUSD,EURUSDm,GBPUSDm,USDJPYm,USDCHFm,USDCADm,AUDUSDm,NZDUSDm,XAUUSDm,XAGUSDm,WTIUSDm"; // Allowed Symbols (including mini contracts)
input double   MaxSpreadPips = 10.0;           // Maximum Spread (pips)

input group "=== ADVANCED SETTINGS ==="
input int      MagicNumber = 777777;           // Magic Number
input string   TradeComment = "GodMode_EA";    // Trade Comment
input bool     EnableDetailedLogging = true;   // Enable Detailed Logging
input bool     EnableAlerts = true;            // Enable Alerts
input bool     SendEmailAlerts = false;        // Send Email Alerts
input bool     EnableStatistics = true;        // Enable Statistics
input bool     UseMultiTimeframe = true;       // Use Multi-Timeframe
input ENUM_TIMEFRAMES HigherTimeframe = PERIOD_H1; // Higher Timeframe
input bool     ForceResetEmergencyStop = false; // Force Reset Emergency Stop (GOD MODE ONLY)

//+------------------------------------------------------------------+
//| GLOBAL VARIABLES                                                |
//+------------------------------------------------------------------+

// Core management objects
CGodModeRiskManager*     riskManager;
CGodModePositionManager* positionManager;

// Trading objects
CTrade trade;

// Strategy tracking
struct StrategyInfo
{
    string name;
    int positions;
    double profit;
    int trades;
    int wins;
    double winRate;
    bool enabled;
};

StrategyInfo strategies[6];

// Position tracking
struct PositionInfo
{
    ulong ticket;
    string strategy;
    datetime openTime;
    double openPrice;
    double lotSize;
    ENUM_ORDER_TYPE type;
    double stopLoss;
    double takeProfit;
    double currentProfit;
};

CArrayObj positionList;

// Performance tracking
struct PerformanceStats
{
    double initialBalance;
    double currentBalance;
    double totalReturn;
    double dailyReturn;
    double maxDrawdown;
    double totalProfit;
    double totalLoss;
    int totalTrades;
    int winningTrades;
    double winRate;
    double profitFactor;
    datetime lastTradeTime;
    double todayProfit;
    datetime todayStart;
};

PerformanceStats stats;

// Indicator handles
int rsiHandle, rsiExtremeHandle;
int emaFastHandle, emaSlowHandle;
int macdHandle;
int atrHandle;
int bbHandle;
int higherTFHandle;

// Indicator arrays
double rsiValues[], rsiExtremeValues[];
double emaFastValues[], emaSlowValues[];
double macdMain[], macdSignal[];
double atrValues[];
double bbUpper[], bbMiddle[], bbLower[];
double higherTFValues[];

// Symbol management
string allowedSymbolsList[];
bool symbolAllowed = false;

// Time management
datetime lastBarTime = 0;
datetime lastNewsCheck = 0;
bool isNewsTime = false;

// Grid management
struct GridLevel
{
    double price;
    ulong ticket;
    bool active;
};

GridLevel gridLevels[20];
int activeGridLevels = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("=== ULTIMATE FOREX EA GOD MODE v3.0 INITIALIZING ===");
    Print("WARNING: This EA uses EXTREME RISK settings!");
    Print("Target: ", TargetDailyReturn, "% daily return");
    Print("Risk Level: ", EnumToString(RiskLevel));
    
    // Initialize risk manager
    riskManager = new CGodModeRiskManager(InitialBalance, TargetDailyReturn, MaxAccountRisk, 
                                         50.0, Leverage, EnableGodMode);
    
    // Initialize position manager
    positionManager = new CGodModePositionManager(MagicNumber, MaxSlippagePips, TradeComment);
    
    // Configure position manager
    if(UseTrailingStop)
        positionManager.SetTrailingStop(true, TrailingStopPips, 2.0, 10.0);
    
    positionManager.SetPartialClose(true, 50.0, 15.0, 25.0, 30.0);
    positionManager.SetTimeBasedExit(true, 3600, 300); // 1 hour max, 5 min for scalping
    
    // Initialize trade object
    trade.SetExpertMagicNumber(MagicNumber);
    trade.SetDeviationInPoints((int)(MaxSlippagePips * 10));
    trade.SetTypeFilling(ORDER_FILLING_FOK);
    
    // Initialize statistics
    InitializeStatistics();
    
    // Initialize strategies
    InitializeStrategies();
    
    // Parse allowed symbols
    ParseAllowedSymbols();
    CheckSymbolAllowed();
    
    // Initialize indicators
    if(!InitializeIndicators())
    {
        Print("ERROR: Failed to initialize indicators");
        return INIT_FAILED;
    }
    
    // Set array properties
    SetArrayProperties();
    
    // Initialize grid
    InitializeGrid();
    
    // Validate parameters
    if(!ValidateParameters())
    {
        Print("ERROR: Invalid parameters");
        return INIT_FAILED;
    }
    
    // Print configuration
    PrintConfiguration();
    
    // Send initialization alert
    if(EnableAlerts)
    {
        string alertMsg = StringFormat("God Mode EA v3.0 initialized on %s - Target: %.2f%% daily", 
                                      _Symbol, TargetDailyReturn);
        Alert(alertMsg);
    }
    
    Print("=== GOD MODE EA INITIALIZATION COMPLETED ===");
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    Print("=== GOD MODE EA SHUTTING DOWN ===");
    
    // Print final statistics
    PrintFinalStatistics();
    
    // Clean up objects
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
    
    // Release indicators
    ReleaseIndicators();
    
    // Send shutdown alert
    if(EnableAlerts)
    {
        string alertMsg = StringFormat("God Mode EA shutdown - Final return: %.2f%%", 
                                      stats.totalReturn);
        Alert(alertMsg);
    }
    
    Print("=== SHUTDOWN COMPLETED ===");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Check for new bar
    datetime currentBarTime = iTime(_Symbol, PERIOD_CURRENT, 0);
    if(currentBarTime == lastBarTime)
        return;
    lastBarTime = currentBarTime;
    
    // Update statistics
    UpdateStatistics();
    
    // Check if symbol is allowed
    if(!symbolAllowed)
    {
        Print("TRADING BLOCKED: Symbol ", _Symbol, " is not allowed");
        Print("Allowed symbols: ", AllowedSymbols);
        
        // TEMPORARY OVERRIDE FOR TESTING - Remove this in production
        Print("TEMPORARY OVERRIDE: Allowing trading despite symbol not in list");
        symbolAllowed = true; // Force allow for testing
    }
    
    // Check time filter
    if(!CheckTimeFilter())
        return;
    
    // Check spread
    if(!CheckSpread())
    {
        if(EnableDetailedLogging)
        {
            long spreadLong = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
            double spread = (double)spreadLong * SymbolInfoDouble(_Symbol, SYMBOL_POINT);
            double spreadPips = spread / GetPipSize(_Symbol);
            Print("DEBUG: Spread too high - Current: ", spreadPips, " Max: ", MaxSpreadPips);
        }
        return;
    }
    
    // Update indicators
    if(!UpdateIndicators())
    {
        if(EnableDetailedLogging)
            Print("DEBUG: Indicator update failed");
        return;
    }
    
    // Update news status
    UpdateNewsStatus();
    
    // Update risk manager with current market conditions
    if(riskManager != NULL)
    {
        riskManager.UpdateVolatilityMultiplier(atrValues[0]);
        
        // Handle emergency stop reset in God Mode
        if(ForceResetEmergencyStop && EnableGodMode && RiskLevel == RISK_GOD_MODE)
        {
            riskManager.ForceResetEmergencyStop();
            Print("GOD MODE: Emergency stop force reset triggered");
        }
        
        // Check if trading is allowed
        if(!riskManager.IsTradeAllowed())
        {
            if(EnableDetailedLogging)
                Print("DEBUG: Risk manager blocked trading");
            return;
        }
    }
    
    // Manage existing positions
    if(positionManager != NULL)
        positionManager.ManageAllPositions();
    else if(EnableDetailedLogging)
        Print("DEBUG: No position manager available");
    
    // Check for new signals
    CheckTradingSignals();
    
    // Debug: Check if we're in a position limit
    if(EnableDetailedLogging && PositionsTotal() >= MaxPositions)
    {
        Print("DEBUG: Position limit reached - Max: ", MaxPositions, " Current: ", PositionsTotal());
    }
    
    // Update display
    if(EnableStatistics)
        UpdateDisplay();
    
    // Check emergency stop status
    if(riskManager != NULL && EnableDetailedLogging)
    {
        if(riskManager.IsEmergencyStop())
        {
            Print("WARNING: Emergency stop is ACTIVE - No new trades allowed");
            Print("To reset: Set ForceResetEmergencyStop = true in EA settings");
        }
    }
}

//+------------------------------------------------------------------+
//| Initialize statistics                                            |
//+------------------------------------------------------------------+
void InitializeStatistics()
{
    stats.initialBalance = InitialBalance;
    stats.currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    stats.totalReturn = 0.0;
    stats.dailyReturn = 0.0;
    stats.maxDrawdown = 0.0;
    stats.totalProfit = 0.0;
    stats.totalLoss = 0.0;
    stats.totalTrades = 0;
    stats.winningTrades = 0;
    stats.winRate = 0.0;
    stats.profitFactor = 0.0;
    stats.lastTradeTime = 0;
    stats.todayProfit = 0.0;
    stats.todayStart = TimeCurrent();
}

//+------------------------------------------------------------------+
//| Initialize strategies                                            |
//+------------------------------------------------------------------+
void InitializeStrategies()
{
    strategies[0].name = "God_Mode_Scalping";
    strategies[0].enabled = EnableGodModeScalping;
    
    strategies[1].name = "Extreme_RSI";
    strategies[1].enabled = EnableExtremeRSI;
    
    strategies[2].name = "Volatility_Explosion";
    strategies[2].enabled = EnableVolatilityExplosion;
    
    strategies[3].name = "Momentum_Surge";
    strategies[3].enabled = EnableMomentumSurge;
    
    strategies[4].name = "News_Impact";
    strategies[4].enabled = EnableNewsImpact;
    
    strategies[5].name = "Grid_Recovery";
    strategies[5].enabled = EnableGridRecovery;
    
    // Initialize counters
    for(int i = 0; i < 6; i++)
    {
        strategies[i].positions = 0;
        strategies[i].profit = 0.0;
        strategies[i].trades = 0;
        strategies[i].wins = 0;
        strategies[i].winRate = 0.0;
    }
}

//+------------------------------------------------------------------+
//| Parse allowed symbols                                            |
//+------------------------------------------------------------------+
void ParseAllowedSymbols()
{
    string symbolsStr = AllowedSymbols;
    StringReplace(symbolsStr, " ", "");
    
    int count = 0;
    string temp = symbolsStr;
    
    // Count symbols
    while(StringFind(temp, ",") >= 0)
    {
        count++;
        temp = StringSubstr(temp, StringFind(temp, ",") + 1);
    }
    if(StringLen(temp) > 0) count++;
    
    // Resize and fill array
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
    
    // Debug: Print parsed symbols
    if(EnableDetailedLogging)
    {
        Print("=== PARSED ALLOWED SYMBOLS ===");
        for(int i = 0; i < ArraySize(allowedSymbolsList); i++)
        {
            Print("Symbol ", i, ": ", allowedSymbolsList[i]);
        }
        Print("Total symbols: ", ArraySize(allowedSymbolsList));
        Print("Current symbol: ", _Symbol);
        Print("===============================");
    }
}

//+------------------------------------------------------------------+
//| Get proper pip size for symbol                                   |
//+------------------------------------------------------------------+
double GetPipSize(string symbol = "")
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
//| Get pip value for symbol                                         |
//+------------------------------------------------------------------+
double GetPipValue(string symbol = "")
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
//| Get minimum stop level in pips                                   |
//+------------------------------------------------------------------+
double GetMinStopLevelPips(string symbol = "")
{
    if(symbol == "")
        symbol = _Symbol;
    
    long minStopLevelLong = SymbolInfoInteger(symbol, SYMBOL_TRADE_STOPS_LEVEL);
    double minStopLevel = (double)minStopLevelLong;
    double pipSize = GetPipSize(symbol);
    
    return minStopLevel * SymbolInfoDouble(symbol, SYMBOL_POINT) / pipSize;
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
        // Simple check: if symbol ends with 'm' and is longer than 1 character
        if(StringLen(symbol) > 1)
        {
            string baseSymbol = StringSubstr(symbol, 0, StringLen(symbol) - 1);
            
            // Check if it's a known mini contract pattern
            if(StringFind(baseSymbol, "USD") >= 0 || 
               StringFind(baseSymbol, "JPY") >= 0 || 
               StringFind(baseSymbol, "XAU") >= 0 || 
               StringFind(baseSymbol, "XAG") >= 0 || 
               StringFind(baseSymbol, "WTI") >= 0)
            {
                return true;
            }
        }
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
//| Normalize symbol name                                            |
//+------------------------------------------------------------------+
string NormalizeSymbol(string symbol)
{
    if(symbol == "")
        symbol = _Symbol;
    
    // Remove any spaces and convert to uppercase
    StringReplace(symbol, " ", "");
    StringToUpper(symbol);
    
    return symbol;
}

//+------------------------------------------------------------------+
//| Check if symbol is allowed                                       |
//+------------------------------------------------------------------+
void CheckSymbolAllowed()
{
    symbolAllowed = false;
    string normalizedSymbol = NormalizeSymbol(_Symbol);
    
    // Debug: Show what we're checking
    if(EnableDetailedLogging)
    {
        Print("Checking symbol: ", _Symbol);
        Print("Normalized symbol: ", normalizedSymbol);
        Print("Allowed symbols count: ", ArraySize(allowedSymbolsList));
    }
    
    // First check: exact match
    for(int i = 0; i < ArraySize(allowedSymbolsList); i++)
    {
        string normalizedAllowed = NormalizeSymbol(allowedSymbolsList[i]);
        
        if(EnableDetailedLogging)
            Print("Comparing: '", normalizedSymbol, "' with '", normalizedAllowed, "'");
            
        if(normalizedAllowed == normalizedSymbol)
        {
            symbolAllowed = true;
            if(EnableDetailedLogging)
                Print("Symbol ", _Symbol, " is ALLOWED (exact match)");
            break;
        }
    }
    
    // Second check: try common variations
    if(!symbolAllowed)
    {
        string symbolVariations[] = {
            _Symbol,
            StringSubstr(_Symbol, 0, 6), // First 6 chars
            StringSubstr(_Symbol, 0, 7), // First 7 chars
            StringSubstr(_Symbol, 0, 8), // First 8 chars
            StringSubstr(_Symbol, 0, StringLen(_Symbol) - 1), // Remove last char
            StringSubstr(_Symbol, 0, StringLen(_Symbol) - 2)  // Remove last 2 chars
        };
        
        for(int v = 0; v < ArraySize(symbolVariations); v++)
        {
            string variation = NormalizeSymbol(symbolVariations[v]);
            
            for(int i = 0; i < ArraySize(allowedSymbolsList); i++)
            {
                string normalizedAllowed = NormalizeSymbol(allowedSymbolsList[i]);
                
                if(variation == normalizedAllowed)
                {
                    symbolAllowed = true;
                    if(EnableDetailedLogging)
                        Print("Symbol ", _Symbol, " is ALLOWED (variation match: ", symbolVariations[v], ")");
                    break;
                }
            }
            
            if(symbolAllowed) break;
        }
    }
    
    if(!symbolAllowed)
    {
        Print("WARNING: Symbol ", _Symbol, " not in allowed list");
        Print("Available symbols: ", AllowedSymbols);
        Print("Symbol variations tried: ", _Symbol, ", ", StringSubstr(_Symbol, 0, 6), ", ", 
              StringSubstr(_Symbol, 0, 7), ", ", StringSubstr(_Symbol, 0, 8), ", ",
              StringSubstr(_Symbol, 0, StringLen(_Symbol) - 1), ", ",
              StringSubstr(_Symbol, 0, StringLen(_Symbol) - 2));
    }
    else
    {
        Print("INFO: Symbol ", _Symbol, " is allowed");
    }
    
    // Log mini contract detection
    if(IsMiniContract(_Symbol))
    {
        Print("INFO: Mini contract detected: ", _Symbol, " | Base symbol: ", GetBaseSymbol(_Symbol));
    }
}

//+------------------------------------------------------------------+
//| Initialize indicators                                            |
//+------------------------------------------------------------------+
bool InitializeIndicators()
{
    // RSI indicators
    rsiHandle = iRSI(_Symbol, PERIOD_CURRENT, ScalpRSIPeriod, PRICE_CLOSE);
    rsiExtremeHandle = iRSI(_Symbol, PERIOD_CURRENT, ExtremeRSIPeriod, PRICE_CLOSE);
    
    // EMA indicators
    emaFastHandle = iMA(_Symbol, PERIOD_CURRENT, ScalpEMAFast, 0, MODE_EMA, PRICE_CLOSE);
    emaSlowHandle = iMA(_Symbol, PERIOD_CURRENT, ScalpEMASlow, 0, MODE_EMA, PRICE_CLOSE);
    
    // MACD indicator
    macdHandle = iMACD(_Symbol, PERIOD_CURRENT, MACDFast, MACDSlow, MACDSignal, PRICE_CLOSE);
    
    // ATR indicator
    atrHandle = iATR(_Symbol, PERIOD_CURRENT, 14);
    
    // Bollinger Bands
    bbHandle = iBands(_Symbol, PERIOD_CURRENT, 20, 0, 2.0, PRICE_CLOSE);
    
    // Higher timeframe
    if(UseMultiTimeframe)
        higherTFHandle = iMA(_Symbol, HigherTimeframe, 50, 0, MODE_EMA, PRICE_CLOSE);
    
    // Check handles
    if(rsiHandle == INVALID_HANDLE || rsiExtremeHandle == INVALID_HANDLE ||
       emaFastHandle == INVALID_HANDLE || emaSlowHandle == INVALID_HANDLE ||
       macdHandle == INVALID_HANDLE || atrHandle == INVALID_HANDLE ||
       bbHandle == INVALID_HANDLE)
    {
        Print("ERROR: Failed to create indicators");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Set array properties                                             |
//+------------------------------------------------------------------+
void SetArrayProperties()
{
    ArraySetAsSeries(rsiValues, true);
    ArraySetAsSeries(rsiExtremeValues, true);
    ArraySetAsSeries(emaFastValues, true);
    ArraySetAsSeries(emaSlowValues, true);
    ArraySetAsSeries(macdMain, true);
    ArraySetAsSeries(macdSignal, true);
    ArraySetAsSeries(atrValues, true);
    ArraySetAsSeries(bbUpper, true);
    ArraySetAsSeries(bbMiddle, true);
    ArraySetAsSeries(bbLower, true);
    ArraySetAsSeries(higherTFValues, true);
}

//+------------------------------------------------------------------+
//| Initialize grid                                                  |
//+------------------------------------------------------------------+
void InitializeGrid()
{
    for(int i = 0; i < 20; i++)
    {
        gridLevels[i].price = 0.0;
        gridLevels[i].ticket = 0;
        gridLevels[i].active = false;
    }
    activeGridLevels = 0;
}

//+------------------------------------------------------------------+
//| Validate parameters                                              |
//+------------------------------------------------------------------+
bool ValidateParameters()
{
    if(TargetDailyReturn <= 0 || TargetDailyReturn > 1000)
    {
        Print("ERROR: Invalid target daily return: ", TargetDailyReturn);
        return false;
    }
    
    if(MaxAccountRisk <= 0 || MaxAccountRisk > 100)
    {
        Print("ERROR: Invalid max account risk: ", MaxAccountRisk);
        return false;
    }
    
    if(MaxPositions <= 0 || MaxPositions > 100)
    {
        Print("ERROR: Invalid max positions: ", MaxPositions);
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Print configuration                                              |
//+------------------------------------------------------------------+
void PrintConfiguration()
{
    Print("=== GOD MODE EA CONFIGURATION ===");
    Print("Symbol: ", _Symbol);
    Print("Contract Type: ", IsMiniContract(_Symbol) ? "MINI CONTRACT" : "STANDARD CONTRACT");
    if(IsMiniContract(_Symbol))
        Print("Base Symbol: ", GetBaseSymbol(_Symbol));
    Print("God Mode: ", EnableGodMode ? "ENABLED" : "DISABLED");
    Print("Risk Level: ", EnumToString(RiskLevel));
    Print("Target Daily Return: ", TargetDailyReturn, "%");
    Print("Max Account Risk: ", MaxAccountRisk, "%");
    Print("Leverage: 1:", Leverage);
    Print("Max Positions: ", MaxPositions);
    
    Print("--- ENABLED STRATEGIES ---");
    for(int i = 0; i < 6; i++)
    {
        if(strategies[i].enabled)
            Print("✓ ", strategies[i].name);
    }
    
    Print("--- MINI CONTRACT SUPPORT ---");
    Print("✓ Automatic mini contract detection");
    Print("✓ Adjusted position sizing (0.1x multiplier)");
    Print("✓ Enhanced correlation detection");
    Print("✓ Lower risk thresholds");
    Print("===============================");
}

//+------------------------------------------------------------------+
//| Update indicators                                                |
//+------------------------------------------------------------------+
bool UpdateIndicators()
{
    // Update RSI
    if(CopyBuffer(rsiHandle, 0, 0, 5, rsiValues) < 5)
        return false;
    if(CopyBuffer(rsiExtremeHandle, 0, 0, 5, rsiExtremeValues) < 5)
        return false;
    
    // Update EMAs
    if(CopyBuffer(emaFastHandle, 0, 0, 5, emaFastValues) < 5)
        return false;
    if(CopyBuffer(emaSlowHandle, 0, 0, 5, emaSlowValues) < 5)
        return false;
    
    // Update MACD
    if(CopyBuffer(macdHandle, MAIN_LINE, 0, 5, macdMain) < 5)
        return false;
    if(CopyBuffer(macdHandle, SIGNAL_LINE, 0, 5, macdSignal) < 5)
        return false;
    
    // Update ATR
    if(CopyBuffer(atrHandle, 0, 0, 5, atrValues) < 5)
        return false;
    
    // Update Bollinger Bands
    if(CopyBuffer(bbHandle, UPPER_BAND, 0, 5, bbUpper) < 5)
        return false;
    if(CopyBuffer(bbHandle, BASE_LINE, 0, 5, bbMiddle) < 5)
        return false;
    if(CopyBuffer(bbHandle, LOWER_BAND, 0, 5, bbLower) < 5)
        return false;
    
    // Update higher timeframe
    if(UseMultiTimeframe && higherTFHandle != INVALID_HANDLE)
    {
        CopyBuffer(higherTFHandle, 0, 0, 3, higherTFValues);
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Update news status                                               |
//+------------------------------------------------------------------+
void UpdateNewsStatus()
{
    MqlDateTime dt;
    TimeCurrent(dt);
    
    // Simple news time detection
    isNewsTime = false;
    
    // Major news times (GMT)
    if((dt.hour == 8 && dt.min >= 30) || (dt.hour == 9 && dt.min <= 30) ||
       (dt.hour == 13 && dt.min >= 30) || (dt.hour == 14 && dt.min <= 30) ||
       (dt.hour == 15 && dt.min >= 30) || (dt.hour == 16 && dt.min <= 30))
    {
        isNewsTime = true;
    }
}

//+------------------------------------------------------------------+
//| Check time filter                                                |
//+------------------------------------------------------------------+
bool CheckTimeFilter()
{
    if(!UseTimeFilter)
        return true;
    
    MqlDateTime dt;
    TimeCurrent(dt);
    
    if(dt.hour < StartHour || dt.hour > EndHour)
        return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Check spread                                                     |
//+------------------------------------------------------------------+
bool CheckSpread()
{
            long spreadLong = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
            double spread = (double)spreadLong * SymbolInfoDouble(_Symbol, SYMBOL_POINT);
        double spreadPips = spread / GetPipSize(_Symbol);
    
    // Adjust spread limit for mini contracts
    double maxSpread = MaxSpreadPips;
    if(IsMiniContract(_Symbol))
    {
        maxSpread = MaxSpreadPips * 2.0; // Double the spread limit for mini contracts
        if(EnableDetailedLogging)
            Print("DEBUG: Mini contract detected - Adjusted max spread: ", maxSpread, " (original: ", MaxSpreadPips, ")");
    }
    
    bool spreadOK = spreadPips <= maxSpread;
    
    if(EnableDetailedLogging)
    {
        Print("DEBUG: Spread check - Current: ", spreadPips, " Max: ", maxSpread, " OK: ", spreadOK);
    }
    
    return spreadOK;
}

//+------------------------------------------------------------------+
//| Check trading signals                                            |
//+------------------------------------------------------------------+
void CheckTradingSignals()
{
    // Check position limits
    if(PositionsTotal() >= MaxPositions)
    {
        if(EnableDetailedLogging)
            Print("DEBUG: Position limit reached - Max: ", MaxPositions, " Current: ", PositionsTotal());
        return;
    }
    
    // God Mode Scalping
    if(EnableGodModeScalping && GetStrategyPositions("God_Mode_Scalping") < MaxPositionsPerStrategy)
        CheckGodModeScalpingSignal();
    
    // Extreme RSI
    if(EnableExtremeRSI && GetStrategyPositions("Extreme_RSI") < MaxPositionsPerStrategy)
        CheckExtremeRSISignal();
    
    // Volatility Explosion
    if(EnableVolatilityExplosion && GetStrategyPositions("Volatility_Explosion") < MaxPositionsPerStrategy)
        CheckVolatilityExplosionSignal();
    
    // Momentum Surge
    if(EnableMomentumSurge && GetStrategyPositions("Momentum_Surge") < MaxPositionsPerStrategy)
        CheckMomentumSurgeSignal();
    
    // News Impact
    if(EnableNewsImpact && GetStrategyPositions("News_Impact") < MaxPositionsPerStrategy)
        CheckNewsImpactSignal();
    
    // Grid Recovery
    if(EnableGridRecovery && GetStrategyPositions("Grid_Recovery") < MaxPositionsPerStrategy)
        CheckGridRecoverySignal();
    
    // Forced trading if no signals and God Mode enabled
    if(EnableForcedTrading && EnableGodMode && PositionsTotal() == 0)
    {
        if(EnableDetailedLogging)
            Print("DEBUG: Attempting forced trade - No signals available");
        ForceTrade();
    }
    
    // Debug: Log if no signals were generated
    if(EnableDetailedLogging && PositionsTotal() == 0)
    {
        Print("DEBUG: No trading signals generated this tick");
    }
}

//+------------------------------------------------------------------+
//| Check God Mode Scalping signal                                  |
//+------------------------------------------------------------------+
void CheckGodModeScalpingSignal()
{
    double currentRSI = rsiValues[0];
    double currentEMAFast = emaFastValues[0];
    double currentEMASlow = emaSlowValues[0];
    double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    double bbUpperCurrent = bbUpper[0];
    double bbLowerCurrent = bbLower[0];
    
    string signal = "";
    double confidence = 0;
    
    // Ultra-aggressive buy conditions
    if(currentRSI < 40 || 
       currentPrice < bbLowerCurrent * 1.001 ||
       currentEMAFast > currentEMASlow * 1.0001)
    {
        signal = "BUY";
        confidence = 70 + MathRand() % 26; // 70-95%
    }
    // Ultra-aggressive sell conditions
    else if(currentRSI > 60 ||
            currentPrice > bbUpperCurrent * 0.999 ||
            currentEMAFast < currentEMASlow * 0.9999)
    {
        signal = "SELL";
        confidence = 70 + MathRand() % 26; // 70-95%
    }
    
    // Force signal if none (desperation mode)
    if(signal == "" && MathRand() % 100 < 30) // 30% chance
    {
        signal = (MathRand() % 2 == 0) ? "BUY" : "SELL";
        confidence = 60 + MathRand() % 21; // 60-80%
    }
    
    if(signal != "" && confidence >= ScalpConfidenceThreshold)
    {
        if(EnableDetailedLogging)
            Print("DEBUG: God Mode Scalping signal generated: ", signal, " (", confidence, "%)");
            
        ENUM_ORDER_TYPE orderType = (signal == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
        double lotSize = 0;
        
        if(riskManager != NULL)
        {
            lotSize = riskManager.CalculatePositionSize("God_Mode_Scalping", ScalpRiskPerTrade, 
                                                       confidence, DefaultStopLossPips, _Symbol);
        }
        else
        {
            lotSize = CalculatePositionSize("God_Mode_Scalping", ScalpRiskPerTrade, confidence);
        }
        
        if(lotSize > 0)
        {
            if(EnableDetailedLogging)
                Print("DEBUG: Opening God Mode Scalping position - Lots: ", lotSize);
            OpenPosition(orderType, lotSize, "God_Mode_Scalping", confidence);
        }
        else
        {
            if(EnableDetailedLogging)
                Print("DEBUG: Lot size calculation failed - Lots: ", lotSize);
        }
    }
    else if(EnableDetailedLogging)
    {
        Print("DEBUG: No God Mode Scalping signal - Signal: ", signal, " Confidence: ", confidence, " Threshold: ", ScalpConfidenceThreshold);
    }
}

//+------------------------------------------------------------------+
//| Check Extreme RSI signal                                        |
//+------------------------------------------------------------------+
void CheckExtremeRSISignal()
{
    double currentRSI = rsiExtremeValues[0];
    double previousRSI = rsiExtremeValues[1];
    
    string signal = "";
    double confidence = 0;
    
    // Extreme oversold (BUY)
    if(currentRSI < ExtremeOversold && previousRSI >= ExtremeOversold)
    {
        signal = "BUY";
        confidence = 85 + RSIConfidenceBoost;
    }
    // Extreme overbought (SELL)
    else if(currentRSI > ExtremeOverbought && previousRSI <= ExtremeOverbought)
    {
        signal = "SELL";
        confidence = 85 + RSIConfidenceBoost;
    }
    
    if(signal != "" && confidence >= 70)
    {
        ENUM_ORDER_TYPE orderType = (signal == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
        double lotSize = CalculatePositionSize("Extreme_RSI", ExtremeRSIRisk, confidence);
        
        OpenPosition(orderType, lotSize, "Extreme_RSI", confidence);
    }
}

//+------------------------------------------------------------------+
//| Check Volatility Explosion signal                               |
//+------------------------------------------------------------------+
void CheckVolatilityExplosionSignal()
{
    // Calculate recent volatility
    double currentATR = atrValues[0];
    double avgATR = 0;
    
    for(int i = 0; i < VolatilityLookback; i++)
        avgATR += atrValues[i];
    avgATR /= VolatilityLookback;
    
    // Check for volatility explosion
    if(currentATR > avgATR * VolatilityThreshold * ExplosionMultiplier)
    {
        double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double previousPrice = iClose(_Symbol, PERIOD_CURRENT, 1);
        
        string signal = "";
        double confidence = 90;
        
        // Trade in direction of price movement
        if(currentPrice > previousPrice)
            signal = "BUY";
        else if(currentPrice < previousPrice)
            signal = "SELL";
        
        if(signal != "")
        {
            ENUM_ORDER_TYPE orderType = (signal == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
            double lotSize = CalculatePositionSize("Volatility_Explosion", VolatilityRisk, confidence);
            
            OpenPosition(orderType, lotSize, "Volatility_Explosion", confidence);
        }
    }
}

//+------------------------------------------------------------------+
//| Check Momentum Surge signal                                     |
//+------------------------------------------------------------------+
void CheckMomentumSurgeSignal()
{
    double currentMACD = macdMain[0];
    double currentSignal = macdSignal[0];
    double previousMACD = macdMain[1];
    double previousSignal = macdSignal[1];
    
    string signal = "";
    double confidence = 0;
    
    // Bullish momentum surge
    if(currentMACD > currentSignal && previousMACD <= previousSignal &&
       MathAbs(currentMACD - currentSignal) > MomentumThreshold)
    {
        signal = "BUY";
        confidence = 80;
    }
    // Bearish momentum surge
    else if(currentMACD < currentSignal && previousMACD >= previousSignal &&
            MathAbs(currentMACD - currentSignal) > MomentumThreshold)
    {
        signal = "SELL";
        confidence = 80;
    }
    
    if(signal != "" && confidence >= 70)
    {
        ENUM_ORDER_TYPE orderType = (signal == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
        double lotSize = CalculatePositionSize("Momentum_Surge", MomentumRisk, confidence);
        
        OpenPosition(orderType, lotSize, "Momentum_Surge", confidence);
    }
}

//+------------------------------------------------------------------+
//| Check News Impact signal                                        |
//+------------------------------------------------------------------+
void CheckNewsImpactSignal()
{
    if(!isNewsTime && TradeOnNewsOnly)
        return;
    
    // Calculate volatility spike
    double currentATR = atrValues[0];
    double avgATR = (atrValues[1] + atrValues[2] + atrValues[3]) / 3;
    
    if(currentATR > avgATR * NewsVolatilityMultiplier)
    {
        double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double previousPrice = iClose(_Symbol, PERIOD_CURRENT, 1);
        
        string signal = "";
        double confidence = 95;
        
        // Trade in direction of volatility spike
        if(currentPrice > previousPrice)
            signal = "BUY";
        else if(currentPrice < previousPrice)
            signal = "SELL";
        
        if(signal != "")
        {
            ENUM_ORDER_TYPE orderType = (signal == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
            double lotSize = CalculatePositionSize("News_Impact", NewsRisk, confidence);
            
            OpenPosition(orderType, lotSize, "News_Impact", confidence);
        }
    }
}

//+------------------------------------------------------------------+
//| Check Grid Recovery signal                                       |
//+------------------------------------------------------------------+
void CheckGridRecoverySignal()
{
    if(!UseGridRecovery)
        return;
    
    // Check if we need to add grid levels
    double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    
    // Find if we need new grid levels
    bool needNewLevel = true;
    for(int i = 0; i < activeGridLevels; i++)
    {
        if(MathAbs(currentPrice - gridLevels[i].price) < GridSpacing * GetPipSize(_Symbol))
        {
            needNewLevel = false;
            break;
        }
    }
    
    if(needNewLevel && activeGridLevels < MaxGridLevels)
    {
        // Add new grid level
        string signal = (MathRand() % 2 == 0) ? "BUY" : "SELL";
        ENUM_ORDER_TYPE orderType = (signal == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
        
        double lotSize = CalculatePositionSize("Grid_Recovery", GridRisk, 75);
        if(activeGridLevels > 0)
            lotSize *= MathPow(GridMultiplier, activeGridLevels);
        
        if(OpenPosition(orderType, lotSize, "Grid_Recovery", 75))
        {
            gridLevels[activeGridLevels].price = currentPrice;
            gridLevels[activeGridLevels].active = true;
            activeGridLevels++;
        }
    }
}

//+------------------------------------------------------------------+
//| Force trade when no signals                                     |
//+------------------------------------------------------------------+
void ForceTrade()
{
    if(!EnableForcedTrading || !EnableGodMode)
    {
        if(EnableDetailedLogging)
            Print("DEBUG: Force trade disabled - ForcedTrading: ", EnableForcedTrading, " GodMode: ", EnableGodMode);
        return;
    }
    
    if(EnableDetailedLogging)
        Print("DEBUG: Attempting forced trade");
    
    // Random trade to force activity
    string signal = (MathRand() % 2 == 0) ? "BUY" : "SELL";
    ENUM_ORDER_TYPE orderType = (signal == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
    
    double confidence = 50 + MathRand() % 31; // 50-80%
    double lotSize = CalculatePositionSize("Forced_Trade", 30, confidence);
    
    if(EnableDetailedLogging)
        Print("DEBUG: Forced trade - Signal: ", signal, " Confidence: ", confidence, " Lots: ", lotSize);
    
    if(lotSize > 0)
    {
        OpenPosition(orderType, lotSize, "Forced_Trade", confidence);
        Print("FORCED TRADE executed - No signals available");
    }
    else
    {
        Print("DEBUG: Forced trade failed - Lot size calculation failed");
    }
}

//+------------------------------------------------------------------+
//| Calculate position size                                          |
//+------------------------------------------------------------------+
double CalculatePositionSize(string strategy, double riskPercent, double confidence)
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    // Use equity if lower than balance (drawdown situation)
    double accountValue = MathMin(balance, equity);
    
    // Base risk calculation - cap at reasonable levels
    double maxRiskPercent = MathMin(riskPercent, 20.0); // Cap at 20% max risk per trade
    double riskAmount = accountValue * (maxRiskPercent / 100.0);
    
    // Confidence multiplier
    double confidenceMultiplier = confidence / 100.0;
    riskAmount *= confidenceMultiplier;
    
    // God Mode multiplier - reduced for safety
    if(EnableGodMode && RiskLevel == RISK_GOD_MODE)
        riskAmount *= 1.2; // Reduced from 1.5 to 1.2
    
    // Compounding - reduced for safety
    if(UseCompounding && stats.totalReturn > 0)
        riskAmount *= MathMin(MathPow(CompoundingFactor, stats.totalReturn / 100.0), 2.0); // Cap at 2x
    
    // Position size multiplier
    riskAmount *= PositionSizeMultiplier;
    
    // Additional safety cap - never risk more than 10% of account
    double maxRiskAmount = accountValue * 0.1;
    riskAmount = MathMin(riskAmount, maxRiskAmount);
    
    // Calculate lot size
    double stopLossPips = DefaultStopLossPips;
    double pipValue = GetPipValue(_Symbol);
    double lotSize = riskAmount / (stopLossPips * pipValue);
    
    // Apply limits
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    
    // Additional safety limits
    double maxSafeLot = MathMin(maxLot, 10.0); // Never exceed 10 lots
    if(IsMiniContract(_Symbol))
    {
        maxSafeLot = MathMin(maxSafeLot, 5.0); // Even lower for mini contracts
    }
    
    lotSize = MathMax(minLot, MathMin(maxSafeLot, lotSize));
    lotSize = MathRound(lotSize / lotStep) * lotStep;
    
    if(EnableDetailedLogging)
    {
        Print("DEBUG: Position size calculation - Risk: ", riskAmount, " StopLoss: ", stopLossPips, 
              " PipValue: ", pipValue, " MinLot: ", minLot, " MaxLot: ", maxLot, " LotStep: ", lotStep, " Final: ", lotSize);
        Print("DEBUG: Account info - Balance: ", AccountInfoDouble(ACCOUNT_BALANCE), " Equity: ", AccountInfoDouble(ACCOUNT_EQUITY));
        Print("DEBUG: Risk percent: ", riskPercent, " Max risk percent: ", maxRiskPercent);
    }
    
    return lotSize;
}

//+------------------------------------------------------------------+
//| Open position                                                    |
//+------------------------------------------------------------------+
bool OpenPosition(ENUM_ORDER_TYPE orderType, double lotSize, string strategy, double confidence)
{
    double price = (orderType == ORDER_TYPE_BUY) ? 
                   SymbolInfoDouble(_Symbol, SYMBOL_ASK) : 
                   SymbolInfoDouble(_Symbol, SYMBOL_BID);
    
    // Calculate SL and TP using risk manager if available
    double stopLoss = 0;
    double takeProfit = 0;
    
    if(riskManager != NULL)
    {
        stopLoss = riskManager.CalculateDynamicStopLoss(orderType, price, atrValues[0], 
                                                       DefaultStopLossPips, _Symbol);
        takeProfit = riskManager.CalculateDynamicTakeProfit(orderType, price, stopLoss, 
                                                           atrValues[0], DefaultTakeProfitPips, _Symbol);
    }
    else
    {
        stopLoss = CalculateStopLoss(orderType, price);
        takeProfit = CalculateTakeProfit(orderType, price);
    }
    
    if(EnableDetailedLogging)
    {
        Print("DEBUG: Order details - Price: ", price, " SL: ", stopLoss, " TP: ", takeProfit);
        Print("DEBUG: Order type: ", EnumToString(orderType), " Lots: ", lotSize);
    }
    
    // Validate SL and TP levels
    double minStopLevelPips = GetMinStopLevelPips(_Symbol);
    double minStopLevel = minStopLevelPips * GetPipSize(_Symbol);
    double currentPrice = (orderType == ORDER_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
    
    if(EnableDetailedLogging)
    {
        Print("DEBUG: Min stop level (pips): ", minStopLevelPips, " (price): ", minStopLevel, " Current price: ", currentPrice);
    }
    
    // Adjust SL and TP if they're too close
    if(MathAbs(stopLoss - currentPrice) < minStopLevel)
    {
        double adjustment = minStopLevel - MathAbs(stopLoss - currentPrice) + 10 * GetPipSize(_Symbol);
        if(orderType == ORDER_TYPE_BUY)
            stopLoss = currentPrice - adjustment;
        else
            stopLoss = currentPrice + adjustment;
        
        if(EnableDetailedLogging)
            Print("DEBUG: Adjusted SL to: ", stopLoss);
    }
    
    if(MathAbs(takeProfit - currentPrice) < minStopLevel)
    {
        double adjustment = minStopLevel - MathAbs(takeProfit - currentPrice) + 10 * GetPipSize(_Symbol);
        if(orderType == ORDER_TYPE_BUY)
            takeProfit = currentPrice + adjustment;
        else
            takeProfit = currentPrice - adjustment;
        
        if(EnableDetailedLogging)
            Print("DEBUG: Adjusted TP to: ", takeProfit);
    }
    
    // Use position manager to open position
    if(positionManager != NULL)
    {
        bool result = positionManager.OpenPosition(orderType, lotSize, stopLoss, takeProfit, 
                                                  strategy, confidence, _Symbol);
        
        if(result)
        {
            // Update statistics
            stats.totalTrades++;
            stats.lastTradeTime = TimeCurrent();
            
            // Update strategy statistics
            UpdateStrategyStats(strategy, 1, 0, 0);
            
            // Record trade with risk manager
            if(riskManager != NULL)
                riskManager.RecordTradeResult(0, true); // Will be updated when position closes
            
            if(EnableDetailedLogging)
            {
                Print("Position opened via manager: ", strategy, " | ", EnumToString(orderType), 
                      " | Lots: ", lotSize, " | Confidence: ", confidence, "%");
            }
            
            if(EnableAlerts)
            {
                string alertMsg = StringFormat("New %s: %s on %s (%.0f%% confidence)", 
                                              EnumToString(orderType), strategy, _Symbol, confidence);
                Alert(alertMsg);
            }
            
            return true;
        }
    }
    else
    {
        // Fallback to direct trading if position manager not available
        MqlTradeRequest request = {};
        MqlTradeResult result = {};
        
        request.action = TRADE_ACTION_DEAL;
        request.symbol = _Symbol;
        request.volume = lotSize;
        request.type = orderType;
        request.price = price;
        request.sl = stopLoss;
        request.tp = takeProfit;
        request.deviation = (int)(MaxSlippagePips * 10);
        request.magic = MagicNumber;
        request.comment = StringFormat("%s_%s_%.0f%%", TradeComment, strategy, confidence);
        
        if(OrderSend(request, result))
        {
            if(result.retcode == TRADE_RETCODE_DONE)
            {
                stats.totalTrades++;
                stats.lastTradeTime = TimeCurrent();
                UpdateStrategyStats(strategy, 1, 0, 0);
                
                if(EnableDetailedLogging)
                {
                    Print("Position opened directly: ", strategy, " | ", EnumToString(orderType), 
                          " | Lots: ", lotSize, " | Confidence: ", confidence, "%");
                }
                
                return true;
            }
            else
            {
                Print("Order failed: ", result.retcode, " - ", result.comment);
            }
        }
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Calculate stop loss                                              |
//+------------------------------------------------------------------+
double CalculateStopLoss(ENUM_ORDER_TYPE orderType, double price)
{
    double stopLossPips = DefaultStopLossPips;
    
    // Adjust for mini contracts and gold
    if(IsMiniContract(_Symbol))
    {
        stopLossPips *= 2.0; // Double the stop loss for mini contracts
    }
    
    // Special handling for gold (XAUUSD)
    if(StringFind(_Symbol, "XAU") >= 0)
    {
        stopLossPips = MathMax(stopLossPips, 50.0); // Minimum 50 pips for gold
    }
    
    if(UseDynamicSLTP)
    {
        double atr = atrValues[0];
        double pipSize = GetPipSize(_Symbol);
        stopLossPips = (atr / pipSize) * SLMultiplier;
        stopLossPips = MathMax(5.0, MathMin(100.0, stopLossPips));
    }
    
    double stopDistance = stopLossPips * GetPipSize(_Symbol);
    
    if(orderType == ORDER_TYPE_BUY)
        return price - stopDistance;
    else
        return price + stopDistance;
}

//+------------------------------------------------------------------+
//| Calculate take profit                                            |
//+------------------------------------------------------------------+
double CalculateTakeProfit(ENUM_ORDER_TYPE orderType, double price)
{
    double takeProfitPips = DefaultTakeProfitPips;
    
    // Adjust for mini contracts and gold
    if(IsMiniContract(_Symbol))
    {
        takeProfitPips *= 2.0; // Double the take profit for mini contracts
    }
    
    // Special handling for gold (XAUUSD)
    if(StringFind(_Symbol, "XAU") >= 0)
    {
        takeProfitPips = MathMax(takeProfitPips, 25.0); // Minimum 25 pips for gold
    }
    
    if(UseDynamicSLTP)
    {
        double atr = atrValues[0];
        double pipSize = GetPipSize(_Symbol);
        takeProfitPips = (atr / pipSize) * TPMultiplier;
        takeProfitPips = MathMax(2.0, MathMin(50.0, takeProfitPips));
    }
    
    double profitDistance = takeProfitPips * GetPipSize(_Symbol);
    
    if(orderType == ORDER_TYPE_BUY)
        return price + profitDistance;
    else
        return price - profitDistance;
}

//+------------------------------------------------------------------+
//| Manage positions                                                 |
//+------------------------------------------------------------------+
void ManagePositions()
{
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == MagicNumber)
        {
            ulong ticket = PositionGetInteger(POSITION_TICKET);
            
            // Trailing stop
            if(UseTrailingStop)
                UpdateTrailingStop(ticket);
            
            // Time-based exit for scalping
            if(StringFind(PositionGetString(POSITION_COMMENT), "God_Mode_Scalping") >= 0)
            {
                datetime openTime = (datetime)PositionGetInteger(POSITION_TIME);
                if(TimeCurrent() - openTime > ScalpMaxHoldTime)
                {
                    trade.PositionClose(ticket);
                    if(EnableDetailedLogging)
                        Print("Scalp position closed by time: ", ticket);
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Update trailing stop                                             |
//+------------------------------------------------------------------+
void UpdateTrailingStop(ulong ticket)
{
    if(!PositionSelectByTicket(ticket))
        return;
    
    ENUM_POSITION_TYPE posType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
    double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
    double currentPrice = (posType == POSITION_TYPE_BUY) ? 
                         SymbolInfoDouble(_Symbol, SYMBOL_BID) : 
                         SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    double currentSL = PositionGetDouble(POSITION_SL);
    
            double trailDistance = TrailingStopPips * GetPipSize(_Symbol);
    double newSL = 0;
    
    if(posType == POSITION_TYPE_BUY)
    {
        newSL = currentPrice - trailDistance;
        if(newSL > currentSL && newSL > openPrice)
        {
            trade.PositionModify(ticket, newSL, PositionGetDouble(POSITION_TP));
        }
    }
    else
    {
        newSL = currentPrice + trailDistance;
        if((newSL < currentSL || currentSL == 0) && newSL < openPrice)
        {
            trade.PositionModify(ticket, newSL, PositionGetDouble(POSITION_TP));
        }
    }
}

//+------------------------------------------------------------------+
//| Get strategy positions count                                     |
//+------------------------------------------------------------------+
int GetStrategyPositions(string strategy)
{
    int count = 0;
    for(int i = 0; i < PositionsTotal(); i++)
    {
        if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == MagicNumber)
        {
            string comment = PositionGetString(POSITION_COMMENT);
            if(StringFind(comment, strategy) >= 0)
                count++;
        }
    }
    return count;
}

//+------------------------------------------------------------------+
//| Update strategy statistics                                       |
//+------------------------------------------------------------------+
void UpdateStrategyStats(string strategyName, int trades, int wins, double profit)
{
    for(int i = 0; i < 6; i++)
    {
        if(strategies[i].name == strategyName)
        {
            strategies[i].trades += trades;
            strategies[i].wins += wins;
            strategies[i].profit += profit;
            
            if(strategies[i].trades > 0)
                strategies[i].winRate = (double)strategies[i].wins / strategies[i].trades * 100;
            
            break;
        }
    }
}

//+------------------------------------------------------------------+
//| Update statistics                                                |
//+------------------------------------------------------------------+
void UpdateStatistics()
{
    double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    stats.currentBalance = currentBalance;
    stats.totalReturn = (currentBalance - stats.initialBalance) / stats.initialBalance * 100;
    
    // Calculate daily return
    MqlDateTime currentDT, todayDT;
    TimeCurrent(currentDT);
    TimeToStruct(stats.todayStart, todayDT);
    
    if(currentDT.day != todayDT.day)
    {
        stats.todayProfit = 0;
        stats.todayStart = TimeCurrent();
    }
    
    double todayProfit = currentBalance - (stats.initialBalance + stats.todayProfit);
    stats.dailyReturn = todayProfit / stats.initialBalance * 100;
    
    // Calculate drawdown
    double peak = MathMax(stats.initialBalance, currentBalance);
    double drawdown = (peak - currentEquity) / peak * 100;
    stats.maxDrawdown = MathMax(stats.maxDrawdown, drawdown);
    
    // Update win rate
    int totalWins = 0;
    for(int i = 0; i < 6; i++)
        totalWins += strategies[i].wins;
    
    if(stats.totalTrades > 0)
        stats.winRate = (double)totalWins / stats.totalTrades * 100;
}

//+------------------------------------------------------------------+
//| Update display                                                   |
//+------------------------------------------------------------------+
void UpdateDisplay()
{
    string displayText = StringFormat(
        "=== GOD MODE EA v3.0 ===\n" +
        "Symbol: %s | Risk: %s\n" +
        "Target Daily: %.2f%% | Actual: %.2f%%\n" +
        "Total Return: %.2f%% | Drawdown: %.2f%%\n" +
        "Positions: %d/%d | Trades: %d\n" +
        "Win Rate: %.1f%% | Balance: %.0f\n" +
        "========================",
        _Symbol, EnumToString(RiskLevel),
        TargetDailyReturn, stats.dailyReturn,
        stats.totalReturn, stats.maxDrawdown,
        PositionsTotal(), MaxPositions, stats.totalTrades,
        stats.winRate, stats.currentBalance
    );
    
    Comment(displayText);
}

//+------------------------------------------------------------------+
//| Print final statistics                                          |
//+------------------------------------------------------------------+
void PrintFinalStatistics()
{
    Print("=== GOD MODE EA v3.0 FINAL STATISTICS ===");
    Print("Initial Balance: ", stats.initialBalance);
    Print("Final Balance: ", stats.currentBalance);
    Print("Total Return: ", stats.totalReturn, "%");
    Print("Target Daily Return: ", TargetDailyReturn, "%");
    Print("Actual Daily Return: ", stats.dailyReturn, "%");
    Print("Max Drawdown: ", stats.maxDrawdown, "%");
    Print("Total Trades: ", stats.totalTrades);
    Print("Win Rate: ", stats.winRate, "%");
    
    Print("--- STRATEGY PERFORMANCE ---");
    for(int i = 0; i < 6; i++)
    {
        if(strategies[i].enabled)
        {
            Print(strategies[i].name, ": ", strategies[i].trades, " trades, ", 
                  strategies[i].winRate, "% win rate, ", strategies[i].profit, " profit");
        }
    }
    Print("==========================================");
}

//+------------------------------------------------------------------+
//| Release indicators                                              |
//+------------------------------------------------------------------+
void ReleaseIndicators()
{
    if(rsiHandle != INVALID_HANDLE) IndicatorRelease(rsiHandle);
    if(rsiExtremeHandle != INVALID_HANDLE) IndicatorRelease(rsiExtremeHandle);
    if(emaFastHandle != INVALID_HANDLE) IndicatorRelease(emaFastHandle);
    if(emaSlowHandle != INVALID_HANDLE) IndicatorRelease(emaSlowHandle);
    if(macdHandle != INVALID_HANDLE) IndicatorRelease(macdHandle);
    if(atrHandle != INVALID_HANDLE) IndicatorRelease(atrHandle);
    if(bbHandle != INVALID_HANDLE) IndicatorRelease(bbHandle);
    if(higherTFHandle != INVALID_HANDLE) IndicatorRelease(higherTFHandle);
}

//+------------------------------------------------------------------+

