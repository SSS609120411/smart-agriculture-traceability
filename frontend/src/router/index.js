import { createRouter, createWebHashHistory } from 'vue-router'
import Layout from '../components/Layout.vue'

const routes = [
  { path: '/login', component: () => import('../views/Login.vue'), meta: { title: '登录' } },
  { path: '/register', component: () => import('../views/Register.vue'), meta: { title: '注册' } },
  { path: '/trace/:code?', component: () => import('../views/Trace.vue'), meta: { title: '溯源查询' } },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '数据看板' } },
      { path: 'categories', component: () => import('../views/Categories.vue'), meta: { title: '产品分类', roles: ['admin'] } },
      { path: 'products', component: () => import('../views/Products.vue'), meta: { title: '产品管理' } },
      { path: 'batches', component: () => import('../views/BatchList.vue'), meta: { title: '批次管理' } },
      { path: 'batches/:id', component: () => import('../views/BatchDetail.vue'), meta: { title: '批次详情' } },
      { path: 'users', component: () => import('../views/Users.vue'), meta: { title: '用户管理', roles: ['admin'] } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.path === '/login' || to.path === '/register' || to.path.startsWith('/trace')) return true
  if (!token) return { path: '/login' }
  if (to.meta.roles) {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user || !to.meta.roles.includes(user.role)) return { path: '/dashboard' }
  }
  return true
})

export default router
