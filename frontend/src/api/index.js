import axios from 'axios'
import { ElMessage } from 'element-plus'

// 部署到线上时，构建前设置 VITE_SERVER_BASE=https://你的后端域名
// 本地开发时留空，走 Vite 代理
export const SERVER_BASE = import.meta.env.VITE_SERVER_BASE || ''

// 拼接后端返回的静态资源路径（如二维码 /static/qrcodes/xx.png）
export const assetUrl = (path) => (path ? `${SERVER_BASE}${path}` : '')

const request = axios.create({ baseURL: `${SERVER_BASE}/api`, timeout: 15000 })

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

request.interceptors.response.use(
  (res) => {
    const data = res.data
    if (data && data.code === 0) return data
    ElMessage.error(data?.message || '请求失败')
    return Promise.reject(new Error(data?.message || '请求失败'))
  },
  (error) => {
    const status = error.response?.status
    const msg = error.response?.data?.message || error.message || '网络错误'
    ElMessage.error(msg)
    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (!location.hash.startsWith('#/login')) location.hash = '#/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (data) => request.post('/auth/login', data),
  register: (data) => request.post('/auth/register', data),
  me: () => request.get('/auth/me'),
}

export const userApi = {
  list: () => request.get('/users'),
  create: (data) => request.post('/users', data),
  update: (id, data) => request.put(`/users/${id}`, data),
  remove: (id) => request.delete(`/users/${id}`),
}

export const categoryApi = {
  list: () => request.get('/categories'),
  create: (data) => request.post('/categories', data),
  update: (id, data) => request.put(`/categories/${id}`, data),
  remove: (id) => request.delete(`/categories/${id}`),
}

export const productApi = {
  list: (params) => request.get('/products', { params }),
  create: (data) => request.post('/products', data),
  update: (id, data) => request.put(`/products/${id}`, data),
  remove: (id) => request.delete(`/products/${id}`),
}

export const batchApi = {
  list: () => request.get('/batches'),
  detail: (id) => request.get(`/batches/${id}`),
  create: (data) => request.post('/batches', data),
  update: (id, data) => request.put(`/batches/${id}`, data),
  remove: (id) => request.delete(`/batches/${id}`),
  qrcode: (id) => request.get(`/batches/${id}/qrcode`),
}

export const recordApi = {
  list: (batchId, stage) => request.get(`/batches/${batchId}/records/${stage}`),
  create: (batchId, stage, data) => request.post(`/batches/${batchId}/records/${stage}`, data),
  remove: (stage, id) => request.delete(`/batches/records/${stage}/${id}`),
}

export const traceApi = {
  get: (code) => request.get(`/trace/${code}`),
}

export const dashboardApi = {
  stats: () => request.get('/dashboard/stats'),
}

export default request
