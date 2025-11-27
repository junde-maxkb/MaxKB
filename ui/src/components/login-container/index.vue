<template>
  <div class="login-form-container">
    <el-card class="login-card" shadow="hover">
      <slot></slot>
    </el-card>
  </div>
</template>
<script setup lang="ts">
defineOptions({ name: 'LoginContainer' })
defineProps({
  title: String
})
</script>
<style lang="scss" scoped>
// 主题色变量
$theme-primary: #554BDB;
$theme-gradient: linear-gradient(135deg, #554BDB 0%, #7B6FE8 100%);

.login-form-container {
  width: 440px;
  animation: fadeInUp 0.6s ease-out;

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .login-card {
    border-radius: 16px;
    padding: 32px 24px;
    border: none;
    background: #ffffff;
    box-shadow: 0 10px 40px rgba(85, 75, 219, 0.1), 
                0 2px 10px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 15px 50px rgba(85, 75, 219, 0.15), 
                  0 5px 15px rgba(0, 0, 0, 0.08);
    }
    
    :deep(.el-card__body) {
      padding: 0;
    }
  }
}
</style>
