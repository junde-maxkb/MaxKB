import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { TeamMember, Team } from '@/api/type/team'

const prefix = '/team/member'

/**
 * 获取团队成员列表
 */
const getTeamMember: () => Promise<Result<TeamMember[]>> = () => {
  return get(`${prefix}`)
}

/**
 * 添加成员
 * @param 参数 []
 */
const postCreatTeamMember: (data: Array<String>) => Promise<Result<boolean>> = (data) => {
  return post(`${prefix}/_batch`, data)
}

/**
 * 删除成员
 * @param 参数 member_id
 */
const delTeamMember: (member_id: String) => Promise<Result<boolean>> = (member_id) => {
  return del(`${prefix}/${member_id}`)
}

/**
 * 获取成员权限
 * @param 参数 member_id
 */
const getMemberPermissions: (member_id: String) => Promise<Result<any>> = (member_id) => {
  return get(`${prefix}/${member_id}`)
}

/**
 * 获取成员权限
 * @param 参数 member_id
 * @param 参数 {
          "team_member_permission_list": [
            {
              "target_id": "string",
              "type": "string",
              "operate": {
                "USE": true,
                "MANAGE": true
              }
            }
          ]
        }
 */
const putMemberPermissions: (member_id: String, body: any) => Promise<Result<any>> = (
  member_id,
  body
) => {
  return put(`${prefix}/${member_id}`, body)
}

/**
 * 获取当前用户所在所有团队
 */
const getCurrentUserTeams: () => Promise<Result<Team[]>> = () => {
  return get('/team/user_teams')
}

/**
 * 获取可选用户或团队列表
 * @param 参数 keyword 搜索关键词
 */
const getAvailableUsersOrTeams: (keyword?: string) => Promise<Result<any[]>> = (keyword) => {
  return get('/team/shareable-list', { params: { keyword } })
}

export default {
  getTeamMember,
  postCreatTeamMember,
  delTeamMember,
  getMemberPermissions,
  putMemberPermissions,
  getCurrentUserTeams,
  getAvailableUsersOrTeams
}
