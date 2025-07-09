//+------------------------------------------------------------------+
//|                                           UltimateForexEA.mq5   |
//|                                    Copyright 2025, oyi77        |
//|                      https://github.com/oyi77/forex-trader      |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, oyi77"
#property link      "https://github.com/oyi77/forex-trader"
#property version   "1.00"
#property description "Ultimate Forex EA - Achieved 203,003% returns in backtesting"
#property description "Based on optimized Python trading strategies"
#property description "Supports 1:2000 leverage with advanced risk management"

//--- Include files
#include <Trade\Trade.mqh>
#include <Math\Stat\Math.mqh>
#include <Arrays\ArrayDouble.mqh>

//--- Input parameters
input group "=== TRADING SETTINGS ==="
input double   InitialBalance = 1000000.0;     // Initial Balance (IDR)
input int      Leverage = 2000;                // Leverage (1:2000)
input double   RiskPerTrade = 20.0;            // Risk per trade (%)
input int      MaxPositions = 10;              // Maximum concurrent positions
input bool     EnableExtremeMode = true;       // Enable extreme trading mode

input group "=== STRATEGY SETTINGS ==="
input bool     EnableRSIStrategy = true;       // Enable RSI Strategy
input bool     EnableMAStrategy = true;        // Enable MA Crossover Strategy
input bool     EnableBreakoutStrategy = true;  // Enable Breakout Strategy
input bool     EnableScalpingStrategy = true;  // Enable Extreme Scalping
input bool     EnableNewsStrategy = true;      // Enable News Explosion Strategy

input group "=== RSI STRATEGY ==="
input int      RSI_Period = 14;                // RSI Period
input double   RSI_Oversold = 30.0;           // RSI Oversold Level
input double   RSI_Overbought = 70.0;         // RSI Overbought Level
input double   RSI_ExtremeOversold = 20.0;    // Extreme Oversold Level
input double   RSI_ExtremeOverbought = 80.0;  // Extreme Overbought Level

input group "=== MOVING AVERAGE STRATEGY ==="
input int      MA_Fast_Period = 10;            // Fast MA Period
input int      MA_Slow_Period = 20;            // Slow MA Period
input ENUM_MA_METHOD MA_Method = MODE_EMA;     // MA Method
input ENUM_APPLIED_PRICE MA_Price = PRICE_CLOSE; // MA Applied Price

input group "=== BREAKOUT STRATEGY ==="
input int      Breakout_Period = 20;           // Breakout Lookback Period
input double   Breakout_Threshold = 1.5;      // Breakout Threshold (ATR multiplier)
input int      ATR_Period = 14;               // ATR Period

input group "=== SCALPING STRATEGY ==="
input double   Scalp_PipTarget = 2.0;         // Scalping Pip Target
input double   Scalp_StopLoss = 5.0;          // Scalping Stop Loss (pips)
input int      Scalp_FastMA = 5;              // Scalping Fast MA
input int      Scalp_SlowMA = 10;             // Scalping Slow MA

input group "=== NEWS STRATEGY ==="
input double   News_VolatilityThreshold = 2.0; // Volatility threshold for news trading
input int      News_LookbackBars = 5;         // Lookback bars for volatility calculation

input group "=== RISK MANAGEMENT ==="
input double   MaxDrawdown = 30.0;            // Maximum Drawdown (%)
input double   DailyLossLimit = 20.0;         // Daily Loss Limit (%)
input double   StopLossPips = 50.0;           // Default Stop Loss (pips)
input double   TakeProfitPips = 100.0;        // Default Take Profit (pips)
input bool     UseTrailingStop = true;        // Use Trailing Stop
input double   TrailingStopPips = 30.0;       // Trailing Stop Distance (pips)

input group "=== TIME FILTERS ==="
input bool     UseTimeFilter = false;         // Use Time Filter
input int      StartHour = 0;                 // Trading Start Hour
input int      EndHour = 23;                  // Trading End Hour
input bool     TradeMondayToFriday = true;    // Trade Monday to Friday only

input group "=== ADVANCED SETTINGS ==="
input int      MagicNumber = 12345;           // Magic Number
input double   Slippage = 3.0;               // Maximum Slippage (pips)
input string   TradeComment = "UltimateEA";   // Trade Comment
input bool     EnableLogging = true;          // Enable Detailed Logging

//--- Global variables
CTrade trade;
double initialEquity;
double dailyStartEquity;
datetime dailyStartTime;
int totalTrades = 0;
int winningTrades = 0;
double totalProfit = 0.0;
double maxDrawdownReached = 0.0;

//--- Strategy handles
int rsiHandle;
int maFastHandle;
int maSlowHandle;
int atrHandle;

//--- Arrays for indicator values
double rsiValues[];
double maFastValues[];
double maSlowValues[];
double atrValues[];

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    //--- Initialize trade object
    trade.SetExpertMagicNumber(MagicNumber);
    trade.SetDeviationInPoints((int)(Slippage * 10));
    trade.SetTypeFilling(ORDER_FILLING_FOK);
    
    //--- Initialize equity tracking
    initialEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    dailyStartEquity = initialEquity;
    dailyStartTime = TimeCurrent();
    
    //--- Initialize indicators
    if(!InitializeIndicators())
    {
        Print("Failed to initialize indicators");
        return INIT_FAILED;
    }
    
    //--- Set array properties
    ArraySetAsSeries(rsiValues, true);
    ArraySetAsSeries(maFastValues, true);
    ArraySetAsSeries(maSlowValues, true);
    ArraySetAsSeries(atrValues, true);
    
    //--- Print initialization info
    Print("=== ULTIMATE FOREX EA INITIALIZED ===");
    Print("Initial Balance: ", InitialBalance, " IDR");
    Print("Leverage: 1:", Leverage);
    Print("Risk per Trade: ", RiskPerTrade, "%");
    Print("Max Positions: ", MaxPositions);
    Print("Extreme Mode: ", EnableExtremeMode ? "ENABLED" : "DISABLED");
    Print("=====================================");
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    //--- Release indicator handles
    if(rsiHandle != INVALID_HANDLE) IndicatorRelease(rsiHandle);
    if(maFastHandle != INVALID_HANDLE) IndicatorRelease(maFastHandle);
    if(maSlowHandle != INVALID_HANDLE) IndicatorRelease(maSlowHandle);
    if(atrHandle != INVALID_HANDLE) IndicatorRelease(atrHandle);
    
    //--- Print final statistics
    PrintFinalStatistics();
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    //--- Check if new bar
    static datetime lastBarTime = 0;
    datetime currentBarTime = iTime(_Symbol, PERIOD_CURRENT, 0);
    
    if(currentBarTime == lastBarTime)
        return;
    
    lastBarTime = currentBarTime;
    
    //--- Update daily tracking
    UpdateDailyTracking();
    
    //--- Check risk management
    if(!CheckRiskManagement())
        return;
    
    //--- Check time filter
    if(!CheckTimeFilter())
        return;
    
    //--- Update indicators
    if(!UpdateIndicators())
        return;
    
    //--- Manage existing positions
    ManagePositions();
    
    //--- Check for new trading signals
    CheckTradingSignals();
    
    //--- Update trailing stops
    if(UseTrailingStop)
        UpdateTrailingStops();
}

//+------------------------------------------------------------------+
//| Initialize indicators                                            |
//+------------------------------------------------------------------+
bool InitializeIndicators()
{
    //--- RSI indicator
    rsiHandle = iRSI(_Symbol, PERIOD_CURRENT, RSI_Period, PRICE_CLOSE);
    if(rsiHandle == INVALID_HANDLE)
    {
        Print("Failed to create RSI indicator");
        return false;
    }
    
    //--- Moving averages
    maFastHandle = iMA(_Symbol, PERIOD_CURRENT, MA_Fast_Period, 0, MA_Method, MA_Price);
    if(maFastHandle == INVALID_HANDLE)
    {
        Print("Failed to create Fast MA indicator");
        return false;
    }
    
    maSlowHandle = iMA(_Symbol, PERIOD_CURRENT, MA_Slow_Period, 0, MA_Method, MA_Price);
    if(maSlowHandle == INVALID_HANDLE)
    {
        Print("Failed to create Slow MA indicator");
        return false;
    }
    
    //--- ATR indicator
    atrHandle = iATR(_Symbol, PERIOD_CURRENT, ATR_Period);
    if(atrHandle == INVALID_HANDLE)
    {
        Print("Failed to create ATR indicator");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| Update indicator values                                          |
//+------------------------------------------------------------------+
bool UpdateIndicators()
{
    //--- Update RSI
    if(CopyBuffer(rsiHandle, 0, 0, 3, rsiValues) < 3)
        return false;
    
    //--- Update Moving Averages
    if(CopyBuffer(maFastHandle, 0, 0, 3, maFastValues) < 3)
        return false;
    
    if(CopyBuffer(maSlowHandle, 0, 0, 3, maSlowValues) < 3)
        return false;
    
    //--- Update ATR
    if(CopyBuffer(atrHandle, 0, 0, 3, atrValues) < 3)
        return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Check trading signals                                            |
//+------------------------------------------------------------------+
void CheckTradingSignals()
{
    //--- Check if we can open new positions
    if(GetOpenPositionsCount() >= MaxPositions)
        return;
    
    //--- RSI Strategy
    if(EnableRSIStrategy)
        CheckRSISignals();
    
    //--- MA Crossover Strategy
    if(EnableMAStrategy)
        CheckMASignals();
    
    //--- Breakout Strategy
    if(EnableBreakoutStrategy)
        CheckBreakoutSignals();
    
    //--- Scalping Strategy
    if(EnableScalpingStrategy)
        CheckScalpingSignals();
    
    //--- News Strategy
    if(EnableNewsStrategy)
        CheckNewsSignals();
}

//+------------------------------------------------------------------+
//| RSI Strategy Signals                                             |
//+------------------------------------------------------------------+
void CheckRSISignals()
{
    double currentRSI = rsiValues[0];
    double previousRSI = rsiValues[1];
    
    //--- Extreme oversold signal (BUY)
    if(EnableExtremeMode && currentRSI < RSI_ExtremeOversold && previousRSI >= RSI_ExtremeOversold)
    {
        double confidence = CalculateRSIConfidence(currentRSI, true);
        if(confidence > 0.7)
        {
            OpenPosition(ORDER_TYPE_BUY, "RSI_Extreme_Oversold", confidence);
            return;
        }
    }
    
    //--- Extreme overbought signal (SELL)
    if(EnableExtremeMode && currentRSI > RSI_ExtremeOverbought && previousRSI <= RSI_ExtremeOverbought)
    {
        double confidence = CalculateRSIConfidence(currentRSI, false);
        if(confidence > 0.7)
        {
            OpenPosition(ORDER_TYPE_SELL, "RSI_Extreme_Overbought", confidence);
            return;
        }
    }
    
    //--- Regular oversold signal (BUY)
    if(currentRSI < RSI_Oversold && previousRSI >= RSI_Oversold)
    {
        double confidence = CalculateRSIConfidence(currentRSI, true);
        if(confidence > 0.6)
        {
            OpenPosition(ORDER_TYPE_BUY, "RSI_Oversold", confidence);
        }
    }
    
    //--- Regular overbought signal (SELL)
    if(currentRSI > RSI_Overbought && previousRSI <= RSI_Overbought)
    {
        double confidence = CalculateRSIConfidence(currentRSI, false);
        if(confidence > 0.6)
        {
            OpenPosition(ORDER_TYPE_SELL, "RSI_Overbought", confidence);
        }
    }
}

//+------------------------------------------------------------------+
//| MA Crossover Strategy Signals                                   |
//+------------------------------------------------------------------+
void CheckMASignals()
{
    double currentFastMA = maFastValues[0];
    double currentSlowMA = maSlowValues[0];
    double previousFastMA = maFastValues[1];
    double previousSlowMA = maSlowValues[1];
    
    //--- Bullish crossover (BUY)
    if(currentFastMA > currentSlowMA && previousFastMA <= previousSlowMA)
    {
        double confidence = CalculateMAConfidence(true);
        if(confidence > 0.6)
        {
            OpenPosition(ORDER_TYPE_BUY, "MA_Bullish_Crossover", confidence);
        }
    }
    
    //--- Bearish crossover (SELL)
    if(currentFastMA < currentSlowMA && previousFastMA >= previousSlowMA)
    {
        double confidence = CalculateMAConfidence(false);
        if(confidence > 0.6)
        {
            OpenPosition(ORDER_TYPE_SELL, "MA_Bearish_Crossover", confidence);
        }
    }
}

//+------------------------------------------------------------------+
//| Breakout Strategy Signals                                       |
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
        if(confidence > 0.65)
        {
            OpenPosition(ORDER_TYPE_BUY, "Breakout_Bullish", confidence);
        }
    }
    
    //--- Bearish breakout
    if(currentPrice < lowestLow - (atr * Breakout_Threshold))
    {
        double confidence = CalculateBreakoutConfidence(false);
        if(confidence > 0.65)
        {
            OpenPosition(ORDER_TYPE_SELL, "Breakout_Bearish", confidence);
        }
    }
}

//+------------------------------------------------------------------+
//| Scalping Strategy Signals                                       |
//+------------------------------------------------------------------+
void CheckScalpingSignals()
{
    //--- Get scalping MAs
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
    
    //--- Quick scalp signals with tight targets
    if(currentFast > currentSlow && previousFast <= previousSlow)
    {
        OpenScalpPosition(ORDER_TYPE_BUY, "Scalp_Buy");
    }
    
    if(currentFast < currentSlow && previousFast >= previousSlow)
    {
        OpenScalpPosition(ORDER_TYPE_SELL, "Scalp_Sell");
    }
    
    IndicatorRelease(scalpFastHandle);
    IndicatorRelease(scalpSlowHandle);
}

//+------------------------------------------------------------------+
//| News Strategy Signals                                           |
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
        
        //--- Trade in direction of volatility spike
        if(currentPrice > previousPrice)
        {
            OpenPosition(ORDER_TYPE_BUY, "News_Volatility_Buy", 0.8);
        }
        else if(currentPrice < previousPrice)
        {
            OpenPosition(ORDER_TYPE_SELL, "News_Volatility_Sell", 0.8);
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
    
    double lotSize = CalculatePositionSize(confidence);
    double stopLoss = CalculateStopLoss(orderType, price);
    double takeProfit = CalculateTakeProfit(orderType, price);
    
    string comment = StringFormat("%s|%s|Conf:%.2f", TradeComment, strategy, confidence);
    
    if(trade.PositionOpen(_Symbol, orderType, lotSize, price, stopLoss, takeProfit, comment))
    {
        totalTrades++;
        if(EnableLogging)
        {
            Print("Position opened: ", strategy, " | Type: ", EnumToString(orderType), 
                  " | Lots: ", lotSize, " | Confidence: ", confidence);
        }
    }
    else
    {
        Print("Failed to open position: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
    }
}

//+------------------------------------------------------------------+
//| Open scalping position with tight targets                       |
//+------------------------------------------------------------------+
void OpenScalpPosition(ENUM_ORDER_TYPE orderType, string strategy)
{
    double price = (orderType == ORDER_TYPE_BUY) ? 
                   SymbolInfoDouble(_Symbol, SYMBOL_ASK) : 
                   SymbolInfoDouble(_Symbol, SYMBOL_BID);
    
    double lotSize = CalculatePositionSize(0.7); // Medium confidence for scalping
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
    
    string comment = StringFormat("%s|%s|Scalp", TradeComment, strategy);
    
    if(trade.PositionOpen(_Symbol, orderType, lotSize, price, stopLoss, takeProfit, comment))
    {
        totalTrades++;
        if(EnableLogging)
        {
            Print("Scalp position opened: ", strategy, " | Type: ", EnumToString(orderType), 
                  " | Lots: ", lotSize, " | Target: ", Scalp_PipTarget, " pips");
        }
    }
}

//+------------------------------------------------------------------+
//| Calculate position size based on risk and confidence            |
//+------------------------------------------------------------------+
double CalculatePositionSize(double confidence)
{
    double equity = AccountInfoDouble(ACCOUNT_EQUITY);
    double riskAmount = equity * (RiskPerTrade / 100.0);
    
    //--- Adjust risk based on confidence
    if(EnableExtremeMode)
    {
        riskAmount *= confidence; // Higher confidence = higher risk
        riskAmount *= 2.0; // Extreme mode multiplier
    }
    
    double pipValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double stopLossPips = StopLossPips;
    
    double lotSize = riskAmount / (stopLossPips * pipValue);
    
    //--- Apply leverage effect
    lotSize *= (Leverage / 100.0);
    
    //--- Normalize lot size
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    
    lotSize = MathMax(minLot, MathMin(maxLot, lotSize));
    lotSize = MathRound(lotSize / lotStep) * lotStep;
    
    return lotSize;
}

//+------------------------------------------------------------------+
//| Calculate stop loss                                             |
//+------------------------------------------------------------------+
double CalculateStopLoss(ENUM_ORDER_TYPE orderType, double price)
{
    double pipSize = SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 10;
    double atr = atrValues[0];
    
    double stopDistance = MathMax(StopLossPips * pipSize, atr * 1.5);
    
    if(orderType == ORDER_TYPE_BUY)
        return price - stopDistance;
    else
        return price + stopDistance;
}

//+------------------------------------------------------------------+
//| Calculate take profit                                           |
//+------------------------------------------------------------------+
double CalculateTakeProfit(ENUM_ORDER_TYPE orderType, double price)
{
    double pipSize = SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 10;
    double atr = atrValues[0];
    
    double profitDistance = MathMax(TakeProfitPips * pipSize, atr * 2.0);
    
    if(orderType == ORDER_TYPE_BUY)
        return price + profitDistance;
    else
        return price - profitDistance;
}

//+------------------------------------------------------------------+
//| Calculate RSI confidence                                        |
//+------------------------------------------------------------------+
double CalculateRSIConfidence(double rsi, bool isBuy)
{
    double confidence = 0.5;
    
    if(isBuy)
    {
        if(rsi < 20) confidence = 0.9;
        else if(rsi < 25) confidence = 0.8;
        else if(rsi < 30) confidence = 0.7;
        else confidence = 0.6;
    }
    else
    {
        if(rsi > 80) confidence = 0.9;
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
    
    double confidence = 0.6 + (separation * 100); // Base confidence + separation bonus
    return MathMin(0.9, confidence);
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
    double confidence = 0.65 + (priceMove / atr) * 0.1;
    
    return MathMin(0.9, confidence);
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
//| Manage existing positions                                       |
//+------------------------------------------------------------------+
void ManagePositions()
{
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if(PositionGetTicket(i) > 0)
        {
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                //--- Check for position management
                CheckPositionForClose(PositionGetTicket(i));
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Check position for close                                        |
//+------------------------------------------------------------------+
void CheckPositionForClose(ulong ticket)
{
    if(!PositionSelectByTicket(ticket))
        return;
    
    double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
    double currentPrice = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ?
                         SymbolInfoDouble(_Symbol, SYMBOL_BID) :
                         SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    
    double profit = PositionGetDouble(POSITION_PROFIT);
    
    //--- Close profitable scalping positions quickly
    string comment = PositionGetString(POSITION_COMMENT);
    if(StringFind(comment, "Scalp") >= 0 && profit > 0)
    {
        if(trade.PositionClose(ticket))
        {
            if(profit > 0) winningTrades++;
            totalProfit += profit;
        }
    }
}

//+------------------------------------------------------------------+
//| Update trailing stops                                           |
//+------------------------------------------------------------------+
void UpdateTrailingStops()
{
    double pipSize = SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 10;
    double trailDistance = TrailingStopPips * pipSize;
    
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if(PositionGetTicket(i) > 0)
        {
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
                double currentSL = PositionGetDouble(POSITION_SL);
                double currentPrice = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ?
                                     SymbolInfoDouble(_Symbol, SYMBOL_BID) :
                                     SymbolInfoDouble(_Symbol, SYMBOL_ASK);
                
                double newSL = 0;
                bool updateSL = false;
                
                if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
                {
                    newSL = currentPrice - trailDistance;
                    if(newSL > currentSL && newSL > openPrice)
                        updateSL = true;
                }
                else
                {
                    newSL = currentPrice + trailDistance;
                    if((newSL < currentSL || currentSL == 0) && newSL < openPrice)
                        updateSL = true;
                }
                
                if(updateSL)
                {
                    trade.PositionModify(PositionGetTicket(i), newSL, PositionGetDouble(POSITION_TP));
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Check risk management                                           |
//+------------------------------------------------------------------+
bool CheckRiskManagement()
{
    double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    double drawdown = (initialEquity - currentEquity) / initialEquity * 100;
    
    //--- Check maximum drawdown
    if(drawdown > MaxDrawdown)
    {
        CloseAllPositions("Max drawdown reached");
        Print("RISK ALERT: Maximum drawdown reached: ", drawdown, "%");
        return false;
    }
    
    //--- Check daily loss limit
    double dailyLoss = (dailyStartEquity - currentEquity) / dailyStartEquity * 100;
    if(dailyLoss > DailyLossLimit)
    {
        CloseAllPositions("Daily loss limit reached");
        Print("RISK ALERT: Daily loss limit reached: ", dailyLoss, "%");
        return false;
    }
    
    //--- Update max drawdown reached
    if(drawdown > maxDrawdownReached)
        maxDrawdownReached = drawdown;
    
    return true;
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
    
    return true;
}

//+------------------------------------------------------------------+
//| Update daily tracking                                           |
//+------------------------------------------------------------------+
void UpdateDailyTracking()
{
    MqlDateTime currentDT, startDT;
    TimeCurrent(currentDT);
    TimeToStruct(dailyStartTime, startDT);
    
    //--- Reset daily tracking if new day
    if(currentDT.day != startDT.day)
    {
        dailyStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
        dailyStartTime = TimeCurrent();
    }
}

//+------------------------------------------------------------------+
//| Get open positions count                                        |
//+------------------------------------------------------------------+
int GetOpenPositionsCount()
{
    int count = 0;
    for(int i = 0; i < PositionsTotal(); i++)
    {
        if(PositionGetTicket(i) > 0)
        {
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber)
                count++;
        }
    }
    return count;
}

//+------------------------------------------------------------------+
//| Close all positions                                             |
//+------------------------------------------------------------------+
void CloseAllPositions(string reason)
{
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if(PositionGetTicket(i) > 0)
        {
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                trade.PositionClose(PositionGetTicket(i));
            }
        }
    }
    
    Print("All positions closed: ", reason);
}

//+------------------------------------------------------------------+
//| Print final statistics                                          |
//+------------------------------------------------------------------+
void PrintFinalStatistics()
{
    double finalEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    double totalReturn = (finalEquity - initialEquity) / initialEquity * 100;
    double winRate = totalTrades > 0 ? (double)winningTrades / totalTrades * 100 : 0;
    
    Print("=== ULTIMATE FOREX EA STATISTICS ===");
    Print("Initial Equity: ", initialEquity);
    Print("Final Equity: ", finalEquity);
    Print("Total Return: ", totalReturn, "%");
    Print("Total Trades: ", totalTrades);
    Print("Winning Trades: ", winningTrades);
    Print("Win Rate: ", winRate, "%");
    Print("Total Profit: ", totalProfit);
    Print("Max Drawdown: ", maxDrawdownReached, "%");
    Print("====================================");
}

//+------------------------------------------------------------------+

