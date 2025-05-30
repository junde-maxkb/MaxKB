<template>
  <LayoutContainer :header="$t('views.dataSource.title')">
    <div class="team-manage flex main-calc-height">
      <div class="team-member p-8 border-r">
        <div class="flex-between p-16">
          <h4>{{ $t('views.dataSource.dataSourceList') }}</h4>
          <el-button type="primary" link @click="addMember">
            <AppIcon iconName="DocumentAdd" class="DocumentAdd" style="font-size: 16px;"/>
          </el-button>
        </div>
        <div class="team-member-input">
          <el-input
            v-model="filterText"
            :placeholder="$t('views.dataSource.source.SearBar.placeholder')"
            prefix-icon="Search"
            clearable
          />
        </div>
        <div class="list-height-left">
          <el-scrollbar>
            <common-list
              :data="filterMember"
              class="mt-8"
              v-loading="loading"
              @click="clickMemberHandle"
              :default-active="currentSource"
              valueKey="name"
            >
              <template #default="{ row }">
                <div class="flex-between" style="align-items: center; height: 100%">
                  <div  style="display: flex; align-items: center">
                    <el-icon style="font-size: 16px; display: flex; align-items: center"><Coin /></el-icon>&nbsp;&nbsp;
                    <span class="mr-8">{{ row.name }}</span>
                    <el-tag v-if="isManage(row.type)" class="default-tag">{{
                      $t('views.team.manage')
                    }}</el-tag>
                  </div>
                  <div @click.stop style="margin-top: 5px">
                    <el-dropdown trigger="click" v-if="!isManage(row.type)">
                      <span class="cursor">
                        <el-icon class="rotate-90"><MoreFilled /></el-icon>
                      </span>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item @click.prevent="deleteMember(row)">{{
                            $t('views.team.delete.button')
                          }}</el-dropdown-item>
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
      <div class="permission-setting flex" v-loading="rLoading">
        <div class="team-manage__table">
          <h4 class="p-24 pb-0 mb-4">{{ $t('views.dataSource.detail') }}</h4>
          <el-tabs v-model="activeName" class="team-manage__tabs">
            <el-tab-pane
              v-for="(item, index) in settingTags"
              :key="item.value"
              :label="item.label"
              :name="item.value"
            >
               <el-collapse  v-model="activeNames" 
               style="height: 400px;padding:10px 50px; overflow-y: auto;border-top: none;

border-bottom: none;">
                <!-- 基础信息 -->
                <el-collapse-item title="基础信息" name="1">
                  <div class="collapse-content">
                    <el-row>
                      <el-col :span="12">数据源名称</el-col>
                      <el-col :span="12">{{ dataSource.name }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :span="12">描述</el-col>
                      <el-col :span="12">{{ dataSource.description || '-' }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :span="12">主机名/IP地址</el-col>
                      <el-col :span="12">{{ dataSource.host }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :span="12">端口</el-col>
                      <el-col :span="12">{{ dataSource.port }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :span="12">用户名</el-col>
                      <el-col :span="12">{{ dataSource.username }}</el-col>
                    </el-row>
                  </div>
                </el-collapse-item>

                <!-- SSH设置 -->
                <el-collapse-item title="SSH 设置" name="2">
                  <div class="collapse-content">
                    <el-row>
                      <el-col :span="12">主机名/IP地址</el-col>
                      <el-col :span="12">{{ dataSource.ssh_config.host }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :span="12">端口</el-col>
                      <el-col :span="12">{{ dataSource.ssh_config.port }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :span="12">用户名</el-col>
                      <el-col :span="12">{{ dataSource.ssh_config.username }}</el-col>
                    </el-row>
                  </div>
                </el-collapse-item>

                <!-- 高级设置 -->
                <el-collapse-item title="高级设置" name="3">
                  <div class="collapse-content">
                    <el-row>
                      <el-col :span="12">初始连接数</el-col>
                      <el-col :span="12">{{ dataSource.advanced.initialSize }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :span="12">最大连接数</el-col>
                      <el-col :span="12">{{ dataSource.advanced.maxActive }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :span="12">最小连接数</el-col>
                      <el-col :span="12">{{ dataSource.advanced.minIdle }}</el-col>
                    </el-row>
                    <el-row>
                      <el-col :span="12">查询超时</el-col>
                      <el-col :span="12">{{ dataSource.advanced.queryTimeout }}秒</el-col>
                    </el-row>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </el-tab-pane>
            <el-tab-pane></el-tab-pane>
          </el-tabs>
        </div>

        <div class="submit-button">
          <el-button type="primary" @click="editDataSource">
            <!-- {{ $t('common.save') }} -->
            <el-icon><EditPen /></el-icon>
          {{ $t('common.edit') }}
          </el-button>
          
        </div>
      </div>
    </div>
    <createDataSourceDialog ref="createDataSourceRef" @refresh="refresh" />
    <EditDataSourceDialog ref="EditDataSourceRef" @refresh="refresh" />
  </LayoutContainer>
</template>

<script lang="ts" setup>
import { onMounted, ref, reactive, watch } from 'vue'
import dBSourceApi from '@/api/db-data-source'
import type { TeamMember } from '@/api/type/team'
import createDataSourceDialog from './component/createDataSourceDialog.vue'
import EditDataSourceDialog from './component/EditDataSourceDialog.vue'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { TeamEnum } from '@/enums/team'
import { t } from '@/locales'
const createDataSourceRef = ref<InstanceType<typeof createDataSourceDialog>>()
const EditDataSourceRef= ref<InstanceType<typeof EditDataSourceDialog>>()
const loading = ref(false)
const rLoading = ref(false)
const sourceList = ref([]) // 全部成员
const filterMember = ref<TeamMember[]>([]) // 搜索过滤后列表
const currentSource = ref<String>('')
const currentSourceId = ref('')
const filterText = ref('')
const activeNames = ref(['1']);
const activeName = ref(TeamEnum.DATASET)
const tableHeight = ref(0)
const dataSource = ref({
  name:"",
  description:"",
  host:"",
  port:"",
  username: '',
  advanced: {
    initialSize: 0,
    minIdle: 0,
    maxActive: 0,
    queryTimeout: 0
  },
  ssh_config: {
    host: '',
    port: 0,
    username: '',
  }
})
const settingTags = ref([
  {
    label: t('views.dataSource.dataSourceConfig'),
    value: TeamEnum.DATASET,
    data: [] as any
  }
])

watch(filterText, (val) => {
  if (val) {
    filterMember.value = sourceList.value.filter((v) =>
      v.name.toLowerCase().includes(val.toLowerCase())
    )
  } else {
    filterMember.value = sourceList.value
  }
})

function isManage(type: String) {
  return type === 'manage'
}


function deleteMember(row: TeamMember) {
  MsgConfirm(
    `${t('views.team.delete.confirmTitle')}${row.name}?`,
    t('views.team.delete.confirmMessage'),

    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      loading.value = true
      dBSourceApi.deleteDbSource(row.id)
        .then(() => {
          MsgSuccess(t('common.deleteSuccess'))
          getSource()
        })
        .catch(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}

function clickMemberHandle(item: any) {
  dataSource.value = item
  currentSourceId.value = item.id
}
function editDataSource() {
  EditDataSourceRef.value?.open(currentSourceId.value)
}
function addMember() {
  createDataSourceRef.value?.open()
}

function getSource(id?: string) {
  loading.value = true
  dBSourceApi.getDbSourceList()
    .then((res) => {
      sourceList.value = res.data
      filterMember.value = res.data
      currentSource.value = sourceList.value[0].name
      dataSource.value = res.data[0]
      currentSourceId.value = res.data[0].id
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function refresh(data?: string[]) {
  getSource(data && data[0])
}

onMounted(() => {
  tableHeight.value = window.innerHeight - 330
  window.onresize = () => {
    return (() => {
      tableHeight.value = window.innerHeight - 330
    })()
  }
  getSource()
})
</script>

<style lang="scss" scoped>
.team-manage {
  .add-user-icon {
    font-size: 17px;
  }
  .team-member-input {
    padding: 0 calc(var(--app-base-px) * 2);
  }
  .team-member {
    box-sizing: border-box;
    width: var(--setting-left-width);
    min-width: var(--setting-left-width);
  }

  .permission-setting {
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
