<template>
  <LayoutContainer :header="$t('views.dataset.shareSetting')">
    <div class="dataset-share main-calc-height">
      <el-scrollbar>
        <div class="p-24" v-loading="loading">
          <el-table :data="memberList" style="width: 100%">
            <el-table-column prop="username" :label="$t('views.dataset.memberName')" />
            <el-table-column :label="$t('views.dataset.permission')">
              <template #default="{ row }">
                <el-radio-group v-model="row.permission" @change="(val: string) => updatePermission(row, val)">
                  <el-radio label="MANAGE">{{ $t('views.dataset.permissionManage') }}</el-radio>
                  <el-radio label="WRITE">{{ $t('views.dataset.permissionWrite') }}</el-radio>
                  <el-radio label="READ">{{ $t('views.dataset.permissionRead') }}</el-radio>
                </el-radio-group>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-scrollbar>
    </div>
  </LayoutContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import datasetApi from '@/api/dataset'
import { MsgSuccess } from '@/utils/message'
import { t } from '@/locales'

const route = useRoute()
const id = ref('')
const loading = ref(false)
const memberList = ref<any[]>([])

interface Member {
  user_id: string
  username: string
  permission: string
}

// 获取成员列表
async function getMemberList() {
  if (!id.value) return
  try {
    loading.value = true
    const res = await datasetApi.getDatasetMembers(id.value, loading)
    memberList.value = res.data
  } catch (error) {
    console.error('获取成员列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 更新成员权限
async function updatePermission(row: Member, permission: string) {
  if (!id.value) return
  try {
    loading.value = true
    await datasetApi.updateDatasetMemberPermission(id.value, row.user_id, permission, loading)
    MsgSuccess(t('common.saveSuccess'))
  } catch (error) {
    console.error('更新权限失败:', error)
  } finally {
    loading.value = false
  }
}

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    id.value = newId as string
    getMemberList()
  }
}, { immediate: true })

// 监听路由变化
watch(() => route.fullPath, () => {
  // 当路由变化时重新获取数据
  if (route.name === 'DatasetShare') {
    getMemberList()
  }
})
</script>

<style lang="scss" scoped>
.dataset-share {
  width: 70%;
  margin: 0 auto;
}
</style>