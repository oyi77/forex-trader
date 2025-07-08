import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Play, 
  Pause, 
  Settings,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Target,
  Zap,
  RefreshCw
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Progress } from '@/components/ui/progress'

const StrategiesView = () => {
  const [strategies, setStrategies] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStrategies()
  }, [])

  const fetchStrategies = async () => {
    try {
      const response = await fetch('/api/trading/strategies')
      const data = await response.json()
      setStrategies(data)
    } catch (error) {
      console.error('Error fetching strategies:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStrategyToggle = async (strategyName, active) => {
    try {
      const action = active ? 'enable' : 'disable'
      const response = await fetch(`/api/trading/strategies/${strategyName}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
      })

      if (response.ok) {
        fetchStrategies() // Refresh data
      }
    } catch (error) {
      console.error('Error toggling strategy:', error)
    }
  }

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`
  }

  const getStrategyIcon = (strategyName) => {
    if (strategyName.includes('RSI')) return <Target className="h-5 w-5" />
    if (strategyName.includes('MA')) return <TrendingUp className="h-5 w-5" />
    if (strategyName.includes('Breakout')) return <Zap className="h-5 w-5" />
    return <BarChart3 className="h-5 w-5" />
  }

  const getPerformanceColor = (value) => {
    if (value > 0.1) return 'text-green-600'
    if (value > 0) return 'text-green-500'
    if (value > -0.05) return 'text-yellow-500'
    return 'text-red-600'
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
            Trading Strategies
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage and monitor your automated trading strategies
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={fetchStrategies}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Settings className="h-4 w-4 mr-2" />
            Strategy Settings
          </Button>
        </div>
      </div>

      {/* Strategy Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Active Strategies
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {strategies.filter(s => s.active).length}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                of {strategies.length} total
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
                Best Performer
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {strategies.length > 0 ? 
                  formatPercentage(Math.max(...strategies.map(s => s.performance.total_return))) : 
                  '0.00%'
                }
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {strategies.length > 0 ? 
                  strategies.reduce((best, current) => 
                    current.performance.total_return > best.performance.total_return ? current : best
                  ).name : 
                  'No strategies'
                }
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
                Average Confidence
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {strategies.length > 0 ? 
                  formatPercentage(strategies.reduce((sum, s) => sum + s.confidence, 0) / strategies.length) : 
                  '0.00%'
                }
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Signal confidence
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Strategy Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {strategies.map((strategy, index) => (
          <motion.div
            key={strategy.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 + index * 0.1 }}
          >
            <Card className={`${strategy.active ? 'ring-2 ring-blue-500 ring-opacity-20' : ''}`}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${
                      strategy.active ? 'bg-blue-100 dark:bg-blue-900' : 'bg-gray-100 dark:bg-gray-800'
                    }`}>
                      {getStrategyIcon(strategy.name)}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{strategy.name}</CardTitle>
                      <CardDescription>
                        Last signal: {new Date(strategy.last_signal).toLocaleString()}
                      </CardDescription>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${
                      strategy.active ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
                    }`}></div>
                    <Switch
                      checked={strategy.active}
                      onCheckedChange={(checked) => handleStrategyToggle(strategy.name, checked)}
                    />
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Performance Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Total Return</div>
                    <div className={`text-lg font-bold ${getPerformanceColor(strategy.performance.total_return)}`}>
                      {formatPercentage(strategy.performance.total_return)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Sharpe Ratio</div>
                    <div className="text-lg font-bold">
                      {strategy.performance.sharpe_ratio.toFixed(2)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Win Rate</div>
                    <div className="text-lg font-bold text-green-600">
                      {formatPercentage(strategy.performance.win_rate)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Max Drawdown</div>
                    <div className="text-lg font-bold text-red-600">
                      {formatPercentage(strategy.performance.max_drawdown)}
                    </div>
                  </div>
                </div>

                {/* Confidence Bar */}
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600 dark:text-gray-400">Signal Confidence</span>
                    <span className="font-medium">{formatPercentage(strategy.confidence)}</span>
                  </div>
                  <Progress 
                    value={strategy.confidence * 100} 
                    className="h-2"
                  />
                </div>

                {/* Status Badges */}
                <div className="flex items-center space-x-2">
                  <Badge variant={strategy.active ? 'default' : 'secondary'}>
                    {strategy.active ? 'Active' : 'Inactive'}
                  </Badge>
                  
                  <Badge variant={strategy.confidence > 0.7 ? 'default' : 'outline'}>
                    {strategy.confidence > 0.7 ? 'High Confidence' : 'Low Confidence'}
                  </Badge>
                  
                  <Badge variant={strategy.performance.total_return > 0 ? 'default' : 'destructive'}>
                    {strategy.performance.total_return > 0 ? 'Profitable' : 'Loss'}
                  </Badge>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center space-x-2 pt-2">
                  <Button
                    variant={strategy.active ? 'destructive' : 'default'}
                    size="sm"
                    onClick={() => handleStrategyToggle(strategy.name, !strategy.active)}
                    className="flex-1"
                  >
                    {strategy.active ? (
                      <>
                        <Pause className="h-4 w-4 mr-1" />
                        Stop Strategy
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-1" />
                        Start Strategy
                      </>
                    )}
                  </Button>
                  
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-1" />
                    Configure
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Strategy Comparison Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Strategy Comparison</CardTitle>
            <CardDescription>
              Side-by-side performance comparison of all strategies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                      Strategy
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                      Status
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                      Total Return
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                      Sharpe Ratio
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                      Win Rate
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                      Max Drawdown
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900 dark:text-white">
                      Confidence
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {strategies.map((strategy) => (
                    <tr
                      key={strategy.name}
                      className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          {getStrategyIcon(strategy.name)}
                          <span className="font-medium text-gray-900 dark:text-white">
                            {strategy.name}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={strategy.active ? 'default' : 'secondary'}>
                          {strategy.active ? 'Active' : 'Inactive'}
                        </Badge>
                      </td>
                      <td className={`py-3 px-4 font-medium ${getPerformanceColor(strategy.performance.total_return)}`}>
                        {formatPercentage(strategy.performance.total_return)}
                      </td>
                      <td className="py-3 px-4 text-gray-900 dark:text-white">
                        {strategy.performance.sharpe_ratio.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-green-600 font-medium">
                        {formatPercentage(strategy.performance.win_rate)}
                      </td>
                      <td className="py-3 px-4 text-red-600 font-medium">
                        {formatPercentage(strategy.performance.max_drawdown)}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <Progress value={strategy.confidence * 100} className="w-16 h-2" />
                          <span className="text-sm font-medium">
                            {formatPercentage(strategy.confidence)}
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

export default StrategiesView

