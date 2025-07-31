import { defineStore } from 'pinia'
import applicationApi from '@/api/application'
import applicationXpackApi from '@/api/application-xpack'
import { type Ref } from 'vue'
import { getBrowserLang } from '@/locales/index'
import useUserStore from './user'
const useApplicationStore = defineStore({
  id: 'application',
  state: () => ({
    location: `${window.location.origin}/ui/chat/`
  }),
  actions: {
    async asyncGetAllApplication() {
      return new Promise((resolve, reject) => {
        applicationApi
          .getAllAppilcation()
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncGetAllAccessibleApplications(loading?: Ref<boolean>) {
      return new Promise(async (resolve, reject) => {
        try {
          const userStore = useUserStore()
          const isAdmin = userStore.userInfo?.role === 'ADMIN'
          
          if (isAdmin) {
            // 管理员获取系统中所有应用
            const allApplicationsRes = await applicationApi.getApplication({ current_page: 1, page_size: 10000 }, {}, loading)
            const allApplications: any[] = []
            
            if (allApplicationsRes?.data?.records) {
              allApplicationsRes.data.records.forEach((item: any) => {
                allApplications.push({
                  ...item,
                  source_type: 'admin_all',
                  permission: 'MANAGE' // 管理员对所有应用都有管理权限
                })
              })
            }
            
            // 去重（以ID为准）
            const uniqueApplications = allApplications.filter((item, index, self) => 
              index === self.findIndex(d => d.id === item.id)
            )
            
            resolve({ data: uniqueApplications })
          } else {
            // 普通用户获取有权限的应用
            const promises = [
              // 我的应用
              applicationApi.getAllAppilcation(),
              // 共享给我的应用
              applicationApi.getShareToMePage({ current_page: 1, page_size: 1000 }, {}, loading)
            ]
            
            const results = await Promise.all(promises)
            const allApplications: any[] = []
            
            // 处理我的应用
            if (results[0]?.data) {
              results[0].data.forEach((item: any) => {
                allApplications.push({
                  ...item,
                  source_type: 'my'
                })
              })
            }
            
            // 处理共享给我的应用（只保留有写入或管理权限的）
            if (results[1]?.data?.records) {
              results[1].data.records.forEach((item: any) => {
                // 只有非只读权限的共享应用才能进入内页
                if (item.permission !== 'read') {
                  allApplications.push({
                    ...item,
                    source_type: 'shared'
                  })
                }
              })
            }
            
            // 去重（以ID为准）
            const uniqueApplications = allApplications.filter((item, index, self) => 
              index === self.findIndex(d => d.id === item.id)
            )
            
            resolve({ data: uniqueApplications })
          }
        } catch (error) {
          reject(error)
        }
      })
    },

    async asyncGetApplicationDetail(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .getApplicationDetail(id, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncGetApplicationDataset(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .getApplicationDataset(id, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncGetAccessToken(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        const user = useUserStore()
        if (user.isEnterprise()) {
          applicationXpackApi
            .getAccessToken(id, loading)
            .then((data) => {
              resolve(data)
            })
            .catch((error) => {
              reject(error)
            })
        } else {
          applicationApi
            .getAccessToken(id, loading)
            .then((data) => {
              resolve(data)
            })
            .catch((error) => {
              reject(error)
            })
        }
      })
    },

    async asyncGetAppProfile(loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .getAppProfile(loading)
          .then((res) => {
            sessionStorage.setItem('language', res.data?.language || getBrowserLang())
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncAppAuthentication(
      token: string,
      loading?: Ref<boolean>,
      authentication_value?: any
    ) {
      return new Promise((resolve, reject) => {
        applicationApi
          .postAppAuthentication(token, loading, authentication_value)
          .then((res) => {
            localStorage.setItem(`${token}-accessToken`, res.data)
            sessionStorage.setItem(`${token}-accessToken`, res.data)
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async refreshAccessToken(token: string) {
      this.asyncAppAuthentication(token)
    },
    // 修改应用
    async asyncPutApplication(id: string, data: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .putApplication(id, data, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async validatePassword(id: string, password: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .validatePassword(id, password, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    }
  }
})

export default useApplicationStore
