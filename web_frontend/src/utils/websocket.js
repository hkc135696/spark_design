import { io } from 'socket.io-client'

let socket = null

export function connectWs(onKpiUpdate, onRankUpdate) {
  if (socket) return socket

  socket = io('http://localhost:5000', {
    transports: ['websocket', 'polling'],
  })

  socket.on('connected', () => {
    console.log('[WebSocket] 已连接')
  })

  socket.on('kpi_update', (data) => {
    if (onKpiUpdate) onKpiUpdate(data)
  })

  socket.on('rank_update', (data) => {
    if (onRankUpdate) onRankUpdate(data)
  })

  socket.on('disconnect', () => {
    console.log('[WebSocket] 已断开')
  })

  return socket
}

export function disconnectWs() {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}
