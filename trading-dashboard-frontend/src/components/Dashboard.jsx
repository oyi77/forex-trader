import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Target,
  Activity,
  BarChart3,
  PieChart,
  AlertCircle
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Cell } from 'recharts'

const Dashboard = () => {
  const [performanceData, setPerformanceData] = useState(null)
  const [equityData, setEquityData] = useState([])
  const [marketData, setMarketData] = useState({})
  const [trades, setTrades] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      
      // Fetch performance data
      const perfResponse = await fetch('/api/trading/performance')
      const perfData = await perfResponse.json()
      setPerformanceData(perfData)

      // Fetch equity curve
      const equityResponse = await fetch('/api/trading/equity-curve')
      const equityData = await equityResponse.json()
      setEquityData(equityData)

      // Fetch market data
      const marketResponse = await fetch('/api/trading/market-data')
      const marketData = await marketResponse.json()
      setMarketData(marketData)

      // Fetch recent trades
      const tradesResponse = await fetch('/api/trading/trades?limit=5')
      const tradesData = await tradesResponse.json()
      setTrades(tradesData.trades)

    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
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

  // Prepare pie chart data for position distribution
  const positionData = Object.entries(marketData).map(([symbol, data]) => ({
    name: symbol,
    value: Math.random() * 100, // Mock position size
    color: `hsl(${Math.random() * 360}, 70%, 50%)`
  }))

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Trading Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Real-time overview of your forex trading bot performance
        </p>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total P&L</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {performanceData ? formatCurrency(performanceData.total_pnl) : '$0.00'}
              </div>
              <p className="text-xs text-muted-foreground">
                {performanceData ? formatPercentage(performanceData.total_return) : '0.00%'} from start
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {performanceData ? formatPercentage(performanceData.win_rate) : '0.00%'}
              </div>
              <p className="text-xs text-muted-foreground">
                {performanceData ? performanceData.total_trades : 0} total trades
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Sharpe Ratio</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {performanceData ? performanceData.sharpe_ratio.toFixed(2) : '0.00'}
              </div>
              <p className="text-xs text-muted-foreground">
                Risk-adjusted return
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Max Drawdown</CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {performanceData ? formatPercentage(performanceData.max_drawdown) : '0.00%'}
              </div>
              <p className="text-xs text-muted-foreground">
                Maximum loss from peak
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Equity Curve */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Equity Curve</CardTitle>
              <CardDescription>
                Account equity over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={equityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <YAxis tickFormatter={(value) => `$${value.toFixed(0)}`} />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                      formatter={(value) => [formatCurrency(value), 'Equity']}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="equity" 
                      stroke="#2563eb" 
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Position Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Position Distribution</CardTitle>
              <CardDescription>
                Current exposure by currency pair
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPieChart>
                    <Pie
                      data={positionData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {positionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Exposure']} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Market Data and Recent Trades */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Market Data */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Market Data</CardTitle>
              <CardDescription>
                Current prices for major currency pairs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(marketData).map(([symbol, data]) => (
                  <div key={symbol} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="font-medium text-gray-900 dark:text-white">
                        {symbol}
                      </span>
                      <Badge variant={data.change >= 0 ? 'default' : 'destructive'}>
                        {data.change >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                        {formatPercentage(data.change_pct / 100)}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-gray-900 dark:text-white">
                        {data.price.toFixed(4)}
                      </div>
                      <div className={`text-sm ${data.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {data.change >= 0 ? '+' : ''}{data.change.toFixed(4)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Trades */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Recent Trades</CardTitle>
              <CardDescription>
                Latest trading activity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {trades.map((trade) => (
                  <div key={trade.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Badge variant={trade.side === 'buy' ? 'default' : 'secondary'}>
                        {trade.side.toUpperCase()}
                      </Badge>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {trade.symbol}
                      </span>
                      <Badge variant={trade.status === 'closed' ? 'outline' : 'default'}>
                        {trade.status}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <div className={`font-medium ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(trade.pnl)}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(trade.entry_time).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}

export default Dashboard

