export default {
  title: '团队管理',
  teamList: '团队列表',
  teamMemberList: '团队成员列表',
  EditTeam: '编辑团队名称',
  addTeamMember: '新增团队成员',
  addTeam: '新增团队',
  manage:"管理",
  team: {
    SearBar:{
      placeholder:'请输入团队名搜索'
    },
    delete: {
      button: '删除',
      confirmTitle: '是否删除团队:',
      confirmMessage: '删除团队会默认删除团队中所有成员'
    },
    
  },
  member: {
    title:"团队成员列表",
    addMember:'新增团队成员',
    delete: {
      confirmTitle: '是否删除团队成员:',
      confirmMessage: ''
    },
    teamForm: {
      name: {
          label: '用户名/邮箱',
          placeholder: '请输入用户名/邮箱',
          requiredMessage: '用户名/邮箱不能为空'
        }
    },
  },
  team_member_type:{
    "label":"用户类型",
    "member":"普通成员",
    "manager":"管理员",
    "admin":"系统管理员"
  },
  addSubTitle: '成员登录后可以访问到您授权的数据。',


  setting: {
    setTeamManager: "设置管理员",
    cancelTeamManager: "删除管理员"
  },
  teamForm: {
    name: {
      label: '团队名称',
      placeholder: '请输入团队名称',
      requiredMessage: '团队名称不能为空'
    },
     
 
  },
  setTeamManager: {
    setConfirmTitle: '是否设置团队管理员: ',
    cancelConfirmTitle: '是否删除团队管理员: ',
    setConfirmMessage: '警告：您即将授予该用户系统管理员权限',
    cancelConfirmMessage: '警告：您即将删除该用户系统管理员权限',
    setTeamManagerSuccess: "设置管理员成功",
    setTeamManagerFailed: "设置管理员失败",
    cancelTeamManagerSuccess: "取消管理员成功",
    cancelTeamManagerFailed: "取消管理员失败",
    
  }
}
