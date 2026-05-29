<template>
  <div class="avg-speed">
    <div class="section-header">
      <h3>② 实时统计平均车速</h3>
      <button class="btn btn-gray btn-sm" @click="loadData">&#8635; 刷新</button>
    </div>
    <div class="chart-wrapper">
      <div class="chart-container" ref="chartRef"></div>
    </div>
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>检测器ID</th><th>检测器名称</th><th>区域</th>
            <th>平均车速</th><th>标准差</th><th>最高车速</th><th>最低车速</th><th>中位数</th><th>数据点数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data" :key="row.detector_id">
            <td>{{ row.detector_id }}</td>
            <td>{{ row.detector_name }}</td>
            <td>{{ row.district }}</td>
            <td class="num">{{ row.avg_speed }}</td>
            <td class="num">{{ row.speed_stddev }}</td>
            <td class="num">{{ row.max_speed }}</td>
            <td class="num">{{ row.min_speed }}</td>
            <td class="num">{{ row.median_speed }}</td>
            <td class="num">{{ row.data_points }}</td>
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
import { getAvgSpeedList } from '../../utils/api.js'

const data = ref([])
const chartRef = ref(null)
let chart = null

function drawGroupedBarChart(rows) {
  if (!chartRef.value || !rows || rows.length === 0) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  // 按区域分组，计算各指标的区域均值
  const districtMap = {}
  rows.forEach(r => {
    if (!r.district) return
    if (!districtMap[r.district]) {
      districtMap[r.district] = { avg_speed: [], max_speed: [], min_speed: [], median_speed: [] }
    }
    districtMap[r.district].avg_speed.push(Number(r.avg_speed) || 0)
    districtMap[r.district].max_speed.push(Number(r.max_speed) || 0)
    districtMap[r.district].min_speed.push(Number(r.min_speed) || 0)
    districtMap[r.district].median_speed.push(Number(r.median_speed) || 0)
  })

  const districts = Object.keys(districtMap)
  if (districts.length === 0) return

  const avg = arr => arr.reduce((s, v) => s + v, 0) / arr.length

  const metrics = [
    { name: '平均车速', key: 'avg_speed', color: '#58a6ff' },
    { name: '最高车速', key: 'max_speed', color: '#f85149' },
    { name: '最低车速', key: 'min_speed', color: '#3fb950' },
    { name: '中位数车速', key: 'median_speed', color: '#d29922' },
  ]

  const series = metrics.map(m => ({
    name: m.name,
    type: 'bar',
    barGap: '15%',
    barCategoryGap: '30%',
    data: districts.map(d => +avg(districtMap[d][m.key]).toFixed(1)),
    itemStyle: {
      color: m.color,
      borderRadius: [4, 4, 0, 0],
    },
    emphasis: {
      itemStyle: { color: m.color },
    },
  }))

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#21262d',
      borderColor: '#30363d',
      textStyle: { color: '#e6edf3', fontSize: 13 },
      formatter: (params) => {
        let html = `<b style="color:#e6edf3">${params[0].axisValue}</b><br/>`
        params.forEach(p => {
          html += `${p.marker} ${p.seriesName}: ${p.value} km/h<br/>`
        })
        return html
      },
    },
    legend: {
      data: metrics.map(m => m.name),
      textStyle: { color: '#8b949e', fontSize: 12 },
      top: 0,
      left: 'center',
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
      data: districts,
      axisLabel: {
        color: '#8b949e',
        fontSize: 11,
        interval: 0,
      },
      axisLine: { lineStyle: { color: '#30363d' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      name: 'km/h',
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

async function loadData() {
  try {
    const rows = await getAvgSpeedList()
    data.value = rows
    await nextTick()
    drawGroupedBarChart(rows)
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped>
.avg-speed { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }
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
.data-table td.empty { text-align: center; color: #484f58; padding: 40px; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s; font-family: inherit; }
.btn-gray { background: #21262d; color: #c9d1d9; }
.btn-gray:hover { background: #30363d; }
</style>
