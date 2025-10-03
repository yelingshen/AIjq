const fs = require('fs')
const path = require('path')
const { exec } = require('child_process')
const http = require('http')
const https = require('https')

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
    // try common version flags
    exec(cmd + ' --version', (err, stdout) => {
      if (!err && stdout) return resolve(stdout.toString().trim())
      exec(cmd + ' version', (err2, stdout2) => {
        if (!err2 && stdout2) return resolve(stdout2.toString().trim())
        exec(cmd + ' -v', (err3, stdout3) => {
          if (!err3 && stdout3) return resolve(stdout3.toString().trim())
          return resolve(null)
        })
      })
    })
  })
}

function probeHttp(port, pathTry = ['/health', '/v1/models', '/api/status', '/']) {
  return new Promise((resolve) => {
    const host = '127.0.0.1'
    let tried = 0
    const tryNext = () => {
      if (tried >= pathTry.length) return resolve(false)
      const p = pathTry[tried++]
      const options = { hostname: host, port, path: p, timeout: 2000 }
      const req = http.get(options, (res) => {
        res.resume()
        resolve(true)
      })
      req.on('error', () => tryNext())
      req.on('timeout', () => { req.destroy(); tryNext() })
    }
    tryNext()
  })
}

function probeHttps(url, pathTry = ['/health', '/v1/models', '/api/status', '/']) {
  return new Promise((resolve) => {
    let tried = 0
    const tryNext = () => {
      if (tried >= pathTry.length) return resolve(false)
      const p = pathTry[tried++]
      const full = new URL(p, url)
      const req = https.get(full, { timeout: 2000 }, (res) => { res.resume(); resolve(true) })
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

  // 1b) check Windows common install locations if on Windows
  if (process.platform === 'win32') {
    const winCandidates = [
      process.env['ProgramFiles'] ? path.join(process.env['ProgramFiles'], 'Ollama', 'ollama.exe') : null,
      process.env['ProgramFiles(x86)'] ? path.join(process.env['ProgramFiles(x86)'], 'Ollama', 'ollama.exe') : null
    ].filter(Boolean)
    for (const p of winCandidates) {
      try { if (fs.existsSync(p)) results.push({ name: 'ollama', path: p, type: 'executable', version: null, reachable: true }) } catch (e) {}
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

  // try https localhost (some services may expose https)
  const httpsOk = await probeHttps('https://127.0.0.1:11443')
  if (httpsOk) results.push({ name: 'https-service:11443', path: 'https://127.0.0.1:11443', type: 'https', version: null, reachable: true })

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
