<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../../api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()

const form = ref({
  username: '',
  password: '',
  confirmPassword: '',
  email: ''
})

const loading = ref(false)

const handleRegister = async () => {
  if (!form.value.username || !form.value.password || !form.value.email) {
    ElMessage.warning('请填写完整信息')
    return
  }

  if (form.value.password !== form.value.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  if (form.value.password.length < 6) {
    ElMessage.warning('密码长度至少为6位')
    return
  }

  loading.value = true
  try {
    await register({
      username: form.value.username,
      password: form.value.password,
      email: form.value.email
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>用户注册</h2>
          <p class="subtitle">创建新账号</p>
        </div>
      </template>

      <el-form :model="form" label-position="top">
        <el-form-item label="账号">
          <el-input v-model="form.username" placeholder="请输入账号" size="large" />
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱" size="large" />
        </el-form-item>

        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="full-width"
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>

        <div class="form-footer">
          <el-link type="primary" @click="goToLogin">已有账号？立即登录</el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
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
