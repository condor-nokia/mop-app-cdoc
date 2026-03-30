
const { spawn } = require('child_process')

async function runCommand(cmdv, argv = [], opts = {}) {
  if (!cmdv) throw new TypeError('Command not specified')
  return new Promise((resolve, reject) => {
    const stdout = []
    const stderr = []
    const ps = spawn(cmdv, [...argv], opts)
    ps.on('close', (code) => {
      if (code === 0) {
        if (stderr.length) process.stderr.write(stderr.join(''))
        resolve(ps)
      } else {
        let msg = `Command failed: ${ps.spawnargs.join(' ')}`
        if (stderr.length) msg += '\n' + stderr.join('')
        reject(new Error(msg))
      }
    })
    ps.on('error', (err) => reject(err))
    ps.stdout.on('data', (data) => stdout.push(data))
    ps.stderr.on('data', (data) => stderr.push(data))

  })
}

module.exports = runCommand
