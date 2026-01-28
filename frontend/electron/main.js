const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const fs = require('fs')
const http = require('http')

// __filename and __dirname are available in CommonJS

let mainWindow = null
let backendProcess = null

const BACKEND_PORT = 8000

async function waitForBackend(maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      await new Promise((resolve, reject) => {
        const req = http.get(`http://127.0.0.1:${BACKEND_PORT}/health`, (res) => {
          if (res.statusCode === 200) {
            resolve()
          } else {
            reject()
          }
        })
        req.on('error', reject)
        req.setTimeout(1000, () => {
          req.destroy()
          reject()
        })
      })
      return true
    } catch (e) {
      await new Promise(r => setTimeout(r, 500))
    }
  }
  return false
}

function startBackend() {
  const backendPath = path.join(__dirname, '..', 'backend')
  const mainPy = path.join(backendPath, 'main.py')
  
  // Check if Python file exists
  if (!fs.existsSync(mainPy)) {
    console.error('Backend not found:', mainPy)
    return
  }
  
  backendProcess = spawn('python', [mainPy], {
    cwd: backendPath,
    stdio: ['pipe', 'pipe', 'pipe']
  })
  
  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`)
  })
  
  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`)
  })
  
  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`)
  })
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    backgroundColor: '#1a1a2e'
  })
  
  // Check if production build exists
  const prodPath = path.join(__dirname, '..', 'dist', 'index.html')
  const useProd = fs.existsSync(prodPath)
  
  let startUrl
  if (useProd) {
    // Use production build (file protocol)
    startUrl = `file://${prodPath}`
    console.log('Using production build')
  } else {
    // Use Vite dev server
    startUrl = 'http://localhost:5173'
    console.log('Using dev server')
  }
  
  mainWindow.loadURL(startUrl)
  
  // Open DevTools in development
  mainWindow.webContents.openDevTools()
  
  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(async () => {
  // Start backend
  startBackend()
  
  // Wait for backend to be ready
  console.log('Waiting for backend...')
  const ready = await waitForBackend()
  
  if (ready) {
    console.log('Backend is ready!')
    createWindow()
  } else {
    console.error('Backend failed to start!')
    app.quit()
  }
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill()
  }
})

// IPC handlers for dialogs
ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory', 'createDirectory']
  })
  
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0]
  }
  return null
})

ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory', 'createDirectory']
  })
  
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0]
  }
  return null
})
