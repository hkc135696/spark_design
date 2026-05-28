<template>
  <div class="todo-page">
    <div class="todo-banner">
      <div class="todo-icon">&#128678;</div>
      <h3>基于状态计算的持续拥堵检测</h3>
      <p>此功能正在开发中，敬请期待。</p>
      <div class="todo-detail">
        <h4>预期功能</h4>
        <ul>
          <li>使用 ROW_NUMBER 窗口函数识别连续拥堵周期</li>
          <li>区分偶发性拥堵（短时）和持续性拥堵（长时）</li>
          <li>按拥堵等级（轻度/中度/重度）分类告警</li>
          <li>触发后写入 MySQL traffic_alerts 表</li>
        </ul>
        <p class="todo-file">对应文件：<code>spark_streaming/advanced_analytics/⑦_sustained_congestion.py</code></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.todo-page { min-height: 400px; display: flex; align-items: center; justify-content: center; }
.todo-banner { text-align: center; background: #161b22; border: 1px solid #30363d; border-radius: 16px; padding: 48px; max-width: 480px; }
.todo-icon { font-size: 64px; margin-bottom: 16px; opacity: 0.5; }
.todo-banner h3 { margin: 0 0 8px; font-size: 24px; color: #e6edf3; }
.todo-banner p { margin: 0 0 24px; color: #8b949e; font-size: 14px; }
.todo-detail { text-align: left; background: #0d1117; border-radius: 10px; padding: 20px; }
.todo-detail h4 { margin: 0 0 12px; font-size: 14px; color: #8b949e; }
.todo-detail ul { margin: 0 0 16px; padding-left: 18px; font-size: 13px; color: #8b949e; line-height: 1.8; }
.todo-file { margin: 0; font-size: 12px; color: #6e7681; }
.todo-file code { background: #21262d; padding: 2px 6px; border-radius: 4px; color: #79c0ff; }
</style>
