import { defineStore } from 'pinia'
import type { datasetData } from '@/api/type/dataset'
import type { UploadUserFile } from 'element-plus'
import datasetApi from '@/api/dataset'
import { type Ref } from 'vue'
import useUserStore from './user'

export interface datasetStateTypes {
  baseInfo: datasetData | null
  webInfo: any
  documentsType: string
  documentsFiles: UploadUserFile[]
}

const useDatasetStore = defineStore({
  id: 'dataset',
  state: (): datasetStateTypes => ({
    baseInfo: null,
    webInfo: null,
    documentsType: '',
    documentsFiles: []
  }),
  actions: {
    saveBaseInfo(info: datasetData | null) {
      this.baseInfo = info
    },
    saveWebInfo(info: any) {
      this.webInfo = info
    },
    saveDocumentsType(val: string) {
      this.documentsType = val
    },
    saveDocumentsFile(file: UploadUserFile[]) {
      this.documentsFiles = file
    },
    async asyncGetAllDataset(loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        datasetApi
          .getAllDataset(loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncGetAllAccessibleDatasets(loading?: Ref<boolean>) {
      return new Promise(async (resolve, reject) => {
        try {
          const userStore = useUserStore()
          const isAdmin = userStore.userInfo?.role === 'ADMIN'
          
          if (isAdmin) {
            // 管理员获取系统中所有知识库
            const allDatasetsRes = await datasetApi.getDataset({ current_page: 1, page_size: 10000 }, {}, loading)
            const allDatasets: any[] = []
            
            if (allDatasetsRes?.data?.records) {
              allDatasetsRes.data.records.forEach((item: any) => {
                allDatasets.push({
                  ...item,
                  source_type: 'admin_all',
                  permission: 'MANAGE' // 管理员对所有知识库都有管理权限
                })
              })
            }
            
            // 去重（以ID为准）
            const uniqueDatasets = allDatasets.filter((item, index, self) => 
              index === self.findIndex(d => d.id === item.id)
            )
            
            resolve({ data: uniqueDatasets })
          } else {
            // 普通用户获取有权限的知识库
            const promises = [
              // 我的知识库
              datasetApi.getAllDataset(loading),
              // 共享给我的知识库
              datasetApi.getSharedToMeDataset({ current_page: 1, page_size: 1000 }, {}, loading)
            ]
            
            const results = await Promise.all(promises)
            const allDatasets: any[] = []
            
            // 处理我的知识库
            if (results[0]?.data) {
              results[0].data.forEach((item: any) => {
                allDatasets.push({
                  ...item,
                  source_type: 'my'
                })
              })
            }
            
            // 处理共享给我的知识库（只保留有写入或管理权限的）
            if (results[1]?.data?.records) {
              results[1].data.records.forEach((item: any) => {
                // 只有 MANAGE 或 WRITE 权限的共享知识库才能进入内页
                if (item.permission === 'MANAGE' || item.permission === 'WRITE') {
                  allDatasets.push({
                    ...item,
                    source_type: 'shared'
                  })
                }
              })
            }
            
            // 去重（以ID为准）
            const uniqueDatasets = allDatasets.filter((item, index, self) => 
              index === self.findIndex(d => d.id === item.id)
            )
            
            resolve({ data: uniqueDatasets })
          }
        } catch (error) {
          reject(error)
        }
      })
    },
    async asyncGetSharedToMeDataset(page: { current_page: number; page_size: number }, param: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        datasetApi
          .getSharedToMeDataset(page, param, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncGetDatasetDetail(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        datasetApi
          .getDatasetDetail(id, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncSyncDataset(id: string, sync_type: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        datasetApi
          .putSyncWebDataset(id, sync_type, loading)
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

export default useDatasetStore
