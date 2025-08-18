<template>
  <el-form
    ref="FormRef"
    :model="form"
    :rules="rules"
    label-position="top"
    require-asterisk-position="right"
    v-loading="loading"
  >
    <el-form-item :label="$t('views.dataset.datasetForm.form.datasetName.label')" prop="name">
      <el-input
        v-model="form.name"
        :placeholder="$t('views.dataset.datasetForm.form.datasetName.placeholder')"
        maxlength="64"
        show-word-limit
        @blur="form.name = form.name.trim()"
      />
    </el-form-item>
    <el-form-item
      :label="$t('views.dataset.datasetForm.form.datasetDescription.label')"
      prop="desc"
    >
      <el-input
        v-model="form.desc"
        type="textarea"
        :placeholder="$t('views.dataset.datasetForm.form.datasetDescription.placeholder')"
        maxlength="256"
        show-word-limit
        :autosize="{ minRows: 3 }"
        @blur="form.desc = form.desc.trim()"
      />
    </el-form-item>
    <!-- 向量模型固定为默认（maxkb-embedding），前端不展示选择 -->
    <el-form-item v-if="false"
      :label="$t('views.dataset.datasetForm.form.EmbeddingModel.label')"
      prop="embedding_mode_id"
    >
      <ModelSelect
        v-model="form.embedding_mode_id"
        :placeholder="$t('views.dataset.datasetForm.form.EmbeddingModel.placeholder')"
        :options="modelOptions"
        :model-type="'EMBEDDING'"
        showFooter
      ></ModelSelect>
    </el-form-item>
  </el-form>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { groupBy } from 'lodash'
import useStore from '@/stores'
import type { datasetData } from '@/api/type/dataset'
import { t } from '@/locales'
const props = defineProps({
  data: {
    type: Object,
    default: () => {}
  }
})
const { model } = useStore()
const form = ref<datasetData>({
  name: '',
  desc: '',
  embedding_mode_id: ''
})

const rules = reactive({
  name: [
    {
      required: true,
      message: t('views.dataset.datasetForm.form.datasetName.requiredMessage'),
      trigger: 'blur'
    }
  ],
  desc: [
    {
      required: true,
      message: t('views.dataset.datasetForm.form.datasetDescription.requiredMessage'),
      trigger: 'blur'
    }
  ],
  // 向量模型固定为默认，不再校验用户选择
})

const FormRef = ref()
const loading = ref(false)
const modelOptions = ref<any>([])

watch(
  () => props.data,
  (value) => {
    if (value && JSON.stringify(value) !== '{}') {
      form.value.name = value.name
      form.value.desc = value.desc
      form.value.embedding_mode_id = value.embedding_mode_id
    }
  },
  {
    immediate: true
  }
)
/*
  表单校验
*/
function validate() {
  if (!FormRef.value) return
  return FormRef.value.validate((valid: any) => {
    return valid
  })
}

function getModel() {
  loading.value = true
  model
    .asyncGetModel({ model_type: 'EMBEDDING' })
    .then((res: any) => {
      // 自动选择名为 maxkb-embedding 的模型作为默认
      const list = res?.data || []
      const def = list.find((m: any) => m?.name === 'maxkb-embedding' || m?.model_name === 'maxkb-embedding')
      if (def?.id) {
        form.value.embedding_mode_id = def.id
      } else if (list[0]?.id) {
        form.value.embedding_mode_id = list[0].id
      }
      modelOptions.value = groupBy(list, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

onMounted(() => {
  getModel()
})
onUnmounted(() => {
  form.value = {
    name: '',
    desc: '',
    embedding_mode_id: ''
  }
  FormRef.value?.clearValidate()
})

defineExpose({
  validate,
  form
})
</script>
<style scoped lang="scss"></style>
