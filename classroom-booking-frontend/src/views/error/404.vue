<template>
  <div class="error-page">
    <el-result icon="error" title="404" sub-title="页面不存在">
      <template #extra>
        <el-button type="primary" @click="$router.push('/classrooms')">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>

<style scoped>
.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>
