// Wizard navigation helpers
function showStep(n) {
  document.querySelectorAll('.step').forEach(el => el.style.display = el.dataset.step === String(n) ? '' : 'none')
}

document.getElementById('to-step-2').addEventListener('click', () => showStep(2))
document.getElementById('back-step-1').addEventListener('click', () => showStep(1))
document.getElementById('to-step-3').addEventListener('click', () => showStep(3))
document.getElementById('back-step-2').addEventListener('click', () => showStep(2))
document.getElementById('to-step-4').addEventListener('click', () => showStep(4))
document.getElementById('back-step-3').addEventListener('click', () => showStep(3))

const detectBtn = document.getElementById('detect')
const results = document.getElementById('results')

async function runDetect() {
  detectBtn.disabled = true
  detectBtn.textContent = '检测中...'
  const envs = await window.electronAPI.detectEnvironments()
  results.innerHTML = ''
  if (!envs || envs.length === 0) {
    const li = document.createElement('li')
    li.textContent = '未检测到已知部署。'
    results.appendChild(li)
  } else {
    envs.forEach(e => {
      const li = document.createElement('li')
      li.textContent = `${e.name} — ${e.path}`
      results.appendChild(li)
    })
  }
  detectBtn.disabled = false
  detectBtn.textContent = '检测本地 AI 环境'
}

detectBtn.addEventListener('click', runDetect)

// Dependencies area
const depsArea = document.getElementById('deps-area')
async function runDepsCheck() {
  depsArea.innerHTML = '<p>正在检查依赖...</p>'
  const deps = await window.electronAPI.validateDeps()
  const ul = document.createElement('ul')
  deps.forEach(d => {
    const li = document.createElement('li')
    li.textContent = `${d.name} — ${d.installed ? '已安装' : '未安装'}`
    if (!d.installed) {
      const instBtn = document.createElement('button')
      instBtn.textContent = '安装说明'
      instBtn.addEventListener('click', async () => {
        const inst = await window.electronAPI.getInstallInstructions(d.name)
        alert(inst.text + '\nWindows: ' + inst.windows + '\nLinux: ' + inst.linux)
      })
      li.appendChild(instBtn)

      const copyBtn = document.createElement('button')
      copyBtn.textContent = '复制安装命令'
      copyBtn.addEventListener('click', async () => {
        const cmd = await window.electronAPI.getInstallCommand(d.name, navigator.platform.startsWith('Win') ? 'win32' : 'linux')
        await navigator.clipboard.writeText(cmd)
        alert('已复制安装命令: ' + cmd)
      })
      li.appendChild(copyBtn)
    }
    ul.appendChild(li)
  })
  depsArea.innerHTML = ''
  depsArea.appendChild(ul)
}

document.getElementById('to-step-3').addEventListener('click', runDepsCheck)

// Install step area
const installArea = document.getElementById('install-area')
async function prepareInstallStep() {
  installArea.innerHTML = '<p>请在上一页选择要安装的依赖，然后在此复制命令并按平台执行。</p>'
}

document.getElementById('to-step-4').addEventListener('click', prepareInstallStep)
