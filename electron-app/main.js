const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')
const detector = require('./detector')
const installer = require('./installer')

function createWindow () {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })

  win.loadFile(path.join(__dirname, 'index.html'))
}

app.whenReady().then(() => {
  createWindow()
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

ipcMain.handle('detect-environments', async () => {
  const envs = await detector.detect()
  return envs
})

ipcMain.handle('validate-deps', async () => {
  return await installer.validateDeps()
})

ipcMain.handle('get-install-instructions', async (event, depName) => {
  return installer.getInstructions(depName)
})

ipcMain.handle('get-install-command', async (event, depName, platform) => {
  return installer.getInstallCommand(depName, platform)
})

ipcMain.handle('select-directory', async () => {
  const res = await dialog.showOpenDialog({ properties: ['openDirectory'] })
  if (res.canceled) return null
  return res.filePaths[0]
})

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})
