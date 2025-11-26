/**
 * AI 模式管理 Composable
 * 管理不同 AI 功能模式（写作、翻译、摘要、综述、问数）
 */
import { ref, computed } from 'vue'
import { postModelChat } from '@/api/model'

// AI 模式类型
export type AIMode =
  | 'chat'
  | 'writing'
  | 'translate'
  | 'summary'
  | 'review'
  | 'question'

// 写作意图类型
export type WritingIntent = 'writing' | 'polish' | 'expand' | 'chat'

// 翻译目标语言
export const TRANSLATION_LANGUAGES = [
  { label: '中文', value: '中文' },
  { label: 'English', value: '英文' },
  { label: '日本語', value: '日语' },
  { label: '한국어', value: '韩语' },
  { label: 'Français', value: '法语' },
  { label: 'Deutsch', value: '德语' },
  { label: 'Español', value: '西班牙语' },
  { label: 'Русский', value: '俄语' }
]

export function useAIMode() {
  // 当前 AI 模式
  const currentMode = ref<AIMode>('chat')

  // 各模式开关状态
  const isAIWritingMode = computed(() => currentMode.value === 'writing')
  const isAITranslateMode = computed(() => currentMode.value === 'translate')
  const isAISummaryMode = computed(() => currentMode.value === 'summary')
  const isAIReviewMode = computed(() => currentMode.value === 'review')
  const isAIQuestionMode = computed(() => currentMode.value === 'question')
  const isNormalChatMode = computed(() => currentMode.value === 'chat')

  // 翻译目标语言
  const targetLanguage = ref('中文')

  // 文档内容状态
  const translateDocumentContent = ref('')
  const translateDocumentName = ref('')
  const summaryDocumentContent = ref('')
  const summaryDocumentName = ref('')
  const reviewDocumentContent = ref('')
  const reviewDocumentName = ref('')
  const questionDocumentContent = ref('')
  const questionDocumentName = ref('')
  const uploadedDocumentContent = ref('')
  const uploadedDocumentName = ref('')

  // 上传状态
  const isUploadingTranslateDocument = ref(false)
  const isUploadingSummaryDocument = ref(false)
  const isUploadingReviewDocument = ref(false)
  const isUploadingQuestionDocument = ref(false)

  /**
   * 切换 AI 模式
   */
  const setMode = (mode: AIMode) => {
    currentMode.value = mode
    console.log(`切换到 ${getModeLabel(mode)} 模式`)
  }

  /**
   * 切换到普通聊天模式
   */
  const switchToChat = () => setMode('chat')

  /**
   * 切换到 AI 写作模式
   */
  const switchToWriting = () => setMode('writing')

  /**
   * 切换到 AI 翻译模式
   */
  const switchToTranslate = () => setMode('translate')

  /**
   * 切换到 AI 摘要模式
   */
  const switchToSummary = () => setMode('summary')

  /**
   * 切换到 AI 综述模式
   */
  const switchToReview = () => setMode('review')

  /**
   * 切换到 AI 问数模式
   */
  const switchToQuestion = () => setMode('question')

  /**
   * 获取当前模式的标签名称
   */
  const getModeLabel = (mode?: AIMode): string => {
    const m = mode || currentMode.value
    const labels: Record<AIMode, string> = {
      chat: '知识库问答',
      writing: 'AI 写作',
      translate: 'AI 翻译',
      summary: 'AI 摘要',
      review: 'AI 综述',
      question: 'AI 问数'
    }
    return labels[m] || '知识库问答'
  }

  /**
   * 获取当前模式标签
   */
  const currentModeLabel = computed(() => getModeLabel())

  /**
   * 检查当前模式是否需要选中知识库
   */
  const requiresKnowledgeBase = computed(() => {
    return currentMode.value === 'chat'
  })

  /**
   * 检查当前模式是否支持文档上传
   */
  const supportsDocumentUpload = computed(() => {
    return ['translate', 'summary', 'review', 'question', 'writing'].includes(currentMode.value)
  })

  /**
   * AI 写作意图识别函数
   */
  const detectWritingIntent = async (
    userInput: string,
    modelId: string
  ): Promise<WritingIntent> => {
    try {
      console.log('--- 开始意图识别 ---')
      console.log('输入文本长度:', userInput.length, '字')
      console.log('使用模型ID:', modelId)

      const intentPrompt = `你是一个意图识别助手。请判断用户的输入属于以下哪一种意图：
1. 写作（writing）：用户提供主题或大纲，需要从零开始创作一篇文章
2. 润写（polish）：用户提供了已有的文章内容，需要优化语言、修正错误、提升表达质量
3. 扩写（expand）：用户提供了简短的内容或要点，需要在原有基础上扩充内容、增加细节
4. 对话（chat）：用户只是打招呼、闲聊或者问简单的问题，不需要进行写作

判断规则（请严格按照以下规则进行判断）：
- 如果用户输入的是打招呼（如"你好"、"hello"、"hi"）、闲聊或简单问题，判定为"对话"
- 如果用户输入明确包含"扩写"、"扩充"、"展开"、"增加内容"、"详细说明"、"补充"、"丰富"等关键词，或者提供了简短内容且要求增加内容，判定为"扩写"
- 如果用户输入明确包含"润写"、"润色"、"优化"、"改进"、"修改"、"提升"、"完善"等关键词，且提供了完整的文章段落或较长的文本内容（通常超过100字），判定为"润写"
- 如果用户输入的是主题、标题、大纲、具体的写作要求或描述，没有提供完整文章内容，也没有明确要求扩写或润写，判定为"写作"

特别注意：
- "扩写"要求用户提供原始内容并明确要求扩充内容
- "润写"要求用户提供完整文章内容并要求优化
- "写作"是用户只提供主题或大纲，需要从零开始创作
- 优先识别明确的关键词，如"扩写"、"润写"等

用户输入：
${userInput}

请只返回一个词：writing、polish、expand 或 chat`

      const messages = [{ role: 'user', content: intentPrompt }]
      console.log('发送意图识别请求到AI模型...')

      const response = await postModelChat(modelId, { messages })
      console.log('收到AI模型响应:', response)

      if (response && response.data && response.data.content) {
        const rawIntent = response.data.content.trim()
        const intent = rawIntent.toLowerCase()

        console.log('AI返回的原始意图:', rawIntent)
        console.log('处理后的意图文本:', intent)

        let finalIntent: WritingIntent
        if (intent.includes('chat')) {
          finalIntent = 'chat'
          console.log('解析结果: 对话模式 (chat)')
        } else if (intent.includes('polish')) {
          finalIntent = 'polish'
          console.log('解析结果: 润写模式 (polish)')
        } else if (intent.includes('expand')) {
          finalIntent = 'expand'
          console.log('解析结果: 扩写模式 (expand)')
        } else {
          finalIntent = 'writing'
          console.log('解析结果: 写作模式 (writing)')
        }

        console.log('--- 意图识别完成 ---')
        return finalIntent
      }

      console.log('AI模型未返回有效内容，使用默认意图: writing')
      console.log('--- 意图识别完成 ---')
      return 'writing'
    } catch (error) {
      console.error('意图识别失败，使用默认意图:', error)
      // 发生错误时，根据文本长度做简单判断
      const fallbackIntent: WritingIntent = userInput.length > 100 ? 'polish' : 'writing'
      console.log('基于文本长度判断，使用意图:', fallbackIntent)
      console.log('--- 意图识别完成（异常处理）---')
      return fallbackIntent
    }
  }

  /**
   * 判断当前模式是否需要跳过对话历史
   */
  const shouldSkipHistory = (currentIntent?: WritingIntent): boolean => {
    return (
      isAITranslateMode.value ||
      isAISummaryMode.value ||
      currentIntent === 'polish' ||
      currentIntent === 'expand'
    )
  }

  /**
   * 清除翻译文档
   */
  const clearTranslateDocument = () => {
    translateDocumentContent.value = ''
    translateDocumentName.value = ''
  }

  /**
   * 清除摘要文档
   */
  const clearSummaryDocument = () => {
    summaryDocumentContent.value = ''
    summaryDocumentName.value = ''
  }

  /**
   * 清除综述文档
   */
  const clearReviewDocument = () => {
    reviewDocumentContent.value = ''
    reviewDocumentName.value = ''
  }

  /**
   * 清除问数文档
   */
  const clearQuestionDocument = () => {
    questionDocumentContent.value = ''
    questionDocumentName.value = ''
  }

  /**
   * 清除写作文档
   */
  const clearUploadedDocument = () => {
    uploadedDocumentContent.value = ''
    uploadedDocumentName.value = ''
  }

  /**
   * 重置所有模式状态
   */
  const resetModeState = () => {
    currentMode.value = 'chat'
    targetLanguage.value = '中文'
    clearTranslateDocument()
    clearSummaryDocument()
    clearReviewDocument()
    clearQuestionDocument()
    clearUploadedDocument()
  }

  /**
   * 获取当前上传的文档内容
   */
  const getCurrentDocumentContent = (): { content: string; name: string } => {
    switch (currentMode.value) {
      case 'translate':
        return { content: translateDocumentContent.value, name: translateDocumentName.value }
      case 'summary':
        return { content: summaryDocumentContent.value, name: summaryDocumentName.value }
      case 'review':
        return { content: reviewDocumentContent.value, name: reviewDocumentName.value }
      case 'question':
        return { content: questionDocumentContent.value, name: questionDocumentName.value }
      case 'writing':
        return { content: uploadedDocumentContent.value, name: uploadedDocumentName.value }
      default:
        return { content: '', name: '' }
    }
  }

  /**
   * 检查当前模式是否有上传的文档
   */
  const hasUploadedDocument = computed(() => {
    const { content } = getCurrentDocumentContent()
    return !!content
  })

  return {
    // 模式状态
    currentMode,
    isAIWritingMode,
    isAITranslateMode,
    isAISummaryMode,
    isAIReviewMode,
    isAIQuestionMode,
    isNormalChatMode,
    currentModeLabel,
    requiresKnowledgeBase,
    supportsDocumentUpload,
    hasUploadedDocument,

    // 翻译相关
    targetLanguage,

    // 文档内容
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

    // 上传状态
    isUploadingTranslateDocument,
    isUploadingSummaryDocument,
    isUploadingReviewDocument,
    isUploadingQuestionDocument,

    // 方法
    setMode,
    switchToChat,
    switchToWriting,
    switchToTranslate,
    switchToSummary,
    switchToReview,
    switchToQuestion,
    getModeLabel,
    detectWritingIntent,
    shouldSkipHistory,
    clearTranslateDocument,
    clearSummaryDocument,
    clearReviewDocument,
    clearQuestionDocument,
    clearUploadedDocument,
    resetModeState,
    getCurrentDocumentContent
  }
}
