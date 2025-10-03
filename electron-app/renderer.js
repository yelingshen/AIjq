const detectBtn = document.getElementById('detect')
const results = document.getElementById('results')

const depsSection = document.createElement('div')
const depsBtn = document.createElement('button')
depsBtn.textContent = '检查依赖'
depsSection.appendChild(depsBtn)
document.body.insertBefore(depsSection, results)

depsBtn.addEventListener('click', async () => {
  depsBtn.disabled = true
  depsBtn.textContent = '检查中...'
  const deps = await window.electronAPI.validateDeps()
  let ul = document.getElementById('deps-list')
  if (!ul) { ul = document.createElement('ul'); ul.id = 'deps-list'; depsSection.appendChild(ul) }
  ul.innerHTML = ''
  deps.forEach(d => {
    const li = document.createElement('li')
    li.textContent = `${d.name} — ${d.installed ? '已安装' : '未安装'}`
    if (!d.installed) {
      const btn = document.createElement('button')
      btn.textContent = '安装说明'
      btn.addEventListener('click', async () => {
        const inst = await window.electronAPI.getInstallInstructions(d.name)
        alert(inst.text + '\nWindows: ' + inst.windows + '\nLinux: ' + inst.linux)
      })
      li.appendChild(btn)

      const copyBtn = document.createElement('button')
      copyBtn.textContent = '复制安装命令'
      copyBtn.addEventListener('click', async () => {
        const cmd = await window.electronAPI.getInstallCommand(d.name, navigator.platform.startsWith('Win'))
        await navigator.clipboard.writeText(cmd)
        alert('已复制安装命令: ' + cmd)
      })
      li.appendChild(copyBtn)
    }
    ul.appendChild(li)
  })
  depsBtn.disabled = false
  depsBtn.textContent = '检查依赖'
})

detectBtn.addEventListener('click', async () => {
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
})
