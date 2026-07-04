<script setup>
import { onMounted } from 'vue'
import { useUserStore } from './stores/user'

const userStore = useUserStore()

onMounted(() => {
  userStore.initializeAuth()
})
</script>

<template>
  <router-view />
</template>

<style scoped>
</style>
