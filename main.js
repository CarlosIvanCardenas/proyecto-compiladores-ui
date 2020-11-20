const { app, BrowserWindow } = require('electron')
const { ipcMain } = require('electron')
const spawn = require('child_process').spawn
const path = require('path')

function createWindow () {
  const win = new BrowserWindow({
    width: 1280,
    height: 720,
    webPreferences: {
      nodeIntegration: true
    }
  })

  win.loadFile('index.html')
  //win.webContents.openDevTools()
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

ipcMain.on('asynchronous-message', (event, arg) => {
  console.log(arg)
  let python = spawn('python', [path.join(app.getAppPath(), '..', 'core/test.py'), arg])
  python.stdout.on('data', function(data) {
    event.reply('asynchronous-reply', data.toString())
  })
})
