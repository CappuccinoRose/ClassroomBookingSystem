<template>
  <div class="auth-page">
    <div class="auth-container">
      <!-- 左侧品牌区 -->
      <div class="auth-brand">
        <div class="brand-content">
          <div class="brand-logo">
            <el-icon size="32" color="#fff"><School /></el-icon>
            <span class="brand-title">教室预订系统</span>
          </div>
          <p class="brand-desc">数字化教室资源管理平台<br>高效预订 · 智能管理 · 数据驱动</p>
        </div>
        <!-- 装饰几何图形 -->
        <div class="deco-shape shape-1"></div>
        <div class="deco-shape shape-2"></div>
        <div class="deco-shape shape-3"></div>
        <div class="deco-line line-1"></div>
        <div class="deco-line line-2"></div>
      </div>
      <!-- 右侧表单区 -->
      <div class="auth-form-area">
        <div class="form-header">
          <h2 class="form-title">欢迎回来</h2>
          <p class="form-subtitle">请登录您的账号以继续使用</p>
        </div>
        <el-form :model="form" :rules="rules" ref="formRef" @keyup.enter="handleLogin">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入账号"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          <div class="form-options">
            <el-checkbox v-model="form.remember">记住密码</el-checkbox>
            <el-link type="primary" :underline="false" style="font-size: 13px">忘记密码？</el-link>
          </div>
          <el-form-item>
            <el-button type="primary" @click="handleLogin" :loading="loading" size="large" style="width: 100%">
              登 录
            </el-button>
          </el-form-item>
        </el-form>
        <div class="form-footer">
          <span>还没有账号？</span>
          <el-link type="primary" :underline="false" @click="$router.push('/register')">立即注册</el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { login } from '@/api/auth'
import { ElMessage } from 'element-plus'
import { School, User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)

const form = ref({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await login({ username: form.value.username, password: form.value.password })
    userStore.setToken(res.data.token)
    userStore.setUserInfo(res.data.user)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (err) {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f1f5f9;
}
.auth-container {
  display: flex;
  width: 860px;
  height: 520px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.06);
}
.auth-brand {
  position: relative;
  width: 45%;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px;
  overflow: hidden;
}
.brand-content {
  position: relative;
  z-index: 2;
}
.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}
.brand-title {
  font-size: 22px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 1px;
}
.brand-desc {
  font-size: 14px;
  color: #94a3b8;
  line-height: 1.8;
  margin: 0;
}
/* 装饰图形 */
.deco-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
  background: #fff;
}
.shape-1 {
  width: 280px;
  height: 280px;
  bottom: -80px;
  right: -60px;
}
.shape-2 {
  width: 160px;
  height: 160px;
  top: 60px;
  right: 40px;
}
.shape-3 {
  width: 80px;
  height: 80px;
  top: 140px;
  right: 160px;
}
.deco-line {
  position: absolute;
  background: rgba(255,255,255,0.06);
  border-radius: 2px;
}
.line-1 {
  width: 60px;
  height: 3px;
  bottom: 100px;
  left: 40px;
}
.line-2 {
  width: 30px;
  height: 3px;
  bottom: 88px;
  left: 40px;
}
.auth-form-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 50px 50px 40px;
}
.form-header {
  margin-bottom: 32px;
}
.form-title {
  margin: 0 0 8px 0;
  font-size: 22px;
  font-weight: 600;
  color: #1e293b;
}
.form-subtitle {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.form-footer {
  text-align: center;
  font-size: 14px;
  color: #64748b;
  margin-top: 8px;
}
</style>
