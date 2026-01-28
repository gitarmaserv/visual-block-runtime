import React from 'react'
import { useStore } from '../store'

function NodeInspector() {
  const store = useStore()
  const { selectedNodeId, nodes, nodeSettings, projectVars } = store
  
  if (!selectedNodeId) {
    return (
      <div className="panel" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#a0a0a0' }}>
        Select a node to view its settings
      </div>
    )
  }
  
  const node = nodes.find(n => n.id === selectedNodeId)
  if (!node) return null
  
  const settings = nodeSettings[selectedNodeId] || {}
  const spec = store.plugins.find(p => p.plugin_id === node.data.plugin_id)?.spec
  
  const handleParamChange = (key, value) => {
    const newParams = { ...node.data.params, [key]: value }
    store.updateNodeSettings(selectedNodeId, { params: newParams })
  }
  
  const handleTitleChange = (e) => {
    store.updateNodeSettings(selectedNodeId, { node_title: e.target.value })
  }
  
  const handleBreakpointChange = (e) => {
    store.updateNodeSettings(selectedNodeId, { breakpoint: e.target.checked })
  }
  
  const handleErrorToFailChange = (e) => {
    store.updateNodeSettings(selectedNodeId, { error_to_fail: e.target.checked })
  }
  
  const handleInputVarChange = (e) => {
    store.updateNodeSettings(selectedNodeId, { input_var_ref: e.target.value || null })
  }
  
  const handleCreateOutputVar = async () => {
    const baseName = `output_${selectedNodeId}`
    const result = await store.createProjectVar(baseName)
    if (result) {
      store.updateNodeSettings(selectedNodeId, { output_var_ref: result.ref })
    }
  }
  
  return (
    <div className="panel" style={{ flex: 1, overflow: 'auto' }}>
      <div className="panel-title">Node Inspector</div>
      
      {/* General settings */}
      <div className="form-group">
        <label className="form-label">Title</label>
        <input
          type="text"
          value={node.data.node_title || ''}
          onChange={handleTitleChange}
          className="form-input"
        />
      </div>
      
      <div style={{ 
        padding: '8px 12px', 
        background: 'var(--bg-tertiary)', 
        borderRadius: '6px',
        marginBottom: '16px',
        fontSize: '12px'
      }}>
        <div style={{ color: '#a0a0a0' }}>Plugin ID</div>
        <div>{node.data.plugin_id}</div>
        {spec && (
          <>
            <div style={{ color: '#a0a0a0', marginTop: '8px' }}>Description</div>
            <div>{spec.description}</div>
          </>
        )}
      </div>
      
      {/* Checkboxes */}
      <div className="form-group">
        <label className="form-checkbox">
          <input
            type="checkbox"
            checked={node.data.breakpoint || false}
            onChange={handleBreakpointChange}
          />
          <span>Breakpoint (pause on this node)</span>
        </label>
      </div>
      
      <div className="form-group">
        <label className="form-checkbox">
          <input
            type="checkbox"
            checked={node.data.error_to_fail || false}
            onChange={handleErrorToFailChange}
          />
          <span>Error to Fail (treat errors as FAIL branch)</span>
        </label>
      </div>
      
      {/* Input/Output selection */}
      {spec?.requires_input && (
        <div className="form-group">
          <label className="form-label">Input Variable</label>
          <select
            value={node.data.input_var_ref || ''}
            onChange={handleInputVarChange}
            className="form-input"
          >
            <option value="">-- Select variable --</option>
            {projectVars.map(v => (
              <option key={v.var_id} value={`proj:${v.var_id}`}>
                {v.title}
              </option>
            ))}
          </select>
        </div>
      )}
      
      {spec?.produces_output && (
        <div className="form-group">
          <label className="form-label">Output Variable</label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <select
              value={node.data.output_var_ref || ''}
              onChange={(e) => store.updateNodeSettings(selectedNodeId, { output_var_ref: e.target.value || null })}
              className="form-input"
              style={{ flex: 1 }}
            >
              <option value="">-- Select variable --</option>
              {projectVars.map(v => (
                <option key={v.var_id} value={`proj:${v.var_id}`}>
                  {v.title}
                </option>
              ))}
            </select>
            <button 
              className="btn btn-secondary"
              onClick={handleCreateOutputVar}
              style={{ padding: '8px 12px' }}
              title="Create new variable"
            >
              +
            </button>
          </div>
        </div>
      )}
      
      {/* Parameters */}
      {spec?.params && spec.params.length > 0 && (
        <>
          <div className="panel-title" style={{ marginTop: '20px' }}>Parameters</div>
          
          {spec.params.map(param => {
            const isAdvanced = param.advanced
            const [showAdvanced, setShowAdvanced] = React.useState(false)
            
            if (isAdvanced && !showAdvanced) return null
            
            return (
              <div key={param.key} className="form-group">
                <label className="form-label tooltip" data-tooltip={param.help}>
                  {param.label}
                  {param.help && <span style={{ marginLeft: '6px', color: '#a0a0a0' }}>?</span>}
                </label>
                
                {param.type === 'string' && (
                  <input
                    type="text"
                    value={node.data.params[param.key] ?? param.default ?? ''}
                    onChange={(e) => handleParamChange(param.key, e.target.value)}
                    className="form-input"
                  />
                )}
                
                {param.type === 'int' && (
                  <input
                    type="number"
                    value={node.data.params[param.key] ?? param.default ?? 0}
                    onChange={(e) => handleParamChange(param.key, parseInt(e.target.value))}
                    className="form-input"
                  />
                )}
                
                {param.type === 'float' && (
                  <input
                    type="number"
                    step="0.01"
                    value={node.data.params[param.key] ?? param.default ?? 0}
                    onChange={(e) => handleParamChange(param.key, parseFloat(e.target.value))}
                    className="form-input"
                  />
                )}
                
                {param.type === 'bool' && (
                  <label className="form-checkbox">
                    <input
                      type="checkbox"
                      checked={node.data.params[param.key] ?? param.default ?? false}
                      onChange={(e) => handleParamChange(param.key, e.target.checked)}
                    />
                    <span>{param.help || param.label}</span>
                  </label>
                )}
                
                {param.type === 'text' && (
                  <textarea
                    value={node.data.params[param.key] ?? param.default ?? ''}
                    onChange={(e) => handleParamChange(param.key, e.target.value)}
                    className="form-input"
                    rows={3}
                  />
                )}
              </div>
            )
          })}
          
          {spec.params.some(p => p.advanced) && !showAdvanced && (
            <button 
              className="btn btn-secondary" 
              style={{ width: '100%', marginTop: '8px' }}
              onClick={() => setShowAdvanced(true)}
            >
              Show Advanced
            </button>
          )}
        </>
      )}
    </div>
  )
}

export default NodeInspector
