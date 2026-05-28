<template>
  <div class="peak-traffic">
    <div class="section-header">
      <h3>④ 统计高峰时段流量变化</h3>
      <button class="btn btn-gray btn-sm" @click="loadData">&#8635; 刷新</button>
    </div>
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>日期</th><th>小时</th><th>区域</th><th>时段类型</th>
            <th>总流量</th><th>平均车速</th><th>平均拥堵</th><th>最大拥堵</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data" :key="row.stat_date + row.stat_hour + row.district">
            <td>{{ row.stat_date }}</td>
            <td class="num">{{ row.stat_hour }}:00</td>
            <td>{{ row.district }}</td>
            <td><span class="peak-tag" :class="row.peak_type">{{ row.peak_type }}</span></td>
            <td class="num">{{ row.total_vehicles }}</td>
            <td class="num">{{ row.avg_speed }}</td>
            <td class="num">{{ row.avg_congestion }}</td>
            <td class="num">{{ row.max_congestion }}</td>
          </tr>
          <tr v-if="data.length === 0"><td colspan="8" class="empty">暂无数据</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPeakTrafficStats } from '../../utils/api.js'

const data = ref([])

async function loadData() {
  try { data.value = await getPeakTrafficStats() } catch (e) { console.error(e) }
}

onMounted(loadData)
</script>

<style scoped>
.peak-traffic { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-header h3 { margin: 0; font-size: 16px; font-weight: 600; color: #e6edf3; }
.table-wrapper { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { background: #21262d; color: #8b949e; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 8px 12px; border-bottom: 1px solid #21262d; color: #c9d1d9; }
.data-table tr:hover td { background: #1c2128; }
.data-table td.num { text-align: right; font-family: monospace; }
.data-table td.empty { text-align: center; color: #484f58; padding: 40px; }
.peak-tag { padding: 2px 8px; border-radius: 10px; font-size: 12px; font-weight: 600; }
.peak-tag.\u65e9\u9ad8\u5cf0 { background: #f8514922; color: #f85149; }
.peak-tag.\u665a\u9ad8\u5cf0 { background: #d2992222; color: #d29922; }
.peak-tag.\u5e73\u5cf0 { background: #3fb95022; color: #3fb950; }
.peak-tag.\u591c\u95f4 { background: #58a6ff22; color: #58a6ff; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s; font-family: inherit; }
.btn-gray { background: #21262d; color: #c9d1d9; }
.btn-gray:hover { background: #30363d; }
</style>
