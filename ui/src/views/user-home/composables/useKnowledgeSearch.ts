/**
 * 知识库搜索 Composable
 * 提供知识库检索和CNKI文献查询功能
 */
import { ref } from 'vue'
import datasetApi from '@/api/dataset'
import documentApi from '@/api/document'
import type { TreeNode, SearchResponse, SearchResult } from '../types/chat'

// 搜索配置常量
const MAX_TOTAL_RESULTS = 200
const MAX_RESULTS_PER_DOCUMENT = 3
const MIN_RESULTS_PER_DOCUMENT = 3
const DEFAULT_SIMILARITY = 0.3
const MAX_CONTEXT_CHARS = 15000 // 上下文最大字符数限制

export function useKnowledgeSearch() {
  // 搜索状态
  const isSearching = ref(false)
  const showServiceWarning = ref(false)
  const serviceWarningMessage = ref('')

  /**
   * CNKI文献查询
   */
  const performCNKISearch = async (query: string): Promise<any[]> => {
    try {
      const response = await documentApi.cnkiSearch(query)
      if (response.code === 200 && response.data) {
        console.log('CNKI文献查询结果:', response.data)
        return response.data
      } else {
        console.warn('CNKI文献查询失败:', response.message)
        return []
      }
    } catch (error) {
      console.error('CNKI文献查询异常:', error)
      return []
    }
  }

  /**
   * 从树形数据中查找知识库节点
   */
  const findDatasetNode = (datasetId: string, treeData: TreeNode[]): TreeNode | null => {
    const searchInNodes = (nodes: TreeNode[]): TreeNode | null => {
      for (const node of nodes) {
        if (node.datasetId === datasetId && node.type === 'dataset') {
          return node
        }
        if (node.children) {
          const found = searchInNodes(node.children)
          if (found) return found
        }
      }
      return null
    }
    return searchInNodes(treeData)
  }

  /**
   * 基于选中文档进行知识检索
   */
  const performKnowledgeSearch = async (
    query: string,
    selectedDocuments: TreeNode[],
    selectedDatasets: TreeNode[],
    treeData: TreeNode[]
  ): Promise<SearchResponse> => {
    isSearching.value = true
    showServiceWarning.value = false
    serviceWarningMessage.value = ''
    
    console.log('=== performKnowledgeSearch 开始 ===')
    console.log('查询:', query)
    console.log('选中文档数量:', selectedDocuments.length)
    console.log('选中知识库数量:', selectedDatasets.length)
    
    try {
      let allResults: SearchResult[] = []
      let hasConnectionError = false
      let hasEmbeddingError = false
      const isDocumentSearch = selectedDocuments.length > 0

      // 1. 准备所有检索任务
      const searchTasks: Promise<any>[] = []

      if (isDocumentSearch) {
        console.log('基于选中的文档进行检索:', selectedDocuments)

        // 按知识库分组文档
        const documentsByDataset = new Map<string, TreeNode[]>()
        selectedDocuments.forEach((doc) => {
          if (doc.datasetId) {
            if (!documentsByDataset.has(doc.datasetId)) {
              documentsByDataset.set(doc.datasetId, [])
            }
            documentsByDataset.get(doc.datasetId)!.push(doc)
          }
        })

        // 为每个文档创建检索任务
        for (const [datasetId, docs] of documentsByDataset) {
          const datasetNode = findDatasetNode(datasetId, treeData)
          const datasetName = datasetNode?.label || '未知知识库'

          for (const doc of docs) {
            if (!doc.documentId) continue

            const task = async () => {
              try {
                const searchData = {
                  query_text: query,
                  top_number: 50,
                  similarity: DEFAULT_SIMILARITY,
                  search_mode: 'blend',
                  document_ids: `${doc.documentId}`
                }
                
                const response = await datasetApi.getDatasetHitTest(datasetId, searchData)
                
                if (response.code === 200 && response.data) {
                  return response.data.map((item: any) => ({
                    ...item,
                    dataset_name: datasetName,
                    dataset_id: datasetId,
                    document_name: doc.label || item.document_name || item.source,
                    document_id: item.document_id ?? doc.documentId,
                    source: doc.label || item.document_name || item.source,
                    _score: item.similarity ?? item.comprehensive_score ?? 0
                  }))
                } else if (response.code === 500) {
                  if (response.message?.includes('Failed to establish a new connection') || response.message?.includes('Connection refused')) {
                    hasEmbeddingError = true
                  }
                }
              } catch (error: any) {
                console.warn(`文档 ${doc.label} 检索失败:`, error)
                if (error.message?.includes('Failed to establish a new connection') || error.message?.includes('Connection refused')) {
                  hasEmbeddingError = true
                } else {
                  hasConnectionError = true
                }
              }
              return []
            }
            searchTasks.push(task())
          }
        }
      } else if (selectedDatasets.length > 0) {
        console.log('基于选中的知识库进行检索:', selectedDatasets)

        // 为每个知识库创建检索任务
        for (const dataset of selectedDatasets) {
          if (!dataset.datasetId) continue

          const task = async () => {
            // CNKI 特殊处理
            if (dataset.datasetId === 'd1f6f1cc-b3c3-11f0-9ffe-1df6b9a97505') {
              return await performCNKISearch(query)
            }

            try {
              const searchData = {
                query_text: query,
                top_number: 300,
                similarity: DEFAULT_SIMILARITY,
                search_mode: 'blend'
              }
              
              const response = await datasetApi.getDatasetHitTest(dataset.datasetId!, searchData)
              
              if (response.code === 200 && response.data) {
                return response.data.map((item: any) => ({
                  ...item,
                  dataset_name: dataset.label,
                  source: dataset.label,
                  _score: item.similarity ?? item.comprehensive_score ?? 0
                }))
              } else if (response.code === 500) {
                if (response.message?.includes('Failed to establish a new connection') || response.message?.includes('Connection refused')) {
                  hasEmbeddingError = true
                }
              }
            } catch (error: any) {
              console.warn(`知识库 ${dataset.label} 检索失败:`, error)
              if (error.message?.includes('Failed to establish a new connection') || error.message?.includes('Connection refused')) {
                hasEmbeddingError = true
              } else {
                hasConnectionError = true
              }
            }
            return []
          }
          searchTasks.push(task())
        }
      } else {
        return { results: [], hasEmbeddingError: false, hasConnectionError: false }
      }

      // 2. 并发执行所有检索任务
      const resultsArrays = await Promise.all(searchTasks)
      
      // 3. 合并结果
      resultsArrays.forEach(results => {
        if (results && results.length > 0) {
          allResults.push(...results)
        }
      })

      // 4. 全局排序
      allResults.sort((a: any, b: any) => (b._score || 0) - (a._score || 0))

      // 5. 统一截断
      const finalResults = allResults.slice(0, MAX_TOTAL_RESULTS).map(({ _score, ...rest }: any) => rest)

      console.log(`检索完成: 总召回 ${allResults.length} 条, 最终采纳 ${finalResults.length} 条`)

      // 更新警告状态
      if (hasEmbeddingError) {
        showServiceWarning.value = true
        serviceWarningMessage.value = '嵌入模型服务暂时不可用'
      } else if (hasConnectionError) {
        showServiceWarning.value = true
        serviceWarningMessage.value = '知识库检索服务暂时不可用'
      }

      return {
        results: finalResults,
        hasEmbeddingError,
        hasConnectionError
      }
    } catch (error) {
      console.error('知识检索失败:', error)
      return {
        results: [],
        hasEmbeddingError: false,
        hasConnectionError: true
      }
    } finally {
      isSearching.value = false
    }
  }

  /**
   * 构建搜索上下文 (优化版：压缩格式 + 动态截断)
   */
  const buildSearchContext = (
    searchResults: SearchResult[],
    hasEmbeddingError: boolean,
    hasConnectionError: boolean
  ): { context: string; contextNote: string } => {
    let context = ''
    let contextNote = ''

    if (hasEmbeddingError) {
      contextNote = '\n\n注意：嵌入模型服务暂时不可用，无法进行知识库检索。回答将基于通用知识。'
      context = '由于嵌入模型服务不可用，暂时无法检索相关的知识库内容。'
    } else if (hasConnectionError) {
      contextNote = '\n\n注意：知识库检索服务暂时不可用。回答将基于通用知识。'
      context = '由于知识库检索服务不可用，暂时无法检索相关内容。'
    } else if (searchResults.length > 0) {
      // 再次确保按相似度排序
      const sortedResults = [...searchResults].sort((a, b) => {
        const sa = a.similarity ?? a.comprehensive_score ?? 0
        const sb = b.similarity ?? b.comprehensive_score ?? 0
        return sb - sa
      })

      let currentLength = 0
      const contextParts: string[] = []

      for (let i = 0; i < sortedResults.length; i++) {
        const result = sortedResults[i]
        
        // 紧凑格式：[序号] 标题 | 来源 \n 内容
        const titlePart = result.title ? `标题：${result.title} | ` : ''
        const sourcePart = result.document_name || result.source || '未知来源'
        
        // 智能合并：如果标题和来源相同，只显示一个
        const headerInfo = (result.title === sourcePart) 
          ? `来源：${sourcePart}`
          : `${titlePart}来源：${sourcePart}`

        const itemText = `[${i + 1}] ${headerInfo}\n${result.content}`
        
        // 动态截断：检查是否超出字符限制
        if (currentLength + itemText.length > MAX_CONTEXT_CHARS) {
          console.log(`上下文构建截断: 已达到 ${currentLength} 字符，丢弃剩余 ${sortedResults.length - i} 条结果`)
          break
        }
        
        contextParts.push(itemText)
        currentLength += itemText.length + 2 // +2 for \n\n
      }
      
      context = contextParts.join('\n\n')
    } else {
      context = '未找到与问题相关的知识库内容。'
      contextNote = '\n\n注意：在选中的知识库中未找到相关内容，回答将基于通用知识。'
    }

    return { context, contextNote }
  }

  /**
   * 格式化搜索结果供AI使用
   */
  const formatSearchResultsForAI = (searchResults: SearchResult[]): SearchResult[] => {
    if (!searchResults || searchResults.length === 0) return []

    return searchResults.map((result) => ({
      title: result.title,
      content: result.content,
      source: result.document_name || result.source,
      document_name: result.document_name,
      dataset_name: result.dataset_name,
      document_id: result.document_id,
      dataset_id: result.dataset_id,
      similarity: result.similarity,
      comprehensive_score: result.comprehensive_score
    }))
  }

  /**
   * 去重分段信息（按document_name去重）
   */
  const deduplicateParagraphs = (paragraphs: SearchResult[]): SearchResult[] => {
    const documentMap = new Map()
    const newParagraphs: SearchResult[] = []

    paragraphs.forEach((item) => {
      if (!documentMap.has(item.document_name)) {
        documentMap.set(item.document_name, 1)
        newParagraphs.push(item)
      }
    })

    return newParagraphs
  }

  return {
    // 状态
    isSearching,
    showServiceWarning,
    serviceWarningMessage,

    // 方法
    performKnowledgeSearch,
    performCNKISearch,
    buildSearchContext,
    formatSearchResultsForAI,
    deduplicateParagraphs,
    findDatasetNode
  }
}
