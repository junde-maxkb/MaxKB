import { Result } from '@/request/Result'
import { get, post, del, put, } from '@/request/index'
import type { Ref } from 'vue'


const prefix = '/data_source'
/**
 * 创建数据源
 * @param 参数
 * 
 */
const addDataSource: (
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (data, loading) => {
  return post(`${prefix}`, data, {}, loading, 1000 * 60 * 5)
}
/**
 * 获取数据源列表
 * @returns {Promise<Result<any>>} 
 */
const getDbSourceList = (): Promise<Result<any>> => {
  return get(`${prefix}`)
}
/**
 * 删除数据源
 * @param {String} team_id 
 * @returns {Promise<Result<boolean>>} 
 */
const deleteDbSource = (id: String): Promise<Result<boolean>> => {
  return del(`${prefix}/${id}`)
}
/**
 * 获取单个数据源详情
 * @param {String} team_id 
 * @returns {Promise<Result<boolean>>} 
 */
const getDataSource = (id: String): Promise<Result<boolean>> => {
  return get(`${prefix}/${id}`)
}
/**
 * 更新数据源信息
 * @param {String} id 
 * @param {any} body 
 * @returns {Promise<Result<any>>} 
 */
const updateSourceData = (id: String, body: any): Promise<Result<any>> => {
  return put(`${prefix}/${id}`, body)
}
/**
 * 查询数据源Schema
 * @param {String} id 
 * @param {any} body 
 * @returns {Promise<Result<any>>} 
 */
const SearchDataSourceSchema: (
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (data, loading) => {
  return post(`${prefix}/get_schema`, data, {}, loading, 1000 * 60 * 5)
}
/**
 * 获取数据源中所有的表
 * @param {String} id 
 * @returns {Promise<Result<boolean>>} 
 */
const getTable = (id: String): Promise<Result<boolean>> => {
  return get(`${prefix}/get_table/${id}`)
}
/**
 * 获取数据源中表中的字段
 * @param {String} id 
 *  @param {String} table_name 
 * @returns {Promise<Result<boolean>>} 
 */
const getTableColumns = (id: String,table_name: String): Promise<Result<boolean>> => {
  return get(`${prefix}/${id}/${table_name}`)
}
/**
 * 测试连接数据库
 * @param {any} body 
 * @returns {Promise<Result<any>>} 
 */
const testConnect: (
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (data, loading) => {
  return post(`${prefix}/test_connect`, data, {}, loading, 1000 * 60 * 5)
}
export default {
 addDataSource,
 getDbSourceList,
 deleteDbSource,
 getDataSource,
 updateSourceData,
 SearchDataSourceSchema,
 getTable,
 getTableColumns,
 testConnect
}
