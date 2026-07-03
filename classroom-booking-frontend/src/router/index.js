import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getUserInfo } from '@/api/auth'

const routes = [
  {
    path: '/',
    redirect: '/classrooms'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { public: true, title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { public: true, title: '注册' }
  },
  {
    path: '/classrooms',
    name: 'ClassroomList',
    component: () => import('@/views/user/ClassroomList.vue'),
    meta: { title: '空闲教室查询' }
  },
  {
    path: '/my-reservations',
    name: 'MyReservation',
    component: () => import('@/views/user/MyReservation.vue'),
    meta: { title: '我的预订' }
  },
  {
    path: '/periodic-rules',
    name: 'PeriodicRule',
    component: () => import('@/views/user/PeriodicRule.vue'),
    meta: { title: '周期预订管理' }
  },
  {
    path: '/admin/classrooms',
    name: 'ClassroomManage',
    component: () => import('@/views/admin/ClassroomManage.vue'),
    meta: { admin: true, title: '教室管理' }
  },
  {
    path: '/admin/reservations',
    name: 'ReservationManage',
    component: () => import('@/views/admin/ReservationManage.vue'),
    meta: { admin: true, title: '预订管理' }
  },
  {
    path: '/admin/approvals',
    name: 'ApprovalList',
    component: () => import('@/views/admin/ApprovalList.vue'),
    meta: { admin: true, title: '预订审批' }
  },
  {
    path: '/admin/statistics',
    name: 'Statistics',
    component: () => import('@/views/admin/Statistics.vue'),
    meta: { admin: true, title: '数据统计' }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: { title: '无权限' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.public) {
    if (userStore.isLoggedIn && to.path !== '/register') {
      return next('/classrooms')
    }
    return next()
  }

  if (!userStore.isLoggedIn) {
    return next('/login')
  }

  if (!userStore.userInfo) {
    try {
      const res = await getUserInfo()
      userStore.setUserInfo(res.data)
    } catch {
      userStore.logout()
      return next('/login')
    }
  }

  if (to.meta.admin && !userStore.isAdmin) {
    return next('/403')
  }

  next()
})

export default router
