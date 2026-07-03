<template>
  <div class="app-wrapper">
    <!-- 侧边栏 -->
    <aside class="sidebar" v-if="!isAuthPage">
      <div class="sidebar-logo">
        <el-icon size="20" color="#fff"><School /></el-icon>
        <span class="logo-text">教室预订系统</span>
      </div>
      <div class="sidebar-menu">
        <el-menu
          :default-active="activeMenu"
          router
          class="menu-vertical"
          text-color="#94a3b8"
          active-text-color="#fff"
          background-color="#0f172a"
        >
          <template v-for="item in menuList" :key="item.path">
            <el-menu-item :index="item.path">
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </div>
      <div class="sidebar-footer">
        <el-tag :type="userStore.isAdmin ? 'danger' : 'info'" size="small" effect="dark" style="border-radius: 2px">
          {{ userStore.isAdmin ? '管理员' : '普通用户' }}
        </el-tag>
      </div>
    </aside>

    <!-- 右侧主体区 -->
    <div class="main-container" :class="{ 'full-width': isAuthPage }">
      <!-- 顶部状态栏 -->
      <header class="top-header" v-if="!isAuthPage">
        <div class="breadcrumb-area">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/classrooms' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRouteMeta?.title">{{ currentRouteMeta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="user-area">
          <span class="user-nickname">{{ userStore.userInfo?.username }}</span>
          <el-tag size="small" :type="userStore.isAdmin ? 'danger' : 'info'" effect="plain" style="margin-right: 12px; border-radius: 2px">
            {{ userStore.isAdmin ? '管理员' : '普通用户' }}
          </el-tag>
          <el-dropdown @command="handleCommand" style="margin-right: 8px">
            <el-avatar :size="30" :icon="UserFilled" style="cursor: pointer; background: #2563eb; font-size: 14px" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 主内容区 -->
      <main class="app-main" :class="{ 'auth-main': isAuthPage }">
        <router-view />
      </main>
    </div>
  </div>

  <!-- 修改密码弹窗 -->
  <el-dialog v-model="passwordDialogVisible" title="修改密码" width="480px" align-center destroy-on-close>
    <el-form :model="passwordForm" :rules="passwordRules" ref="passwordRef" label-width="100px">
      <el-form-item label="原密码" prop="old_password">
        <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="请输入原密码" />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="请输入新密码" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="passwordDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitPassword" :loading="pwdLoading">确定</el-button>
    </template>
  </el-dialog>

  <!-- 个人信息弹窗 -->
  <el-dialog v-model="profileDialogVisible" title="个人信息" width="400px" align-center destroy-on-close>
    <div class="profile-content">
      <p><strong>账号：</strong>{{ userStore.userInfo?.username }}</p>
      <p><strong>邮箱：</strong>{{ userStore.userInfo?.email }}</p>
      <p><strong>角色：</strong>{{ userStore.isAdmin ? '管理员' : '普通用户' }}</p>
      <p><strong>状态：</strong>{{ userStore.userInfo?.status === 1 ? '正常' : '停用' }}</p>
      <p><strong>注册时间：</strong>{{ formatTime(userStore.userInfo?.create_time) }}</p>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { changePassword } from '@/api/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  School, UserFilled, OfficeBuilding, Calendar, Timer,
  Grid, Document, Collection, DataAnalysis, Histogram
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const passwordRef = ref()

const isAuthPage = computed(() => route.meta?.public === true)
const activeMenu = computed(() => route.path)

const currentRouteMeta = computed(() => {
  const matched = route.matched.find(r => r.meta?.title)
  return matched?.meta
})

const menuList = computed(() => {
  if (!userStore.isLoggedIn) return []
  const common = [
    { path: '/classrooms', title: '空闲教室查询', icon: 'OfficeBuilding' },
    { path: '/my-reservations', title: '我的预订', icon: 'Calendar' },
    { path: '/periodic-rules', title: '周期预订', icon: 'Timer' }
  ]
  if (userStore.isAdmin) {
    return [
      ...common,
      { path: '/admin/classrooms', title: '教室管理', icon: 'Grid' },
      { path: '/admin/reservations', title: '预订管理', icon: 'Document' },
      { path: '/admin/approvals', title: '预订审批', icon: 'Collection' },
      { path: '/admin/statistics', title: '数据统计', icon: 'DataAnalysis' }
    ]
  }
  return common
})

const passwordDialogVisible = ref(false)
const profileDialogVisible = ref(false)
const pwdLoading = ref(false)
const passwordForm = ref({ old_password: '', new_password: '' })
const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const handleCommand = (cmd) => {
  if (cmd === 'logout') {
    ElMessageBox.confirm('确认退出登录？', '提示', { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }).then(() => {
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    })
  } else if (cmd === 'password') {
    passwordDialogVisible.value = true
    passwordForm.value = { old_password: '', new_password: '' }
  } else if (cmd === 'profile') {
    profileDialogVisible.value = true
  }
}

const submitPassword = async () => {
  await passwordRef.value.validate()
  pwdLoading.value = true
  try {
    await changePassword(passwordForm.value)
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
  } finally {
    pwdLoading.value = false
  }
}

const formatTime = (t) => {
  if (!t) return '-'
  const d = new Date(t)
  return d.toLocaleString('zh-CN')
}

watch(() => route.path, () => {
  if (!userStore.isLoggedIn && !route.meta?.public) {
    router.push('/login')
  }
})
</script>

<style scoped>
.app-wrapper {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
.sidebar {
  width: 210px;
  height: 100vh;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
.sidebar-logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.logo-text {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 0.5px;
}
.sidebar-menu {
  flex: 1;
  overflow-y: auto;
}
.menu-vertical {
  border-right: none;
  background: #0f172a;
}
.menu-vertical :deep(.el-menu-item) {
  height: 46px;
  line-height: 46px;
  font-size: 14px;
  margin: 2px 8px;
  border-radius: 4px;
}
.menu-vertical :deep(.el-menu-item:hover) {
  background-color: rgba(255,255,255,0.05) !important;
}
.menu-vertical :deep(.el-menu-item.is-active) {
  background-color: #2563eb !important;
}
.menu-vertical :deep(.el-icon) {
  font-size: 16px;
}
.sidebar-footer {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.main-container.full-width {
  width: 100vw;
}
.top-header {
  height: 52px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
}
.breadcrumb-area {
  font-size: 14px;
  color: #64748b;
}
.breadcrumb-area :deep(.el-breadcrumb__inner) {
  color: #64748b;
}
.breadcrumb-area :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #1e293b;
  font-weight: 500;
}
.user-area {
  display: flex;
  align-items: center;
  gap: 8px;
}
.user-nickname {
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
}
.app-main {
  flex: 1;
  padding: 20px;
  background: #f1f5f9;
  overflow-y: auto;
}
.app-main.auth-main {
  padding: 0;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
}
.profile-content p {
  margin: 12px 0;
  color: #475569;
  font-size: 14px;
}
</style>
