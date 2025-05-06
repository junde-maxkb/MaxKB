import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import { type Ref } from 'vue'

const prefix = '/github_auth'

/**
 * 发起oauth2认证
 */
const startOauthLogin: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
    data,
    loading
  ) => {
    return get(`${prefix}`, undefined, loading)
  }

export default {
  startOauthLogin
}
