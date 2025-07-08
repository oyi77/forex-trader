import { motion } from 'framer-motion'
import { 
  BarChart3, 
  TrendingUp, 
  Shield, 
  Settings, 
  Activity,
  DollarSign,
  Menu,
  Bot
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const Sidebar = ({ isOpen, currentView, onViewChange, onToggle }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'trading', label: 'Trading', icon: TrendingUp },
    { id: 'performance', label: 'Performance', icon: DollarSign },
    { id: 'strategies', label: 'Strategies', icon: Bot },
    { id: 'risk', label: 'Risk Management', icon: Shield },
    { id: 'settings', label: 'Settings', icon: Settings }
  ]

  return (
    <motion.div
      initial={{ x: -250 }}
      animate={{ x: 0 }}
      className={`fixed left-0 top-0 h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 z-30 transition-all duration-300 ${
        isOpen ? 'w-64' : 'w-16'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center space-x-2"
          >
            <Activity className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              ForexBot
            </span>
          </motion.div>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggle}
          className="p-2"
        >
          <Menu className="h-4 w-4" />
        </Button>
      </div>

      {/* Navigation */}
      <nav className="mt-6">
        <ul className="space-y-2 px-3">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = currentView === item.id

            return (
              <li key={item.id}>
                <Button
                  variant={isActive ? "default" : "ghost"}
                  className={`w-full justify-start ${
                    isOpen ? 'px-4' : 'px-2'
                  } ${
                    isActive 
                      ? 'bg-blue-600 text-white hover:bg-blue-700' 
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                  onClick={() => onViewChange(item.id)}
                >
                  <Icon className={`h-5 w-5 ${isOpen ? 'mr-3' : ''}`} />
                  {isOpen && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.1 }}
                    >
                      {item.label}
                    </motion.span>
                  )}
                </Button>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Status Indicator */}
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute bottom-4 left-4 right-4"
        >
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-green-700 dark:text-green-300 font-medium">
                Bot Active
              </span>
            </div>
            <p className="text-xs text-green-600 dark:text-green-400 mt-1">
              All systems operational
            </p>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default Sidebar

