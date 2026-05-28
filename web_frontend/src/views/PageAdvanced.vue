<template>
  <div class="page-advanced">
    <div class="page-header">
      <h2>进阶流数据分析</h2>
    </div>

    <div class="sub-nav">
      <router-link
        v-for="item in subNavItems"
        :key="item.path"
        :to="item.path"
        class="sub-nav-item"
        :class="{ 'unimplemented': item.todo }"
      >
        <span class="sub-nav-num" :class="{ todo: item.todo }">{{ item.num }}</span>
        <span class="sub-nav-label">{{ item.label }}</span>
        <span v-if="item.todo" class="todo-badge">待开发</span>
      </router-link>
    </div>

    <div class="sub-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
const subNavItems = [
  { num: '1', label: '滑动窗口统计', path: '/advanced/sliding-window', todo: true },
  { num: '2', label: 'TopN 热点道路', path: '/advanced/hotspot-topn', todo: false },
  { num: '3', label: '异常车辆检测', path: '/advanced/anomaly-detect', todo: false },
  { num: '4', label: '交通事故预警', path: '/advanced/accident-alert', todo: true },
  { num: '5', label: '拥堵预测', path: '/advanced/congestion-predict', todo: true },
  { num: '6', label: '区域拥堵排行', path: '/advanced/region-rank', todo: false },
  { num: '7', label: '持续拥堵检测', path: '/advanced/sustained-congestion', todo: true },
]
</script>

<style scoped>
.page-advanced { max-width: 1200px; margin: 0 auto; }
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
.sub-nav-item.unimplemented { opacity: 0.6; }
.sub-nav-num { background: #30363d; border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; }
.sub-nav-num.todo { background: #6e7681; }
.sub-nav-item.router-link-active .sub-nav-num { background: #1f6feb; color: #fff; }
.sub-nav-item.router-link-active .sub-nav-num.todo { background: #6e7681; }
.todo-badge { background: #6e7681; color: #c9d1d9; font-size: 11px; padding: 1px 6px; border-radius: 10px; }

.sub-content { min-height: 400px; }
</style>
