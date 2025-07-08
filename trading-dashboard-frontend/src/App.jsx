import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import './App.css'

// Import components
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './components/Dashboard'
import TradingView from './components/TradingView'
import PerformanceView from './components/PerformanceView'
import StrategiesView from './components/StrategiesView'
import RiskView from './components/RiskView'
import SettingsView from './components/SettingsView'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [currentView, setCurrentView] = useState('dashboard')
  const [botStatus, setBotStatus] = useState('active')
  const [alerts, setAlerts] = useState([])

  // Fetch initial data
  useEffect(() => {
    fetchAlerts()
    fetchBotStatus()
  }, [])

  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/trading/alerts')
      const data = await response.json()
      setAlerts(data)
    } catch (error) {
      console.error('Error fetching alerts:', error)
    }
  }

  const fetchBotStatus = async () => {
    try {
      const response = await fetch('/api/trading/status')
      const data = await response.json()
      setBotStatus(data.bot_active ? 'active' : 'inactive')
    } catch (error) {
      console.error('Error fetching bot status:', error)
    }
  }

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard />
      case 'trading':
        return <TradingView />
      case 'performance':
        return <PerformanceView />
      case 'strategies':
        return <StrategiesView />
      case 'risk':
        return <RiskView />
      case 'settings':
        return <SettingsView />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="flex">
        {/* Sidebar */}
        <Sidebar 
          isOpen={sidebarOpen}
          currentView={currentView}
          onViewChange={setCurrentView}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
        />

        {/* Main Content */}
        <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-16'}`}>
          {/* Header */}
          <Header 
            botStatus={botStatus}
            alerts={alerts}
            onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          />

          {/* Main Content Area */}
          <main className="p-6">
            <motion.div
              key={currentView}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {renderCurrentView()}
            </motion.div>
          </main>
        </div>
      </div>
    </div>
  )
}

export default App

