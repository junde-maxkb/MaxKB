<template>
  <div class="user-knowledge-container">
    <div class="knowledge-layout">
      <!-- 侧边栏 -->
      <div class="knowledge-sidebar">
        <div class="sidebar-header">
          <h3>知识库</h3>
          <el-button
              type="primary"
              size="small"
              class="create-btn"
              @click="showCreateDialog = true"
          >
            <el-icon>
              <Plus/>
            </el-icon>
            新建知识库
          </el-button>
        </div>

        <div class="sidebar-content">
          <div class="knowledge-search">
            <el-input
                v-model="searchText"
                placeholder="搜索..."
                prefix-icon="Search"
                size="small"
            />
          </div>

          <!-- 选中状态显示 -->
          <div class="selection-info" v-show="getSelectedStats().datasets > 0">
            <span class="selected-count">
              已选择: {{ getSelectedStats().datasets }}个知识库
            </span>
          </div>

          <!-- 知识库树形结构 -->
          <div class="knowledge-tree">
            <el-tree
                ref="treeRef"
                :data="treeData"
                :props="treeProps"
                node-key="id"
                :default-expand-all="false"
                :expand-on-click-node="false"
                :check-on-click-node="false"
                :show-checkbox="true"
                :check-strictly="false"
                @node-click="handleNodeClick"
                @check="handleNodeCheck"
                @node-expand="handleNodeExpand"
                class="knowledge-tree-container"
            >
              <template #default="{ node, data }">
                <div class="tree-node" :class="{ 
                  'level-1': data.level === 1, 
                  'level-2': data.level === 2, 
                  'level-3': data.level === 3,
                  'active': selectedNode?.id === data.id 
                }">
                  <!-- 一级目录 -->
                  <div v-if="data.level === 1" class="node-content level-1-content">
                    <div class="node-left">
                      <el-icon class="node-icon">
                        <component :is="data.icon"/>
                      </el-icon>
                      <span class="node-label" :title="data.label">{{ data.label }}</span>
                    </div>
                    <el-dropdown
                        trigger="click"
                        @command="handleLevel1Action"
                        @click.stop
                    >
                      <el-icon class="more-actions">
                        <MoreFilled/>
                      </el-icon>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <!-- 个人知识库菜单 -->
                          <template v-if="data.type === 'personal'">
                            <el-dropdown-item :command="{ action: 'refresh', data }">
                              <el-icon>
                                <Refresh/>
                              </el-icon>
                              刷新
                            </el-dropdown-item>
                            <el-dropdown-item divided>
                              <span style="color: #909399; font-size: 12px;">排序方式</span>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'sort-by-time', data }">
                              <el-icon>
                                <Timer/>
                              </el-icon>
                              按时间排序
                              <el-icon v-if="personalKBSortType === 'time'" style="margin-left: auto; color: #409eff;">
                                <Check/>
                              </el-icon>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'sort-by-name', data }">
                              <el-icon>
                                <Sort/>
                              </el-icon>
                              按名称排序
                              <el-icon v-if="personalKBSortType === 'name'" style="margin-left: auto; color: #409eff;">
                                <Check/>
                              </el-icon>
                            </el-dropdown-item>
                          </template>

                          <!-- 机构知识库菜单 - 只有排序功能 -->
                          <template v-else-if="data.type === 'organization'">
                            <el-dropdown-item :command="{ action: 'refresh', data }">
                              <el-icon>
                                <Refresh/>
                              </el-icon>
                              刷新
                            </el-dropdown-item>
                            <el-dropdown-item divided>
                              <span style="color: #909399; font-size: 12px;">排序方式</span>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'org-sort-by-name', data }">
                              <el-icon>
                                <Sort/>
                              </el-icon>
                              按名称排序
                              <el-icon v-if="organizationKBSortType === 'name'"
                                       style="margin-left: auto; color: #409eff;">
                                <Check/>
                              </el-icon>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'org-sort-by-time', data }">
                              <el-icon>
                                <Timer/>
                              </el-icon>
                              按创建时间排序
                              <el-icon v-if="organizationKBSortType === 'time'"
                                       style="margin-left: auto; color: #409eff;">
                                <Check/>
                              </el-icon>
                            </el-dropdown-item>
                          </template>

                          <!-- 共享知识库菜单 -->
                          <template v-else-if="data.type === 'shared'">
                            <el-dropdown-item :command="{ action: 'refresh', data }">
                              <el-icon>
                                <Refresh/>
                              </el-icon>
                              刷新
                            </el-dropdown-item>
                            <el-dropdown-item divided>
                              <span style="color: #909399; font-size: 12px;">排序方式</span>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'shared-sort-by-name', data }">
                              <el-icon>
                                <Sort/>
                              </el-icon>
                              按名称排序
                              <el-icon v-if="sharedKBSortType === 'name'" style="margin-left: auto; color: #409eff;">
                                <Check/>
                              </el-icon>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'shared-sort-by-time', data }">
                              <el-icon>
                                <Timer/>
                              </el-icon>
                              按创建时间排序
                              <el-icon v-if="sharedKBSortType === 'time'" style="margin-left: auto; color: #409eff;">
                                <Check/>
                              </el-icon>
                            </el-dropdown-item>
                          </template>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>

                  <!-- 二级目录 - 知识库 -->
                  <div v-else-if="data.level === 2" class="node-content level-2-content">
                    <div class="node-left">
                      <el-icon class="node-icon">
                        <Folder/>
                      </el-icon>
                      <span class="node-label" :title="data.label">{{ data.label }}</span>
                      <span class="doc-count">({{ data.documentCount || 0 }})</span>
                    </div>

                    <!-- 知识库操作按钮 -->
                    <el-dropdown
                        trigger="click"
                        @command="handleKBAction"
                        @click.stop
                    >
                      <el-icon class="more-actions">
                        <MoreFilled/>
                      </el-icon>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <!-- 我的知识库 - 完整操作权限 -->
                          <template v-if="getKBType(data) === 'personal'">
                            <el-dropdown-item :command="{ action: 'view', data }">
                              <el-icon>
                                <View/>
                              </el-icon>
                              查看详情
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'rename', data }">
                              <el-icon>
                                <EditPen/>
                              </el-icon>
                              重命名
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'share', data }" @click.stop>
                              <el-icon>
                                <Share/>
                              </el-icon>
                              共享设置
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'delete', data }" divided>
                              <el-icon>
                                <Delete/>
                              </el-icon>
                              删除
                            </el-dropdown-item>
                          </template>

                          <!-- 共享知识库 - 辅助管理可以查看详情 -->
                          <template v-if="getKBType(data) === 'shared'">
                            <template
                                v-if="data.permission === 'MANAGE' || (data.shared_with_type === 'TEAM' && data.team_permission === 'MANAGE')">
                              <el-dropdown-item :command="{ action: 'view', data }">
                                <el-icon>
                                  <View/>
                                </el-icon>
                                查看详情
                              </el-dropdown-item>
                              <el-dropdown-item divided :command="{ action: 'exit-share', data }">
                                <el-icon>
                                  <Close/>
                                </el-icon>
                                退出共享
                              </el-dropdown-item>
                            </template>
                            <template v-else>
                              <el-dropdown-item :command="{ action: 'exit-share', data }">
                                <el-icon>
                                  <Close/>
                                </el-icon>
                                退出共享
                              </el-dropdown-item>
                            </template>
                          </template>

                          <!-- 机构知识库 - 管理员权限 -->
                          <template v-if="getKBType(data) === 'organization'">
                            <template v-if="isAdmin">
                              <el-dropdown-item :command="{ action: 'edit', data }">
                                <el-icon>
                                  <Edit/>
                                </el-icon>
                                编辑
                              </el-dropdown-item>
                              <el-dropdown-item :command="{ action: 'remove-from-org', data }">
                                <el-icon>
                                  <FolderRemove/>
                                </el-icon>
                                移出机构
                              </el-dropdown-item>
                            </template>
                            <template v-else>
                              <el-dropdown-item disabled>
                                <span style="color: #c0c4cc;">无可用操作</span>
                              </el-dropdown-item>
                            </template>
                          </template>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>

                  <!-- 三级目录 - 文档 -->
                  <div v-else-if="data.level === 3" class="node-content level-3-content">
                    <el-icon class="node-icon">
                      <DocumentCopy/>
                    </el-icon>
                    <span class="node-label" :title="data.label">{{ data.label }}</span>
                    <span class="file-size">{{ formatFileSize(data.size) }}</span>
                  </div>
                </div>
              </template>
            </el-tree>
          </div>
        </div>
      </div>

      <!-- 主内容区域 -->
      <div class="knowledge-main">
        <div class="chat-content">
          <!-- 服务状态提示 -->
          <div v-if="showServiceWarning" class="service-warning">
            <el-alert
                :title="serviceWarningMessage"
                type="warning"
                :closable="true"
                @close="showServiceWarning = false"
                show-icon
            >
              <template #default>
                <p>这可能会影响问答的准确性。如问题持续，请联系管理员。</p>
              </template>
            </el-alert>
          </div>

          <div class="chat-area" :class="{ 'has-messages': hasMessages }">

            <!-- 对话消息区域 -->
            <div class="chat-messages" ref="messagesContainer" v-if="hasMessages">

              <div
                  v-for="(message, index) in chatMessages"
                  :key="index"
                  class="message"
                  :class="{ 'user-message': message.role === 'user', 'ai-message': message.role === 'assistant' }"
              >
                <div class="message-content">
                  <div class="message-text" v-html="formatMessageContent(message.content)"></div>

                  <!-- 显示匹配的分段（仅AI回答且有分段信息时显示） -->
                  <div v-if="message.role === 'assistant' && message.paragraphs && message.paragraphs.length > 0"
                       class="matched-paragraphs">
                    <div class="paragraphs-header">
                      <el-button
                          type="text"
                          size="small"
                          @click="toggleParagraphsVisibility(index)"
                          class="toggle-paragraphs-btn"
                      >
                        <el-icon>
                          <Document/>
                        </el-icon>
                        找到 {{ message.paragraphs.length }} 个相关分段
                        <el-icon :class="{ 'rotate': isParagraphsExpanded(index) }">
                          <ArrowDown/>
                        </el-icon>
                      </el-button>
                    </div>

                    <div v-show="isParagraphsExpanded(index)" class="paragraphs-list">
                      <div
                          v-for="(paragraph, pIndex) in message.paragraphs.slice(0, 5)"
                          :key="pIndex"
                          class="paragraph-item"
                      >
                        <div class="paragraph-header">
                          <span class="paragraph-index">{{ pIndex + 1 }}</span>
                          <span class="paragraph-score">
                            相关度: {{
                              ((paragraph.similarity || paragraph.comprehensive_score || 0) * 100).toFixed(1)
                            }}%
                          </span>
                        </div>
                        <div class="paragraph-content">{{ paragraph.content }}</div>
                        <div class="paragraph-meta">
                          <span
                            class="paragraph-source clickable"
                            @click="openDocumentParagraphs(paragraph)"
                            :title="`点击查看 ${paragraph.document_name || paragraph.source || paragraph.dataset_name} 的分段内容`"
                          >
                            来源: {{ paragraph.document_name || paragraph.source || paragraph.dataset_name }}
                          </span>
                          <span class="paragraph-dataset">数据集: {{ paragraph.dataset_name }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                </div>
              </div>

              <!-- 流式输出显示 -->
              <div v-if="isStreaming" class="message ai-message streaming">
                <div class="message-content">
                  <div class="message-text">
                    <span class="loading-text">AI正在思考</span>
                    <span class="loading-dots">
                      <span class="dot">.</span>
                      <span class="dot">.</span>
                      <span class="dot">.</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 集成聊天输入组件 -->
            <div class="integrated-chat-input" :class="{ 'centered': !hasMessages, 'bottom': hasMessages }">
              <!-- 知识库信息提示 -->
              <div class="kb-info-container" :class="{ 'moved-down': hasMessages }">
                <div class="kb-info-content">
                  <div class="kb-info-text" v-if="getSelectedStats().datasets > 0">
                    基于 {{ getSelectedStats().datasets }} 个知识库：
                  </div>
                  <div class="kb-info-text" v-else>
                    请从左侧选择知识库开始问答
                  </div>
                  <div v-if="getSelectedStats().datasets > 0" class="selected-datasets">
                    <el-tag
                        v-for="dataset in getSelectedDatasets().slice(0, 4)"
                        :key="dataset.id"
                        size="small"
                        class="dataset-tag"
                    >
                      {{ dataset.label }}
                    </el-tag>
                    <el-tag
                        v-if="getSelectedDatasets().length > 4"
                        size="small"
                        class="dataset-tag more-tag"
                    >
                      +{{ getSelectedDatasets().length - 4 }}
                    </el-tag>
                  </div>
                </div>
              </div>

              <!-- 模型选择器 -->
              <div class="model-selector" v-show="false">
                <div class="model-selector-label">
                  <el-icon>
                    <Setting/>
                  </el-icon>
                  <span>对话模型</span>
                </div>
                <el-select
                    v-model="selectedModelId"
                    placeholder="选择对话模型"
                    @change="handleModelChange"
                    class="model-select"
                    :loading="modelsLoading"
                    filterable
                >
                  <el-option
                      v-for="model in availableModels"
                      :key="model.id"
                      :label="model.name"
                      :value="model.id"
                  >
                    <div class="model-option">
                      <div class="model-info">
                        <span class="model-name">{{ model.name }}</span>
                        <el-tag size="small" :type="getModelTypeColor(model.model_type)">
                          {{ model.model_type }}
                        </el-tag>
                      </div>
                      <div class="model-provider">{{ model.provider }}</div>
                    </div>
                  </el-option>
                </el-select>
              </div>

<!--              &lt;!&ndash; STT设置面板 &ndash;&gt;-->
<!--              <div class="stt-settings" v-if="sttModelEnabled">-->
<!--                <div class="stt-settings-header">-->
<!--                  <el-icon>-->
<!--                    <Microphone />-->
<!--                  </el-icon>-->
<!--                  <span>语音设置</span>-->
<!--                </div>-->
<!--                <div class="stt-settings-content">-->
<!--                  <el-checkbox v-model="sttAutoSend" size="small">-->
<!--                    自动发送语音转换结果-->
<!--                  </el-checkbox>-->
<!--                </div>-->
<!--              </div>-->

<!--              &lt;!&ndash; STT不可用提示 &ndash;&gt;-->
<!--              <div class="stt-disabled-tip" v-else-if="getSelectedStats().datasets > 0">-->
<!--                <el-icon>-->
<!--                  <Microphone />-->
<!--                </el-icon>-->
<!--                <span>语音功能不可用，请检查STT模型配置</span>-->
<!--              </div>-->

              <!-- 输入区域 -->
              <div class="input-container">
                <div class="input-wrapper">
                  <div class="input-content">
                    <el-input
                        v-model="currentMessage"
                        type="textarea"
                        :autosize="{ minRows: 1, maxRows: 3 }"
                        :placeholder="getInputPlaceholder()"
                        class="chat-input"
                        @keyup.enter.exact.prevent="sendMessage"
                        @focus="handleInputFocus"
                        :disabled="isStreaming || getSelectedStats().datasets === 0"
                    />

                    <!-- 语音录制按钮 -->
                    <el-button
                        text
                        class="voice-btn"
                        @click="startRecording"
                        v-if="recorderStatus === 'STOP'"
                        :disabled="isStreaming || getSelectedStats().datasets === 0 || !sttModelEnabled"
                    >
                      <el-icon>
                        <Microphone />
                      </el-icon>
                    </el-button>

                    <!-- 音频文件上传按钮 -->
                    <el-upload
                        ref="audioUploadRef"
                        class="audio-upload-btn"
                        :show-file-list="false"
                        :before-upload="handleAudioUpload"
                        :disabled="isStreaming || getSelectedStats().datasets === 0 || !sttModelEnabled || isUploadingAudio"
                        accept="audio/*"
                        v-if="recorderStatus === 'STOP'"
                    >
                        <el-button
                            text
                            class="voice-btn"
                            :disabled="isStreaming || getSelectedStats().datasets === 0 || !sttModelEnabled || isUploadingAudio"
                            :loading="isUploadingAudio"
                        >
                          <el-icon v-if="!isUploadingAudio">
                            <UploadFilled />
                          </el-icon>
                        </el-button>
                    </el-upload>

                    <!-- 录音状态显示 -->
                    <div v-else class="voice-recording flex align-center">
                      <el-text type="info" class="recording-time">
                        00:{{ recorderTime < 10 ? `0${recorderTime}` : recorderTime }}
                      </el-text>
                      <el-button
                          text
                          type="primary"
                          @click="stopRecording"
                          :loading="recorderStatus === 'TRANSCRIBING'"
                          class="stop-btn"
                      >
                        <el-icon v-if="recorderStatus !== 'TRANSCRIBING'">
                          <i class="stop-icon">⏹</i>
                        </el-icon>
                      </el-button>
                    </div>

                    <el-button
                        type="primary"
                        class="send-btn"
                        @click="sendMessage"
                        :loading="isStreaming"
                        :disabled="!currentMessage.trim() || isStreaming || getSelectedStats().datasets === 0"
                    >
                      {{ isStreaming ? '发送中...' : '发送' }}
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建知识库对话框 -->
    <el-dialog
        v-model="showCreateDialog"
        title="创建知识库"
        width="500px"
    >
      <el-form :model="newKB" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="newKB.name" placeholder="请输入知识库名称"/>
        </el-form-item>
        <!-- 描述字段隐藏，将在提交时自动使用标题作为描述 -->
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createKnowledgeBase">确认</el-button>
      </template>
    </el-dialog>

    <!-- 文档管理弹窗 -->
    <el-dialog
        v-model="showDocumentModal"
        :title="`文档管理 - ${currentDatasetName}`"
        width="90%"
        top="5vh"
        :close-on-click-modal="false"
        class="document-modal"
    >
      <DocumentManagement
          v-if="showDocumentModal"
          :dataset-id="currentDatasetId"
          :dataset-name="currentDatasetName"
          @close="showDocumentModal = false"
          @document-changed="handleDocumentChanged"
      />
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showDocumentModal = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 共享设置弹窗 -->
    <el-dialog
        v-model="showShareModal"
        :title="`共享设置 - ${currentDatasetName}`"
        width="80%"
        top="8vh"
        :close-on-click-modal="false"
        class="share-modal"
    >
      <ShareSettings
          v-if="showShareModal"
          :dataset-id="currentDatasetId"
          :dataset-name="currentDatasetName"
          @close="showShareModal = false"
      />
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showShareModal = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 文档分段详情弹窗 -->
    <DocumentParagraphsDialog
        v-model="showParagraphsDialog"
        :document-id="currentDocumentId"
        :dataset-id="currentParagraphDatasetId"
        :document-name="currentDocumentName"
        :hit-paragraph-id="currentHitParagraphId"
        :hit-paragraph-content="currentHitParagraphContent"
    />

    <!-- 重命名知识库对话框 -->
    <el-dialog
        v-model="showRenameDialog"
        title="重命名知识库"
        width="550px"
        :before-close="() => showRenameDialog = false"
        class="rename-dialog"
    >
      <el-form :model="renameForm" label-width="100px">
        <el-form-item label="知识库名称" required>
          <el-input
              v-model="renameForm.name"
              placeholder="请输入新的知识库名称"
              maxlength="50"
              show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showRenameDialog = false">取消</el-button>
          <el-button
              type="primary"
              @click="confirmRename"
              :disabled="!renameForm.name.trim()"
          >
            确认重命名
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {ref, computed, onMounted, onUnmounted, nextTick} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import useStore from '@/stores'
import {
  Plus,
  Search,
  Document,
  DocumentDelete,
  ChatDotSquare,
  DocumentCopy,
  MoreFilled,
  ArrowDown,
  Refresh,
  OfficeBuilding,
  Share,
  User,
  Setting,
  Edit,
  EditPen,
  Delete,
  View,
  Close,
  FolderRemove,
  Folder,
  Timer,
  Sort,
  Check,
  Upload,
  UploadFilled,
  Download,
  Collection,
  Clock,
  Switch,
  Microphone
} from '@element-plus/icons-vue'
import datasetApi from '@/api/dataset'
import documentApi from '@/api/document'
import modelApi, {postModelChatStream} from '@/api/model'
import applicationApi from '@/api/application'
import DocumentManagement from './components/DocumentManagement.vue'
import ShareSettings from './components/ShareSettings.vue'
import DocumentParagraphsDialog from './components/DocumentParagraphsDialog.vue'
import Recorder from 'recorder-core'
import 'recorder-core/src/engine/mp3'
import 'recorder-core/src/engine/mp3-engine'
import { MsgAlert, MsgWarning } from '@/utils/message'

// 类型定义
interface TreeNode {
  id: string
  label: string
  level: number
  type: string
  icon?: string
  checked?: boolean
  children?: TreeNode[]
  permission?: string
  shared_with_type?: string
  team_permission?: string
  datasetId?: string
  documentId?: string
  description?: string
  documentCount?: number
  size?: number
  status?: string
}

interface Message {
  role: string  // 'user' | 'assistant' | 'system'
  content: string
  timestamp?: Date
  paragraphs?: Array<{
    title?: string
    content: string
    source: string
    dataset_name: string
    similarity?: number
    comprehensive_score?: number
    document_id?: string
    dataset_id?: string
    document_name?: string
  }>
}

interface KBForm {
  name: string
  description?: string  // 描述字段改为可选
  type?: string
}


// 响应式数据
const searchText = ref('')
const selectedKB = ref<TreeNode | null>(null)
const selectedNode = ref<TreeNode | null>(null)
const currentMessage = ref('')
const isLoading = ref(false)
const showCreateDialog = ref(false)
const showDocumentModal = ref(false)
const showShareModal = ref(false)
const showParagraphsDialog = ref(false)
const currentDatasetId = ref('')
const currentDatasetName = ref('')
const currentDocumentId = ref('')
const currentParagraphDatasetId = ref('')
const currentDocumentName = ref('')
const currentHitParagraphId = ref('')
const currentHitParagraphContent = ref('')

// 重命名相关状态
const showRenameDialog = ref(false)
const renameForm = ref({
  id: '',
  name: ''
})
const messagesContainer = ref<HTMLElement | null>(null)
const treeRef = ref<any>(null)

// 新建知识库表单
const newKB = ref<KBForm>({
  name: ''
  // description 字段隐藏，将在创建时自动使用 name 的值
})

// 树形组件配置
const treeProps = {
  children: 'children',
  label: 'label'
}

// 树形数据
const treeData = ref<TreeNode[]>([
  {
    id: 'org',
    label: '机构知识库',
    level: 1,
    type: 'organization',
    icon: 'OfficeBuilding',
    checked: false,
    children: []
  },
  {
    id: 'shared',
    label: '共享知识库',
    level: 1,
    type: 'shared',
    icon: 'Share',
    checked: false,
    children: []
  },
  {
    id: 'my',
    label: '我的知识库',
    level: 1,
    type: 'personal',
    icon: 'User',
    checked: false,
    children: []
  }
])

// 对话消息列表
const chatMessages = ref<Message[]>([])
// 流式输出状态
const isStreaming = ref(false)
// 服务状态警告
const showServiceWarning = ref(false)
const serviceWarningMessage = ref('')
// 模型选择相关
const selectedModelId = ref('')
const availableModels = ref<any[]>([])
const modelsLoading = ref(false)

// 分段展开状态管理
const expandedParagraphs = ref<Set<number>>(new Set())

// 语音录制相关状态
const intervalId = ref<any | null>(null)
const recorderTime = ref(0)
const recorderStatus = ref<'START' | 'TRANSCRIBING' | 'STOP'>('STOP')

// 音频文件上传相关状态
const audioUploadRef = ref()
const isUploadingAudio = ref(false)

// STT相关状态
const sttModelEnabled = ref(false)
const sttAutoSend = ref(false)
const availableSTTModels = ref<any[]>([])
const selectedSTTModelId = ref('')
// 不再需要临时应用ID

// 用户权限
const {user} = useStore()
const userRole = computed(() => user.getRole())
const isAdmin = computed(() => userRole.value === 'ADMIN')

// 原有的知识库数据存储
const organizationKBs = ref<any[]>([])
const sharedKBs = ref<any[]>([])
const personalKBs = ref<any[]>([])

// 排序相关
const personalKBSortType = ref<'time' | 'name'>('time') // 默认按时间排序（创建时间倒排）
const organizationKBSortType = ref<'time' | 'name'>('time') // 机构知识库排序类型
const sharedKBSortType = ref<'time' | 'name'>('time') // 共享知识库排序类型

// 计算属性
computed(() => {
  // 这里可以根据搜索文本过滤树形数据
  return treeData.value
});
// 判断是否有聊天消息
const hasMessages = computed(() => {
  return chatMessages.value.length > 0
})

// 解析默认模型ID（优先选择对话模型）
const resolveDefaultModelId = async (): Promise<string> => {
  const cached = localStorage.getItem('user_knowledge_default_model_id')

  // 如果有缓存，先验证模型是否仍然存在且支持对话
  if (cached) {
    try {
      const res = await modelApi.getModel()
      const list = res.data || []
      const cachedModel = list.find(model => model.id === cached)

      // 验证缓存的模型是否仍存在且支持对话
      if (cachedModel && isChatModel(cachedModel)) {
        return cached
      } else {
        // 缓存的模型不存在或不支持对话，清除缓存
        localStorage.removeItem('user_knowledge_default_model_id')
      }
    } catch (e) {
      console.warn('验证缓存模型失败:', e)
    }
  }

  // 获取新的对话模型
  try {
    const res = await modelApi.getModel()
    const list = res.data || []

    // 优先选择支持对话的模型
    const chatModels = list.filter(model => isChatModel(model))

    if (chatModels.length > 0) {
      const selectedModel = chatModels[0]
      localStorage.setItem('user_knowledge_default_model_id', selectedModel.id)
      return selectedModel.id
    } else {
      console.warn('未找到支持对话的模型')
    }
  } catch (e) {
    console.warn('获取默认模型失败', e)
  }
  return ''
}

// 判断模型是否支持对话
const isChatModel = (model: any): boolean => {
  // 检查模型类型是否为对话类型
  const chatTypes = ['LLM', 'CHAT', 'LLM_CHAT']
  const isCorrectType = chatTypes.includes(model.model_type?.toUpperCase())

  // 检查模型状态是否正常
  const isStatusOk = model.status === 'SUCCESS'

  // 检查是否为嵌入模型（排除）
  const embeddingTypes = ['EMBEDDING', 'EMBED']
  const isNotEmbedding = !embeddingTypes.includes(model.model_type?.toUpperCase())

  const result = isCorrectType && isStatusOk && isNotEmbedding


  return result
}

// 加载可用的对话模型列表
const loadAvailableModels = async () => {
  modelsLoading.value = true
  try {
    const res = await modelApi.getModel()
    const list = res.data || []
    
    console.log("模型列表：",res)
    // 过滤出支持对话的模型
    availableModels.value = list.filter(model => isChatModel(model))


    // 如果当前没有选择模型，自动选择第一个
    if (!selectedModelId.value && availableModels.value.length > 0) {
      selectedModelId.value = availableModels.value[0].id
      // 更新缓存
      localStorage.setItem('user_knowledge_default_model_id', selectedModelId.value)
    }

    // 如果当前选择的模型不在可用列表中，重新选择
    if (selectedModelId.value && !availableModels.value.find(m => m.id === selectedModelId.value)) {
      selectedModelId.value = availableModels.value.length > 0 ? availableModels.value[0].id : ''
      if (selectedModelId.value) {
        localStorage.setItem('user_knowledge_default_model_id', selectedModelId.value)
      }
    }
  } catch (error) {
    console.error('加载模型列表失败:', error)
    ElMessage.error('加载模型列表失败')
  } finally {
    modelsLoading.value = false
  }
}

// 加载可用的STT模型列表
const loadAvailableSTTModels = async () => {
  try {
    // 从全局模型列表中过滤出STT模型
    const res = await modelApi.getModel()
    const list = res.data || []
    
    // 过滤出STT类型的模型
    const sttModels = list.filter(model => model.model_type === 'STT')
    
    if (sttModels.length > 0) {
      availableSTTModels.value = sttModels
      sttModelEnabled.value = true

      // 自动选择第一个STT模型
      if (!selectedSTTModelId.value) {
        selectedSTTModelId.value = sttModels[0].id
      }
    } else {
      sttModelEnabled.value = false
    }
  } catch (error) {
    console.error('加载STT模型失败:', error)
    sttModelEnabled.value = false
  }
}

// 不再需要创建临时应用，直接使用STT模型API

// 处理模型切换
const handleModelChange = (modelId: string) => {
  selectedModelId.value = modelId
  // 更新缓存
  localStorage.setItem('user_knowledge_default_model_id', modelId)

  const selectedModel = availableModels.value.find(m => m.id === modelId)
  if (selectedModel) {
    ElMessage.success(`已切换到模型: ${selectedModel.name}`)
  }
}

// 处理输入框获得焦点
const handleInputFocus = () => {
  // 当输入框获得焦点时，如果还没有消息，可以触发动画
  // 这里可以添加额外的逻辑，比如自动滚动等
}

// 获取输入框占位符文本
const getInputPlaceholder = () => {
  if (getSelectedStats().datasets === 0) {
    return '请先选择知识库...'
  }
  return '请输入您的问题...'
}

// 获取模型类型对应的标签颜色
const getModelTypeColor = (modelType: string) => {
  const typeMap: Record<string, string> = {
    'LLM': 'primary',
    'CHAT': 'success',
    'LLM_CHAT': 'warning'
  }
  return typeMap[modelType?.toUpperCase()] || 'info'
}

// 分段展开/收起功能
const toggleParagraphsVisibility = (messageIndex: number) => {
  if (expandedParagraphs.value.has(messageIndex)) {
    expandedParagraphs.value.delete(messageIndex)
  } else {
    expandedParagraphs.value.add(messageIndex)
  }
}

const isParagraphsExpanded = (messageIndex: number) => {
  return expandedParagraphs.value.has(messageIndex)
}

// 创建AI消息的辅助函数
const createAssistantMessage = (content: string, paragraphs?: any[]) => {
  return {
    role: 'assistant',
    content,
    timestamp: new Date(),
    paragraphs: paragraphs || undefined
  }
}

// 方法
const selectKnowledgeBase = (kb: TreeNode) => {
  selectedKB.value = kb
  // 清空之前的对话
  // chatMessages.value = [] // 临时注释，测试消息保持
}

// 打开文档分段详情
const openDocumentParagraphs = async (paragraph: any) => {
  console.log('点击的分段数据:', paragraph)
  console.log('document_id:', paragraph.document_id)
  console.log('dataset_id:', paragraph.dataset_id)
  console.log('paragraph.id:', paragraph.id)
  console.log('paragraph的所有属性:', Object.keys(paragraph))
  console.log('paragraph的完整内容:', JSON.stringify(paragraph, null, 2))

  if (!paragraph.document_id || !paragraph.dataset_id) {
    console.error('缺少必要字段:', {
      document_id: paragraph.document_id,
      dataset_id: paragraph.dataset_id,
      paragraph: paragraph
    })
    ElMessage.warning('无法获取文档信息')
    return
  }

  currentDocumentId.value = paragraph.document_id
  currentParagraphDatasetId.value = paragraph.dataset_id
  currentDocumentName.value = paragraph.document_name || paragraph.source || paragraph.dataset_name
  
  // 由于搜索结果中没有分段ID，我们需要通过内容匹配来找到对应的分段
  // 传递搜索结果的完整内容，用于在分段详情中匹配
  currentHitParagraphId.value = paragraph.title || '段落 1' // 使用title作为临时标识
  currentHitParagraphContent.value = paragraph.content // 保存搜索结果的完整内容
  console.log('设置命中分段标识:', currentHitParagraphId.value)
  console.log('设置命中分段内容:', currentHitParagraphContent.value.substring(0, 100) + '...')
  showParagraphsDialog.value = true
}

// 处理树节点点击
const handleNodeClick = (data: TreeNode) => {
  selectedNode.value = data

  if (data.level === 2) {
    // 点击知识库，切换到该知识库
    selectKnowledgeBase(data)
  } else if (data.level === 3) {
    // 点击文档，显示文档详情
    showDocumentDetail(data)
  }
}

// 处理节点展开
const handleNodeExpand = async (data: TreeNode) => {

  // 如果是二级节点（知识库）且还没有加载文档，则加载文档
  if (data.level === 2 && data.datasetId && (!data.children || data.children.length === 0)) {
    await loadDocuments(data.datasetId, data.id)
  }
}

// 处理复选框选择
const handleNodeCheck = (data: TreeNode, checkInfo: any) => {
  // 获取所有选中的节点
  const checkedNodes = treeRef.value?.getCheckedNodes() || []
  const checkedKeys = treeRef.value?.getCheckedKeys() || []

  // 分类统计选中的项目
  const selectedStats = getSelectedStats()
}

// 获取选中项目的统计信息
const getSelectedStats = () => {
  const checkedNodes = treeRef.value?.getCheckedNodes() || []

  const stats = {
    categories: 0,      // 一级目录数量
    datasets: 0,        // 知识库数量  
    documents: 0,       // 文档数量
    selectedNodes: checkedNodes
  }

  checkedNodes.forEach((node: TreeNode) => {
    switch (node.level) {
      case 1:
        stats.categories++
        break
      case 2:
        stats.datasets++
        break
      case 3:
        stats.documents++
        break
    }
  })

  return stats
}

// 获取选中的知识库列表
const getSelectedDatasets = (): TreeNode[] => {
  const checkedNodes = treeRef.value?.getCheckedNodes() || []
  return checkedNodes.filter((node: TreeNode) => node.level === 2)
}

// 获取选中的文档列表
const getSelectedDocuments = (): TreeNode[] => {
  const checkedNodes = treeRef.value?.getCheckedNodes() || []
  return checkedNodes.filter((node: TreeNode) => node.level === 3)
}


// 处理一级目录的三个点菜单操作
const handleLevel1Action = (command: { action: string; data: TreeNode }) => {
  const {action, data} = command

  switch (action) {
    case 'refresh':
      console.log('刷新', data.label)
      refreshKnowledgeBase(data.type)
      break
      // 个人知识库排序
    case 'sort-by-time':
      console.log('个人知识库按时间排序')
      personalKBSortType.value = 'time'
      localStorage.setItem('personal_kb_sort_type', 'time')
      sortPersonalKBs()
      ElMessage.success('已切换为按时间排序（创建时间倒序）')
      break
    case 'sort-by-name':
      console.log('个人知识库按名称排序')
      personalKBSortType.value = 'name'
      localStorage.setItem('personal_kb_sort_type', 'name')
      sortPersonalKBs()
      ElMessage.success('已切换为按名称排序（A-Z）')
      break
      // 机构知识库排序
    case 'org-sort-by-name':
      console.log('机构知识库按名称排序')
      organizationKBSortType.value = 'name'
      localStorage.setItem('organization_kb_sort_type', 'name')
      sortOrganizationKBs()
      ElMessage.success('机构知识库已切换为按名称排序（A-Z）')
      break
    case 'org-sort-by-time':
      console.log('机构知识库按创建时间排序')
      organizationKBSortType.value = 'time'
      localStorage.setItem('organization_kb_sort_type', 'time')
      sortOrganizationKBs()
      ElMessage.success('机构知识库已切换为按创建时间排序（最新在前）')
      break
      // 共享知识库排序
    case 'shared-sort-by-name':
      console.log('共享知识库按名称排序')
      sharedKBSortType.value = 'name'
      localStorage.setItem('shared_kb_sort_type', 'name')
      sortSharedKBs()
      ElMessage.success('共享知识库已切换为按名称排序（A-Z）')
      break
    case 'shared-sort-by-time':
      console.log('共享知识库按创建时间排序')
      sharedKBSortType.value = 'time'
      localStorage.setItem('shared_kb_sort_type', 'time')
      sortSharedKBs()
      ElMessage.success('共享知识库已切换为按创建时间排序（最新在前）')
      break
  }
}

// 获取知识库类型
const getKBType = (data: TreeNode): string => {
  // 通过父节点或ID前缀确定知识库类型
  if (data.id.includes('org_')) return 'organization'
  if (data.id.includes('shared_')) return 'shared'
  if (data.id.includes('my_')) return 'personal'

  // 备用判断：通过TreeRef查找父节点
  const allNodes = treeRef.value?.store?.nodesMap
  if (allNodes && data.id) {
    const currentNode = allNodes[data.id]
    if (currentNode?.parent?.data?.type) {
      return currentNode.parent.data.type
    }
  }

  return 'personal' // 默认值
}

// 排序个人知识库
const sortPersonalKBs = async () => {
  try {
    if (personalKBs.value.length === 0) return

    // 复制数组进行排序
    let sortedKBs = [...personalKBs.value]

    if (personalKBSortType.value === 'time') {
      // 按创建时间倒序排列（最新的在前面）
      sortedKBs.sort((a, b) => {
        const timeA = new Date(a.create_time || a.created_at || '').getTime()
        const timeB = new Date(b.create_time || b.created_at || '').getTime()
        return timeB - timeA // 倒序
      })
    } else if (personalKBSortType.value === 'name') {
      // 按名称正序排列（A-Z）
      sortedKBs.sort((a, b) => {
        return (a.name || '').localeCompare(b.name || '', 'zh-CN', {
          numeric: true,
          sensitivity: 'base'
        })
      })
    }

    // 更新排序后的数据
    personalKBs.value = sortedKBs
    await updateTreeData('my', sortedKBs)

    console.log(`个人知识库已按${personalKBSortType.value === 'time' ? '时间' : '名称'}排序`)
  } catch (error) {
    console.error('排序失败:', error)
  }
}

// 排序机构知识库
const sortOrganizationKBs = async () => {
  try {
    if (organizationKBs.value.length === 0) return

    // 复制数组进行排序
    let sortedKBs = [...organizationKBs.value]

    if (organizationKBSortType.value === 'time') {
      // 按创建时间倒序排列（最新的在前面）
      sortedKBs.sort((a, b) => {
        const timeA = new Date(a.create_time || a.created_at || '').getTime()
        const timeB = new Date(b.create_time || b.created_at || '').getTime()
        return timeB - timeA // 倒序
      })
    } else if (organizationKBSortType.value === 'name') {
      // 按名称正序排列（A-Z）
      sortedKBs.sort((a, b) => {
        return (a.name || '').localeCompare(b.name || '', 'zh-CN', {
          numeric: true,
          sensitivity: 'base'
        })
      })
    }

    // 更新排序后的数据
    organizationKBs.value = sortedKBs
    await updateTreeData('org', sortedKBs)

    console.log(`机构知识库已按${organizationKBSortType.value === 'time' ? '创建时间' : '名称'}排序`)
  } catch (error) {
    console.error('机构知识库排序失败:', error)
  }
}

// 排序共享知识库
const sortSharedKBs = async () => {
  try {
    if (sharedKBs.value.length === 0) return

    // 复制数组进行排序
    let sortedKBs = [...sharedKBs.value]

    if (sharedKBSortType.value === 'time') {
      // 按创建时间倒序排列（最新的在前面）
      sortedKBs.sort((a, b) => {
        const timeA = new Date(a.create_time || a.created_at || '').getTime()
        const timeB = new Date(b.create_time || b.created_at || '').getTime()
        return timeB - timeA // 倒序
      })
    } else if (sharedKBSortType.value === 'name') {
      // 按名称正序排列（A-Z）
      sortedKBs.sort((a, b) => {
        return (a.name || '').localeCompare(b.name || '', 'zh-CN', {
          numeric: true,
          sensitivity: 'base'
        })
      })
    }

    // 更新排序后的数据
    sharedKBs.value = sortedKBs
    await updateTreeData('shared', sortedKBs)

    console.log(`共享知识库已按${sharedKBSortType.value === 'time' ? '创建时间' : '名称'}排序`)
  } catch (error) {
    console.error('共享知识库排序失败:', error)
  }
}

// 处理知识库操作
const handleKBAction = async (command: { action: string; data: TreeNode }) => {
  const {action, data} = command

  try {
    switch (action) {
      case 'rename':
        const targetId = data.datasetId || data.id

        renameForm.value = {
          id: targetId,
          name: data.label
        }
        showRenameDialog.value = true
        break

      case 'share':
        currentDatasetId.value = data.datasetId || data.id
        currentDatasetName.value = data.label
        showShareModal.value = true
        break

      case 'delete':
        await ElMessageBox.confirm(
            `确定要删除知识库"${data.label}"吗？此操作不可恢复。`,
            '删除确认',
            {
              confirmButtonText: '确定删除',
              cancelButtonText: '取消',
              type: 'warning'
            }
        )

        if (data.datasetId) {
          await datasetApi.delDataset(data.datasetId)
          ElMessage.success('删除成功')
          // 刷新对应的知识库列表
          refreshKnowledgeBase('personal')
        }
        break

      case 'exit-share':
        await ElMessageBox.confirm(
            `确定要退出共享知识库"${data.label}"吗？`,
            '退出共享确认',
            {
              confirmButtonText: '确定退出',
              cancelButtonText: '取消',
              type: 'warning'
            }
        )

        if (data.datasetId) {
          await datasetApi.putExitShare(data.datasetId)
          ElMessage.success('已退出共享')
          // 刷新共享知识库列表
          refreshKnowledgeBase('shared')
        }
        break

      case 'remove-from-org':
        if (!isAdmin.value) {
          ElMessage.error('无权限执行此操作')
          return
        }

        await ElMessageBox.confirm(
            `确定要将知识库"${data.label}"移出机构吗？`,
            '移出机构确认',
            {
              confirmButtonText: '确定移出',
              cancelButtonText: '取消',
              type: 'warning'
            }
        )

        if (data.datasetId) {
          await datasetApi.removeFromOrganization(data.datasetId)
          ElMessage.success('已移出机构')
          // 刷新机构知识库列表
          refreshKnowledgeBase('organization')
        }
        break

      case 'view':
        console.log('查看详情:', data.label)
        // 打开文档管理弹窗
        // 使用datasetId而不是带前缀的id
        currentDatasetId.value = data.datasetId || data.id
        currentDatasetName.value = data.label
        showDocumentModal.value = true
        break

      default:
        console.log('未知操作:', action)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error('操作失败：' + (error.message || '未知错误'))
    }
  }
}

// 刷新知识库数据
const refreshKnowledgeBase = async (type: string) => {
  try {
    switch (type) {
      case 'organization':
        await loadOrganizationKBs()
        break
      case 'shared':
        await loadSharedKBs()
        break
      case 'personal':
        await loadPersonalKBs()
        break
    }
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

// 处理文档变化事件
const handleDocumentChanged = async () => {
  try {
    // 刷新当前知识库的文档列表
    if (currentDatasetId.value) {
      const parentNodeId = `my_${currentDatasetId.value}`
      await loadDocuments(currentDatasetId.value, parentNodeId)

      // 更新知识库节点的文档数量统计
      const findAndUpdateDocumentCount = (nodes: TreeNode[]): boolean => {
        for (let node of nodes) {
          if (node.id === parentNodeId) {
            node.documentCount = node.children?.length || 0
            return true
          }
          if (node.children && findAndUpdateDocumentCount(node.children)) {
            return true
          }
        }
        return false
      }
      findAndUpdateDocumentCount(treeData.value)
    }

    // 刷新个人知识库列表以更新文档数量统计
    await loadPersonalKBs()

    console.log('文档变化已处理，知识库数据已更新')
  } catch (error) {
    console.error('处理文档变化失败:', error)
  }
}

// 显示文档详情
const showDocumentDetail = (document: TreeNode) => {
  console.log('显示文档详情:', document)
  // 这里可以在主内容区域显示文档详情
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (!bytes) return '-'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

// 加载机构知识库
const loadOrganizationKBs = async () => {
  try {
    const page = {current_page: 1, page_size: 100}
    const response = await datasetApi.getOrganizationDataset(page, {})

    console.log('机构知识库API响应:', response)

    if (response.data) {
      const orgKBsList = response.data.records || []
      console.log('获取到的机构知识库列表:', orgKBsList.map((kb: any) => ({
        id: kb.id,
        name: kb.name,
        create_time: kb.create_time,
        creator: kb.user?.username || '未知'
      })))

      organizationKBs.value = orgKBsList

      // 加载后立即应用排序
      await sortOrganizationKBs()
    }
  } catch (error) {
    console.error('加载机构知识库失败:', error)
  }
}

// 加载共享知识库
const loadSharedKBs = async () => {
  try {
    const page = {current_page: 1, page_size: 100}
    const response = await datasetApi.getSharedToMeDataset(page, {})

    console.log('共享知识库API响应:', response)

    if (response.data) {
      const sharedKBsList = response.data.records || []
      console.log('获取到的共享知识库列表:', sharedKBsList.map((kb: any) => ({
        id: kb.id,
        name: kb.name,
        create_time: kb.create_time,
        creator: kb.user?.username || '未知',
        shared_user_count: kb.shared_user_count || 0,
        permission: kb.permission,  // 添加权限信息
        shared_with_type: kb.shared_with_type,
        team_permission: kb.team_permission
      })))

      // 打印原始权限数据
      sharedKBsList.forEach((kb: any) => {
        console.log('知识库权限详情:', {
          name: kb.name,
          permission: kb.permission,
          shared_with_type: kb.shared_with_type,
          team_permission: kb.team_permission,
          shared_with_id: kb.shared_with_id
        })
      })

      sharedKBs.value = sharedKBsList

      // 加载后立即应用排序
      await sortSharedKBs()
    }
  } catch (error) {
    console.error('加载共享知识库失败:', error)
  }
}

// 加载个人知识库
const loadPersonalKBs = async () => {
  try {
    const page = {current_page: 1, page_size: 100}
    const response = await datasetApi.getDataset(page, {})

    if (response.data) {
      personalKBs.value = response.data.records || []

      // 加载后立即应用排序
      await sortPersonalKBs()
    }
  } catch (error) {
    console.error('加载个人知识库失败:', error)
  }
}

// 更新树形数据
const updateTreeData = async (categoryId: string, datasets: any[]) => {
  const categoryIndex = treeData.value.findIndex(item => item.id === categoryId)
  if (categoryIndex === -1) return

  const children: TreeNode[] = []

  // 为每个知识库创建节点并加载其文档
  for (const dataset of datasets) {
    const datasetNode: TreeNode = {
      id: `${categoryId}_${dataset.id}`,
      label: dataset.name,
      level: 2,
      type: 'dataset',
      datasetId: dataset.id,
      description: dataset.description,
      documentCount: dataset.document_count || 0,
      permission: dataset.permission,  // 添加权限信息
      shared_with_type: dataset.shared_with_type,
      team_permission: dataset.team_permission,
      children: [] // 先设置为空数组，稍后加载文档
    }

    // 立即加载该知识库的文档
    try {
      const docResponse = await documentApi.getAllDocument(dataset.id)
      if (docResponse.data && docResponse.data.length > 0) {
        datasetNode.children = docResponse.data.map((doc: any) => ({
          id: `doc_${doc.id}`,
          label: doc.name,
          level: 3,
          type: 'document',
          documentId: doc.id,
          datasetId: dataset.id,
          size: doc.char_length || 0,
          status: doc.status
        }))
      }
    } catch (error) {
      console.error(`加载知识库 ${dataset.name} 的文档失败:`, error)
    }

    children.push(datasetNode)
  }

  treeData.value[categoryIndex].children = children
}

// 加载知识库下的文档
const loadDocuments = async (datasetId: string, parentNodeId: string) => {
  try {
    const response = await documentApi.getAllDocument(datasetId)

    if (response.data) {
      const documents: TreeNode[] = response.data.map((doc: any) => ({
        id: `doc_${doc.id}`,
        label: doc.name,
        level: 3,
        type: 'document',
        documentId: doc.id,
        datasetId: datasetId,
        size: doc.char_length || 0,
        status: doc.status
      }))

      // 更新对应节点的children
      updateNodeChildren(parentNodeId, documents)
    }
  } catch (error) {
    console.error('加载文档失败:', error)
  }
}

// 更新节点的子节点
const updateNodeChildren = (nodeId: string, children: TreeNode[]) => {
  const findAndUpdate = (nodes: TreeNode[]): boolean => {
    for (let node of nodes) {
      if (node.id === nodeId) {
        node.children = children
        return true
      }
      if (node.children && findAndUpdate(node.children)) {
        return true
      }
    }
    return false
  }

  findAndUpdate(treeData.value)
}

// 基于选中知识库进行知识检索
const performKnowledgeSearch = async (query: string) => {
  try {
    const selectedDatasets = getSelectedDatasets()
    let searchResults: any[] = []
    let hasConnectionError = false
    let hasEmbeddingError = false

    // 对每个选中的知识库进行检索
    for (const dataset of selectedDatasets) {
      if (!dataset.datasetId) continue

      try {
        const searchData = {
          query_text: query,
          top_number: 3, // 每个知识库取前3条结果
          similarity: 0.5,
          search_mode: 'embedding'
        }

        const response = await datasetApi.getDatasetHitTest(dataset.datasetId, searchData)
        if (response.code === 200 && response.data) {
          const results = response.data.map((item: any) => ({
            ...item,
            dataset_name: dataset.label,
            source: dataset.label
          }))
          searchResults.push(...results)
        } else if (response.code === 500) {
          // 检查是否是嵌入模型连接错误
          if (response.message?.includes('Failed to establish a new connection') ||
              response.message?.includes('Connection refused')) {
            hasEmbeddingError = true
          }
        }
      } catch (error: any) {
        console.warn(`知识库 ${dataset.label} 检索失败:`, error)

        // 检测连接错误类型
        if (error.message?.includes('Failed to establish a new connection') ||
            error.message?.includes('Connection refused')) {
          hasEmbeddingError = true
        } else {
          hasConnectionError = true
        }
      }
    }

    // 按相似度排序，取前5条
    searchResults.sort((a, b) => {
      const sa = (a.similarity ?? a.comprehensive_score ?? 0)
      const sb = (b.similarity ?? b.comprehensive_score ?? 0)
      return sb - sa
    })

    return {
      results: searchResults.slice(0, 5),
      hasEmbeddingError,
      hasConnectionError
    }
  } catch (error) {
    console.error('知识检索失败:', error)
    return {
      results: [],
      hasEmbeddingError: false,
      hasConnectionError: true
    }
  }
}

// 发送消息并获得AI回答
const sendMessage = async () => {
  if (!currentMessage.value.trim() || isStreaming.value || !selectedModelId.value) return

  const userQuestion = currentMessage.value.trim()

  // 添加用户消息
  chatMessages.value.push({
    role: 'user',
    content: userQuestion,
    timestamp: new Date()
  })

  console.log('用户消息已添加，当前消息数量:', chatMessages.value.length)
  console.log('hasMessages计算值:', chatMessages.value.length > 0)

  // 清空输入框
  currentMessage.value = ''
  isStreaming.value = true

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    // 使用默认模型ID
    const modelId = selectedModelId.value || await resolveDefaultModelId()
    if (!modelId) {
      chatMessages.value.push(
          createAssistantMessage('无法获取可用的对话模型，请联系管理员配置。')
      )
      return
    }

    // 基于选中知识库进行检索
    const searchResponse = await performKnowledgeSearch(userQuestion)
    const {results: searchResults, hasEmbeddingError, hasConnectionError} = searchResponse
    console.log('知识检索结果:', searchResults)
    // 保存搜索结果，稍后添加到AI回答消息中
    let searchResultsForAI: any[] = []
    if (searchResults && searchResults.length > 0) {
      searchResultsForAI = searchResults.map(result => ({
        title: result.title,
        content: result.content,
        source: result.document_name || result.source, // 优先使用文档名称
        document_name: result.document_name,
        dataset_name: result.dataset_name,
        document_id: result.document_id,
        dataset_id: result.dataset_id,
        similarity: result.similarity,
        comprehensive_score: result.comprehensive_score
      }))
    }

    // 构建上下文
    let context = ''
    let contextNote = ''

    if (hasEmbeddingError) {
      contextNote = '\n\n注意：嵌入模型服务暂时不可用，无法进行知识库检索。回答将基于通用知识。'
      context = '由于嵌入模型服务不可用，暂时无法检索相关的知识库内容。'
      // 显示服务警告
      showServiceWarning.value = true
      serviceWarningMessage.value = '嵌入模型服务暂时不可用'
    } else if (hasConnectionError) {
      contextNote = '\n\n注意：知识库检索服务暂时不可用。回答将基于通用知识。'
      context = '由于知识库检索服务不可用，暂时无法检索相关内容。'
      // 显示服务警告
      showServiceWarning.value = true
      serviceWarningMessage.value = '知识库检索服务暂时不可用'
    } else if (searchResults.length > 0) {
      context = searchResults.map((result, index) => `参考资料${index + 1}：
标题：${result.title || '无标题'}
内容：${result.content}
来源：${result.document_name || result.source}
数据集：${result.dataset_name}`).join('\n\n')
    } else {
      context = '未找到与问题相关的知识库内容。'
      contextNote = '\n\n注意：在选中的知识库中未找到相关内容，回答将基于通用知识。'
    }

    // 构建消息
    const systemPrompt = hasEmbeddingError || hasConnectionError
      ? `你是一个专业的知识库助手。由于技术问题，当前无法检索知识库内容，请基于你的通用知识回答用户问题。请诚实告知用户当前情况，并尽力提供有帮助的一般性回答。`
      : `你是一个专业的知识库助手。请根据以下检索到的知识库内容回答用户问题。如果检索内容不足以回答问题，请诚实说明，并提供一般性建议。

检索到的相关内容：
${context}

请基于上述内容回答用户问题，保持专业、准确和有帮助的态度。${contextNote}`

    const messages = [
      {
        role: 'system',
        content: systemPrompt
      },
      ...chatMessages.value.slice(-10), // 保留最近10轮对话作为上下文
      {role: 'user', content: userQuestion}
    ]

    // 调用模型API进行流式对话
    try {
      const resp = await postModelChatStream(modelId, {messages})

      if (resp?.body && typeof resp.body.getReader === 'function') {
        const reader = resp.body.getReader()
        const decoder = new TextDecoder('utf-8')
        let currentAssistantMessage = ''

        while (true) {
          const {value, done} = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const parts = chunk.match(/data:.*\n\n/g)

          if (parts) {
            for (const part of parts) {
              try {
                const json = JSON.parse(part.replace('data:', ''))
                if (json?.content) {
                  currentAssistantMessage += json.content

                  // 实时更新最后一条消息，如果不存在则创建新的
                  const lastMessage = chatMessages.value[chatMessages.value.length - 1]
                  if (lastMessage && lastMessage.role === 'assistant') {
                    lastMessage.content = currentAssistantMessage
                  } else {
                    chatMessages.value.push({
                      role: 'assistant',
                      content: currentAssistantMessage,
                      timestamp: new Date()
                    })
                  }

                  // 滚动到底部
                  await nextTick()
                  scrollToBottom()
                }
              } catch (e) {
                console.warn('解析流式数据失败:', e)
              }
            }
          }
        }

        // 如果没有接收到内容，显示默认错误消息
        if (!currentAssistantMessage) {
          chatMessages.value.push(
              createAssistantMessage('抱歉，模型服务暂时不可用，请稍后重试。', searchResultsForAI.length > 0 ? searchResultsForAI : undefined)
          )
        } else {
          // 流式输出完成后，将分段信息添加到AI消息中
          if (searchResultsForAI.length > 0) {
            const lastMessage = chatMessages.value[chatMessages.value.length - 1]
            if (lastMessage && lastMessage.role === 'assistant') {
              lastMessage.paragraphs = searchResultsForAI
            }
          }
        }
      } else {
        // 检查是否是模型不支持的错误
        const errorText = await resp?.text?.() || ''
        if (errorText.includes('该模型不支持直接对话调用')) {
          chatMessages.value.push(
              createAssistantMessage('抱歉，当前选择的模型不支持对话功能。请联系管理员配置支持对话的模型（如：GPT、Claude、通义千问等）。', searchResultsForAI.length > 0 ? searchResultsForAI : undefined)
          )
        } else {
          chatMessages.value.push(
              createAssistantMessage('抱歉，模型服务暂时不可用，请稍后重试。', searchResultsForAI.length > 0 ? searchResultsForAI : undefined)
          )
        }
      }
    } catch (modelError: any) {
      console.error('模型调用失败:', modelError)

      // 根据错误类型提供具体的错误消息
      let errorMessage = '抱歉，处理您的问题时出现错误。'

      if (modelError.message?.includes('该模型不支持直接对话调用')) {
        errorMessage = '当前选择的模型不支持对话功能，请联系管理员配置支持对话的语言模型。'
      } else if (modelError.message?.includes('Failed to establish a new connection')) {
        errorMessage = '模型服务暂时不可用，请稍后重试或联系管理员。'
      } else if (modelError.message?.includes('timeout')) {
        errorMessage = '请求超时，请稍后重试。'
      }

      chatMessages.value.push(
          createAssistantMessage(errorMessage, searchResultsForAI.length > 0 ? searchResultsForAI : undefined)
      )
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    chatMessages.value.push(
        createAssistantMessage('抱歉，处理您的问题时出现错误，请稍后重试。')
    )
  } finally {
    isStreaming.value = false
    await nextTick()
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    setTimeout(() => {
      const container = messagesContainer.value as HTMLElement
      if (container) {
        container.scrollTop = container.scrollHeight
        // 确保滚动到底部
        container.scrollTo({
          top: container.scrollHeight,
          behavior: 'smooth'
        })
      }
    }, 100)
  }
}

const formatTime = (timestamp?: Date) => {
  if (!timestamp) return ''
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(timestamp)
}

// 格式化消息内容（支持简单的换行和段落）
const formatMessageContent = (content: string) => {
  return content
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

const createKnowledgeBase = async () => {
  if (!newKB.value.name.trim()) {
    ElMessage.warning('请输入知识库名称')
    return
  }

  try {
    // 获取默认的embedding模型ID
    let embeddingModeId = ''
    try {
      const modelRes = await modelApi.getModel({model_type: 'EMBEDDING'})
      const modelList = modelRes?.data || []
      // 自动选择名为 maxkb-embedding 的模型作为默认
      const defaultModel = modelList.find((m: any) => m?.name === 'maxkb-embedding' || m?.model_name === 'maxkb-embedding')
      if (defaultModel?.id) {
        embeddingModeId = defaultModel.id
      } else if (modelList[0]?.id) {
        embeddingModeId = modelList[0].id
      }
      console.log('获取到默认embedding模型ID:', embeddingModeId)
    } catch (error) {
      console.warn('获取默认embedding模型失败，使用空值:', error)
    }

    // 调用实际的API创建知识库，描述默认使用标题
    const newKnowledgeBase = {
      name: newKB.value.name,
      desc: newKB.value.name,  // 描述字段默认使用标题
      type: '0',  // 默认类型为普通知识库
      embedding_mode_id: embeddingModeId  // 使用获取到的默认embedding模型ID
    }

    const response = await datasetApi.postDataset(newKnowledgeBase)

    ElMessage.success('知识库创建成功')

    // 保存创建的知识库信息
    const createdDatasetId = response.data?.id
    const createdDatasetName = newKB.value.name

    // 重置表单
    newKB.value = {
      name: ''
      // description 字段隐藏，将在创建时自动使用标题
    }

    showCreateDialog.value = false

    // 刷新个人知识库列表
    await refreshKnowledgeBase('personal')

    // 显示文档管理弹窗
    if (createdDatasetId) {
      currentDatasetId.value = createdDatasetId
      currentDatasetName.value = createdDatasetName
      showDocumentModal.value = true
    }
  } catch (error) {
    console.error('创建知识库失败:', error)
    ElMessage.error('知识库创建失败')
  }
}

// 知识库重命名
const confirmRename = async () => {
  if (!renameForm.value.name.trim()) {
    ElMessage.warning('请输入知识库名称')
    return
  }

  try {
    const newName = renameForm.value.name.trim()
    const updateData = {
      name: newName,
      desc: newName
    }

    console.log('开始重命名:', {
      id: renameForm.value.id,
      oldName: renameForm.value.name,
      newName: newName,
      updateData: updateData
    })

    console.log('准备调用API，知识库ID:', renameForm.value.id)
    console.log('更新数据:', updateData)

    const response = await datasetApi.putDataset(renameForm.value.id, updateData)
    console.log('API请求URL:', `${datasetApi.putDataset.toString().split(' ')[1]}/${renameForm.value.id}`)
    console.log('API请求数据:', updateData)
    console.log('API响应:', response)
    console.log('API响应状态:', response.code, response.message)

    if (response.code === 200) {
      ElMessage.success('知识库重命名成功')

      // 更新前端数据
      const updatedKB = personalKBs.value.find(kb => kb.id === renameForm.value.id)
      if (updatedKB) {
        updatedKB.name = updateData.name
        updatedKB.desc = updateData.desc
      }

      showRenameDialog.value = false
      loadPersonalKBs()
    } else {
      ElMessage.error(response.message || '重命名失败')
    }

  } catch (error: any) {
    console.error('重命名失败:', error)
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('重命名失败，请稍后重试')
    }
  }
}

// 取消录音控制台日志
Recorder.CLog = function () {}

// 语音录制管理类
class RecorderManage {
  recorder?: any
  uploadRecording: (blob: Blob, duration: number) => void

  constructor(uploadRecording: (blob: Blob, duration: number) => void) {
    this.uploadRecording = uploadRecording
  }

  open(callback?: () => void) {
    const recorder = new Recorder({
      type: 'mp3',
      bitRate: 128,
      sampleRate: 16000
    })
    if (!this.recorder) {
      recorder.open(() => {
        this.recorder = recorder
        if (callback) {
          callback()
        }
      }, this.errorCallBack)
    }
  }

  start() {
    if (this.recorder) {
      this.recorder.start()
      recorderStatus.value = 'START'
      handleTimeChange()
    } else {
      const recorder = new Recorder({
        type: 'mp3',
        bitRate: 128,
        sampleRate: 16000
      })
      recorder.open(() => {
        this.recorder = recorder
        recorder.start()
        recorderStatus.value = 'START'
        handleTimeChange()
      }, this.errorCallBack)
    }
  }

  stop() {
    if (this.recorder) {
      this.recorder.stop(
        (blob: Blob, duration: number) => {
          // 立即停止计时器
          stopTimer()
          // 释放媒体设备权限
          this.close()
          this.uploadRecording(blob, duration)
        },
        (err: any) => {
          // 出错时也要重置状态和释放设备
          recorderStatus.value = 'STOP'
          stopTimer()
          this.close()
          MsgAlert('提示', err, {
            confirmButtonText: '确定',
            dangerouslyUseHTMLString: true
          })
        }
      )
    }
  }

  close() {
    if (this.recorder) {
      this.recorder.close()
      this.recorder = undefined
    }
  }

  private errorCallBack(err: any, isUserNotAllow: boolean) {
    if (isUserNotAllow) {
      MsgAlert('提示', err, {
        confirmButtonText: '确定',
        dangerouslyUseHTMLString: true
      })
    } else {
      MsgAlert(
        '提示',
        `${err}
        <div style="width: 100%;height:1px;border-top:1px var(--el-border-color) solid;margin:10px 0;"></div>
        录音功能需要麦克风权限，请在浏览器设置中允许此网站访问麦克风。`,
        {
          confirmButtonText: '确定',
          dangerouslyUseHTMLString: true
        }
      )
    }
  }
}

// 上传录音文件并转换为文字
const uploadRecording = async (audioBlob: Blob) => {
  try {
    // 立即设置状态为转换中
    recorderStatus.value = 'TRANSCRIBING'
    const formData = new FormData()
    formData.append('file', audioBlob, 'recording.mp3')

    // 检查STT模型是否可用
    if (!sttModelEnabled.value || !selectedSTTModelId.value) {
      ElMessage.warning('语音转文字功能不可用，请检查STT模型配置')
      recorderStatus.value = 'STOP'
      return
    }

    // 直接调用STT模型API，不需要创建临时应用
    const response = await modelApi.postSTTDirect(selectedSTTModelId.value, formData)
    if (response.data) {
      const transcribedText = typeof response.data === 'string' ? response.data : ''
      currentMessage.value = transcribedText
      ElMessage.success('语音转换完成')

      // 如果启用自动发送，则自动发送消息
      if (sttAutoSend.value && transcribedText.trim()) {
        await nextTick()
        sendMessage()
      }
    } else {
      ElMessage.error('语音转换失败')
    }
  } catch (error: any) {
    console.error('语音转换失败:', error)
    ElMessage.error('语音转换失败，请重试')
  } finally {
    // 确保状态最终被重置
    recorderStatus.value = 'STOP'
  }
}

// 创建录音管理器实例
const recorderManage = new RecorderManage(uploadRecording)

// 开始录音
const startRecording = () => {
  if (getSelectedStats().datasets === 0) {
    ElMessage.warning('请先选择知识库')
    return
  }

  if (!sttModelEnabled.value) {
    ElMessage.warning('语音转文字功能不可用，请检查STT模型配置')
    return
  }

  recorderManage.start()
}

// 停止录音
const stopRecording = () => {
  recorderManage.stop()
}

// 处理音频文件上传
const handleAudioUpload = async (file: File) => {
  // 验证文件类型
  if (!file.type.startsWith('audio/')) {
    ElMessage.error('请选择音频文件')
    return false
  }

  // 验证文件大小 (限制为50MB)
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error('音频文件大小不能超过50MB')
    return false
  }

  try {
    isUploadingAudio.value = true
    ElMessage.info('正在上传音频文件...')

    // 检查STT模型是否可用
    if (!sttModelEnabled.value || !selectedSTTModelId.value) {
      ElMessage.warning('语音转文字功能不可用，请检查STT模型配置')
      return false
    }

    // 创建FormData
    const formData = new FormData()
    formData.append('file', file)
    formData.append('model_id', selectedSTTModelId.value)

    // 调用STT API
    const response = await modelApi.postSTTDirect(selectedSTTModelId.value, formData)

    if (response.data) {
      const transcribedText = typeof response.data === 'string' ? response.data : ''
      currentMessage.value = transcribedText
      ElMessage.success('音频文件转换完成')

      // 如果启用自动发送，则自动发送消息
      if (sttAutoSend.value && transcribedText.trim()) {
        await nextTick()
        sendMessage()
      }
    } else {
      ElMessage.error('音频文件转换失败')
    }
  } catch (error: any) {
    console.error('音频文件转换失败:', error)
    ElMessage.error('音频文件转换失败，请重试')
  } finally {
    isUploadingAudio.value = false
  }

  return false // 阻止默认上传行为
}

// 处理录音计时
const handleTimeChange = () => {
  recorderTime.value = 0
  if (intervalId.value) {
    return
  }
  intervalId.value = setInterval(() => {
    if (recorderStatus.value === 'STOP') {
      clearInterval(intervalId.value!)
      intervalId.value = null
      return
    }

    recorderTime.value++

    // 60秒自动停止录音
    if (recorderTime.value === 60) {
      stopRecording()
      clearInterval(intervalId.value!)
      intervalId.value = null
      recorderStatus.value = 'STOP'
      ElMessage.warning('录音时长超过60秒，已自动停止')
    }
  }, 1000)
}

// 停止计时
const stopTimer = () => {
  if (intervalId.value !== null) {
    clearInterval(intervalId.value)
    recorderTime.value = 0
    intervalId.value = null
  }
}

onMounted(async () => {
  // 从缓存中恢复选择的模型
  const cachedModelId = localStorage.getItem('user_knowledge_default_model_id')
  if (cachedModelId) {
    selectedModelId.value = cachedModelId
  } else {
    // 如果没有缓存模型，自动选择一个默认模型
    try {
      const defaultModelId = await resolveDefaultModelId()
      if (defaultModelId) {
        selectedModelId.value = defaultModelId
      }
    } catch (error) {
      console.warn('获取默认模型失败:', error)
    }
  }

  // 从缓存中恢复排序偏好
  const cachedSortType = localStorage.getItem('personal_kb_sort_type') as 'time' | 'name'
  if (cachedSortType && ['time', 'name'].includes(cachedSortType)) {
    personalKBSortType.value = cachedSortType
  }

  // 恢复机构知识库排序偏好
  const cachedOrgSortType = localStorage.getItem('organization_kb_sort_type') as 'time' | 'name'
  if (cachedOrgSortType && ['time', 'name'].includes(cachedOrgSortType)) {
    organizationKBSortType.value = cachedOrgSortType
  }

  // 恢复共享知识库排序偏好
  const cachedSharedSortType = localStorage.getItem('shared_kb_sort_type') as 'time' | 'name'
  if (cachedSharedSortType && ['time', 'name'].includes(cachedSharedSortType)) {
    sharedKBSortType.value = cachedSharedSortType
  }

  // 并行加载知识库、模型列表和STT模型
  await Promise.all([
    loadOrganizationKBs(),
    loadSharedKBs(),
    loadPersonalKBs(),
    loadAvailableModels(),
    loadAvailableSTTModels()
  ])
})

// 页面卸载时清理媒体设备
onUnmounted(() => {
  // 停止录音并释放媒体设备
  if (recorderStatus.value !== 'STOP') {
    stopRecording()
  }
  // 确保录音器被关闭
  recorderManage.close()
  // 清理计时器
  stopTimer()
})
</script>

<style lang="scss" scoped>
.user-knowledge-container {
  height: calc(100vh - 64px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.knowledge-layout {
  display: flex;
  height: 100%;
  max-height: calc(100vh - 64px);
  overflow: hidden;
}

.knowledge-sidebar {
  width: 300px;
  background: #ffffff;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  height: 100%;
  max-height: calc(100vh - 64px);
  overflow: hidden;

  .sidebar-header {
    padding: 20px;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      margin: 0;
      color: #2c3e50;
      font-size: 18px;
      font-weight: 600;
    }

    .create-btn {
      border-radius: 6px;
      font-size: 14px;
      padding: 8px 16px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
      }
    }
  }

  .sidebar-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 20px;
    min-height: 0;
    overflow: hidden;
  }

  .knowledge-search {
    margin-bottom: 16px;
  }

  .selection-info {
    background: #e6f3ff;
    border: 1px solid #3370ff;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 16px;
    text-align: center;

    .selected-count {
      font-size: 13px;
      color: #3370ff;
      font-weight: 500;
    }
  }

  .knowledge-tree {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    min-height: 0;

    /* 自定义滚动条样式 */
    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-track {
      background: #f8fafc;
      border-radius: 3px;
    }

    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 3px;

      &:hover {
        background: #a8a8a8;
      }
    }

    .knowledge-tree-container {
      border: none;
      background: transparent;

      :deep(.el-tree-node) {
        margin-bottom: 4px;

        .el-tree-node__content {
          height: auto;
          padding: 4px 0;
          background: transparent;
          border-radius: 6px;

          &:hover {
            background: #f5f7fa !important;
          }
        }

        .el-tree-node__expand-icon {
          padding: 6px;
          font-size: 12px;
          color: #909399;

          &.is-leaf {
            color: transparent;
          }
        }

        .el-checkbox {
          margin-right: 8px;

          .el-checkbox__input {
            .el-checkbox__inner {
              width: 16px;
              height: 16px;
              border-radius: 3px;
            }
          }
        }
      }
    }

    .tree-node {
      width: 80%;

      &.active {
        .node-content {
          background: #e6f3ff;
          border: 1px solid #3370ff;
        }
      }
    }

    .node-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 2px 12px;
      border-radius: 6px;
      transition: all 0.3s ease;
      min-height: 36px;

      &.level-1-content {
        font-weight: 600;
        background: #f8fafc;
        border: 1px solid #e9ecef;
        margin-bottom: 4px;

        .node-left {
          display: flex;
          align-items: center;
          gap: 8px;
          flex: 1;
          min-width: 0;
        }

        .node-icon {
          color: #3370ff;
          font-size: 16px;
        }

        .node-label {
          color: #2c3e50;
          font-size: 14px;
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .more-actions {
          color: #909399;
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;

          &:hover {
            background: #e9ecef;
            color: #606266;
          }
        }
      }

      &.level-2-content {
        padding-left: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;

        .node-left {
          display: flex;
          align-items: center;
          flex: 1;
          min-width: 0;
        }

        .node-icon {
          color: #67c23a;
          font-size: 14px;
          margin-right: 8px;
          flex-shrink: 0;
        }

        .node-label {
          color: #303133;
          font-size: 13px;
          font-weight: 500;
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .doc-count {
          color: #909399;
          font-size: 12px;
          margin-left: 6px;
        }

        .more-actions {
          opacity: 0;
          transition: opacity 0.2s;
          cursor: pointer;
          padding: 2px;
          font-size: 14px;
          color: #909399;

          &:hover {
            color: #409eff;
          }
        }

        &:hover .more-actions {
          opacity: 1;
        }
      }

      &.level-3-content {
        padding-left: 10px;
        display: flex;
        align-items: center;

        .node-icon {
          color: #e6a23c;
          font-size: 12px;
          margin-right: 8px;
          flex-shrink: 0;
        }

        .node-label {
          color: #606266;
          font-size: 12px;
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .file-size {
          color: #c0c4cc;
          font-size: 11px;
          margin-left: 8px;
          flex-shrink: 0;
        }
      }
    }
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #909399;

    .el-icon {
      font-size: 48px;
      margin-bottom: 16px;
    }

    p {
      margin: 0;
    }
  }
}

.knowledge-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  position: relative; /* 为绝对定位提供上下文 */


  .chat-content {
    display: flex;
    flex-direction: column;
    height: 100%;
    flex: 1;
    min-height: 0;
  }

  .chat-header {
    padding: 20px;
    background: white;
    border-bottom: 1px solid #e4e7ed;

    .header-info {
      margin-bottom: 16px;

      h2 {
        margin: 0 0 8px 0;
        color: #303133;
        font-size: 20px;
        font-weight: 600;
      }

      p {
        margin: 0;
        color: #909399;
        font-size: 14px;
      }
    }

    .selected-datasets {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .dataset-tag {
        background: #e6f3ff;
        border-color: #3370ff;
        color: #3370ff;

        &.more-tag {
          background: #f0f2f5;
          border-color: #c0c4cc;
          color: #909399;
        }
      }
    }

    .service-warning {
      margin-top: 16px;

      :deep(.el-alert) {
        border-radius: 6px;

        .el-alert__title {
          font-size: 14px;
          font-weight: 500;
        }

        .el-alert__content {
          font-size: 13px;

          p {
            margin: 4px 0 0 0;
          }
        }
      }
    }
  }

  .chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
    position: relative;
    background: #fafbfc; /* 设置白色背景，为输入组件预留空间 */

    &:not(.has-messages) {
      justify-content: center;
      align-items: center;
      min-height: calc(100vh - 200px); /* 确保有足够的高度 */
    }

    &.has-messages {
      justify-content: flex-start;
      /* 当有消息时，为输入框预留空间 */
      padding-bottom: 140px; /* 调整底部空间，为输入组件留出合适高度 */
    }
  }

  .chat-messages {
    flex: 1;
    padding: 20px;
    padding-bottom: 20px; /* 调整底部内边距 */
    overflow-y: auto;
    background: #fafbfc;
    min-height: 0;
    max-height: calc(100vh - 300px); /* 调整最大高度，为输入组件留出合适空间 */

    /* 自定义滚动条样式 */
    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 3px;
    }

    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 3px;

      &:hover {
        background: #a8a8a8;
      }
    }

    .message {
      margin-bottom: 20px;
      display: flex;

      &.user-message {
        justify-content: flex-end;

        .message-content {
          max-width: 70%;
          background: #3370ff;
          color: white;
          padding: 12px 16px;
          border-radius: 18px 18px 4px 18px;
          box-shadow: 0 2px 4px rgba(51, 112, 255, 0.2);
        }
      }

      &.ai-message {
        justify-content: flex-start;

        .message-content {
          max-width: 70%;
          background: white;
          color: #303133;
          padding: 12px 16px;
          border-radius: 18px 18px 18px 4px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          border: 1px solid #e9ecef;
        }

        &.streaming .message-content {
          background: #f8fafc;
          border-color: #3370ff;
        }
      }

      .message-text {
        line-height: 1.6;
        word-wrap: break-word;

        :deep(strong) {
          font-weight: 600;
        }

        :deep(em) {
          font-style: italic;
          color: #3370ff;
        }
      }

      .message-time {
        font-size: 11px;
        opacity: 0.6;
        margin-top: 6px;
        text-align: right;
      }

      // 匹配分段样式
      .matched-paragraphs {
        margin-top: 12px;
        border-top: 1px solid #e9ecef;
        padding-top: 12px;

        .paragraphs-header {
          margin-bottom: 8px;

          .toggle-paragraphs-btn {
            color: #606266;
            font-size: 12px;
            padding: 4px 0;

            &:hover {
              color: #3370ff;
            }

            .el-icon {
              &.rotate {
                transform: rotate(180deg);
              }

              transition: transform 0.3s ease;
            }
          }
        }

        .paragraphs-list {
          .paragraph-item {
            background: #f8fafc;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;

            &:last-child {
              margin-bottom: 0;
            }

            .paragraph-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 8px;

              .paragraph-index {
                background: #e9ecef;
                color: #606266;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
              }

              .paragraph-score {
                font-size: 11px;
                color: #3370ff;
                font-weight: 500;
              }
            }

            .paragraph-content {
              font-size: 12px;
              line-height: 1.5;
              color: #303133;
              margin-bottom: 8px;
              max-height: 150px;
              overflow: hidden;
              text-overflow: ellipsis;
              display: -webkit-box;
              -webkit-line-clamp: 6;
              line-clamp: 6;
              -webkit-box-orient: vertical;
            }

            .paragraph-meta {
              display: flex;
              gap: 12px;
              font-size: 10px;
              color: #909399;

              .paragraph-source,
              .paragraph-dataset {
                background: #e9ecef;
                padding: 2px 6px;
                border-radius: 3px;
              }

              .paragraph-source.clickable {
                cursor: pointer;
                transition: all 0.3s ease;

                &:hover {
                  background: #3370ff;
                  color: white;
                  transform: translateY(-1px);
                }
              }
            }
          }
        }
      }
    }

    .loading-text {
      color: #3370ff;
      font-weight: 500;
    }

    .loading-dots {
      .dot {
        animation: loading-dots 1.4s infinite ease-in-out;
        color: #3370ff;
        font-size: 18px;

        &:nth-child(1) {
          animation-delay: -0.32s;
        }

        &:nth-child(2) {
          animation-delay: -0.16s;
        }

        &:nth-child(3) {
          animation-delay: 0s;
        }
      }
    }
  }

  @keyframes loading-dots {
    0%, 80%, 100% {
      opacity: 0;
      transform: scale(0.8);
    }
    40% {
      opacity: 1;
      transform: scale(1);
    }
  }

  .integrated-chat-input {
    padding: 16px 20px;
    background: white;
    flex-shrink: 0;
    min-height: 120px; /* 设置最小高度，确保输入组件有足够空间 */
    position: relative;
    transition: all 0.5s ease-in-out;

    &.centered {
      position: absolute !important;
      top: 50% !important;
      left: 50% !important;
      transform: translate(-50%, -50%) !important;
      width: 85% !important;
      max-width: 800px !important;
      border: 1px solid #e9ecef !important;
      border-radius: 16px !important;
      box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12) !important;
      z-index: 1000 !important;
    }

    &.bottom {
      position: absolute !important;
      bottom: 30px !important; /* 调整底部位置，给消息区域更多空间 */
      left: 50% !important;
      transform: translateX(-50%) !important;
      width: 85% !important;
      max-width: 800px !important;
      border: 1px solid #e9ecef !important;
      border-radius: 16px !important;
      box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12) !important;
      top: auto !important;
      right: auto !important;
      z-index: 1000 !important;
    }

    .kb-info-container {
      margin-bottom: 16px;
      transition: all 0.3s ease-in-out;

      .kb-info-content {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 8px;
        flex-wrap: wrap;

        .kb-info-text {
          font-size: 12px;
          color: #666;
          margin: 0;
          white-space: nowrap;
        }

        .selected-datasets {
          display: flex;
          align-items: center;
          gap: 6px;
          flex-wrap: wrap;

          .dataset-tag {
            font-size: 11px;
            height: 20px;
            line-height: 18px;

            &.more-tag {
              background-color: #f0f0f0;
              color: #666;
            }
          }
        }
      }
    }

    &.centered .kb-info-container {
      .kb-info-content {
        justify-content: flex-start;
      }

      .kb-info-text {
        font-size: 13px;
        color: #333;
        font-weight: 500;
      }
    }

    .input-container {
      .input-wrapper {
        background: #ffffff;
        border: 1px solid var(--el-border-color-light);
        border-radius: 12px;
        padding: 12px 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;

        &:has(.el-textarea__inner:focus) {
          border-color: var(--el-color-primary);
          box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.15);
        }

        .input-content {
          display: flex;
          align-items: center;
          gap: 12px;

          .chat-input {
            flex: 1;

            :deep(.el-textarea__inner) {
              border: none;
              box-shadow: none;
              padding: 6px 0;
              background: transparent;
              font-size: 14px;
              line-height: 1.5;
              resize: none;
              min-height: 24px;
              vertical-align: middle;

              &::placeholder {
                color: var(--el-text-color-placeholder);
              }
            }
          }

          .send-btn {
            border-radius: 8px;
            font-size: 13px;
            padding: 6px 20px;
            font-weight: 500;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
            flex-shrink: 0;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;

            &:hover:not(:disabled) {
              transform: translateY(-1px);
              box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
            }
          }

          // 语音按钮样式
          .voice-btn {
            border-radius: 8px;
            padding: 6px 12px;
            height: 36px;
            color: #606266;
            transition: all 0.3s ease;
            flex-shrink: 0;

            &:hover:not(:disabled) {
              color: #409eff;
              background-color: #ecf5ff;
              transform: translateY(-1px);
            }

            &:disabled {
              opacity: 0.5;
              cursor: not-allowed;
            }
          }

          // 音频上传按钮样式
          .audio-upload-btn {
            display: inline-block;
            margin-left: 4px;

            .voice-btn {
              margin-left: 0;
            }
          }

          // 录音状态显示样式
          .voice-recording {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            background: #f0f9ff;
            border: 1px solid #409eff;
            border-radius: 8px;
            height: 36px;
            flex-shrink: 0;

            .recording-time {
              font-size: 12px;
              font-weight: 500;
              color: #409eff;
              min-width: 35px;
            }

            .stop-btn {
              padding: 4px 8px;
              height: 24px;
              border-radius: 4px;
              color: #409eff;

              &:hover:not(:disabled) {
                background-color: #409eff;
                color: white;
              }

              .stop-icon {
                font-style: normal;
                font-size: 12px;
              }
            }
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .knowledge-layout {
    flex-direction: column;
  }

  .knowledge-sidebar {
    width: 100%;
    height: 200px;
    max-height: 200px;

    .sidebar-content {
      padding: 12px;
    }

    .knowledge-tree {
      /* 移动端滚动条稍微细一些 */
      &::-webkit-scrollbar {
        width: 4px;
      }
    }
  }

  .knowledge-main {
    .chat-messages {
      max-height: calc(100vh - 320px); /* 移动端调整高度，为输入组件留出更多空间 */
      padding: 16px;
    }

    .chat-area.has-messages {
      padding-bottom: 160px; /* 移动端输入框空间调整 */
    }
  }

  .integrated-chat-input {
    &.centered, &.bottom {
      width: 95% !important;
      max-width: none !important;
      min-height: 100px; /* 移动端输入组件最小高度 */
    }

    .input-container .input-wrapper {
      padding: 12px 16px; /* 增加移动端内边距 */

      .input-content {
        gap: 10px;

        .chat-input {
          :deep(.el-textarea__inner) {
            padding: 6px 0;
            min-height: 24px;
            font-size: 14px; /* 增大字体 */
          }
        }

        .send-btn {
          padding: 6px 18px;
          font-size: 13px;
          height: 34px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      }
    }
  }
}

/* 模型选择器样式 */
.model-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding: 10px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

/* STT设置面板样式 */
.stt-settings {
  margin-bottom: 12px;
  padding: 10px 16px;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #b3d8ff;

  .stt-settings-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 8px;
    font-size: 13px;
    font-weight: 500;
    color: #409eff;

    .el-icon {
      font-size: 14px;
    }
  }

  .stt-settings-content {
    .el-checkbox {
      font-size: 12px;
      color: #606266;

      :deep(.el-checkbox__label) {
        font-size: 12px;
      }
    }
  }
}

/* STT不可用提示样式 */
.stt-disabled-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #fef0f0;
  border-radius: 6px;
  border: 1px solid #fbc4c4;
  font-size: 12px;
  color: #f56c6c;

  .el-icon {
    font-size: 14px;
  }
}

.model-selector-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.model-select {
  flex: 1;
  max-width: 250px;
}

.model-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-name {
  font-weight: 500;
  color: #303133;
}

.model-provider {
  font-size: 12px;
  color: #909399;
}

/* 文档管理弹窗样式 */
:deep(.document-modal) {
  .el-dialog__body {
    padding: 0 20px 20px 20px;
  }

  .el-dialog__header {
    padding: 20px 20px 10px 20px;
    border-bottom: 1px solid #ebeef5;
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 12px 0 0 0;
    border-top: 1px solid #ebeef5;
  }
}


/* 共享设置弹窗样式 */
:deep(.share-modal) {
  .el-dialog__body {
    padding: 20px;
    max-height: 60vh;
    overflow-y: auto;
  }

  .el-dialog__header {
    padding: 20px 20px 10px 20px;
    border-bottom: 1px solid #ebeef5;
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    padding: 12px 0 0 0;
    border-top: 1px solid #ebeef5;
  }
}

/* 重命名对话框样式 */
:deep(.rename-dialog) {
  .el-dialog__header {
    .el-dialog__title {
      white-space: nowrap; /* 防止标题换行 */
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .el-dialog__body {
    padding: 20px;
  }
}
</style>
