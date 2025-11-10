import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'

const prefix = '/messages'


export interface Message {
  msg: string
  log_id: string
  log_read: boolean
  create_time: string
}

/**
 * 获取团队成员列表
 */
export const getMessages: () => Promise<Result<Message[]>> = () => {
  return get(`${prefix}`)
}

export const readMessage: (id: string) => Promise<Result<null>> = (id) => {
  return put(`${prefix}`, { log_id: id })
}