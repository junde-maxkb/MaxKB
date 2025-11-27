<template>
  <div class="dataset-share" v-loading="loading">
    <div class="share-container">
      <!-- 搜索输入 -->
      <div class="search-bar">
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
            <div class="members">{{item.type}}</div>
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
               @click.stop="canManageShare && openDropdown(user)">
            <span>{{ permissionLabel(user.permission) }}</span>
            <div v-if="user.showDropdown && canManageShare" class="permission-dropdown">
              <div
                v-for="option in getPermissionOptions(user)"
                :key="option.value"
                class="permission-option"
                :class="{ selected: user.permission === option.value }"
                @click.stop="changePermission(user, option.value)"
              >
                {{ option.label }}
              </div>
            </div>
          </div>
          <div
               class="remove-btn" 
               @click="removePermission(user)">移除</div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!memberList.length" class="empty-state">
        <div class="empty-icon">👥</div>
        <div class="empty-text">还没有共享给任何人</div>
        <div class="empty-subtext">搜索并添加团队来开始共享</div>
      </div>

      <!-- 底部按钮 -->
      <div class="footer-btns">
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
import {ElMessageBox} from 'element-plus'

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
// 既然能打开共享设置，说明有管理权限，默认设置为 MANAGE
const userPermission = ref('MANAGE')

// 权限选项
const PERMISSION_OPTIONS = [
  { value: 'READ', label: '只读权限' },
  { value: 'WRITE', label: '编辑权限' },
  { value: 'MANAGE', label: '辅助管理' }
]

// 计算属性
const filteredResults = computed(() => {
  const query = searchQuery.value.toLowerCase()
  const allItems = [
    ...availableTeams.value.map(team => ({
      ...team
    }))
  ]
  if (!query) return allItems


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
  emit('close')
}

const onSave = () => {
  ElMessageBox.confirm('是否确定该内容不涉密，且是公开可用的知识语料?')
    .then(async () => {
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
        emit('close')
      } catch (error) {
        console.error('保存权限失败:', error)
        ElMessage.error('保存失败')
      } finally {
        loading.value = false
      }
    })
    .catch(() => {
      // catch error
    })

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
      // res.data 是一个对象，包含 teams 和 users 两个数组
      const data = res.data as any
      const teams = data.teams || []
      const users = data.users || []
      availableTeams.value = [
        ...teams.map((team: any) => ({
          id: team.id,
          name: team.name,
          type: 'TEAM'
        })),
        ...users.map((user: any) => ({
          id: user.id,
          name: user.name,
          type: 'USER'
        }))
      ]
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
      getAvailableUsersOrTeams()
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
$primary-color: #554BDB;
$primary-hover: #6B62E0;
$primary-light: #F0EEFA;

.dataset-share {
  .share-container {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    max-width: 700px;
    margin: 0 auto;
    overflow: visible;
  }

  .search-bar {
    position: relative;
    margin-bottom: 20px;
  }

  .search-input {
    width: 100%;
    border: 1px solid #DCDFE6;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    
    &:focus {
      border-color: $primary-color;
      box-shadow: 0 0 0 2px rgba(85, 75, 219, 0.1);
    }
    
    &::placeholder {
      color: #C0C4CC;
    }
  }

  .dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    z-index: 10;
    margin-top: 4px;
    max-height: 280px;
    overflow-y: auto;
  }

  .dropdown-item {
    padding: 12px 16px;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    flex-direction: column;
    border-bottom: 1px solid #F2F3F5;
    
    &:last-child {
      border-bottom: none;
    }
    
    &.selected,
    &:hover {
      background: $primary-light;
    }
    
    .name {
      font-size: 14px;
      font-weight: 500;
      color: #303133;
    }
    
    .members {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
    }
  }

  .user-list {
    margin: 0;
    max-height: 320px;
    overflow: visible;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .user-row {
    display: flex;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
    background: #fff;
    border-radius: 10px;
    padding: 12px 14px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
    transition: border-color 0.2s, box-shadow 0.2s;
    
    &:hover {
      border-color: #cbd5e1;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
  }

  .user-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
    
    .name {
      font-size: 14px;
      font-weight: 500;
      color: #334155;
      word-break: break-word;
    }
    
    .type {
      font-size: 12px;
      color: #64748b;
      display: inline-flex;
      align-items: center;
      padding: 2px 8px;
      background: #ecfdf5;
      color: #059669;
      border-radius: 6px;
      font-weight: 500;
      letter-spacing: 0.5px;
      width: fit-content;
    }
  }

  .permission-select {
    min-width: 100px;
    margin-right: 16px;
    position: relative;
    background: $primary-light;
    border-radius: 6px;
    padding: 6px 28px 6px 12px;
    font-size: 13px;
    color: $primary-color;
    cursor: pointer;
    user-select: none;
    border: 1px solid transparent;
    transition: all 0.2s;
    font-weight: 500;

    &.disabled {
      background: #F5F7FA;
      color: #C0C4CC;
      cursor: not-allowed;
      
      &::after {
        border-top-color: #C0C4CC;
      }
    }

    &::after {
      content: '';
      position: absolute;
      right: 10px;
      top: 50%;
      transform: translateY(-50%);
      width: 0;
      height: 0;
      border-left: 4px solid transparent;
      border-right: 4px solid transparent;
      border-top: 5px solid $primary-color;
    }
    
    &:hover:not(.disabled) {
      border-color: $primary-color;
    }
  }

  .permission-dropdown {
    position: absolute;
    left: 0;
    top: calc(100% + 4px);
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    min-width: 120px;
    z-index: 9999;
    overflow: hidden;
    
    * {
      border: none !important;
      outline: none !important;
      box-shadow: none !important;
    }
  }

  .permission-option {
    padding: 10px 14px;
    cursor: pointer;
    font-size: 13px;
    color: #606266;
    transition: background 0.2s, color 0.2s;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;

    &::before,
    &::after {
      display: none !important;
    }
    
    &.selected {
      background: $primary-light;
      color: $primary-color;
      font-weight: 500;
      border: none !important;
      outline: none !important;
      box-shadow: none !important;
    }
    
    &:hover {
      background: $primary-light;
      color: $primary-color;
    }
    
    &:focus,
    &:focus-visible,
    &:active {
      border: none !important;
      outline: none !important;
      box-shadow: none !important;
    }
  }

  .remove-btn {
    color: #F56C6C;
    font-size: 13px;
    cursor: pointer;
    font-weight: 500;
    transition: color 0.2s;
    padding: 4px 8px;
    border-radius: 4px;
    
    &:hover {
      color: #F34D4D;
      background: #FEF0F0;
    }
  }

  .empty-state {
    text-align: center;
    padding: 48px 20px;
    background: #FAFAFA;
    border-radius: 8px;
    border: 1px dashed #DCDFE6;
    
    .empty-icon {
      font-size: 40px;
      margin-bottom: 16px;
      opacity: 0.8;
    }
    
    .empty-text {
      font-size: 15px;
      color: #303133;
      margin-bottom: 8px;
      font-weight: 500;
    }
    
    .empty-subtext {
      font-size: 13px;
      color: #909399;
    }
  }

  .footer-btns {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid #EBEEF5;
  }

  .cancel-btn {
    border: 1px solid #DCDFE6;
    background: #fff;
    color: #606266;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      color: $primary-color;
      border-color: $primary-color;
      background: $primary-light;
    }
  }

  .save-btn {
    background: $primary-color;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.2s;
    
    &:hover {
      background: $primary-hover;
    }
  }
}
</style>