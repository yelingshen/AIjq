const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  detectEnvironments: () => ipcRenderer.invoke('detect-environments'),
  selectDirectory: () => ipcRenderer.invoke('select-directory')
})
