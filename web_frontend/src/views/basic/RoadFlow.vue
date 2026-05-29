<template>
  <div class="road-flow">
    <div class="section-header">
      <h3>① 实时统计道路车流量</h3>
      <div class="header-actions">
        <button v-if="selectedRoad" class="btn btn-blue btn-sm" @click="selectedRoad = ''">
          ✕ 清除过滤: {{ selectedRoad }}
        </button>
        <button class="btn btn-gray btn-sm" @click="loadData">&#8635; 刷新</button>
      </div>
    </div>

    <div class="chart-wrapper">
      <div ref="chartRef" class="chart-container"></div>
    </div>

    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>检测器ID</th><th>检测器名称</th><th>区域</th><th>道路类型</th>
            <th>时间窗口</th><th>总流量</th><th>平均车速</th><th>最大车速</th>
            <th>平均拥堵</th><th>最大拥堵</th><th>更新时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filteredData" :key="row.detector_id + row.time_window_start"
              :class="{ 'row-highlight': selectedRoad && row.detector_name === selectedRoad }">
            <td>{{ row.detector_id }}</td>
            <td>{{ row.detector_name }}</td>
            <td>{{ row.district }}</td>
            <td>{{ row.road_type }}</td>
            <td>{{ row.time_window_start }}</td>
            <td class="num">{{ row.total_vehicles }}</td>
            <td class="num">{{ row.avg_speed }}</td>
            <td class="num">{{ row.max_speed }}</td>
            <td class="num">{{ row.avg_congestion }}</td>
            <td class="num">{{ row.max_congestion }}</td>
            <td class="time">{{ row.update_time }}</td>
          </tr>
          <tr v-if="filteredData.length === 0"><td colspan="11" class="empty">暂无数据</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { getRoadFlowList } from '../../utils/api.js'
import * as echarts from 'echarts'

const data = ref([])
const chartRef = ref(null)
let chart = null
const selectedRoad = ref('')

async function loadData() {
  try {
    data.value = await getRoadFlowList()
    await nextTick()
    drawHorizontalBarChart()
  } catch (e) { console.error(e) }
}

const filteredData = computed(() => {
  if (!selectedRoad.value) return data.value
  return data.value.filter(row => row.detector_name === selectedRoad.value)
})

function prepareChartData() {
  const grouped = {}
  data.value.forEach(row => {
    const name = row.detector_name
    if (!grouped[name]) {
      grouped[name] = { detector_name: name, district: row.district, total_vehicles: 0 }
    }
    grouped[name].total_vehicles += row.total_vehicles
  })
  const sorted = Object.values(grouped).sort((a, b) => b.total_vehicles - a.total_vehicles)
  return sorted.slice(0, 15)
}

function drawHorizontalBarChart() {
  if (!chartRef.value) return
  const chartData = prepareChartData()
  if (chartData.length === 0) {
    if (chart) { chart.dispose(); chart = null }
    return
  }

  if (!chart) {
    chart = echarts.init(chartRef.value)
    chart.on('click', (params) => {
      if (params.componentType === 'series') {
        selectedRoad.value = params.name
      }
    })
  }

  const names = chartData.map(d => d.detector_name)
  const values = chartData.map(d => d.total_vehicles)
  const maxVal = Math.max(...values)

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#21262d',
      borderColor: '#30363d',
      textStyle: { color: '#c9d1d9', fontSize: 13 },
      formatter: (params) => {
        const p = params[0]
        const d = chartData[p.dataIndex]
        return `<b>${p.name}</b><br/>
          总流量: <b>${p.value.toLocaleString()}</b> 辆<br/>
          区域: ${d.district}`
      }
    },
    grid: { left: 8, right: 80, top: 8, bottom: 8, containLabel: true },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#30363d' } },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#21262d', type: 'dashed' } },
      axisLabel: { color: '#8b949e', fontSize: 12 }
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLine: { lineStyle: { color: '#30363d' } },
      axisTick: { show: false },
      axisLabel: {
        color: '#c9d1d9',
        fontSize: 12,
        width: 140,
        overflow: 'truncate'
      },
      inverse: true
    },
    series: [{
      type: 'bar',
      data: values.map((v, i) => ({
        value: v,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#1a6dd4' },
            { offset: 1, color: '#79c0ff' }
          ]),
          borderRadius: [0, 4, 4, 0],
          shadowBlur: i < 3 ? 12 : 0,
          shadowColor: i < 3 ? 'rgba(88, 166, 255, 0.45)' : 'transparent',
          shadowOffsetX: 0,
          shadowOffsetY: 0
        }
      })),
      barMaxWidth: 28,
      label: {
        show: true,
        position: 'right',
        color: '#8b949e',
        fontSize: 12,
        fontFamily: 'monospace',
        formatter: (p) => p.value.toLocaleString()
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 16,
          shadowColor: 'rgba(88, 166, 255, 0.6)'
        }
      }
    }]
  })
}

function handleResize() {
  chart?.resize()
}

onMounted(async () => {
  await loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped>
.road-flow { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-header h3 { margin: 0; font-size: 16px; font-weight: 600; color: #e6edf3; }
.header-actions { display: flex; align-items: center; gap: 8px; }

.chart-wrapper {
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 10px;
  padding: 16px 12px 8px 8px;
  margin-bottom: 16px;
  box-shadow: 0 0 24px rgba(88, 166, 255, 0.06);
}
.chart-container { width: 100%; height: 460px; }

.table-wrapper { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { background: #21262d; color: #8b949e; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 8px 12px; border-bottom: 1px solid #21262d; color: #c9d1d9; }
.data-table tr:hover td { background: #1c2128; }
.data-table td.num { text-align: right; font-family: monospace; }
.data-table td.time { color: #6e7681; font-size: 12px; }
.data-table td.empty { text-align: center; color: #484f58; padding: 40px; }

.row-highlight td {
  background: rgba(88, 166, 255, 0.08) !important;
  color: #79c0ff !important;
}

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border: none; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s; font-family: inherit; }
.btn-gray { background: #21262d; color: #c9d1d9; }
.btn-gray:hover { background: #30363d; }
.btn-blue { background: rgba(88, 166, 255, 0.15); color: #58a6ff; }
.btn-blue:hover { background: rgba(88, 166, 255, 0.25); }
</style>
