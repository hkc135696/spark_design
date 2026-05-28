<template>
  <div class="todo-page">
    <div class="todo-banner">
      <div class="todo-icon">&#128678;</div>
      <h3>滑动窗口统计</h3>
      <p>此功能正在开发中，敬请期待。</p>
      <div class="todo-detail">
        <h4>预期功能</h4>
        <ul>
          <li>实现 Tumbling Window（滚动窗口）统计</li>
          <li>实现 Sliding Window（滑动窗口）统计</li>
          <li>实现 Session Window（会话窗口）统计</li>
          <li>支持自定义窗口大小和滑动步长</li>
        </ul>
        <p class="todo-file">对应文件：<code>spark_streaming/advanced_analytics/①_sliding_window.py</code></p>
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
