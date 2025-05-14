import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'

const prefix = '/team_manage'

/**
 * 获取团队列表
 * @returns {Promise<Result<any>>} 
 */
const getTeam = (): Promise<Result<any>> => {
  return get(`${prefix}`)
}

/**
 * 创建团队
 * @param {Array<String>} data 
 * @returns {Promise<Result<boolean>>} 
 */
const CreateTeam = (data: Array<String>): Promise<Result<boolean>> => {
  return post(`${prefix}`, data)
}

/**
 * 删除团队
 * @param {String} team_id 
 * @returns {Promise<Result<boolean>>} 
 */
const deleteTeam = (team_id: String): Promise<Result<boolean>> => {
  return del(`${prefix}/${team_id}`)
}

/**
 * 更新团队信息
 * @param {String} team_id 
 * @param {any} body 
 * @returns {Promise<Result<any>>} 
 */
const updateTeam = (team_id: String, body: any): Promise<Result<any>> => {
  return put(`${prefix}/${team_id}`, body)
}

/**
 * 获取团队成员列表
 * @param {string} team_id 
 * @param {pageRequest} page 
 * @param {string} email_or_username 
 * @returns {Promise<Result<any>>} 
 */
const clickGetTeamMember = (
  team_id: string,
  page: pageRequest,
  email_or_username: string
): Promise<Result<any>> => {
  return get(
    `${prefix}/${team_id}/${page.current_page}/${page.page_size}`,
    email_or_username ? { email_or_username } : undefined
  )
}

/**
 * 删除团队成员
 * @param {String} member_id 
 * @returns {Promise<Result<boolean>>} 
 */
const deleteTeamMember = (member_id: String): Promise<Result<boolean>> => {
  return del(`${prefix}/member/${member_id}`)
}

/**
 * 设置团队管理员
 * @param {String} member_id 
 * @param {any} body 
 * @returns {Promise<Result<boolean>>} 
 */
const setAdminManage = (member_id: String, body: any): Promise<Result<boolean>> => {
  return post(`${prefix}/member/${member_id}`, body)
}

/**
 * 新增团队成员
 * @param {any} data 
 * @returns {Promise<Result<boolean>>} 
 */
const CreateTeamMember = (data: any): Promise<Result<boolean>> => {
  return post(`${prefix}/member`, data)
}

export default {
  getTeam,
  CreateTeam,
  deleteTeam,
  updateTeam,
  clickGetTeamMember,
  deleteTeamMember,
  setAdminManage,
  CreateTeamMember
}