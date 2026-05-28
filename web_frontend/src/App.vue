<template>
  <div class="app">
    <nav class="navbar">
      <div class="nav-brand">
        <span class="logo">&#128663;</span>
        智慧交通实时路况监测系统
      </div>
      <div class="nav-links">
        <router-link to="/console">总控制台</router-link>
        <router-link to="/collection">实时采集</router-link>
        <router-link to="/cleaning">数据清洗</router-link>
        <router-link to="/basic">基础分析</router-link>
        <router-link to="/advanced" class="advanced-link">进阶分析</router-link>
      </div>
      <div class="nav-status">
        <span class="dot" :class="{ connected: wsConnected }"></span>
        {{ wsConnected ? '实时连接' : '连接中...' }}
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { connectWs, disconnectWs } from './utils/websocket.js'

const wsConnected = ref(false)
const kpiData = ref({})
const rankData = ref({ region: [], road: [] })

function onKpiUpdate(data) { kpiData.value = data }
function onRankUpdate(data) { rankData.value = data }

onMounted(async () => {
  connectWs(onKpiUpdate, onRankUpdate)
  wsConnected.value = true
})

onUnmounted(() => {
  disconnectWs()
})
</script>

<style>
.app { min-height: 100vh; background: #0f1419; color: #e6edf3; }
.navbar {
  display: flex; align-items: center; padding: 0 24px; height: 56px;
  background: #161b22; border-bottom: 1px solid #30363d;
  position: sticky; top: 0; z-index: 100;
}
.nav-brand { font-size: 18px; font-weight: 700; color: #58a6ff; margin-right: 32px; }
.logo { margin-right: 8px; }
.nav-links { display: flex; gap: 8px; flex: 1; }
.nav-links a {
  padding: 6px 16px; border-radius: 6px; color: #8b949e; text-decoration: none;
  font-size: 14px; transition: all 0.2s;
}
.nav-links a:hover { background: #21262d; color: #e6edf3; }
.nav-links a.router-link-active { background: #1f6feb33; color: #58a6ff; }
.nav-links a.control-link {
  background: #2ea04322;
  color: #3fb950;
  border: 1px solid #2ea04355;
}
.nav-links a.control-link:hover { background: #2ea04344; color: #3fb950; }
.nav-links a.control-link.router-link-active { background: #2ea04333; color: #3fb950; }
.nav-links a.advanced-link {
  background: #6e768122;
  color: #d29922;
  border: 1px solid #6e768155;
}
.nav-links a.advanced-link:hover { background: #6e768133; color: #d29922; }
.nav-links a.advanced-link.router-link-active { background: #6e768144; color: #d29922; }
.nav-status { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #8b949e; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #f85149; }
.dot.connected { background: #3fb950; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
.main-content { padding: 20px 24px; }
</style>
