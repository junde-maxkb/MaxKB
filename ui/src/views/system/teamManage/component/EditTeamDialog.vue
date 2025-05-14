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
        <h4 :id="titleId" :class="titleClass">{{ $t('views.teamManage.EditTeam') }}</h4>
        <!-- <div class="dialog-sub-title">{{ $t('views.team.addSubTitle') }}</div> -->
      </template>
  
      <el-form
        ref="addMemberFormRef"
        :model="memberForm"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
        :rules="rules"
      >
        <el-form-item :label="$t('views.teamManage.teamForm.name.label')" prop="team_name">
          <!-- <tags-input v-model:tags="memberForm.users" :placeholder="$t('views.system.team_manage.teamForm.form.team.placeholder')" /> -->
          <el-input
          v-model="memberForm.team_name"
          :placeholder="$t('views.teamManage.teamForm.name.placeholder')"
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
  import { ref, watch, onMounted, reactive } from 'vue'
  import type { FormInstance, FormRules } from 'element-plus'
  import { MsgSuccess } from '@/utils/message'
  import TeamApi from '@/api/team-manage'
  import { t } from '@/locales'
  const emit = defineEmits(['refresh'])
  
  const dialogVisible = ref<boolean>(false)
  
  const memberForm = ref({
    team_name: ""
  })
  
  const addMemberFormRef = ref<FormInstance>()
  const dialogData = ref<any>(null);
  const loading = ref<boolean>(false)
  
  const rules = reactive<FormRules<any>>({
    team_name: [
      { required: true, message: t('views.teamManage.teamForm.name.requiredMessage'), trigger: 'blur' }
    ]
  })
  
  watch(dialogVisible, (bool) => {
    if (!bool) {
      memberForm.value = {
        team_name: ""
      }
      loading.value = false
    }
  })
  
  const open = (rowData: any) => {
    dialogData.value = rowData; 
    dialogVisible.value = true;
  };
  const submitMember = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate((valid, fields) => {
      if (valid) {
        loading.value = true
        TeamApi.updateTeam(dialogData.value,{"team_name":memberForm.value.team_name})
          .then((res) => {
            MsgSuccess(t('common.submitSuccess'))
            emit('refresh', [])
            dialogVisible.value = false
            loading.value = false
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
      padding-top: 8px;
    }
    .el-input__wrapper {
      align-items: start;
    }
  }
  </style>
  