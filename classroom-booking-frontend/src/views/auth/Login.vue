<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { login } from '../../api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const form = ref({
  username: '',
  password: ''
})

const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请填写账号和密码')
    return
  }

  loading.value = true
  try {
    const res = await login(form.value)
    userStore.setAuth(res.data.token, res.data.user)
    ElMessage.success('登录成功')

    if (res.data.user.role === 1) {
      router.push('/admin')
    } else {
      router.push('/user')
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>教室预订系统</h2>
          <p class="subtitle">用户登录</p>
        </div>
      </template>

      <el-form :model="form" label-position="top">
        <el-form-item label="账号">
          <el-input
            v-model="form.username"
            placeholder="请输入账号"
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="full-width"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="form-footer">
          <el-link type="primary" @click="goToRegister">还没有账号？立即注册</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.subtitle {
  margin: 10px 0 0;
  color: #909399;
  font-size: 14px;
}

.form-footer {
  text-align: center;
  margin-top: 15px;
}
</style>
