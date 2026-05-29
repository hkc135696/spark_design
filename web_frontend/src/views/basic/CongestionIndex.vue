<template>
  <div class="congestion-index">
    <div class="section-header">
      <h3>③ 实时计算道路拥堵指数</h3>
      <button class="btn btn-gray btn-sm" @click="loadData">&#8635; 刷新</button>
    </div>
    <div class="chart-wrapper">
      <div class="chart-container" ref="chartRef"></div>
    </div>
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>检测器ID</th><th>检测器名称</th><th>区域</th><th>道路类型</th>
            <th>总流量</th><th>原始拥堵均值</th><th>计算拥堵指数</th><th>平均车速</th><th>更新时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data" :key="row.detector_id">
            <td>{{ row.detector_id }}</td>
            <td>{{ row.detector_name }}</td>
            <td>{{ row.district }}</td>
            <td>{{ row.road_type }}</td>
            <td class="num">{{ row.total_vehicles }}</td>
            <td class="num">{{ row.raw_avg_congestion }}</td>
            <td class="num" :class="congestionClass(row.calculated_congestion)">{{ row.calculated_congestion }}</td>
            <td class="num">{{ row.avg_speed }}</td>
            <td class="time">{{ row.update_time }}</td>
          </tr>
          <tr v-if="data.length === 0"><td colspan="9" class="empty">暂无数据</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getCongestionIndexList, getCongestionIndexTrend } from '../../utils/api.js'

const data = ref([])
const chartRef = ref(null)
let chart = null

const ROAD_COLORS = {
  '高速': '#58a6ff',
  '快速路': '#3fb950',
  '主干路': '#d29922',
  '次干路': '#f85149',
  '支路': '#bc8cff',
}

function congestionClass(v) {
  if (v > 0.75) return 'severe'
  if (v > 0.5) return 'moderate'
  return 'light'
}

function drawLineChart(rows) {
  if (!chartRef.value || !rows || rows.length === 0) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  // 按道路类型分组，构建时间序列
  const timeSet = new Set()
  const typeMap = {}
  rows.forEach(r => {
    if (!r.road_type || !r.time_label) return
    timeSet.add(r.time_label)
    if (!typeMap[r.road_type]) {
      typeMap[r.road_type] = {}
    }
    typeMap[r.road_type][r.time_label] = Number(r.avg_congestion) || 0
  })

  const times = Array.from(timeSet).sort()
  if (times.length === 0) return

  const roadTypes = Object.keys(typeMap).sort()
  const series = roadTypes.map(rt => ({
    name: rt,
    type: 'line',
    smooth: true,
    symbol: 'circle',
    symbolSize: 4,
    lineStyle: { width: 2.5, color: ROAD_COLORS[rt] || '#8b949e' },
    itemStyle: { color: ROAD_COLORS[rt] || '#8b949e' },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: (ROAD_COLORS[rt] || '#8b949e') + '20' },
        { offset: 1, color: (ROAD_COLORS[rt] || '#8b949e') + '02' },
      ]),
    },
    data: times.map(t => typeMap[rt][t] ?? null),
  }))

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#21262d',
      borderColor: '#30363d',
      textStyle: { color: '#e6edf3', fontSize: 13 },
      formatter: (params) => {
        let html = `<b style="color:#e6edf3">${params[0].axisValue}</b><br/>`
        params.forEach(p => {
          html += `${p.marker} ${p.seriesName}: ${Number(p.value).toFixed(3)}<br/>`
        })
        return html
      },
    },
    legend: {
      data: roadTypes,
      textStyle: { color: '#8b949e', fontSize: 12 },
      top: 0,
      left: 'center',
      itemWidth: 20,
      itemHeight: 3,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '8%',
      top: '14%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: times,
      boundaryGap: false,
      axisLabel: {
        color: '#8b949e',
        fontSize: 11,
        interval: Math.max(Math.floor(times.length / 8), 0),
      },
      axisLine: { lineStyle: { color: '#30363d' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      name: '拥堵指数',
      scale: true,
      nameTextStyle: { color: '#8b949e', fontSize: 11 },
      axisLabel: { color: '#8b949e', fontSize: 11 },
      splitLine: { lineStyle: { color: '#21262d', type: 'dashed' } },
      axisLine: { show: false },
    },
    series,
  })
}

function handleResize() {
  chart?.resize()
}

async function loadTrend() {
  try {
    const rows = await getCongestionIndexTrend()
    if (rows && rows.length) {
      await nextTick()
      drawLineChart(rows)
    }
  } catch (e) {
    console.error(e)
  }
}

async function loadData() {
  try {
    data.value = await getCongestionIndexList()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadData()
  loadTrend()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped>
.congestion-index { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-header h3 { margin: 0; font-size: 16px; font-weight: 600; color: #e6edf3; }
.chart-wrapper { display: flex; justify-content: center; margin-bottom: 20px; }
.chart-container { width: 100%; height: 380px; background: #0d1117; border: 1px solid #30363d; border-radius: 12px; box-shadow: 0 0 24px rgba(88, 166, 255, 0.06), 0 0 6px rgba(88, 166, 255, 0.04); }
.table-wrapper { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { background: #21262d; color: #8b949e; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 8px 12px; border-bottom: 1px solid #21262d; color: #c9d1d9; }
.data-table tr:hover td { background: #1c2128; }
.data-table td.num { text-align: right; font-family: monospace; }
.data-table td.time { color: #6e7681; font-size: 12px; }
.data-table td.severe { color: #f85149; font-weight: 700; }
.data-table td.moderate { color: #d29922; }
.data-table td.light { color: #3fb950; }
.data-table td.empty { text-align: center; color: #484f58; padding: 40px; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s; font-family: inherit; }
.btn-gray { background: #21262d; color: #c9d1d9; }
.btn-gray:hover { background: #30363d; }
</style>
