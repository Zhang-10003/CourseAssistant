import { createRouter, createWebHistory } from 'vue-router'

// 1. 定义路由映射表
const routes = [
  {
    path: '/admin',
    name: 'Admin',
    // 这里的路径必须指向你截图中的 admin.vue
    component: () => import('../pages/admin/admin.vue') 
  },
  {
    path: '/db',
    name: 'Database',
    // 这里的路径必须指向你截图中的 db.vue
    component: () => import('../pages/admin/db.vue')
  },
  {
    path: '/',
    redirect: '/admin' // 默认访问时跳转到教师管理
  }
]

// 2. 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router