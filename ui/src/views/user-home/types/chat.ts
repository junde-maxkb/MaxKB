/**
 * 聊天相关类型定义
 */

// 消息类型
export interface ChatMessage {
  id?: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: Date
  paragraphs?: ParagraphInfo[]
  write_ed?: boolean
  is_stop?: boolean
  vote_status?: string
  reasoning_content?: string
  suggest_questions?: string[]
}

// 段落信息（知识库检索结果）
export interface ParagraphInfo {
  title?: string
  content: string
  source: string
  dataset_name: string
  document_name?: string
  document_id?: string
  dataset_id?: string
  similarity?: number
  comprehensive_score?: number
}

// 树节点类型
export interface TreeNode {
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

// AI模式类型
export type AIMode = 
  | 'normal'      // 普通问答
  | 'writing'     // AI写作
  | 'translate'   // AI翻译
  | 'summary'     // AI摘要
  | 'review'      // AI综述
  | 'question'    // AI问数

// 写作意图类型
export type WritingIntent = 'writing' | 'polish' | 'expand' | 'chat'

// 选中信息
export interface SelectedInfo {
  type: 'documents' | 'datasets'
  count: number
  items: string[]
}

// 上传的文档信息
export interface UploadedDocument {
  name: string
  content: string
}

// 模型信息
export interface ModelInfo {
  id: string
  name: string
  model_type: string
  provider: string
  status: string
}

// 引导问题
export interface GuideQuestion {
  submit: string
  display: string
}

// 知识检索结果
export interface SearchResult {
  title?: string
  content: string
  source: string
  dataset_name: string
  document_name?: string
  document_id?: string
  dataset_id?: string
  similarity?: number
  comprehensive_score?: number
}

// 知识检索响应
export interface SearchResponse {
  results: SearchResult[]
  hasEmbeddingError: boolean
  hasConnectionError: boolean
}
