<template>
  <el-dialog
    :title="$t('views.dataset.createDataset')"
    v-model="dialogVisible"
    width="720"
    append-to-body
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <!-- 基本信息 -->
    <BaseForm ref="BaseFormRef" v-if="dialogVisible" />
    <el-form
      ref="DatasetFormRef"
      :rules="rules"
      :model="datasetForm"
      label-position="top"
      require-asterisk-position="right"
    >
      <el-form-item v-if="datasetTypes.length > 1" :label="$t('views.dataset.datasetForm.form.datasetType.label')">
        <el-radio-group v-model="datasetForm.type" class="card__radio" @change="radioChange">
          <el-row :gutter="20">
            <el-col :span="24">
              <el-card
                shadow="never"
                class="mb-16"
                :class="datasetForm.type === '0' ? 'active' : ''"
                @click="datasetForm.type = '0'"
              >
                <div class="flex-between">
                  <div class="flex align-center">
                    <AppAvatar class="mr-8 avatar-blue" shape="square" :size="32">
                      <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                    </AppAvatar>
                    <div>
                      <p>
                        <el-text>{{ $t('views.dataset.general') }}</el-text>
                      </p>
                      <el-text type="info">{{
                        $t('views.dataset.datasetForm.form.datasetType.generalInfo')
                      }}</el-text>
                    </div>
                  </div>
                  <el-radio value="0" size="large" style="width: 16px"></el-radio>
                </div>
              </el-card>
            </el-col>
            <el-col :span="24">
              <el-card
                shadow="never"
                class="mb-16"
                :class="datasetForm.type === '1' ? 'active' : ''"
                @click="datasetForm.type = '1'"
              >
                <div class="flex-between">
                  <div class="flex align-center">
                    <AppAvatar class="mr-8 avatar-green" shape="square" :size="32">
                      <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                    </AppAvatar>
                    <div>
                      <p>
                        <el-text>{{ $t('views.dataset.web') }}</el-text>
                      </p>
                      <el-text type="info">{{
                        $t('views.dataset.datasetForm.form.datasetType.webInfo')
                      }}</el-text>
                    </div>
                  </div>
                  <el-radio value="1" size="large" style="width: 16px"></el-radio>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-radio-group>
      </el-form-item>
      
      <!-- WEB类型的额外字段 -->
      <div v-if="datasetForm.type === '1'">
        <el-form-item 
          :label="$t('views.dataset.datasetForm.form.source_url.label')" 
          prop="source_url"
        >
          <el-input
            v-model="datasetForm.source_url"
            :placeholder="$t('views.dataset.datasetForm.form.source_url.placeholder')"
          />
        </el-form-item>
        
        <el-form-item 
          :label="$t('views.dataset.datasetForm.form.selector.label')" 
          prop="selector"
        >
          <el-input
            v-model="datasetForm.selector"
            :placeholder="$t('views.dataset.datasetForm.form.selector.placeholder')"
          />
        </el-form-item>
      </div>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submitHandle" :loading="loading">
          {{ $t('common.confirm') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BaseForm from './BaseForm.vue'
import datasetApi from '@/api/dataset'
import { MsgSuccess, MsgAlert } from '@/utils/message'
import { t } from '@/locales'
import { ComplexPermission } from '@/utils/permission/type'
const emit = defineEmits(['refresh'])

const router = useRouter()
const BaseFormRef = ref()
const DatasetFormRef = ref()

const loading = ref(false)
const dialogVisible = ref<boolean>(false)

const datasetForm = ref({
  type: '0',
  source_url: '',
  selector: ''
})
// 当前可用类型列表（恢复多类型支持）
const datasetTypes = ref([
  { value: '0', label: t('views.dataset.general') },
  { value: '1', label: t('views.dataset.web') }
])

const rules = reactive({
  source_url: [
    {
      required: true,
      message: t('views.dataset.datasetForm.form.source_url.requiredMessage'),
      trigger: 'blur'
    }
  ],
  app_id: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appIdPlaceholder'),
      trigger: 'blur'
    }
  ],
  app_secret: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.appSecretPlaceholder'),
      trigger: 'blur'
    }
  ],
  folder_token: [
    {
      required: true,
      message: t('views.application.applicationAccess.larkSetting.folderTokenPlaceholder'),
      trigger: 'blur'
    }
  ],
  user_id: [
    {
      required: true,
      message: t('views.dataset.datasetForm.form.user_id.requiredMessage'),
      trigger: 'blur'
    }
  ],
  token: [
    {
      required: true,
      message: t('views.dataset.datasetForm.form.token.requiredMessage'),
      trigger: 'blur'
    }
  ]
})

watch(dialogVisible, (bool) => {
  if (!bool) {
    datasetForm.value = {
      type: '0',
      source_url: '',
      selector: ''
    }
    DatasetFormRef.value?.clearValidate()
  }
})

const open = () => {
  dialogVisible.value = true
}

const submitHandle = async () => {
  if (await BaseFormRef.value?.validate()) {
    await DatasetFormRef.value.validate((valid: any) => {
      if (valid) {
        if (datasetForm.value.type === '0') {
          const obj = {
            ...BaseFormRef.value.form,
            type: datasetForm.value.type
          }
          datasetApi.postDataset(obj, loading).then((res) => {
            MsgSuccess(t('common.createSuccess'))
            router.push({ path: `/dataset/${res.data.id}/document` })
            emit('refresh')
          })
        } else if (datasetForm.value.type === '1') {
          const obj = { ...BaseFormRef.value.form, ...datasetForm.value }
          datasetApi.postWebDataset(obj, loading).then((res) => {
            MsgSuccess(t('common.createSuccess'))
            router.push({ path: `/dataset/${res.data.id}/document` })
            emit('refresh')
          })
        } else if (datasetForm.value.type === '2') {
          const obj = { ...BaseFormRef.value.form, ...datasetForm.value }
          datasetApi.postLarkDataset(obj, loading).then((res) => {
            MsgSuccess(t('common.createSuccess'))
            router.push({ path: `/dataset/${res.data.id}/document` })
            emit('refresh')
          })
        }
      } else {
        return false
      }
    })
  } else {
    return false
  }
}
function radioChange() {
  datasetForm.value.source_url = ''
  datasetForm.value.selector = ''
}

defineExpose({ open })
</script>
<style lang="scss" scoped></style>
