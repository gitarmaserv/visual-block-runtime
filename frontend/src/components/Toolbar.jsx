import React, { useState } from 'react'
import { useStore } from '../store'

function Toolbar() {
  const store = useStore()
  const { executionState, selectedNodeId, projectName, isProjectOpen } = store
  
  const isIdle = executionState === 'Idle'
  const isRunning = executionState === 'Running'
  const isPaused = executionState === 'Paused'
  const [showProjectDialog, setShowProjectDialog] = useState('none') // 'none', 'create'
  const [projectInput, setProjectInput] = useState('')
  
  const handleCreateProject = () => {
    setShowProjectDialog('create')
  }
  
  const handleOpenProject = async () => {
    if (window.electronAPI && window.electronAPI.selectFile) {
      const path = await window.electronAPI.selectFile()
      if (path) {
        await store.openProject(path)
      }
    }
  }
  
  const handleSubmitProject = async () => {
    if (!projectInput.trim()) return
    
    const path = `projects/${projectInput}.botui`
    await store.createProject(projectInput, path)
    setShowProjectDialog('none')
    setProjectInput('')
  }
  
  const handleCancel = () => {
    setShowProjectDialog('none')
    setProjectInput('')
  }
  
  if (!isProjectOpen) {
    return (
      <>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
          padding: '12px 16px',
          background: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-color)'
        }}>
          <button className="btn btn-primary" onClick={handleCreateProject}>
            + Create New Project
          </button>
          <button className="btn btn-secondary" onClick={handleOpenProject}>
            📂 Open Project
          </button>
        </div>
        
        {showProjectDialog === 'create' && (
          <div style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              background: 'var(--bg-secondary)',
              padding: '24px',
              borderRadius: '8px',
              minWidth: '300px'
            }}>
              <h3 style={{ marginBottom: '16px' }}>Create New Project</h3>
              <input
                type="text"
                value={projectInput}
                onChange={(e) => setProjectInput(e.target.value)}
                placeholder="Project name"
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  marginBottom: '16px',
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '4px',
                  color: 'var(--text-primary)'
                }}
                autoFocus
              />
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                <button className="btn btn-secondary" onClick={handleCancel}>
                  Cancel
                </button>
                <button className="btn btn-primary" onClick={handleSubmitProject}>
                  Create
                </button>
              </div>
            </div>
          </div>
        )}
      </>
    )
  }
  
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
        {projectName || 'Visual Block Runtime'}
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
        <button
          className="btn btn-secondary"
          onClick={() => store.saveGraph()}
        >
          💾 Save
        </button>

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
