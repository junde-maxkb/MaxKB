<template>
  <div class="loading-container">
    <p>正在跳转到统一身份认证...</p>
    <!-- 可选：加个小动画 -->
    <div class="spinner"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// ===== 请改成你自己的配置 =====
const CLIENT_ID = 'your_client_id'  // 学校给的 AppKey
const REDIRECT_URI = encodeURIComponent(
  // 重要：这里必须是你前端的完整回调地址，且已在学校后台白名单！
  `${window.location.origin}/oauth/callback`
)
const SSO_AUTHORIZE_URL = 'https://sso.xxx.edu.cn/sso/oauth2/authorize'  // 改成你们学校的

onMounted(() => {
  // 1. 生成随机 state（防 CSRF）
  const state = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
  localStorage.setItem('oauth_state', state)

  // 2. 可选：生成 nonce（防重放攻击，OIDC 推荐）
  const nonce = Math.random().toString(36).substring(2)
  localStorage.setItem('oauth_nonce', nonce)

  // 3. 直接前端跳转（最丝滑！）
  const authUrl = `${SSO_AUTHORIZE_URL}?` + new URLSearchParams({
    response_type: 'code',
    client_id: CLIENT_ID,
    redirect_uri: REDIRECT_URI,
    scope: 'openid',                   // 必须包含 openid 才能拿到 id_token 和 account
    state,
    nonce,                             // 可选，但建议带上
    // prompt: 'login',                // 强制显示登录页（可选，调试用）
  })

  window.location.href = authUrl
})
</script>

<style scoped>
.loading-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 20px;
  background: #f5f7fa;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #409eff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>