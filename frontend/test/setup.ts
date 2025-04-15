import { config } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { vi } from 'vitest'

// 全局组件配置
config.global.plugins = [ElementPlus]

// Mock环境变量
vi.stubGlobal('VITE_API_URL', 'http://localhost:5000')
vi.stubGlobal('VITE_WS_URL', 'ws://localhost:5000')

// Mock WebSocket
class MockWebSocket {
  addEventListener() {}
  removeEventListener() {}
  send() {}
  close() {}
}

global.WebSocket = MockWebSocket as any

// Mock Intersection Observer
const mockIntersectionObserver = vi.fn()
mockIntersectionObserver.mockReturnValue({
  observe: () => null,
  unobserve: () => null,
  disconnect: () => null
})
window.IntersectionObserver = mockIntersectionObserver