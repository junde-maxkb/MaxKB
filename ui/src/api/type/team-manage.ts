interface TeamMember {
  id: string
  team_id: string
  user_id: string
  team_member_type: string
  username: string
  email: string
  role:string
  is_manager:boolean
  type: string
}

interface Team {
  team_id: string
  team_name: string
  role: string
}

export type { TeamMember, Team }
