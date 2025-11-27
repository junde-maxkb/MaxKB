<template>
  <login-layout v-if="!loading" v-loading="loading">
    <LoginContainer>
      <h2 class="login-title" v-if="!showQrCodeTab">{{ loginMode || '登录' }}</h2>
      <p class="login-subtitle" v-if="!showQrCodeTab">{{ user.themeInfo?.slogan || $t('views.system.theme.defaultSlogan') }}</p>
      <div v-if="!showQrCodeTab" class="login-form-wrapper">
        <el-form
          class="login-form"
          :rules="rules"
          :model="loginForm"
          ref="loginFormRef"
          @keyup.enter="login"
        >
          <div class="mb-24">
            <el-form-item prop="username">
              <el-input
                size="large"
                class="input-item"
                v-model="loginForm.username"
                :placeholder="$t('views.user.userForm.form.username.placeholder')"
                :prefix-icon="User"
              >
              </el-input>
            </el-form-item>
          </div>
          <div class="mb-24">
            <el-form-item prop="password">
              <el-input
                type="password"
                size="large"
                class="input-item"
                v-model="loginForm.password"
                :placeholder="$t('views.user.userForm.form.password.placeholder')"
                show-password
                :prefix-icon="Lock"
              >
              </el-input>
            </el-form-item>
          </div>
        </el-form>

        <el-button size="large" type="primary" class="login-btn w-full" @click="login">
          <span class="login-btn-text">{{ $t('views.login.buttons.login') }}</span>
        </el-button>
        <div class="operate-container flex-between mt-16">
          <el-button class="register" @click="router.push('/oauth_login/')" link type="primary">
            教科院统一认证登录
          </el-button>
          <el-button
            class="forgot-password"
            @click="router.push('/forgot_password')"
            link
            type="primary"
          >
            {{ $t('views.login.forgotPassword') }}?
          </el-button>
        </div>
      </div>
      <div v-if="showQrCodeTab">
        <QrCodeTab :tabs="orgOptions" />
      </div>

      <div class="login-gradient-divider lighter mt-24" v-if="modeList.length > 1">
        <span>{{ $t('views.login.moreMethod') }}</span>
      </div>
      <div class="text-center mt-16">
        <template v-for="item in modeList">
          <el-button
            v-if="item !== '' && loginMode !== item && item !== 'QR_CODE'"
            circle
            :key="item"
            class="login-button-circle color-secondary"
            @click="changeMode(item)"
          >
            <span
              :style="{
                'font-size': item === 'OAUTH2' ? '8px' : '10px',
                color: user.themeInfo?.theme
              }"
              >{{ item }}</span
            >
          </el-button>
          <el-button
            v-if="item === 'QR_CODE' && loginMode !== item"
            circle
            :key="item"
            class="login-button-circle color-secondary"
            @click="changeMode('QR_CODE')"
          >
            <img src="@/assets/icon_qr_outlined.svg" width="25px" />
          </el-button>
          <el-button
            v-if="item === '' && loginMode !== ''"
            circle
            :key="item"
            class="login-button-circle color-secondary"
            style="font-size: 24px"
            icon="UserFilled"
            @click="changeMode('')"
          />
        </template>
      </div>
    </LoginContainer>
  </login-layout>
</template>
<script setup lang="ts">
import { onMounted, ref, onBeforeMount } from 'vue'
import { User, Lock } from '@element-plus/icons-vue'
import type { LoginRequest } from '@/api/type/user'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import useStore from '@/stores'
import authApi from '@/api/auth-setting'
import { MsgConfirm, MsgError, MsgSuccess } from '@/utils/message'

import { t, getBrowserLang } from '@/locales'
import QrCodeTab from '@/views/login/components/QrCodeTab.vue'
import { useI18n } from 'vue-i18n'
import * as dd from 'dingtalk-jsapi'
import { loadScript } from '@/utils/utils'
const { locale } = useI18n({ useScope: 'global' })
const loading = ref<boolean>(false)
const { user } = useStore()
const router = useRouter()
const loginForm = ref<LoginRequest>({
  username: '',
  password: ''
})

const rules = ref<FormRules<LoginRequest>>({
  username: [
    {
      required: true,
      message: t('views.user.userForm.form.username.requiredMessage'),
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: t('views.user.userForm.form.password.requiredMessage'),
      trigger: 'blur'
    }
  ]
})
const loginFormRef = ref<FormInstance>()

const modeList = ref<string[]>([''])
const QrList = ref<any[]>([''])
const loginMode = ref('')
const showQrCodeTab = ref(false)

interface qrOption {
  key: string
  value: string
}

const orgOptions = ref<qrOption[]>([])

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

function redirectAuth(authType: string) {
  if (authType === 'LDAP' || authType === '') {
    return
  }
  authApi.getAuthSetting(authType, loading).then((res: any) => {
    if (!res.data) {
      return
    }
    MsgConfirm(t('views.login.jump_tip'), '', {
      confirmButtonText: t('views.login.jump'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: ''
    })
      .then(() => {
        if (!res.data.config_data) {
          return
        }
        const config = res.data.config_data
        const redirectUrl = eval(`\`${config.redirectUrl}\``)
        let url
        if (authType === 'CAS') {
          url = config.ldpUri
          if (url.indexOf('?') !== -1) {
            url = `${config.ldpUri}&service=${encodeURIComponent(redirectUrl)}`
          } else {
            url = `${config.ldpUri}?service=${encodeURIComponent(redirectUrl)}`
          }
        }
        if (authType === 'OIDC') {
          const scope = config.scope || 'openid+profile+email'
          url = `${config.authEndpoint}?client_id=${config.clientId}&redirect_uri=${redirectUrl}&response_type=code&scope=${scope}`
          if (config.state) {
            url += `&state=${config.state}`
          }
        }
        if (authType === 'OAuth2') {
          url =
            `${config.authEndpoint}?client_id=${config.clientId}&response_type=code` +
            `&redirect_uri=${redirectUrl}&state=${uuidv4()}`
          if (config.scope) {
            url += `&scope=${config.scope}`
          }
        }
        if (url) {
          window.location.href = url
        }
      })
      .catch(() => {})
  })
}

function changeMode(val: string) {
  loginMode.value = val === 'LDAP' ? val : ''
  if (val === 'QR_CODE') {
    loginMode.value = val
    showQrCodeTab.value = true
    return
  }
  showQrCodeTab.value = false
  loginForm.value = {
    username: '',
    password: ''
  }
  redirectAuth(val)
  loginFormRef.value?.clearValidate()
}

const login = () => {
  loginFormRef.value?.validate().then(() => {
    loading.value = true
    user
      .login(loginMode.value, loginForm.value.username, loginForm.value.password)
      .then(() => {
        locale.value = localStorage.getItem('MaxKB-locale') || getBrowserLang() || 'en-US'
        router.push({ name: 'application' })
      })
      .finally(() => (loading.value = false))
  })
}

onBeforeMount(() => {
  loading.value = true
  user.asyncGetProfile().then((res) => {
    if (user.isEnterprise()) {
      user
        .getAuthType()
        .then((res) => {
          //如果结果包含LDAP，把LDAP放在第一个
          const ldapIndex = res.indexOf('LDAP')
          if (ldapIndex !== -1) {
            const [ldap] = res.splice(ldapIndex, 1)
            res.unshift(ldap)
          }
          modeList.value = [...modeList.value, ...res]
        })
        .finally(() => (loading.value = false))
      user
        .getQrType()
        .then((res) => {
          if (res.length > 0) {
            modeList.value = ['QR_CODE', ...modeList.value]
            QrList.value = res
            QrList.value.forEach((item) => {
              orgOptions.value.push({
                key: item,
                value:
                  item === 'wecom'
                    ? t('views.system.authentication.scanTheQRCode.wecom')
                    : item === 'dingtalk'
                      ? t('views.system.authentication.scanTheQRCode.dingtalk')
                      : t('views.system.authentication.scanTheQRCode.lark')
              })
            })
          }
        })
        .finally(() => (loading.value = false))
    } else {
      loading.value = false
    }
  })
})
declare const window: any

onMounted(() => {
  const route = useRoute()
  const currentUrl = ref(route.fullPath)
  const params = new URLSearchParams(currentUrl.value.split('?')[1])
  const client = params.get('client')

  const handleDingTalk = () => {
    const code = params.get('corpId')
    if (code) {
      dd.runtime.permission.requestAuthCode({ corpId: code }).then((res) => {
        console.log('DingTalk client request success:', res)
        user.dingOauth2Callback(res.code).then(() => {
          router.push({ name: 'home' })
        })
      })
    }
  }

  const handleLark = () => {
    const appId = params.get('appId')
    const callRequestAuthCode = () => {
      window.tt?.requestAuthCode({
        appId: appId,
        success: (res: any) => {
          user.larkCallback(res.code).then(() => {
            router.push({ name: 'home' })
          })
        },
        fail: (error: any) => {
          MsgError(error)
        }
      })
    }

    loadScript('https://lf-scm-cn.feishucdn.com/lark/op/h5-js-sdk-1.5.35.js', {
      jsId: 'lark-sdk',
      forceReload: true
    })
      .then(() => {
        if (window.tt) {
          window.tt.requestAccess({
            appID: appId,
            scopeList: [],
            success: (res: any) => {
              user.larkCallback(res.code).then(() => {
                router.push({ name: 'home' })
              })
            },
            fail: (error: any) => {
              const { errno } = error
              if (errno === 103) {
                callRequestAuthCode()
              }
            }
          })
        } else {
          callRequestAuthCode()
        }
      })
      .catch((error) => {
        console.error('SDK 加载失败:', error)
      })
  }

  switch (client) {
    case 'dingtalk':
      handleDingTalk()
      break
    case 'lark':
      handleLark()
      break
    default:
      break
  }
})
</script>
<style lang="scss" scoped>
// 主题色变量
$theme-primary: #554BDB;
$theme-primary-light: rgba(85, 75, 219, 0.1);
$theme-gradient: linear-gradient(135deg, #554BDB 0%, #7B6FE8 100%);

.login-title {
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 8px 0;
}

.login-subtitle {
  text-align: center;
  font-size: 14px;
  color: #718096;
  margin: 0 0 24px 0;
  letter-spacing: 0.5px;
}

.login-form-wrapper {
  :deep(.el-input) {
    .el-input__wrapper {
      border-radius: 10px;
      padding: 4px 15px;
      box-shadow: 0 2px 8px rgba(85, 75, 219, 0.08);
      border: 1px solid #e2e8f0;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: rgba(85, 75, 219, 0.4);
      }
      
      &.is-focus {
        border-color: $theme-primary;
        box-shadow: 0 0 0 3px rgba(85, 75, 219, 0.12);
      }
    }
    
    .el-input__prefix {
      color: $theme-primary;
      font-size: 18px;
    }
    
    .el-input__inner {
      &::placeholder {
        color: #a0aec0;
      }
    }
  }
  
  :deep(.el-form-item) {
    margin-bottom: 0;
    
    .el-form-item__error {
      padding-top: 4px;
    }
  }
}

.login-btn {
  height: 48px;
  border-radius: 10px;
  background: $theme-gradient;
  border: none;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  box-shadow: 0 4px 15px rgba(85, 75, 219, 0.35);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(85, 75, 219, 0.45);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  .login-btn-text {
    display: inline-block;
  }
}

.operate-container {
  .register,
  .forgot-password {
    color: #718096;
    font-size: 13px;
    transition: color 0.3s ease;
    
    &:hover {
      color: $theme-primary;
    }
  }
}

.login-gradient-divider {
  position: relative;
  text-align: center;
  color: #a0aec0;
  font-size: 13px;

  &::before {
    content: '';
    width: 30%;
    height: 1px;
    background: linear-gradient(90deg, rgba(85, 75, 219, 0) 0%, rgba(85, 75, 219, 0.3) 100%);
    position: absolute;
    left: 16px;
    top: 50%;
  }

  &::after {
    content: '';
    width: 30%;
    height: 1px;
    background: linear-gradient(90deg, rgba(85, 75, 219, 0.3) 0%, rgba(85, 75, 219, 0) 100%);
    position: absolute;
    right: 16px;
    top: 50%;
  }
}

.login-button-circle {
  padding: 20px !important;
  margin: 0 6px;
  width: 40px;
  height: 40px;
  text-align: center;
  border: 1px solid rgba(85, 75, 219, 0.2);
  background: #ffffff;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: $theme-primary;
    background: $theme-primary-light;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(85, 75, 219, 0.2);
  }
}
</style>
