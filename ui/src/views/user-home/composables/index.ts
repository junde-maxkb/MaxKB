/**
 * User Home Composables 统一导出
 */

export { useChat } from './useChat'
export { useKnowledgeSearch } from './useKnowledgeSearch'
export { useAIMode, TRANSLATION_LANGUAGES } from './useAIMode'
export type { AIMode, WritingIntent } from './useAIMode'
export { useDocumentUpload } from './useDocumentUpload'
export {
  getTranslatePrompt,
  getSummaryPrompt,
  getReviewPrompt,
  getQuestionPrompt,
  getPromptByIntent,
  getChatSystemPrompt,
  replaceQuickChartWithEncodedUrl
} from './usePrompts'
