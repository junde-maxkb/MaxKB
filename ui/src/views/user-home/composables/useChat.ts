/**
 * 聊天核心逻辑 - Composable
 */
import { ref, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import type { ChatMessage, GuideQuestion, SearchResult } from '../types/chat'
import { postModelChatStream } from '@/api/model'
import useGuide from '@/utils/useGuide'

export function useChat() {
  // 聊天消息列表
  const chatMessages = ref<ChatMessage[]>([])
  // 当前输入
  const currentMessage = ref('')
  // 流式输出状态
  const isStreaming = ref(false)
  // 加载状态
  const isLoading = ref(false)
  // 引导问题
  const guides = ref<GuideQuestion[]>([])
  // 滚动容器引用
  const scrollRef = ref<any>(null)

  // 是否有消息
  const hasMessages = computed(() => chatMessages.value.length > 0)

  // 生成唯一ID
  const generateId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }

  // 创建AI消息
  const createAssistantMessage = (content: string, paragraphs?: SearchResult[], writeCompleted: boolean = false): ChatMessage => {
    return {
      id: generateId(),
      role: 'assistant',
      content,
      timestamp: new Date(),
      paragraphs: paragraphs || undefined,
      write_ed: writeCompleted  // 默认为 false，表示正在生成中
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

  // 添加用户消息
  const addUserMessage = (content: string): ChatMessage => {
    const message: ChatMessage = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date()
    }
    chatMessages.value.push(message)
    return message
  }

  // 添加AI消息
  const addAssistantMessage = (content: string, paragraphs?: SearchResult[], writeCompleted: boolean = false): ChatMessage => {
    const message = createAssistantMessage(content, paragraphs, writeCompleted)
    chatMessages.value.push(message)
    return message
  }

  // 流式发送消息
  const sendStreamMessage = async (
    modelId: string,
    messages: Array<{ role: string; content: string }>,
    searchResults?: SearchResult[],
    mode: string = '无特定要求'
  ): Promise<string> => {
    isStreaming.value = true
    let currentAssistantMessage = ''

    try {
      const resp = await postModelChatStream(modelId, { messages })

      if (resp?.body && typeof resp.body.getReader === 'function') {
        const reader = resp.body.getReader()
        const decoder = new TextDecoder('utf-8')

        while (isStreaming.value) {
          const { value, done } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const parts = chunk.match(/data:.*\n\n/g)

          if (parts) {
            for (const part of parts) {
              try {
                const json = JSON.parse(part.replace('data:', ''))
                if (json?.content) {
                  currentAssistantMessage += json.content

                  // 实时更新最后一条消息
                  const lastMessage = chatMessages.value[chatMessages.value.length - 1]
                  if (lastMessage && lastMessage.role === 'assistant') {
                    lastMessage.content = currentAssistantMessage
                  } else {
                    chatMessages.value.push({
                      id: generateId(),
                      role: 'assistant',
                      content: currentAssistantMessage,
                      timestamp: new Date(),
                      write_ed: false
                    })
                  }

                  await nextTick()
                  scrollToBottom()
                }
              } catch (e) {
                console.warn('解析流式数据失败:', e)
              }
            }
          }
        }

        // 流式输出结束后处理
        const lastMessage = chatMessages.value[chatMessages.value.length - 1]
        if (lastMessage && lastMessage.role === 'assistant') {
          lastMessage.content = currentAssistantMessage
          lastMessage.write_ed = true
          
          // 添加检索结果引用
          if (searchResults && searchResults.length > 0) {
            // 去重
            const documentMap = new Map()
            const newParagraphs: SearchResult[] = []
            searchResults.forEach((item) => {
              if (!documentMap.has(item.document_name)) {
                documentMap.set(item.document_name, 1)
                newParagraphs.push(item)
              }
            })
            lastMessage.paragraphs = newParagraphs
          }
        }

        // 获取引导问题
        if (currentAssistantMessage) {
          try {
            const { getGuideQuestions } = useGuide()
            const userQuestion = messages.find(m => m.role === 'user')?.content || ''
            guides.value = await getGuideQuestions(
              modelId,
              mode,
              userQuestion,
              currentAssistantMessage
            )
          } catch (e) {
            console.warn('获取引导问题失败:', e)
          }
        }

        // 如果没有接收到内容，显示错误消息
        if (!currentAssistantMessage) {
          if (!isStreaming.value) {
            addAssistantMessage('回答已中断。', searchResults)
          } else {
            addAssistantMessage('抱歉，模型服务暂时不可用，请稍后重试。', searchResults)
          }
        }
      } else {
        // 检查是否是模型不支持的错误
        const errorText = (await resp?.text?.()) || ''
        if (errorText.includes('该模型不支持直接对话调用')) {
          addAssistantMessage(
            '抱歉，当前选择的模型不支持对话功能。请联系管理员配置支持对话的模型（如：GPT、Claude、通义千问等）。',
            searchResults
          )
        } else {
          addAssistantMessage('抱歉，模型服务暂时不可用，请稍后重试。', searchResults)
        }
      }
    } catch (modelError: any) {
      console.error('模型调用失败:', modelError)

      let errorMessage = '抱歉，处理您的问题时出现错误。'
      if (modelError.message?.includes('该模型不支持直接对话调用')) {
        errorMessage = '当前选择的模型不支持对话功能，请联系管理员配置支持对话的语言模型。'
      } else if (modelError.message?.includes('Failed to establish a new connection')) {
        errorMessage = '模型服务暂时不可用，请稍后重试或联系管理员。'
      } else if (modelError.message?.includes('timeout')) {
        errorMessage = '请求超时，请稍后重试。'
      }

      addAssistantMessage(errorMessage, searchResults)
    } finally {
      isStreaming.value = false
      await nextTick()
      scrollToBottom()
    }

    return currentAssistantMessage
  }

  // 停止生成
  const stopGeneration = () => {
    isStreaming.value = false
  }

  // 新聊天
  const newChat = () => {
    chatMessages.value = []
    currentMessage.value = ''
    guides.value = []
    isStreaming.value = false
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

  // 重新生成
  const regenerate = (message: ChatMessage) => {
    ElMessage.info('正在重新生成...')
    // TODO: 实现重新生成逻辑
  }

  // 点赞
  const handleLike = (message: ChatMessage) => {
    message.vote_status = message.vote_status === '1' ? '-1' : '1'
  }

  // 点踩
  const handleDislike = (message: ChatMessage) => {
    message.vote_status = message.vote_status === '0' ? '-1' : '0'
    ElMessage.info('感谢您的反馈')
  }

  // 获取回答文本
  const getAnswerText = (message: ChatMessage): string => {
    return message.content || ''
  }

  return {
    // 状态
    chatMessages,
    currentMessage,
    isStreaming,
    isLoading,
    hasMessages,
    guides,
    scrollRef,
    
    // 方法
    generateId,
    addUserMessage,
    addAssistantMessage,
    sendStreamMessage,
    stopGeneration,
    newChat,
    scrollToBottom,
    copyText,
    regenerate,
    handleLike,
    handleDislike,
    getAnswerText
  }
}
