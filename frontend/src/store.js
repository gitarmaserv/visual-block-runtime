import { create } from 'zustand'
import axios from 'axios'

const API_BASE = '/api'

// Store for application state
export const useStore = create((set, get) => ({
  // Project state
  projectPath: null,
  projectName: null,
  isProjectOpen: false,
  
  // Graph state
  nodes: [],
  edges: [],
  viewport: { x: 0, y: 0, zoom: 1 },
  
  // Plugins
  plugins: [],
  pluginsByCategory: {},
  
  // Selection
  selectedNodeId: null,
  
  // Node settings
  nodeSettings: {},
  
  // Variables
  projectVars: [],
  
  // Execution state
  executionState: 'Idle',
  activeNodeId: null,
  activeNodeTitle: null,
  runId: null,
  
  // Log
  logLines: [],
  logFilter: 'INFO',
  
  // UI state
  categoriesExpanded: {},
  
  // Actions
  setProjectPath: (path) => set({ projectPath: path }),
  setProjectName: (name) => set({ projectName: name }),
  
  openProject: async (path) => {
    try {
      await axios.post(`${API_BASE}/projects/open`, { path })
      
      // Load graph
      const name = path.split('/').pop().replace('.botui', '')
      
      set({ 
        projectPath: path, 
        projectName: name, 
        isProjectOpen: true 
      })
      
      await get().loadGraph()
      await get().loadPlugins()
      await get().loadNodeSettings()
      await get().loadProjectVars()
      
      return true
    } catch (error) {
      console.error('Failed to open project:', error)
      return false
    }
  },
  
  createProject: async (name, path) => {
    try {
      await axios.post(`${API_BASE}/projects/create`, { name, path })
      await get().openProject(path)
      return true
    } catch (error) {
      console.error('Failed to create project:', error)
      return false
    }
  },
  
  loadGraph: async () => {
    const { projectPath, projectName } = get()
    if (!projectPath) return
    
    try {
      const res = await axios.get(`${API_BASE}/graph/load`, {
        params: { path: projectPath, name: projectName }
      })
      
      set({
        nodes: res.data.graph_json.nodes || [],
        edges: res.data.graph_json.edges || [],
        viewport: res.data.graph_json.viewport || { x: 0, y: 0, zoom: 1 }
      })
    } catch (error) {
      console.error('Failed to load graph:', error)
    }
  },
  
  saveGraph: async () => {
    const { projectPath, projectName, nodes, edges, viewport } = get()
    if (!projectPath) return
    
    try {
      await axios.post(`${API_BASE}/graph/save`, {
        path: projectPath,
        name: projectName,
        graph_json: { nodes, edges, viewport }
      })
    } catch (error) {
      console.error('Failed to save graph:', error)
    }
  },
  
  setNodes: (nodes) => {
    set({ nodes })
    get().saveGraph()
  },
  
  setEdges: (edges) => {
    set({ edges })
    get().saveGraph()
  },
  
  setViewport: (viewport) => {
    set({ viewport })
    get().saveGraph()
  },
  
  loadPlugins: async () => {
    try {
      const res = await axios.get(`${API_BASE}/plugins`)
      const plugins = res.data.plugins
      
      // Group by category
      const byCategory = {}
      plugins.forEach(p => {
        const cat = p.category || 'Other'
        if (!byCategory[cat]) byCategory[cat] = []
        byCategory[cat].push(p)
      })
      
      set({ plugins, pluginsByCategory: byCategory })
    } catch (error) {
      console.error('Failed to load plugins:', error)
    }
  },
  
  selectNode: (nodeId) => set({ selectedNodeId: nodeId }),
  
  loadNodeSettings: async () => {
    const { projectPath, projectName } = get()
    if (!projectPath) return
    
    try {
      const res = await axios.get(`${API_BASE}/nodes/settings`, {
        params: { path: projectPath, graph_name: projectName }
      })
      set({ nodeSettings: res.data.settings })
    } catch (error) {
      console.error('Failed to load node settings:', error)
    }
  },
  
  updateNodeSettings: async (nodeId, settings) => {
    const { projectPath, projectName } = get()
    
    try {
      await axios.post(`${API_BASE}/nodes/settings/update`, {
        path: projectPath,
        graph_name: projectName,
        node_uid: nodeId,
        settings
      })
      
      set(state => ({
        nodeSettings: {
          ...state.nodeSettings,
          [nodeId]: { ...state.nodeSettings[nodeId], ...settings }
        }
      }))
    } catch (error) {
      console.error('Failed to update node settings:', error)
    }
  },
  
  loadProjectVars: async () => {
    const { projectPath } = get()
    if (!projectPath) return
    
    try {
      const res = await axios.get(`${API_BASE}/vars/project`, {
        params: { path: projectPath }
      })
      set({ projectVars: res.data.variables })
    } catch (error) {
      console.error('Failed to load project vars:', error)
    }
  },
  
  createProjectVar: async (baseName) => {
    const { projectPath } = get()
    if (!projectPath) return null
    
    try {
      const res = await axios.post(`${API_BASE}/vars/project/create`, {
        path: projectPath,
        base_name: baseName,
        description: ''
      })
      await get().loadProjectVars()
      return res.data
    } catch (error) {
      console.error('Failed to create variable:', error)
      return null
    }
  },
  
  // Execution
  getExecutionStatus: async () => {
    try {
      const res = await axios.get(`${API_BASE}/run/status`)
      const { state, run_id, active_node_uid, active_node_title } = res.data
      
      set({
        executionState: state,
        activeNodeId: active_node_uid,
        activeNodeTitle: active_node_title,
        runId: run_id
      })
    } catch (error) {
      console.error('Failed to get execution status:', error)
    }
  },
  
  startFromBeginning: async () => {
    const { projectPath, projectName } = get()
    try {
      await axios.post(`${API_BASE}/run/start_from_beginning`, {
        path: projectPath,
        graph_name: projectName,
        from_beginning: true
      })
      await get().getExecutionStatus()
      await get().pollExecutionStatus()
    } catch (error) {
      console.error('Failed to start execution:', error)
    }
  },
  
  startFromSelected: async () => {
    const { projectPath, projectName, selectedNodeId } = get()
    if (!selectedNodeId) return
    
    try {
      await axios.post(`${API_BASE}/run/start_from_selected`, {
        path: projectPath,
        graph_name: projectName,
        node_uid: selectedNodeId,
        from_beginning: false
      })
      await get().getExecutionStatus()
      await get().pollExecutionStatus()
    } catch (error) {
      console.error('Failed to start execution:', error)
    }
  },
  
  softStop: async () => {
    try {
      await axios.post(`${API_BASE}/run/stop_soft`)
      await get().getExecutionStatus()
    } catch (error) {
      console.error('Failed to stop:', error)
    }
  },
  
  hardStop: async () => {
    try {
      await axios.post(`${API_BASE}/run/stop_hard`)
      await get().getExecutionStatus()
    } catch (error) {
      console.error('Failed to stop:', error)
    }
  },
  
  resume: async () => {
    try {
      await axios.post(`${API_BASE}/run/resume`)
      await get().getExecutionStatus()
      await get().pollExecutionStatus()
    } catch (error) {
      console.error('Failed to resume:', error)
    }
  },
  
  pollExecutionStatus: async () => {
    const { executionState } = get()
    
    if (executionState === 'Running' || executionState === 'Paused') {
      await get().getExecutionStatus()
      await get().loadLog()
      
      if (executionState === 'Running' || executionState === 'Paused') {
        setTimeout(() => get().pollExecutionStatus(), 500)
      }
    }
  },
  
  // Log
  loadLog: async () => {
    const { projectPath } = get()
    if (!projectPath) return
    
    try {
      const res = await axios.get(`${API_BASE}/log/tail`, {
        params: { path: projectPath, lines: 500 }
      })
      set({ logLines: res.data.lines })
    } catch (error) {
      console.error('Failed to load log:', error)
    }
  },
  
  setLogFilter: (filter) => set({ logFilter: filter }),
  
  // Categories
  toggleCategory: (category) => {
    set(state => ({
      categoriesExpanded: {
        ...state.categoriesExpanded,
        [category]: !state.categoriesExpanded[category]
      }
    }))
  },
  
  // Add node to graph
  addNode: (plugin) => {
    const { nodes } = get()
    
    const newNode = {
      id: `node_${Date.now()}`,
      type: 'custom',
      position: { x: 100 + nodes.length * 20, y: 100 + nodes.length * 20 },
      data: {
        plugin_id: plugin.plugin_id,
        node_title: plugin.name,
        params: {},
        breakpoint: false,
        error_to_fail: false,
        input_var_ref: null,
        output_var_ref: null,
        visual: {}
      }
    }
    
    set({ nodes: [...nodes, newNode] })
    get().saveGraph()
  }
}))
