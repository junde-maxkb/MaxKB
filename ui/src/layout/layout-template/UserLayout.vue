<template>
  <div class="common-layout">
    <el-container style="height: 100%">
      <el-aside width="260px" style="background: rgb(246, 247, 250)">

        <div class="container">
          <div class="first">
            <div class="icon-box">
              <img src="@/assets/JKY.png" alt="JKY" class="logo-img" />
              <div class="home-icon" @click="goToHome">
                <el-icon :size="24"><HomeFilled /></el-icon>
              </div>
            </div>
            <div class="input-box">
              <el-input
                v-model="searchText"
                style="width: 240px"
                placeholder="搜索..."
                :suffix-icon="Search"
              />
            </div>

            <div class="add-btn">
              <el-button style="width: 240px" type="primary" :icon="Plus">新建知识库</el-button>
            </div>

            <div class="home-item" @click="goToHome">
              <div class="home-item-box">
                <div class="item-icon">
                  <el-icon :size="24"><HomeFilled /></el-icon>
                  <div>
                    <span>主页</span>
                  </div>
                </div>

                <div class="arrow-icon">
                  <el-icon><ArrowRightBold /></el-icon>
                </div>
              </div>
            </div>

            <div class="line-split"></div>
          </div>

          <div class="knowledge-tree second">
            <el-tree
              ref="treeRef"
              :data="filteredTreeData"
              :props="treeProps"
              node-key="id"
              :default-expand-all="false"
              :expand-on-click-node="false"
              :check-on-click-node="false"
              :show-checkbox="true"
              :check-strictly="false"
              @node-click="handleNodeClick"
              @check="handleNodeCheck"
              @node-expand="handleNodeExpand"
              class="knowledge-tree-container"
            >
              <template #default="{ node, data }">
                <div
                  class="tree-node"
                  :class="{
                  'level-1': data.level === 1,
                  'level-2': data.level === 2,
                  'level-3': data.level === 3,
                  active: selectedNode?.id === data.id
                }"
                >
                  <!-- 一级目录 -->
                  <div v-if="data.level === 1" class="node-content level-1-content">
                    <div class="node-left">
                      <el-icon class="node-icon">
                        <component :is="data.icon" />
                      </el-icon>
                      <span class="node-label" :title="data.label">{{ data.label }}</span>
                    </div>
                    <el-dropdown trigger="click" @command="handleLevel1Action" @click.stop>
                      <el-icon class="more-actions">
                        <more-one theme="outline" size="24" fill="#333"/>
                      </el-icon>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <!-- 个人知识库菜单 -->
                          <template v-if="data.type === 'personal'">
                            <el-dropdown-item :command="{ action: 'refresh', data }">
                              <el-icon>
                                <Refresh />
                              </el-icon>
                              刷新
                            </el-dropdown-item>
                            <el-dropdown-item divided>
                              <span style="color: #909399; font-size: 12px">排序方式</span>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'sort-by-time', data }">
                              <el-icon>
                                <Timer />
                              </el-icon>
                              按时间排序
                              <el-icon
                                v-if="personalKBSortType === 'time'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
                              </el-icon>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'sort-by-name', data }">
                              <el-icon>
                                <Sort />
                              </el-icon>
                              按名称排序
                              <el-icon
                                v-if="personalKBSortType === 'name'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
                              </el-icon>
                            </el-dropdown-item>
                          </template>

                          <!-- 机构知识库菜单 - 只有排序功能 -->
                          <template v-else-if="data.type === 'organization'">
                            <el-dropdown-item :command="{ action: 'refresh', data }">
                              <el-icon>
                                <Refresh />
                              </el-icon>
                              刷新
                            </el-dropdown-item>
                            <el-dropdown-item divided>
                              <span style="color: #909399; font-size: 12px">排序方式</span>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'org-sort-by-name', data }">
                              <el-icon>
                                <Sort />
                              </el-icon>
                              按名称排序
                              <el-icon
                                v-if="organizationKBSortType === 'name'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
                              </el-icon>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'org-sort-by-time', data }">
                              <el-icon>
                                <Timer />
                              </el-icon>
                              按创建时间排序
                              <el-icon
                                v-if="organizationKBSortType === 'time'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
                              </el-icon>
                            </el-dropdown-item>
                          </template>

                          <!-- 共享知识库菜单 -->
                          <template v-else-if="data.type === 'shared'">
                            <el-dropdown-item :command="{ action: 'refresh', data }">
                              <el-icon>
                                <Refresh />
                              </el-icon>
                              刷新
                            </el-dropdown-item>
                            <el-dropdown-item divided>
                              <span style="color: #909399; font-size: 12px">排序方式</span>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'shared-sort-by-name', data }">
                              <el-icon>
                                <Sort />
                              </el-icon>
                              按名称排序
                              <el-icon
                                v-if="sharedKBSortType === 'name'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
                              </el-icon>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'shared-sort-by-time', data }">
                              <el-icon>
                                <Timer />
                              </el-icon>
                              按创建时间排序
                              <el-icon
                                v-if="sharedKBSortType === 'time'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
                              </el-icon>
                            </el-dropdown-item>
                          </template>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>

                  <!-- 二级目录 - 知识库 -->
                  <div
                    v-else-if="data.level === 2 && data.label != 'CNKI文献'"
                    class="node-content level-2-content"
                  >
                    <div class="node-left">
                      <el-icon class="node-icon">
                        <Folder />
                      </el-icon>
                      <span class="node-label" :title="data.label">{{ data.label }}</span>
                      <span class="doc-count">({{ data.documentCount || 0 }})</span>
                    </div>

                    <!-- 知识库操作按钮 -->
                    <el-dropdown trigger="click" @command="handleKBAction" @click.stop>
                      <el-icon class="more-actions">
                        <MoreOne />
                      </el-icon>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <!-- 我的知识库 - 完整操作权限 -->
                          <template v-if="getKBType(data) === 'personal'">
                            <el-dropdown-item :command="{ action: 'view', data }">
                              <el-icon>
                                <View />
                              </el-icon>
                              查看详情
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'rename', data }">
                              <el-icon>
                                <EditPen />
                              </el-icon>
                              重命名
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'share', data }" @click.stop>
                              <el-icon>
                                <Share />
                              </el-icon>
                              共享设置
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'delete', data }" divided>
                              <el-icon>
                                <Delete />
                              </el-icon>
                              删除
                            </el-dropdown-item>
                          </template>

                          <!-- 共享知识库 - 辅助管理可以查看详情 -->
                          <template v-if="getKBType(data) === 'shared'">
                            <template
                              v-if="
                              data.permission === 'MANAGE' ||
                              (data.shared_with_type === 'TEAM' &&
                                data.team_permission === 'MANAGE')
                            "
                            >
                              <el-dropdown-item :command="{ action: 'view', data }">
                                <el-icon>
                                  <View />
                                </el-icon>
                                查看详情
                              </el-dropdown-item>
                              <el-dropdown-item divided :command="{ action: 'exit-share', data }">
                                <el-icon>
                                  <Close />
                                </el-icon>
                                退出共享
                              </el-dropdown-item>
                            </template>
                            <template v-else>
                              <el-dropdown-item :command="{ action: 'exit-share', data }">
                                <el-icon>
                                  <Close />
                                </el-icon>
                                退出共享
                              </el-dropdown-item>
                            </template>
                          </template>

                          <!-- 机构知识库 - 管理员权限 -->
                          <template v-if="getKBType(data) === 'organization'">
                            <template v-if="isAdmin">
                              <el-dropdown-item :command="{ action: 'edit', data }">
                                <el-icon>
                                  <Edit />
                                </el-icon>
                                编辑
                              </el-dropdown-item>
                              <el-dropdown-item :command="{ action: 'remove-from-org', data }">
                                <el-icon>
                                  <FolderRemove />
                                </el-icon>
                                移出机构
                              </el-dropdown-item>
                            </template>
                            <template v-else>
                              <el-dropdown-item disabled>
                                <span style="color: #c0c4cc">无可用操作</span>
                              </el-dropdown-item>
                            </template>
                          </template>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>

                  <!-- 三级目录 - 文档 -->
                  <div
                    v-else-if="data.level === 3 || data.label == 'CNKI文献'"
                    class="node-content level-3-content"
                  >
                    <el-icon class="node-icon">
                      <DocumentCopy />
                    </el-icon>
                    <span class="node-label" :title="data.label">{{ data.label }}</span>
                    <span class="file-size">{{
                        data.label == 'CNKI文献' ? '（184912）' : formatFileSize(data.size)
                      }}</span>
                  </div>
                </div>
              </template>
            </el-tree>
          </div>
        </div>

      </el-aside>
      <el-container>
        <el-header class="header">
          <div style="height: 100%; display: flex; align-items: center">
            <div class="history-icon" @click="openDrawer">
              <el-icon :size="20"><Timer /></el-icon>
            </div>

            <span style="display: flex; align-items: center; width: 100%">
              <el-dropdown trigger="click" @command="handleUserCommand" style="height: fit-content">
                <div class="user-info">
                  <div style="display: flex; align-items: center; margin-left: 8px">
                    <el-badge is-dot v-show="notRead">
                      <span class="username">{{ user.userInfo?.username }}</span>
                    </el-badge>

                    <span class="username" v-show="!notRead">{{ user.userInfo?.username }}</span>
                  </div>

                  <el-icon class="dropdown-icon">
                    <ArrowDown />
                  </el-icon>
                </div>

                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="messages">
                      <el-icon><Message /></el-icon>
                      <el-badge is-dot v-show="notRead"> 消息通知 </el-badge>
                      <span v-show="!notRead"> 消息通知 </span>
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </span>
          </div>

          <el-drawer
            v-model="drawer"
            :beforeClose="closeDrawer"
            title="消息中心"
            :direction="'rtl'"
          >
            <div
              v-loading="msgLoading"
              style="display: flex; flex-direction: column; gap: 12px; min-height: 100px"
            >
              <MessageCard
                v-for="item in messages"
                :key="item.log_id"
                :msg="item.msg"
                @click="() => readMsg(item.log_id)"
                :create-time="item.create_time"
                :log-read="item.log_read"
              />
            </div>
          </el-drawer>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import {
  ArrowDown,
  Check,
  Close,
  Delete,
  DocumentCopy,
  Edit,
  EditPen,
  Folder,
  FolderRemove,
  Plus,
  Refresh,
  Search,
  Share,
  Sort,
  SwitchButton,
  Timer,
  View
} from '@element-plus/icons-vue'
import { computed, onBeforeMount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import documentApi from '@/api/document'
import datasetApi from '@/api/dataset'
import useStore from '@/stores'
import { getMessages, type Message, readMessage } from '@/api/messages'
import MessageCard from '@/layout/layout-template/MessageCard.vue'
import modelApi from '@/api/model'
import {MoreOne} from "@icon-park/vue-next";

// 类型定义
interface TreeNode {
  id: string
  label: string
  level: number
  type: string
  icon?: string
  checked?: boolean
  children?: TreeNode[]
  permission?: string
  shared_with_type?: string
  team_permission?: string
  datasetId?: string
  documentId?: string
  description?: string
  documentCount?: number
  size?: number
  status?: string
}

const router = useRouter()
const { user } = useStore()
const drawer = ref(false)
const messages = ref<Message[]>([])
const userRole = computed(() => user.getRole())
const selectedNode = ref<TreeNode | null>(null)
const isAdmin = computed(() => userRole.value === 'ADMIN')
const personalKBSortType = ref<'time' | 'name'>('time') // 默认按时间排序（创建时间倒排）
const sharedKBSortType = ref<'time' | 'name'>('time') // 共享知识库排序类型
const organizationKBSortType = ref<'time' | 'name'>('time') // 机构知识库排序类型
const treeRef = ref<any>(null)
const sharedKBs = ref<any[]>([])
const organizationKBs = ref<any[]>([])
const searchText = ref('')
const selectedKB = ref<TreeNode | null>(null)
const personalKBs = ref<any[]>([])
// 树形数据
const treeData = ref<TreeNode[]>([
  {
    id: 'org',
    label: '机构知识库',
    level: 1,
    type: 'organization',
    icon: 'OfficeBuilding',
    checked: false,
    children: []
  },
  {
    id: 'shared',
    label: '共享知识库',
    level: 1,
    type: 'shared',
    icon: 'Share',
    checked: false,
    children: []
  },
  {
    id: 'my',
    label: '我的知识库',
    level: 1,
    type: 'personal',
    icon: 'User',
    checked: false,
    children: []
  }
])

// 树形组件配置
const treeProps = {
  children: 'children',
  label: 'label'
}

const goToHome = () => {
  if (router.currentRoute.value.path === '/user-home') {
    return
  }
  router.push('/user-home')
}

const useLoading = () => {
  const loading = ref(false)

  const setLoading = (value: boolean) => {
    loading.value = value
  }

  return {
    loading,
    setLoading
  }
}

const { loading: msgLoading, setLoading: setMsgLoading } = useLoading()

const { loading: notRead, setLoading: setNotRead } = useLoading()

// 打开消息通知抽屉
const openDrawer = async () => {
  drawer.value = true
  await loadMessages(true)
}

// 关闭消息通知抽屉
const closeDrawer = () => {
  drawer.value = false
  loadMessages(false)
}

const loadMessages = async (isLoading: boolean) => {
  if (isLoading) {
    setMsgLoading(true)
  }
  setNotRead(false)
  const result = await getMessages()
  if (result.code === 200) {
    messages.value = result.data
    if (!messages.value.some((item) => !item.log_read)) {
      setNotRead(false)
    } else {
      setNotRead(true)
    }
  }
  if (isLoading) {
    setMsgLoading(false)
  }
}

let interval: any
onMounted(() => {
  loadMessages(false)
  interval = setInterval(() => {
    loadMessages(false)
  }, 60000)
})
onBeforeMount(() => {
  clearInterval(interval)
})

// 已读回调
const readMsg = async (log_id: string) => {
  const result = await readMessage(log_id)
  if (result.code === 200) {
    messages.value = messages.value.map((item) => {
      if (item.log_id === log_id) {
        item.log_read = true
      }
      return item
    })
  }
}

// 处理用户下拉菜单命令
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'messages':
      await openDrawer()
      break
    case 'profile':
      ElMessage.info('个人信息功能开发中...')
      break
    case 'settings':
      ElMessage.info('设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '退出确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await user.logout()
        router.push('/login')
        ElMessage.success('已退出登录')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('退出登录失败')
        }
      }
      break
  }
}

// 计算属性：根据搜索文本过滤树形数据
const filteredTreeData = computed(() => {
  if (!searchText.value.trim()) {
    return treeData.value
  }

  const searchLower = searchText.value.toLowerCase()

  // 递归过滤树形数据
  const filterTree = (nodes: TreeNode[]): TreeNode[] => {
    return nodes
      .map((node) => {
        // 检查当前节点是否匹配
        const labelMatch = node.label?.toLowerCase().includes(searchLower)

        // 递归过滤子节点
        const filteredChildren = node.children ? filterTree(node.children) : []

        // 如果当前节点匹配或有子节点匹配，则保留该节点
        if (labelMatch || filteredChildren.length > 0) {
          return {
            ...node,
            children: filteredChildren
          }
        }

        return null
      })
      .filter((node) => node !== null) as TreeNode[]
  }

  return filterTree(treeData.value)
})

// 方法
const selectKnowledgeBase = (kb: TreeNode) => {
  selectedKB.value = kb
  // 清空之前的对话
  // chatMessages.value = [] // 临时注释，测试消息保持
}

// 显示文档详情
const showDocumentDetail = (document: TreeNode) => {
  console.log('显示文档详情:', document)
  // 这里可以在主内容区域显示文档详情
}

// 处理树节点点击
const handleNodeClick = (data: TreeNode) => {
  selectedNode.value = data

  if (data.level === 2) {
    // 点击知识库，切换到该知识库
    selectKnowledgeBase(data)
  } else if (data.level === 3) {
    // 点击文档，显示文档详情
    showDocumentDetail(data)
  }
}

// 更新节点的子节点
const updateNodeChildren = (nodeId: string, children: TreeNode[]) => {
  const findAndUpdate = (nodes: TreeNode[]): boolean => {
    for (let node of nodes) {
      if (node.id === nodeId) {
        node.children = children
        // 同时更新文档数量统计
        node.documentCount = children.length
        return true
      }
      if (node.children && findAndUpdate(node.children)) {
        return true
      }
    }
    return false
  }

  findAndUpdate(treeData.value)
}

// 加载知识库下的文档
const loadDocuments = async (datasetId: string, parentNodeId: string) => {
  try {
    const response = await documentApi.getAllDocument(datasetId)

    if (response.data) {
      // 只显示启用状态的文档 (is_active 为 true 的文档)
      const documents: TreeNode[] = response.data
        .filter((doc: any) => doc.is_active !== false)
        .map((doc: any) => ({
          id: `doc_${doc.id}`,
          label: doc.name,
          level: 3,
          type: 'document',
          documentId: doc.id,
          datasetId: datasetId,
          size: doc.char_length || 0,
          status: doc.status
        }))

      // 更新对应节点的children
      updateNodeChildren(parentNodeId, documents)
    }
  } catch (error) {
    console.error('加载文档失败:', error)
  }
}

// 处理节点展开
const handleNodeExpand = async (data: TreeNode) => {
  // 如果是二级节点（知识库）且还没有加载文档，则加载文档
  if (data.level === 2 && data.datasetId && (!data.children || data.children.length === 0)) {
    await loadDocuments(data.datasetId, data.id)
  }
}

// 获取选中项目的统计信息
const getSelectedStats = () => {
  const checkedNodes = treeRef.value?.getCheckedNodes() || []

  const stats = {
    categories: 0, // 一级目录数量
    datasets: 0, // 知识库数量
    documents: 0, // 文档数量
    selectedNodes: checkedNodes
  }

  checkedNodes.forEach((node: TreeNode) => {
    switch (node.level) {
      case 1:
        stats.categories++
        break
      case 2:
        stats.datasets++
        break
      case 3:
        stats.documents++
        break
    }
  })

  return stats
}

// 处理复选框选择
const handleNodeCheck = (data: TreeNode, checkInfo: any) => {
  // 获取所有选中的节点
  const checkedNodes = treeRef.value?.getCheckedNodes() || []
  const checkedKeys = treeRef.value?.getCheckedKeys() || []

  // 分类统计选中的项目
  const selectedStats = getSelectedStats()
}

const showRenameDialog = ref(false)
const currentDatasetId = ref('')
const showShareModal = ref(false)
const showDocumentModal = ref(false)
const currentDatasetName = ref('')
const renameForm = ref({
  id: '',
  name: '',
  oldName: '' // 保存原始名称，用于日志和验证
})

// 处理知识库操作
const handleKBAction = async (command: { action: string; data: TreeNode }) => {
  const { action, data } = command

  try {
    switch (action) {
      case 'rename':
        const targetId = data.datasetId || data.id

        renameForm.value = {
          id: targetId,
          name: data.label,
          oldName: data.label // 保存原始名称
        }
        showRenameDialog.value = true
        break

      case 'share':
        currentDatasetId.value = data.datasetId || data.id
        currentDatasetName.value = data.label
        showShareModal.value = true
        break

      case 'delete':
        await ElMessageBox.confirm(
          `确定要删除知识库"${data.label}"吗？此操作不可恢复。`,
          '删除确认',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        if (data.datasetId) {
          await datasetApi.delDataset(data.datasetId)
          ElMessage.success('删除成功')
          // 刷新对应的知识库列表
          refreshKnowledgeBase('personal')
        }
        break

      case 'exit-share':
        await ElMessageBox.confirm(`确定要退出共享知识库"${data.label}"吗？`, '退出共享确认', {
          confirmButtonText: '确定退出',
          cancelButtonText: '取消',
          type: 'warning'
        })

        if (data.datasetId) {
          await datasetApi.putExitShare(data.datasetId)
          ElMessage.success('已退出共享')
          // 刷新共享知识库列表
          refreshKnowledgeBase('shared')
        }
        break

      case 'remove-from-org':
        if (!isAdmin.value) {
          ElMessage.error('无权限执行此操作')
          return
        }

        await ElMessageBox.confirm(`确定要将知识库"${data.label}"移出机构吗？`, '移出机构确认', {
          confirmButtonText: '确定移出',
          cancelButtonText: '取消',
          type: 'warning'
        })

        if (data.datasetId) {
          await datasetApi.removeFromOrganization(data.datasetId)
          ElMessage.success('已移出机构')
          // 刷新机构知识库列表
          refreshKnowledgeBase('organization')
        }
        break

      case 'view':
        console.log('查看详情:', data.label)
        // 打开文档管理弹窗
        // 使用datasetId而不是带前缀的id
        currentDatasetId.value = data.datasetId || data.id
        currentDatasetName.value = data.label
        showDocumentModal.value = true
        break

      default:
        console.log('未知操作:', action)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error('操作失败：' + (error.message || '未知错误'))
    }
  }
}

// 获取知识库类型
const getKBType = (data: TreeNode): string => {
  // 通过父节点或ID前缀确定知识库类型
  if (data.id.includes('org_')) return 'organization'
  if (data.id.includes('shared_')) return 'shared'
  if (data.id.includes('my_')) return 'personal'

  // 备用判断：通过TreeRef查找父节点
  const allNodes = treeRef.value?.store?.nodesMap
  if (allNodes && data.id) {
    const currentNode = allNodes[data.id]
    if (currentNode?.parent?.data?.type) {
      return currentNode.parent.data.type
    }
  }

  return 'personal' // 默认值
}

// 加载机构知识库
const loadOrganizationKBs = async () => {
  try {
    const page = { current_page: 1, page_size: 100 }
    const response = await datasetApi.getOrganizationDataset(page, {})

    console.log('机构知识库API响应:', response)

    if (response.data) {
      const orgKBsList = response.data.records || []
      console.log(
        '获取到的机构知识库列表:',
        orgKBsList.map((kb: any) => ({
          id: kb.id,
          name: kb.name,
          create_time: kb.create_time,
          creator: kb.user?.username || '未知'
        }))
      )

      orgKBsList.push({
        id: 'd1f6f1cc-b3c3-11f0-9ffe-1df6b9a97505',
        name: 'CNKI文献',
        create_time: '2024-01-01T00:00:00Z',
        creator: '系统集成'
      })

      organizationKBs.value = orgKBsList

      // 加载后立即应用排序
      await sortOrganizationKBs()
    }
  } catch (error) {
    console.error('加载机构知识库失败:', error)
  }
}

// 加载共享知识库
const loadSharedKBs = async () => {
  try {
    const page = { current_page: 1, page_size: 100 }
    const response = await datasetApi.getSharedToMeDataset(page, {})

    console.log('共享知识库API响应:', response)

    if (response.data) {
      const sharedKBsList = response.data.records || []
      console.log(
        '获取到的共享知识库列表:',
        sharedKBsList.map((kb: any) => ({
          id: kb.id,
          name: kb.name,
          create_time: kb.create_time,
          creator: kb.user?.username || '未知',
          shared_user_count: kb.shared_user_count || 0,
          permission: kb.permission, // 添加权限信息
          shared_with_type: kb.shared_with_type,
          team_permission: kb.team_permission
        }))
      )

      // 打印原始权限数据
      sharedKBsList.forEach((kb: any) => {
        console.log('知识库权限详情:', {
          name: kb.name,
          permission: kb.permission,
          shared_with_type: kb.shared_with_type,
          team_permission: kb.team_permission,
          shared_with_id: kb.shared_with_id
        })
      })

      sharedKBs.value = sharedKBsList

      // 加载后立即应用排序
      await sortSharedKBs()
    }
  } catch (error) {
    console.error('加载共享知识库失败:', error)
  }
}

// 加载个人知识库
const loadPersonalKBs = async () => {
  try {
    const page = { current_page: 1, page_size: 100 }
    const response = await datasetApi.getDataset(page, {})

    if (response.data) {
      personalKBs.value = response.data.records || []

      // 加载后立即应用排序
      await sortPersonalKBs()
    }
  } catch (error) {
    console.error('加载个人知识库失败:', error)
  }
}

// 刷新知识库数据
const refreshKnowledgeBase = async (type: string) => {
  try {
    switch (type) {
      case 'organization':
        await loadOrganizationKBs()
        break
      case 'shared':
        await loadSharedKBs()
        break
      case 'personal':
        await loadPersonalKBs()
        break
    }
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

// 排序个人知识库
const sortPersonalKBs = async () => {
  try {
    if (personalKBs.value.length === 0) return

    // 复制数组并深拷贝每个对象，确保使用最新数据
    let sortedKBs = personalKBs.value.map((kb) => ({
      ...kb,
      description: kb.description,
      desc: kb.desc
    }))

    // 调试：打印排序前的数据，确认更新是否生效
    console.log(
      '排序前的knowledge bases:',
      sortedKBs.map((kb) => ({
        id: kb.id,
        name: kb.name,
        desc: kb.desc,
        description: kb.description
      }))
    )

    if (personalKBSortType.value === 'time') {
      // 按创建时间倒序排列（最新的在前面）
      sortedKBs.sort((a, b) => {
        const timeA = new Date(a.create_time || a.created_at || '').getTime()
        const timeB = new Date(b.create_time || b.created_at || '').getTime()
        return timeB - timeA // 倒序
      })
    } else if (personalKBSortType.value === 'name') {
      // 按名称正序排列（A-Z）
      sortedKBs.sort((a, b) => {
        return sortByName(a.name || '', b.name || '')
      })
    }

    // 将排序后的数组直接用于更新树，不修改personalKBs的引用
    await updateTreeData('my', sortedKBs)

    console.log(`个人知识库已按${personalKBSortType.value === 'time' ? '时间' : '名称'}排序`)
  } catch (error) {
    console.error('排序失败:', error)
  }
}

// 排序机构知识库
const sortOrganizationKBs = async () => {
  try {
    if (organizationKBs.value.length === 0) return

    // 复制数组进行排序
    let sortedKBs = [...organizationKBs.value]

    if (organizationKBSortType.value === 'time') {
      // 按创建时间倒序排列（最新的在前面）
      sortedKBs.sort((a, b) => {
        const timeA = new Date(a.create_time || a.created_at || '').getTime()
        const timeB = new Date(b.create_time || b.created_at || '').getTime()
        return timeB - timeA // 倒序
      })
    } else if (organizationKBSortType.value === 'name') {
      // 按名称正序排列（A-Z）
      sortedKBs.sort((a, b) => {
        return sortByName(a.name || '', b.name || '')
      })
    }

    // 更新排序后的数据
    organizationKBs.value = sortedKBs
    await updateTreeData('org', sortedKBs)

    console.log(
      `机构知识库已按${organizationKBSortType.value === 'time' ? '创建时间' : '名称'}排序`
    )
  } catch (error) {
    console.error('机构知识库排序失败:', error)
  }
}

// 按名称排序函数（支持中英文混合）
const sortByName = (a: string, b: string): number => {
  // 获取字符类型优先级：数字(0) < 英文大写(A-Z, 1) < 英文小写(a-z, 2) < 中文(3)
  const getCharPriority = (char: string): number => {
    const code = char.charCodeAt(0)
    if (code >= 48 && code <= 57) return 0 // 数字 0-9
    if (code >= 65 && code <= 90) return 1 // 大写 A-Z
    if (code >= 97 && code <= 122) return 2 // 小写 a-z
    if (/[\u4e00-\u9fa5]/.test(char)) return 3 // 中文
    return 4 // 其他字符
  }

  const lenA = a.length
  const lenB = b.length
  const minLen = Math.min(lenA, lenB)

  // 逐字符比较
  for (let i = 0; i < minLen; i++) {
    const charA = a[i]
    const charB = b[i]
    const priorityA = getCharPriority(charA)
    const priorityB = getCharPriority(charB)

    // 类型不同，按类型优先级排序
    if (priorityA !== priorityB) {
      return priorityA - priorityB
    }

    // 类型相同，按字符ASCII值排序
    if (charA !== charB) {
      if (priorityA === 3) {
        // 中文字符使用拼音排序
        return charA.localeCompare(charB, 'zh-CN')
      }
      return charA.charCodeAt(0) - charB.charCodeAt(0)
    }
  }

  // 前面的字符都相同，比较长度
  return lenA - lenB
}

// 更新树形数据
const updateTreeData = async (categoryId: string, datasets: any[]) => {
  const categoryIndex = treeData.value.findIndex((item) => item.id === categoryId)
  if (categoryIndex === -1) return

  const children: TreeNode[] = []

  // 为每个知识库创建节点并加载其文档
  for (const dataset of datasets) {
    const datasetNode: TreeNode = {
      id: `${categoryId}_${dataset.id}`,
      label: dataset.name,
      level: 2,
      type: 'dataset',
      datasetId: dataset.id,
      description: dataset.description || dataset.desc,
      documentCount: dataset.document_count || 0,
      permission: dataset.permission, // 添加权限信息
      shared_with_type: dataset.shared_with_type,
      team_permission: dataset.team_permission,
      children: [] // 先设置为空数组，稍后加载文档
    }

    // 立即加载该知识库的文档
    try {
      const docResponse = await documentApi.getAllDocument(dataset.id)
      if (docResponse.data && docResponse.data.length > 0) {
        // 只显示启用状态的文档 (is_active 为 true 的文档)
        datasetNode.children = docResponse.data
          .filter((doc: any) => doc.is_active !== false && doc.status == 'nn2')
          .map((doc: any) => ({
            id: `doc_${doc.id}`,
            label: doc.name,
            level: 3,
            type: 'document',
            documentId: doc.id,
            datasetId: dataset.id,
            size: doc.char_length || 0,
            status: doc.status
          }))
        // 更新文档数量为实际过滤后的文档数
        datasetNode.documentCount = datasetNode.children?.length || 0
      } else {
        // 如果没有文档，设置为0
        datasetNode.documentCount = 0
      }
    } catch (error) {
      console.error(`加载知识库 ${dataset.name} 的文档失败:`, error)
      datasetNode.documentCount = 0
    }

    children.push(datasetNode)
  }

  treeData.value[categoryIndex].children = children
}

// 排序共享知识库
const sortSharedKBs = async () => {
  try {
    if (sharedKBs.value.length === 0) return

    // 复制数组进行排序
    let sortedKBs = [...sharedKBs.value]

    if (sharedKBSortType.value === 'time') {
      // 按创建时间倒序排列（最新的在前面）
      sortedKBs.sort((a, b) => {
        const timeA = new Date(a.create_time || a.created_at || '').getTime()
        const timeB = new Date(b.create_time || b.created_at || '').getTime()
        return timeB - timeA // 倒序
      })
    } else if (sharedKBSortType.value === 'name') {
      // 按名称正序排列（A-Z）
      sortedKBs.sort((a, b) => {
        return sortByName(a.name || '', b.name || '')
      })
    }

    // 更新排序后的数据
    sharedKBs.value = sortedKBs
    await updateTreeData('shared', sortedKBs)

    console.log(`共享知识库已按${sharedKBSortType.value === 'time' ? '创建时间' : '名称'}排序`)
  } catch (error) {
    console.error('共享知识库排序失败:', error)
  }
}

// 处理一级目录的三个点菜单操作
const handleLevel1Action = (command: { action: string; data: TreeNode }) => {
  const { action, data } = command

  switch (action) {
    case 'refresh':
      console.log('刷新', data.label)
      refreshKnowledgeBase(data.type)
      break
    // 个人知识库排序
    case 'sort-by-time':
      console.log('个人知识库按时间排序')
      personalKBSortType.value = 'time'
      localStorage.setItem('personal_kb_sort_type', 'time')
      sortPersonalKBs()
      ElMessage.success('已切换为按时间排序（创建时间倒序）')
      break
    case 'sort-by-name':
      console.log('个人知识库按名称排序')
      personalKBSortType.value = 'name'
      localStorage.setItem('personal_kb_sort_type', 'name')
      sortPersonalKBs()
      ElMessage.success('已切换为按名称排序（A-Z）')
      break
    // 机构知识库排序
    case 'org-sort-by-name':
      console.log('机构知识库按名称排序')
      organizationKBSortType.value = 'name'
      localStorage.setItem('organization_kb_sort_type', 'name')
      sortOrganizationKBs()
      ElMessage.success('机构知识库已切换为按名称排序（A-Z）')
      break
    case 'org-sort-by-time':
      console.log('机构知识库按创建时间排序')
      organizationKBSortType.value = 'time'
      localStorage.setItem('organization_kb_sort_type', 'time')
      sortOrganizationKBs()
      ElMessage.success('机构知识库已切换为按创建时间排序（最新在前）')
      break
    // 共享知识库排序
    case 'shared-sort-by-name':
      console.log('共享知识库按名称排序')
      sharedKBSortType.value = 'name'
      localStorage.setItem('shared_kb_sort_type', 'name')
      sortSharedKBs()
      ElMessage.success('共享知识库已切换为按名称排序（A-Z）')
      break
    case 'shared-sort-by-time':
      console.log('共享知识库按创建时间排序')
      sharedKBSortType.value = 'time'
      localStorage.setItem('shared_kb_sort_type', 'time')
      sortSharedKBs()
      ElMessage.success('共享知识库已切换为按创建时间排序（最新在前）')
      break
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (!bytes) return '-'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}
const selectedModelId = ref('')
const currentUserId = ref('')
const currentUsername = ref('')

// 获取当前用户信息
const getCurrentUserInfo = () => {
  const userInfo = user.userInfo
  if (userInfo) {
    currentUserId.value = userInfo.id || ''
    currentUsername.value = userInfo.username || ''
  }
}

const modelsLoading = ref(false)
const availableModels = ref<any[]>([])

// 加载可用的对话模型列表
const loadAvailableModels = async () => {
  modelsLoading.value = true
  try {
    const res = await modelApi.getModel()
    const list = res.data || []

    console.log('模型列表：', res)
    // 过滤出支持对话的模型
    availableModels.value = list.filter((model) => isChatModel(model))

    // 如果当前没有选择模型，自动选择第一个
    if (!selectedModelId.value && availableModels.value.length > 0) {
      selectedModelId.value = availableModels.value[0].id
      // 更新缓存
      localStorage.setItem('user_knowledge_default_model_id', selectedModelId.value)
    }

    // 如果当前选择的模型不在可用列表中，重新选择
    if (
      selectedModelId.value &&
      !availableModels.value.find((m) => m.id === selectedModelId.value)
    ) {
      selectedModelId.value = availableModels.value.length > 0 ? availableModels.value[0].id : ''
      if (selectedModelId.value) {
        localStorage.setItem('user_knowledge_default_model_id', selectedModelId.value)
      }
    }
  } catch (error) {
    console.error('加载模型列表失败:', error)
    ElMessage.error('加载模型列表失败')
  } finally {
    modelsLoading.value = false
  }
}

// 判断模型是否支持对话
const isChatModel = (model: any): boolean => {
  // 检查模型类型是否为对话类型
  const chatTypes = ['LLM', 'CHAT', 'LLM_CHAT']
  const isCorrectType = chatTypes.includes(model.model_type?.toUpperCase())

  // 检查模型状态是否正常
  const isStatusOk = model.status === 'SUCCESS'

  // 检查是否为嵌入模型（排除）
  const embeddingTypes = ['EMBEDDING', 'EMBED']
  const isNotEmbedding = !embeddingTypes.includes(model.model_type?.toUpperCase())

  const result = isCorrectType && isStatusOk && isNotEmbedding

  return result
}

// 解析默认模型ID（优先选择对话模型）
const resolveDefaultModelId = async (): Promise<string> => {
  const cached = localStorage.getItem('user_knowledge_default_model_id')

  // 如果有缓存，先验证模型是否仍然存在且支持对话
  if (cached) {
    try {
      const res = await modelApi.getModel()
      const list = res.data || []
      const cachedModel = list.find((model) => model.id === cached)

      // 验证缓存的模型是否仍存在且支持对话
      if (cachedModel && isChatModel(cachedModel)) {
        return cached
      } else {
        // 缓存的模型不存在或不支持对话，清除缓存
        localStorage.removeItem('user_knowledge_default_model_id')
      }
    } catch (e) {
      console.warn('验证缓存模型失败:', e)
    }
  }

  // 获取新的对话模型
  try {
    const res = await modelApi.getModel()
    const list = res.data || []

    // 优先选择支持对话的模型
    const chatModels = list.filter((model) => isChatModel(model))

    if (chatModels.length > 0) {
      const selectedModel = chatModels[0]
      localStorage.setItem('user_knowledge_default_model_id', selectedModel.id)
      return selectedModel.id
    } else {
      console.warn('未找到支持对话的模型')
    }
  } catch (e) {
    console.warn('获取默认模型失败', e)
  }
  return ''
}

// STT相关状态
const sttModelEnabled = ref(false)
const sttAutoSend = ref(false)
const availableSTTModels = ref<any[]>([])
const selectedSTTModelId = ref('')

// 加载可用的STT模型列表
const loadAvailableSTTModels = async () => {
  try {
    // 从全局模型列表中过滤出STT模型
    const res = await modelApi.getModel()
    const list = res.data || []

    // 过滤出STT类型的模型
    const sttModels = list.filter((model) => model.model_type === 'STT')

    if (sttModels.length > 0) {
      availableSTTModels.value = sttModels
      sttModelEnabled.value = true

      // 自动选择第一个STT模型
      if (!selectedSTTModelId.value) {
        selectedSTTModelId.value = sttModels[0].id
      }
    } else {
      sttModelEnabled.value = false
    }
  } catch (error) {
    console.error('加载STT模型失败:', error)
    sttModelEnabled.value = false
  }
}

onMounted(async () => {
  // 获取当前用户信息
  getCurrentUserInfo()

  // 从缓存中恢复选择的模型
  const cachedModelId = localStorage.getItem('user_knowledge_default_model_id')
  if (cachedModelId) {
    selectedModelId.value = cachedModelId
  } else {
    // 如果没有缓存模型，自动选择一个默认模型
    try {
      const defaultModelId = await resolveDefaultModelId()
      if (defaultModelId) {
        selectedModelId.value = defaultModelId
      }
    } catch (error) {
      console.warn('获取默认模型失败:', error)
    }
  }

  // 从缓存中恢复排序偏好
  const cachedSortType = localStorage.getItem('personal_kb_sort_type') as 'time' | 'name'
  if (cachedSortType && ['time', 'name'].includes(cachedSortType)) {
    personalKBSortType.value = cachedSortType
  }

  // 恢复机构知识库排序偏好
  const cachedOrgSortType = localStorage.getItem('organization_kb_sort_type') as 'time' | 'name'
  if (cachedOrgSortType && ['time', 'name'].includes(cachedOrgSortType)) {
    organizationKBSortType.value = cachedOrgSortType
  }

  // 恢复共享知识库排序偏好
  const cachedSharedSortType = localStorage.getItem('shared_kb_sort_type') as 'time' | 'name'
  if (cachedSharedSortType && ['time', 'name'].includes(cachedSharedSortType)) {
    sharedKBSortType.value = cachedSharedSortType
  }

  // 并行加载知识库、模型列表和STT模型
  await Promise.all([
    loadOrganizationKBs(),
    loadSharedKBs(),
    loadPersonalKBs(),
    loadAvailableModels(),
    loadAvailableSTTModels()
  ])
})
</script>

<style lang="scss" scoped>
.line-split {
  height: 1px;
  background: rgb(209, 214, 226);
  margin: 10px 10px;
}

.common-layout {
  height: 100vh;
  width: 100vw;

  .icon-box {
    width: 100%;
    display: flex;
    justify-content: space-around;
    align-items: center;

    .logo-img {
      height: 60px;
    }

    .home-icon {
      cursor: pointer;
    }
    .home-icon:hover {
      color: #409eff;
    }
  }

  .input-box {
    display: flex;
    justify-content: center;
    margin-top: 18px;

    :deep(.el-input__wrapper) {
      background: rgb(236, 240, 246);
    }
  }

  .add-btn {
    display: flex;
    justify-content: center;
    margin-top: 14px;
  }

  .home-item {
    &:hover {
      color: #409eff;
      background: #dfdfdf;
    }
    cursor: pointer;
    display: flex;
    padding: 10px 0;
    justify-content: center;
    margin-top: 14px;

    .home-item-box {
      width: 240px;
      display: flex;
      justify-content: space-between;

      .arrow-icon {
        display: flex;
        align-items: center;
      }
    }

    .item-icon {
      display: flex;
      align-content: center;

      div {
        font-size: 16px;
        margin-left: 6px;
        display: flex;
        align-items: center;
      }
    }
  }

  .header {
    border-bottom: 1px solid rgb(237, 237, 237);
    display: flex;
    justify-content: flex-end;
    align-content: center;

    :deep(.el-dropdown) {
      display: flex;
      align-content: center;
    }

    .user-info {
      height: fit-content;
      display: flex;

      .dropdown-icon {
        margin-left: 14px;
      }
    }

    .history-icon {
      height: 100%;
      display: flex;
      align-items: center;
      margin-right: 10px;
      cursor: pointer;

      &:hover {
        color: #409eff;
      }
    }
  }
}

.knowledge-tree {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;

  /* 自定义滚动条样式 */
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #f8fafc;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;

    &:hover {
      background: #a8a8a8;
    }
  }

  .knowledge-tree-container {
    border: none;
    background: transparent;

    :deep(.el-tree-node) {
      margin-bottom: 4px;

      .el-tree-node__content {
        height: auto;
        padding: 4px 0;
        background: transparent;
        border-radius: 6px;

        &:hover {
          background: #f5f7fa !important;
        }
      }

      .el-tree-node__expand-icon {
        padding: 6px;
        font-size: 12px;
        color: #909399;

        &.is-leaf {
          color: transparent;
        }
      }

      .el-checkbox {
        margin-right: 8px;

        .el-checkbox__input {
          .el-checkbox__inner {
            width: 16px;
            height: 16px;
            border-radius: 3px;
          }
        }
      }
    }
  }

  .tree-node {
    width: 80%;

    &.active {
      .node-content {
        background: #e6f3ff;
        border: 1px solid #3370ff;
      }
    }
  }

  .node-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 2px 12px;
    border-radius: 6px;
    transition: all 0.3s ease;
    min-height: 36px;

    &.level-1-content {
      font-weight: 600;
      background: #f8fafc;
      margin-bottom: 4px;

      .node-left {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
        min-width: 0;
      }

      .node-icon {
        color: #3370ff;
        font-size: 16px;
      }

      .node-label {
        color: #2c3e50;
        font-size: 14px;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .more-actions {
        color: #909399;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;

        &:hover {
          background: #e9ecef;
          color: #606266;
        }
      }
    }

    &.level-2-content {
      padding-left: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;

      .node-left {
        display: flex;
        align-items: center;
        flex: 1;
        min-width: 0;
      }

      .node-icon {
        color: #67c23a;
        font-size: 14px;
        margin-right: 8px;
        flex-shrink: 0;
      }

      .node-label {
        color: #303133;
        font-size: 13px;
        font-weight: 500;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .doc-count {
        color: #909399;
        font-size: 12px;
        margin-left: 6px;
      }

      .more-actions {
        opacity: 0;
        transition: opacity 0.2s;
        cursor: pointer;
        padding: 2px;
        font-size: 14px;
        color: #909399;

        &:hover {
          color: #409eff;
        }
      }

      &:hover .more-actions {
        opacity: 1;
      }
    }

    &.level-3-content {
      padding-left: 10px;
      display: flex;
      align-items: center;

      .node-icon {
        color: #e6a23c;
        font-size: 12px;
        margin-right: 8px;
        flex-shrink: 0;
      }

      .node-label {
        color: #606266;
        font-size: 12px;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .file-size {
        color: #c0c4cc;
        font-size: 11px;
        margin-left: 8px;
        flex-shrink: 0;
      }
    }
  }
}

.container {
  display: flex;
  flex-direction: column;
  height: 100vh; /* 或具体高度如 500px */
}

.first {
  height: fit-content;  /* 根据内容自适应 */
}

.second {
  flex: 1;  /* 铺满剩余高度 */
}
</style>
