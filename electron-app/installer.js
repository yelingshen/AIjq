const { exec } = require('child_process')

function which(cmd) {
  return new Promise((resolve) => {
    exec(process.platform === 'win32' ? `where ${cmd}` : `which ${cmd}`, (err, stdout) => {
      if (err) return resolve(null)
      const p = stdout.split(/\r?\n/)[0]
      resolve(p || null)
    })
  })
}

async function validateDeps() {
  const deps = ['ollama', 'python3', 'node', 'docker']
  const res = []
  for (const d of deps) {
    const p = await which(d)
    res.push({ name: d, installed: !!p, path: p })
  }
  return res
}

function getInstructions(depName) {
  const lower = (depName || '').toLowerCase()
  if (lower === 'ollama') {
    return {
      text: 'Ollama 是一个本地模型管理工具。请访问 https://ollama.com 下载并安装。',
      windows: 'https://ollama.com/download',
      linux: 'curl https://ollama.com/install.sh | sh'
    }
  }
  if (lower === 'python3' || lower === 'python') {
    return {
      text: '安装 Python 3（推荐 3.10+）。',
      windows: 'https://www.python.org/downloads/windows/',
      linux: 'sudo apt install -y python3'
    }
  }
  if (lower === 'node') {
    return {
      text: '安装 Node.js（LTS）。',
      windows: 'https://nodejs.org/en/download/',
      linux: 'curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs'
    }
  }
  if (lower === 'docker') {
    return {
      text: '安装 Docker 并确保已登录并启动。',
      windows: 'https://docs.docker.com/desktop/',
      linux: 'https://docs.docker.com/engine/install/ubuntu/'
    }
  }
  return { text: '未找到安装说明', windows: '', linux: '' }
}

function getInstallCommand(depName, platform) {
  const lower = (depName || '').toLowerCase()
  const plat = (platform || process.platform)
  if (lower === 'python3' || lower === 'python') {
    if (plat === 'win32') return 'Visit https://www.python.org/downloads/windows/ and install Python 3'
    return 'sudo apt install -y python3'
  }
  if (lower === 'node') {
    if (plat === 'win32') return 'Visit https://nodejs.org and download the Windows installer (LTS)'
    return 'curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs'
  }
  if (lower === 'ollama') {
    if (plat === 'win32') return 'Visit https://ollama.com/download for Windows installer'
    return 'curl https://ollama.com/install.sh | sh'
  }
  if (lower === 'docker') {
    if (plat === 'win32') return 'Visit https://docs.docker.com/desktop/ to install Docker Desktop'
    return 'Follow instructions: https://docs.docker.com/engine/install/ubuntu/'
  }
  return ''
}

module.exports = { validateDeps, getInstructions }
