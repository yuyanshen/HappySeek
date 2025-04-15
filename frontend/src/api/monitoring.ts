import axios from 'axios'

const BASE_URL = '/api/monitoring'

export interface SystemStats {
  system: {
    cpu_percent: number
    memory_percent: number
    disk_usage: number
    boot_time: string
  }
  process: {
    cpu_percent: number
    memory_percent: number
    threads: number
    open_files: number
    connections: number
  }
  application: {
    avg_response_time: number
    requests_per_second: number
    error_rate: number
    version: string
  }
}

export interface ErrorData {
  timestamp: string
  endpoint: string
  method: string
  status: string
  count: number
}

export interface PerformanceData {
  response_times: Array<{
    timestamp: string
    value: number
    endpoint: string
    method: string
  }>
  request_rates: Array<{
    timestamp: string
    value: number
  }>
  resources: {
    cpu: number[]
    memory: number[]
  }
}

export interface HealthCheck {
  status: string
  timestamp: string
  version: string
  components: {
    database?: {
      status: string
      message: string
    }
    redis?: {
      status: string
      message: string
    }
    system?: {
      status: string
      message?: string
      metrics: {
        cpu_percent: number
        memory_percent: number
        disk_percent: number
      }
    }
  }
}

class MonitoringAPI {
  async getSystemStats(): Promise<SystemStats> {
    const response = await axios.get(`${BASE_URL}/stats`)
    return response.data
  }

  async getErrorStats(): Promise<ErrorData[]> {
    const response = await axios.get(`${BASE_URL}/errors`)
    return response.data
  }

  async getPerformanceStats(): Promise<PerformanceData> {
    const response = await axios.get(`${BASE_URL}/performance`)
    return response.data
  }

  async getDetailedHealth(): Promise<HealthCheck> {
    const response = await axios.get(`${BASE_URL}/health/detailed`)
    return response.data
  }

  async getMetrics(): Promise<string> {
    const response = await axios.get(`${BASE_URL}/metrics`)
    return response.data
  }
}

export const monitoringAPI = new MonitoringAPI()