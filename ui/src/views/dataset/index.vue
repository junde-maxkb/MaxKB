<template>
  <div class="dataset-list-container p-24" style="padding-top: 16px">
    <el-tabs v-model="datasetType" @tab-change="tabChangeHandle">
      <el-tab-pane :label="$t('views.dataset.tabs.myDataset')" name="MY"></el-tab-pane>
      <el-tab-pane :label="$t('views.dataset.tabs.sharedDataset')" name="SHARED">
        <el-tabs v-model="sharedType" @tab-change="sharedTabChangeHandle" class="mt-16">
          <el-tab-pane :label="$t('views.dataset.tabs.organizationDataset')" name="ORGANIZATION"></el-tab-pane>
          <el-tab-pane :label="$t('views.dataset.tabs.sharedToMeDataset')" name="SHARED_TO_ME"></el-tab-pane>
        </el-tabs>
      </el-tab-pane>
      <el-tab-pane :label="$t('views.dataset.tabs.searchDataset')" name="SEARCH"></el-tab-pane>
      <!-- 回收站标签页 - 只有管理员能看到 -->
      <el-tab-pane 
        v-if="user.userInfo?.role === 'ADMIN'" 
        :label="$t('views.dataset.tabs.recycleBin')" 
        name="RECYCLE_BIN"
      ></el-tab-pane>
    </el-tabs>

    <!-- 原有的数据集列表展示 -->
    <template v-if="datasetType !== 'SEARCH' && datasetType !== 'RECYCLE_BIN'">
      <div class="flex-between mb-16">
        <h4></h4>
        <div class="flex-between">
          <el-select
            v-model="sortField"
            class="mr-12"
            @change="searchHandle"
            style="max-width: 240px; width: 150px"
          >
            <el-option
              v-for="item in sortOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-select
            v-model="selectUserId"
            class="mr-12"
            @change="searchHandle"
            style="max-width: 240px; width: 150px"
          >
            <el-option
              v-for="item in userOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-input
            v-model="searchValue"
            @change="searchHandle"
            :placeholder="$t('views.dataset.searchBar.placeholder')"
            prefix-icon="Search"
            class="w-240"
            style="max-width: 240px"
            clearable
          />
        </div>
      </div>
      <div v-loading.fullscreen.lock="paginationConfig.current_page === 1 && loading">
        <InfiniteScroll
          :size="datasetList.length"
          :total="paginationConfig.total"
          :page_size="paginationConfig.page_size"
          v-model:current_page="paginationConfig.current_page"
          @load="getList"
          :loading="loading"
        >
          <el-row :gutter="15">
            <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" class="mb-16" v-if="datasetType === 'MY'">
              <CardAdd :title="$t('views.dataset.createDataset')" @click="openCreateDialog" />
            </el-col>
            <template v-for="(item, index) in datasetList" :key="index">
              <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" class="mb-16">
                <CardBox
                  :title="item.name"
                  :description="item.desc"
                  :class="{'cursor': item.permission !== 'READ' && !(datasetType === 'SHARED' && sharedType === 'ORGANIZATION')}"
                  @click="!(datasetType === 'SHARED' && sharedType === 'ORGANIZATION') && item.permission !== 'read' && router.push({ path: `/dataset/${item.id}/document` })"
                >
                  <template #icon>
                    <AppAvatar
                      v-if="item.type === '1'"
                      class="mr-8 avatar-purple"
                      shape="square"
                      :size="32"
                    >
                      <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                    </AppAvatar>
                    <AppAvatar
                      v-else-if="item.type === '2'"
                      class="mr-8 avatar-purple"
                      shape="square"
                      :size="32"
                      style="background: none"
                    >
                      <img src="@/assets/logo_lark.svg" style="width: 100%" alt="" />
                    </AppAvatar>
                    <AppAvatar v-else class="mr-8 avatar-blue" shape="square" :size="32">
                      <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                    </AppAvatar>
                  </template>
                  <template #subTitle>
                    <el-text class="color-secondary" size="small">
                      <auto-tooltip :content="item.username">
                        {{ $t('common.creator') }}: {{ item.username }}
                      </auto-tooltip>
                    </el-text>
                  </template>
                  <div class="delete-button">
                    <el-tag class="blue-tag" v-if="item.type === '0'" style="height: 22px">{{
                      $t('views.dataset.general')
                    }}</el-tag>
                    <el-tag
                      class="purple-tag"
                      v-else-if="item.type === '1'"
                      type="warning"
                      style="height: 22px"
                      >{{ $t('views.dataset.web') }}</el-tag
                    >
                    <el-tag
                      class="purple-tag"
                      v-else-if="item.type === '2'"
                      type="warning"
                      style="height: 22px"
                      >{{ $t('views.dataset.lark') }}</el-tag
                    >
                    <el-tag
                      class="purple-tag"
                      v-else-if="item.type === '3'"
                      type="warning"
                      style="height: 22px"
                      >{{ $t('views.dataset.yuque') }}</el-tag
                    >
                    <el-tag
                      v-if="datasetType === 'SHARED' && sharedType === 'SHARED_TO_ME'"
                      :class="{
                        'purple-tag': item.permission === 'MANAGE',
                        'blue-tag': item.permission === 'WRITE',
                        'green-tag': item.permission === 'read'
                      }"
                      style="height: 22px; margin-left: 8px"
                      >{{ 
                        item.permission === 'MANAGE' 
                          ? $t('views.dataset.permissionManage') 
                          : item.permission === 'WRITE' 
                            ? $t('views.dataset.permissionWrite') 
                            : $t('views.dataset.permissionRead') 
                      }}</el-tag
                    >
                  </div>

                  <template #footer>
                    <div class="footer-content flex-between">
                      <div>
                        <span class="bold">{{ item?.document_count || 0 }}</span>
                        {{ $t('views.dataset.document_count') }}<el-divider direction="vertical" />
                        <span class="bold">{{ numberFormat(item?.char_length) || 0 }}</span>
                        {{ $t('common.character') }}<el-divider direction="vertical" />
                        <span class="bold">{{ item?.application_mapping_count || 0 }}</span>
                        {{ $t('views.dataset.relatedApp_count') }}
                      </div>
                      <div @click.stop>
                        <el-dropdown trigger="click">
                          <el-button text @click.stop>
                            <el-icon><MoreFilled /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item
                                v-if="datasetType === 'SHARED' && sharedType === 'ORGANIZATION' && user.userInfo?.role === 'ADMIN'"
                                icon="Close"
                                @click.stop="removeFromOrganization(item)">{{
                                $t('views.dataset.setting.removeFromOrganization')
                              }}</el-dropdown-item>
                              <template v-if="!(datasetType === 'SHARED' && sharedType === 'ORGANIZATION')">
                                <el-dropdown-item
                                  v-if="(datasetType === 'MY' || (datasetType === 'SHARED' && sharedType === 'ORGANIZATION')) && item.type === '1'"
                                  icon="Refresh"
                                  @click.stop="syncDataset(item)"
                                  >{{ $t('views.dataset.setting.sync') }}</el-dropdown-item
                                >
                                <el-dropdown-item 
                                  v-if="datasetType === 'MY' || (datasetType === 'SHARED' && sharedType === 'ORGANIZATION') || (datasetType === 'SHARED' && sharedType === 'SHARED_TO_ME' && (item.permission === 'MANAGE' || item.permission === 'WRITE'))"
                                  @click="reEmbeddingDataset(item)">
                                  <AppIcon
                                    iconName="app-document-refresh"
                                    style="font-size: 16px"
                                  ></AppIcon>
                                  {{ $t('views.dataset.setting.vectorization') }}</el-dropdown-item
                                >
                                <el-dropdown-item
                                  v-if="datasetType === 'MY' || (datasetType === 'SHARED' && sharedType === 'ORGANIZATION') || (datasetType === 'SHARED' && sharedType === 'SHARED_TO_ME' && item.permission === 'MANAGE')"
                                  icon="Connection"
                                  @click.stop="openGenerateDialog(item)"
                                  >{{ $t('views.document.generateQuestion.title') }}</el-dropdown-item
                                >
                                <el-dropdown-item
                                  v-if="datasetType === 'MY' || (datasetType === 'SHARED' && sharedType === 'ORGANIZATION') || (datasetType === 'SHARED' && sharedType === 'SHARED_TO_ME' && item.permission === 'MANAGE')"
                                  icon="Setting"
                                  @click.stop="router.push({ path: `/dataset/${item.id}/setting` })"
                                >
                                  {{ $t('common.setting') }}</el-dropdown-item
                                >
                                <el-dropdown-item 
                                  v-if="datasetType === 'MY' || (datasetType === 'SHARED' && sharedType === 'ORGANIZATION') || (datasetType === 'SHARED' && sharedType === 'SHARED_TO_ME' && item.permission === 'MANAGE')"
                                  @click.stop="export_dataset(item)">
                                  <AppIcon iconName="app-export"></AppIcon
                                  >{{ $t('views.document.setting.export') }} Excel</el-dropdown-item
                                >
                                <el-dropdown-item 
                                  v-if="datasetType === 'MY' || (datasetType === 'SHARED' && sharedType === 'ORGANIZATION') || (datasetType === 'SHARED' && sharedType === 'SHARED_TO_ME' && item.permission === 'MANAGE')"
                                  @click.stop="export_zip_dataset(item)">
                                  <AppIcon iconName="app-export"></AppIcon
                                  >{{ $t('views.document.setting.export') }} ZIP</el-dropdown-item
                                >
                                <el-dropdown-item 
                                  v-if="datasetType === 'SHARED' && sharedType === 'SHARED_TO_ME' && (item.permission === 'MANAGE' || item.permission === 'WRITE' || item.permission === 'read')"
                                  icon="Close"
                                  @click.stop="exitDataset(item)">{{
                                  $t('common.exit')
                                }}</el-dropdown-item>
                                <el-dropdown-item 
                                  v-if="datasetType === 'MY'"
                                  icon="Delete"
                                  @click.stop="deleteDataset(item)">{{
                                  $t('common.delete')
                                }}</el-dropdown-item>
                                <el-dropdown-item 
                                  v-if="datasetType === 'MY'"
                                  icon="OfficeBuilding"
                                  @click.stop="addToOrganization(item)">{{
                                  $t('views.dataset.setting.addToOrganization')
                                }}</el-dropdown-item>
                              </template>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                    </div>
                  </template>
                </CardBox>
              </el-col>
            </template>
          </el-row>
        </InfiniteScroll>
      </div>
    </template>

    <!-- 多知识库检索功能 -->
    <template v-else-if="datasetType === 'SEARCH'">
      <div class="knowledge-search-container">
        <!-- 知识库选择区域 -->
        <div class="dataset-selection-section mb-24">
          <div class="flex-between mb-16">
            <h4>{{ $t('views.dataset.searchDataset.selectDatasets') }}</h4>
            <el-button type="primary" link @click="openDatasetDialog">
              <el-icon class="mr-4">
                <Plus />
              </el-icon>
              {{ $t('common.add') }}
            </el-button>
          </div>
          <div class="dataset-selection-content">
            <el-text type="info" v-if="selectedDatasets.length === 0" class="empty-placeholder">
              {{ $t('views.dataset.searchDataset.selectDatasetsPlaceholder') }}
            </el-text>
            <el-row :gutter="12" v-else>
              <el-col
                :xs="24"
                :sm="12"
                :md="8"
                :lg="6"
                :xl="6"
                class="mb-12"
                v-for="(datasetId, index) in selectedDatasets"
                :key="index"
              >
                <el-card class="relate-dataset-card border-r-4" shadow="never">
                  <div class="flex-between">
                    <div class="flex align-center dataset-info">
                      <AppAvatar
                        v-if="getDatasetById(datasetId)?.type === '1'"
                        class="mr-8 avatar-purple"
                        shape="square"
                        :size="32"
                      >
                        <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                      </AppAvatar>
                      <AppAvatar
                        v-else-if="getDatasetById(datasetId)?.type === '2'"
                        class="mr-8 avatar-purple"
                        shape="square"
                        :size="32"
                        style="background: none"
                      >
                        <img src="@/assets/logo_lark.svg" style="width: 100%" alt="" />
                      </AppAvatar>
                      <AppAvatar v-else class="mr-8 avatar-blue" shape="square" :size="32">
                        <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                      </AppAvatar>

                      <span
                        class="ellipsis dataset-name"
                        :title="getDatasetById(datasetId)?.name"
                      >
                        {{ getDatasetById(datasetId)?.name }}
                      </span>
                    </div>
                    <el-button text @click="removeDataset(datasetId)" class="remove-btn">
                      <el-icon>
                        <Close />
                      </el-icon>
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </div>

        <!-- 搜索结果区域 -->
        <LayoutContainer>
          <template #header>
            <h4>
              {{ $t('views.dataset.searchDataset.searchResult') }}
              <el-text type="info" class="ml-4">{{ $t('views.dataset.searchDataset.searchResultTip') }}</el-text>
            </h4>
          </template>
          <div class="search-result__main p-16" v-loading="searchLoading">
            <div class="question-title" :style="{ visibility: questionTitle ? 'visible' : 'hidden' }">
              <div class="avatar">
                <AppAvatar>
                  <img src="@/assets/user-icon.svg" style="width: 54%" alt="" />
                </AppAvatar>
              </div>
              <div class="content">
                <h4 class="text break-all">{{ questionTitle }}</h4>
              </div>
            </div>
            <el-scrollbar>
              <div class="search-result-height">
                <el-empty
                  v-if="firstSearch"
                  :image="emptyImg"
                  :description="$t('views.dataset.searchDataset.emptyMessage1')"
                  style="padding-top: 160px"
                  :image-size="125"
                />
                <el-empty
                  v-else-if="searchResults.length == 0"
                  :description="$t('views.dataset.searchDataset.emptyMessage2')"
                  style="padding-top: 160px"
                  :image-size="125"
                />
                <el-row v-else>
                  <el-col
                    :xs="24"
                    :sm="12"
                    :md="12"
                    :lg="8"
                    :xl="6"
                    v-for="(item, index) in searchResults"
                    :key="index"
                    class="p-8"
                  >
                    <CardBox
                      shadow="hover"
                      :title="item.title || '-'"
                      :description="item.content"
                      class="document-card layout-bg layout-bg cursor"
                      :class="item.is_active ? '' : 'disabled'"
                      :showIcon="false"
                      @click="editParagraph(item)"
                    >
                      <template #icon>
                        <AppAvatar class="mr-12 avatar-light" :size="22">
                          {{ index + 1 + '' }}</AppAvatar
                        >
                      </template>
                      <div class="active-button primary">{{ item.similarity?.toFixed(3) }}</div>
                      <template #footer>
                        <div class="footer-content flex-between">
                          <el-text>
                            <el-icon>
                              <Document />
                            </el-icon>
                            {{ item?.document_name }}
                          </el-text>
                          <el-text class="dataset-source">
                            <el-icon>
                              <Collection />
                            </el-icon>
                            {{ getDatasetName(item.dataset_id) }}
                          </el-text>
                        </div>
                      </template>
                    </CardBox>
                  </el-col>
                </el-row>
              </div>
            </el-scrollbar>
          </div>

          <ParagraphDialog ref="ParagraphDialogRef" :title="paragraphDialogTitle" @refresh="refreshParagraph" />
        </LayoutContainer>

        <!-- 操作区域 -->
        <div class="search-operate p-24 pt-0">
          <el-popover :visible="popoverVisible" placement="right-end" :width="500" trigger="click">
            <template #reference>
              <el-button icon="Setting" class="mb-8" @click="settingChange('open')">{{
                $t('common.paramSetting')
              }}</el-button>
            </template>
            <div class="mb-16">
              <div class="title mb-8">
                {{ $t('views.application.applicationForm.dialog.selectSearchMode') }}
              </div>
              <el-radio-group
                v-model="cloneForm.search_mode"
                class="card__radio"
                @change="changeHandle"
              >
                <el-card
                  shadow="never"
                  class="mb-16"
                  :class="cloneForm.search_mode === 'embedding' ? 'active' : ''"
                >
                  <el-radio value="embedding" size="large">
                    <p class="mb-4">
                      {{ $t('views.application.applicationForm.dialog.vectorSearch') }}
                    </p>
                    <el-text type="info">{{
                      $t('views.application.applicationForm.dialog.vectorSearchTooltip')
                    }}</el-text>
                  </el-radio>
                </el-card>
                <el-card
                  shadow="never"
                  class="mb-16"
                  :class="cloneForm.search_mode === 'keywords' ? 'active' : ''"
                >
                  <el-radio value="keywords" size="large">
                    <p class="mb-4">
                      {{ $t('views.application.applicationForm.dialog.fullTextSearch') }}
                    </p>
                    <el-text type="info">{{
                      $t('views.application.applicationForm.dialog.fullTextSearchTooltip')
                    }}</el-text>
                  </el-radio>
                </el-card>
                <el-card
                  shadow="never"
                  class="mb-16"
                  :class="cloneForm.search_mode === 'blend' ? 'active' : ''"
                >
                  <el-radio value="blend" size="large">
                    <p class="mb-4">
                      {{ $t('views.application.applicationForm.dialog.hybridSearch') }}
                    </p>
                    <el-text type="info">{{
                      $t('views.application.applicationForm.dialog.hybridSearchTooltip')
                    }}</el-text>
                  </el-radio>
                </el-card>
              </el-radio-group>
            </div>
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="mb-16">
                  <div class="title mb-8">
                    {{ $t('views.application.applicationForm.dialog.similarityThreshold') }}
                  </div>
                  <el-input-number
                    v-model="cloneForm.similarity"
                    :min="0"
                    :max="cloneForm.search_mode === 'blend' ? 2 : 1"
                    :precision="3"
                    :step="0.1"
                    :value-on-clear="0"
                    controls-position="right"
                    class="w-full"
                  />
                </div>
              </el-col>
              <el-col :span="12">
                <div class="mb-16">
                  <div class="title mb-8">
                    {{ $t('views.application.applicationForm.dialog.topReferences') }}
                  </div>
                  <el-input-number
                    v-model="cloneForm.top_number"
                    :min="1"
                    :max="10000"
                    controls-position="right"
                    class="w-full"
                  />
                </div>
              </el-col>
            </el-row>

            <div class="text-right">
              <el-button @click="popoverVisible = false">{{ $t('common.cancel') }}</el-button>
              <el-button type="primary" @click="settingChange('close')">{{
                $t('common.confirm')
              }}</el-button>
            </div>
          </el-popover>
          <div class="operate-textarea flex">
            <el-input
              ref="quickInputRef"
              v-model="inputValue"
              type="textarea"
              :placeholder="$t('views.dataset.searchDataset.inputPlaceholder')"
              :autosize="{ minRows: 1, maxRows: 8 }"
              @keydown.enter="sendSearchHandle($event)"
            />
            <div class="operate">
              <el-button
                text
                class="sent-button"
                :disabled="isDisabledSearch || searchLoading"
                @click="sendSearchHandle"
              >
                <img v-show="isDisabledSearch || searchLoading" src="@/assets/icon_send.svg" alt="" />
                <img
                  v-show="!isDisabledSearch && !searchLoading"
                  src="@/assets/icon_send_colorful.svg"
                  alt=""
                />
              </el-button>
            </div>
          </div>
        </div>

        <!-- 添加知识库对话框 -->
        <AddDatasetDialog
          ref="AddDatasetDialogRef"
          :data="availableDatasets"
          :loading="datasetsLoading"
          @addData="addDatasets"
          @refresh="loadAvailableDatasets"
        />
      </div>
    </template>

    <!-- 回收站功能 -->
    <template v-else-if="datasetType === 'RECYCLE_BIN'">
      <div class="recycle-bin-container">
        <div class="flex-between mb-16">
          <h4>{{ $t('views.dataset.recycleBin.title') }}</h4>
          <div class="flex-between">
            <el-input
              v-model="recycleBinSearchValue"
              @change="searchRecycleBinHandle"
              :placeholder="$t('views.dataset.searchBar.placeholder')"
              prefix-icon="Search"
              class="w-240"
              style="max-width: 240px"
              clearable
            />
          </div>
        </div>
        <div v-loading.fullscreen.lock="loading">
          <el-row :gutter="15">
            <template v-for="(item, index) in recycleBinList" :key="index">
              <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" class="mb-16">
                <CardBox
                  :title="item.name"
                  :description="item.desc"
                  class="recycle-dataset-card"
                >
                  <template #icon>
                    <AppAvatar
                      v-if="item.type === '1'"
                      class="mr-8 avatar-purple"
                      shape="square"
                      :size="32"
                    >
                      <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                    </AppAvatar>
                    <AppAvatar
                      v-else-if="item.type === '2'"
                      class="mr-8 avatar-purple"
                      shape="square"
                      :size="32"
                      style="background: none"
                    >
                      <img src="@/assets/logo_lark.svg" style="width: 100%" alt="" />
                    </AppAvatar>
                    <AppAvatar v-else class="mr-8 avatar-blue" shape="square" :size="32">
                      <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                    </AppAvatar>
                  </template>
                  <template #subTitle>
                    <el-text class="color-secondary" size="small">
                      <auto-tooltip :content="item.creator_name">
                        {{ $t('common.creator') }}: {{ item.creator_name }}
                      </auto-tooltip>
                    </el-text>
                  </template>
                  <div class="delete-button">
                    <el-tag class="red-tag" style="height: 22px">
                      {{ $t('views.dataset.recycleBin.deleted') }}
                    </el-tag>
                  </div>

                  <template #footer>
                    <div class="footer-content flex-between">
                      <div>
                        <span class="bold">{{ item?.document_count || 0 }}</span>
                        {{ $t('views.dataset.document_count') }}<el-divider direction="vertical" />
                        <span class="bold">{{ numberFormat(item?.char_length) || 0 }}</span>
                        {{ $t('common.character') }}<el-divider direction="vertical" />
                        <span class="text-xs text-gray-500">{{ formatDeleteTime(item.delete_time) }}</span>
                      </div>
                      <div @click.stop>
                        <el-dropdown trigger="click">
                          <el-button text @click.stop>
                            <el-icon><MoreFilled /></el-icon>
                          </el-button>
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item 
                                icon="RefreshRight"
                                @click.stop="restoreDataset(item)">{{
                                $t('views.dataset.recycleBin.restore')
                              }}</el-dropdown-item>
                              <el-dropdown-item 
                                icon="Delete"
                                @click.stop="permanentlyDeleteDataset(item)">{{
                                $t('views.dataset.recycleBin.permanentlyDelete')
                              }}</el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </div>
                    </div>
                  </template>
                </CardBox>
              </el-col>
            </template>
          </el-row>
          <el-empty 
            v-if="recycleBinList.length === 0"
            :description="$t('views.dataset.recycleBin.emptyMessage')"
            :image-size="125"
          />
        </div>
      </div>
    </template>

    <SyncWebDialog ref="SyncWebDialogRef" @refresh="refresh" />
    <CreateDatasetDialog ref="CreateDatasetDialogRef" />
    <GenerateRelatedDialog ref="GenerateRelatedDialogRef" />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive, watch, computed, nextTick } from 'vue'
import SyncWebDialog from '@/views/dataset/component/SyncWebDialog.vue'
import CreateDatasetDialog from './component/CreateDatasetDialog.vue'
import ParagraphDialog from '@/views/paragraph/component/ParagraphDialog.vue'
import AddDatasetDialog from '@/views/application/component/AddDatasetDialog.vue'
import datasetApi from '@/api/dataset'
import { MsgSuccess, MsgConfirm } from '@/utils/message'
import { useRouter } from 'vue-router'
import { numberFormat, arraySort } from '@/utils/utils'
import { ValidType, ValidCount } from '@/enums/common'
import { t } from '@/locales'
import useStore from '@/stores'
import applicationApi from '@/api/application'
import GenerateRelatedDialog from '@/components/generate-related-dialog/index.vue'
import { cloneDeep } from 'lodash'
import emptyImg from '@/assets/hit-test-empty.png'
import { DeleteFilled } from '@element-plus/icons-vue'
import { datetimeFormat } from '@/utils/time'
const { user, common } = useStore()
const router = useRouter()

const CreateDatasetDialogRef = ref()
const SyncWebDialogRef = ref()
const loading = ref(false)
const datasetList = ref<any[]>([])
const paginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0
})
const GenerateRelatedDialogRef = ref<InstanceType<typeof GenerateRelatedDialog>>()

const searchValue = ref('')

interface UserOption {
  label: string
  value: string
}

const userOptions = ref<UserOption[]>([])
const selectUserId = ref('all')
const datasetType = ref('MY')
const sharedType = ref('ORGANIZATION')
const sortField = ref('name')
const sortOptions = [
  { label: '按名称排序', value: 'name' },
  { label: '按创建时间排序', value: 'create_time' },
  { label: '按修改时间排序', value: 'update_time' }
]

// 多知识库检索功能相关变量
const selectedDatasets = ref<string[]>([])
const availableDatasets = ref<any[]>([])
const searchLoading = ref(false)
const searchResults = ref<any[]>([])
const questionTitle = ref('')
const firstSearch = ref(true)
const inputValue = ref('')
const ParagraphDialogRef = ref()
const paragraphDialogTitle = ref('')
const quickInputRef = ref()
const popoverVisible = ref(false)
const AddDatasetDialogRef = ref()
const datasetsLoading = ref(false)

// 搜索参数
const formInline = ref({
  similarity: 0.6,
  top_number: 5,
  search_mode: 'embedding'
})
const cloneForm = ref<any>({})

// 回收站相关变量
const recycleBinSearchValue = ref('')
const recycleBinList = ref<any[]>([])
const recycleBinPaginationConfig = reactive({
  current_page: 1,
  page_size: 30,
  total: 0
})

// 计算属性
const isDisabledSearch = computed(() => !inputValue.value || selectedDatasets.value.length === 0)

function openGenerateDialog(row: any) {
  if (GenerateRelatedDialogRef.value) {
    GenerateRelatedDialogRef.value.open([], 'dataset', row.id)
  }
}

function sortDatasetList(list: any[]) {
  const field = sortField.value
  return [...list].sort((a, b) => {
    if (field === 'name') {
      return a.name.localeCompare(b.name)
    } else if (field === 'create_time') {
      return new Date(b.create_time).getTime() - new Date(a.create_time).getTime()
    } else if (field === 'update_time') {
      return new Date(b.update_time).getTime() - new Date(a.update_time).getTime()
    }
    return 0
  })
}

watch(
  [datasetType, sharedType],
  ([newDatasetType, newSharedType]) => {
    paginationConfig.total = 0
    paginationConfig.current_page = 1
    datasetList.value = []
    
    // 如果是回收站标签页，加载回收站数据
    if (newDatasetType === 'RECYCLE_BIN') {
      recycleBinPaginationConfig.total = 0
      recycleBinPaginationConfig.current_page = 1
      recycleBinList.value = []
      getRecycleBinList()
    } else {
      getList()
    }
  },
  { immediate: true }
)

function tabChangeHandle() {
  selectUserId.value = 'all'
  searchValue.value = ''
}

function sharedTabChangeHandle() {
  selectUserId.value = 'all'
  searchValue.value = ''
}

function openCreateDialog() {
  common.asyncGetValid(ValidType.Dataset, ValidCount.Dataset, loading).then(async (res: any) => {
    if (res?.data) {
      CreateDatasetDialogRef.value.open()
    } else if (res?.code === 400) {
      MsgConfirm(t('common.tip'), t('views.dataset.tip.professionalMessage'), {
        cancelButtonText: t('common.confirm'),
        confirmButtonText: t('common.professional')
      })
        .then(() => {
          window.open('https://maxkb.cn/pricing.html', '_blank')
        })
        .catch(() => {})
    }
  })
}

function refresh() {
  MsgSuccess(t('views.dataset.tip.syncSuccess'))
}

function reEmbeddingDataset(row: any) {
  datasetApi.putReEmbeddingDataset(row.id).then(() => {
    MsgSuccess(t('common.submitSuccess'))
  })
}

function syncDataset(row: any) {
  SyncWebDialogRef.value.open(row.id)
}

function searchHandle() {
  if (user.userInfo) {
    localStorage.setItem(user.userInfo.id + 'dataset', selectUserId.value)
  }
  paginationConfig.current_page = 1
  datasetList.value = []
  getList()
}
const export_dataset = (item: any) => {
  datasetApi.exportDataset(item.name, item.id, loading).then((ok) => {
    MsgSuccess(t('common.exportSuccess'))
  })
}
const export_zip_dataset = (item: any) => {
  datasetApi.exportZipDataset(item.name, item.id, loading).then((ok) => {
    MsgSuccess(t('common.exportSuccess'))
  })
}

function deleteDataset(row: any) {
  MsgConfirm(
    `${t('views.dataset.delete.confirmTitle')}${row.name} ?`,
    `${t('views.dataset.delete.confirmMessage1')} ${row.application_mapping_count} ${t('views.dataset.delete.confirmMessage2')}`,
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      datasetApi.delDataset(row.id, loading).then(() => {
        const index = datasetList.value.findIndex((v) => v.id === row.id)
        datasetList.value.splice(index, 1)
        MsgSuccess(t('common.deleteSuccess'))
      })
    })
    .catch(() => {})
}

function addToOrganization(row: any) {
  MsgConfirm(
    t('views.dataset.addToOrganization.confirmTitle'),
    t('views.dataset.addToOrganization.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'primary'
    }
  )
    .then(() => {
      datasetApi.addToOrganization(row.id, loading).then(() => {
        MsgSuccess(t('views.dataset.addToOrganization.success'))
      })
    })
    .catch(() => {})
}

function removeFromOrganization(row: any) {
  MsgConfirm(
    t('views.dataset.removeFromOrganization.confirmTitle'),
    t('views.dataset.removeFromOrganization.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      datasetApi.removeFromOrganization(row.id, loading).then(() => {
        MsgSuccess(t('views.dataset.removeFromOrganization.success'))
        paginationConfig.current_page = 1
        datasetList.value = []
        getList()
      })
    })
    .catch(() => {})
}

function getList() {
  const params = {
    ...(searchValue.value && { name: searchValue.value }),
    ...(selectUserId.value &&
      selectUserId.value !== 'all' && { select_user_id: selectUserId.value })
  }
  
  let apiPromise
  if (datasetType.value === 'SHARED' && sharedType.value === 'SHARED_TO_ME') {
    apiPromise = datasetApi.getSharedToMeDataset(paginationConfig, params, loading)
  } else if (datasetType.value === 'SHARED' && sharedType.value === 'ORGANIZATION') {
    apiPromise = datasetApi.getOrganizationDataset(paginationConfig, params, loading)
  } else {
    apiPromise = datasetApi.getDataset(paginationConfig, {
      ...params,
      type: datasetType.value,
      ...(datasetType.value === 'SHARED' && { shared_type: sharedType.value })
    }, loading)
  }

  apiPromise.then((res) => {
    res.data.records.forEach((item: any) => {
      if (datasetType.value === 'SHARED' && sharedType.value === 'SHARED_TO_ME') {
        item.username = item.username || item.creator_name
      } else  {
        if (user.userInfo && item.user_id === user.userInfo.id) {
          item.username = user.userInfo.username
        } else {
          item.username = userOptions.value.find((v) => v.value === item.user_id)?.label
        }
      }
    })
    paginationConfig.total = res.data.total
    let newRecords = sortDatasetList(res.data.records)
    
    if (datasetType.value === 'SHARED' && sharedType.value === 'SHARED_TO_ME' && user.userInfo?.id) {
      newRecords = newRecords.filter(item => item.user_id !== user.userInfo?.id)
      paginationConfig.total = datasetList.value.length + newRecords.length
    }
    
    datasetList.value = [...datasetList.value, ...newRecords]
  })
}

function getUserList() {
  applicationApi.getUserList('DATASET', loading).then((res) => {
    if (res.data) {
      userOptions.value = res.data.map((item: any) => {
        return {
          label: item.username,
          value: item.id
        }
      })
      if (user.userInfo) {
        const selectUserIdValue = localStorage.getItem(user.userInfo.id + 'dataset')
        if (selectUserIdValue && userOptions.value.find((v) => v.value === selectUserIdValue)) {
          selectUserId.value = selectUserIdValue
        }
      }
    }
  })
}

function exitDataset(row: any) {
  if (!user.userInfo?.id) return
  MsgConfirm(
    t('views.dataset.exit.confirmTitle'),
    t('views.dataset.exit.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      datasetApi.putExitShare(row.id).then(() => {
        paginationConfig.current_page = 1
        datasetList.value = []
        getList()
        MsgSuccess(t('common.exitSuccess'))
      })
    })
    .catch(() => {})
}

function editParagraph(item: any) {
  paragraphDialogTitle.value = t('views.paragraph.paragraphDetail')
  if (ParagraphDialogRef.value) {
    ParagraphDialogRef.value.open(item)
  }
}

function refreshParagraph(data: any) {
  if (data) {
    const obj = searchResults.value.filter((v) => v.id === data.id)[0]
    if (obj) {
      obj.content = data.content
      obj.title = data.title
    }
  } else {
    searchResults.value = []
    if (questionTitle.value) {
      performMultiDatasetSearch()
    }
  }
}

function settingChange(action: string) {
  if (action === 'open') {
    popoverVisible.value = true
    cloneForm.value = cloneDeep(formInline.value)
  } else if (action === 'close') {
    popoverVisible.value = false
    formInline.value = cloneDeep(cloneForm.value)
  }
}

function changeHandle(val: string) {
  if (val === 'keywords') {
    cloneForm.value.similarity = 0
  } else {
    cloneForm.value.similarity = 0.6
  }
}

function sendSearchHandle(event?: any) {
  if (event && !event?.ctrlKey && !event?.shiftKey && !event?.altKey && !event?.metaKey) {
    event.preventDefault()
    if (!isDisabledSearch.value && !searchLoading.value) {
      performMultiDatasetSearch()
    }
  } else if (event) {
    insertNewlineAtCursor(event)
  } else {
    if (!isDisabledSearch.value && !searchLoading.value) {
      performMultiDatasetSearch()
    }
  }
}

function insertNewlineAtCursor(event?: any) {
  const textarea = quickInputRef.value.$el.querySelector(
    '.el-textarea__inner'
  ) as HTMLTextAreaElement
  const startPos = textarea.selectionStart
  const endPos = textarea.selectionEnd
  event.preventDefault()
  inputValue.value = inputValue.value.slice(0, startPos) + '\n' + inputValue.value.slice(endPos)
  nextTick(() => {
    textarea.setSelectionRange(startPos + 1, startPos + 1)
  })
}

function getDatasetName(datasetId: string) {
  const dataset = availableDatasets.value.find(d => d.id === datasetId)
  return dataset ? dataset.name : '-'
}

function performMultiDatasetSearch() {
  if (selectedDatasets.value.length === 0) {
    MsgConfirm(t('views.dataset.searchDataset.noDatasetSelected'), '', {
      confirmButtonText: t('common.confirm'),
      showCancelButton: false
    })
    return
  }

  const searchParams = {
    query_text: inputValue.value,
    ...formInline.value
  }

  searchLoading.value = true
  
  // 对每个选中的数据集执行搜索，然后合并结果
  const searchPromises = selectedDatasets.value.map(datasetId => 
    datasetApi.getDatasetHitTest(datasetId, searchParams, searchLoading).then((res: any) => {
      if (res.data && Array.isArray(res.data)) {
        return res.data.map((item: any) => ({
          ...item,
          dataset_id: datasetId
        }))
      }
      return []
    }).catch(() => [])
  )

  Promise.all(searchPromises).then((results: any[][]) => {
    // 合并所有结果并按相似度排序
    const allResults = results.flat()
    searchResults.value = arraySort(allResults, 'similarity', true)
    questionTitle.value = inputValue.value
    inputValue.value = ''
    firstSearch.value = false
    searchLoading.value = false
  }).catch(() => {
    searchResults.value = []
    firstSearch.value = false
    searchLoading.value = false
  })
}

function loadAvailableDatasets() {
  datasetsLoading.value = true
  
  // 并行获取用户的知识库、共享知识库和机构知识库
  const promises = [
    // 我的知识库
    datasetApi.getDataset({ current_page: 1, page_size: 1000 }, { type: 'MY' }, datasetsLoading),
    // 共享给我的知识库
    datasetApi.getSharedToMeDataset({ current_page: 1, page_size: 1000 }, {}, datasetsLoading),
    // 机构知识库
    datasetApi.getOrganizationDataset({ current_page: 1, page_size: 1000 }, {}, datasetsLoading)
  ]
  
  Promise.all(promises).then((results: any[]) => {
    const allDatasets: any[] = []
    
    // 处理我的知识库
    if (results[0]?.data?.records) {
      results[0].data.records.forEach((item: any) => {
        allDatasets.push({
          ...item,
          is_owned: true,
          is_shared: false,
          is_organization: false,
          username: user.userInfo?.username || 'Unknown'
        })
      })
    }
    
    // 处理共享给我的知识库
    if (results[1]?.data?.records) {
      results[1].data.records.forEach((item: any) => {
        allDatasets.push({
          ...item,
          is_owned: false,
          is_shared: true,
          is_organization: false,
          username: item.username || item.creator_name || 'Unknown'
        })
      })
    }
    
    // 处理机构知识库
    if (results[2]?.data?.records) {
      results[2].data.records.forEach((item: any) => {
        allDatasets.push({
          ...item,
          is_owned: false,
          is_shared: false,
          is_organization: true,
          username: userOptions.value.find((v) => v.value === item.user_id)?.label || 'Unknown'
        })
      })
    }
    
    availableDatasets.value = allDatasets
    datasetsLoading.value = false
  }).catch(() => {
    availableDatasets.value = []
    datasetsLoading.value = false
  })
}

// 监听标签页变化，当切换到SEARCH时加载可用数据集
watch(datasetType, (newType) => {
  if (newType === 'SEARCH') {
    loadAvailableDatasets()
  }
})

function openDatasetDialog() {
  if (AddDatasetDialogRef.value) {
    AddDatasetDialogRef.value.open(selectedDatasets.value)
  }
}

function removeDataset(datasetId: string) {
  const index = selectedDatasets.value.indexOf(datasetId)
  if (index > -1) {
    selectedDatasets.value.splice(index, 1)
  }
}

function getDatasetById(datasetId: string) {
  return availableDatasets.value.find(d => d.id === datasetId)
}

function addDatasets(datasetIds: string[]) {
  selectedDatasets.value = [...datasetIds]
}

// 回收站相关函数
function getRecycleBinList() {
  const params = {
    ...(recycleBinSearchValue.value && { name: recycleBinSearchValue.value })
  }
  
  datasetApi.getRecycleBinDataset(recycleBinPaginationConfig, params, loading).then((res: any) => {
    if (res.code === 200) {
      recycleBinList.value = res.data.records || []
      recycleBinPaginationConfig.total = res.data.total || 0
    }
  })
}

function searchRecycleBinHandle() {
  recycleBinPaginationConfig.current_page = 1
  getRecycleBinList()
}

function formatDeleteTime(deleteTime: string) {
  if (!deleteTime) return ''
  const deleteDate = new Date(deleteTime)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - deleteDate.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) {
    return '1天前'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    return datetimeFormat(deleteTime)
  }
}

function restoreDataset(row: any) {
  MsgConfirm(
    t('views.dataset.restore.confirmTitle'),
    t('views.dataset.restore.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'primary'
    }
  )
    .then(() => {
      datasetApi.restoreDataset(row.id, loading).then((res: any) => {
        if (res.code === 200) {
          MsgSuccess(t('views.dataset.restore.success'))
          getRecycleBinList()
        }
      })
    })
    .catch(() => {})
}

function permanentlyDeleteDataset(row: any) {
  MsgConfirm(
    t('views.dataset.permanentlyDelete.confirmTitle'),
    t('views.dataset.permanentlyDelete.confirmMessage'),
    {
      confirmButtonText: t('common.confirm'),
      confirmButtonClass: 'danger'
    }
  )
    .then(() => {
      datasetApi.permanentlyDeleteDataset(row.id, loading).then((res: any) => {
        if (res.code === 200) {
          MsgSuccess(t('views.dataset.permanentlyDelete.success'))
          getRecycleBinList()
        }
      })
    })
    .catch(() => {})
}

onMounted(() => {
  getUserList()
})
</script>
<style lang="scss" scoped>
.dataset-list-container {
  .delete-button {
    position: absolute;
    right: 12px;
    top: 15px;
    height: auto;
  }
  .footer-content {
    .bold {
      color: var(--app-text-color);
    }
  }
  :deep(.el-divider__text) {
    background: var(--app-layout-bg-color);
  }
  
  // 权限标签样式
  :deep(.green-tag) {
    background-color: var(--el-color-success-light-9);
    border-color: var(--el-color-success-light-7);
    color: var(--el-color-success);
  }
}

// 多知识库检索功能样式
.knowledge-search-container {
  .dataset-selection-section {
    .dataset-selection-content {
      min-height: 60px;
      
      .empty-placeholder {
        display: block;
        text-align: center;
        padding: 40px 0;
        color: var(--el-text-color-placeholder);
      }
    }
    
    .relate-dataset-card {
      border: 1px solid var(--app-layout-bg-color);
      background-color: var(--app-layout-bg-color);
      
      :deep(.el-card__body) {
        padding: 12px;
      }
      
      .dataset-info {
        flex: 1;
        min-width: 0;
        
        .dataset-name {
          flex: 1;
          min-width: 0;
          display: inline-block;
          max-width: 100%;
          overflow: hidden;
          white-space: nowrap;
          text-overflow: ellipsis;
        }
      }
      
      .remove-btn {
        flex-shrink: 0;
        padding: 4px;
        margin-left: 8px;
      }
    }
  }

  .search-result__main {
    .question-title {
      .avatar {
        float: left;
      }
      .content {
        padding-left: 40px;
        .text {
          padding: 6px 0;
          height: 34px;
          box-sizing: border-box;
        }
      }
    }

    .search-result-height {
      height: calc(var(--app-main-height) - 170px);
    }

    .document-card {
      height: 230px;
      border: 1px solid var(--app-layout-bg-color);
      &:hover {
        background: #ffffff;
        border: 1px solid var(--el-border-color);
      }
      &.disabled {
        background: var(--app-layout-bg-color);
        border: 1px solid var(--app-layout-bg-color);
        :deep(.description) {
          color: var(--app-border-color-dark);
        }
        :deep(.title) {
          color: var(--app-border-color-dark);
        }
      }
      :deep(.description) {
        -webkit-line-clamp: 4 !important;
        height: 90px;
      }
      .active-button {
        position: absolute;
        right: 16px;
        top: 16px;
      }
      
      .dataset-source {
        color: var(--el-color-primary);
        font-size: 12px;
      }
    }
  }

  .search-operate {
    .operate-textarea {
      box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);
      background-color: #ffffff;
      border-radius: 8px;
      border: 1px solid #ffffff;
      box-sizing: border-box;

      &:has(.el-textarea__inner:focus) {
        border: 1px solid var(--el-color-primary);
      }

      :deep(.el-textarea__inner) {
        border-radius: 8px !important;
        box-shadow: none;
        resize: none;
        padding: 12px 16px;
      }
      .operate {
        padding: 6px 10px;
        .sent-button {
          max-height: none;
          .el-icon {
            font-size: 24px;
          }
        }
        :deep(.el-loading-spinner) {
          margin-top: -15px;
          .circular {
            width: 31px;
            height: 31px;
          }
        }
      }
    }
  }
}

// 回收站功能样式
.recycle-bin-container {
  .recycle-dataset-card {
    border: 1px solid var(--app-layout-bg-color);
    background-color: var(--app-layout-bg-color);
    border-left: 4px solid var(--el-color-danger);

    :deep(.el-card__body) {
      padding: 12px;
    }

    .delete-button {
      position: absolute;
      right: 12px;
      top: 15px;
      height: auto;
    }

    .footer-content {
      .bold {
        color: var(--app-text-color);
      }
    }
    :deep(.el-divider__text) {
      background: var(--app-layout-bg-color);
    }

    .red-tag {
      background-color: var(--el-color-danger-light-9);
      border-color: var(--el-color-danger-light-7);
      color: var(--el-color-danger);
    }
  }
}
</style>
