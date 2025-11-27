<template>
  <div class="chat-page" :class="{ 'chat-mode': hasChatMessages }">
    <!-- 聊天内容区域 -->
    <el-scrollbar ref="scrollRef" class="chat-content-area" @scroll="handleScroll">
      <div class="chat-content" ref="chatContentRef">
        
        <!-- 对话列表 (对话模式时显示) -->
        <div v-if="hasChatMessages" class="chat-messages">
          <template v-for="(item, index) in chatMessages" :key="item.id || index">
            <!-- 用户消息 -->
            <div v-if="item.role === 'user'" class="message-item user-message">
              <div class="message-content user-content">
                <span>{{ item.content }}</span>
              </div>
            </div>

            <!-- AI 回答 -->
            <div v-else-if="item.role === 'assistant'" class="message-item ai-message">
              <div class="ai-avatar">
                <svg width="28" height="28" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="30" cy="30" r="28" stroke="#5E56DD" stroke-width="2" fill="none"/>
                  <text x="30" y="38" text-anchor="middle" fill="#5E56DD" font-size="24" font-weight="bold">Ai</text>
                </svg>
              </div>
              <div class="message-content ai-content">
                <div class="ai-answer" v-if="item.write_ed || item.content">
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
                  正在思考中<span class="dotting"></span><span class="dotting"></span><span class="dotting"></span>
                </div>

                <!-- 推荐问题 - 只在最后一条AI消息且已完成时显示 -->
                <div class="recommend-questions" v-if="item.write_ed && isLastAssistantMessage(index)">
                  <!-- 加载中状态 -->
                  <div v-if="guidesLoading" class="recommend-loading">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <span>正在生成推荐问题...</span>
                  </div>
                  <!-- 推荐问题列表 -->
                  <template v-else-if="guides?.length">
                    <p class="recommend-title">推荐问题：</p>
                    <div 
                      v-for="(question, qIndex) in guides" 
                      :key="qIndex"
                      class="recommend-item"
                      @click="sendRecommendQuestion(question.submit || question.display)"
                    >
                      <span>{{ question.display || question.submit }}</span>
                      <el-icon><ArrowRight /></el-icon>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </template>
        </div>

      </div>
    </el-scrollbar>

    <!-- 底部输入区域 - 始终存在，通过GSAP控制位置 -->
    <div ref="inputAreaRef" class="input-area-wrapper">
      <!-- Logo 和问候语 (欢迎模式时显示) -->
      <div v-if="!hasChatMessages" ref="welcomeHeaderRef" class="welcome-header">
          <div class="logo-container">
            <div class="ai-logo">
              <img src="/images/ai-agent.png" alt="">
            </div>
          </div>
          <h1 class="greeting">{{ greeting }}，有什么我可以帮助你的吗？</h1>
          <p class="hint-text">请从左侧选择知识库或文档开始问答</p>
        </div>

      <!-- 开启新对话按钮 (对话模式时显示) -->
      <Transition name="btn-fade">
        <div v-if="hasChatMessages" class="new-chat-btn-container">
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
        <div class="input-wrapper" :class="{ 'is-uploading': isUploading }">
          <!-- 上传中遮罩 -->
          <div v-if="isUploading" class="upload-loading-overlay">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>文档解析中...</span>
          </div>
          <el-input
            ref="inputRef"
            v-model="inputValue"
            type="textarea"
            :autosize="{ minRows: hasChatMessages ? 1 : 3, maxRows: 6 }"
            :placeholder="getInputPlaceholder()"
            :disabled="isUploading"
            @keydown.enter="handleEnter"
            class="chat-input"
          />

          <!-- 输入框底部工具栏 -->
          <div class="input-toolbar">
            <div class="toolbar-left">
              <span class="selected-kb-text">已选{{ selectedCount }}项</span>

              <!-- 翻译模式：目标语言选择器 -->
              <el-select
                v-if="isAITranslateMode"
                v-model="targetLanguage"
                size="small"
                class="language-select"
                placeholder="目标语言"
              >
                <el-option
                  v-for="lang in TRANSLATION_LANGUAGES"
                  :key="lang.value"
                  :label="lang.label"
                  :value="lang.value"
                />
              </el-select>

              <!-- 已上传文档标签 -->
              <el-tag
                v-if="currentUploadedDocumentName"
                size="small"
                closable
                @close="clearCurrentDocument"
                class="document-tag"
              >
                <el-icon class="document-icon"><Document /></el-icon>
                <span class="document-name">{{ currentUploadedDocumentName }}</span>
              </el-tag>
            </div>

            <div class="toolbar-right">
              <el-upload
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                @change="handleFileChange"
                v-if="shouldShowToolButtons"
              >
                <el-button text class="tool-btn">
                  <UploadCloudIcon />
                </el-button>
              </el-upload>
              <el-divider direction="vertical" v-if="shouldShowToolButtons" />
              <!-- 发送按钮 -->
              <el-button 
                v-if="!isStreaming"
                type="primary" 
                circle 
                class="send-btn"
                :disabled="!inputValue.trim() || loading"
                @click="sendMessage"
              >
                <el-icon><Position /></el-icon>
              </el-button>
              <!-- 停止按钮 -->
              <el-button 
                v-else
                type="danger" 
                circle 
                class="send-btn stop-btn"
                @click="handleStopGeneration"
              >
                <el-icon><VideoPause /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- 快捷操作按钮 (欢迎模式时显示) -->
        <div v-if="!hasChatMessages" ref="quickActionsRef" class="quick-actions">
          <el-button 
            v-for="action in quickActions" 
            :key="action.key"
            class="quick-action-btn"
            :class="{ active: currentMode === action.key }"
            @click="handleQuickAction(action)"
          >
            <AIWriteIcon v-if="action.icon === 'AIWriteIcon'" class="action-icon" />
            <AITranslateIcon v-else-if="action.icon === 'AITranslateIcon'" class="action-icon" />
            <AISummaryIcon v-else-if="action.icon === 'AISummaryIcon'" class="action-icon" />
            <AIReviewIcon v-else-if="action.icon === 'AIReviewIcon'" class="action-icon" />
            <AIQuestionIcon v-else-if="action.icon === 'AIQuestionIcon'" class="action-icon" />
            <span>{{ action.label }}</span>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, h, watch, inject } from 'vue'
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
  VideoPause,
  DataLine,
  PieChart,
  Close,
  Loading
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import MdRenderer from '@/components/markdown/MdRenderer.vue'
import { postModelChatStream } from '@/api/model'
import { gsap } from 'gsap'
import AIWriteIcon from '@/components/icons/AIWriteIcon.vue'
import AITranslateIcon from '@/components/icons/AITranslateIcon.vue'
import AISummaryIcon from '@/components/icons/AISummaryIcon.vue'
import AIReviewIcon from '@/components/icons/AIReviewIcon.vue'
import AIQuestionIcon from '@/components/icons/AIQuestionIcon.vue'
import UploadCloudIcon from '@/components/icons/UploadCloudIcon.vue'

// 导入 composables
import { useChat } from '../composables/useChat'
import { useKnowledgeSearch } from '../composables/useKnowledgeSearch'
import { useAIMode, TRANSLATION_LANGUAGES } from '../composables/useAIMode'
import { useDocumentUpload } from '../composables/useDocumentUpload'
import useGuide from '@/utils/useGuide'
import {
  getTranslatePrompt,
  getSummaryPrompt,
  getReviewPrompt,
  getQuestionPrompt,
  getPromptByIntent,
  getChatSystemPrompt,
  replaceQuickChartWithEncodedUrl
} from '../composables/usePrompts'
import type { TreeNode, ChatMessage, SearchResult } from '../types/chat'

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

// 定义 Props
const props = defineProps<{
  selectedDocuments?: TreeNode[]
  selectedDatasets?: TreeNode[]
  treeData?: TreeNode[]
  selectedModelId?: string
}>()

// 定义 Emits
const emit = defineEmits<{
  (e: 'manageSelection'): void
  (e: 'clearSelection'): void
}>()

// 使用 composables
const {
  chatMessages,
  isStreaming,
  guides,
  addUserMessage,
  addAssistantMessage,
  stopGeneration,
  newChat,
  copyText,
  handleLike,
  handleDislike,
  scrollToBottom: chatScrollToBottom
} = useChat()

const {
  isSearching,
  showServiceWarning,
  serviceWarningMessage,
  performKnowledgeSearch,
  buildSearchContext,
  formatSearchResultsForAI,
  deduplicateParagraphs
} = useKnowledgeSearch()

const {
  currentMode,
  isAIWritingMode,
  isAITranslateMode,
  isAISummaryMode,
  isAIReviewMode,
  isAIQuestionMode,
  currentModeLabel,
  targetLanguage,
  translateDocumentContent,
  translateDocumentName,
  summaryDocumentContent,
  summaryDocumentName,
  reviewDocumentContent,
  reviewDocumentName,
  questionDocumentContent,
  questionDocumentName,
  uploadedDocumentContent,
  uploadedDocumentName,
  setMode,
  detectWritingIntent,
  shouldSkipHistory,
  clearTranslateDocument,
  clearSummaryDocument,
  clearReviewDocument,
  clearQuestionDocument,
  resetModeState,
  getCurrentDocumentContent
} = useAIMode()

const { handleDocumentUpload, isUploading } = useDocumentUpload()

// 状态
const inputValue = ref('')
const loading = ref(false)
const scrollRef = ref()
const chatContentRef = ref()
const inputRef = ref()
const guidesLoading = ref(false) // 推荐问题加载状态
const userScrolledUp = ref(false) // 用户是否向上滚动了
const userStoppedGeneration = ref(false) // 用户是否主动停止了生成
const inputAreaRef = ref<HTMLElement | null>(null) // 输入区域的 ref
const welcomeHeaderRef = ref<HTMLElement | null>(null) // 欢迎头部的 ref
const quickActionsRef = ref<HTMLElement | null>(null) // 快捷操作的 ref

// 计算已选择的数量（只统计叶子节点）
const selectedCount = computed(() => {
  const countLeafNodes = (nodes: TreeNode[]): number => {
    let count = 0
    for (const node of nodes) {
      if (!node.children || node.children.length === 0) {
        // 只有叶子节点才计数
        count++
      }
      // 枝干节点不计数
    }
    return count
  }

  const docCount = props.selectedDocuments ? countLeafNodes(props.selectedDocuments) : 0
  const datasetCount = props.selectedDatasets ? countLeafNodes(props.selectedDatasets) : 0
  const total = docCount + datasetCount

  return total
})// 计算当前已上传的文档名称
const currentUploadedDocumentName = computed(() => {
  if (isAITranslateMode.value && translateDocumentName.value) {
    return translateDocumentName.value
  }
  if (isAISummaryMode.value && summaryDocumentName.value) {
    return summaryDocumentName.value
  }
  if (isAIReviewMode.value && reviewDocumentName.value) {
    return reviewDocumentName.value
  }
  if (isAIQuestionMode.value && questionDocumentName.value) {
    return questionDocumentName.value
  }
  if (isAIWritingMode.value && uploadedDocumentName.value) {
    return uploadedDocumentName.value
  }
  return ''
})

// 计算是否有聊天消息
const hasChatMessages = computed(() => chatMessages.value.length > 0)

// 监听聊天模式变化，使用 GSAP 实现流畅动画
watch(hasChatMessages, async (newVal, oldVal) => {
  if (newVal && !oldVal && inputAreaRef.value) {
    // 从欢迎页进入聊天页，执行 GSAP 动画
    await nextTick()
    
    const inputArea = inputAreaRef.value
    const welcomeHeader = welcomeHeaderRef.value
    const quickActions = quickActionsRef.value
    const inputBox = inputArea.querySelector('.input-box') as HTMLElement
    
    // 创建动画时间线
    const timeline = gsap.timeline()
    
    // 第一阶段：渐隐欢迎头部和快捷按钮（0.8秒）
    if (welcomeHeader) {
      timeline.to(welcomeHeader, {
        opacity: 0,
        y: -20,
        duration: 0.8,
        ease: 'power2.in'
      })
    }
    if (quickActions) {
      timeline.to(quickActions, {
        opacity: 0,
        y: 10,
        duration: 0.8,
        ease: 'power2.in'
      }, '<') // 与上一个动画同时开始
    }
    
    // 第二阶段：扩展输入框宽度（0.6秒）
    timeline.to(inputBox, {
      maxWidth: '860px',
      duration: 0.6,
      ease: 'power2.out'
    })
    
    // 第三阶段：移动到底部（1.2秒）
    timeline.to(inputArea, {
      top: 'auto',
      bottom: '0',
      left: '0',
      right: '0',
      xPercent: 0,
      yPercent: 0,
      width: 'auto',
      maxWidth: 'none',
      paddingTop: '30px',
      paddingBottom: '24px',
      paddingLeft: '20px',
      paddingRight: '20px',
      duration: 1.2,
      ease: 'power2.inOut'
    })
  }
})

// 计算是否应该显示工具按钮（文件上传和语音）
const shouldShowToolButtons = computed(() => {
  // 在普通聊天模式下不显示工具按钮
  return isAIWritingMode.value || isAITranslateMode.value || isAISummaryMode.value || isAIReviewMode.value || isAIQuestionMode.value
})

// 判断是否是最后一条AI消息
const isLastAssistantMessage = (index: number): boolean => {
  // 检查当前消息是否是最后一条消息，且是AI消息
  const lastIndex = chatMessages.value.length - 1
  return index === lastIndex && chatMessages.value[index]?.role === 'assistant'
}

// 快捷操作配置
const quickActions = [
  { key: 'writing', label: 'AI写作', icon: 'AIWriteIcon' },
  { key: 'translate', label: 'AI翻译', icon: 'AITranslateIcon' },
  { key: 'summary', label: 'AI摘要', icon: 'AISummaryIcon' },
  { key: 'review', label: 'AI综述', icon: 'AIReviewIcon' },
  { key: 'question', label: 'AI问数', icon: 'AIQuestionIcon' }
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

// 获取回答文本（兼容旧格式）
const getAnswerText = (item: ChatMessage) => {
  return item.content || ''
}

// 发送消息
const sendMessage = async () => {
  const hasTranslateDocument = isAITranslateMode.value && translateDocumentContent.value
  const hasSummaryDocument = isAISummaryMode.value && summaryDocumentContent.value
  const hasReviewDocument = isAIReviewMode.value && reviewDocumentContent.value

  if (
    (!inputValue.value.trim() && !hasTranslateDocument && !hasSummaryDocument && !hasReviewDocument) ||
    isStreaming.value ||
    !props.selectedModelId
  ) {
    if (!props.selectedModelId) {
      ElMessage.warning('请先选择对话模型')
    }
    return
  }

  // 检查是否选中了文档或知识库（部分模式下可以不选择）
  if (
    !isAIWritingMode.value &&
    !isAITranslateMode.value &&
    !isAISummaryMode.value &&
    !isAIReviewMode.value &&
    !isAIQuestionMode.value &&
    selectedCount.value === 0
  ) {
    ElMessage.warning('请先选择要查询的文档或知识库')
    return
  }

  // 清除已有的推荐问题
  guides.value = []
  guidesLoading.value = true

  const userQuestion = inputValue.value.trim()

  // 保存文档内容
  const savedTranslateDocContent = translateDocumentContent.value
  const savedTranslateDocName = translateDocumentName.value
  const savedSummaryDocContent = summaryDocumentContent.value
  const savedSummaryDocName = summaryDocumentName.value
  const savedReviewDocContent = reviewDocumentContent.value
  const savedReviewDocName = reviewDocumentName.value
  const savedQuestionDocContent = questionDocumentContent.value
  const savedQuestionDocName = questionDocumentName.value
  const savedUploadedDocContent = uploadedDocumentContent.value
  const savedUploadedDocName = uploadedDocumentName.value

  // 添加用户消息
  let displayUserMessage = userQuestion
  if (hasTranslateDocument && !userQuestion) {
    displayUserMessage = `翻译文档：${savedTranslateDocName}`
  } else if (hasSummaryDocument && !userQuestion) {
    displayUserMessage = `摘要文档：${savedSummaryDocName}`
  }

  addUserMessage(displayUserMessage)

  // 重置用户滚动状态，允许新消息自动滚动到底部
  userScrolledUp.value = false
  // 重置用户停止标记
  userStoppedGeneration.value = false

  // 清空输入框
  inputValue.value = ''

  // 不再自动清除文档，保留显示直到用户手动关闭

  loading.value = true
  isStreaming.value = true

  // 立即添加空的 AI 消息，显示"正在思考中"状态
  addAssistantMessage('')
  const assistantMsgIndex = chatMessages.value.length - 1

  await nextTick()
  scrollToBottom()

  try {
    const modelId = props.selectedModelId

    // 执行知识库检索
    console.log('=== 开始知识检索 ===')
    console.log('用户问题:', userQuestion)
    console.log('选中的文档:', props.selectedDocuments)
    console.log('选中的知识库:', props.selectedDatasets)
    console.log('树形数据:', props.treeData?.length, '个顶级节点')
    
    const searchResponse = await performKnowledgeSearch(
      userQuestion,
      props.selectedDocuments || [],
      props.selectedDatasets || [],
      props.treeData || []
    )

    const { results: searchResults, hasEmbeddingError, hasConnectionError } = searchResponse
    console.log('知识检索结果:', searchResults.length, '条')
    console.log('嵌入错误:', hasEmbeddingError, '连接错误:', hasConnectionError)

    // 构建搜索上下文
    const { context, contextNote } = buildSearchContext(searchResults, hasEmbeddingError, hasConnectionError)
    const searchResultsForAI = formatSearchResultsForAI(searchResults)
    
    console.log('=== 构建上下文 ===')
    console.log('context:', context.substring(0, 300))
    console.log('contextNote:', contextNote)

    // 构建系统提示词
    let systemPrompt = ''
    let currentIntent: 'writing' | 'polish' | 'expand' | 'chat' | null = null
    const documentDoc = `
上传文档内容（${savedTranslateDocName || savedUploadedDocName || savedSummaryDocName || savedReviewDocName || savedQuestionDocName}）：
${savedTranslateDocContent || savedUploadedDocContent || savedSummaryDocContent || savedReviewDocContent || savedQuestionDocContent}
知识库内容：
${context}
${contextNote}`

    if (isAITranslateMode.value) {
      if (savedTranslateDocContent) {
        systemPrompt = getTranslatePrompt(
          targetLanguage.value,
          '',
          savedTranslateDocContent,
          savedTranslateDocName,
          userQuestion
        )
      } else {
        systemPrompt = getTranslatePrompt(targetLanguage.value, userQuestion)
      }
    } else if (isAIWritingMode.value) {
      const intent = await detectWritingIntent(userQuestion, modelId)
      currentIntent = intent

      if (intent === 'chat') {
        systemPrompt = getChatSystemPrompt(context, contextNote, hasEmbeddingError || hasConnectionError, chatMessages.value)
      } else {
        let documentContext = ''
        if (savedUploadedDocContent) {
          documentContext = `\n\n上传文档内容（${savedUploadedDocName}）：\n${savedUploadedDocContent}`
        }
        systemPrompt = getPromptByIntent(intent, userQuestion, context, documentContext, contextNote)
      }
    } else if (isAISummaryMode.value) {
      if (savedSummaryDocContent) {
        systemPrompt = getSummaryPrompt('中英文', userQuestion, savedSummaryDocContent, savedSummaryDocName, '', '', chatMessages.value.slice(-10))
      } else {
        systemPrompt = getSummaryPrompt('中英文', userQuestion, '', '', context, contextNote, chatMessages.value.slice(-10))
      }
    } else if (isAIReviewMode.value) {
      if (savedReviewDocContent) {
        systemPrompt = getReviewPrompt(userQuestion, savedReviewDocContent, savedReviewDocName)
      } else {
        systemPrompt = getReviewPrompt(userQuestion, '', '', context, contextNote)
      }
    } else if (isAIQuestionMode.value) {
      if (savedQuestionDocContent) {
        systemPrompt = getQuestionPrompt(userQuestion, savedQuestionDocContent, savedQuestionDocName)
      } else {
        systemPrompt = getQuestionPrompt(userQuestion, '', '', context, contextNote)
      }
    } else {
      systemPrompt = getChatSystemPrompt(context, contextNote, hasEmbeddingError || hasConnectionError, chatMessages.value)
    }

    // 构建消息数组
    const skipHistory = shouldSkipHistory(currentIntent || undefined)
    const messages = [
      { role: 'system', content: systemPrompt },
      ...(skipHistory ? [] : chatMessages.value.slice(-10).map(m => ({ role: m.role, content: m.content }))),
      { role: 'user', content: userQuestion }
    ]
    
    console.log('=== 准备调用 AI API ===')
    console.log('模型ID:', modelId)
    console.log('系统提示词:', systemPrompt.substring(0, 500))
    console.log('用户问题:', userQuestion)
    console.log('消息数组:', messages.length, '条')

    // 调用流式 API
    const resp = await postModelChatStream(modelId, { messages })
    console.log('API 响应:', resp ? '成功获取响应体' : '响应为空')

    if (resp?.body && typeof resp.body.getReader === 'function') {
      const reader = resp.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let currentAssistantMessage = ''

      // 使用前面已添加的 AI 消息索引

      while (isStreaming.value) {
        const { value, done } = await reader.read()
        if (done) {
          console.log('流式读取完成')
          break
        }

        const chunk = decoder.decode(value)
        console.log('收到原始数据块:', chunk.substring(0, 200)) // 只打印前200字符
        
        // 尝试多种格式匹配
        const parts = chunk.match(/data:.*?\n\n/gs) || chunk.match(/data:[^\n]+/g)

        if (parts) {
          console.log('匹配到', parts.length, '个数据块')
          for (const part of parts) {
            try {
              const jsonStr = part.replace(/^data:\s*/, '').replace(/\n\n$/, '').trim()
              if (!jsonStr) continue
              
              console.log('解析JSON:', jsonStr.substring(0, 100))
              const json = JSON.parse(jsonStr)
              
              // 检查是否有内容（包括空字符串的情况也记录）
              console.log('JSON内容:', JSON.stringify(json))
              
              if (json?.content !== undefined && json.content !== '') {
                currentAssistantMessage += json.content
                // 直接修改数组中的对象，确保响应式更新
                chatMessages.value[assistantMsgIndex].content = currentAssistantMessage
                console.log('累计内容长度:', currentAssistantMessage.length)
                await nextTick()
                scrollToBottom()
              }
              
              // 检查是否结束
              if (json?.is_end === true) {
                console.log('收到结束标记')
              }
            } catch (e) {
              console.warn('解析流式数据失败:', e, '原始数据:', part.substring(0, 100))
            }
          }
        } else {
          console.log('未匹配到数据块格式')
        }
      }

      console.log('流式处理结束，总内容长度:', currentAssistantMessage.length)
      console.log('最终内容:', currentAssistantMessage.substring(0, 200))

      // 流式输出完成后处理
      if (currentAssistantMessage) {
        chatMessages.value[assistantMsgIndex].content = replaceQuickChartWithEncodedUrl(currentAssistantMessage)
        chatMessages.value[assistantMsgIndex].write_ed = true

        // 添加分段信息
        if (searchResultsForAI.length > 0) {
          chatMessages.value[assistantMsgIndex].paragraphs = deduplicateParagraphs(searchResultsForAI)
        }
        
        // 如果用户没有主动停止生成，才获取推荐问题
        if (!userStoppedGeneration.value) {
          try {
            const { getGuideQuestions } = useGuide()
            const guideQuestions = await getGuideQuestions(
              modelId,
              currentModeLabel.value,
              userQuestion,
              currentAssistantMessage
            )
            guides.value = guideQuestions
            console.log('获取到推荐问题:', guideQuestions)
          } catch (e) {
            console.warn('获取推荐问题失败:', e)
          } finally {
            guidesLoading.value = false
          }
        } else {
          guidesLoading.value = false
          console.log('用户主动停止生成，跳过推荐问题')
        }
      } else {
        chatMessages.value[assistantMsgIndex].content = isStreaming.value ? '抱歉，模型服务暂时不可用，请稍后重试。' : '回答已中断。'
        chatMessages.value[assistantMsgIndex].write_ed = true
        guidesLoading.value = false
      }
    } else {
      // API 响应无效，更新已存在的 AI 消息
      chatMessages.value[assistantMsgIndex].content = '抱歉，模型服务暂时不可用，请稍后重试。'
      chatMessages.value[assistantMsgIndex].write_ed = true
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    // 更新已存在的 AI 消息显示错误
    chatMessages.value[assistantMsgIndex].content = '抱歉，发送消息时发生错误，请稍后重试。'
    chatMessages.value[assistantMsgIndex].write_ed = true
  } finally {
    loading.value = false
    isStreaming.value = false
    guidesLoading.value = false
    await nextTick()
    scrollToBottom()
  }
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
  if (scrollRef.value && !userScrolledUp.value) {
    const scrollWrap = scrollRef.value.wrapRef
    if (scrollWrap) {
      scrollWrap.scrollTop = scrollWrap.scrollHeight
    }
  }
}

// 监听滚动事件
const handleScroll = () => {
  if (scrollRef.value) {
    const scrollWrap = scrollRef.value.wrapRef
    if (scrollWrap) {
      const isAtBottom = scrollWrap.scrollTop + scrollWrap.clientHeight >= scrollWrap.scrollHeight - 10
      userScrolledUp.value = !isAtBottom
    }
  }
}

// 重新生成回答
const regenerate = (item: ChatMessage) => {
  ElMessage.info('正在重新生成...')
  // 实际实现中调用 API 重新生成
}

// 发送推荐问题
const sendRecommendQuestion = (question: string) => {
  inputValue.value = question
  sendMessage()
}

// 开启新对话
const startNewChat = async () => {
  // 执行反向动画
  await playReverseAnimation()
  
  // 动画完成后清空数据
  newChat()
  inputValue.value = ''
  resetModeState()
  userScrolledUp.value = false // 重置滚动状态
}

// 反向动画：从聊天页回到欢迎页
const playReverseAnimation = async () => {
  if (!inputAreaRef.value) return
  
  await nextTick()
  
  const inputArea = inputAreaRef.value
  const inputBox = inputArea.querySelector('.input-box') as HTMLElement
  
  // 创建反向动画时间线
  const timeline = gsap.timeline()
  
  // 第一阶段：缩小输入框宽度（0.4秒）
  timeline.to(inputBox, {
    maxWidth: '700px',
    duration: 0.4,
    ease: 'power2.in'
  })
  
  // 第二阶段：从底部移回中央（0.6秒）
  timeline.to(inputArea, {
    top: '50%',
    bottom: 'auto',
    left: '50%',
    right: 'auto',
    xPercent: -50,
    yPercent: -50,
    width: '100%',
    maxWidth: '700px',
    paddingTop: '0px',
    paddingBottom: '0px',
    paddingLeft: '20px',
    paddingRight: '20px',
    duration: 0.6,
    ease: 'power2.inOut'
  })
  
  // 等待动画完成
  await timeline.then()
  
  // 动画完成后，让欢迎元素渐入显示
  await nextTick()
  
  const welcomeHeader = welcomeHeaderRef.value
  const quickActions = quickActionsRef.value
  
  if (welcomeHeader) {
    gsap.set(welcomeHeader, { opacity: 0, y: 20 })
    gsap.to(welcomeHeader, {
      opacity: 1,
      y: 0,
      duration: 0.5,
      ease: 'power2.out'
    })
  }
  
  if (quickActions) {
    gsap.set(quickActions, { opacity: 0, y: -10 })
    gsap.to(quickActions, {
      opacity: 1,
      y: 0,
      duration: 0.5,
      ease: 'power2.out'
    })
  }
}

// 清除当前上传的文档
const clearCurrentDocument = () => {
  if (isAITranslateMode.value) {
    clearTranslateDocument()
  } else if (isAISummaryMode.value) {
    clearSummaryDocument()
  } else if (isAIReviewMode.value) {
    clearReviewDocument()
  } else if (isAIQuestionMode.value) {
    // 问数模式没有清除函数，需要手动清除
    questionDocumentContent.value = ''
    questionDocumentName.value = ''
  } else if (isAIWritingMode.value) {
    // 写作模式也没有清除函数，需要手动清除
    uploadedDocumentContent.value = ''
    uploadedDocumentName.value = ''
  }
  ElMessage.success('已清除上传的文档')
}

// 获取输入框占位符文本
const getInputPlaceholder = () => {
  if (isAIWritingMode.value) {
    if (uploadedDocumentName.value) {
      return '请输入写作主题或上传文档，AI将为您提供论文写作、申报书写作、论文续写、润色等服务。'
    }
    return '请输入写作主题或上传文档，AI将为您提供论文写作、申报书写作、论文续写、润色等服务。'
  }
  if (isAITranslateMode.value) {
    if (translateDocumentName.value) {
      return `点击发送开始翻译文档，或输入附加说明...`
    }
    return `请输入内容或上传文档，AI将为您翻译成${targetLanguage.value}。`
  }
  if (isAISummaryMode.value) {
    if (summaryDocumentName.value) {
      return '请输入内容或上传文档，AI将为您提炼要点或生成中英文摘要。'
    }
    return '请输入内容或上传文档，AI将为您提炼要点或生成中英文摘要。'
  }
  if (isAIReviewMode.value) {
    if (reviewDocumentName.value) {
      return '请勾选知识库或上传文档，AI将为您生成文献综述。'
    }
    return '请勾选知识库或上传文档，AI将为您生成文献综述。'
  }
  if (isAIQuestionMode.value) {
    if (questionDocumentName.value) {
      return '请上传Excel文档或输入数据，AI将为您提供数据解读与可视化图表。'
    }
    return '请上传Excel文档或输入数据，AI将为您提供数据解读与可视化图表。'
  }
  if (!selectedCount.value) {
    return '请先勾选知识库或文档，再与AI进行对话。'
  }
  return '请输入您的问题...'
}

// 处理知识库下拉命令
const handleKBCommand = (command: string) => {
  if (command === 'manage') {
    emit('manageSelection')
  } else if (command === 'clear') {
    emit('clearSelection')
    ElMessage.success('已清空选择')
  }
}

// 文件上传处理
const handleFileChange = async (uploadFile: any) => {
  const file = uploadFile.raw || uploadFile
  
  const onSuccess = (content: string, fileName: string) => {
    switch (currentMode.value) {
      case 'translate':
        translateDocumentContent.value = content
        translateDocumentName.value = fileName
        break
      case 'summary':
        summaryDocumentContent.value = content
        summaryDocumentName.value = fileName
        break
      case 'review':
        reviewDocumentContent.value = content
        reviewDocumentName.value = fileName
        break
      case 'question':
        questionDocumentContent.value = content
        questionDocumentName.value = fileName
        break
      case 'writing':
        uploadedDocumentContent.value = content
        uploadedDocumentName.value = fileName
        break
    }
  }

  await handleDocumentUpload(file, currentMode.value, onSuccess)
}

// 快捷操作
const handleQuickAction = (action: any) => {
  console.log('点击了快捷操作:', action.key, action.label)
  // 如果点击的是当前已选中的模式，则切换回普通聊天模式
  if (currentMode.value === action.key) {
    setMode('chat')
    console.log('取消选中，切换回普通聊天模式')
  } else {
    setMode(action.key)
    console.log('当前模式已切换为:', currentMode.value)
  }
  inputRef.value?.focus()
}

// 停止生成
const handleStopGeneration = () => {
  userStoppedGeneration.value = true // 标记用户主动停止
  stopGeneration()
  guidesLoading.value = false // 停止推荐问题加载
  // 更新最后一条消息的状态
  const lastMsg = chatMessages.value[chatMessages.value.length - 1]
  if (lastMsg && lastMsg.role === 'assistant') {
    lastMsg.write_ed = true
    if (!lastMsg.content) {
      lastMsg.content = '回答已中断。'
    }
  }
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
    }
  }

  // 对话模式 - 输入框在底部
  &.chat-mode {
    .input-area-wrapper {
      position: absolute;
      top: auto !important;
      bottom: 0 !important;
      left: 0 !important;
      right: 0 !important;
      transform: none !important;
      width: auto !important;
      max-width: none !important;
      padding: 30px 20px 24px !important;
      z-index: 100;
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
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
    border: 1px solid #e4e7ed;
    overflow: hidden;
    position: relative;

    &.is-uploading {
      .chat-input {
        opacity: 0.5;
        pointer-events: none;
      }
    }

    .upload-loading-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(255, 255, 255, 0.9);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      z-index: 10;
      color: #5E56DD;
      font-size: 14px;

      .el-icon {
        font-size: 20px;
      }
    }

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
        display: flex;
        align-items: center;
        gap: 8px;

        .selected-kb-text {
          font-size: 12px;
          color: #5E56DD;
          padding: 0 8px;
          background-color: #f0eeff;
          border-radius: 4px;
          height: 24px;
          line-height: 24px;
        }

        .language-select {
          width: 100px;

          :deep(.el-input__wrapper) {
            height: 24px;
            background-color: #f0eeff;
            border: 1px solid #e4e1ff;
            box-shadow: none;

            .el-input__inner {
              font-size: 12px;
              color: #5E56DD;
            }

            &:hover {
              background-color: #e4e1ff;
            }
          }
        }

        .document-tag {
          background-color: #f0eeff;
          border-color: #e4e1ff;
          color: #5E56DD;
          font-size: 12px;
          max-width: 180px;
          display: inline-flex;
          align-items: center;
          height: 24px;

          :deep(.el-tag__content) {
            display: inline-flex;
            align-items: center;
            line-height: 1;
          }

          .document-icon {
            font-size: 12px;
            margin-right: 4px;
            flex-shrink: 0;
          }

          .document-name {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
            min-width: 0;
          }

          &:hover {
            background-color: #e4e1ff;
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
          
          &.stop-btn {
            background: linear-gradient(135deg, #f56c6c, #e74c3c);
            
            &:hover {
              background: linear-gradient(135deg, #e74c3c, #c0392b);
            }
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
      gap: 8px;
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

      &.active {
        border-color: #5E56DD;
        color: #fff;
        background: #5E56DD;

        &:hover {
          background: #4a45b8;
          border-color: #4a45b8;
        }
      }

      .action-icon {
        font-size: 16px;
        margin-right: 6px;
        flex-shrink: 0;
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

          .recommend-loading {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 12px;
            color: #8f959e;
            font-size: 13px;

            .el-icon {
              color: #5E56DD;
            }
          }

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
  width: 6px;
  height: 6px;
  background-color: currentColor;
  border-radius: 50%;
  margin: 0 2px;
  opacity: 0.3;
  animation: dotting-blink 1.4s infinite both;
}
.dotting:nth-child(1) {
  animation-delay: 0s;
}
.dotting:nth-child(2) {
  animation-delay: 0.2s;
}
.dotting:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dotting-blink {
  0%, 80%, 100% {
    opacity: 0.3;
  }
  40% {
    opacity: 1;
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