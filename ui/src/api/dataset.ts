import { Result } from '@/request/Result'
import { get, post, del, put, exportExcel, exportFile } from '@/request/index'
import type { datasetData } from '@/api/type/dataset'
import type { pageRequest } from '@/api/type/common'
import type { ApplicationFormType } from '@/api/type/application'
import type { WebDatasetData, LarkDatasetData, QADatasetData, DatasetHitTestData, LarkDocumentListData, ImportLarkDocumentData, GenerateRelatedData } from '@/api/type/datasetTypes'
import { type Ref } from 'vue'

const prefix = '/dataset'

/**
 * 获取分页知识库
 * @param 参数
 * page {
 "current_page": "string",
 "page_size": "string",
 }
 * param {
 "name": "string",
 }
 */
const getDataset: (
  page: pageRequest,
  param: { name?: string },
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 获取全部知识库
 * @param 参数
 */
const getAllDataset: (loading?: Ref<boolean>) => Promise<Result<any[]>> = (loading) => {
  return get(`${prefix}`, undefined, loading)
}

/**
 * 删除知识库
 * @param 参数 dataset_id
 */
const delDataset: (dataset_id: String, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  dataset_id,
  loading
) => {
  return del(`${prefix}/${dataset_id}`, undefined, {}, loading)
}

/**
 * 创建知识库
 * @param 参数
 * {
 "name": "string",
 "desc": "string",
 "documents": [
 {
 "name": "string",
 "paragraphs": [
 {
 "content": "string",
 "title": "string",
 "problem_list": [
 {
 "id": "string",
 "content": "string"
 }
 ]
 }
 ]
 }
 ]
 }
 */
const postDataset: (data: datasetData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}`, data, undefined, loading, 1000 * 60 * 5)
}

/**
 * 创建Web知识库
 * @param 参数
 * {
 "name": "string",
 "desc": "string",
 "source_url": "string",
 "selector": "string",
 }
 */
const postWebDataset: (data: WebDatasetData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}/web`, data, undefined, loading)
}
/**
 * 创建Lark知识库
 * @param 参数
 * {
 "name": "string",
 "desc": "string",
 "app_id": "string",
 "app_secret": "string",
 "folder_token": "string",
 }
 */
const postLarkDataset: (data: LarkDatasetData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}/lark/save`, data, undefined, loading)
}

/**
 * 创建QA知识库
 * @param 参数 formData
 * {
 "file": "file",
 "name": "string",
 "desc": "string",
 }
 */
const postQADataset: (data: QADatasetData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}/qa`, data, undefined, loading)
}

/**
 * 知识库详情
 * @param 参数 dataset_id
 */
const getDatasetDetail: (dataset_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  dataset_id,
  loading
) => {
  return get(`${prefix}/${dataset_id}`, undefined, loading)
}

/**
 * 修改知识库信息
 * @param 参数
 * dataset_id
 * {
 "name": "string",
 "desc": true
 }
 */
const putDataset: (
  dataset_id: string,
  data: { name?: string, desc?: string },
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, data, loading) => {
  return put(`${prefix}/${dataset_id}`, data, undefined, loading)
}
const putLarkDataset: (
  dataset_id: string,
  data: { name?: string, desc?: string, app_id?: string, app_secret?: string, folder_token?: string },
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, data, loading) => {
  return put(`${prefix}/lark/${dataset_id}`, data, undefined, loading)
}
/**
 * 获取知识库 可关联的应用列表
 * @param dataset_id
 * @param loading
 * @returns
 */
const listUsableApplication: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<ApplicationFormType>>> = (dataset_id, loading) => {
  return get(`${prefix}/${dataset_id}/application`, {}, loading)
}

/**
 * 命中测试列表
 * @param dataset_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getDatasetHitTest: (
  dataset_id: string,
  data: DatasetHitTestData,
  loading?: Ref<boolean>
) => Promise<Result<Array<any>>> = (dataset_id, data, loading) => {
  return get(`${prefix}/${dataset_id}/hit_test`, data, loading)
}

/**
 * 同步知识库
 * @param 参数 dataset_id
 * @query 参数 sync_type // 同步类型->replace:替换同步,complete:完整同步
 */
const putSyncWebDataset: (
  dataset_id: string,
  sync_type: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, sync_type, loading) => {
  return put(`${prefix}/${dataset_id}/sync_web`, undefined, { sync_type }, loading)
}

/**
 * 向量化知识库
 * @param 参数 dataset_id
 */
const putReEmbeddingDataset: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, loading) => {
  return put(`${prefix}/${dataset_id}/re_embedding`, undefined, undefined, loading)
}

/**
 * 导出知识库
 * @param dataset_name 知识库名称
 * @param dataset_id   知识库id
 * @returns
 */
const exportDataset: (
  dataset_name: string,
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<any> = (dataset_name, dataset_id, loading) => {
  return exportExcel(dataset_name + '.xlsx', `dataset/${dataset_id}/export`, undefined, loading)
}
/**
 *导出Zip知识库
 * @param dataset_name 知识库名称
 * @param dataset_id   知识库id
 * @param loading      加载器
 * @returns
 */
const exportZipDataset: (
  dataset_name: string,
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<any> = (dataset_name, dataset_id, loading) => {
  return exportFile(dataset_name + '.zip', `dataset/${dataset_id}/export_zip`, undefined, loading)
}

/**
 * 获取当前用户可使用的模型列表
 * @param application_id
 * @param loading
 * @query  { query_text: string, top_number: number, similarity: number }
 * @returns
 */
const getDatasetModel: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<Array<any>>> = (dataset_id, loading) => {
  return get(`${prefix}/${dataset_id}/model`, loading)
}
/**
 * 获取飞书文档列表
 * @param dataset_id
 * @param folder_token
 * @param loading
 * @returns
 */
const getLarkDocumentList: (
  dataset_id: string,
  folder_token: string,
  data: LarkDocumentListData,
  loading?: Ref<boolean>
) => Promise<Result<Array<any>>> = (dataset_id, folder_token, data, loading) => {
  return post(`${prefix}/lark/${dataset_id}/${folder_token}/doc_list`, data, null, loading)
}

const importLarkDocument: (
  dataset_id: string,
  data: ImportLarkDocumentData,
  loading?: Ref<boolean>
) => Promise<Result<Array<any>>> = (dataset_id, data, loading) => {
  return post(`${prefix}/lark/${dataset_id}/import`, data, null, loading)
}
/**
 * 生成关联问题
 * @param dataset_id 知识库id
 * @param data
 * @param loading
 * @returns
 */
const generateRelated: (
  dataset_id: string,
  data: GenerateRelatedData,
  loading?: Ref<boolean>
) => Promise<Result<Array<any>>> = (dataset_id, data, loading) => {
  return put(`${prefix}/${dataset_id}/generate_related`, data, null, loading)
}

/**
 * 获取知识库团队成员及其权限
 * @param dataset_id 知识库ID
 * @param loading 加载状态
 * @returns 团队成员及其权限信息
 */
const getDatasetMembers: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<{
  dataset_id: string;
  members: Array<{
    user_id: string;
    username: string;
    permission: string;
  }>;
}>> = (dataset_id, loading) => {
  return get(`${prefix}/${dataset_id}/members`, undefined, loading);
}

/**
 * 更新知识库成员权限
 * @param dataset_id 知识库ID
 * @param data 更新数据 { user_id: string, permission: string }
 * @param loading 加载状态
 * @returns 更新结果
 */
const putMemberPermission: (
  dataset_id: string,
  data: { user_id: string; permission: string ,share_with_type: string},
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, data, loading) => {
  return put(`${prefix}/${dataset_id}/members/put_permissions`, data, undefined, loading)
}

/**
 * 退出共享知识库
 * @param dataset_id 知识库ID
 * @param loading 加载状态
 */
const putExitShare: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (dataset_id, loading) => {
  return put(`${prefix}/${dataset_id}/exit_share`, undefined, undefined, loading)
}

/**
 * 获取共享给我的知识库列表
 * @param page 分页参数
 * @param param 查询参数
 * @param loading 加载状态
 */
const getSharedToMeDataset: (
  page: pageRequest,
  param: {
    name?: string;
    select_user_id?: string;
  },
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/share/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 获取当前用户对知识库的权限
 * @param dataset_id 知识库ID
 * @param loading 加载状态
 */
const getCurrentUserPermission: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<{
  dataset_id: string;
  permission: string;
}>> = (dataset_id, loading) => {
  return get(`${prefix}/${dataset_id}/current_user_permission`, undefined, loading)
}

/**
 * 获取机构知识库分页列表
 * @param page 分页参数
 * @param param 查询参数
 * @param loading 加载状态
 * @returns Promise<Result<any>>
 */
const getOrganizationDataset: (
  page: pageRequest,
  param: {
    name?: string;
    desc?: string;
  },
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/organization/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 获取回收站知识库分页列表
 * @param page 分页参数
 * @param param 查询参数
 * @param loading 加载状态
 * @returns Promise<Result<any>>
 */
const getRecycleBinDataset: (
  page: pageRequest,
  param: {
    name?: string;
    desc?: string;
  },
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/recycle_bin/${page.current_page}/${page.page_size}`, param, loading)
}

const addToOrganization: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, loading) => {
  return post(`${prefix}/${dataset_id}/add_to_organization`, undefined, undefined, loading)
}

/**
 * 从机构知识库中移除
 * @param dataset_id 知识库ID
 * @param loading 加载状态
 */
const removeFromOrganization: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, loading) => {
  return post(`${prefix}/${dataset_id}/remove_from_organization`, undefined, undefined, loading)
}

/**
 * 恢复已删除的知识库
 * @param dataset_id
 * @param loading
 * @returns
 */
const restoreDataset: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, loading) => {
  return put(`${prefix}/${dataset_id}/restore`, {}, undefined, loading)
}

/**
 * 永久删除知识库
 * @param dataset_id
 * @param loading
 * @returns
 */
const permanentlyDeleteDataset: (
  dataset_id: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (dataset_id, loading) => {
  return del(`${prefix}/${dataset_id}/permanently`, undefined, {}, loading)
}

export default {
  getDataset,
  getAllDataset,
  delDataset,
  postDataset,
  postWebDataset,
  postLarkDataset,
  postQADataset,
  getDatasetDetail,
  putDataset,
  putLarkDataset,
  listUsableApplication,
  getDatasetHitTest,
  putSyncWebDataset,
  putReEmbeddingDataset,
  exportDataset,
  exportZipDataset,
  getDatasetModel,
  getLarkDocumentList,
  importLarkDocument,
  generateRelated,
  getDatasetMembers,
  putMemberPermission,
  putExitShare,
  getSharedToMeDataset,
  getCurrentUserPermission,
  getOrganizationDataset,
  getRecycleBinDataset,
  addToOrganization,
  removeFromOrganization,
  restoreDataset,
  permanentlyDeleteDataset
}
