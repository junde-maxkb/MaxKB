<template>
    <LayoutContainer :header="$t('views.system.login_auth.title')">
      <div class="email-setting main-calc-height">
        <el-scrollbar>
          <div class="p-24" v-loading="loading">
            <el-form
              ref="loginAuthFormRef"
              :rules="rules"
              :model="form"
              label-position="top"
              require-asterisk-position="right"
            >
              <el-form-item :label="$t('views.system.login_auth.authorizedUrl')" prop="authorized_url">
                <el-input
                  v-model="form.authorized_url"
                  :placeholder="$t('views.system.login_auth.authorizedUrlPlaceholder')"
                />
              </el-form-item>
              <el-form-item :label="$t('views.system.login_auth.tokenUrl')" prop="token_url">
                <el-input
                  v-model="form.token_url"
                  :placeholder="$t('views.system.login_auth.tokenUrlPlaceholder')"
                />
              </el-form-item>
              <el-form-item :label="$t('views.system.login_auth.userInfoUrl')" prop="user_info_url">
                <el-input
                  v-model="form.user_info_url"
                  :placeholder="$t('views.system.login_auth.userInfoUrlPlaceholder')"
                />
              </el-form-item>
              <el-form-item :label="$t('views.system.login_auth.connectRange')" prop="connect_range">
                <el-input
                  v-model="form.connect_range"
                  :placeholder="$t('views.system.login_auth.connectRangePlaceholder')"
                />
              </el-form-item>
              <el-form-item :label="$t('views.system.login_auth.clientId')" prop="client_id">
                <el-input
                  v-model="form.client_id"
                  :placeholder="$t('views.system.login_auth.clientIdPlaceholder')"

                />
              </el-form-item>
              <el-form-item :label="$t('views.system.login_auth.clientSecret')" prop="client_secret">
                <el-input
                  v-model="form.client_secret"
                  :placeholder="$t('views.system.login_auth.clientSecretPlaceholder')"
                  show-password
                />
              </el-form-item>
              <el-form-item :label="$t('views.system.login_auth.callBackUrl')" prop="callback_url">
                <el-input
                  v-model="form.callback_url"
                  :placeholder="$t('views.system.login_auth.callBackUrlPlaceholder')"
                />
              </el-form-item>
              <el-form-item :label="$t('views.system.login_auth.fieldMap')" prop="field_map">
                <el-input
                  v-model="form.field_map"
                  :placeholder="$t('views.system.login_auth.fieldMapPlaceholder')"
                />
              </el-form-item>
              <el-form-item>
                <el-checkbox v-model="form.enable_oauth2"
                  >{{ $t('views.system.login_auth.enableOauth2') }}
                </el-checkbox>
              </el-form-item>
              <!-- <el-button @click="submit(loginAuthFormRef, 'test')" :disabled="loading">
                {{ $t('views.system.test') }}
              </el-button> -->
            </el-form>
  
            <div class="text-right">
              <el-button @click="submit(loginAuthFormRef)" type="primary" :disabled="loading">
                {{ $t('common.save') }}
              </el-button>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </LayoutContainer>
  </template>
  <script setup lang="ts">
  import { reactive, ref, watch, onMounted } from 'vue'
  import emailApi from '@/api/login_auth_setting'
  import type { FormInstance, FormRules } from 'element-plus'
  
  import { MsgSuccess,MsgError} from '@/utils/message'
  import { t } from '@/locales'
  
  const form = ref<any>({
    authorized_url: '',
    token_url: '',
    user_info_url: '',
    connect_range: '',
    client_id: '',
    client_secret: '',
    callback_url: '',
    field_map: '',
    enable_oauth2: false
  })
  
  const loginAuthFormRef = ref()
  
  const loading = ref(false)
  
  const rules = reactive<FormRules<any>>({
    authorized_url: [
      { required: true, message: t('views.system.login_auth.authorizedUrlPlaceholder'), trigger: 'blur' }
    ],
    token_url: [
      { required: true, message: t('views.system.login_auth.tokenUrlPlaceholder'), trigger: 'blur' }
    ],
    user_info_url: [
      { required: true, message: t('views.system.login_auth.userInfoUrlPlaceholder'), trigger: 'blur' }
    ],
    connect_range: [
      { required: true, message: t('views.system.login_auth.connectRangePlaceholder'), trigger: 'blur' }
    ],
    client_id: [
      { required: true, message: t('views.system.login_auth.clientIdPlaceholder'), trigger: 'blur' }
    ],
    client_secret: [
      { required: true, message: t('views.system.login_auth.clientSecretPlaceholder'), trigger: 'blur' }
    ],
    callback_url: [
      { required: true, message: t('views.system.login_auth.callBackUrlPlaceholder'), trigger: 'blur' }
    ],
    field_map: [
      { required: true, message: t('views.system.login_auth.fieldMapPlaceholder'), trigger: 'blur' }
    ]
  })
  
  const submit = async (formEl: FormInstance) => {
    if (!formEl) return
    await formEl.validate((valid, fields) => {
      if (valid) {

          emailApi.putLoginAuthSetting(form.value, loading).then((res) => {
            console.log("res",res)
            if (res.code == 200){
              MsgSuccess(t('common.saveSuccess'))
              if (form.value.enable_oauth2){
                window.location.href = res.data.auth_url
              }
              // window.location.href = res.data
            }else{
              MsgError(t('common.saveError'))
            }
            
          })
        
      }
    })
  }
  
  function getDetail() {
    emailApi.getLoginAuthSetting(loading).then((res: any) => {
      if (res.data && JSON.stringify(res.data) !== '{}') {
        form.value = res.data
      }
    })
  }
  
  onMounted(() => {
    getDetail()
  })
  </script>
  <style lang="scss" scoped>
  .email-setting {
    width: 70%;
    margin: 0 auto;
  
    :deep(.el-checkbox__label) {
      font-weight: 400;
    }
  }
  </style>
  