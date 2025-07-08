import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Shield, 
  AlertTriangle,
  TrendingDown,
  BarChart3,
  PieChart,
  Target,
  Settings,
  RefreshCw
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  PieChart as RechartsPieChart, 
  Cell, 
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  LineChart,
  Line
} from 'recharts'

const RiskView = () => {
  const [riskMetrics, setRiskMetrics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRiskData()
  }, [])

  const fetchRiskData = async () => {
    try {
      const response = await fetch('/api/trading/risk-metrics')
      const data = await response.json()
      setRiskMetrics(data)
    } catch (error) {
      console.error('Error fetching risk data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`
  }

  const getRiskLevel = (score) => {
    if (score <= 3) return { level: 'Low', color: 'text-green-600', bgColor: 'bg-green-100' }
    if (score <= 6) return { level: 'Medium', color: 'text-yellow-600', bgColor: 'bg-yellow-100' }
    if (score <= 8) return { level: 'High', color: 'text-orange-600', bgColor: 'bg-orange-100' }
    return { level: 'Critical', color: 'text-red-600', bgColor: 'bg-red-100' }
  }

  // Prepare position distribution data for pie chart
  const positionData = riskMetrics ? Object.entries(riskMetrics.position_sizes).map(([symbol, size]) => ({
    name: symbol,
    value: size * 100,
    color: `hsl(${Math.random() * 360}, 70%, 50%)`
  })) : []

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

  // Mock VaR history data
  const varHistoryData = [
    { date: '2025-07-01', var: -0.018 },
    { date: '2025-07-02', var: -0.022 },
    { date: '2025-07-03', var: -0.025 },
    { date: '2025-07-04', var: -0.019 },
    { date: '2025-07-05', var: -0.028 },
    { date: '2025-07-06', var: -0.024 },
    { date: '2025-07-07', var: -0.021 },
    { date: '2025-07-08', var: -0.025 }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const riskLevel = getRiskLevel(riskMetrics?.risk_score || 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Risk Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Monitor and control your trading risk exposure
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={fetchRiskData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Settings className="h-4 w-4 mr-2" />
            Risk Settings
          </Button>
        </div>
      </div>

      {/* Risk Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Risk Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${riskLevel.color}`}>
                {riskMetrics?.risk_score?.toFixed(1) || '0.0'}/10
              </div>
              <div className="flex items-center mt-2">
                <Badge variant="outline" className={`${riskLevel.bgColor} ${riskLevel.color}`}>
                  {riskLevel.level} Risk
                </Badge>
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
                Current Exposure
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {riskMetrics ? formatPercentage(riskMetrics.current_exposure) : '0.00%'}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Limit: {riskMetrics ? formatPercentage(riskMetrics.max_exposure_limit) : '0.00%'}
              </div>
              <Progress 
                value={(riskMetrics?.current_exposure / riskMetrics?.max_exposure_limit) * 100 || 0} 
                className="mt-2 h-2"
              />
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
                VaR (95%)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {riskMetrics ? formatPercentage(riskMetrics.var_95) : '0.00%'}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                1-day Value at Risk
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
                Leverage Ratio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {riskMetrics?.leverage_ratio?.toFixed(1) || '0.0'}:1
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Margin: {riskMetrics ? formatPercentage(riskMetrics.margin_utilization) : '0.00%'}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Position Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Position Distribution</CardTitle>
              <CardDescription>
                Risk exposure by currency pair
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

        {/* VaR History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>VaR History</CardTitle>
              <CardDescription>
                Value at Risk trend over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={varHistoryData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <YAxis 
                      tickFormatter={(value) => `${(value * 100).toFixed(1)}%`}
                    />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleDateString()}
                      formatter={(value) => [`${(value * 100).toFixed(2)}%`, 'VaR']}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="var" 
                      stroke="#ef4444" 
                      strokeWidth={2}
                      dot={{ fill: '#ef4444' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Risk Metrics Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Limits */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Risk Limits</CardTitle>
              <CardDescription>
                Current usage vs. configured limits
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Total Exposure</span>
                  <span>
                    {riskMetrics ? formatPercentage(riskMetrics.current_exposure) : '0.00%'} / 
                    {riskMetrics ? formatPercentage(riskMetrics.max_exposure_limit) : '0.00%'}
                  </span>
                </div>
                <Progress 
                  value={(riskMetrics?.current_exposure / riskMetrics?.max_exposure_limit) * 100 || 0}
                  className="h-2"
                />
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Margin Utilization</span>
                  <span>{riskMetrics ? formatPercentage(riskMetrics.margin_utilization) : '0.00%'} / 80.00%</span>
                </div>
                <Progress 
                  value={(riskMetrics?.margin_utilization / 0.8) * 100 || 0}
                  className="h-2"
                />
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Correlation Risk</span>
                  <span>{riskMetrics ? formatPercentage(riskMetrics.correlation_risk) : '0.00%'} / 60.00%</span>
                </div>
                <Progress 
                  value={(riskMetrics?.correlation_risk / 0.6) * 100 || 0}
                  className="h-2"
                />
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Leverage Ratio</span>
                  <span>{riskMetrics?.leverage_ratio?.toFixed(1) || '0.0'}:1 / 10.0:1</span>
                </div>
                <Progress 
                  value={(riskMetrics?.leverage_ratio / 10) * 100 || 0}
                  className="h-2"
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Risk Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Risk Alerts</CardTitle>
              <CardDescription>
                Current risk warnings and recommendations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {riskMetrics?.current_exposure > 0.7 && (
                  <div className="flex items-start space-x-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
                    <div>
                      <div className="font-medium text-yellow-800 dark:text-yellow-200">
                        High Exposure Warning
                      </div>
                      <div className="text-sm text-yellow-700 dark:text-yellow-300">
                        Current exposure is {formatPercentage(riskMetrics.current_exposure)}, approaching the limit.
                      </div>
                    </div>
                  </div>
                )}

                {riskMetrics?.correlation_risk > 0.6 && (
                  <div className="flex items-start space-x-3 p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-orange-500 mt-0.5" />
                    <div>
                      <div className="font-medium text-orange-800 dark:text-orange-200">
                        High Correlation Risk
                      </div>
                      <div className="text-sm text-orange-700 dark:text-orange-300">
                        Positions show high correlation ({formatPercentage(riskMetrics.correlation_risk)}). Consider diversification.
                      </div>
                    </div>
                  </div>
                )}

                {riskMetrics?.var_95 < -0.03 && (
                  <div className="flex items-start space-x-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5" />
                    <div>
                      <div className="font-medium text-red-800 dark:text-red-200">
                        High VaR Alert
                      </div>
                      <div className="text-sm text-red-700 dark:text-red-300">
                        Value at Risk is {formatPercentage(riskMetrics.var_95)}, indicating high potential losses.
                      </div>
                    </div>
                  </div>
                )}

                {(!riskMetrics || (riskMetrics.current_exposure <= 0.7 && riskMetrics.correlation_risk <= 0.6 && riskMetrics.var_95 >= -0.03)) && (
                  <div className="flex items-start space-x-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <Shield className="h-5 w-5 text-green-500 mt-0.5" />
                    <div>
                      <div className="font-medium text-green-800 dark:text-green-200">
                        Risk Levels Normal
                      </div>
                      <div className="text-sm text-green-700 dark:text-green-300">
                        All risk metrics are within acceptable limits.
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Detailed Risk Metrics Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Detailed Risk Metrics</CardTitle>
            <CardDescription>
              Comprehensive risk analysis and statistics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900 dark:text-white">Exposure Metrics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Current Exposure</span>
                    <span className="font-medium">
                      {riskMetrics ? formatPercentage(riskMetrics.current_exposure) : '0.00%'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Max Exposure Limit</span>
                    <span className="font-medium">
                      {riskMetrics ? formatPercentage(riskMetrics.max_exposure_limit) : '0.00%'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Margin Utilization</span>
                    <span className="font-medium">
                      {riskMetrics ? formatPercentage(riskMetrics.margin_utilization) : '0.00%'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900 dark:text-white">Risk Measures</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">VaR (95%)</span>
                    <span className="font-medium text-red-600">
                      {riskMetrics ? formatPercentage(riskMetrics.var_95) : '0.00%'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Expected Shortfall</span>
                    <span className="font-medium text-red-600">
                      {riskMetrics ? formatPercentage(riskMetrics.expected_shortfall) : '0.00%'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Correlation Risk</span>
                    <span className="font-medium">
                      {riskMetrics ? formatPercentage(riskMetrics.correlation_risk) : '0.00%'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900 dark:text-white">Leverage & Margin</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Leverage Ratio</span>
                    <span className="font-medium">
                      {riskMetrics?.leverage_ratio?.toFixed(1) || '0.0'}:1
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Risk Score</span>
                    <span className={`font-medium ${riskLevel.color}`}>
                      {riskMetrics?.risk_score?.toFixed(1) || '0.0'}/10
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Risk Level</span>
                    <Badge variant="outline" className={`${riskLevel.bgColor} ${riskLevel.color}`}>
                      {riskLevel.level}
                    </Badge>
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

export default RiskView

