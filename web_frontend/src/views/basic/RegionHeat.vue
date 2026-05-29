<template>
  <div class="region-heat-page">
    <!-- 热力地图 -->
    <div class="map-section">
      <div class="section-header">
        <h3>{{ mode === 'detail' ? selectedDistrict?.name + ' - 路段详情' : '区域交通热度热力图' }}</h3>
        <div class="header-right">
          <button v-if="mode === 'detail'" class="btn btn-blue btn-sm" @click="resetView">
            ← 返回总览
          </button>
          <span class="map-hint">{{ mode === 'detail' ? '滚轮缩放 | 拖拽平移' : '点击区域查看路段详情 | 滚轮缩放' }}</span>
        </div>
      </div>
      <div class="chart-wrapper" ref="chartRef">
        <!-- 概览模式：选中区域摘要卡片 -->
        <div v-if="mode === 'overview' && selectedDistrict" class="district-card">
          <div class="card-title">{{ selectedDistrict.name }}</div>
          <div class="card-row">
            <span class="card-label">热度评分</span>
            <span class="card-value" :class="heatClass(selectedDistrict.heat_score)">{{ selectedDistrict.heat_score }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">拥堵等级</span>
            <span class="card-value" :class="heatClass(selectedDistrict.heat_score)">
              {{ selectedDistrict.heat_score > 0.75 ? '严重拥堵' : selectedDistrict.heat_score > 0.5 ? '中度拥堵' : '畅通' }}
            </span>
          </div>
          <div class="card-row">
            <span class="card-label">总流量</span>
            <span class="card-value">{{ selectedDistrict.total_vehicles?.toLocaleString() }}</span>
          </div>
          <div class="card-row">
            <span class="card-label">平均车速</span>
            <span class="card-value">{{ selectedDistrict.avg_speed }} km/h</span>
          </div>
          <div class="card-row">
            <span class="card-label">活跃道路</span>
            <span class="card-value">{{ selectedDistrict.active_roads }} 条</span>
          </div>
          <div class="card-hint">点击区域进入路段详情</div>
        </div>
      </div>

      <!-- 详情模式：路段列表 -->
      <div v-if="mode === 'detail'" class="road-panel">
        <div class="road-panel-header">
          <h4>{{ selectedDistrict?.name }} 路段实时状态</h4>
          <span class="road-count">共 {{ districtRoads.length }} 个检测点</span>
        </div>
        <div class="road-list">
          <div
            v-for="rd in districtRoads"
            :key="rd.detector_id"
            class="road-item"
            :class="congestionClass(rd.avg_congestion)"
          >
            <div class="road-info">
              <div class="road-name">{{ rd.detector_name }}</div>
              <div class="road-meta">
                <span class="road-tag">{{ rd.road_type }}</span>
                <span class="road-dir">{{ rd.direction }}</span>
              </div>
            </div>
            <div class="road-stats">
              <div class="road-stat">
                <span class="stat-label">流量</span>
                <span class="stat-value">{{ rd.total_vehicles?.toLocaleString() }}</span>
              </div>
              <div class="road-stat">
                <span class="stat-label">车速</span>
                <span class="stat-value">{{ rd.avg_speed }} km/h</span>
              </div>
              <div class="road-stat">
                <span class="stat-label">拥堵</span>
                <span class="stat-value" :class="heatClass(rd.avg_congestion)">{{ rd.avg_congestion }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 排行明细表格 -->
    <div class="region-heat">
      <div class="section-header">
        <h3>⑤ 统计区域交通热度 - 排行明细</h3>
        <button class="btn btn-gray btn-sm" @click="refreshAll">&#8635; 刷新</button>
      </div>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>排行</th><th>区域</th><th>总流量</th><th>平均拥堵指数</th><th>活跃道路数</th><th>平均车速</th><th>热度评分</th><th>更新时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in data" :key="row.district"
                :class="{ 'row-selected': selectedDistrict && selectedDistrict.name === row.district }"
                @click="onTableRowClick(row)">
              <td class="rank">{{ index + 1 }}</td>
              <td>{{ row.district }}</td>
              <td class="num">{{ row.total_vehicles }}</td>
              <td class="num" :class="heatClass(row.avg_congestion)">{{ row.avg_congestion }}</td>
              <td class="num">{{ row.active_roads }}</td>
              <td class="num">{{ row.avg_speed }}</td>
              <td class="num" :class="heatClass(row.heat_score)">{{ row.heat_score }}</td>
              <td class="time">{{ row.update_time }}</td>
            </tr>
            <tr v-if="data.length === 0"><td colspan="8" class="empty">暂无数据</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getRegionHeatRank, getRoadFlowList } from '../../utils/api.js'
import { getDetectorsByDistrict, EXCLUDED_DISTRICTS } from '../../data/road_detectors.js'

const data = ref([])
const roadFlowData = ref([])
const chartRef = ref(null)
const selectedDistrict = ref(null)
const mode = ref('overview') // 'overview' | 'detail'
let chart = null
let resizeHandler = null
let mapRegistered = false

// 10 个活跃区中心坐标
const DISTRICT_COORDS = {
  '海淀区': [116.298, 39.960],
  '朝阳区': [116.443, 39.921],
  '西城区': [116.366, 39.912],
  '东城区': [116.416, 39.928],
  '丰台区': [116.287, 39.858],
  '石景山区': [116.223, 39.906],
  '通州区': [116.657, 39.910],
  '昌平区': [116.231, 40.221],
  '大兴区': [116.338, 39.727],
  '顺义区': [116.654, 40.130],
}

const ACTIVE_DISTRICTS = Object.keys(DISTRICT_COORDS)

const DEFAULT_CENTER = [116.38, 39.95]
const DEFAULT_ZOOM = 1.15
const FOCUS_ZOOM = 2.5

// 每个区域的路段列表（从静态坐标数据匹配实时 API 数据）
const districtRoads = computed(() => {
  if (!selectedDistrict.value) return []
  const staticDetectors = getDetectorsByDistrict(selectedDistrict.value.name)
  // 按 detector_name 去重，合并实时数据
  const seen = new Set()
  return staticDetectors
    .filter(d => {
      if (seen.has(d.detector_id)) return false
      seen.add(d.detector_id)
      return true
    })
    .map(d => {
      const live = roadFlowData.value.find(r => r.detector_id === d.detector_id)
      return {
        detector_id: d.detector_id,
        detector_name: d.detector_name,
        road_type: d.road_type,
        direction: d.direction,
        lng: d.lng,
        lat: d.lat,
        total_vehicles: live?.total_vehicles || 0,
        avg_speed: live?.avg_speed || 0,
        avg_congestion: live?.avg_congestion || 0,
        max_congestion: live?.max_congestion || 0,
      }
    })
})

function heatClass(v) {
  if (v > 0.75) return 'severe'
  if (v > 0.5) return 'moderate'
  return 'light'
}

function congestionClass(v) {
  if (v > 0.75) return 'border-severe'
  if (v > 0.5) return 'border-moderate'
  return 'border-light'
}

async function loadData() {
  try { data.value = await getRegionHeatRank() } catch (e) { console.error(e) }
}

async function loadRoadFlow() {
  try { roadFlowData.value = await getRoadFlowList() } catch (e) { console.error(e) }
}

function buildMapSeriesData() {
  return ACTIVE_DISTRICTS.map(d => {
    const row = data.value.find(r => r.district === d)
    return {
      name: d,
      value: row ? row.heat_score : 0,
      _raw: row,
    }
  })
}

function buildRoadScatterData() {
  if (mode.value !== 'detail' || !selectedDistrict.value) return []
  return districtRoads.value.map(rd => {
    const cong = rd.avg_congestion || 0
    let color = '#3fb950'
    if (cong > 0.75) color = '#f85149'
    else if (cong > 0.5) color = '#d29922'

    return {
      name: rd.detector_name,
      value: [rd.lng, rd.lat, cong, rd.total_vehicles, rd.avg_speed, rd.road_type, rd.direction],
      _road: rd,
      symbolSize: Math.max(6, Math.sqrt(cong || 0.1) * 18),
      itemStyle: {
        color: color,
        borderColor: '#ffffff44',
        borderWidth: 1,
        shadowBlur: 4,
        shadowColor: 'rgba(0,0,0,0.3)',
      },
    }
  })
}

function getMapOption(center, zoom) {
  const isDetail = mode.value === 'detail'
  const selName = selectedDistrict.value?.name || ''

  const baseTooltip = {
    trigger: 'item',
    backgroundColor: '#1c2128',
    borderColor: '#30363d',
    textStyle: { color: '#e6edf3', fontSize: 13 },
  }

  if (isDetail) {
    // 详情模式：geo + scatter 路段散点层
    return {
      tooltip: {
        ...baseTooltip,
        formatter(params) {
          const rd = params.data?._road
          if (!rd) return params.name
          const cong = rd.avg_congestion || 0
          const level = cong > 0.75 ? '严重拥堵' : cong > 0.5 ? '中度拥堵' : '畅通'
          return `<b>${rd.detector_name}</b><br/>
            方向：${rd.direction} | 类型：${rd.road_type}<br/>
            流量：${rd.total_vehicles?.toLocaleString()}<br/>
            车速：${rd.avg_speed} km/h<br/>
            拥堵指数：<span style="color:${cong > 0.75 ? '#f85149' : cong > 0.5 ? '#d29922' : '#3fb950'};font-weight:700">${cong.toFixed(3)}</span>
            (${level})`
        },
      },
      geo: {
        map: 'beijing',
        roam: true,
        center: center,
        zoom: zoom,
        aspectScale: 0.85,
        itemStyle: {
          areaColor: '#0d1117',
          borderColor: '#21262d',
          borderWidth: 1,
        },
        emphasis: { disabled: true },
        label: { show: false },
        regions: ACTIVE_DISTRICTS.map(d => {
          if (d === selName) {
            return {
              name: d,
              itemStyle: {
                areaColor: '#1f6feb15',
                borderColor: '#58a6ff',
                borderWidth: 2.5,
                shadowBlur: 16,
                shadowColor: 'rgba(88,166,255,0.35)',
              },
              label: {
                show: true,
                color: '#58a6ff',
                fontSize: 14,
                fontWeight: 'bold',
              },
            }
          }
          return {
            name: d,
            itemStyle: { areaColor: '#0d1117', borderColor: '#21262d' },
            label: { show: false },
          }
        }),
      },
      series: [
        {
          type: 'scatter',
          coordinateSystem: 'geo',
          data: buildRoadScatterData(),
          encode: { value: 2 },
          label: { show: false },
          emphasis: {
            scale: 1.5,
            label: {
              show: true,
              formatter: '{b}',
              position: 'top',
              color: '#fff',
              fontSize: 12,
              fontWeight: 'bold',
            },
          },
        },
      ],
    }
  }

  // 概览模式：choropleth 面状填充地图
  return {
    tooltip: {
      ...baseTooltip,
      formatter(params) {
        if (!params.data || params.data.value === undefined) return params.name
        const score = params.data.value
        const level = score > 0.75 ? '严重拥堵' : score > 0.5 ? '中度拥堵' : '畅通'
        const raw = params.data._raw
        return `<b>${params.name}</b><br/>
          热度评分：<span style="color:${score > 0.75 ? '#f85149' : score > 0.5 ? '#d29922' : '#3fb950'};font-weight:700">${score.toFixed(3)}</span><br/>
          拥堵等级：${level}<br/>
          总流量：${raw ? raw.total_vehicles?.toLocaleString() : '-'}<br/>
          平均车速：${raw ? raw.avg_speed + ' km/h' : '-'}<br/>
          <span style="color:#6e7681;font-size:11px">点击查看路段详情</span>`
      },
    },
    visualMap: {
      min: 0,
      max: 1,
      left: 20,
      bottom: 20,
      orient: 'horizontal',
      inRange: {
        color: ['#1a3a2a', '#3fb950', '#d29922', '#f85149'],
      },
      text: ['高热度', '低热度'],
      textStyle: { color: '#8b949e', fontSize: 12 },
      calculable: false,
    },
    series: [
      {
        type: 'map',
        map: 'beijing',
        roam: true,
        center: center,
        zoom: zoom,
        aspectScale: 0.85,
        nameProperty: 'name',
        data: buildMapSeriesData(),
        selectedMode: false,
        itemStyle: {
          borderColor: '#30363d',
          borderWidth: 1.5,
        },
        emphasis: {
          itemStyle: {
            areaColor: '#ffffff15',
            borderColor: '#8b949e',
            borderWidth: 2,
          },
          label: {
            color: '#fff',
            fontSize: 13,
            fontWeight: 'bold',
          },
        },
        label: {
          show: true,
          color: '#8b949e',
          fontSize: 11,
        },
      },
    ],
  }
}

function renderMap(center, zoom) {
  if (!chartRef.value || !mapRegistered) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
    chart.on('click', onChartClick)
  }

  const c = center || DEFAULT_CENTER
  const z = zoom || DEFAULT_ZOOM
  chart.setOption(getMapOption(c, z), true)
}

function onChartClick(params) {
  if (mode.value === 'overview') {
    // 概览模式：点击区域 → 进入详情
    if (params.componentType !== 'series' || params.seriesType !== 'map') return
    const raw = params.data?._raw
    if (!raw) return
    enterDetailMode(raw)
  }
  // 详情模式点击散点不处理（tooltip 已显示信息）
}

function enterDetailMode(row) {
  selectedDistrict.value = {
    name: row.district,
    heat_score: row.heat_score,
    total_vehicles: row.total_vehicles,
    avg_speed: row.avg_speed,
    avg_congestion: row.avg_congestion,
    active_roads: row.active_roads,
  }
  mode.value = 'detail'
  const coords = DISTRICT_COORDS[row.district] || DEFAULT_CENTER
  renderMap(coords, FOCUS_ZOOM)
}

function onTableRowClick(row) {
  enterDetailMode(row)
}

function resetView() {
  selectedDistrict.value = null
  mode.value = 'overview'
  renderMap(DEFAULT_CENTER, DEFAULT_ZOOM)
}

async function refreshAll() {
  await Promise.all([loadData(), loadRoadFlow()])
  await nextTick()
  if (mode.value === 'detail' && selectedDistrict.value) {
    const coords = DISTRICT_COORDS[selectedDistrict.value.name] || DEFAULT_CENTER
    renderMap(coords, FOCUS_ZOOM)
  } else {
    renderMap()
  }
}

async function registerBeijingMap() {
  try {
    const resp = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/110000_full.json')
    if (!resp.ok) throw new Error('fetch failed')
    const geoJson = await resp.json()

    // 过滤掉远郊区（无检测器数据）
    const filteredFeatures = geoJson.features.filter(feat => {
      const name = feat.properties?.name || ''
      return !EXCLUDED_DISTRICTS.includes(name)
    })

    // 修正 GeoJSON 中可能不一致的区域名称
    const nameFixup = {
      '海淀': '海淀区', '朝阳': '朝阳区', '东城': '东城区', '西城': '西城区',
      '丰台': '丰台区', '石景山': '石景山区', '通州': '通州区',
      '昌平': '昌平区', '大兴': '大兴区', '顺义': '顺义区',
      '房山': '房山区', '门头沟': '门头沟区', '平谷': '平谷区',
      '怀柔': '怀柔区', '密云': '密云区', '延庆': '延庆区',
    }

    for (const feat of filteredFeatures) {
      const name = feat.properties?.name || ''
      if (nameFixup[name]) {
        feat.properties.name = nameFixup[name]
      }
    }

    echarts.registerMap('beijing', {
      type: 'FeatureCollection',
      features: filteredFeatures,
    })
  } catch (e) {
    console.warn('[热力图] 北京 GeoJSON 加载失败', e.message)
    echarts.registerMap('beijing', { type: 'FeatureCollection', features: [] })
  } finally {
    mapRegistered = true
  }
}

onMounted(async () => {
  await Promise.all([loadData(), loadRoadFlow(), registerBeijingMap()])
  await nextTick()
  renderMap()

  resizeHandler = () => chart?.resize()
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  chart?.dispose()
  chart = null
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
})
</script>

<style scoped>
.region-heat-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 地图区域 */
.map-section {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 20px;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #e6edf3;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.map-hint {
  font-size: 12px;
  color: #6e7681;
}
.chart-wrapper {
  width: 100%;
  height: 520px;
  position: relative;
}

/* 概览模式：选中区域卡片 */
.district-card {
  position: absolute;
  top: 16px;
  right: 16px;
  background: #1c2128ee;
  backdrop-filter: blur(8px);
  border: 1px solid #30363d;
  border-radius: 10px;
  padding: 16px 20px;
  min-width: 180px;
  z-index: 10;
  pointer-events: none;
}
.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #58a6ff;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #30363d;
}
.card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  gap: 24px;
}
.card-label {
  font-size: 12px;
  color: #8b949e;
}
.card-value {
  font-size: 14px;
  font-weight: 600;
  color: #e6edf3;
  font-family: monospace;
}
.card-value.severe { color: #f85149; }
.card-value.moderate { color: #d29922; }
.card-value.light { color: #3fb950; }
.card-hint {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #30363d;
  font-size: 11px;
  color: #58a6ff;
  text-align: center;
}

/* 详情模式：路段列表面板 */
.road-panel {
  margin-top: 16px;
  border-top: 1px solid #30363d;
  padding-top: 16px;
}
.road-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.road-panel-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #e6edf3;
}
.road-count {
  font-size: 12px;
  color: #6e7681;
}
.road-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 8px;
  max-height: 320px;
  overflow-y: auto;
}
.road-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: 8px;
  background: #0d1117;
  border-left: 3px solid #30363d;
  gap: 16px;
}
.road-item.border-severe { border-left-color: #f85149; }
.road-item.border-moderate { border-left-color: #d29922; }
.road-item.border-light { border-left-color: #3fb950; }
.road-info {
  min-width: 0;
  flex: 1;
}
.road-name {
  font-size: 13px;
  font-weight: 500;
  color: #c9d1d9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.road-meta {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}
.road-tag {
  font-size: 11px;
  color: #8b949e;
  background: #21262d;
  padding: 1px 6px;
  border-radius: 4px;
}
.road-dir {
  font-size: 11px;
  color: #6e7681;
}
.road-stats {
  display: flex;
  gap: 16px;
  flex-shrink: 0;
}
.road-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 48px;
}
.stat-label {
  font-size: 10px;
  color: #6e7681;
  text-transform: uppercase;
}
.stat-value {
  font-size: 13px;
  font-weight: 600;
  color: #e6edf3;
  font-family: monospace;
}
.stat-value.severe { color: #f85149; }
.stat-value.moderate { color: #d29922; }
.stat-value.light { color: #3fb950; }

/* 表格区域 */
.region-heat {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 20px;
}
.table-wrapper { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { background: #21262d; color: #8b949e; padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap; }
.data-table td { padding: 8px 12px; border-bottom: 1px solid #21262d; color: #c9d1d9; }
.data-table tr:hover td { background: #1c2128; cursor: pointer; }
.data-table tr.row-selected td { background: #1f6feb22; }
.data-table td.rank { text-align: center; font-weight: 700; color: #d29922; }
.data-table td.num { text-align: right; font-family: monospace; }
.data-table td.severe { color: #f85149; font-weight: 700; }
.data-table td.moderate { color: #d29922; }
.data-table td.light { color: #3fb950; }
.data-table td.time { color: #6e7681; font-size: 12px; }
.data-table td.empty { text-align: center; color: #484f58; padding: 40px; }

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.btn-gray { background: #21262d; color: #c9d1d9; }
.btn-gray:hover { background: #30363d; }
.btn-blue { background: #1f6feb33; color: #58a6ff; border: 1px solid #1f6feb55; }
.btn-blue:hover { background: #1f6feb55; }
</style>
