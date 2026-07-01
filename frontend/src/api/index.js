import axios from 'axios'
const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = 'Bearer ' + token
  return cfg
})
api.interceptors.response.use(r => r, e => {
  if (e.response?.status === 401) { localStorage.removeItem('token'); window.location.href = '/login' }
  return Promise.reject(e)
})
export default api
