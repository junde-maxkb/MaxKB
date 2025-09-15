<template>
  <div class="user-knowledge-container">
    <div class="knowledge-layout">
      <!-- 侧边栏 -->
      <div class="knowledge-sidebar">
        <div class="sidebar-header">
          <h3>知识库列表</h3>
          <el-button 
            type="primary" 
            size="small" 
            class="create-btn"
            @click="showCreateDialog = true"
          >
            <el-icon><Plus /></el-icon>
            新建知识库
          </el-button>
        </div>
        
        <div class="sidebar-content">
          <div class="knowledge-search">
            <el-input
              v-model="searchText"
              placeholder="搜索知识库..."
              prefix-icon="Search"
              size="small"
            />
          </div>
          
          <div class="knowledge-list">
            <div 
              v-for="kb in filteredKnowledgeBases" 
              :key="kb.id"
              class="knowledge-item"
              :class="{ active: selectedKB?.id === kb.id }"
              @click="selectKnowledgeBase(kb)"
            >
              <div class="kb-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="kb-info">
                <div class="kb-name">{{ kb.name }}</div>
                <div class="kb-desc">{{ kb.description }}</div>
              </div>
            </div>
            
            <div v-if="filteredKnowledgeBases.length === 0" class="empty-state">
              <el-icon><DocumentDelete /></el-icon>
              <p>暂无知识库</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 主内容区域 -->
      <div class="knowledge-main">
        <div v-if="!selectedKB" class="welcome-content">
          <div class="welcome-icon">
            <el-icon><ChatDotSquare /></el-icon>
          </div>
          <h2>请选择知识库</h2>
          <p>从左侧选择一个知识库开始问答</p>
        </div>
        
        <div v-else class="chat-content">
          <div class="chat-header">
            <h2>{{ selectedKB.name }}</h2>
            <p>{{ selectedKB.description }}</p>
          </div>
          
          <div class="chat-area">
            <div class="chat-messages" ref="messagesContainer">
              <div 
                v-for="message in messages" 
                :key="message.id"
                class="message"
                :class="message.type"
              >
                <div class="message-content">
                  <div class="message-text">{{ message.text }}</div>
                  <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                </div>
              </div>
            </div>
            
            <div class="chat-input-area">
              <div class="input-container">
                <div class="input-wrapper">
                  <el-input
                    v-model="currentMessage"
                    type="textarea"
                    :rows="3"
                    placeholder="请输入您的问题..."
                    class="chat-input"
                    @keydown.ctrl.enter="sendMessage"
                  />
                  <div class="input-actions">
                    <el-button 
                      type="primary" 
                      class="send-btn"
                      @click="sendMessage"
                      :loading="isLoading"
                      :disabled="!currentMessage.trim()"
                    >
                      发送
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 创建知识库对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建知识库"
      width="500px"
    >
      <el-form :model="newKB" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="newKB.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="newKB.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入知识库描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createKnowledgeBase">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Plus, 
  Search, 
  Document, 
  DocumentDelete, 
  ChatDotSquare 
} from '@element-plus/icons-vue'

// 响应式数据
const searchText = ref('')
const selectedKB = ref(null)
const currentMessage = ref('')
const isLoading = ref(false)
const showCreateDialog = ref(false)
const messagesContainer = ref(null)

// 新建知识库表单
const newKB = ref({
  name: '',
  description: ''
})

// 模拟知识库数据
const knowledgeBases = ref([
  {
    id: 1,
    name: '产品文档',
    description: '产品功能和使用说明文档'
  },
  {
    id: 2,
    name: '技术规范',
    description: '技术开发和API接口文档'
  },
  {
    id: 3,
    name: '常见问题',
    description: 'FAQ和问题解答汇总'
  }
])

// 消息列表
const messages = ref([])

// 计算属性
const filteredKnowledgeBases = computed(() => {
  if (!searchText.value) {
    return knowledgeBases.value
  }
  return knowledgeBases.value.filter(kb => 
    kb.name.toLowerCase().includes(searchText.value.toLowerCase()) ||
    kb.description.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

// 方法
const selectKnowledgeBase = (kb: any) => {
  selectedKB.value = kb
  messages.value = [
    {
      id: 1,
      type: 'system',
      text: `您好！我是${kb.name}的智能助手，有什么问题可以问我。`,
      timestamp: new Date()
    }
  ]
}

const sendMessage = async () => {
  if (!currentMessage.value.trim() || isLoading.value) return
  
  const userMessage = {
    id: Date.now(),
    type: 'user',
    text: currentMessage.value,
    timestamp: new Date()
  }
  
  messages.value.push(userMessage)
  
  // 清空输入框
  const messageToSend = currentMessage.value
  currentMessage.value = ''
  
  // 显示加载状态
  isLoading.value = true
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 模拟AI回复
  setTimeout(() => {
    const aiMessage = {
      id: Date.now() + 1,
      type: 'assistant',
      text: `这是对"${messageToSend}"的回复。这里将集成实际的问答功能，基于所选知识库的内容进行智能回答。`,
      timestamp: new Date()
    }
    
    messages.value.push(aiMessage)
    isLoading.value = false
    
    nextTick(() => {
      scrollToBottom()
    })
  }, 1500)
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (timestamp: Date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(timestamp)
}

const createKnowledgeBase = () => {
  if (!newKB.value.name.trim()) {
    ElMessage.warning('请输入知识库名称')
    return
  }
  
  const newKnowledgeBase = {
    id: Date.now(),
    name: newKB.value.name,
    description: newKB.value.description || '暂无描述'
  }
  
  knowledgeBases.value.push(newKnowledgeBase)
  
  // 重置表单
  newKB.value = {
    name: '',
    description: ''
  }
  
  showCreateDialog.value = false
  ElMessage.success('知识库创建成功')
}

onMounted(() => {
  // 组件挂载后的初始化逻辑
})
</script>

<style lang="scss" scoped>
.user-knowledge-container {
  height: calc(100vh - 64px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.knowledge-layout {
  display: flex;
  height: 100%;
}

.knowledge-sidebar {
  width: 300px;
  background: #ffffff;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  
  .sidebar-header {
    padding: 20px;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      margin: 0;
      color: #2c3e50;
      font-size: 18px;
      font-weight: 600;
    }
    
    .create-btn {
      border-radius: 6px;
      font-size: 14px;
      padding: 8px 16px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
      
      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
      }
    }
  }
  
  .sidebar-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 20px;
  }
  
  .knowledge-search {
    margin-bottom: 20px;
  }
  
  .knowledge-list {
    flex: 1;
    overflow-y: auto;
  }
  
  .knowledge-item {
    display: flex;
    align-items: center;
    padding: 12px;
    margin-bottom: 8px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      background: #f5f7fa;
    }
    
    &.active {
      background: #e6f3ff;
      border: 1px solid #3370ff;
    }
    
    .kb-icon {
      margin-right: 12px;
      color: #3370ff;
      font-size: 18px;
    }
    
    .kb-info {
      flex: 1;
      
      .kb-name {
        font-weight: 500;
        color: #303133;
        margin-bottom: 4px;
      }
      
      .kb-desc {
        font-size: 12px;
        color: #909399;
        line-height: 1.4;
      }
    }
  }
  
  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #909399;
    
    .el-icon {
      font-size: 48px;
      margin-bottom: 16px;
    }
    
    p {
      margin: 0;
    }
  }
}

.knowledge-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  
  .welcome-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: #909399;
    
    .welcome-icon {
      font-size: 80px;
      margin-bottom: 20px;
      color: #c0c4cc;
    }
    
    h2 {
      margin: 0 0 10px 0;
      color: #606266;
    }
    
    p {
      margin: 0;
    }
  }
  
  .chat-content {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  
  .chat-header {
    padding: 20px;
    background: white;
    border-bottom: 1px solid #e4e7ed;
    
    h2 {
      margin: 0 0 8px 0;
      color: #303133;
      font-size: 18px;
    }
    
    p {
      margin: 0;
      color: #909399;
      font-size: 14px;
    }
  }
  
  .chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .chat-messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    background: white;
    
    .message {
      margin-bottom: 20px;
      
      &.user {
        display: flex;
        justify-content: flex-end;
        
        .message-content {
          max-width: 70%;
          background: #3370ff;
          color: white;
          padding: 12px 16px;
          border-radius: 18px 18px 4px 18px;
        }
      }
      
      &.assistant, &.system {
        display: flex;
        justify-content: flex-start;
        
        .message-content {
          max-width: 70%;
          background: #f0f2f5;
          color: #303133;
          padding: 12px 16px;
          border-radius: 18px 18px 18px 4px;
        }
      }
      
      .message-text {
        line-height: 1.6;
        word-wrap: break-word;
      }
      
      .message-time {
        font-size: 12px;
        opacity: 0.7;
        margin-top: 4px;
      }
    }
  }
  
  .chat-input-area {
    padding: 20px;
    background: white;
    border-top: 1px solid #e9ecef;
    
    .input-container {
      .input-wrapper {
        background: #ffffff;
        border: 1px solid var(--el-border-color-light);
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
        
        &:has(.el-textarea__inner:focus) {
          border-color: var(--el-color-primary);
          box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
        }
        
        .chat-input {
          :deep(.el-textarea__inner) {
            border: none;
            box-shadow: none;
            padding: 0;
            background: transparent;
            font-size: 14px;
            line-height: 1.5;
            resize: none;
            
            &::placeholder {
              color: var(--el-text-color-placeholder);
            }
          }
        }
        
        .input-actions {
          border-top: 1px solid var(--el-border-color-lighter);
          padding-top: 12px;
          margin-top: 12px;
          text-align: right;
          
          .send-btn {
            border-radius: 6px;
            font-size: 14px;
            padding: 8px 24px;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
            
            &:hover:not(:disabled) {
              transform: translateY(-1px);
              box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
            }
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .knowledge-layout {
    flex-direction: column;
  }
  
  .knowledge-sidebar {
    width: 100%;
    height: 200px;
  }
  
  .knowledge-main {
    flex: 1;
  }
}
</style>
