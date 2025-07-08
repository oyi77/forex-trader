import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Play, 
  Pause, 
  Square,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Filter,
  Download
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

const TradingView = () => {
  const [trades, setTrades] = useState([])
  const [marketData, setMarketData] = useState({})
  const [strategies, setStrategies] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTradingData()
    const interval = setInterval(fetchTradingData, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchTradingData = async () => {
    try {
      // Fetch trades
      const tradesResponse = await fetch(`/api/trading/trades?status=${filter}`)
      const tradesData = await tradesResponse.json()
      setTrades(tradesData.trades)

      // Fetch market data
      const marketResponse = await fetch('/api/trading/market-data')
      const marketData = await marketResponse.json()
      setMarketData(marketData)

      // Fetch strategies
      const strategiesResponse = await fetch('/api/trading/strategies')
      const strategiesData = await strategiesResponse.json()
      setStrategies(strategiesData)

    } catch (error) {
      console.error('Error fetching trading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStrategyToggle = async (strategyName, action) => {
    try {
      const response = await fetch(`/api/trading/strategies/${strategyName}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
      })

      if (response.ok) {
        fetchTradingData() // Refresh data
      }
    } catch (error) {
      console.error('Error toggling strategy:', error)
    }
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value)
  }

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Live Trading
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Monitor and control your trading strategies in real-time
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={fetchTradingData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Market Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Market Overview</CardTitle>
          <CardDescription>
            Real-time prices for major currency pairs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {Object.entries(marketData).map(([symbol, data]) => (
              <motion.div
                key={symbol}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                <div className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                  {symbol}
                </div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {data.price.toFixed(4)}
                </div>
                <div className={`flex items-center text-sm ${
                  data.change >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {data.change >= 0 ? 
                    <TrendingUp className="h-3 w-3 mr-1" /> : 
                    <TrendingDown className="h-3 w-3 mr-1" />
                  }
                  {data.change >= 0 ? '+' : ''}{data.change.toFixed(4)} ({formatPercentage(data.change_pct / 100)})
                </div>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Active Strategies */}
      <Card>
        <CardHeader>
          <CardTitle>Trading Strategies</CardTitle>
          <CardDescription>
            Manage and monitor your automated trading strategies
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {strategies.map((strategy) => (
              <motion.div
                key={strategy.name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${
                    strategy.active ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
                  }`}></div>
                  
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      {strategy.name}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Last signal: {new Date(strategy.last_signal).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      Return: {formatPercentage(strategy.performance.total_return)}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      Sharpe: {strategy.performance.sharpe_ratio.toFixed(2)}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Badge variant={strategy.confidence > 0.7 ? 'default' : 'secondary'}>
                      {formatPercentage(strategy.confidence)} confidence
                    </Badge>
                    
                    <Button
                      variant={strategy.active ? 'destructive' : 'default'}
                      size="sm"
                      onClick={() => handleStrategyToggle(
                        strategy.name, 
                        strategy.active ? 'disable' : 'enable'
                      )}
                    >
                      {strategy.active ? (
                        <>
                          <Pause className="h-4 w-4 mr-1" />
                          Stop
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 mr-1" />
                          Start
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Trade History */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Trade History</CardTitle>
              <CardDescription>
                Recent trading activity and positions
              </CardDescription>
            </div>
            
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <Select value={filter} onValueChange={setFilter}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Trades</SelectItem>
                  <SelectItem value="open">Open Only</SelectItem>
                  <SelectItem value="closed">Closed Only</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                    Symbol
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                    Side
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                    Entry Price
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                    Exit Price
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                    Quantity
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                    P&L
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                    Status
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                    Time
                  </th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade) => (
                  <motion.tr
                    key={trade.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800"
                  >
                    <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">
                      {trade.symbol}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant={trade.side === 'buy' ? 'default' : 'secondary'}>
                        {trade.side.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-gray-900 dark:text-white">
                      {trade.entry_price.toFixed(4)}
                    </td>
                    <td className="py-3 px-4 text-gray-900 dark:text-white">
                      {trade.exit_price ? trade.exit_price.toFixed(4) : '-'}
                    </td>
                    <td className="py-3 px-4 text-gray-900 dark:text-white">
                      {trade.quantity.toLocaleString()}
                    </td>
                    <td className={`py-3 px-4 font-medium ${
                      trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatCurrency(trade.pnl)}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant={trade.status === 'closed' ? 'outline' : 'default'}>
                        {trade.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-500 dark:text-gray-400">
                      {new Date(trade.entry_time).toLocaleString()}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default TradingView

