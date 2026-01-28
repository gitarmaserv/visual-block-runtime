import React, { useState, useEffect } from 'react'
import { useStore } from '../store'

function LogPanel() {
  const store = useStore()
  const [autoScroll, setAutoScroll] = useState(true)
  const logEndRef = React.useRef(null)
  
  const { logLines, logFilter, executionState } = store
  
  const filteredLines = logLines.filter(line => {
    if (logFilter === 'DEBUG') return true
    if (logFilter === 'INFO') return !line.includes('lvl=DEBUG')
    if (logFilter === 'WARN') return line.includes('lvl=WARN') || line.includes('lvl=ERROR')
    if (logFilter === 'ERROR') return line.includes('lvl=ERROR')
    return true
  })
  
  useEffect(() => {
    if (autoScroll && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logLines, autoScroll])
  
  const getLogClass = (line) => {
    if (line.includes('lvl=ERROR')) return 'log-line error'
    if (line.includes('lvl=WARN')) return 'log-line warn'
    if (line.includes('lvl=DEBUG')) return 'log-line debug'
    return 'log-line info'
  }
  
  return (
    <div className="log-panel">
      <div className="log-header">
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span className="panel-title" style={{ margin: 0 }}>Log</span>
          <select
            value={logFilter}
            onChange={(e) => store.setLogFilter(e.target.value)}
            className="form-input"
            style={{ padding: '4px 8px', fontSize: '12px' }}
          >
            <option value="DEBUG">DEBUG</option>
            <option value="INFO">INFO</option>
            <option value="WARN">WARN</option>
            <option value="ERROR">ERROR</option>
          </select>
        </div>
        
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <label style={{ fontSize: '12px', color: '#a0a0a0', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            Auto-scroll
          </label>
          <span style={{ fontSize: '12px', color: '#a0a0a0' }}>
            {filteredLines.length} lines
          </span>
        </div>
      </div>
      
      <div className="log-content">
        {filteredLines.map((line, i) => (
          <div key={i} className={getLogClass(line)}>
            {line}
          </div>
        ))}
        <div ref={logEndRef} />
        
        {filteredLines.length === 0 && (
          <div style={{ color: '#a0a0a0', textAlign: 'center', padding: '20px' }}>
            No log entries
          </div>
        )}
      </div>
    </div>
  )
}

export default LogPanel
