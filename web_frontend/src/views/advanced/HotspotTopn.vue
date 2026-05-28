<template>
  <div class="hotspot-topn">
    <div class="section-header">
      <h3>② 实时 TopN 热点道路分析</h3>
      <button class="btn btn-gray btn-sm" @click="loadData">&#8635; 刷新</button>
    </div>
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>检测器ID</th><th>检测器名称</th><th>区域</th><th>道路类型</th>
            <th>拥堵评分</th><th>总流量</th><th>平均车速</th><th>统计周期</th><th>更新时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data" :key="row.detector_id + row.stat_period">
            <td>{{ row.detector_id }}</td>
            <td>{{ row.detector_name }}</td>
            <td>{{ row.district }}</td>
            <td>{{ row.road_type }}</td>
            <td class="num" :class="congestionClass(row.congestion_score)">{{ row.congestion_score }}</td>
            <td class="num">{{ row.total_vehicles }}</td>
            <td class="num">{{ row.avg_speed }}</td>
            <td>{{ row.stat_period }}</td>
            <td class="time">{{ row.update_time }}</td>
          </tr>
          <tr v-if="data.length === 0"><td colspan="9" class="empty">暂无数据</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getHotspotTopnList } from '../../utils/api.js'

const data = ref([])

function congestionClass(v) {
  if (v > 0.75) return 'severe'
  if (v > 0.5) return 'moderate'
  return 'light'
}

async function loadData() {
  try { data.value = await getHotspotTopnList() } catch (e) { console.error(e) }
}

onMounted(loadData)
</script>

<style scoped>
.hotspot-topn { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-header h3 { margin: 0; font-size: 16px; font-weight: 600; color: #e6edf3; }
.table-wrapper { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { background: #21262d; color: #8b949e; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 8px 12px; border-bottom: 1px solid #21262d; color: #c9d1d9; }
.data-table tr:hover td { background: #1c2128; }
.data-table td.num { text-align: right; font-family: monospace; }
.data-table td.severe { color: #f85149; font-weight: 700; }
.data-table td.moderate { color: #d29922; }
.data-table td.light { color: #3fb950; }
.data-table td.time { color: #6e7681; font-size: 12px; }
.data-table td.empty { text-align: center; color: #484f58; padding: 40px; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s; font-family: inherit; }
.btn-gray { background: #21262d; color: #c9d1d9; }
.btn-gray:hover { background: #30363d; }
</style>
