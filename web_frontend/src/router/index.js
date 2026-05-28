import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/console'
  },
  {
    path: '/console',
    name: 'PageConsole',
    component: () => import('../views/PageConsole.vue'),
    meta: { title: '总控制台' }
  },
  {
    path: '/collection',
    name: 'PageCollection',
    component: () => import('../views/PageCollection.vue'),
    meta: { title: '实时数据采集' }
  },
  {
    path: '/cleaning',
    name: 'PageCleaning',
    component: () => import('../views/PageCleaning.vue'),
    meta: { title: '数据清洗与预处理' }
  },
  {
    path: '/basic',
    name: 'PageBasic',
    component: () => import('../views/PageBasic.vue'),
    meta: { title: '基础流数据分析' },
    children: [
      { path: '', redirect: '/basic/road-flow' },
      { path: 'road-flow', name: 'RoadFlow', component: () => import('../views/basic/RoadFlow.vue'), meta: { title: '道路车流量' } },
      { path: 'avg-speed', name: 'AvgSpeed', component: () => import('../views/basic/AvgSpeed.vue'), meta: { title: '平均车速' } },
      { path: 'congestion-index', name: 'CongestionIndex', component: () => import('../views/basic/CongestionIndex.vue'), meta: { title: '拥堵指数' } },
      { path: 'peak-traffic', name: 'PeakTraffic', component: () => import('../views/basic/PeakTraffic.vue'), meta: { title: '高峰时段' } },
      { path: 'region-heat', name: 'RegionHeat', component: () => import('../views/basic/RegionHeat.vue'), meta: { title: '区域热度' } },
    ]
  },
  {
    path: '/advanced',
    name: 'PageAdvanced',
    component: () => import('../views/PageAdvanced.vue'),
    meta: { title: '进阶流数据分析' },
    children: [
      { path: '', redirect: '/advanced/hotspot-topn' },
      { path: 'hotspot-topn', name: 'HotspotTopn', component: () => import('../views/advanced/HotspotTopn.vue'), meta: { title: 'TopN热点' } },
      { path: 'anomaly-detect', name: 'AnomalyDetect', component: () => import('../views/advanced/AnomalyDetect.vue'), meta: { title: '异常检测' } },
      { path: 'region-rank', name: 'RegionRank', component: () => import('../views/advanced/RegionRank.vue'), meta: { title: '区域排行' } },
      { path: 'sliding-window', name: 'SlidingWindow', component: () => import('../views/advanced/SlidingWindow.vue'), meta: { title: '滑动窗口' } },
      { path: 'accident-alert', name: 'AccidentAlert', component: () => import('../views/advanced/AccidentAlert.vue'), meta: { title: '事故预警' } },
      { path: 'congestion-predict', name: 'CongestionPredict', component: () => import('../views/advanced/CongestionPredict.vue'), meta: { title: '拥堵预测' } },
      { path: 'sustained-congestion', name: 'SustainedCongestion', component: () => import('../views/advanced/SustainedCongestion.vue'), meta: { title: '持续拥堵' } },
    ]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '页面'} - 智慧交通`
})

export default router
