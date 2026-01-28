import React, { useEffect, useCallback } from 'react'
import { ReactFlow, 
         Controls, 
         Background, 
         MiniMap,
         addEdge,
         useNodesState,
         useEdgesState,
         Handle,
         Position,
         MarkerType
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useStore } from './store'
import NodePalette from './components/NodePalette'
import NodeInspector from './components/NodeInspector'
import LogPanel from './components/LogPanel'
import Toolbar from './components/Toolbar'

// Custom node component
function CustomNode({ data, selected }) {
  const { executionState, activeNodeId } = useStore()
  
  let className = 'react-flow__node'
  if (selected) className += ' selected'
  if (activeNodeId === data.id) {
    className += ` react-flow__node-${executionState.toLowerCase()}`
  }
  
  return (
    <div className={className}>
      <Handle type="target" position={Position.Left} />
      <div style={{ padding: '10px', minWidth: '120px' }}>
        <div style={{ fontWeight: 600, fontSize: '13px', marginBottom: '4px' }}>
          {data.node_title || data.plugin_id}
        </div>
        <div style={{ fontSize: '11px', color: '#a0a0a0' }}>
          {data.plugin_id}
        </div>
        {data.breakpoint && (
          <div style={{ 
            position: 'absolute', 
            top: -8, 
            right: -8, 
            width: 16, 
            height: 16, 
            background: '#ff9800',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 10,
            color: 'white'
          }}>
            ⏸
          </div>
        )}
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  )
}

const nodeTypes = {
  custom: CustomNode
}

function App() {
  const store = useStore()
  
  // Initialize React Flow with store state
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  
  // Sync with store
  useEffect(() => {
    setNodes(store.nodes)
  }, [store.nodes])
  
  useEffect(() => {
    setEdges(store.edges)
  }, [store.edges])
  
  const onConnect = useCallback((params) => {
    const newEdge = {
      ...params,
      id: `e_${Date.now()}`,
      type: 'default',
      animated: true,
      style: { stroke: '#e94560', strokeWidth: 2 },
      data: { branch: 'ok' },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#e94560'
      }
    }
    
    store.setEdges(addEdge(newEdge, store.edges))
  }, [store.edges, store])
  
  const onNodeClick = useCallback((event, node) => {
    store.selectNode(node.id)
  }, [store])
  
  const onPaneClick = useCallback(() => {
    store.selectNode(null)
  }, [store])
  
  return (
    <div className="app-container">
      {/* Left sidebar - Node palette */}
      <aside className="sidebar-left">
        <NodePalette />
      </aside>
      
      {/* Main content - React Flow */}
      <main className="main-content">
        <Toolbar />
        <div style={{ flex: 1, width: '100%', height: 'calc(100% - 60px)' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="bottom-right"
          >
            <Controls />
            <MiniMap 
              nodeColor="#e94560"
              maskColor="rgba(26, 26, 46, 0.8)"
            />
            <Background color="#2a2a4a" gap={20} />
          </ReactFlow>
        </div>
        <LogPanel />
      </main>
      
      {/* Right sidebar - Node inspector */}
      <aside className="sidebar-right">
        <NodeInspector />
      </aside>
    </div>
  )
}

export default App
