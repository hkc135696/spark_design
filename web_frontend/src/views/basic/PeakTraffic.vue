<template>
  <div class="peak-traffic">
    <div class="section-header">
      <h3>④ 统计高峰时段流量变化</h3>
      <button class="btn btn-gray btn-sm" @click="loadData">&#8635; 刷新</button>
    </div>
    <div class="ring-chart-wrapper">
      <div class="ring-chart-container" ref="chartRef"></div>
    </div>
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>日期</th><th>小时</th><th>区域</th><th>时段类型</th>
            <th>总流量</th><th>变化(较上一小时)</th><th>变化率</th><th>平均车速</th><th>平均拥堵</th><th>最大拥堵</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data" :key="row.stat_date + row.stat_hour + row.district">
            <td>{{ formatDate(row.stat_date) }}</td>
            <td class="num">{{ row.stat_hour }}:00</td>
            <td>{{ row.district }}</td>
            <td><span class="peak-tag" :class="row.peak_type">{{ row.peak_type }}</span></td>
            <td class="num">{{ row.total_vehicles }}</td>
            <td class="num">{{ formatDelta(pick(row, 'delta_vehicles', 'deltaVehicles')) }}</td>
            <td class="num">{{ formatPct(pick(row, 'pct_change', 'pctChange')) }}</td>
            <td class="num">{{ row.avg_speed }}</td>
            <td class="num">{{ row.avg_congestion }}</td>
            <td class="num">{{ row.max_congestion }}</td>
          </tr>
          <tr v-if="data.length === 0"><td colspan="10" class="empty">暂无数据</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getPeakTrafficStats, getPeakSummary } from '../../utils/api.js'

const data = ref([])
const chartRef = ref(null)
let chart = null

function formatDate(d) {
  // 后端可能返回 "2026-05-29" 或 "Fri, 29 May 2026 00:00:00 GMT"
  if (!d) return ''
  if (typeof d === 'string') {
    // 优先保留 yyyy-MM-dd
    const m = d.match(/\d{4}-\d{2}-\d{2}/)
    if (m) return m[0]
    const dt = new Date(d)
    if (!Number.isNaN(dt.getTime())) return dt.toISOString().slice(0, 10)
    return d
  }
  const dt = new Date(d)
  if (!Number.isNaN(dt.getTime())) return dt.toISOString().slice(0, 10)
  return String(d)
}

function pick(obj, ...keys) {
  for (const k of keys) {
    if (obj && Object.prototype.hasOwnProperty.call(obj, k)) return obj[k]
  }
  return undefined
}

function formatDelta(v) {
  if (v === null || v === undefined) return '-'
  const n = Number(v)
  if (Number.isNaN(n)) return String(v)
  const sign = n > 0 ? '+' : ''
  return `${sign}${Math.trunc(n)}`
}

function formatPct(v) {
  if (v === null || v === undefined) return '-'
  const n = Number(v)
  if (Number.isNaN(n)) return String(v)
  return `${(n * 100).toFixed(2)}%`
}

function drawRingChart(summary) {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  const peakColors = {
    '早高峰': '#f85149',
    '晚高峰': '#d29922',
    '平峰': '#3fb950',
    '夜间': '#58a6ff',
  }
  const total = summary.reduce((s, r) => s + (r.total_vehicles || 0), 0)
  const seriesData = summary.map(r => ({
    name: r.peak_type,
    value: r.total_vehicles || 0,
    itemStyle: { color: peakColors[r.peak_type] || '#8b949e' }
  }))
  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: '#21262d',
      borderColor: '#30363d',
      textStyle: { color: '#e6edf3', fontSize: 13 },
      formatter: (p) => {
        const pct = total > 0 ? ((p.value / total) * 100).toFixed(1) : 0
        return `${p.marker} ${p.name}<br/>流量: ${p.value.toLocaleString()} 辆<br/>占比: ${pct}%`
      }
    },
    graphic: [{
      type: 'text',
      left: 'center',
      top: 'center',
      style: {
        text: `总计\n${total.toLocaleString()}`,
        textAlign: 'center',
        fill: '#e6edf3',
        fontSize: 14,
        lineHeight: 20,
        fontWeight: 'bold',
      }
    }],
    series: [{
      type: 'pie',
      radius: ['52%', '75%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderColor: '#161b22',
        borderWidth: 3,
        borderRadius: 2,
      },
      label: {
        show: true,
        position: 'outside',
        formatter: '{b}\n{d}%',
        color: '#8b949e',
        fontSize: 12,
        lineHeight: 18,
      },
      labelLine: {
        lineStyle: { color: '#30363d' }
      },
      emphasis: {
        scaleSize: 8,
        label: { fontSize: 15, fontWeight: 'bold' }
      },
      data: seriesData
    }]
  })
}

async function loadSummary() {
  try {
    const summary = await getPeakSummary()
    if (summary && summary.length) {
      await nextTick()
      drawRingChart(summary)
    }
  } catch (e) {
    console.error(e)
  }
}

function handleResize() {
  chart?.resize()
}

async function loadData() {
  try {
    const rows = await getPeakTrafficStats()
    if (Array.isArray(rows) && rows.length) {
      console.log('[PeakTraffic] first row keys:', Object.keys(rows[0]))
      console.log('[PeakTraffic] first row:', rows[0])
    }
    data.value = rows
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadData()
  loadSummary()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped>
.peak-traffic { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }
.ring-chart-wrapper { display: flex; justify-content: center; margin-bottom: 20px; }
.ring-chart-container { width: 420px; height: 380px; background: #0d1117; border: 1px solid #30363d; border-radius: 12px; box-shadow: 0 0 24px rgba(88, 166, 255, 0.06), 0 0 6px rgba(88, 166, 255, 0.04); }
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
