import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import { type Ref } from 'vue'

const prefix = '/user_manage'
/**
 * 用户分页列表
 * @param 参数 
 * page  {
              "current_page": "string",
              "page_size": "string",
            }
 * @query 参数 
   email_or_username: string
 */
const getUserManage: (
  page: pageRequest,
  email_or_username: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, email_or_username, loading) => {
  return get(
    `${prefix}/${page.current_page}/${page.page_size}`,
    email_or_username ? { email_or_username } : undefined,
    loading
  )
}

/**
 * 删除用户
 * @param 参数 user_id,
 */
const delUserManage: (user_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  user_id,
  loading
) => {
  return del(`${prefix}/${user_id}`, undefined, {}, loading)
}

/**
 * 创建用户
 */
const postUserManage: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 编辑用户
 */
const putUserManage: (
  user_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (user_id, data, loading) => {
  return put(`${prefix}/${user_id}`, data, undefined, loading)
}
/**
 * 修改用户密码
 */
const putUserManagePassword: (
  user_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (user_id, data, loading) => {
  return put(`${prefix}/${user_id}/re_password`, data, undefined, loading)
}

/**
 * 设置用户为系统管理员
 */


const setAdminManage: (user_id: string,loading?: Ref<boolean>) => Promise<Result<any>>
 = (user_id,
  loading) => {
  return put(`${prefix}/${user_id}/set_admin`, undefined, loading)
}

/**
 * 获取用户历史聊天记录列表
 * @param user_id 用户ID
 * @param loading 加载状态
 */
const getChatHistory: (
  user_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (user_id, loading) => {
  return get(`/chat_history/${user_id}`, undefined, loading)
}

/**
 * 获取用户历史聊天记录分页列表
 * @param user_id 用户ID
 * @param page 分页参数
 * @param loading 加载状态
 */
const getChatHistoryPage: (
  user_id: string,
  page: pageRequest,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (user_id, page, loading) => {
  return get(
    `/chat_history/${user_id}/${page.current_page}/${page.page_size}`,
    undefined,
    loading
  )
}

/**
 * 保存聊天记录
 * @param data 聊天记录数据
 * @param loading 加载状态
 */
const postChatHistory: (
  data: {
    user_id: string
    application_name: string
    title?: string
    message_count?: number
  },
  loading?: Ref<boolean>
) => Promise<Result<any>> = (data, loading) => {
  return post('/chat_history', data, undefined, loading)
}

/**
 * 保存聊天消息
 * @param data 聊天消息数据
 * @param loading 加载状态
 */
const postChatMessage: (
  data: {
    chat_history_id: string
    role: string
    content: string
    message_index?: number
  },
  loading?: Ref<boolean>
) => Promise<Result<any>> = (data, loading) => {
  return post('/chat_message', data, undefined, loading)
}

/**
 * 批量保存聊天消息
 * @param data 聊天消息数据
 * @param loading 加载状态
 */
const postChatMessageBatch: (
  data: {
    chat_history_id: string
    messages: Array<{
      role: string
      content: string
      message_index?: number
    }>
  },
  loading?: Ref<boolean>
) => Promise<Result<any>> = (data, loading) => {
  return post('/chat_message/batch', data, undefined, loading)
}

/**
 * 获取聊天消息列表
 * @param chat_history_id 聊天历史ID
 * @param loading 加载状态
 */
const getChatMessages: (
  chat_history_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (chat_history_id, loading) => {
  return get('/chat_message/list', { chat_history_id }, loading)
}

export default {
  getUserManage,
  delUserManage,
  postUserManage,
  putUserManage,
  putUserManagePassword,
  setAdminManage,
  getChatHistory,
  getChatHistoryPage,
  postChatHistory,
  postChatMessage,
  postChatMessageBatch,
  getChatMessages
}
