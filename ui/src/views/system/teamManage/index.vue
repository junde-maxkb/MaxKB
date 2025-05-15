<template>
  <LayoutContainer :header="$t('views.teamManage.title')">
    <div class="team-manage flex main-calc-height">
      <!-- 左侧团队列表区域 -->
      <div class="team-list p-8 border-r">
        <div class="flex-between p-16">
          <h4>{{ $t('views.teamManage.teamList') }}</h4>
          <el-button
            type="primary"
            link
            @click="addTeamHandle"
            :disabled="user.userInfo?.role !== 'ADMIN'"
          >
            <AppIcon iconName="app-add-users" class="add-user-icon" />
          </el-button>
        </div>
        <!-- 团队搜索框 -->
        <div class="team-list-input">
          <el-input
            v-model="filterText"
            :placeholder="$t('views.teamManage.team.SearBar.placeholder')"
            prefix-icon="Search"
            clearable
          />
        </div>
        <!-- 可滚动的团队列表 -->
        <div class="list-height-left">
          <el-scrollbar>
            <common-list
              :data="filterTeamList"
              class="mt-8"
              v-loading="loading"
              :defaultActive="currentUser"
              valueKey="team_id"
              @click="clickTeamHandle"
            >
              <template #default="{ row }">
                <div class="flex-between">
                  <div>
                    <span class="mr-8">{{ row.team_name }}</span>
                    <el-tag v-if="!isManage(row.role)" class="default-tag">
                      {{ $t('views.teamManage.manage') }}
                    </el-tag>
                  </div>
                  <!-- 团队操作下拉菜单 -->
                  <div @click.stop style="margin-top: 5px">
                    <el-dropdown trigger="click" :disabled="isManage(row.role)">
                      <span class="cursor">
                        <el-icon class="rotate-90"><MoreFilled /></el-icon>
                      </span>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item @click.prevent="handleEditTeam(row)">
                            {{ $t('common.edit') }}
                          </el-dropdown-item>
                          <el-dropdown-item @click.prevent="deleteTeam(row)">
                            {{ $t('views.teamManage.team.delete.button') }}
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
              </template>
            </common-list>
          </el-scrollbar>
        </div>
      </div>
      
      <!-- 右侧团队成员管理区域 -->
      <div class="team-member flex" v-loading="rLoading">
        <div class="team-manage-table">
          <h4 class="p-24 pb-0 mb-4">{{ $t('views.teamManage.member.title') }}</h4>
          <!-- 团队成员列表组件 -->
          <TeamMemberList ref="getTeamMemberRef" :tableHeight="tableHeight" />
        </div>
      </div>
    </div>
    
    <CreateTeamDialog ref="CreateTeamRef" @refresh="refresh" />
    <CreateTeamMemberDialog ref="CreateTeamMemberRef" @refresh="refresh" />
    <EditTeamDialog ref="EditTeamRef" @refresh="refresh" />
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch } from 'vue'
import TeamApi from '@/api/team-manage'
import type { Team } from '@/api/type/team-manage'
import CreateTeamDialog from './component/CreateTeamDialog.vue'
import EditTeamDialog from './component/EditTeamDialog.vue'
import TeamMemberList from './component/TeamMemberList.vue'
import CreateTeamMemberDialog from './component/CreateTeamMemberDialog.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'
import useStore from '@/stores'

const CreateTeamRef = ref<InstanceType<typeof CreateTeamDialog>>()
const CreateTeamMemberRef = ref<InstanceType<typeof CreateTeamMemberDialog>>()
const EditTeamRef = ref<InstanceType<typeof EditTeamDialog>>()
const getTeamMemberRef = ref<InstanceType<typeof TeamMemberList>>()

const loading = ref(false)
const rLoading = ref(false)
const teamList = ref<Team[]>([]) 
const filterTeamList = ref<Team[]>([]) 
const currentUser = ref<String>('')
const currentType = ref<String>('')
const addTeamManage = ref<String>('')

const filterText = ref('')
const { user } = useStore()
const tableHeight = ref(0)

watch(filterText, (val) => {
  if (val) {
    filterTeamList.value = teamList.value.filter((v) =>
      v.team_name.toLowerCase().includes(val.toLowerCase())
    )
  } else {
    filterTeamList.value = teamList.value
  }
})

function isManage(role: String) {
  return role === 'member'
}

function handleEditTeam(row: any) {
  EditTeamRef.value?.open(row.team_id)
}

function ClickgetTeamMember(team_id: any, team_member_type: any) {
  getTeamMemberRef.value?.openTeamList(team_id, team_member_type)
}

function deleteTeam(row: any) {
  MsgConfirm(
    `${t('views.teamManage.team.delete.confirmTitle')}${row.team_name}?`,
    t('views.teamManage.team.delete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      loading.value = true
      console.log('row.id', row.team_id)
      TeamApi.deleteTeam(row.team_id)
        .then(() => {
          MsgSuccess(t('common.deleteSuccess'))
          getTeamList()
        })
        .catch(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}

function clickTeamHandle(item: any) {
  currentUser.value = item.team_id
  addTeamManage.value = item.role
  ClickgetTeamMember(currentUser.value, addTeamManage.value)
}

function addTeamHandle() {
  CreateTeamRef.value?.open()
}

function getTeamList(id?: string) {
  loading.value = true
  TeamApi.getTeam()
    .then((res) => {
      teamList.value = res.data
      filterTeamList.value = res.data
      currentUser.value = teamList.value[0].team_id
      addTeamManage.value = teamList.value[0].role
      ClickgetTeamMember(currentUser.value, addTeamManage.value)
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function refresh(data?: string[]) {
  getTeamList(data && data[0])
}

onMounted(() => {
  tableHeight.value = window.innerHeight - 330
  window.onresize = () => {
    return (() => {
      tableHeight.value = window.innerHeight - 330
    })()
  }
  getTeamList()
})
</script>

<style lang="scss" scoped>
.team-manage {
  .add-user-icon {
    font-size: 17px;
  }
  .team-list-input {
    padding: 0 calc(var(--app-base-px) * 2);
  }
  .team-list {
    box-sizing: border-box;
    width: var(--setting-left-width);
    min-width: var(--setting-left-width);
  }

  .team-member {
    box-sizing: border-box;
    width: calc(100% - var(--setting-left-width));
    flex-direction: column;
    position: relative;
    .submit-button {
      position: absolute;
      top: 54px;
      right: 24px;
    }
  }
  .list-height-left {
    height: calc(var(--create-dataset-height) - 60px);
  }

  &__tabs {
    margin-top: 10px;

    :deep(.el-tabs__nav-scroll) {
      padding: 0 24px;
    }
  }
  &__table {
    flex: 1;
  }
}
</style>