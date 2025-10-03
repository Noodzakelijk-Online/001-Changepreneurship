import React, { useEffect, useCallback, useState } from 'react'
import { Badge } from '@/components/ui/badge.jsx'
import { CheckCircle, Save, AlertCircle, Wifi, WifiOff } from 'lucide-react'

const AutoSaveManager = ({ data, onSave, saveInterval = 30000 }) => {
  const [saveStatus, setSaveStatus] = useState('saved') // 'saving', 'saved', 'error', 'offline'
  const [lastSaved, setLastSaved] = useState(null)
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Auto-save function
  const performSave = useCallback(async () => {
    if (!isOnline) {
      setSaveStatus('offline')
      return
    }

    try {
      setSaveStatus('saving')
      
      // Save to localStorage as backup
      localStorage.setItem('changepreneurship_assessment_backup', JSON.stringify({
        data,
        timestamp: Date.now()
      }))

      // Call the provided save function (could be API call)
      if (onSave) {
        await onSave(data)
      }

      setSaveStatus('saved')
      setLastSaved(new Date())
    } catch (error) {
      console.error('Auto-save failed:', error)
      setSaveStatus('error')
    }
  }, [data, onSave, isOnline])

  // Auto-save on data changes with debouncing
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (data && Object.keys(data).length > 0) {
        performSave()
      }
    }, 2000) // 2 second debounce

    return () => clearTimeout(timeoutId)
  }, [data, performSave])

  // Periodic auto-save
  useEffect(() => {
    const intervalId = setInterval(() => {
      if (data && Object.keys(data).length > 0) {
        performSave()
      }
    }, saveInterval)

    return () => clearInterval(intervalId)
  }, [data, performSave, saveInterval])

  // Save on page unload
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (saveStatus === 'saving') {
        e.preventDefault()
        e.returnValue = 'Your assessment is still being saved. Are you sure you want to leave?'
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [saveStatus])

  // Restore from backup on component mount
  useEffect(() => {
    const backup = localStorage.getItem('changepreneurship_assessment_backup')
    if (backup) {
      try {
        const { data: backupData, timestamp } = JSON.parse(backup)
        const backupAge = Date.now() - timestamp
        
        // If backup is less than 1 hour old, it might be useful
        if (backupAge < 3600000) {
          console.log('Assessment backup found:', new Date(timestamp))
          // You could emit an event here to ask user if they want to restore
        }
      } catch (error) {
        console.error('Failed to parse backup:', error)
      }
    }
  }, [])

  const getSaveStatusInfo = () => {
    switch (saveStatus) {
      case 'saving':
        return {
          icon: Save,
          text: 'Saving...',
          variant: 'secondary',
          className: 'animate-pulse'
        }
      case 'saved':
        return {
          icon: CheckCircle,
          text: lastSaved ? `Saved ${formatTime(lastSaved)}` : 'Saved',
          variant: 'outline',
          className: 'text-green-600'
        }
      case 'error':
        return {
          icon: AlertCircle,
          text: 'Save failed',
          variant: 'destructive',
          className: ''
        }
      case 'offline':
        return {
          icon: WifiOff,
          text: 'Offline - will save when connected',
          variant: 'secondary',
          className: 'text-orange-600'
        }
      default:
        return {
          icon: Save,
          text: 'Ready to save',
          variant: 'outline',
          className: ''
        }
    }
  }

  const formatTime = (date) => {
    const now = new Date()
    const diff = now - date
    
    if (diff < 60000) return 'just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    return date.toLocaleDateString()
  }

  const statusInfo = getSaveStatusInfo()
  const StatusIcon = statusInfo.icon

  return (
    <div className="flex items-center gap-2">
      {!isOnline && (
        <Badge variant="outline" className="text-orange-600">
          <WifiOff className="h-3 w-3 mr-1" />
          Offline
        </Badge>
      )}
      
      <Badge 
        variant={statusInfo.variant} 
        className={`${statusInfo.className} transition-all duration-200`}
      >
        <StatusIcon className="h-3 w-3 mr-1" />
        {statusInfo.text}
      </Badge>
    </div>
  )
}

// Hook for using auto-save functionality
export const useAutoSave = (data, saveFunction, options = {}) => {
  const [saveStatus, setSaveStatus] = useState('idle')
  
  const save = useCallback(async (dataToSave) => {
    try {
      setSaveStatus('saving')
      
      // Always save to localStorage as backup
      localStorage.setItem('changepreneurship_assessment_data', JSON.stringify({
        data: dataToSave,
        timestamp: Date.now()
      }))

      // Call custom save function if provided
      if (saveFunction) {
        await saveFunction(dataToSave)
      }

      setSaveStatus('saved')
    } catch (error) {
      console.error('Save failed:', error)
      setSaveStatus('error')
    }
  }, [saveFunction])

  return {
    save,
    saveStatus,
    AutoSaveComponent: (props) => (
      <AutoSaveManager 
        data={data} 
        onSave={save} 
        {...options} 
        {...props} 
      />
    )
  }
}

export default AutoSaveManager

