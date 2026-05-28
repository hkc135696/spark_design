<template>
  <div class="page-collection">
    <div class="page-header">
      <h2>实时数据采集</h2>
      <div class="header-actions">
        <button
          v-if="jobStatus === 'running'"
          class="btn btn-red"
          @click="handleStop"
          :disabled="loading"
        >
          <span v-if="loading" class="spinner"></span>
          <span v-else>&#9632; 停止</span>
        </button>
        <button
          v-else
          class="btn btn-green"
          @click="handleStart"
          :disabled="loading"
        >
          <span v-if="loading" class="spinner"></span>
          <span v-else>&#9654; 启动</span>
        </button>
        <button class="btn btn-gray" @click="refresh">&#8635; 刷新</button>
      </div>
    </div>

    <div class="job-status-bar">
      <span class="status-dot" :class="jobStatus"></span>
      <span class="status-text">
        {{ jobStatus === 'running' ? `运行中 (PID: ${jobPid || '-'})` : '已停止' }}
      </span>
    </div>

    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-label">Kafka Topic</div>
        <div class="stat-value">{{ status.kafka_topic || '-' }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">消息速率</div>
        <div class="stat-value">{{ status.message_rate || 0 }} <span class="unit">条/秒</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-label">累计消息数</div>
        <div class="stat-value">{{ status.message_count || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">活跃检测器</div>
        <div class="stat-value">{{ status.detectors_active || 0 }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getCollectionStatus } from '../utils/api.js'
import { getJobs, startJob, stopJob } from '../utils/api.js'

const status = ref({})
const loading = ref(false)
const jobStatus = ref('stopped')
const jobPid = ref(null)
let pollTimer = null

async function fetchJobStatus() {
  try {
    const jobs = await getJobs()
    const simulator = jobs.find(j => j.id === 'simulator')
    if (simulator) {
      jobStatus.value = simulator.status
      jobPid.value = simulator.pid || null
    }
  } catch (e) { console.error(e) }
}

async function refresh() {
  loading.value = true
  try {
    status.value = await getCollectionStatus()
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function handleStart() {
  loading.value = true
  try {
    await startJob('simulator')
    await fetchJobStatus()
  } catch (e) { console.error('启动失败:', e) }
  finally { loading.value = false }
}

async function handleStop() {
  loading.value = true
  try {
    await stopJob('simulator')
    await fetchJobStatus()
  } catch (e) { console.error('停止失败:', e) }
  finally { loading.value = false }
}

onMounted(async () => {
  await fetchJobStatus()
  await refresh()
  pollTimer = setInterval(async () => {
    await fetchJobStatus()
    await refresh()
  }, 5000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.page-collection { max-width: 1000px; margin: 0 auto; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.page-header h2 { margin: 0; font-size: 22px; font-weight: 600; color: #e6edf3; }
.header-actions { display: flex; gap: 8px; }
.job-status-bar {
  display: flex; align-items: center; gap: 8px;
  background: #161b22; border: 1px solid #30363d;
  border-radius: 8px; padding: 10px 16px; margin-bottom: 20px;
}
.status-dot { width: 10px; height: 10px; border-radius: 50%; background: #8b949e; }
.status-dot.running { background: #3fb950; animation: pulse 1.5s infinite; }
.status-dot.stopped { background: #8b949e; }
.status-text { font-size: 13px; color: #c9d1d9; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.stats-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.stat-card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; text-align: center; }
.stat-label { font-size: 13px; color: #8b949e; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: #e6edf3; }
.stat-value .unit { font-size: 14px; font-weight: 400; color: #8b949e; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 18px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.15s; font-family: inherit; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-green { background: #238636; color: #fff; }
.btn-green:hover:not(:disabled) { background: #2ea043; }
.btn-red { background: #da3633; color: #fff; }
.btn-red:hover:not(:disabled) { background: #f85149; }
.btn-gray { background: #21262d; color: #c9d1d9; }
.btn-gray:hover { background: #30363d; }
.spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
