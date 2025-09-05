<template>
    <div class="p-24">
      <div class="submit-button" style="display: inline-block; float:right">
          <el-button 
          type="primary" 
          @click="createTeamMember"
          :disabled="memberType === 'member'"
          >{{ $t('views.teamManage.member.addMember') }}</el-button>
        </div>
      <el-input
        v-model="searchValue"
        @change="searchHandle"
        :placeholder="$t('common.search')"
        prefix-icon="Search"
        class="w-240"
        clearable
        style="display: inline-block; float:right"
      />
      <app-table
        class="mt-16"
        :max-height="tableHeight"
        :data="tableData"
        :pagination-config="paginationConfig"
        @sizeChange="handleSizeChange"
        @changePage="getMemberPageList"
        v-loading="loading"
        style="padding-top: 1%;"
      >
        <el-table-column prop="username" :label="$t('views.user.userForm.form.username.label')" />
        <!-- <el-table-column prop="nick_name" :label="$t('views.user.userForm.form.nick_name.label')" /> -->
        <el-table-column
          prop="email"
          :label="$t('views.user.userForm.form.email.label')"
          show-overflow-tooltip
        />
        <el-table-column prop="team_member_type" :label="$t('views.teamManage.team_member_type.label')">
          <template #default="{ row }">
            {{
              row.team_member_type === 'member'
                ? $t('views.teamManage.team_member_type.member')
                : row.team_member_type === 'manager'
                  ? $t('views.teamManage.team_member_type.manager')
                  : row.team_member_type === 'admin'
                    ? $t('views.teamManage.team_member_type.admin')
                    : row.team_member_type === 'member'
            }}
          </template>
        </el-table-column>

        <el-table-column :label="$t('common.operation')" width="150" align="left" fixed="right">
          <template #default="{ row }">
            <span class="mr-4">
              <el-tooltip effect="dark" 
              :content="row.team_member_type === 'member' 
              ? $t('views.teamManage.setting.setTeamManager') 
              : $t('views.teamManage.setting.cancelTeamManager')" 
               placement="top">
                <el-button type="primary" 
                :disabled="memberType === 'member' || row.team_member_type === 'admin' || row.user_id === user.userInfo?.id"
                text @click.stop="setTeamManager(row)">
                  <el-icon><User /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
            <span class="mr-4"></span>
            <span class="mr-4">
              <el-tooltip effect="dark" :content="$t('common.delete')" placement="top">
                <el-button
                  :disabled="memberType === 'member' || row.team_member_type === 'admin'"
                  type="primary"
                  text
                  @click.stop="deleteTeamMemberHandle(row)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </span>
          </template>
        </el-table-column>
      </app-table>
    </div>
    <CreateTeamMemberDialog ref="CreateTeamMemberRef" @refresh="refresh" />
</template>
<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { MsgSuccess, MsgConfirm, MsgAlert, MsgError} from '@/utils/message'
import teamApi from '@/api/team-manage'
import useStore from '@/stores'
import CreateTeamMemberDialog from './CreateTeamMemberDialog.vue'
import { t } from '@/locales'

const CreateTeamMemberRef = ref<InstanceType<typeof CreateTeamMemberDialog>>()
const { common, user } = useStore()


const loading = ref(false)
const paginationConfig = reactive({
  current_page: 1,
  page_size: 20,
  total: 0
})
const tableData = ref<any[]>([])
const searchValue = ref('')
const teamId = ref('')
const memberType = ref('')
const props = defineProps({
  tableHeight: Number
})
function searchHandle() {
  paginationConfig.total = 0
  paginationConfig.current_page = 1
  tableData.value = []
  getList(teamId.value)
}
function createTeamMember(row: any) {
  CreateTeamMemberRef.value?.open(teamId.value)
}
function changeState(bool: Boolean, row: any) {
  const obj = {
    is_active: bool
  }
  const str = bool ? t('common.status.enableSuccess') : t('common.status.disableSuccess')
  teamApi.setAdminManage(row.id, obj).then((res: any) => {
    getList(teamId.value)
    MsgSuccess(str)
  })
}




function deleteTeamMemberHandle(row: any) {
  MsgConfirm(
    `${t('views.teamManage.member.delete.confirmTitle')}${row.username} ?`,
    t('views.teamManage.member.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      loading.value = true
      teamApi.deleteTeamMember(row.id).then((res) => {
        if (res.code == 200){
          MsgSuccess(t('common.deleteSuccess'))
        
          getList(teamId.value)
          loading.value = false
        }else{
          MsgError(res.message)
        }
        
      })
    })
    .catch(() => {})
}

function setTeamManager(row: any) {
  let is_manager = true
  let ConfirmTitle = ""
  let ConfirmMessage = ""
  let ButtonText = ""
  let ButtonClass = ""
  let TeamManagerFailed = ""
  let TeamManagerSuccess = ""
  if (row.team_member_type == "member"){
    is_manager = true
    ConfirmTitle = 'views.teamManage.setTeamManager.setConfirmTitle'
    ConfirmMessage = 'views.teamManage.setTeamManager.setConfirmMessage'
    ButtonText = "views.teamManage.setting.setTeamManager"
    ButtonClass = "danger"
    TeamManagerSuccess = "views.teamManage.setTeamManager.setTeamManagerSuccess"
    TeamManagerFailed = "views.teamManage.setTeamManager.setTeamManagerFailed"
  }else if(row.team_member_type == "manager"){
    is_manager = false
    ConfirmTitle = 'views.teamManage.setTeamManager.cancelConfirmTitle'
    ConfirmMessage = 'views.teamManage.setTeamManager.cancelConfirmMessage'
    ButtonText = "views.teamManage.setting.cancelTeamManager"
    ButtonClass = "danger"
    TeamManagerSuccess = "views.teamManage.setTeamManager.cancelTeamManagerSuccess"
    TeamManagerFailed = "views.teamManage.setTeamManager.cancelTeamManagerFailed"
  }
  MsgConfirm(
    `${t(ConfirmTitle)}${row.username} ?`,
    t(ConfirmMessage),
    {
      confirmButtonText: t(ButtonText),
      confirmButtonClass: ButtonClass
    }
  )
    .then(() => {
      // loading.value = true
      teamApi.setAdminManage(row.id, {"is_manager":is_manager}).then((res) => {
        if (res.code == 200){
          MsgSuccess(t(TeamManagerSuccess))
          getList(teamId.value)
        }else{
          MsgError(t(TeamManagerFailed))
          loading.value = false
        }
        
      })
    })
    .catch(() => {})
}

function handleSizeChange() {
  paginationConfig.current_page = 1
  getList(teamId.value)
}

function getList(team_id:any) {
  loading.value = true
  teamId.value = team_id
  return teamApi.clickGetTeamMember(team_id, paginationConfig, searchValue.value).then((res) => {
    tableData.value = res.data.records
    paginationConfig.total = res.data.total
    loading.value = false
  })
  .catch(() => {
          loading.value = false
        })
}
function getMemberPageList(){
  getList(teamId.value)
}
function refresh() {
  getList(teamId.value)
}

function openTeamList(team_id:any, type:any){
  console.log("memberType.value",type)
  memberType.value = type
  getList(team_id)
  
}
defineExpose({
  openTeamList
})
</script>
<style lang="scss" scoped>
.log-table tr {
  cursor: pointer;
}
</style>
