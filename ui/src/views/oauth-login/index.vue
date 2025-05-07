<template>
  <!-- 可以留空或添加加载提示 -->
  <div v-if="loading" class="loading-container">
    <p>正在跳转到第三方登录页面...</p>
    <!-- 可以添加加载动画 -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import oauthApi from '@/api/oauth'

const loading = ref(true)

async function handleRedirect() {
  try {
    const res = await oauthApi.startOauthLogin(loading)
    if (res.data) {
      // 直接在当前窗口跳转
      window.location.href = res.data
    } else {
      throw new Error('未获取到重定向地址')
    }
  } catch (error) {
    loading.value = false
    console.error("跳转失败:", error)
    ElMessage.error("跳转失败，请稍后重试")
  }
}

// 组件挂载后立即执行跳转
onMounted(() => {
  handleRedirect()
})
</script>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  flex-direction: column;
  gap: 20px;
}
</style>