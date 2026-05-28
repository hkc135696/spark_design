import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// ============================================================
// 页面一：总控制台
// ============================================================
export const getJobs = () =>
  api.get('/console/jobs').then(r => r.data.data)

export const startJob = (jobId) =>
  api.post(`/console/jobs/${jobId}/start`).then(r => r.data)

export const stopJob = (jobId) =>
  api.post(`/console/jobs/${jobId}/stop`).then(r => r.data)

export const startAllJobs = () =>
  api.post('/console/jobs/start-all').then(r => r.data)

export const stopAllJobs = () =>
  api.post('/console/jobs/stop-all').then(r => r.data)

export const getJobLog = (jobId) =>
  api.get(`/console/jobs/${jobId}/log`).then(r => r.data.data)

// ============================================================
// 页面二：实时数据采集
// ============================================================
export const getCollectionStatus = () =>
  api.get('/collection/status').then(r => r.data.data)

export const getCollectionStats = () =>
  api.get('/collection/stats').then(r => r.data.data)

// ============================================================
// 页面三：数据清洗与预处理
// ============================================================
export const getCleaningStatus = () =>
  api.get('/cleaning/status').then(r => r.data.data)

export const getCleaningErrors = () =>
  api.get('/cleaning/errors').then(r => r.data.data)

// ============================================================
// 页面四：基础流数据分析
// ============================================================
export const getKpi = () => api.get('/basic/kpi').then(r => r.data.data)

export const getTrend = (type = 'congestion', minutes = 60) =>
  api.get('/basic/trend', { params: { type, minutes } }).then(r => r.data.data)

export const getRegionRank = (limit = 10) =>
  api.get('/basic/region-rank', { params: { limit } }).then(r => r.data.data)

export const getHourlyStats = () =>
  api.get('/basic/hourly-stats').then(r => r.data.data)

// 基础分析子功能
export const getRoadFlowList = () =>
  api.get('/basic/road-flow/list').then(r => r.data.data)

export const getAvgSpeedList = () =>
  api.get('/basic/avg-speed/list').then(r => r.data.data)

export const getCongestionIndexList = () =>
  api.get('/basic/congestion-index/list').then(r => r.data.data)

export const getPeakTrafficStats = () =>
  api.get('/basic/peak-traffic/stats').then(r => r.data.data)

export const getPeakSummary = () =>
  api.get('/basic/peak-traffic/summary').then(r => r.data.data)

export const getRegionHeatRank = () =>
  api.get('/basic/region-heat/rank').then(r => r.data.data)

// ============================================================
// 页面五：进阶流数据分析
// ============================================================
export const getHotspotRoads = (limit = 10) =>
  api.get('/advanced/hotspot-roads', { params: { limit } }).then(r => r.data.data)

export const getAlerts = (page = 1, pageSize = 20) =>
  api.get('/advanced/alerts', { params: { page, page_size: pageSize } }).then(r => r.data.data)

// 进阶分析子功能
export const getSlidingWindowStats = () =>
  api.get('/advanced/sliding-window/stats').then(r => r.data.data)

export const getHotspotTopnList = () =>
  api.get('/advanced/hotspot-topn/list').then(r => r.data.data)

export const getAnomalyDetectList = () =>
  api.get('/advanced/anomaly-detect/list').then(r => r.data.data)

export const getAccidentAlertList = () =>
  api.get('/advanced/accident-alert/list').then(r => r.data.data)

export const getCongestionPredictList = () =>
  api.get('/advanced/congestion-predict/list').then(r => r.data.data)

export const getRegionRankList = () =>
  api.get('/advanced/region-rank/list').then(r => r.data.data)

export const getSustainedCongestionList = () =>
  api.get('/advanced/sustained-congestion/list').then(r => r.data.data)

export default api
