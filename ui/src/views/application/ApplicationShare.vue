<template>
  <LayoutContainer :header="$t('views.application.shareSetting')">
    <div class="application-share main-calc-height">
      <el-scrollbar>
        <div class="p-24" v-loading="loading">
          <div class="share-container">
            <!-- 搜索输入 -->
            <div class="search-bar" v-if="canManageShare">
              <input
                v-model="searchQuery"
                @focus="showDropdown = true"
                @input="showDropdown = true"
                @blur="onBlur"
                type="text"
                :placeholder="$t('views.application.searchUserOrTeam')"
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
                    {{ user.type === 'USER' ? $t('views.application.user') : `${$t('views.application.team')} · ${user.members || ''}${user.members ? ' ' + $t('views.application.members') : ''}` }}
                  </div>
                </div>
                <div class="permission-select" 
                     :class="{ 'disabled': !canManageShare }"
                     @click="canManageShare && openDropdown(user)">
                  <span>{{ permissionLabel(user.permission) }}</span>
                  <div v-if="user.showDropdown && canManageShare" class="permission-dropdown">
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
                <div v-if="canManageShare" 
                     class="remove-btn" 
                     @click="removePermission(user)">{{ $t('views.application.remove') }}</div>
              </div>
            </div>

            <!-- 底部按钮 -->
            <div class="footer-btns" v-if="canManageShare">
              <button class="cancel-btn" @click="onCancel">{{ $t('views.application.cancel') }}</button>
              <button class="save-btn" @click="onSave">{{ $t('views.application.savePermission') }}</button>
            </div>
          </div>
        </div>
      </el-scrollbar>
    </div>
  </LayoutContainer>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import applicationApi from '@/api/application'
import teamApi from '@/api/team'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { t } from '@/locales'

const route = useRoute()
const id = ref('')
const loading = ref(false)
const memberList = ref<any[]>([])
const availableMembers = ref<any[]>([])
const availableTeams = ref<any[]>([])
const userPermission = ref<string>('')

const PERMISSION_OPTIONS = [
  { value: 'READ', label: '使用权限' },
  { value: 'WRITE', label: '开发权限' },
  { value: 'MANAGE', label: '管理权限' }
]

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
    const res = await applicationApi.getApplicationMembers(id.value)
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
async function getAvailableUsersOrTeams() {
  try {
    const res = await teamApi.getAvailableUsersOrTeams()
    interface ApiResponse {
      teams: Array<{
        id: string;
        name: string;
        type: string;
      }>;
      users: Array<{
        id: string;
        name: string;
        email: string;
        type: string;
      }>;
    }
    
    const data = (res.data as unknown) as ApiResponse;
    availableMembers.value = (data.users || []).map((member) => ({
      id: member.id,
      name: member.name,
      type: 'USER'
    }))
    availableTeams.value = (data.teams || []).map((team) => ({
      id: team.id,
      name: team.name,
      type: 'TEAM'
    }))
  } catch (error) {
    console.error('获取可用用户和团队列表失败:', error)
  }
}

import useStore from '@/stores'
const { application } = useStore()

// 获取用户对当前应用的权限
async function getUserPermission() {
  try {
    const res = await applicationApi.getCurrentUserPermission(id.value)
    if (res.data) {
      userPermission.value = res.data.permission
    } else {
      userPermission.value = 'MANAGE'
    }
  } catch (error) {
    console.error('获取用户权限失败:', error)
    userPermission.value = 'MANAGE'
  }
}

// 移除权限
async function removePermission(row: any) {
  try {
    await MsgConfirm(t('views.application.confirmRemovePermission'), t('common.confirm'))
    await applicationApi.putMemberPermission(id.value.trim(), {
      user_id: row.id.trim(),
      permission: 'NONE',
      share_with_type: row.type as 'USER' | 'TEAM'
    })
    MsgSuccess(t('common.deleteSuccess'))
    getMemberList()
  } catch (error) {
    console.error('移除权限失败:', error)
  }
}

function permissionLabel(val: string) {
  return PERMISSION_OPTIONS.find(opt => opt.value === val)?.label || ''
}

function openDropdown(user: any) {
  memberList.value.forEach(u => (u.showDropdown = false))
  user.showDropdown = true
}

function changePermission(user: any, value: string) {
  if (user.type === 'TEAM') {
    user.permission = 'READ'
  } else {
    user.permission = value
  }
  user.showDropdown = false
}

// 获取权限选项
function getPermissionOptions(user: any) {
  if (user.type === 'TEAM') {
    return PERMISSION_OPTIONS.filter(opt => opt.value === 'READ')
  }
  return PERMISSION_OPTIONS
}

function onBlur() {
  setTimeout(() => (showDropdown.value = false), 100)
}

function onCancel() {
  getMemberList()
}

async function onSave() {
  try {
    loading.value = true
    for (const member of memberList.value) {
      const params = {
        user_id: member.id,
        permission: member.permission,
        share_with_type: (member.type === 'TEAM' ? 'TEAM' : 'USER') as 'USER' | 'TEAM'
      }
      await applicationApi.putMemberPermission(id.value, params)
    }
    MsgSuccess(t('common.saveSuccess'))
  } catch (error) {
    console.error('保存权限失败:', error)
  } finally {
    loading.value = false
  }
}

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    id.value = newId as string
    getMemberList()
    getAvailableUsersOrTeams()
    getUserPermission()
  }
}, { immediate: true })

const searchQuery = ref('')
const showDropdown = ref(false)
const searchResults = ref([])

// 添加点击其他地方关闭下拉框的功能
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.permission-select')) {
    memberList.value.forEach(user => {
      user.showDropdown = false
    })
  }
}

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

// 注释：removeUser 方法已删除，因为它未被使用且可能造成混淆
// 所有移除操作都通过 removePermission 方法处理，确保立即同步到服务器
</script>

<style lang="scss" scoped>
.application-share {
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

    &.disabled {
      background: #f5f5f5;
      color: #999;
      cursor: not-allowed;
      border: 1px solid #e5e6eb;
      
      &:hover {
        border: 1px solid #e5e6eb;
      }
    }
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
    position: relative;

    &::before,
    &::after {
      display: none !important;  // 强制移除所有伪元素
    }
  }

  .permission-option.selected {
    background: #f4f7ff;
    color: #3a5cff;
    font-weight: 500;
  }

  .permission-option:hover {
    background: #f4f7ff;
    color: #3a5cff;
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