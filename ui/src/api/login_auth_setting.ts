import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'

const prefix = '/login_auth_setting'


/**
 * 获取登录认证设置
 */
const getLoginAuthSetting: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading
) => {
  return get(`${prefix}`, undefined, loading)
}


/**
 * 修改登录认证
 */
const putLoginAuthSetting: (
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (data, loading) => {
  return put(`${prefix}`,  data,undefined, loading)
}

export default {
  getLoginAuthSetting,
  putLoginAuthSetting
}
