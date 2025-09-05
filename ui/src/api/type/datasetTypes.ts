interface WebDatasetData {
  name: string
  desc: string
  source_url: string
  selector: string
}

interface LarkDatasetData {
  name: string
  desc: string
  app_id: string
  app_secret: string
  folder_token: string
}

interface QADatasetData {
  file: File
  name: string
  desc: string
}

interface DatasetHitTestData {
  query_text: string
  top_number: number
  similarity: number
}

interface LarkDocumentListData {
  // 根据实际情况定义字段
  [key: string]: any
}

interface ImportLarkDocumentData {
  // 根据实际情况定义字段
  [key: string]: any
}

interface GenerateRelatedData {
  // 根据实际情况定义字段
  [key: string]: any
}

export type {
  WebDatasetData,
  LarkDatasetData,
  QADatasetData,
  DatasetHitTestData,
  LarkDocumentListData,
  ImportLarkDocumentData,
  GenerateRelatedData
}