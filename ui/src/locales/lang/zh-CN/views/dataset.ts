export default {
  title: '知识库',
  createDataset: '创建知识库',
  general: '通用型',
  web: 'web 站点',
  lark: '飞书',
  yuque: '语雀',
  relatedApplications: '关联应用',
  document_count: '文档数',
  relatedApp_count: '关联应用',
  searchBar: {
    placeholder: '按名称搜索'
  },
  setting: {
    vectorization: '向量化',
    sync: '同步'
  },
  tip: {
    professionalMessage: '社区版最多支持 50 个知识库，如需拥有更多知识库，请升级为专业版。',
    syncSuccess: '同步任务发送成功',
    updateModeMessage: '修改知识库向量模型后，需要对知识库向量化，是否继续保存？'
  },
  delete: {
    confirmTitle: '是否删除知识库：',
    confirmMessage1: '此知识库关联',
    confirmMessage2: '个应用，删除后无法恢复，请谨慎操作。'
  },
  exit: {
    confirmTitle: '是否退出知识库',
    confirmMessage: '退出后，如果通过团队还拥有权限，将保留团队权限；如果完全失去权限，将无法访问该知识库。',
    success: '退出成功'
  },
  tabs: {
    myDataset: '我的知识库',
    sharedDataset: '共享知识库',
    organizationDataset: '机构知识库',
    sharedToMeDataset: '共享给我的知识库',
    searchDataset: '知识库检索'
  },
  search: {
    placeholder: '输入关键词搜索知识库',
    noResults: '暂无搜索结果'
  },

  datasetForm: {
    title: {
      info: '基本信息'
    },
    form: {
      datasetName: {
        label: '知识库名称',
        placeholder: '请输入知识库名称',
        requiredMessage: '请输入知识库名称'
      },
      datasetDescription: {
        label: '知识库描述',
        placeholder:
          '描述知识库的内容，详尽的描述将帮助AI能深入理解该知识库的内容，能更准确的检索到内容，提高该知识库的命中率。',
        requiredMessage: '请输入知识库描述'
      },
      EmbeddingModel: {
        label: '向量模型',
        placeholder: '请选择向量模型',
        requiredMessage: '请输入Embedding模型'
      },
      datasetType: {
        label: '知识库类型',
        generalInfo: '通过上传文件或手动录入构建知识库',
        webInfo: '通过网站链接构建知识库',
        larkInfo: '通过飞书文档构建知识库',
        yuqueInfo: '通过语雀文档构建知识库'
      },
      source_url: {
        label: 'Web 根地址',
        placeholder: '请输入 Web 根地址',
        requiredMessage: ' 请输入 Web 根地址'
      },
      user_id: {
        requiredMessage: '请输入User ID'
      },
      token: {
        requiredMessage: '请输入Token'
      },
      selector: {
        label: '选择器',
        placeholder: '默认为 body，可输入 .classname/#idname/tagname'
      }
    }
  },
  ResultSuccess: {
    title: '知识库创建成功',
    paragraph: '分段',
    paragraph_count: '个分段',
    documentList: '文档列表',
    loading: '导入中',
    buttons: {
      toDataset: '返回知识库列表',
      toDocument: '前往文档'
    }
  },
  syncWeb: {
    title: '同步知识库',
    syncMethod: '同步方式',
    replace: '替换同步',
    replaceText: '重新获取 Web 站点文档，覆盖替换本地知识库中的文档',
    complete: '整体同步',
    completeText: '先删除本地知识库所有文档，重新获取 Web 站点文档',
    tip: '注意：所有同步都会删除已有数据重新获取新数据，请谨慎操作。'
  },
  myDatasets: '我的知识库',
  sharedDatasets: '共享知识库',
  searchDatasets: '知识库检索',
  shareSetting: '共享设置',
  memberName: '成员名称',
  permission: '权限',
  permissionNone: '无权限',
  permissionManage: '管理',
  permissionWrite: '编辑',
  permissionRead: '只读',
  selectMemberOrTeam: '选择成员或团队',
  selectTypePlaceholder: '请选择类型',
  selectPlaceholder: '请选择',
  member: '成员',
  team: '团队',
  type: '共享类型',
  existingPermissions: '现有权限',
  confirmRemovePermission: '确定要移除该权限吗？',
  members: {
    title: '知识库成员',
    addMember: '添加成员',
    removeMember: '移除成员',
    permission: {
      read: '只读',
      write: '读写',
      admin: '管理员'
    },
    searchPlaceholder: '搜索成员',
    noMembers: '暂无成员',
    confirmRemove: '确认移除成员',
    confirmRemoveMessage: '确定要移除该成员吗？'
  },
  statistics: {
    title: '知识库统计',
    totalDocuments: '总文档数',
    totalSegments: '总分段数',
    totalCharacters: '总字符数',
    lastUpdated: '最后更新时间'
  },
  settings: {
    title: '知识库设置',
    basicInfo: '基本信息',
    advancedSettings: '高级设置',
    embeddingSettings: '向量化设置',
    syncSettings: '同步设置',
    saveSuccess: '设置保存成功'
  }
}
