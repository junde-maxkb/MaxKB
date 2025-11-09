export default {
  title: '用户管理',
  createUser: '创建用户',
  editUser: '编辑用户',
  setting: {
    updatePwd: '修改用户密码',
    setAdmin: '设置系统管理员'
  },
  tip: {
    professionalMessage: '社区版最多支持 2 个用户，如需拥有更多用户，请升级为专业版。',
    updatePwdSuccess: '修改用户密码成功'
  },
  delete: {
    confirmTitle: '是否删除用户：',
    confirmMessage: '删除用户，该用户创建的资源（应用、知识库、模型）都会删除，请谨慎操作。'
  },
  setAdmin: {
    confirmTitle: '是否设置用户为系统管理员：',
    confirmMessage: '警告：您即将授予该用户系统管理员权限',
    setAdminFailed: "设置系统管理员失败",
    setAdminSuccess: "设置系统管理员成功"
  },
  disabled: {
    confirmTitle: '是否禁用函数：',
    confirmMessage: '禁用后，引用了该函数的应用提问时会报错 ，请谨慎操作。'
  },
  userForm: {
    form: {
      username: {
        label: '用户名',
        placeholder: '请输入用户名',
        requiredMessage: '请输入用户名',
        lengthMessage: '长度在 2 到 20 个字符'
      },
      nick_name: {
        label: '姓名',
        placeholder: '请输入姓名'
      },
      email: {
        label: '邮箱',
        placeholder: '请输入邮箱',
        requiredMessage: '请输入邮箱',
        validatorEmail: '请输入有效邮箱格式！',
      },
      phone: {
        label: '手机号',
        placeholder: '请输入手机号'
      },
      password: {
        label: '登录密码',
        placeholder: '请输入密码',
        requiredMessage: '请输入密码',
        lengthMessage: '长度在 6 到 20 个字符'
      },
      new_password: {
        label: '新密码',
        placeholder: '请输入新密码',
        requiredMessage: '请输入新密码',
      },
      re_password: {
        label: '确认密码',
        placeholder: '请输入确认密码',
        requiredMessage: '请输入确认密码',
        validatorMessage: '密码不一致',
      }
    }
  },
  source: {
    label: '用户类型',
    local: '系统用户',
    wecom: '企业微信',
    lark: '飞书',
    dingtalk: '钉钉'
  },
  chatHistory: {
    title: '历史聊天记录',
    viewHistory: '查看历史记录',
    history: '历史记录',
    messages: '条消息',
    noHistory: '暂无历史记录',
    searchPlaceholder: '搜索标题或应用名称',
    filterByApp: '按应用筛选',
    sortBy: '排序方式',
    sortByTime: '按时间排序',
    sortByMessages: '按消息数排序',
    viewDetail: '查看详情',
    user: '用户',
    assistant: '助手',
    messageIndex: '消息序号',
    noMessages: '暂无消息'
  }
}
