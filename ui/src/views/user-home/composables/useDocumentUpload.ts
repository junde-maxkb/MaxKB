/**
 * 文档上传 Composable
 * 处理各种模式下的文档上传和内容提取
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import documentApi from '@/api/document'
import type { AIMode } from './useAIMode'

// 支持的文件类型
const ALLOWED_DOCUMENT_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
]

const ALLOWED_EXCEL_TYPES = [
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
]

// 最大文件大小 (10MB)
const MAX_FILE_SIZE = 10 * 1024 * 1024

export function useDocumentUpload() {
  // 上传状态
  const isUploading = ref(false)
  const uploadProgress = ref(0)

  /**
   * 验证文件类型
   */
  const validateFileType = (
    file: File,
    mode: AIMode
  ): { valid: boolean; message?: string } => {
    // 问数模式只支持 Excel 文件
    if (mode === 'question') {
      const isExcel =
        ALLOWED_EXCEL_TYPES.includes(file.type) || file.name.match(/\.(xls|xlsx)$/i)
      if (!isExcel) {
        return {
          valid: false,
          message: '仅支持上传 Excel 文档（xls 或 xlsx 格式）'
        }
      }
      return { valid: true }
    }

    // 其他模式支持多种文档类型
    const isAllowed =
      ALLOWED_DOCUMENT_TYPES.includes(file.type) ||
      file.name.match(/\.(pdf|doc|docx|txt|xls|xlsx)$/i)

    if (!isAllowed) {
      return {
        valid: false,
        message: '仅支持上传 PDF、Word、Excel 和 TXT 文档'
      }
    }

    return { valid: true }
  }

  /**
   * 验证文件大小
   */
  const validateFileSize = (file: File): { valid: boolean; message?: string } => {
    if (file.size > MAX_FILE_SIZE) {
      return {
        valid: false,
        message: '文件大小不能超过 10MB'
      }
    }
    return { valid: true }
  }

  /**
   * 提取文档内容
   */
  const extractDocumentContent = async (
    file: File
  ): Promise<{ content: string; success: boolean; message?: string }> => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('limit', '100000') // 设置较大的字符限制
      formData.append('with_filter', 'false')

      // 调用文档分段API进行文档识别
      const response = await documentApi.postSplitDocument(formData)

      if (response.code === 200 && response.data) {
        let documentContent = ''

        if (Array.isArray(response.data) && response.data.length > 0) {
          const allParagraphs: string[] = []

          response.data.forEach((doc: any) => {
            if (Array.isArray(doc.content)) {
              doc.content.forEach((paragraph: any) => {
                if (paragraph.content && typeof paragraph.content === 'string') {
                  allParagraphs.push(paragraph.content.trim())
                }
              })
            }
          })

          documentContent = allParagraphs.filter((p) => p).join('\n\n')
        }

        if (documentContent.trim()) {
          return { content: documentContent, success: true }
        } else {
          return {
            content: '',
            success: false,
            message: '文档内容为空或无法识别'
          }
        }
      } else {
        return {
          content: '',
          success: false,
          message: response.message || '文档识别失败'
        }
      }
    } catch (error: any) {
      console.error('文档提取失败:', error)
      return {
        content: '',
        success: false,
        message: error.message || '文档提取失败，请重试'
      }
    }
  }

  /**
   * 处理文档上传
   */
  const handleDocumentUpload = async (
    file: File,
    mode: AIMode,
    onSuccess: (content: string, fileName: string) => void
  ): Promise<boolean> => {
    // 验证模式
    const modeLabels: Record<AIMode, string> = {
      chat: '知识库问答',
      writing: 'AI写作',
      translate: 'AI翻译',
      summary: 'AI摘要',
      review: 'AI综述',
      question: 'AI问数'
    }

    if (mode === 'chat') {
      ElMessage.warning('请先切换到支持文档上传的AI模式')
      return false
    }

    // 验证文件类型
    const typeValidation = validateFileType(file, mode)
    if (!typeValidation.valid) {
      ElMessage.error(typeValidation.message!)
      return false
    }

    // 验证文件大小
    const sizeValidation = validateFileSize(file)
    if (!sizeValidation.valid) {
      ElMessage.error(sizeValidation.message!)
      return false
    }

    try {
      isUploading.value = true
      uploadProgress.value = 0

      // 提取文档内容
      const result = await extractDocumentContent(file)

      if (result.success) {
        onSuccess(result.content, file.name)
        ElMessage.success(`文档 "${file.name}" 上传成功，准备${modeLabels[mode]}！`)
        return true
      } else {
        ElMessage.error(result.message || '文档处理失败')
        return false
      }
    } catch (error: any) {
      console.error('文档上传失败:', error)
      ElMessage.error(error.message || '文档上传失败，请重试')
      return false
    } finally {
      isUploading.value = false
      uploadProgress.value = 0
    }
  }

  /**
   * 创建特定模式的上传处理器
   */
  const createModeUploadHandler = (
    mode: AIMode,
    setContent: (content: string) => void,
    setName: (name: string) => void
  ) => {
    return async (file: File): Promise<boolean> => {
      return handleDocumentUpload(file, mode, (content, fileName) => {
        setContent(content)
        setName(fileName)
      })
    }
  }

  return {
    // 状态
    isUploading,
    uploadProgress,

    // 验证方法
    validateFileType,
    validateFileSize,

    // 核心方法
    extractDocumentContent,
    handleDocumentUpload,
    createModeUploadHandler
  }
}
