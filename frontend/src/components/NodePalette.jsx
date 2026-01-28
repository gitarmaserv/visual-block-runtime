import React, { useState } from 'react'
import { useStore } from '../store'

function NodePalette() {
  const store = useStore()
  const [search, setSearch] = useState('')
  
  const categories = Object.keys(store.pluginsByCategory)
    .filter(cat => {
      if (!search) return true
      const plugins = store.pluginsByCategory[cat]
      return plugins.some(p => 
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.plugin_id.toLowerCase().includes(search.toLowerCase())
      )
    })
  
  const handleDragStart = (e, plugin) => {
    e.dataTransfer.setData('application/reactflow', JSON.stringify(plugin))
    e.dataTransfer.effectAllowed = 'move'
  }
  
  const handleAddNode = (plugin) => {
    store.addNode(plugin)
  }
  
  return (
    <div className="panel" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="panel-title">Node Palette</div>
      
      <input
        type="text"
        placeholder="Search nodes..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="form-input"
        style={{ marginBottom: '12px' }}
      />
      
      <div style={{ flex: 1, overflow: 'auto' }}>
        {categories.map(category => {
          const isExpanded = store.categoriesExpanded[category] !== false
          const plugins = store.pluginsByCategory[category]
          
          return (
            <div key={category} className="node-category">
              <div 
                className="category-header"
                onClick={() => store.toggleCategory(category)}
              >
                <span className="category-name">{category}</span>
                <span className="category-toggle">
                  {isExpanded ? '▼' : '▶'}
                </span>
              </div>
              
              {isExpanded && (
                <div className="category-items">
                  {plugins.map(plugin => (
                    <div 
                      key={plugin.plugin_id}
                      className="node-item"
                      draggable
                      onDragStart={(e) => handleDragStart(e, plugin)}
                      onClick={() => handleAddNode(plugin)}
                    >
                      <div className="node-icon">
                        {plugin.name.charAt(0)}
                      </div>
                      <span className="node-name">{plugin.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
        
        {categories.length === 0 && (
          <div style={{ padding: '20px', textAlign: 'center', color: '#a0a0a0' }}>
            No nodes found
          </div>
        )}
      </div>
    </div>
  )
}

export default NodePalette
