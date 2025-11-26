<template>
  <div class="chat-page" :class="{ 'chat-mode': chatList.length > 0 }">
    <!-- 聊天内容区域 -->
    <el-scrollbar ref="scrollRef" class="chat-content-area">
      <div class="chat-content" ref="chatContentRef">
        
        <!-- 对话列表 (对话模式时显示) -->
        <div v-if="chatList.length > 0" class="chat-messages">
          <template v-for="(item, index) in chatList" :key="index">
            <!-- 用户问题 -->
            <div class="message-item user-message">
              <div class="message-content user-content">
                <span>{{ item.problem_text }}</span>
              </div>
            </div>

            <!-- AI 回答 -->
            <div class="message-item ai-message">
              <div class="ai-avatar">
                <svg width="28" height="28" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="30" cy="30" r="28" stroke="#5E56DD" stroke-width="2" fill="none"/>
                  <text x="30" y="38" text-anchor="middle" fill="#5E56DD" font-size="24" font-weight="bold">Ai</text>
                </svg>
              </div>
              <div class="message-content ai-content">
                <div class="ai-answer" v-if="item.write_ed || item.answer_text">
                  <div class="answer-content">
                    <MdRenderer
                      :source="getAnswerText(item)"
                      :reasoning_content="item.reasoning_content || ''"
                    />
                  </div>
                  <!-- 操作按钮 - 在气泡内右下角 -->
                  <div class="message-actions" v-if="item.write_ed">
                    <el-tooltip content="重新生成" placement="top">
                      <el-button text size="small" @click="regenerate(item)">
                        <el-icon :size="16"><RefreshRight /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="复制" placement="top">
                      <el-button text size="small" @click="copyText(getAnswerText(item))">
                        <el-icon :size="16"><CopyDocument /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="赞" placement="top">
                      <el-button text size="small" @click="handleLike(item)" :class="{ 'is-liked': item.vote_status === '1' }">
                        <el-icon :size="16"><Good /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="踩" placement="top">
                      <el-button text size="small" @click="handleDislike(item)" :class="{ 'is-disliked': item.vote_status === '0' }">
                        <el-icon :size="16"><Bad /></el-icon>
                      </el-button>
                    </el-tooltip>
                  </div>
                </div>
                <div v-else class="loading-text">
                  正在思考中 <span class="dotting"></span>
                </div>

                <!-- 推荐问题 -->
                <div class="recommend-questions" v-if="item.write_ed && item.suggest_questions?.length">
                  <p class="recommend-title">推荐问题：</p>
                  <div 
                    v-for="(question, qIndex) in item.suggest_questions" 
                    :key="qIndex"
                    class="recommend-item"
                    @click="sendRecommendQuestion(question)"
                  >
                    <span>{{ question }}</span>
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>

      </div>
    </el-scrollbar>

    <!-- 底部输入区域 - 始终存在，通过CSS控制位置 -->
    <div class="input-area-wrapper">
      <!-- Logo 和问候语 (欢迎模式时显示) -->
      <Transition name="header-fade">
        <div v-if="chatList.length === 0" class="welcome-header">
          <div class="logo-container">
            <div class="ai-logo">
              <svg width="70" height="70" viewBox="0 0 70 70" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#7B74E8;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#5E56DD;stop-opacity:1" />
                  </linearGradient>
                </defs>
                <circle cx="35" cy="35" r="32" stroke="url(#logoGradient)" stroke-width="2" fill="none"/>
                <text x="35" y="44" text-anchor="middle" fill="url(#logoGradient)" font-size="28" font-weight="500" font-family="Arial, sans-serif">Ai</text>
              </svg>
            </div>
          </div>
          <h1 class="greeting">{{ greeting }}，有什么我可以帮助你的吗？</h1>
          <p class="hint-text">请从左侧选择知识库或文档开始问答</p>
        </div>
      </Transition>

      <!-- 开启新对话按钮 (对话模式时显示) -->
      <Transition name="btn-fade">
        <div v-if="chatList.length > 0" class="new-chat-btn-container">
          <el-button 
            type="primary" 
            plain
            @click="startNewChat"
            class="new-chat-btn"
          >
            <el-icon><DocumentAdd /></el-icon>
            开启新对话
          </el-button>
        </div>
      </Transition>

      <!-- 输入框 - 始终存在 -->
      <div class="input-box">
        <div class="input-wrapper">
          <el-input
            ref="inputRef"
            v-model="inputValue"
            type="textarea"
            :autosize="{ minRows: chatList.length > 0 ? 1 : 3, maxRows: 6 }"
            placeholder="请输入您的问题..."
            @keydown.enter="handleEnter"
            class="chat-input"
          />

          <!-- 输入框底部工具栏 -->
          <div class="input-toolbar">
            <div class="toolbar-left">
              <el-dropdown trigger="click" @command="handleKBCommand">
                <el-button type="primary" size="small" class="selected-kb-btn">
                  已选{{ selectedCount }}项
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="manage">管理选择</el-dropdown-item>
                    <el-dropdown-item command="clear">清空选择</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>

            <div class="toolbar-right">
              <el-button text class="tool-btn" @click="startVoice">
                <el-icon :size="20"><Microphone /></el-icon>
              </el-button>
              <el-upload
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                @change="handleFileChange"
              >
                <el-button text class="tool-btn">
                  <el-icon :size="20"><Paperclip /></el-icon>
                </el-button>
              </el-upload>
              <el-divider direction="vertical" />
              <el-button 
                type="primary" 
                circle 
                class="send-btn"
                :disabled="!inputValue.trim() || loading"
                @click="sendMessage"
              >
                <el-icon><Position /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- 快捷操作按钮 (欢迎模式时显示) -->
        <Transition name="actions-fade">
          <div v-if="chatList.length === 0" class="quick-actions">
            <el-button 
              v-for="action in quickActions" 
              :key="action.key"
              class="quick-action-btn"
              @click="handleQuickAction(action)"
            >
              <component :is="action.icon" class="action-icon" />
              <span>{{ action.label }}</span>
            </el-button>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, reactive, h } from 'vue'
import { 
  ArrowDown, 
  Microphone, 
  Paperclip, 
  Position,
  RefreshRight,
  CopyDocument,
  ArrowRight,
  DocumentAdd,
  Document,
  DataLine,
  PieChart
} from '@element-plus/icons-vue'
// 自定义点赞/踩图标
const Good = () => h('svg', { 
  width: '1em', height: '1em', viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg'
}, [
  h('path', { d: 'M7 22V11M2 13V20C2 21.1046 2.89543 22 4 22H17.4262C18.907 22 20.1662 20.9197 20.3914 19.4562L21.4683 12.4562C21.7479 10.6389 20.3418 9 18.5032 9H15C14.4477 9 14 8.55228 14 8V4.46584C14 3.10399 12.896 2 11.5342 2C11.2093 2 10.915 2.1913 10.7831 2.48812L7.26394 10.4061C7.10344 10.7673 6.74532 11 6.35013 11H4C2.89543 11 2 11.8954 2 13Z', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
])

const Bad = () => h('svg', { 
  width: '1em', height: '1em', viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg'
}, [
  h('path', { d: 'M17 2V13M22 11V4C22 2.89543 21.1046 2 20 2H6.57376C5.09299 2 3.83381 3.08033 3.60855 4.54379L2.53168 11.5438C2.25212 13.3611 3.65822 15 5.49684 15H9C9.55228 15 10 15.4477 10 16V19.5342C10 20.896 11.104 22 12.4658 22C12.7907 22 13.085 21.8087 13.2169 21.5119L16.7361 13.5939C16.8966 13.2327 17.2547 13 17.6499 13H20C21.1046 13 22 12.1046 22 11Z', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
])
import { ElMessage } from 'element-plus'
import MdRenderer from '@/components/markdown/MdRenderer.vue'

// 定义聊天记录类型
interface ChatRecord {
  id: string
  problem_text: string
  answer_text: string
  answer_text_list: any[]
  write_ed: boolean
  is_stop: boolean
  vote_status: string
  reasoning_content?: string
  suggest_questions?: string[]
}

// AI写作图标组件
const AIWriteIcon = () => h('svg', { 
  width: '16', height: '16', viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg'
}, [
  h('path', { d: 'M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z', fill: 'currentColor' })
])

// AI翻译图标组件
const AITranslateIcon = () => h('svg', {
  width: '16', height: '16', viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg'
}, [
  h('path', { d: 'M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v1.99h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z', fill: 'currentColor' })
])

// 状态
const inputValue = ref('')
const loading = ref(false)
const chatList = ref<ChatRecord[]>([])
const scrollRef = ref()
const chatContentRef = ref()
const inputRef = ref()
const selectedCount = ref(2) // 已选择的知识库数量

// 快捷操作配置
const quickActions = [
  { key: 'write', label: 'AI写作', icon: AIWriteIcon },
  { key: 'translate', label: 'AI翻译', icon: AITranslateIcon },
  { key: 'summary', label: 'AI摘要', icon: Document },
  { key: 'overview', label: 'AI综述', icon: DataLine },
  { key: 'ask', label: 'AI问数', icon: PieChart }
]

// 计算问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 17) return '下午好'
  if (hour < 19) return '傍晚好'
  return '晚上好'
})

// 获取回答文本
const getAnswerText = (item: ChatRecord) => {
  if (item.answer_text) return item.answer_text
  if (item.answer_text_list?.length > 0) {
    const lastList = item.answer_text_list[item.answer_text_list.length - 1]
    if (Array.isArray(lastList)) {
      return lastList.map((t: any) => typeof t === 'string' ? t : t.content || '').join('')
    }
    return typeof lastList === 'string' ? lastList : lastList.content || ''
  }
  return ''
}

// 生成唯一ID
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

// 发送消息
const sendMessage = async () => {
  if (!inputValue.value.trim() || loading.value) return

  const question = inputValue.value.trim()
  inputValue.value = ''
  loading.value = true

  // 添加用户消息和AI占位
  const chatRecord: ChatRecord = {
    id: generateId(),
    problem_text: question,
    answer_text: '',
    answer_text_list: [],
    write_ed: false,
    is_stop: false,
    vote_status: '-1',
    suggest_questions: []
  }
  chatList.value.push(chatRecord)

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // 模拟 AI 回答（实际项目中应调用 API）
  setTimeout(() => {
    chatRecord.answer_text = `这是对"${question}"的回答。\n\n**核心特点**\n- 信息结构化：将文本、数据等转化为 AI 可理解的格式（如知识图谱、向量数据）。\n- 动态更新：可通过新数据、反馈持续迭代，优化 AI 的知识储备。\n- 高效检索：支持快速匹配查询，为 AI 生成回答、解决问题提供依据。`
    chatRecord.write_ed = true
    chatRecord.suggest_questions = [
      'AI知识库的搭建需要哪些技术支持？',
      'AI知识库搭建的成功案例',
      '如何保证AI知识库的信息准确性？'
    ]
    loading.value = false
    nextTick(() => scrollToBottom())
  }, 1500)
}

// 处理回车发送
const handleEnter = (event: KeyboardEvent) => {
  if (!event.shiftKey && !event.ctrlKey && !event.altKey && !event.metaKey) {
    event.preventDefault()
    sendMessage()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (scrollRef.value) {
    const scrollWrap = scrollRef.value.wrapRef
    if (scrollWrap) {
      scrollWrap.scrollTop = scrollWrap.scrollHeight
    }
  }
}

// 重新生成回答
const regenerate = (item: ChatRecord) => {
  ElMessage.info('正在重新生成...')
  // 实际实现中调用 API 重新生成
}

// 复制文本
const copyText = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 点赞
const handleLike = (item: ChatRecord) => {
  item.vote_status = item.vote_status === '1' ? '-1' : '1'
}

// 点踩
const handleDislike = (item: ChatRecord) => {
  ElMessage.info('感谢您的反馈')
}

// 发送推荐问题
const sendRecommendQuestion = (question: string) => {
  inputValue.value = question
  sendMessage()
}

// 开启新对话
const startNewChat = () => {
  chatList.value = []
  inputValue.value = ''
}

// 处理知识库下拉命令
const handleKBCommand = (command: string) => {
  if (command === 'manage') {
    ElMessage.info('打开知识库管理')
  } else if (command === 'clear') {
    selectedCount.value = 0
    ElMessage.success('已清空选择')
  }
}

// 语音输入
const startVoice = () => {
  ElMessage.info('语音输入功能开发中...')
}

// 文件上传
const handleFileChange = (file: any) => {
  ElMessage.info(`已选择文件: ${file.name}`)
}

// 快捷操作
const handleQuickAction = (action: any) => {
  const prompts: Record<string, string> = {
    write: '请帮我写一篇关于',
    translate: '请帮我翻译以下内容：',
    summary: '请帮我总结以下内容的要点：',
    overview: '请帮我综述以下主题：',
    ask: '请根据数据回答以下问题：'
  }
  inputValue.value = prompts[action.key] || ''
  inputRef.value?.focus()
}

onMounted(() => {
  // 初始化
})
</script>

<style scoped lang="scss">
.chat-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;

  // 欢迎模式 - 输入框居中
  &:not(.chat-mode) {
    .input-area-wrapper {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 100%;
      max-width: 700px;
      padding: 0 20px;
      box-sizing: border-box;
      transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
  }

  // 对话模式 - 输入框在底部
  &.chat-mode {
    .input-area-wrapper {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 30px 20px 24px;
      z-index: 100;
      transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .input-box {
      max-width: 860px;
      margin: 0 auto;
    }
  }
}

.chat-content-area {
  flex: 1;
  overflow: hidden;
}

.chat-content {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  padding-bottom: 200px;
  height: 100%;
  box-sizing: border-box;
}

// 欢迎头部 - logo和问候语
.welcome-header {
  text-align: center;
  margin-bottom: 30px;

  .logo-container {
    margin-bottom: 20px;

    .ai-logo {
      width: 80px;
      height: 80px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }

  .greeting {
    font-size: 24px;
    font-weight: 500;
    color: #1f2329;
    margin: 0 0 8px 0;
  }

  .hint-text {
    font-size: 14px;
    color: #8f959e;
    margin: 0;
  }
}

// 新对话按钮容器
.new-chat-btn-container {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;

  .new-chat-btn {
    border-radius: 20px;
    border-color: #5E56DD;
    color: #5E56DD;

    &:hover {
      background: #f0eeff;
    }
  }
}

// 输入框区域
.input-box {
  .input-wrapper {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    overflow: hidden;

    .chat-input {
      :deep(.el-textarea__inner) {
        border: none;
        box-shadow: none;
        padding: 16px;
        font-size: 14px;
        resize: none;

        &:focus {
          box-shadow: none;
        }
      }
    }

    .input-toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 16px;

      .toolbar-left {
        .selected-kb-btn {
          border-radius: 4px;
          font-size: 13px;
          padding: 6px 12px;
          background-color: #f0eeff;
          border-color: #f0eeff;
          color: #5E56DD;

          &:hover {
            background-color: #e4e1ff;
            border-color: #e4e1ff;
          }
        }
      }

      .toolbar-right {
        display: flex;
        align-items: center;
        gap: 4px;

        .tool-btn {
          color: #8f959e;
          padding: 8px;

          &:hover {
            color: #5E56DD;
          }
        }

        .el-divider {
          margin: 0 8px;
          height: 20px;
        }

        .send-btn {
          width: 36px;
          height: 36px;
          background: linear-gradient(135deg, #7B74E8, #5E56DD);
          border: none;

          &:hover {
            background: linear-gradient(135deg, #5E56DD, #4840C7);
          }

          &:disabled {
            background: #e4e7ed;
          }
        }
      }
    }
  }

  // 快捷操作按钮
  .quick-actions {
    margin-top: 20px;
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;

    .quick-action-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 10px 20px;
      border-radius: 24px;
      border: 1px solid #e4e7ed;
      background: #fff;
      color: #606266;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        border-color: #5E56DD;
        color: #5E56DD;
        background: #f8f7ff;
      }

      .action-icon {
        font-size: 16px;
      }
    }
  }
}

// 聊天消息样式
.chat-messages {
  .message-item {
    margin-bottom: 24px;

    &.user-message {
      display: flex;
      justify-content: flex-end;

      .user-content {
        display: inline-block;
        background: #e8e6ff;
        border-radius: 8px;
        padding: 12px 16px;
        max-width: 80%;
        word-break: break-word;
      }
    }

    &.ai-message {
      display: flex;
      align-items: flex-start;
      gap: 8px;

      .ai-avatar {
        flex-shrink: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .ai-content {
        max-width: 80%;

        .ai-answer {
          display: inline-block;
          background: #fff;
          border-radius: 8px;
          padding: 16px;
          padding-bottom: 8px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

          .answer-content {
            margin-bottom: 8px;
          }

          .message-actions {
            display: flex;
            justify-content: flex-end;
            gap: 4px;
            padding-top: 8px;
            border-top: 1px solid #f0f0f0;

            .el-button {
              color: #bfbfbf;
              padding: 4px 8px;
              height: auto;
              min-height: auto;

              &:hover {
                color: #5E56DD;
              }

              &.is-liked {
                color: #5E56DD;
              }

              &.is-disliked {
                color: #ff4d4f;
              }
            }
          }
        }

        .loading-text {
          display: inline-block;
          background: #fff;
          border-radius: 8px;
          padding: 12px 16px;
          color: #8f959e;
        }

        .recommend-questions {
          margin-top: 16px;

          .recommend-title {
            font-size: 13px;
            color: #8f959e;
            margin: 0 0 8px 0;
          }

          .recommend-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 12px;
            background: #f5f7fa;
            border-radius: 6px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s;

            &:hover {
              background: #f0eeff;
              color: #5E56DD;
            }

            span {
              font-size: 14px;
            }

            .el-icon {
              font-size: 14px;
              color: #c0c4cc;
            }
          }
        }
      }
    }
  }
}

// 加载动画
.dotting {
  display: inline-block;
  min-width: 2px;
  min-height: 2px;
  animation: dotting 1s infinite step-start;
}

@keyframes dotting {
  25% {
    box-shadow: 2px 0 0 currentColor;
  }

  50% {
    box-shadow: 2px 0 0 currentColor, 6px 0 0 currentColor;
  }

  75% {
    box-shadow: 2px 0 0 currentColor, 6px 0 0 currentColor, 10px 0 0 currentColor;
  }
}

// 欢迎头部动画
.header-fade-enter-active {
  animation: header-in 0.4s ease-out;
}

.header-fade-leave-active {
  animation: header-out 0.3s ease-in;
}

@keyframes header-in {
  0% {
    opacity: 0;
    transform: translateY(-20px);
  }

  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes header-out {
  0% {
    opacity: 1;
    transform: translateY(0);
  }

  100% {
    opacity: 0;
    transform: translateY(-30px);
  }
}

// 新对话按钮动画
.btn-fade-enter-active {
  animation: btn-in 0.4s ease-out 0.2s both;
}

.btn-fade-leave-active {
  animation: btn-out 0.2s ease-in;
}

@keyframes btn-in {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }

  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes btn-out {
  0% {
    opacity: 1;
  }

  100% {
    opacity: 0;
  }
}

// 快捷操作动画
.actions-fade-enter-active {
  animation: actions-in 0.4s ease-out 0.1s both;
}

.actions-fade-leave-active {
  animation: actions-out 0.2s ease-in;
}

@keyframes actions-in {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }

  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes actions-out {
  0% {
    opacity: 1;
  }

  100% {
    opacity: 0;
  }
}

// 消息气泡动画
.message-item {
  animation: message-slide-in 0.3s ease-out;
}

@keyframes message-slide-in {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }

  100% {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>