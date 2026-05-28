<template>
  <div class="anomaly-detect">
    <div class="section-header">
      <h3>③ 异常车辆检测</h3>
      <button class="btn btn-gray btn-sm" @click="loadData">&#8635; 刷新</button>
    </div>
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th><th>告警类型</th><th>级别</th><th>检测器ID</th><th>检测器名称</th>
            <th>区域</th><th>触发值(车速)</th><th>Z-Score</th><th>描述</th><th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data" :key="row.id">
            <td>{{ row.id }}</td>
            <td><span class="alert-type">{{ row.alert_type }}</span></td>
            <td><span class="alert-level" :class="'level-' + row.alert_level">{{ row.alert_level }}</span></td>
            <td>{{ row.detector_id }}</td>
            <td>{{ row.detector_name }}</td>
            <td>{{ row.district }}</td>
            <td class="num">{{ row.trigger_value }}</td>
            <td class="num">{{ row.z_score }}</td>
            <td class="desc">{{ row.description }}</td>
            <td class="time">{{ row.start_time }}</td>
          </tr>
          <tr v-if="data.length === 0"><td colspan="10" class="empty">暂无异常数据</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAnomalyDetectList } from '../../utils/api.js'

const data = ref([])

async function loadData() {
  try { data.value = await getAnomalyDetectList() } catch (e) { console.error(e) }
}

onMounted(loadData)
</script>

<style scoped>
.anomaly-detect { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-header h3 { margin: 0; font-size: 16px; font-weight: 600; color: #e6edf3; }
.table-wrapper { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { background: #21262d; color: #8b949e; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 8px 12px; border-bottom: 1px solid #21262d; color: #c9d1d9; }
.data-table tr:hover td { background: #1c2128; }
.data-table td.num { text-align: right; font-family: monospace; }
.data-table td.desc { max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 12px; color: #d29922; }
.data-table td.time { color: #6e7681; font-size: 12px; white-space: nowrap; }
.data-table td.empty { text-align: center; color: #484f58; padding: 40px; }
.alert-type { background: #d2992222; color: #d29922; padding: 2px 8px; border-radius: 8px; font-size: 12px; font-weight: 600; }
.alert-level { padding: 2px 8px; border-radius: 8px; font-size: 12px; font-weight: 600; }
.alert-level.level-2 { background: #f8514922; color: #f85149; }
.alert-level.level-3 { background: #da363322; color: #f85149; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s; font-family: inherit; }
.btn-gray { background: #21262d; color: #c9d1d9; }
.btn-gray:hover { background: #30363d; }
</style>
