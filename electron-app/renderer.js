const detectBtn = document.getElementById('detect')
const results = document.getElementById('results')

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
