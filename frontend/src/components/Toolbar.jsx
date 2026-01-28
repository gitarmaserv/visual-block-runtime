import React from 'react'
import { useStore } from '../store'

function Toolbar() {
  const store = useStore()
  const { executionState, selectedNodeId } = store
  
  const isIdle = executionState === 'Idle'
  const isRunning = executionState === 'Running'
  const isPaused = executionState === 'Paused'
  
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      padding: '12px 16px',
      background: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border-color)'
    }}>
      <div style={{ fontWeight: 600, fontSize: '16px' }}>
        {store.projectName || 'Visual Block Runtime'}
      </div>
      
      <div style={{ flex: 1 }} />
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {/* Status indicator */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          background: 'var(--bg-tertiary)',
          borderRadius: '6px',
          fontSize: '13px'
        }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: isRunning ? 'var(--warning)' : 
                        isPaused ? 'var(--warning)' : 
                        'var(--success)'
          }} />
          <span>{executionState}</span>
          {store.activeNodeTitle && (
            <span style={{ color: '#a0a0a0' }}>
              → {store.activeNodeTitle}
            </span>
          )}
        </div>
        
        {/* Actions */}
        {isIdle && (
          <>
            <button 
              className="btn btn-primary"
              onClick={() => store.startFromBeginning()}
            >
              ▶ Start from Beginning
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => store.startFromSelected()}
              disabled={!selectedNodeId}
            >
              ▶ Start from Selected
            </button>
          </>
        )}
        
        {isRunning && (
          <>
            <button 
              className="btn btn-secondary"
              onClick={() => store.softStop()}
            >
              ⏹ Soft Stop
            </button>
            <button 
              className="btn btn-danger"
              onClick={() => store.hardStop()}
            >
              ⏹⏹ Hard Stop
            </button>
          </>
        )}
        
        {isPaused && (
          <>
            <button 
              className="btn btn-success"
              onClick={() => store.resume()}
            >
              ▶ Resume
            </button>
            <button 
              className="btn btn-danger"
              onClick={() => store.hardStop()}
            >
              ⏹⏹ Stop
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default Toolbar
