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
    console.log('树形数据顶级节点数量:', treeData.length)
    
    // 调试: 打印第一个选中文档的结构
    if (selectedDocuments.length > 0) {
      console.log('第一个选中文档结构:', JSON.stringify(selectedDocuments[0], null, 2))
    }
    if (selectedDatasets.length > 0) {
      console.log('第一个选中知识库结构:', JSON.stringify(selectedDatasets[0], null, 2))
    }

    try {
      let searchResults: SearchResult[] = []
      let hasConnectionError = false
      let hasEmbeddingError = false
      const isDocumentSearch = selectedDocuments.length > 0
      let reachedMaxResults = false

      // 如果选中了具体文档，优先基于文档进行检索
      if (isDocumentSearch) {
        console.log('基于选中的文档进行检索:', selectedDocuments)

        // 按知识库分组文档
        const documentsByDataset = new Map<string, TreeNode[]>()
        selectedDocuments.forEach((doc) => {
          console.log('处理文档节点:', { label: doc.label, documentId: doc.documentId, datasetId: doc.datasetId, level: doc.level })
          if (doc.datasetId) {
            if (!documentsByDataset.has(doc.datasetId)) {
              documentsByDataset.set(doc.datasetId, [])
            }
            documentsByDataset.get(doc.datasetId)!.push(doc)
          } else {
            console.warn('文档没有 datasetId:', doc)
          }
        })

        // 对每个知识库的选中文档进行检索
        for (const [datasetId, docs] of documentsByDataset) {
          const datasetNode = findDatasetNode(datasetId, treeData)
          const datasetName = datasetNode?.label || '未知知识库'

          for (const doc of docs) {
            if (reachedMaxResults) break
            if (!doc.documentId) continue

            try {
              const searchData = {
                query_text: query,
                top_number: 50,
                similarity: DEFAULT_SIMILARITY,
                search_mode: 'blend',
                document_ids: `${doc.documentId}`
              }
              
              console.log(`准备调用 API: dataset=${datasetId}, searchData=`, searchData)

              const response = await datasetApi.getDatasetHitTest(datasetId, searchData)
              console.log(`API 响应: code=${response.code}, data=`, response.data)
              
              if (response.code === 200 && response.data) {
                const rawCount = Array.isArray(response.data) ? response.data.length : 0
                const formattedResults = response.data
                  .map((item: any) => ({
                    ...item,
                    dataset_name: datasetName,
                    dataset_id: datasetId,
                    document_name: doc.label || item.document_name || item.source,
                    document_id: item.document_id ?? doc.documentId,
                    source: doc.label || item.document_name || item.source,
                    _score: item.similarity ?? item.comprehensive_score ?? 0
                  }))
                  .sort((a: any, b: any) => b._score - a._score)
                  .map(({ _score, ...rest }: any) => rest)

                if (formattedResults.length > 0) {
                  const sliceCount =
                    formattedResults.length >= MIN_RESULTS_PER_DOCUMENT
                      ? Math.min(formattedResults.length, MAX_RESULTS_PER_DOCUMENT)
                      : formattedResults.length

                  let accepted = formattedResults.slice(0, sliceCount)
                  const remainingSlots = MAX_TOTAL_RESULTS - searchResults.length

                  if (remainingSlots <= 0) {
                    reachedMaxResults = true
                    console.log(
                      `文档命中测试 => 数据集: ${datasetName}(${datasetId}), 文档: ${doc.label || doc.documentId}, 原始召回: ${rawCount} 条, 采纳: 0 条 (总量达到上限)`
                    )
                    break
                  }

                  if (accepted.length > remainingSlots) {
                    accepted = accepted.slice(0, remainingSlots)
                    reachedMaxResults = true
                  }

                  searchResults.push(...accepted)
                  if (searchResults.length >= MAX_TOTAL_RESULTS) {
                    reachedMaxResults = true
                  }

                  console.log(
                    `文档命中测试 => 数据集: ${datasetName}(${datasetId}), 文档: ${doc.label || doc.documentId}, 原始召回: ${rawCount} 条, 采纳: ${accepted.length} 条`
                  )
                }
              } else if (response.code === 500) {
                if (
                  response.message?.includes('Failed to establish a new connection') ||
                  response.message?.includes('Connection refused')
                ) {
                  hasEmbeddingError = true
                }
              }
            } catch (error: any) {
              console.warn(`文档 ${doc.label || doc.documentId} 检索失败:`, error)
              if (
                error.message?.includes('Failed to establish a new connection') ||
                error.message?.includes('Connection refused')
              ) {
                hasEmbeddingError = true
              } else {
                hasConnectionError = true
              }
            }

            if (reachedMaxResults) break
          }

          if (reachedMaxResults) break
        }
      }
      // 如果没有选中文档但选中了知识库，则基于整个知识库进行检索
      else if (selectedDatasets.length > 0) {
        console.log('基于选中的知识库进行检索:', selectedDatasets)

        for (const dataset of selectedDatasets) {
          if (!dataset.datasetId) continue
          if (reachedMaxResults) break

          // 处理 CNKI 知识库的特殊查询
          if (dataset.datasetId === 'd1f6f1cc-b3c3-11f0-9ffe-1df6b9a97505') {
            const cnkiResults = await performCNKISearch(query)
            if (cnkiResults.length > 0) {
              const remainingSlots = MAX_TOTAL_RESULTS - searchResults.length
              if (remainingSlots <= 0) {
                reachedMaxResults = true
              } else {
                let acceptedCNKIResults = cnkiResults
                if (cnkiResults.length > remainingSlots) {
                  acceptedCNKIResults = cnkiResults.slice(0, remainingSlots)
                  reachedMaxResults = true
                }
                searchResults.push(...acceptedCNKIResults)
                if (searchResults.length >= MAX_TOTAL_RESULTS) {
                  reachedMaxResults = true
                }
              }
            }
            continue
          }

          try {
            const searchData = {
              query_text: query,
              top_number: 300,
              similarity: DEFAULT_SIMILARITY,
              search_mode: 'blend'
            }
            
            console.log(`准备调用知识库 API: dataset=${dataset.datasetId}, label=${dataset.label}, searchData=`, searchData)

            const response = await datasetApi.getDatasetHitTest(dataset.datasetId, searchData)
            console.log(`知识库 API 响应: code=${response.code}, data长度=`, response.data?.length)
            
            if (response.code === 200 && response.data) {
              const rawCount = Array.isArray(response.data) ? response.data.length : 0
              let results = response.data.map((item: any) => ({
                ...item,
                dataset_name: dataset.label,
                source: dataset.label
              }))

              if (results.length > 0) {
                const remainingSlots = MAX_TOTAL_RESULTS - searchResults.length
                if (remainingSlots <= 0) {
                  reachedMaxResults = true
                } else {
                  if (results.length > remainingSlots) {
                    results = results.slice(0, remainingSlots)
                    reachedMaxResults = true
                  }
                  searchResults.push(...results)
                  if (searchResults.length >= MAX_TOTAL_RESULTS) {
                    reachedMaxResults = true
                  }
                }
              }

              console.log(
                `知识库命中测试 => 知识库: ${dataset.label}(${dataset.datasetId}), 原始召回: ${rawCount} 条, 采纳: ${results.length} 条`
              )
            } else if (response.code === 500) {
              if (
                response.message?.includes('Failed to establish a new connection') ||
                response.message?.includes('Connection refused')
              ) {
                hasEmbeddingError = true
              }
            }
          } catch (error: any) {
            console.warn(`知识库 ${dataset.label} 检索失败:`, error)
            if (
              error.message?.includes('Failed to establish a new connection') ||
              error.message?.includes('Connection refused')
            ) {
              hasEmbeddingError = true
            } else {
              hasConnectionError = true
            }
          }
        }
      } else {
        console.log('未选中任何文档或知识库')
        return {
          results: [],
          hasEmbeddingError: false,
          hasConnectionError: false
        }
      }

      // 按相似度排序
      if (!isDocumentSearch) {
        searchResults.sort((a, b) => {
          const sa = a.similarity ?? a.comprehensive_score ?? 0
          const sb = b.similarity ?? b.comprehensive_score ?? 0
          return sb - sa
        })
      }

      // 更新警告状态
      if (hasEmbeddingError) {
        showServiceWarning.value = true
        serviceWarningMessage.value = '嵌入模型服务暂时不可用'
      } else if (hasConnectionError) {
        showServiceWarning.value = true
        serviceWarningMessage.value = '知识库检索服务暂时不可用'
      }

      return {
        results: searchResults,
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
   * 构建搜索上下文
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
      context = searchResults
        .map(
          (result, index) => `参考资料${index + 1}：
标题：${result.title || '无标题'}
内容：${result.content}
来源：${result.document_name || result.source}
数据集：${result.dataset_name}`
        )
        .join('\n\n')
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
