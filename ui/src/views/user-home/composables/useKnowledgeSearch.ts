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
      // TODO: 暂时使用 mock 数据，待 API 调试完成后切换回真实接口
      const useMockData = false
      
      if (useMockData) {
        console.log('CNKI文献查询 [MOCK模式]:', query)
        // Mock 数据 - 模拟 CNKI 返回的文献
        const mockResults = [
          {
    "abstract": "蓬勃发展的数字技术深刻影响着教育发展的格局,全面革新了教育发展的逻辑内涵与实践路向,教育数字化、数字教育、人工智能+教育业已成为新时代教育改革的重要议题。然而,数字技术为教育生态重构和教育理念重塑提供新思路与新方法的同时,也带来了诸多挑战。在新的技术背景下,如何以数字变革推进高等教育数字化转型的进程,新型人技关系下数字教育运行的基本逻辑是什么,如何发展可信的人工智能并建立起相应准则,人工智能赋能教育产生了怎样的现实挑战,未来进路如何等问题,成为推动数字技术与教育深度融合的关键,引起了教育研究者的高度关注和热切讨论。本刊特约请5位教育领域的专家围绕上述问题进行阐述,以期为发展数字教育、建设教育强国贡献学界智慧。",
    "authors": "夏立新;杨宗凯;黄荣怀;顾建军;刘三(女牙);",
    "journal": "华中师范大学学报(人文社会科学版)",
    "keywords": "",
    "orgs": "华中师范大学信息管理学院;华中师范大学国家数字化学习工程技术研究中心、教育大数据应用技术国家工程研究中心;北京师范大学教育学部、互联网教育智能技术及应用国家工程研究中心;南京师范大学教育科学学院;华中师范大学人工智能教育学部;",
    "pubdate": "2023-09-26",
    "title": "教育数字化与新时代教育变革(笔谈)"
}
        ]
        
        // 格式化为标准结构
        return mockResults.map((item, index) => ({
          title: item.title,
          content: item.abstract,
          document_name: `${item.title} (${item.authors}, ${item.pubdate} ${item.journal})`,
          dataset_name: 'CNKI文献',
          dataset_id: 'd1f6f1cc-b3c3-11f0-9ffe-1df6b9a97505',
          document_id: `cnki-mock-${index}`,
          source: item.journal,
          similarity: 0.85 - index * 0.05, // 模拟递减的相似度
          comprehensive_score: 0.85 - index * 0.05,
          _score: 0.85 - index * 0.05,
          author: item.authors,
          publish_date: item.pubdate,
          journal: item.journal,
          keywords: item.keywords
        }))
      }
      
      // 真实 API 调用
      const response = await documentApi.cnkiSearch(query)
      if (response.code === 200 && response.data) {
        console.log('CNKI文献查询结果:', response.data)
        // 格式化 CNKI 结果，使其符合 SearchResult 结构
        return response.data.map((item: any, index: number) => {
          const title = item.title || '未知标题'
          const author = item.authors || '未知作者'
          const date = item.pubdate || '未知年份'
          const journal = item.journal || '未知期刊'
          const orgs = item.orgs || item.institution || '未知单位'

          return {
            title: title,
            content: item.content || item.abstract || item.summary || '',
            document_name: `${title} (${author}, ${date} ${journal})`,
            dataset_name: 'CNKI文献',
            dataset_id: 'd1f6f1cc-b3c3-11f0-9ffe-1df6b9a97505',
            document_id: item.id || item.doc_id || `cnki-${index}`,
            source: item.source || item.journal || 'CNKI',
            similarity: item.similarity ?? item.score ?? 0.8,
            comprehensive_score: item.comprehensive_score ?? item.score ?? 0.8,
            _score: item.similarity ?? item.score ?? 0.8,
            // 保留原始字段以备需要
            author: item.author,
            publish_date: item.publish_date || item.date,
            journal: item.journal,
            keywords: item.keywords
          }
        })
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

      // CNKI 知识库的特殊 ID
      const CNKI_DATASET_ID = 'd1f6f1cc-b3c3-11f0-9ffe-1df6b9a97505'

      // 1. 准备所有检索任务
      const searchTasks: Promise<any>[] = []

      if (isDocumentSearch) {
        console.log('基于选中的文档进行检索:', selectedDocuments)

        // 检查是否包含 CNKI 知识库（它被当作文档节点处理）
        const cnkiNode = selectedDocuments.find(doc => doc.id === CNKI_DATASET_ID || doc.datasetId === CNKI_DATASET_ID)
        if (cnkiNode) {
          console.log('检测到 CNKI 知识库，执行 CNKI 检索')
          const cnkiTask = async () => {
            return await performCNKISearch(query)
          }
          searchTasks.push(cnkiTask())
        }

        // 按知识库分组文档（排除 CNKI）
        const documentsByDataset = new Map<string, TreeNode[]>()
        selectedDocuments.forEach((doc) => {
          // 排除 CNKI 节点
          if (doc.id === CNKI_DATASET_ID || doc.datasetId === CNKI_DATASET_ID) {
            return
          }
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
            if (dataset.datasetId === CNKI_DATASET_ID) {
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
