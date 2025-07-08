import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Bell, 
  Power, 
  RefreshCw, 
  AlertTriangle,
  CheckCircle,
  Info,
  X
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const Header = ({ botStatus, alerts, onToggleSidebar }) => {
  const [showAlerts, setShowAlerts] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const unacknowledgedAlerts = alerts.filter(alert => !alert.acknowledged)

  const getAlertIcon = (type) => {
    switch (type) {
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'info':
        return <Info className="h-4 w-4 text-blue-500" />
      default:
        return <Info className="h-4 w-4 text-gray-500" />
    }
  }

  const handleBotToggle = async () => {
    try {
      const action = botStatus === 'active' ? 'stop' : 'start'
      const response = await fetch(`/api/trading/bot/${action}`, {
        method: 'POST'
      })
      
      if (response.ok) {
        // Refresh page or update status
        window.location.reload()
      }
    } catch (error) {
      console.error('Error toggling bot:', error)
    }
  }

  const handleRestart = async () => {
    try {
      const response = await fetch('/api/trading/bot/restart', {
        method: 'POST'
      })
      
      if (response.ok) {
        window.location.reload()
      }
    } catch (error) {
      console.error('Error restarting bot:', error)
    }
  }

  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side - Status */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              botStatus === 'active' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`}></div>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Bot Status: {botStatus === 'active' ? 'Active' : 'Inactive'}
            </span>
          </div>
          
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {currentTime.toLocaleString()}
          </div>
        </div>

        {/* Right side - Controls and Alerts */}
        <div className="flex items-center space-x-3">
          {/* Bot Controls */}
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRestart}
              className="flex items-center space-x-1"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Restart</span>
            </Button>
            
            <Button
              variant={botStatus === 'active' ? 'destructive' : 'default'}
              size="sm"
              onClick={handleBotToggle}
              className="flex items-center space-x-1"
            >
              <Power className="h-4 w-4" />
              <span>{botStatus === 'active' ? 'Stop' : 'Start'}</span>
            </Button>
          </div>

          {/* Alerts */}
          <div className="relative">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAlerts(!showAlerts)}
              className="relative"
            >
              <Bell className="h-4 w-4" />
              {unacknowledgedAlerts.length > 0 && (
                <Badge 
                  variant="destructive" 
                  className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
                >
                  {unacknowledgedAlerts.length}
                </Badge>
              )}
            </Button>

            {/* Alerts Dropdown */}
            {showAlerts && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute right-0 top-full mt-2 w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50"
              >
                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Alerts
                    </h3>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowAlerts(false)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="max-h-64 overflow-y-auto">
                  {alerts.length === 0 ? (
                    <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                      No alerts
                    </div>
                  ) : (
                    alerts.map((alert) => (
                      <div
                        key={alert.id}
                        className={`p-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0 ${
                          !alert.acknowledged ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                        }`}
                      >
                        <div className="flex items-start space-x-3">
                          {getAlertIcon(alert.type)}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-gray-900 dark:text-white">
                              {alert.message}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              {new Date(alert.timestamp).toLocaleString()}
                            </p>
                          </div>
                          {!alert.acknowledged && (
                            <Badge variant="secondary" className="text-xs">
                              New
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {unacknowledgedAlerts.length > 0 && (
                  <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={() => {
                        // Mark all alerts as acknowledged
                        setShowAlerts(false)
                      }}
                    >
                      Mark All as Read
                    </Button>
                  </div>
                )}
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header

