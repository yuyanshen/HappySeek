// frontend/src/api/crawler.js
import axios from 'axios'

// Base API client
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// API endpoints
export const startCrawlTask = (urls, depth) => {
  return apiClient.post('/crawl', {
    urls,
    depth
  })
}

export const getTaskStatus = (taskId) => {
  return apiClient.get(`/tasks/${taskId}`)
}

export const checkUrl = (url) => {
  return apiClient.post('/check/url', { url })
}

export const checkLoginPage = (url) => {
  return apiClient.post('/crawler/check-login', { url })
}