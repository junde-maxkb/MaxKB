<template>
  <div class="dataset-share" v-loading="loading">
    <div class="share-container">
      <!-- 搜索输入 -->
      <div class="search-bar" v-if="canManageShare">
        <input
          v-model="searchQuery"
          @focus="showDropdown = true"
          @input="showDropdown = true"
          @blur="onBlur"
          type="text"
          placeholder="搜索团队..."
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
            <div class="members">团队</div>
          </div>
        </div>
      </div>

      <!-- 权限列表 -->
      <div class="user-list">
        <div v-for="user in memberList" :key="user.id" class="user-row">
          <div class="user-info">
            <div class="name">{{ user.name }}</div>
            <div class="type">
              团队
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
               @click="removePermission(user)">移除</div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!memberList.length" class="empty-state">
        <div class="empty-icon">👥</div>
        <div class="empty-text">还没有共享给任何人</div>
        <div class="empty-subtext" v-if="canManageShare">搜索并添加团队来开始共享</div>
      </div>

      <!-- 底部按钮 -->
      <div class="footer-btns" v-if="canManageShare">
        <button class="cancel-btn" @click="onCancel">取消</button>
        <button class="save-btn" @click="onSave">保存权限设置</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import datasetApi from '@/api/dataset'
import teamApi from '@/api/team'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import useStore from '@/stores'

// Props
interface Props {
  datasetId: string
  datasetName: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  close: []
}>()

// Store
const { user } = useStore()

// 响应式数据
const loading = ref(false)
const searchQuery = ref('')
const showDropdown = ref(false)
const memberList = ref<any[]>([])
const availableMembers = ref<any[]>([])
const availableTeams = ref<any[]>([])
const userPermission = ref('READ')

// 权限选项
const PERMISSION_OPTIONS = [
  { value: 'READ', label: '只读权限' },
  { value: 'WRITE', label: '编辑权限' },
  { value: 'MANAGE', label: '辅助管理' }
]

// 计算属性
const filteredResults = computed(() => {
  const query = searchQuery.value.toLowerCase()
  if (!query) return []

  // 只搜索团队，不再搜索用户
  const allItems = [
    ...availableTeams.value.map(team => ({
      ...team,
      type: 'TEAM'
    }))
  ]
  return allItems.filter(item =>
    item.name.toLowerCase().includes(query)
  )
})

const canManageShare = computed(() => {
  return userPermission.value === 'MANAGE'
})

// 方法
const permissionLabel = (val: string) => {
  return PERMISSION_OPTIONS.find(opt => opt.value === val)?.label || ''
}

const getPermissionOptions = (user: any) => {
  // 团队可以选择只读权限和辅助管理权限
  if (user.type === 'TEAM') {
    return PERMISSION_OPTIONS.filter(opt => ['READ', 'MANAGE'].includes(opt.value))
  }
  return PERMISSION_OPTIONS
}

const onBlur = () => {
  setTimeout(() => {
    showDropdown.value = false
    // 同时关闭所有权限下拉框
    memberList.value.forEach(u => (u.showDropdown = false))
  }, 100)
}

// 添加点击外部关闭下拉框的处理函数
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.permission-select') && !target.closest('.search-bar')) {
    showDropdown.value = false
    memberList.value.forEach(u => (u.showDropdown = false))
  }
}

const openDropdown = (user: any) => {
  memberList.value.forEach(u => (u.showDropdown = false))
  user.showDropdown = true
}

const changePermission = (user: any, value: string) => {
  // 团队只能设置为只读权限或辅助管理权限
  if (user.type === 'TEAM' && !['READ', 'MANAGE'].includes(value)) {
    user.permission = 'READ'
  } else {
    user.permission = value
  }
  user.showDropdown = false
}

const addUser = (item: any) => {
  // 检查是否已经存在（同时判断id和type）
  if (!memberList.value.some(u => u.id === item.id && u.type === item.type)) {
    // 添加新团队
    const newMember = {
      id: item.id,
      name: item.name,
      type: item.type,
      permission: item.type === 'TEAM' ? 'MANAGE' : 'READ', // 团队默认辅助管理权限，其他默认只读
      showDropdown: false
    }

    memberList.value.push(newMember)
  }

  showDropdown.value = false
  searchQuery.value = ''
}

const removePermission = async (user: any) => {
  try {
    await MsgConfirm(`确定要移除团队"${user.name}"的访问权限吗？`, '移除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await datasetApi.putMemberPermission(props.datasetId, {
      user_id: user.id,
      permission: 'NONE',
      share_with_type: user.type
    })
    
    ElMessage.success('权限已移除')
    await getMemberList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除权限失败:', error)
      ElMessage.error('移除失败')
    }
  }
}

const onCancel = () => {
  getMemberList()
}

const onSave = async () => {
  try {
    loading.value = true
    for (const member of memberList.value) {
      const params = {
        user_id: member.id,
        permission: member.permission,  // 使用选择的权限
        share_with_type: member.type
      }
      await datasetApi.putMemberPermission(props.datasetId, params)
    }
    ElMessage.success('权限设置已保存')
  } catch (error) {
    console.error('保存权限失败:', error)
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

// 获取成员列表
const getMemberList = async () => {
  try {
    loading.value = true
    const res = await datasetApi.getDatasetMembers(props.datasetId)
    memberList.value = res.data.members
      .filter((member: any) => member.permission !== 'NONE')
      .map((member: any) => ({
        id: member.user_id,
        name: member.type === 'TEAM' ? member.team_name : member.username,
        type: member.type,
        permission: member.permission || 'READ',
        members: member.members,
        showDropdown: false
      }))
  } catch (error) {
    console.error('获取成员列表失败:', error)
    ElMessage.error('获取成员列表失败')
  } finally {
    loading.value = false
  }
}

// 获取可用团队列表（不包含用户）
const getAvailableUsersOrTeams = async () => {
  try {
    const res = await teamApi.getAvailableUsersOrTeams()

    if (res.data) {
      // 只处理团队，不处理用户
      availableMembers.value = []
      availableTeams.value = (res.data || []).map((team: any) => ({
        id: team.id,
        name: team.name,
        type: 'TEAM'
      }))
    }
  } catch (error) {
    console.error('获取可用团队列表失败:', error)
  }
}

// 获取当前用户权限（通过成员列表获取）
const getCurrentUserPermission = async () => {
  try {
    const userId = user.userInfo?.id
    if (!userId) {
      userPermission.value = 'READ'
      return
    }
    
    const res = await datasetApi.getDatasetMembers(props.datasetId)
    const currentUser = res.data.members.find((member: any) => member.user_id === userId)
    if (currentUser) {
      userPermission.value = currentUser.permission
    } else {
      // 如果用户不在成员列表中，可能是知识库所有者，给予管理权限
      userPermission.value = 'MANAGE'
    }
  } catch (error) {
    console.error('获取用户权限失败:', error)
    // 默认给予管理权限，让用户可以查看和管理
    userPermission.value = 'MANAGE'
  }
}

// 组件挂载
onMounted(async () => {
  // 添加点击事件监听
  document.addEventListener('click', handleClickOutside)
  
  try {
    await Promise.all([
      getMemberList(),
      getAvailableUsersOrTeams(),
      getCurrentUserPermission()
    ])
  } catch (error) {
    console.error('ShareSettings 组件初始化失败:', error)
  }
})

// 组件卸载
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style lang="scss" scoped>
.dataset-share {
  .share-container {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 12px #0001;
    padding: 32px 32px 24px 32px;
    max-width: 600px;
    margin: 0 auto;
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
    
    &:focus {
      border-color: #3a5cff;
    }
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
    
    &.selected,
    &:hover {
      background: #f4f7ff;
    }
    
    .name {
      font-size: 15px;
      font-weight: 500;
    }
    
    .members {
      font-size: 12px;
      color: #a0a0a0;
      margin-top: 2px;
    }
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
    
    .name {
      font-size: 16px;
      font-weight: 500;
      color: #222;
    }
    
    .type {
      font-size: 13px;
      color: #a0a0a0;
      margin-top: 2px;
    }
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

    &::after {
      content: '';
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      width: 0;
      height: 0;
      border-left: 4px solid transparent;
      border-right: 4px solid transparent;
      border-top: 4px solid #3a5cff;
    }
    
    &:hover:not(.disabled) {
      border: 1px solid #3a5cff;
    }
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
    
    &.selected {
      background: #f4f7ff;
      color: #3a5cff;
      font-weight: 500;
    }
    
    &:hover {
      background: #f4f7ff;
      color: #3a5cff;
    }
  }

  .remove-btn {
    color: #f53f3f;
    font-size: 15px;
    margin-left: 12px;
    cursor: pointer;
    font-weight: 500;
    transition: color 0.2s;
    
    &:hover {
      color: #d72626;
    }
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    
    .empty-icon {
      font-size: 48px;
      margin-bottom: 16px;
    }
    
    .empty-text {
      font-size: 16px;
      color: #303133;
      margin-bottom: 8px;
    }
    
    .empty-subtext {
      font-size: 14px;
      color: #909399;
    }
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
    
    &:hover {
      background: #f4f7ff;
      border: 1px solid #3a5cff;
    }
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
    
    &:hover {
      background: #2446b9;
    }
  }
}
</style>