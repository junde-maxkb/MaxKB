<template>
  <div class="login-warp">
    <div class="top-logo">
      <img src="@/assets/JKY.png" alt="JKY" class="logo-img" />
    </div>
    <div class="login-container">
      <el-dropdown trigger="click" type="primary" class="lang" v-if="lang">
            <template #dropdown>
              <el-dropdown-menu style="width: 180px">
                <el-dropdown-item
                  v-for="(lang, index) in langList"
                  :key="index"
                  :value="lang.value"
                  @click="changeLang(lang.value)"
                  class="flex-between"
                >
                  <span :class="lang.value === user.getLanguage() ? 'primary' : ''">{{
                    lang.label
                  }}</span>

                  <el-icon
                    :class="lang.value === user.getLanguage() ? 'primary' : ''"
                    v-if="lang.value === user.getLanguage()"
                  >
                    <Check />
                  </el-icon>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
            <el-button>
              {{ currentLanguage }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
          </el-dropdown>
      <slot></slot>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import useStore from '@/stores'
import { useLocalStorage } from '@vueuse/core'
import { langList, localeConfigKey, getBrowserLang } from '@/locales/index'
defineProps({
  lang: {
    type: Boolean,
    default: true
  }
})
defineOptions({ name: 'LoginLayout' })
const { user } = useStore()

const changeLang = (lang: string) => {
  useLocalStorage(localeConfigKey, getBrowserLang()).value = lang
  window.location.reload()
}

const currentLanguage = computed(() => {
  return langList.value?.filter((v: any) => v.value === user.getLanguage())?.[0]?.label
})
</script>
<style lang="scss" scoped>
// 主题色变量
$theme-primary: #554BDB;

.login-warp {
  height: 100vh;
  width: 100vw;
  background: url('https://passport.cnaes.edu.cn/sso/resources/kJUVDCyn1O/static/img/pc-bg.331da7e.png') no-repeat center center;
  background-size: 100% auto;
  position: relative;
  display: flex;
  justify-content: flex-end;
  align-items: center;

  .top-logo {
    position: absolute;
    left: 40px;
    top: 32px;
    z-index: 10;
    
    .logo-img {
      height: 80px;
      filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.15));
    }
  }

  .login-container {
    position: relative;
    width: 50%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background: transparent;
  }
  
  .lang {
    position: absolute;
    right: 24px;
    top: 24px;
    z-index: 10;
    
    :deep(.el-button) {
      border-radius: 8px;
      border-color: rgba(85, 75, 219, 0.2);
      background: rgba(255, 255, 255, 0.9);
      color: $theme-primary;
      
      &:hover {
        border-color: $theme-primary;
        background: rgba(255, 255, 255, 1);
      }
    }
  }
}
</style>
