const fs = require('fs')
const path = require('path')
const { exec } = require('child_process')
const http = require('http')

function which(cmd) {
  return new Promise((resolve) => {
    exec(process.platform === 'win32' ? `where ${cmd}` : `which ${cmd}`, (err, stdout) => {
      if (err) return resolve(null)
      const p = stdout.split(/\r?\n/)[0]
      resolve(p || null)
    })
  })
}

function execVersion(cmd) {
  return new Promise((resolve) => {
    exec(cmd + ' --version', (err, stdout) => {
      if (err) return resolve(null)
      resolve(stdout.toString().trim())
    })
  })
}

function probeHttp(port, pathTry = ['/health', '/v1/models', '/']) {
  return new Promise((resolve) => {
    const host = '127.0.0.1'
    let tried = 0
    const tryNext = () => {
      if (tried >= pathTry.length) return resolve(false)
      const p = pathTry[tried++]
      const req = http.get({ hostname: host, port, path: p, timeout: 2000 }, (res) => {
        res.resume()
        resolve(true)
      })
      req.on('error', () => tryNext())
      req.on('timeout', () => { req.destroy(); tryNext() })
    }
    tryNext()
  })
}

async function detect() {
  const results = []

  // 1) check common executables in PATH
  const executables = ['ollama', 'python3', 'python', 'docker', 'podman', 'vllm']
  for (const exe of executables) {
    const p = await which(exe)
    if (p) {
      const ver = await execVersion(exe)
      results.push({ name: exe, path: p, type: 'executable', version: ver || null, reachable: true })
    }
  }

  // 2) probe common AI service ports on localhost
  const ports = [11434, 5000, 8000, 8080, 7860]
  for (const port of ports) {
    const ok = await probeHttp(port)
    if (ok) {
      results.push({ name: `http-service:${port}`, path: `http://127.0.0.1:${port}`, type: 'http', version: null, reachable: true })
    }
  }

  // 3) detect running docker containers for common images
  try {
    const dockerPath = await which('docker')
    if (dockerPath) {
      const containers = await new Promise((resolve) => {
        exec('docker ps --format "{{.Image}}::{{.Names}}::{{.Status}}"', (err, stdout) => {
          if (err) return resolve([])
          const lines = stdout.split(/\r?\n/).filter(Boolean)
          resolve(lines.map(l => {
            const parts = l.split('::')
            return { image: parts[0], name: parts[1], status: parts[2] }
          }))
        })
      })
      for (const c of containers) {
        // heuristics: common AI image names
        if (/ollama|vllm|llama|transformer|text-generation|gpt-/.test(c.image)) {
          results.push({ name: `docker:${c.name}`, path: c.image, type: 'docker', version: null, reachable: true, extra: c.status })
        }
      }
    }
  } catch (e) {
    // ignore docker errors
  }

  return results
}

module.exports = { detect }
