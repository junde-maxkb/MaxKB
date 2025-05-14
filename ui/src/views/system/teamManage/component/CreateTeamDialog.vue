<template>
  <el-dialog
    v-model="dialogVisible"
    :close-on-press-escape="false"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    width="600"
    class="member-dialog"
  >
    <template #header="{ titleId, titleClass }">
      <h4 :id="titleId" :class="titleClass">{{ $t('views.teamManage.addTeam') }}</h4>
      <div class="dialog-sub-title">{{ $t('views.teamManage.addSubTitle') }}</div>
    </template>

    <el-form
      ref="addTeamFormRef"
      :model="teamForm"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
      :rules="rules"
    >
      <el-form-item :label="$t('views.teamManage.teamForm.name.label')" prop="team_name">
        <el-input
          v-model="teamForm.team_name"
          :placeholder="$t('views.teamManage.teamForm.name.placeholder')"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
        <el-button type="primary" @click="submitTeam(addTeamFormRef)" :loading="loading">
          {{ $t('common.add') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, onMounted, reactive } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { MsgSuccess, MsgError } from '@/utils/message'
import TeamApi from '@/api/team-manage'
import { t } from '@/locales'
const emit = defineEmits(['refresh'])

const dialogVisible = ref<boolean>(false)

const teamForm = ref({
  team_name: ""
})

const addTeamFormRef = ref<FormInstance>()

const loading = ref<boolean>(false)

const rules = reactive<FormRules<any>>({
    team_name: [
      { required: true, message: t('views.teamManage.teamForm.name.requiredMessage'), trigger: 'blur' }
    ]
  })
watch(dialogVisible, (bool) => {
  if (!bool) {
    teamForm.value = {
      team_name: ""
    }
    loading.value = false
  }
})

const open = () => {
  dialogVisible.value = true
}
const submitTeam = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      loading.value = true
      // let idsArray = teamForm.value.name.map((obj: any) => obj.id)
      TeamApi.CreateTeam(teamForm.value)
        .then((res) => {
          if (res.code == 200){
            MsgSuccess(t('common.submitSuccess'))
            emit('refresh', [])
            dialogVisible.value = false
            loading.value = false
          }else{
            MsgError(res.message)
            dialogVisible.value = false
            loading.value = false
          }
          
        })
        .catch(() => {
          loading.value = false
        })
    }
  })
}

onMounted(() => {})

defineExpose({ open, close })
</script>
<style lang="scss" scoped>
.member-dialog {
  .el-dialog__header {
    padding-bottom: 19px;
  }
}
.custom-select-multiple {
  width: 200%;
  .el-input {
    min-height: 100px;
  }
  .el-select__tags {
    top: 0;
    transform: none;
    padding-top: 0px;
  }
  .el-input__wrapper {
    align-items: start;
  }
}
</style>
