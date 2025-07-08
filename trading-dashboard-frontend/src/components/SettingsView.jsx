import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Save, 
  RefreshCw,
  Settings,
  Shield,
  TrendingUp,
  Database,
  Globe,
  AlertCircle,
  CheckCircle
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const SettingsView = () => {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState(null)

  useEffect(() => {
    fetchConfig()
  }, [])

  const fetchConfig = async () => {
    try {
      const response = await fetch('/api/trading/config')
      const data = await response.json()
      setConfig(data)
    } catch (error) {
      console.error('Error fetching config:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveConfig = async () => {
    try {
      setSaving(true)
      const response = await fetch('/api/trading/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      })

      if (response.ok) {
        setSaveStatus('success')
        setTimeout(() => setSaveStatus(null), 3000)
      } else {
        setSaveStatus('error')
        setTimeout(() => setSaveStatus(null), 3000)
      }
    } catch (error) {
      console.error('Error saving config:', error)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus(null), 3000)
    } finally {
      setSaving(false)
    }
  }

  const updateConfig = (section, key, value) => {
    setConfig(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }))
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
            Bot Settings
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Configure your trading bot parameters and preferences
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={fetchConfig}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button onClick={saveConfig} disabled={saving}>
            {saving ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Save Changes
          </Button>
        </div>
      </div>

      {/* Save Status */}
      {saveStatus && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`flex items-center space-x-2 p-3 rounded-lg ${
            saveStatus === 'success' 
              ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200' 
              : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
          }`}
        >
          {saveStatus === 'success' ? (
            <CheckCircle className="h-5 w-5" />
          ) : (
            <AlertCircle className="h-5 w-5" />
          )}
          <span>
            {saveStatus === 'success' 
              ? 'Configuration saved successfully!' 
              : 'Error saving configuration. Please try again.'
            }
          </span>
        </motion.div>
      )}

      {/* Settings Tabs */}
      <Tabs defaultValue="risk" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="risk" className="flex items-center space-x-2">
            <Shield className="h-4 w-4" />
            <span>Risk Management</span>
          </TabsTrigger>
          <TabsTrigger value="trading" className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4" />
            <span>Trading</span>
          </TabsTrigger>
          <TabsTrigger value="data" className="flex items-center space-x-2">
            <Database className="h-4 w-4" />
            <span>Data Sources</span>
          </TabsTrigger>
          <TabsTrigger value="broker" className="flex items-center space-x-2">
            <Globe className="h-4 w-4" />
            <span>Broker</span>
          </TabsTrigger>
        </TabsList>

        {/* Risk Management Tab */}
        <TabsContent value="risk">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Risk Management Settings</CardTitle>
                <CardDescription>
                  Configure risk limits and position sizing parameters
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="max-risk-per-trade">Max Risk Per Trade (%)</Label>
                    <Input
                      id="max-risk-per-trade"
                      type="number"
                      step="0.01"
                      min="0"
                      max="10"
                      value={(config?.risk_management?.max_risk_per_trade * 100) || 0}
                      onChange={(e) => updateConfig('risk_management', 'max_risk_per_trade', parseFloat(e.target.value) / 100)}
                    />
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Maximum percentage of capital to risk per trade
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="max-total-exposure">Max Total Exposure (%)</Label>
                    <Input
                      id="max-total-exposure"
                      type="number"
                      step="0.01"
                      min="0"
                      max="100"
                      value={(config?.risk_management?.max_total_exposure * 100) || 0}
                      onChange={(e) => updateConfig('risk_management', 'max_total_exposure', parseFloat(e.target.value) / 100)}
                    />
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Maximum total portfolio exposure
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="stop-loss">Stop Loss (%)</Label>
                    <Input
                      id="stop-loss"
                      type="number"
                      step="0.01"
                      min="0"
                      max="10"
                      value={(config?.risk_management?.stop_loss_pct * 100) || 0}
                      onChange={(e) => updateConfig('risk_management', 'stop_loss_pct', parseFloat(e.target.value) / 100)}
                    />
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Default stop loss percentage
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="take-profit">Take Profit (%)</Label>
                    <Input
                      id="take-profit"
                      type="number"
                      step="0.01"
                      min="0"
                      max="20"
                      value={(config?.risk_management?.take_profit_pct * 100) || 0}
                      onChange={(e) => updateConfig('risk_management', 'take_profit_pct', parseFloat(e.target.value) / 100)}
                    />
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Default take profit percentage
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Trading Parameters Tab */}
        <TabsContent value="trading">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Trading Parameters</CardTitle>
                <CardDescription>
                  Configure trading strategy and execution settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="min-confidence">Minimum Confidence (%)</Label>
                    <Input
                      id="min-confidence"
                      type="number"
                      step="0.01"
                      min="0"
                      max="100"
                      value={(config?.trading_parameters?.min_confidence * 100) || 0}
                      onChange={(e) => updateConfig('trading_parameters', 'min_confidence', parseFloat(e.target.value) / 100)}
                    />
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Minimum signal confidence to execute trades
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="max-positions">Maximum Positions</Label>
                    <Input
                      id="max-positions"
                      type="number"
                      min="1"
                      max="20"
                      value={config?.trading_parameters?.max_positions || 0}
                      onChange={(e) => updateConfig('trading_parameters', 'max_positions', parseInt(e.target.value))}
                    />
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Maximum number of concurrent positions
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="position-sizing">Position Sizing Method</Label>
                    <Select
                      value={config?.trading_parameters?.position_sizing_method || 'kelly_criterion'}
                      onValueChange={(value) => updateConfig('trading_parameters', 'position_sizing_method', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="fixed">Fixed Size</SelectItem>
                        <SelectItem value="kelly_criterion">Kelly Criterion</SelectItem>
                        <SelectItem value="volatility_adjusted">Volatility Adjusted</SelectItem>
                        <SelectItem value="risk_parity">Risk Parity</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Method for calculating position sizes
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="rebalance-frequency">Rebalance Frequency</Label>
                    <Select
                      value={config?.trading_parameters?.rebalance_frequency || 'daily'}
                      onValueChange={(value) => updateConfig('trading_parameters', 'rebalance_frequency', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hourly">Hourly</SelectItem>
                        <SelectItem value="daily">Daily</SelectItem>
                        <SelectItem value="weekly">Weekly</SelectItem>
                        <SelectItem value="monthly">Monthly</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      How often to rebalance the portfolio
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Data Sources Tab */}
        <TabsContent value="data">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Data Source Settings</CardTitle>
                <CardDescription>
                  Configure market data providers and update frequencies
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="primary-provider">Primary Data Provider</Label>
                    <Select
                      value={config?.data_sources?.primary_provider || 'twelve_data'}
                      onValueChange={(value) => updateConfig('data_sources', 'primary_provider', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="twelve_data">Twelve Data</SelectItem>
                        <SelectItem value="fcs_api">FCS API</SelectItem>
                        <SelectItem value="free_forex_api">Free Forex API</SelectItem>
                        <SelectItem value="alpha_vantage">Alpha Vantage</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Primary source for market data
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="update-frequency">Update Frequency</Label>
                    <Select
                      value={config?.data_sources?.update_frequency || '1min'}
                      onValueChange={(value) => updateConfig('data_sources', 'update_frequency', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1sec">1 Second</SelectItem>
                        <SelectItem value="5sec">5 Seconds</SelectItem>
                        <SelectItem value="15sec">15 Seconds</SelectItem>
                        <SelectItem value="30sec">30 Seconds</SelectItem>
                        <SelectItem value="1min">1 Minute</SelectItem>
                        <SelectItem value="5min">5 Minutes</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      How often to update market data
                    </p>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="fallback-providers">Fallback Providers</Label>
                  <Textarea
                    id="fallback-providers"
                    value={config?.data_sources?.fallback_providers?.join(', ') || ''}
                    onChange={(e) => updateConfig('data_sources', 'fallback_providers', e.target.value.split(', ').filter(p => p.trim()))}
                    placeholder="fcs_api, free_forex_api"
                  />
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Comma-separated list of backup data providers
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Broker Settings Tab */}
        <TabsContent value="broker">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Broker Settings</CardTitle>
                <CardDescription>
                  Configure broker connection and trading account settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="broker-type">Broker Type</Label>
                    <Select
                      value={config?.broker_settings?.broker_type || 'paper_trading'}
                      onValueChange={(value) => updateConfig('broker_settings', 'broker_type', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="paper_trading">Paper Trading</SelectItem>
                        <SelectItem value="exness">Exness</SelectItem>
                        <SelectItem value="mt4">MetaTrader 4</SelectItem>
                        <SelectItem value="mt5">MetaTrader 5</SelectItem>
                        <SelectItem value="oanda">OANDA</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Select your broker platform
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="account-id">Account ID</Label>
                    <Input
                      id="account-id"
                      type="text"
                      value={config?.broker_settings?.account_id || ''}
                      onChange={(e) => updateConfig('broker_settings', 'account_id', e.target.value)}
                      placeholder="Enter your account ID"
                    />
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Your trading account identifier
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="leverage">Leverage</Label>
                    <Select
                      value={config?.broker_settings?.leverage?.toString() || '100'}
                      onValueChange={(value) => updateConfig('broker_settings', 'leverage', parseInt(value))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1:1</SelectItem>
                        <SelectItem value="10">10:1</SelectItem>
                        <SelectItem value="50">50:1</SelectItem>
                        <SelectItem value="100">100:1</SelectItem>
                        <SelectItem value="200">200:1</SelectItem>
                        <SelectItem value="500">500:1</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Trading leverage ratio
                    </p>
                  </div>
                </div>

                {config?.broker_settings?.broker_type === 'paper_trading' && (
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <AlertCircle className="h-5 w-5 text-blue-600" />
                      <span className="font-medium text-blue-800 dark:text-blue-200">
                        Paper Trading Mode
                      </span>
                    </div>
                    <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                      You are currently in paper trading mode. No real money will be used for trades.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>

      {/* Advanced Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Advanced Settings</CardTitle>
            <CardDescription>
              Additional configuration options for experienced users
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="enable-logging">Enable Detailed Logging</Label>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Log detailed trading decisions and market data
                </p>
              </div>
              <Switch id="enable-logging" />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="enable-notifications">Enable Notifications</Label>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Receive alerts for important trading events
                </p>
              </div>
              <Switch id="enable-notifications" defaultChecked />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="auto-restart">Auto-restart on Error</Label>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Automatically restart the bot if it encounters errors
                </p>
              </div>
              <Switch id="auto-restart" defaultChecked />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="backup-config">Backup Configuration</Label>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Automatically backup configuration changes
                </p>
              </div>
              <Switch id="backup-config" defaultChecked />
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

export default SettingsView

