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

ipcMain.on('execute', (event, arg) => {
  let python = spawn('python', [path.join(app.getAppPath(), 'core/main.py'), arg])
  python.stdout.on('data', function(data) {
    console.log(data.toString())
    if (data.toString().indexOf("READ")) {
      event.reply('input', data.toString())
      ipcMain.on('input-value', (event, arg) => {
        python.stdin.write(arg.toString())
        python.stdin.end()
      })
    } else {
      event.reply('output', data.toString())
    }
  })
  python.stdin.setEncoding('utf-8');
  python.stderr.on('data', function(err) {
    console.log(err.toString())
    let errorIndex = err.toString().indexOf("Exception:")
    if (errorIndex !== -1) {
      event.reply('output', err.toString().slice(errorIndex))
    } else {
      errorIndex = err.toString().indexOf("TypeError:")
      if (errorIndex !== -1) {
        event.reply('output', err.toString().slice(errorIndex))
      }
    }
  })
  python.on('close', function (code) {
    console.log('child process exited with code ' + code)
  })
})
