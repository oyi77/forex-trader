# Mini Contract Support Documentation

## Overview

The Ultimate Forex EA God Mode now includes comprehensive support for mini contracts (symbols ending with 'm'). Mini contracts provide lower risk trading opportunities with reduced position sizes and adjusted risk parameters.

## Supported Mini Contracts

### Forex Pairs
- **EURUSDm** - Euro/US Dollar Mini
- **GBPUSDm** - British Pound/US Dollar Mini
- **USDJPYm** - US Dollar/Japanese Yen Mini
- **USDCHFm** - US Dollar/Swiss Franc Mini
- **USDCADm** - US Dollar/Canadian Dollar Mini
- **AUDUSDm** - Australian Dollar/US Dollar Mini
- **NZDUSDm** - New Zealand Dollar/US Dollar Mini

### Commodities
- **XAUUSDm** - Gold/US Dollar Mini
- **XAGUSDm** - Silver/US Dollar Mini
- **WTIUSDm** - West Texas Intermediate Mini

## Key Features

### 1. Automatic Detection
- Mini contracts are automatically detected by the 'm' suffix
- Base symbol validation ensures proper mini contract identification
- Seamless integration with existing trading logic

### 2. Position Sizing Adjustments
- **0.1x Multiplier**: Mini contracts use 0.1x the position size of standard contracts
- **Enhanced Limits**: Maximum position sizes are increased for mini contracts (3x normal)
- **Risk Reduction**: Lower risk per trade due to smaller contract sizes

### 3. Risk Management
- **Adjusted Thresholds**: Profit and loss thresholds are reduced for mini contracts
- **Correlation Detection**: Enhanced correlation detection between mini and standard contracts
- **Volatility Handling**: Adjusted volatility multipliers for mini contracts

### 4. Strategy Adaptations
All trading strategies automatically adapt to mini contracts:

#### God Mode Scalping
- Reduced profit thresholds (50% of standard)
- Adjusted position sizing for lower risk
- Enhanced correlation filtering

#### Extreme RSI
- Improved correlation detection
- Adjusted confidence thresholds
- Modified risk parameters

#### Volatility Explosion
- Adjusted volatility thresholds
- Modified explosion multipliers
- Enhanced risk controls

#### Momentum Surge
- Lower risk thresholds
- Adjusted momentum parameters
- Modified position sizing

#### News Impact
- Reduced position sizing
- Lower volatility multipliers
- Adjusted confidence levels

#### Grid Recovery
- Modified grid spacing
- Adjusted recovery parameters
- Enhanced risk management

## Configuration

### Allowed Symbols
Add mini contracts to your allowed symbols list:

```mql5
AllowedSymbols = "EURUSD,GBPUSD,USDJPY,XAUUSD,EURUSDm,GBPUSDm,USDJPYm,XAUUSDm"
```

### Risk Parameters
Mini contracts automatically use adjusted risk parameters:
- Position size multiplier: 0.1x
- Maximum positions: 3x normal limit
- Profit thresholds: 50% of standard
- Loss thresholds: 50% of standard

## Implementation Details

### Detection Logic
```mql5
bool IsMiniContract(string symbol)
{
    if(StringFind(symbol, "m") >= 0 && StringLen(symbol) > 0)
    {
        string baseSymbol = StringSubstr(symbol, 0, StringLen(symbol) - 1);
        if(SymbolInfoInteger(baseSymbol, SYMBOL_SELECT))
            return true;
    }
    return false;
}
```

### Position Sizing
```mql5
double GetMiniContractMultiplier(string symbol)
{
    if(!IsMiniContract(symbol))
        return 1.0;
    return 0.1; // 0.1x for mini contracts
}
```

### Correlation Detection
```mql5
string GetBaseSymbol(string symbol)
{
    if(IsMiniContract(symbol))
        return StringSubstr(symbol, 0, StringLen(symbol) - 1);
    return symbol;
}
```

## Benefits

### 1. Lower Risk Trading
- Reduced position sizes automatically
- Lower capital requirements
- Safer entry into forex trading

### 2. Enhanced Diversification
- Trade both standard and mini contracts
- Better portfolio management
- Reduced correlation risk

### 3. Learning Platform
- Practice with lower risk
- Understand market dynamics
- Build confidence gradually

### 4. Scalability
- Start with mini contracts
- Scale up to standard contracts
- Flexible risk management

## Usage Examples

### Example 1: EURUSD vs EURUSDm
```mql5
// Standard contract
Symbol: EURUSD
Position Size: 1.0 lot
Risk: $1000 per pip

// Mini contract
Symbol: EURUSDm
Position Size: 0.1 lot
Risk: $100 per pip
```

### Example 2: XAUUSD vs XAUUSDm
```mql5
// Standard contract
Symbol: XAUUSD
Position Size: 0.1 lot
Risk: $1000 per pip

// Mini contract
Symbol: XAUUSDm
Position Size: 0.01 lot
Risk: $100 per pip
```

## Testing

Use the provided test script to verify mini contract support:

1. Copy `test_mini_contracts.mq5` to your MT5 Scripts folder
2. Run the script on any chart
3. Check the Experts tab for test results

## Troubleshooting

### Common Issues

1. **Symbol Not Found**
   - Ensure mini contract symbols are available from your broker
   - Check symbol names match exactly (case-sensitive)

2. **Position Sizing Issues**
   - Verify mini contract detection is working
   - Check broker-specific mini contract specifications

3. **Correlation Problems**
   - Ensure base symbols exist
   - Verify correlation detection logic

### Debug Information
The EA provides detailed logging for mini contracts:
- Automatic detection messages
- Position sizing adjustments
- Risk parameter modifications
- Correlation detection results

## Broker Compatibility

### Supported Brokers
- **Exness**: Full mini contract support
- **IC Markets**: Compatible with mini contracts
- **FXTM**: Mini contract support available
- **Pepperstone**: Mini contract trading available

### Broker-Specific Notes
- Mini contract specifications may vary by broker
- Position size limits may differ
- Commission structures may vary
- Always verify with your specific broker

## Risk Warnings

### Mini Contract Risks
- **Lower Liquidity**: Mini contracts may have lower liquidity
- **Wider Spreads**: Mini contracts often have wider spreads
- **Limited Availability**: Not all brokers offer mini contracts
- **Different Specifications**: Mini contract specs vary by broker

### Recommendations
1. **Start Small**: Begin with mini contracts to learn
2. **Verify Specifications**: Check your broker's mini contract details
3. **Monitor Performance**: Track mini vs standard contract performance
4. **Gradual Scaling**: Move to standard contracts as experience grows

## Future Enhancements

### Planned Features
- **Dynamic Multiplier**: Adjustable mini contract multipliers
- **Broker-Specific Settings**: Custom settings per broker
- **Advanced Correlation**: Enhanced correlation algorithms
- **Performance Analytics**: Mini contract performance tracking

### User Requests
- **Custom Multipliers**: User-defined mini contract multipliers
- **Symbol Groups**: Group mini and standard contracts
- **Risk Profiles**: Different risk profiles for mini contracts
- **Automated Testing**: Automated mini contract testing

## Support

### Documentation
- Complete mini contract documentation
- Configuration examples
- Troubleshooting guides
- Best practices

### Community
- GitHub Issues: Report bugs and request features
- Discussions: Share mini contract experiences
- Updates: Regular improvements and patches

### Getting Help
1. Check this documentation first
2. Review error messages in MT5 Experts tab
3. Search existing GitHub issues
4. Create new issue with detailed information

---

*For updates and support, visit: https://github.com/oyi77/forex-trader*
*Last updated: January 2025* 