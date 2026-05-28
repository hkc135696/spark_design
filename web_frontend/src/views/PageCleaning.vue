<template>
  <div class="page-cleaning">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>数据清洗与预处理</h2>
      <button class="btn btn-gray" @click="refresh">&#8635; 刷新</button>
    </div>

    <!-- 作业状态 -->
    <div class="status-bar" :class="status.job_running ? 'running' : 'stopped'">
      <span class="dot" :class="status.job_running ? 'live' : 'dead'"></span>
      <span>{{ status.job_running ? '清洗作业运行中' : '清洗作业已停止' }}</span>
    </div>

    <!-- 数据流向图 -->
    <div class="flow-section">
      <div class="flow-stage stage-input">
        <div class="stage-icon">&#8593;</div>
        <div class="stage-label">流入原始数据</div>
        <div class="stage-value">{{ fmt(status.total_input) }}</div>
        <div class="stage-unit">条</div>
      </div>

      <div class="flow-arrow">&#10145;</div>

      <div class="flow-stage stage-clean">
        <div class="stage-icon">&#10003;</div>
        <div class="stage-label">清洗后入库</div>
        <div class="stage-value highlight">{{ fmt(status.total_clean) }}</div>
        <div class="stage-unit">条</div>
      </div>
    </div>

    <!-- 本批次最近处理量 -->
    <div class="batch-hint" v-if="status.batch_clean > 0">
      本批次清洗 <strong>{{ fmt(status.batch_clean) }}</strong> 条数据
    </div>

    <!-- 清洗规则说明 -->
    <div class="rule-section">
      <h3>清洗逻辑说明</h3>
      <div class="rules">
        <div class="rule-item">
          <span class="rule-tag tag-filter">过滤</span>
          <span class="rule-text">丢弃 <code>detector_id</code> 或 <code>timestamp</code> 为空的脏数据</span>
        </div>
        <div class="rule-item">
          <span class="rule-tag tag-dedup">去重</span>
          <span class="rule-text">基于 <code>detector_id + timestamp</code> 组合键去除重复记录</span>
        </div>
        <div class="rule-item">
          <span class="rule-tag tag-fix">修正</span>
          <span class="rule-text">
            数值字段越界修正：车辆数 &ge; 0，速度 0-200 km/h，占有率 0-100%，拥堵指数 [0, 1]
          </span>
        </div>
      </div>
    </div>

    <!-- 异常数据日志 -->
    <div class="error-section">
      <h3>异常数据记录</h3>
      <div class="error-empty" v-if="errors.length === 0">
        暂无异常数据记录
      </div>
      <div class="error-table" v-else>
        <div class="error-table-head">
          <span>批次</span>
          <span>原因</span>
          <span>数量</span>
          <span>示例</span>
        </div>
        <div class="error-table-row" v-for="(e, i) in errors" :key="i">
          <span>Batch {{ e.batch_id }}</span>
          <span>{{ e.reason }}</span>
          <span>{{ e.count }} 条</span>
          <span class="examples">{{ fmtExamples(e.examples) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getCleaningStatus, getCleaningErrors } from '../utils/api.js'

const status = ref({
  job_running: false,
  total_input: 0,
  total_clean: 0,
  total_dedup: 0,
  batch_clean: 0,
})

const errors = ref([])
let timer = null

function fmt(val) {
  const n = Number(val) || 0
  return n > 0 ? n.toLocaleString() : '0'
}

function fmtExamples(examples) {
  if (!examples || examples.length === 0) return '-'
  return examples.map(e => e.detector_id || '(空)').join(', ')
}

async function refresh() {
  try {
    const [s, errs] = await Promise.all([
      getCleaningStatus(),
      getCleaningErrors(),
    ])
    status.value = s
    errors.value = errs || []
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  refresh()
  timer = setInterval(refresh, 5000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.page-cleaning { max-width: 900px; margin: 0 auto; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-header h2 { margin: 0; font-size: 22px; font-weight: 600; }

/* 状态条 */
.status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 8px;
  padding: 10px 16px;
  margin-bottom: 24px;
  font-size: 14px;
  font-weight: 500;
}
.status-bar.running {
  background: rgba(35, 134, 54, 0.12);
  border: 1px solid #238636;
  color: #3fb950;
}
.status-bar.stopped {
  background: rgba(248, 81, 73, 0.1);
  border: 1px solid #f85149;
  color: #f85149;
}
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.live { background: #3fb950; animation: pulse 1.5s ease-in-out infinite; }
.dot.dead { background: #f85149; }
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.75); }
}

/* 数据流向 */
.flow-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 14px;
  padding: 28px 32px;
  margin-bottom: 20px;
}
.flow-arrow {
  font-size: 28px;
  color: #484f58;
}
.flow-stage {
  flex: 1;
  text-align: center;
  max-width: 200px;
}
.stage-icon {
  font-size: 32px;
  margin-bottom: 6px;
  color: #8b949e;
}
.stage-label { font-size: 13px; color: #8b949e; margin-bottom: 6px; }
.stage-value { font-size: 28px; font-weight: 800; color: #e6edf3; line-height: 1; }
.stage-value.highlight { color: #3fb950; }
.stage-unit { font-size: 12px; color: #484f58; margin-top: 2px; }

/* 批次提示 */
.batch-hint {
  text-align: center;
  font-size: 13px;
  color: #8b949e;
  margin-bottom: 28px;
}
.batch-hint strong { color: #f0883e; }

/* 规则说明 */
.rule-section {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
}
.rule-section h3 {
  margin: 0 0 16px;
  font-size: 15px;
  font-weight: 600;
  color: #e6edf3;
}
.rules { display: flex; flex-direction: column; gap: 12px; }
.rule-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 14px;
  color: #8b949e;
  line-height: 1.5;
}
.rule-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 2px;
}
.tag-filter { background: rgba(248, 81, 73, 0.18); color: #f85149; }
.tag-dedup { background: rgba(121, 80, 229, 0.18); color: #a371f7; }
.tag-fix { background: rgba(31, 111, 235, 0.18); color: #58a6ff; }
.rule-text { flex: 1; }
.rule-text code {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 4px;
  padding: 0 4px;
  font-size: 12px;
  color: #c9d1d9;
}

/* 异常日志 */
.error-section {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 20px 24px;
}
.error-section h3 {
  margin: 0 0 16px;
  font-size: 15px;
  font-weight: 600;
  color: #e6edf3;
}
.error-empty { font-size: 14px; color: #484f58; padding: 12px 0; }
.error-table { font-size: 13px; }
.error-table-head {
  display: grid;
  grid-template-columns: 80px 1fr 80px 200px;
  gap: 8px;
  padding: 6px 8px;
  font-size: 11px;
  font-weight: 700;
  color: #484f58;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #21262d;
  margin-bottom: 4px;
}
.error-table-row {
  display: grid;
  grid-template-columns: 80px 1fr 80px 200px;
  gap: 8px;
  padding: 8px;
  border-radius: 6px;
  color: #8b949e;
  align-items: start;
}
.error-table-row:hover { background: #1c2128; }
.error-table-row span { line-height: 1.5; }
.examples {
  font-size: 12px;
  color: #6e7681;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 按钮 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.btn-gray { background: #21262d; color: #c9d1d9; }
.btn-gray:hover { background: #30363d; }
</style>
