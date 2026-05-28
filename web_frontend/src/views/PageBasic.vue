<template>
  <div class="page-basic">
    <div class="page-header">
      <h2>基础流数据分析</h2>
    </div>

    <div class="sub-nav">
      <router-link
        v-for="item in subNavItems"
        :key="item.path"
        :to="item.path"
        class="sub-nav-item"
      >
        <span class="sub-nav-num">{{ item.num }}</span>
        <span class="sub-nav-label">{{ item.label }}</span>
      </router-link>
    </div>

    <div class="sub-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
const subNavItems = [
  { num: '1', label: '道路车流量', path: '/basic/road-flow' },
  { num: '2', label: '平均车速', path: '/basic/avg-speed' },
  { num: '3', label: '拥堵指数', path: '/basic/congestion-index' },
  { num: '4', label: '高峰时段', path: '/basic/peak-traffic' },
  { num: '5', label: '区域热度', path: '/basic/region-heat' },
]
</script>

<style scoped>
.page-basic { max-width: 1200px; margin: 0 auto; }
.page-header { margin-bottom: 20px; }
.page-header h2 { margin: 0; font-size: 22px; font-weight: 600; color: #e6edf3; }

.sub-nav {
  display: flex; gap: 8px; margin-bottom: 20px;
  background: #161b22; border: 1px solid #30363d;
  border-radius: 12px; padding: 8px; flex-wrap: wrap;
}
.sub-nav-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px; border-radius: 8px;
  color: #8b949e; text-decoration: none; font-size: 14px;
  transition: all 0.2s;
}
.sub-nav-item:hover { background: #21262d; color: #e6edf3; }
.sub-nav-item.router-link-active { background: #1f6feb33; color: #58a6ff; }
.sub-nav-num { background: #30363d; border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; }
.sub-nav-item.router-link-active .sub-nav-num { background: #1f6feb; color: #fff; }

.sub-content { min-height: 400px; }
</style>
