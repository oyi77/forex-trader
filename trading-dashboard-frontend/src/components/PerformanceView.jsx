import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3,
  PieChart,
  Calendar,
  Download,
  Filter
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Cell,
  Area,
  AreaChart
} from 'recharts'

const PerformanceView = () => {
  const [performanceData, setPerformanceData] = useState(null)
  const [equityData, setEquityData] = useState([])
  const [timeframe, setTimeframe] = useState('1M')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPerformanceData()
  }, [timeframe])

  const fetchPerformanceData = async () => {
    try {
      setLoading(true)
      
      // Fetch performance metrics
      const perfResponse = await fetch('/api/trading/performance')
      const perfData = await perfResponse.json()
      setPerformanceData(perfData)

      // Fetch equity curve data
      const equityResponse = await fetch('/api/trading/equity-curve')
      const equityData = await equityResponse.json()
      setEquityData(equityData)

    } catch (error) {
      console.error('Error fetching performance data:', error)
    } finally {
      setLoading(false)
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

  // Generate monthly P&L data
  const monthlyPnLData = performanceData?.daily_pnl?.reduce((acc, day) => {
    const month = new Date(day.date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    const existing = acc.find(item => item.month === month)
    
    if (existing) {
      existing.pnl += day.pnl
    } else {
      acc.push({ month, pnl: day.pnl })
    }
    
    return acc
  }, []) || []

  // Generate trade distribution data
  const tradeDistributionData = [
    { name: 'Winning Trades', value: 68, color: '#10B981' },
    { name: 'Losing Trades', value: 32, color: '#EF4444' }
  ]

  // Generate drawdown data
  const drawdownData = equityData.map(point => ({
    ...point,
    drawdown: -point.drawdown // Make drawdown negative for chart
  }))

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
            Performance Analytics
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Detailed analysis of your trading bot's performance
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Select value={timeframe} onValueChange={setTimeframe}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1W">1 Week</SelectItem>
              <SelectItem value="1M">1 Month</SelectItem>
              <SelectItem value="3M">3 Months</SelectItem>
              <SelectItem value="6M">6 Months</SelectItem>
              <SelectItem value="1Y">1 Year</SelectItem>
            </SelectContent>
          </Select>
          
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Key Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Return
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {performanceData ? formatPercentage(performanceData.total_return) : '0.00%'}
              </div>
              <div className="flex items-center mt-2 text-sm text-gray-600 dark:text-gray-400">
                <TrendingUp className="h-4 w-4 mr-1" />
                Since inception
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Sharpe Ratio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {performanceData ? performanceData.sharpe_ratio.toFixed(2) : '0.00'}
              </div>
              <div className="flex items-center mt-2 text-sm text-gray-600 dark:text-gray-400">
                <BarChart3 className="h-4 w-4 mr-1" />
                Risk-adjusted return
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Max Drawdown
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {performanceData ? formatPercentage(performanceData.max_drawdown) : '0.00%'}
              </div>
              <div className="flex items-center mt-2 text-sm text-gray-600 dark:text-gray-400">
                <TrendingDown className="h-4 w-4 mr-1" />
                Peak to trough
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Win Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {performanceData ? formatPercentage(performanceData.win_rate) : '0.00%'}
              </div>
              <div className="flex items-center mt-2 text-sm text-gray-600 dark:text-gray-400">
                <PieChart className="h-4 w-4 mr-1" />
                {performanceData ? performanceData.total_trades : 0} total trades
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts Row 1 */}
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
                Account equity progression over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={equityData}>
                    <defs>
                      <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
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
                    <Area
                      type="monotone"
                      dataKey="equity"
                      stroke="#2563eb"
                      fillOpacity={1}
                      fill="url(#equityGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Drawdown Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Drawdown Analysis</CardTitle>
              <CardDescription>
                Underwater equity curve showing drawdown periods
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={drawdownData}>
                    <defs>
                      <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <YAxis 
                      tickFormatter={(value) => `${value.toFixed(1)}%`}
                      domain={['dataMin', 0]}
                    />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                      formatter={(value) => [`${value.toFixed(2)}%`, 'Drawdown']}
                    />
                    <Area
                      type="monotone"
                      dataKey="drawdown"
                      stroke="#ef4444"
                      fillOpacity={1}
                      fill="url(#drawdownGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly P&L */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Monthly P&L</CardTitle>
              <CardDescription>
                Profit and loss breakdown by month
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyPnLData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis tickFormatter={(value) => formatCurrency(value)} />
                    <Tooltip formatter={(value) => [formatCurrency(value), 'P&L']} />
                    <Bar 
                      dataKey="pnl" 
                      fill={(entry) => entry.pnl >= 0 ? '#10B981' : '#EF4444'}
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Trade Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Trade Distribution</CardTitle>
              <CardDescription>
                Breakdown of winning vs losing trades
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPieChart>
                    <Pie
                      data={tradeDistributionData}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {tradeDistributionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value}%`, 'Percentage']} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Performance Statistics Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Detailed Statistics</CardTitle>
            <CardDescription>
              Comprehensive performance metrics and ratios
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900 dark:text-white">Returns</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Return</span>
                    <span className="font-medium">
                      {performanceData ? formatPercentage(performanceData.total_return) : '0.00%'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total P&L</span>
                    <span className="font-medium">
                      {performanceData ? formatCurrency(performanceData.total_pnl) : '$0.00'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Account Balance</span>
                    <span className="font-medium">
                      {performanceData ? formatCurrency(performanceData.account_balance) : '$0.00'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900 dark:text-white">Risk Metrics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Sharpe Ratio</span>
                    <span className="font-medium">
                      {performanceData ? performanceData.sharpe_ratio.toFixed(2) : '0.00'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Max Drawdown</span>
                    <span className="font-medium text-red-600">
                      {performanceData ? formatPercentage(performanceData.max_drawdown) : '0.00%'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Current Positions</span>
                    <span className="font-medium">
                      {performanceData ? performanceData.current_positions : 0}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900 dark:text-white">Trading Activity</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Total Trades</span>
                    <span className="font-medium">
                      {performanceData ? performanceData.total_trades : 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Win Rate</span>
                    <span className="font-medium text-green-600">
                      {performanceData ? formatPercentage(performanceData.win_rate) : '0.00%'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Daily P&L</span>
                    <span className="font-medium">
                      {performanceData?.daily_pnl ? 
                        formatCurrency(performanceData.daily_pnl[performanceData.daily_pnl.length - 1]?.pnl || 0) : 
                        '$0.00'
                      }
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

export default PerformanceView

