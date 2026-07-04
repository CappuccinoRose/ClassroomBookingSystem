import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/Register.vue'),
    meta: { public: true }
  },
  {
    path: '/user',
    component: () => import('../views/layout/UserLayout.vue'),
    meta: { requiresAuth: true, role: 0 },
    children: [
      {
        path: '',
        redirect: '/user/classrooms'
      },
      {
        path: 'classrooms',
        name: 'UserClassrooms',
        component: () => import('../views/user/ClassroomList.vue')
      },
      {
        path: 'reservations',
        name: 'UserReservations',
        component: () => import('../views/user/MyReservation.vue')
      },
      {
        path: 'periodic',
        name: 'UserPeriodic',
        component: () => import('../views/user/PeriodicRule.vue')
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('../views/layout/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 1 },
    children: [
      {
        path: '',
        redirect: '/admin/classrooms'
      },
      {
        path: 'classrooms',
        name: 'AdminClassrooms',
        component: () => import('../views/admin/ClassroomManage.vue')
      },
      {
        path: 'reservations',
        name: 'AdminReservations',
        component: () => import('../views/admin/ReservationManage.vue')
      },
      {
        path: 'approvals',
        name: 'AdminApprovals',
        component: () => import('../views/admin/ApprovalList.vue')
      },
      {
        path: 'statistics',
        name: 'AdminStatistics',
        component: () => import('../views/admin/Statistics.vue')
      }
    ]
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('../views/error/403.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/error/404.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
    return
  }

  if (to.meta.role !== undefined && userStore.userInfo.role !== to.meta.role) {
    next('/403')
    return
  }

  next()
})

export default router
