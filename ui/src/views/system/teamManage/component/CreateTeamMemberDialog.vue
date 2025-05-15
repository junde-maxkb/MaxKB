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
        <h4 :id="titleId" :class="titleClass">{{ $t('views.teamManage.addTeamMember') }}</h4>
        <div class="dialog-sub-title">{{ $t('views.team.addSubTitle') }}</div>
      </template>
  
      <el-form
        ref="addMemberFormRef"
        :model="memberForm"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
        :rules="rules"
      >
        <el-form-item :label="$t('views.teamManage.member.teamForm.name.label')" prop="usernameOrEmail">
          <el-input
          v-model="memberForm.usernameOrEmail"
          :placeholder="$t('views.teamManage.member.teamForm.name.placeholder')"
        />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click.prevent="dialogVisible = false"> {{ $t('common.cancel') }} </el-button>
          <el-button type="primary" @click="submitMember(addMemberFormRef)" :loading="loading">
            {{ $t('common.add') }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </template>
  <script setup lang="ts">
  import { ref, watch, onMounted, reactive} from 'vue'
  import type { FormInstance, FormRules } from 'element-plus'
  import { MsgSuccess } from '@/utils/message'
  import TeamApi from '@/api/team-manage'
  import { t } from '@/locales'
  
  const emit = defineEmits(['refresh'])
  
  const dialogVisible = ref<boolean>(false)
  
  const memberForm = ref({
    usernameOrEmail: ""
  })
  
  const addMemberFormRef = ref<FormInstance>()
  const loading = ref<boolean>(false)
  const teamLoading = ref<boolean>(false)
  const userLoading = ref<boolean>(false)
  const teamId = ref('')
  const teamOptions = ref<any[]>([])
  const userOptions = ref<any[]>([])
  
  const rules = reactive<FormRules<any>>({
      usernameOrEmail: [
        { required: true, message: t('views.teamManage.member.teamForm.name.requiredMessage'), trigger: 'blur' }
      ]
    })
  
  watch(dialogVisible, (bool) => {
    if (!bool) {
      memberForm.value = {
        usernameOrEmail: ""
      }
      loading.value = false
    }
  })
  
  // Fetch initial teams when dialog opens
  const open = async (row:any) => {
    teamId.value = row
    dialogVisible.value = true
  }
  
 
  
  const submitMember = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate((valid, fields) => {
      if (valid) {
        loading.value = true
        TeamApi.CreateTeamMember({
          team_id: teamId.value,
          // usernameOrEmail: memberForm.value.usernameOrEmail
          username_or_email: memberForm.value.usernameOrEmail
        })
          .then((res) => {
            MsgSuccess(t('common.submitSuccess'))
            emit('refresh', res.data)
            dialogVisible.value = false
          })
          .catch(() => {
            loading.value = false
          })
      }
    })
  }
  
  defineExpose({ open })
  </script>
  <style lang="scss" scoped>
  .member-dialog {
    .el-dialog__header {
      padding-bottom: 19px;
    }
    
    .el-select {
      width: 100%;
    }
  }
  </style>