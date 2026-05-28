<template>
  <div class="page-console">
    <div class="page-header">
      <h2>总控制台</h2>
      <div class="header-actions">
        <button class="btn btn-green" @click="handleStartAll" :disabled="allRunning || loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>&#9654; 一键启动</span>
        </button>
        <button class="btn btn-red" @click="handleStopAll" :disabled="noneRunning || loading">
          <span>&#9632; 一键停止</span>
        </button>
        <button class="btn btn-gray" @click="refreshJobs">&#8635; 刷新</button>
      </div>
    </div>

    <div class="jobs-section">
      <h3>数据采集</h3>
      <div class="jobs-grid">
        <div
          v-for="job in simulatorJobs"
          :key="job.id"
          class="job-card"
          :class="{ running: job.status === 'running', stopped: job.status === 'stopped', unimplemented: !job.implemented }"
        >
          <div class="job-icon">{{ getJobIcon(job.id) }}</div>
          <div class="job-info">
            <div class="job-name">{{ job.name }}</div>
            <div class="job-desc">{{ job.desc }}</div>
            <div class="job-pid" v-if="job.pid">PID: {{ job.pid }}</div>
          </div>
          <div class="job-actions">
            <div class="job-status" :class="job.status">
              <span class="status-dot"></span>
              {{ job.status === 'running' ? '运行中' : job.implemented ? '已停止' : '待开发' }}
            </div>
            <template v-if="job.implemented">
              <button v-if="job.status === 'stopped'" class="btn btn-sm btn-green" @click="handleStart(job.id)" :disabled="loading">&#9654; 启动</button>
              <button v-else class="btn btn-sm btn-red" @click="handleStop(job.id)" :disabled="loading">&#9632; 停止</button>
            </template>
            <button class="btn btn-sm btn-gray" @click="toggleLog(job.id)" :disabled="!job.implemented">
              {{ expandedLog === job.id ? '收起' : '日志' }}
            </button>
          </div>
          <div v-if="expandedLog === job.id" class="job-log">
            <div class="job-log-header">
              <span>{{ job.name }} - 实时日志</span>
              <button class="btn btn-sm btn-gray" @click="expandedLog = null">&#x2715;</button>
            </div>
            <div class="job-log-output" :ref="el => { if (el) jobLogRefs[job.id] = el }">
              <div v-if="!jobLogs[job.id]?.length" class="log-empty">暂无日志输出</div>
              <div v-for="(line, i) in jobLogs[job.id] || []" :key="i" class="log-line">{{ line }}</div>
            </div>
          </div>
        </div>
      </div>

      <h3>数据清洗</h3>
      <div class="jobs-grid">
        <div
          v-for="job in cleanerJobs"
          :key="job.id"
          class="job-card"
          :class="{ running: job.status === 'running', stopped: job.status === 'stopped', unimplemented: !job.implemented }"
        >
          <div class="job-icon">{{ getJobIcon(job.id) }}</div>
          <div class="job-info">
            <div class="job-name">{{ job.name }}</div>
            <div class="job-desc">{{ job.desc }}</div>
            <div class="job-pid" v-if="job.pid">PID: {{ job.pid }}</div>
          </div>
          <div class="job-actions">
            <div class="job-status" :class="job.status">
              <span class="status-dot"></span>
              {{ job.status === 'running' ? '运行中' : job.implemented ? '已停止' : '待开发' }}
            </div>
            <template v-if="job.implemented">
              <button v-if="job.status === 'stopped'" class="btn btn-sm btn-green" @click="handleStart(job.id)" :disabled="loading">&#9654; 启动</button>
              <button v-else class="btn btn-sm btn-red" @click="handleStop(job.id)" :disabled="loading">&#9632; 停止</button>
            </template>
            <button class="btn btn-sm btn-gray" @click="toggleLog(job.id)" :disabled="!job.implemented">
              {{ expandedLog === job.id ? '收起' : '日志' }}
            </button>
          </div>
          <div v-if="expandedLog === job.id" class="job-log">
            <div class="job-log-header">
              <span>{{ job.name }} - 实时日志</span>
              <button class="btn btn-sm btn-gray" @click="expandedLog = null">&#x2715;</button>
            </div>
            <div class="job-log-output" :ref="el => { if (el) jobLogRefs[job.id] = el }">
              <div v-if="!jobLogs[job.id]?.length" class="log-empty">暂无日志输出</div>
              <div v-for="(line, i) in jobLogs[job.id] || []" :key="i" class="log-line">{{ line }}</div>
            </div>
          </div>
        </div>
      </div>

      <h3>基础流数据分析</h3>
      <div class="jobs-grid">
        <div
          v-for="job in analyticsJobs"
          :key="job.id"
          class="job-card"
          :class="{ running: job.status === 'running', stopped: job.status === 'stopped', unimplemented: !job.implemented }"
        >
          <div class="job-icon">{{ getJobIcon(job.id) }}</div>
          <div class="job-info">
            <div class="job-name">{{ job.name }}</div>
            <div class="job-desc">{{ job.desc }}</div>
            <div class="job-pid" v-if="job.pid">PID: {{ job.pid }}</div>
          </div>
          <div class="job-actions">
            <div class="job-status" :class="job.status">
              <span class="status-dot"></span>
              {{ job.status === 'running' ? '运行中' : job.implemented ? '已停止' : '待开发' }}
            </div>
            <template v-if="job.implemented">
              <button v-if="job.status === 'stopped'" class="btn btn-sm btn-green" @click="handleStart(job.id)" :disabled="loading">&#9654; 启动</button>
              <button v-else class="btn btn-sm btn-red" @click="handleStop(job.id)" :disabled="loading">&#9632; 停止</button>
            </template>
            <button class="btn btn-sm btn-gray" @click="toggleLog(job.id)" :disabled="!job.implemented">
              {{ expandedLog === job.id ? '收起' : '日志' }}
            </button>
          </div>
          <div v-if="expandedLog === job.id" class="job-log">
            <div class="job-log-header">
              <span>{{ job.name }} - 实时日志</span>
              <button class="btn btn-sm btn-gray" @click="expandedLog = null">&#x2715;</button>
            </div>
            <div class="job-log-output" :ref="el => { if (el) jobLogRefs[job.id] = el }">
              <div v-if="!jobLogs[job.id]?.length" class="log-empty">暂无日志输出</div>
              <div v-for="(line, i) in jobLogs[job.id] || []" :key="i" class="log-line">{{ line }}</div>
            </div>
          </div>
        </div>
      </div>

      <h3>进阶流数据分析</h3>
      <div class="jobs-grid">
        <div
          v-for="job in advancedJobs"
          :key="job.id"
          class="job-card"
          :class="{ running: job.status === 'running', stopped: job.status === 'stopped', unimplemented: !job.implemented }"
        >
          <div class="job-icon">{{ getJobIcon(job.id) }}</div>
          <div class="job-info">
            <div class="job-name">{{ job.name }}</div>
            <div class="job-desc">{{ job.desc }}</div>
            <div class="job-pid" v-if="job.pid">PID: {{ job.pid }}</div>
          </div>
          <div class="job-actions">
            <div class="job-status" :class="job.status">
              <span class="status-dot"></span>
              {{ job.status === 'running' ? '运行中' : job.implemented ? '已停止' : '待开发' }}
            </div>
            <template v-if="job.implemented">
              <button v-if="job.status === 'stopped'" class="btn btn-sm btn-green" @click="handleStart(job.id)" :disabled="loading">&#9654; 启动</button>
              <button v-else class="btn btn-sm btn-red" @click="handleStop(job.id)" :disabled="loading">&#9632; 停止</button>
            </template>
            <button class="btn btn-sm btn-gray" @click="toggleLog(job.id)" :disabled="!job.implemented">
              {{ expandedLog === job.id ? '收起' : '日志' }}
            </button>
          </div>
          <div v-if="expandedLog === job.id" class="job-log">
            <div class="job-log-header">
              <span>{{ job.name }} - 实时日志</span>
              <button class="btn btn-sm btn-gray" @click="expandedLog = null">&#x2715;</button>
            </div>
            <div class="job-log-output" :ref="el => { if (el) jobLogRefs[job.id] = el }">
              <div v-if="!jobLogs[job.id]?.length" class="log-empty">暂无日志输出</div>
              <div v-for="(line, i) in jobLogs[job.id] || []" :key="i" class="log-line">{{ line }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 全局操作日志 -->
    <div class="log-section">
      <div class="log-header">
        <span>操作日志</span>
        <button class="btn btn-sm btn-gray" @click="clearLogs">清空</button>
      </div>
      <div class="log-output" ref="logRef">
        <div v-for="(log, i) in logs" :key="i" class="log-line" :class="log.type">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-msg">{{ log.msg }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive } from 'vue'
import { getJobs, startJob, stopJob, startAllJobs, stopAllJobs, getJobLog } from '../utils/api.js'

const jobs = ref([])
const logs = ref([])
const loading = ref(false)
const logRef = ref(null)
const expandedLog = ref(null)
const jobLogs = reactive({})
const jobLogRefs = reactive({})
const jobLogTimers = reactive({})
let pollTimer = null

const simulatorJobs = computed(() => jobs.value.filter(j => j.id === 'simulator'))
const cleanerJobs = computed(() => jobs.value.filter(j => j.id === 'cleaner'))
const analyticsJobs = computed(() => jobs.value.filter(j => j.id.startsWith('analytics')))
const advancedJobs = computed(() => jobs.value.filter(j => j.id.startsWith('advanced')))

const allRunning = computed(() => jobs.value.length > 0 && jobs.value.filter(j => j.implemented).every(j => j.status === 'running'))
const noneRunning = computed(() => jobs.value.filter(j => j.implemented).every(j => j.status === 'stopped'))

function addLog(msg, type = 'info') {
  const now = new Date()
  const time = now.toLocaleTimeString('zh-CN', { hour12: false })
  logs.value.push({ time, msg, type })
}

function getJobIcon(id) {
  const icons = {
    simulator: '\u26A1', cleaner: '\u2699',
    analytics_road_flow: '1', analytics_avg_speed: '2', analytics_congestion: '3',
    analytics_peak: '4', analytics_region_heat: '5',
    advanced_hotspot: '2', advanced_anomaly: '3', advanced_region_rank: '6',
    advanced_sliding: '1', advanced_accident: '4', advanced_predict: '5', advanced_sustained: '7',
  }
  return icons[id] || '\u25CF'
}

async function refreshJobs() {
  try { jobs.value = await getJobs() } catch (e) { addLog(`刷新失败: ${e.message}`, 'error') }
}

async function fetchJobLog(jobId) {
  try {
    const lines = await getJobLog(jobId)
    jobLogs[jobId] = lines
  } catch (e) { jobLogs[jobId] = [`加载失败: ${e.message}`] }
}

async function toggleLog(jobId) {
  if (expandedLog.value === jobId) { expandedLog.value = null; return }
  expandedLog.value = jobId
  if (!jobLogs[jobId]) await fetchJobLog(jobId)
  if (jobLogTimers[jobId]) clearInterval(jobLogTimers[jobId])
  jobLogTimers[jobId] = setInterval(() => fetchJobLog(jobId), 3000)
}

async function handleStart(id) {
  loading.value = true
  addLog(`启动 ${id}...`)
  try {
    const res = await startJob(id)
    if (res.code === 0) addLog(`\u2713 ${res.message}`, 'success')
    else addLog(`\u2717 ${res.message}`, 'error')
    await refreshJobs()
  } catch (e) { addLog(`\u2717 启动失败: ${e.message}`, 'error') }
  finally { loading.value = false }
}

async function handleStop(id) {
  loading.value = true
  addLog(`停止 ${id}...`)
  try {
    const res = await stopJob(id)
    if (res.code === 0) addLog(`\u2713 ${res.message}`, 'success')
    else addLog(`\u2717 ${res.message}`, 'error')
    await refreshJobs()
  } catch (e) { addLog(`\u2717 停止失败: ${e.message}`, 'error') }
  finally { loading.value = false }
}

async function handleStartAll() {
  loading.value = true
  addLog('一键启动所有作业...')
  try {
    const res = await startAllJobs()
    if (res.code === 0) {
      for (const r of res.data) {
        if (r.status === 'started') addLog(`\u2713 ${r.id} 已启动`, 'success')
        else if (r.status === 'already_running') addLog(`\u25cb ${r.id} 已在运行`, 'info')
        else if (r.status === 'not_implemented') addLog(`\u25cb ${r.id} 尚未实现`, 'info')
        else addLog(`\u2717 ${r.id} 失败: ${r.error}`, 'error')
      }
    }
    await refreshJobs()
  } catch (e) { addLog(`\u2717 一键启动失败: ${e.message}`, 'error') }
  finally { loading.value = false }
}

async function handleStopAll() {
  loading.value = true
  addLog('一键停止所有作业...')
  try {
    const res = await stopAllJobs()
    if (res.code === 0) {
      for (const r of res.data) {
        if (r.status === 'stopped') addLog(`\u2713 ${r.id} 已停止`, 'success')
        else addLog(`\u25cb ${r.id} ${r.status}`, 'info')
      }
    }
    await refreshJobs()
  } catch (e) { addLog(`\u2717 一键停止失败: ${e.message}`, 'error') }
  finally { loading.value = false }
}

function clearLogs() { logs.value = [] }

onMounted(async () => {
  await refreshJobs()
  addLog('总控制台已就绪', 'info')
  pollTimer = setInterval(refreshJobs, 5000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  Object.values(jobLogTimers).forEach(t => clearInterval(t))
})
</script>

<style scoped>
.page-console { max-width: 1100px; margin: 0 auto; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-header h2 { margin: 0; font-size: 22px; font-weight: 600; color: #e6edf3; }
.header-actions { display: flex; gap: 10px; }
.jobs-section h3 { font-size: 16px; font-weight: 600; color: #8b949e; margin: 24px 0 12px; }
.jobs-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.job-card {
  background: #161b22; border: 1px solid #30363d; border-radius: 12px;
  padding: 16px; display: flex; flex-wrap: wrap; gap: 12px; transition: border-color 0.2s; position: relative;
}
.job-card.running { border-color: #238636; }
.job-card.stopped { border-color: #30363d; }
.job-card.unimplemented { opacity: 0.6; }
.job-icon { font-size: 28px; line-height: 1; }
.job-info { flex: 1; min-width: 140px; }
.job-name { font-size: 15px; font-weight: 600; color: #e6edf3; margin-bottom: 4px; }
.job-desc { font-size: 12px; color: #8b949e; margin-bottom: 4px; line-height: 1.4; }
.job-pid { font-size: 11px; color: #6e7681; }
.job-actions { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
.job-status { display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 500; }
.job-status.running { color: #3fb950; }
.job-status.stopped { color: #8b949e; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }
.running .status-dot { animation: pulse-dot 1.5s infinite; }
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.4} }
.job-log { width: 100%; background: #0d1117; border: 1px solid #21262d; border-radius: 8px; overflow: hidden; }
.job-log-header { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #161b22; border-bottom: 1px solid #21262d; font-size: 12px; font-weight: 600; color: #8b949e; }
.job-log-output { height: 160px; overflow-y: auto; padding: 4px 0; font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 11px; }
.job-log-output .log-line { padding: 1px 12px; color: #c9d1d9; white-space: pre-wrap; word-break: break-all; }
.job-log-output .log-empty { padding: 12px; color: #484f58; text-align: center; font-size: 13px; }
.log-section { background: #0d1117; border: 1px solid #30363d; border-radius: 12px; overflow: hidden; margin-top: 24px; }
.log-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #161b22; border-bottom: 1px solid #30363d; font-size: 14px; font-weight: 600; color: #c9d1d9; }
.log-output { height: 180px; overflow-y: auto; padding: 6px 0; font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 12px; }
.log-line { display: flex; gap: 12px; padding: 2px 16px; }
.log-line:hover { background: #161b22; }
.log-time { color: #6e7681; flex-shrink: 0; }
.log-line.success .log-msg { color: #3fb950; }
.log-line.error .log-msg { color: #f85149; }
.log-line.info .log-msg { color: #8b949e; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 18px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.15s; font-family: inherit; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-green { background: #238636; color: #fff; }
.btn-green:hover:not(:disabled) { background: #2ea043; }
.btn-red { background: #da3633; color: #fff; }
.btn-red:hover:not(:disabled) { background: #f85149; }
.btn-gray { background: #21262d; color: #c9d1d9; }
.btn-gray:hover:not(:disabled) { background: #30363d; }
.btn-sm { padding: 4px 10px; font-size: 12px; }
.spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
