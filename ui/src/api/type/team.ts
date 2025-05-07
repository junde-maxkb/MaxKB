interface TeamMember {
  id: string
  username: string
  email: string
  team_id: string
  /**
   * 类型：type：manage 所有者；
   */
  type: string
  user_id: string
}

interface Team {
  id: string
  name: string
  description?: string
  create_time: string
  update_time: string
}

export type { TeamMember, Team }
