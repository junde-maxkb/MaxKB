<template>
  <LayoutContainer :header="$t('views.dataset.shareSetting')">
    <div class="dataset-share main-calc-height">
      <el-scrollbar>
        <div class="p-24" v-loading="loading">
          <div class="share-container">
            <!-- 搜索输入 -->
            <div class="search-bar">
              <input
                v-model="searchQuery"
                @focus="showDropdown = true"
                @input="showDropdown = true"
                @blur="onBlur"
                type="text"
                placeholder="搜索用户或团队..."
                class="search-input"
              />
              <div v-if="showDropdown && filteredResults.length" class="dropdown">
                <div
                  v-for="item in filteredResults"
                  :key="item.id"
                  class="dropdown-item"
                  :class="{ selected: false }"
                  @mousedown.prevent="addUser(item)"
                >
                  <div class="name">{{ item.name }}</div>
                  <div v-if="item.type === 'TEAM'" class="members">{{ item.members }} 成员</div>
                </div>
              </div>
            </div>

            <!-- 权限列表 -->
            <div class="user-list">
              <div v-for="user in memberList" :key="user.id" class="user-row">
                <div class="user-info">
                  <div class="name">{{ user.name }}</div>
                  <div class="type">
                    {{ user.type === 'USER' ? '用户' : `团队 · ${user.members || ''}${user.members ? ' 成员' : ''}` }}
                  </div>
                </div>
                <div class="permission-select" @click="openDropdown(user)">
                  <span>{{ permissionLabel(user.permission) }}</span>
                  <div v-if="user.showDropdown" class="permission-dropdown">
                    <div
                      v-for="option in getPermissionOptions(user)"
                      :key="option.value"
                      class="permission-option"
                      :class="{ selected: user.permission === option.value }"
                      @mousedown.prevent="changePermission(user, option.value)"
                    >
                      {{ option.label }}
                    </div>
                  </div>
                </div>
                <div class="remove-btn" @click="removePermission(user)">移除</div>
              </div>
            </div>

            <!-- 底部按钮 -->
            <div class="footer-btns">
              <button class="cancel-btn" @click="onCancel">取消</button>
              <button class="save-btn" @click="onSave">保存权限设置</button>
            </div>
          </div>
        </div>
      </el-scrollbar>
    </div>
  </LayoutContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import datasetApi from '@/api/dataset'
import teamApi from '@/api/team'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'

const route = useRoute()
const id = ref('')
const loading = ref(false)
const saving = ref(false)
const memberList = ref<any[]>([])
const availableMembers = ref<any[]>([])
const availableTeams = ref<any[]>([])
const userPermission = ref<string>('')

const PERMISSION_OPTIONS = [
  { value: 'READ', label: '只读权限' },
  { value: 'WRITE', label: '编辑权限' },
  { value: 'MANAGE', label: '管理权限' }
]

const shareForm = ref({
  selectedType: 'USER',
  selectedId: '',
  permission: 'READ'
})

// 计算当前可选项
const filteredResults = computed(() => {
  const query = searchQuery.value.toLowerCase()
  const allItems = [
    ...availableMembers.value.map(member => ({
      ...member,
      type: 'USER'
    })),
    ...availableTeams.value.map(team => ({
      ...team,
      type: 'TEAM'
    }))
  ]
  return allItems.filter(item =>
    item.name.toLowerCase().includes(query)
  )
})

// 计算属性：判断用户是否有权限管理共享设置
const canManageShare = computed(() => {
  return userPermission.value === 'MANAGE'
})

// 获取成员列表
async function getMemberList() {
  if (!id.value) return
  try {
    loading.value = true
    const res = await datasetApi.getDatasetMembers(id.value)
    memberList.value = res.data.members
      .filter((member: any) => member.permission !== 'NONE')
      .map((member: any) => ({
        id: member.user_id,
        name: member.username,
        type: member.type,
        permission: member.permission || 'READ',
        showDropdown: false
      }))
  } catch (error) {
    console.error('获取成员列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取可用成员列表
async function getAvailableMembers() {
  try {
    const res = await teamApi.getTeamMember()
    availableMembers.value = (res.data || []).map((member: any) => ({
      id: member.user_id,
      name: member.username,
      type: 'USER'
    }))
  } catch (error) {
    console.error('获取可用成员列表失败:', error)
  }
}

// 获取可用团队列表
async function getAvailableTeams() {
  try {
    const res = await teamApi.getCurrentUserTeams()
    availableTeams.value = (res.data || []).map((team: any) => ({
      id: team.id,
      name: team.name,
      type: 'TEAM',
      role: team.role
    }))
  } catch (error) {
    console.error('获取可用团队列表失败:', error)
  }
}

// 获取用户对当前知识库的权限
async function getUserPermission() {
  if (!id.value) return
  try {
    const res = await datasetApi.getDatasetMembers(id.value)
    const currentUser = res.data.members.find((member: any) => member.user_id === localStorage.getItem('userId'))
    if (currentUser) {
      userPermission.value = currentUser.permission
    }
  } catch (error) {
    console.error('获取用户权限失败:', error)
  }
}

// 处理选择变化
function handleSelectionChange() {
  shareForm.value.permission = 'READ' // 重置权限为默认值
}

// 保存权限
async function savePermission() {
  if (!id.value || !shareForm.value.selectedId) return
  
  try {
    saving.value = true
    const permission = shareForm.value.permission === 'NONE' ? 'NONE' : shareForm.value.permission
    await datasetApi.putMemberPermission(id.value.trim(), shareForm.value.selectedType, {
      user_id: shareForm.value.selectedId.trim(),
      permission: permission as string | null,
      share_with_type: shareForm.value.selectedType
    })
    
    MsgSuccess(t('common.saveSuccess'))
    shareForm.value.selectedId = ''
    shareForm.value.permission = 'READ'
    getMemberList()
  } catch (error) {
    console.error('更新权限失败:', error)
  } finally {
    saving.value = false
  }
}

// 移除权限
async function removePermission(row: any) {
  try {
    await MsgConfirm(t('views.dataset.confirmRemovePermission'), t('common.confirm'))
    await datasetApi.putMemberPermission(id.value.trim(), {
      user_id: row.id.trim(),
      permission: 'NONE',
      share_with_type: row.type
    })
    MsgSuccess(t('common.deleteSuccess'))
    getMemberList()
  } catch (error) {
    console.error('移除权限失败:', error)
  }
}

// 获取权限标签类型
function getPermissionTagType(permission: string) {
  const types: Record<string, string> = {
    'MANAGE': 'success',
    'WRITE': 'warning',
    'READ': 'info',
    'NONE': 'danger'
  }
  return types[permission] || 'info'
}

// 获取权限文本
function getPermissionText(permission: string) {
  const texts: Record<string, string> = {
    'MANAGE': t('views.dataset.permissionManage'),
    'WRITE': t('views.dataset.permissionWrite'),
    'READ': t('views.dataset.permissionRead'),
    'NONE': t('views.dataset.permissionNone')
  }
  return texts[permission] || permission
}

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    id.value = newId as string
    getMemberList()
    getAvailableMembers()
    getAvailableTeams()
    getUserPermission() // 获取用户权限
  }
}, { immediate: true })

const searchQuery = ref('')
const showDropdown = ref(false)
const searchResults = ref([])

function addUser(item: any) {
  // 检查是否已经存在（同时判断id和type）
  if (!memberList.value.some(u => u.id === item.id && u.type === item.type)) {
    // 添加新成员
    const newMember = {
      id: item.id,
      name: item.name,
      type: item.type,
      permission: 'READ',
      showDropdown: false
    }
    
    memberList.value.push(newMember)
  }
  
  showDropdown.value = false
  searchQuery.value = ''
}

function removeUser(user: any) {
  memberList.value = memberList.value.filter(u => u.id !== user.id)
}

function permissionLabel(val: string) {
  return PERMISSION_OPTIONS.find(opt => opt.value === val)?.label || ''
}

function openDropdown(user: any) {
  memberList.value.forEach(u => (u.showDropdown = false))
  user.showDropdown = true
}

function changePermission(user: any, value: string) {
  // 如果是团队类型，强制设置为只读权限
  if (user.type === 'TEAM') {
    user.permission = 'READ'
  } else {
    user.permission = value
  }
  user.showDropdown = false
}

// 获取权限选项
function getPermissionOptions(user: any) {
  // 如果是团队类型，只返回只读权限选项
  if (user.type === 'TEAM') {
    return PERMISSION_OPTIONS.filter(opt => opt.value === 'READ')
  }
  return PERMISSION_OPTIONS
}

function onBlur() {
  setTimeout(() => (showDropdown.value = false), 100)
}

function onCancel() {
  // 重置列表
  getMemberList()
}

async function onSave() {
  try {
    loading.value = true
    console.log('开始保存权限设置，当前成员列表:', memberList.value)
    
    for (const member of memberList.value) {
      console.log('正在处理成员:', member)
      const params = {
        user_id: member.id,
        permission: member.permission,
        share_with_type: member.type === 'TEAM' ? 'TEAM' : 'USER'
      }
      console.log('发送请求参数:', params)
      
      await datasetApi.putMemberPermission(id.value, params)
      console.log('成员权限设置成功:', member.name)
    }
    
    MsgSuccess(t('common.saveSuccess'))
    console.log('所有权限设置完成')
  } catch (error) {
    console.error('保存权限失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.dataset-share {
  width: 70%;
  margin: 0 auto;
  
  .share-container {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 12px #0001;
    padding: 32px 32px 24px 32px;
    max-width: 600px;
    margin: 32px auto;
  }

  .search-bar {
    position: relative;
    margin-bottom: 16px;
  }

  .search-input {
    width: 100%;
    border: 1px solid #e5e6eb;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 15px;
    outline: none;
    box-shadow: 0 2px 8px #0001;
    transition: border 0.2s;
  }

  .dropdown {
    position: absolute;
    top: 44px;
    left: 0;
    right: 0;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 12px #0002;
    z-index: 10;
    padding: 4px 0;
  }

  .dropdown-item {
    padding: 10px 20px 8px 20px;
    cursor: pointer;
    border-radius: 8px;
    transition: background 0.2s;
    display: flex;
    flex-direction: column;
  }

  .dropdown-item.selected,
  .dropdown-item:hover {
    background: #f4f7ff;
  }

  .dropdown-item .name {
    font-size: 15px;
    font-weight: 500;
  }

  .dropdown-item .members {
    font-size: 12px;
    color: #a0a0a0;
    margin-top: 2px;
  }

  .user-list {
    margin: 16px 0 0 0;
  }

  .user-row {
    display: flex;
    align-items: center;
    background: #fafbfc;
    border-radius: 10px;
    margin-bottom: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 4px #0001;
  }

  .user-info {
    flex: 1;
    min-width: 0;
  }

  .user-info .name {
    font-size: 16px;
    font-weight: 500;
    color: #222;
  }

  .user-info .type {
    font-size: 13px;
    color: #a0a0a0;
    margin-top: 2px;
  }

  .permission-select {
    min-width: 120px;
    margin-right: 24px;
    position: relative;
    background: #f4f7ff;
    border-radius: 8px;
    padding: 6px 18px;
    font-size: 15px;
    color: #3a5cff;
    cursor: pointer;
    user-select: none;
    border: 1px solid #e5e6eb;
    transition: border 0.2s;
  }

  .permission-select:hover {
    border: 1px solid #3a5cff;
  }

  .permission-dropdown {
    position: absolute;
    left: 0;
    top: 38px;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 12px #0002;
    min-width: 120px;
    z-index: 20;
    padding: 4px 0;
  }

  .permission-option {
    padding: 8px 18px;
    cursor: pointer;
    font-size: 15px;
    color: #222;
    border-radius: 8px;
    transition: background 0.2s, color 0.2s;
  }

  .permission-option.selected,
  .permission-option:hover {
    background: #f4f7ff;
    color: #3a5cff;
    font-weight: 500;
  }

  .remove-btn {
    color: #f53f3f;
    font-size: 15px;
    margin-left: 12px;
    cursor: pointer;
    font-weight: 500;
    transition: color 0.2s;
  }

  .remove-btn:hover {
    color: #d72626;
  }

  .footer-btns {
    display: flex;
    justify-content: flex-end;
    gap: 16px;
    margin-top: 32px;
  }

  .cancel-btn {
    border: 1px solid #e5e6eb;
    background: #fff;
    color: #222;
    border-radius: 8px;
    padding: 10px 32px;
    font-size: 15px;
    cursor: pointer;
    transition: background 0.2s, border 0.2s;
  }

  .cancel-btn:hover {
    background: #f4f7ff;
    border: 1px solid #3a5cff;
  }

  .save-btn {
    background: #3a5cff;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 10px 32px;
    font-size: 15px;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.2s;
  }

  .save-btn:hover {
    background: #2446b9;
  }
}
</style>