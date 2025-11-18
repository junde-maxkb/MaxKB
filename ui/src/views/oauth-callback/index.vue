<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import UserApi from '@/api/user'


const router = useRouter()

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const code = params.get('code')
  const state = params.get('state')
  const error = params.get('error')

  // 错误处理
  if (error || !code || !state) {
    ElMessage.error('登录失败：' + (params.get('error_description') || '参数缺失'))
    router.push('/login')
    return
  }

  // state 校验（防 CSRF）
  const savedState = localStorage.getItem('oauth_state')
  if (state !== savedState) {
    ElMessage.error('登录失败：state 校验失败')
    router.push('/login')
    return
  }

  try {
    // 调用你后端的接口（我上次给你的那个）
    const res = await UserApi.oauthLogin(code)
    localStorage.setItem('token', res.data)

    ElMessage.success('登录成功！')
    router.push('/')  // 跳转首页
  } catch (err: any) {
    ElMessage.error(err.detail || '登录失败，请重试')
    router.push('/login')
  } finally {
    // 清理
    localStorage.removeItem('oauth_state')
    localStorage.removeItem('oauth_nonce')
  }
})
</script>