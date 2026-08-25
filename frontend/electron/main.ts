import { app, BrowserWindow, dialog, shell } from 'electron'
import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process'
import { createWriteStream, existsSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const currentDirectory = path.dirname(fileURLToPath(import.meta.url))
const isDevelopment = !app.isPackaged
const backendPort = isDevelopment ? 8000 : 8765
const backendOrigin = `http://127.0.0.1:${backendPort}`
let mainWindow: BrowserWindow | null = null
let backendProcess: ChildProcessWithoutNullStreams | null = null
let ownsBackend = false

async function backendIsReady() {
  try {
    const response = await fetch(`${backendOrigin}/health`, { signal: AbortSignal.timeout(800) })
    return response.ok
  } catch {
    return false
  }
}

async function waitForBackend() {
  for (let attempt = 0; attempt < 120; attempt += 1) {
    if (await backendIsReady()) return
    await new Promise(resolve => setTimeout(resolve, 250))
  }
  throw new Error(`El backend no respondió en ${backendOrigin}`)
}

function startBackend() {
  if (isDevelopment) {
    const projectRoot = path.resolve(currentDirectory, '../..')
    const backendDirectory = path.join(projectRoot, 'backend')
    const virtualEnvironmentPython = process.platform === 'win32'
      ? path.join(projectRoot, 'venv', 'Scripts', 'python.exe')
      : path.join(projectRoot, 'venv', 'bin', 'python')
    const python = existsSync(virtualEnvironmentPython) ? virtualEnvironmentPython : 'python'
    backendProcess = spawn(python, ['desktop_server.py'], {
      cwd: backendDirectory,
      env: {
        ...process.env,
        SCHEDULER_PORT: String(backendPort),
        SCHEDULER_DB_PATH: path.join(backendDirectory, 'scheduler.db'),
        SCHEDULER_LOG_LEVEL: 'info',
      },
      windowsHide: true,
    })
  } else {
    const executableName = process.platform === 'win32' ? 'organizador-backend.exe' : 'organizador-backend'
    const executable = path.join(process.resourcesPath, 'backend', executableName)
    if (!existsSync(executable)) throw new Error(`No se encontró el backend empaquetado: ${executable}`)
    backendProcess = spawn(executable, [], {
      cwd: path.dirname(executable),
      env: {
        ...process.env,
        SCHEDULER_PORT: String(backendPort),
        SCHEDULER_DB_PATH: path.join(app.getPath('userData'), 'scheduler.db'),
        SCHEDULER_LOG_LEVEL: 'warning',
      },
      windowsHide: true,
    })
  }

  ownsBackend = true
  const log = createWriteStream(path.join(app.getPath('userData'), 'backend.log'), { flags: 'a' })
  backendProcess.stdout.pipe(log)
  backendProcess.stderr.pipe(log)
  backendProcess.once('error', error => log.write(`\nNo se pudo iniciar el backend: ${error.message}\n`))
  backendProcess.once('exit', code => {
    log.write(`\nBackend finalizado con código ${code ?? 'desconocido'}\n`)
    backendProcess = null
  })
}

function stopBackend() {
  if (ownsBackend && backendProcess && !backendProcess.killed) backendProcess.kill()
  backendProcess = null
  ownsBackend = false
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 900,
    minHeight: 650,
    show: false,
    backgroundColor: '#f5f8fc',
    autoHideMenuBar: true,
    title: 'Organizador de horarios',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  })

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('https://')) void shell.openExternal(url)
    return { action: 'deny' }
  })
  mainWindow.webContents.on('will-navigate', (event, url) => {
    const allowed = isDevelopment ? url.startsWith('http://127.0.0.1:5173') || url.startsWith('http://localhost:5173') : url.startsWith('file:')
    if (!allowed) event.preventDefault()
  })

  if (isDevelopment) {
    await mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL ?? 'http://127.0.0.1:5173')
  } else {
    await mainWindow.loadFile(path.join(currentDirectory, '../dist/index.html'))
  }
  mainWindow.once('ready-to-show', () => mainWindow?.show())
  mainWindow.on('closed', () => { mainWindow = null })
}

const hasSingleInstanceLock = app.requestSingleInstanceLock()
if (!hasSingleInstanceLock) app.quit()

app.on('second-instance', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore()
    mainWindow.focus()
  }
})

app.whenReady().then(async () => {
  try {
    if (!(await backendIsReady())) startBackend()
    await waitForBackend()
    await createWindow()
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    dialog.showErrorBox('No se pudo iniciar Organizador de horarios', `${message}\n\nConsulta backend.log en la carpeta de datos de la aplicación.`)
    stopBackend()
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) void createWindow()
})
app.on('before-quit', stopBackend)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
