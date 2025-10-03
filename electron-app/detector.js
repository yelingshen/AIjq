const fs = require('fs')
const path = require('path')

async function detect() {
  // simple heuristics: look for common local deployment directories
  const candidates = [
    '/usr/local/bin/ollama',
    '/usr/bin/ollama',
    path.join(process.env.HOME || '', '.local', 'bin', 'ollama'),
    path.join(process.env.HOME || '', 'ollama')
  ]
  const found = []
  for (const p of candidates) {
    try {
      if (fs.existsSync(p)) {
        found.push({ name: 'ollama', path: p })
      }
    } catch (e) {
      // ignore
    }
  }
  return found
}

module.exports = { detect }
