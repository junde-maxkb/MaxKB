import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { TeamMember, Team } from '@/api/type/team'

const prefix = '/messages'

/**
 * 获取团队成员列表
 */
export const getMessages: () => Promise<Result<TeamMember[]>> = () => {
  return get(`${prefix}`)
}

export const readMessage: (id: number) => Promise<Result<null>> = (id) => {
  return put(`${prefix}`, { log_id: id })
}