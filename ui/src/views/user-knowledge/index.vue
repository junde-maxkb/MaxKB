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
              <Plus />
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
            <span class="selected-count"> 已选择: {{ getSelectedStats().datasets }}个知识库 </span>
          </div>

          <!-- 知识库树形结构 -->
          <div class="knowledge-tree">
            <el-tree
              ref="treeRef"
              :data="filteredTreeData"
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
                <div
                  class="tree-node"
                  :class="{
                    'level-1': data.level === 1,
                    'level-2': data.level === 2,
                    'level-3': data.level === 3,
                    active: selectedNode?.id === data.id
                  }"
                >
                  <!-- 一级目录 -->
                  <div v-if="data.level === 1" class="node-content level-1-content">
                    <div class="node-left">
                      <el-icon class="node-icon">
                        <component :is="data.icon" />
                      </el-icon>
                      <span class="node-label" :title="data.label">{{ data.label }}</span>
                    </div>
                    <el-dropdown trigger="click" @command="handleLevel1Action" @click.stop>
                      <el-icon class="more-actions">
                        <MoreFilled />
                      </el-icon>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <!-- 个人知识库菜单 -->
                          <template v-if="data.type === 'personal'">
                            <el-dropdown-item :command="{ action: 'refresh', data }">
                              <el-icon>
                                <Refresh />
                              </el-icon>
                              刷新
                            </el-dropdown-item>
                            <el-dropdown-item divided>
                              <span style="color: #909399; font-size: 12px">排序方式</span>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'sort-by-time', data }">
                              <el-icon>
                                <Timer />
                              </el-icon>
                              按时间排序
                              <el-icon
                                v-if="personalKBSortType === 'time'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
                              </el-icon>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'sort-by-name', data }">
                              <el-icon>
                                <Sort />
                              </el-icon>
                              按名称排序
                              <el-icon
                                v-if="personalKBSortType === 'name'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
                              </el-icon>
                            </el-dropdown-item>
                          </template>

                          <!-- 机构知识库菜单 - 只有排序功能 -->
                          <template v-else-if="data.type === 'organization'">
                            <el-dropdown-item :command="{ action: 'refresh', data }">
                              <el-icon>
                                <Refresh />
                              </el-icon>
                              刷新
                            </el-dropdown-item>
                            <el-dropdown-item divided>
                              <span style="color: #909399; font-size: 12px">排序方式</span>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'org-sort-by-name', data }">
                              <el-icon>
                                <Sort />
                              </el-icon>
                              按名称排序
                              <el-icon
                                v-if="organizationKBSortType === 'name'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
                              </el-icon>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'org-sort-by-time', data }">
                              <el-icon>
                                <Timer />
                              </el-icon>
                              按创建时间排序
                              <el-icon
                                v-if="organizationKBSortType === 'time'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
                              </el-icon>
                            </el-dropdown-item>
                          </template>

                          <!-- 共享知识库菜单 -->
                          <template v-else-if="data.type === 'shared'">
                            <el-dropdown-item :command="{ action: 'refresh', data }">
                              <el-icon>
                                <Refresh />
                              </el-icon>
                              刷新
                            </el-dropdown-item>
                            <el-dropdown-item divided>
                              <span style="color: #909399; font-size: 12px">排序方式</span>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'shared-sort-by-name', data }">
                              <el-icon>
                                <Sort />
                              </el-icon>
                              按名称排序
                              <el-icon
                                v-if="sharedKBSortType === 'name'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
                              </el-icon>
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'shared-sort-by-time', data }">
                              <el-icon>
                                <Timer />
                              </el-icon>
                              按创建时间排序
                              <el-icon
                                v-if="sharedKBSortType === 'time'"
                                style="margin-left: auto; color: #409eff"
                              >
                                <Check />
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
                        <Folder />
                      </el-icon>
                      <span class="node-label" :title="data.label">{{ data.label }}</span>
                      <span class="doc-count">({{ data.documentCount || 0 }})</span>
                    </div>

                    <!-- 知识库操作按钮 -->
                    <el-dropdown trigger="click" @command="handleKBAction" @click.stop>
                      <el-icon class="more-actions">
                        <MoreFilled />
                      </el-icon>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <!-- 我的知识库 - 完整操作权限 -->
                          <template v-if="getKBType(data) === 'personal'">
                            <el-dropdown-item :command="{ action: 'view', data }">
                              <el-icon>
                                <View />
                              </el-icon>
                              查看详情
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'rename', data }">
                              <el-icon>
                                <EditPen />
                              </el-icon>
                              重命名
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'share', data }" @click.stop>
                              <el-icon>
                                <Share />
                              </el-icon>
                              共享设置
                            </el-dropdown-item>
                            <el-dropdown-item :command="{ action: 'delete', data }" divided>
                              <el-icon>
                                <Delete />
                              </el-icon>
                              删除
                            </el-dropdown-item>
                          </template>

                          <!-- 共享知识库 - 辅助管理可以查看详情 -->
                          <template v-if="getKBType(data) === 'shared'">
                            <template
                              v-if="
                                data.permission === 'MANAGE' ||
                                (data.shared_with_type === 'TEAM' &&
                                  data.team_permission === 'MANAGE')
                              "
                            >
                              <el-dropdown-item :command="{ action: 'view', data }">
                                <el-icon>
                                  <View />
                                </el-icon>
                                查看详情
                              </el-dropdown-item>
                              <el-dropdown-item divided :command="{ action: 'exit-share', data }">
                                <el-icon>
                                  <Close />
                                </el-icon>
                                退出共享
                              </el-dropdown-item>
                            </template>
                            <template v-else>
                              <el-dropdown-item :command="{ action: 'exit-share', data }">
                                <el-icon>
                                  <Close />
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
                                  <Edit />
                                </el-icon>
                                编辑
                              </el-dropdown-item>
                              <el-dropdown-item :command="{ action: 'remove-from-org', data }">
                                <el-icon>
                                  <FolderRemove />
                                </el-icon>
                                移出机构
                              </el-dropdown-item>
                            </template>
                            <template v-else>
                              <el-dropdown-item disabled>
                                <span style="color: #c0c4cc">无可用操作</span>
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
                      <DocumentCopy />
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

          <!-- 新聊天按钮 -->
          <div v-if="hasMessages" class="new-chat-header">
            <el-button type="primary" link class="new-chat-button" @click="newChat">
              <el-icon>
                <Plus />
              </el-icon>
              <span class="ml-4">新聊天</span>
            </el-button>
          </div>

          <div class="chat-area" :class="{ 'has-messages': hasMessages }">
            <!-- 对话消息区域 -->
            <div
              class="chat-messages"
              ref="messagesContainer"
              @scroll="handleScroll"
              v-if="hasMessages"
            >
              <div
                v-for="(message, index) in chatMessages"
                :key="index"
                class="message"
                :class="{
                  'user-message': message.role === 'user',
                  'ai-message': message.role === 'assistant',
                  'system-message': message.role === 'system'
                }"
              >
                <div class="message-content">
                  <div class="message-text" v-html="formatMessageContent(message.content)"></div>

                  <!-- 显示引导式问答的建议问题（仅AI回答且有suggestions时显示） -->
                  <div
                    v-if="
                      message.role === 'assistant' &&
                      message.suggestions &&
                      message.suggestions.length > 0
                    "
                    class="suggestions-container"
                  >
                    <div class="suggestions-header">
                      <el-icon class="suggestions-icon">
                        <ChatLineRound />
                      </el-icon>
                      <span class="suggestions-title">推荐问题：</span>
                    </div>
                    <div class="suggestions-list">
                      <el-button
                        v-for="(suggestion, sIndex) in message.suggestions"
                        :key="sIndex"
                        type="primary"
                        plain
                        size="small"
                        class="suggestion-btn"
                        @click="handleSuggestionClick(suggestion)"
                      >
                        {{ suggestion }}
                      </el-button>
                    </div>
                  </div>

                  <!-- 显示匹配的分段（仅AI回答且有分段信息时显示） -->
                  <!--                  <div-->
                  <!--                    v-if="-->
                  <!--                      message.role === 'assistant' &&-->
                  <!--                      message.paragraphs &&-->
                  <!--                      message.paragraphs.length > 0-->
                  <!--                    "-->
                  <!--                    class="matched-paragraphs"-->
                  <!--                  >-->
                  <!--                    <div class="paragraphs-header">-->
                  <!--                      <el-button-->
                  <!--                        type="text"-->
                  <!--                        size="small"-->
                  <!--                        @click="toggleParagraphsVisibility(index)"-->
                  <!--                        class="toggle-paragraphs-btn"-->
                  <!--                      >-->
                  <!--                        <el-icon>-->
                  <!--                          <Document />-->
                  <!--                        </el-icon>-->
                  <!--                        找到 {{ message.paragraphs.length }} 个相关分段-->
                  <!--                        <el-icon :class="{ rotate: isParagraphsExpanded(index) }">-->
                  <!--                          <ArrowDown />-->
                  <!--                        </el-icon>-->
                  <!--                      </el-button>-->
                  <!--                    </div>-->

                  <!--                    <div v-show="isParagraphsExpanded(index)" class="paragraphs-list">-->
                  <!--                      <div-->
                  <!--                        v-for="(paragraph, pIndex) in message.paragraphs"-->
                  <!--                        :key="pIndex"-->
                  <!--                        class="paragraph-item"-->
                  <!--                      >-->
                  <!--                        <div class="paragraph-header">-->
                  <!--                          <span class="paragraph-index">{{ pIndex + 1 }}</span>-->
                  <!--                          <span class="paragraph-score">-->
                  <!--                            相关度:-->
                  <!--                            {{-->
                  <!--                              (-->
                  <!--                                (paragraph.similarity || paragraph.comprehensive_score || 0) * 100-->
                  <!--                              ).toFixed(1)-->
                  <!--                            }}%-->
                  <!--                          </span>-->
                  <!--                        </div>-->
                  <!--                        <div class="paragraph-content">{{ paragraph.content }}</div>-->
                  <!--                        <div class="paragraph-meta">-->
                  <!--                          <span-->
                  <!--                            class="paragraph-source clickable"-->
                  <!--                            @click="openDocumentParagraphs(paragraph)"-->
                  <!--                            :title="`点击查看 ${paragraph.document_name || paragraph.source || paragraph.dataset_name} 的分段内容`"-->
                  <!--                          >-->
                  <!--                            文档名称:-->
                  <!--                            {{-->
                  <!--                              paragraph.document_name || paragraph.source || paragraph.dataset_name-->
                  <!--                            }}-->
                  <!--                          </span>-->
                  <!--                          <span class="paragraph-dataset"-->
                  <!--                            >知识库名称: {{ paragraph.dataset_name }}</span-->
                  <!--                          >-->
                  <!--                        </div>-->
                  <!--                      </div>-->
                  <!--                    </div>-->
                  <!--                  </div>-->

                  <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                  <div style="height: 20px" class="copy-btn" v-show="message.role === 'assistant'">
                    <DocumentCopy
                      style="height: inherit"
                      @click="() => copyMessage(message.content)"
                    />
                  </div>
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
            <div
              class="integrated-chat-input"
              :class="{ centered: !hasMessages, bottom: hasMessages }"
            >
              <!-- 知识库信息提示 -->
              <div class="kb-info-container" :class="{ 'moved-down': hasMessages }">
                <div class="kb-info-content">
                  <!-- AI翻译模式已上传文档展示 -->
                  <div v-if="isAITranslateMode && translateDocumentName">
                    <div class="kb-info-text">
                      <el-icon class="info-icon">
                        <Document />
                      </el-icon>
                      已上传待翻译文档：
                    </div>
                    <div class="selected-items">
                      <el-tag
                        size="small"
                        class="item-tag document-tag"
                        closable
                        @close="removeTranslateDocument"
                      >
                        {{ translateDocumentName }}
                      </el-tag>
                    </div>
                  </div>

                  <!-- AI翻译模式提示 -->
                  <div v-else-if="isAITranslateMode" class="kb-info-text">
                    <el-icon class="info-icon">
                      <Connection />
                    </el-icon>
                    AI翻译模式：直接输入需要翻译的内容或上传文档，目标语言为 {{ targetLanguage }}
                  </div>

                  <!-- AI摘要模式已上传文档展示 -->
                  <div v-else-if="isAISummaryMode && summaryDocumentName">
                    <div class="kb-info-text">
                      <el-icon class="info-icon">
                        <Document />
                      </el-icon>
                      已上传待摘要文档：
                    </div>
                    <div class="selected-items">
                      <el-tag
                        size="small"
                        class="item-tag document-tag"
                        closable
                        @close="removeSummaryDocument"
                      >
                        {{ summaryDocumentName }}
                      </el-tag>
                    </div>
                  </div>

                  <!-- AI综述模式已上传文档展示 -->
                  <div v-else-if="isAIReviewMode && reviewDocumentName">
                    <div class="kb-info-text">
                      <el-icon class="info-icon">
                        <Document />
                      </el-icon>
                      已上传待综述文档：
                    </div>
                    <div class="selected-items">
                      <el-tag
                        size="small"
                        class="item-tag document-tag"
                        closable
                        @close="removeReviewDocument"
                      >
                        {{ reviewDocumentName }}
                      </el-tag>
                    </div>
                  </div>

                  <!-- AI问数模式已上传文档展示 -->
                  <div v-else-if="isAIQuestionMode && questionDocumentName">
                    <div class="kb-info-text">
                      <el-icon class="info-icon">
                        <Document />
                      </el-icon>
                      已上传待问数文档：
                    </div>
                    <div class="selected-items">
                      <el-tag
                        size="small"
                        class="item-tag document-tag"
                        closable
                        @close="removeQuestionDocument"
                      >
                        {{ questionDocumentName }}
                      </el-tag>
                    </div>
                  </div>

                  <!-- AI写作模式已上传文档展示 -->
                  <div v-else-if="isAIWritingMode && uploadedDocumentName">
                    <div class="kb-info-text">
                      <el-icon class="info-icon">
                        <Document />
                      </el-icon>
                      已上传参考文档：
                    </div>
                    <div class="selected-items">
                      <el-tag
                        size="small"
                        class="item-tag document-tag"
                        closable
                        @close="removeUploadedDocument"
                      >
                        {{ uploadedDocumentName }}
                      </el-tag>
                    </div>
                  </div>

                  <div class="kb-info-text" v-else-if="selectedInfo">
                    <template v-if="selectedInfo.type === 'documents'">
                      <el-icon class="info-icon">
                        <DocumentCopy />
                      </el-icon>
                      基于 {{ selectedInfo.count }} 个选中文档进行问答：
                    </template>
                    <template v-else-if="selectedInfo.type === 'datasets'">
                      <el-icon class="info-icon">
                        <Collection />
                      </el-icon>
                      基于 {{ selectedInfo.count }} 个知识库进行问答：
                    </template>
                  </div>
                  <div class="kb-info-text" v-else>
                    <el-icon class="info-icon">
                      <Warning />
                    </el-icon>
                    请从左侧选择知识库或文档开始问答
                  </div>

                  <!-- 选中的文档显示 -->
                  <div
                    v-if="selectedInfo && selectedInfo.type === 'documents'"
                    class="selected-items"
                  >
                    <el-tag
                      v-for="(item, index) in selectedInfo.items.slice(0, 4)"
                      :key="index"
                      size="small"
                      class="item-tag document-tag"
                    >
                      {{ item }}
                    </el-tag>
                    <el-tag
                      v-if="selectedInfo.items.length > 4"
                      size="small"
                      class="item-tag more-tag"
                    >
                      +{{ selectedInfo.items.length - 4 }}
                    </el-tag>
                  </div>

                  <!-- 选中的知识库显示 -->
                  <div
                    v-else-if="selectedInfo && selectedInfo.type === 'datasets'"
                    class="selected-items"
                  >
                    <el-tag
                      v-for="item in selectedInfo.items.slice(0, 4)"
                      :key="item"
                      size="small"
                      class="item-tag dataset-tag"
                    >
                      {{ item }}
                    </el-tag>
                    <el-tag
                      v-if="selectedInfo.items.length > 4"
                      size="small"
                      class="item-tag more-tag"
                    >
                      +{{ selectedInfo.items.length - 4 }}
                    </el-tag>
                  </div>
                </div>
              </div>

              <!-- 模型选择器 -->
              <div class="model-selector" v-show="false">
                <div class="model-selector-label">
                  <el-icon>
                    <Setting />
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
                    <!-- AI写作模式标签 -->
                    <div v-if="isAIWritingMode" class="ai-writing-label">
                      <el-icon class="ai-label-icon">
                        <Edit />
                      </el-icon>
                      <span class="ai-label-text">AI 写作</span>
                    </div>
                    <div v-else-if="isAITranslateMode" class="ai-writing-label">
                      <el-icon class="ai-label-icon">
                        <Edit />
                      </el-icon>
                      <span class="ai-label-text">AI 翻译</span>
                    </div>
                    <div v-else-if="isAISummaryMode" class="ai-writing-label">
                      <el-icon class="ai-label-icon">
                        <Edit />
                      </el-icon>
                      <span class="ai-label-text">AI 摘要</span>
                    </div>
                    <div v-else-if="isAIReviewMode" class="ai-writing-label">
                      <el-icon class="ai-label-icon">
                        <Edit />
                      </el-icon>
                      <span class="ai-label-text">AI 综述</span>
                    </div>
                    <div v-else-if="isAIQuestionMode" class="ai-writing-label">
                      <el-icon class="ai-label-icon">
                        <Edit />
                      </el-icon>
                      <span class="ai-label-text">AI 问数</span>
                    </div>

                    <!-- AI翻译模式：目标语言选择 -->
                    <el-select
                      v-if="isAITranslateMode"
                      v-model="targetLanguage"
                      placeholder="选择目标语言"
                      size="small"
                      class="language-select-simple"
                    >
                      <el-option label="中文" value="中文" />
                      <el-option label="英文" value="英文" />
                      <el-option label="日文" value="日文" />
                      <el-option label="韩文" value="韩文" />
                      <el-option label="法文" value="法文" />
                      <el-option label="德文" value="德文" />
                      <el-option label="西班牙文" value="西班牙文" />
                      <el-option label="俄文" value="俄文" />
                    </el-select>

                    <el-input
                      v-model="currentMessage"
                      type="textarea"
                      :autosize="{ minRows: 1, maxRows: 3 }"
                      :placeholder="getInputPlaceholder()"
                      class="chat-input"
                      @keyup.enter.exact.prevent="sendMessage"
                      @focus="handleInputFocus"
                      :disabled="
                        isStreaming ||
                        (!isAIWritingMode &&
                          !isAITranslateMode &&
                          !isAISummaryMode &&
                          !isAIReviewMode &&
                          !isAIQuestionMode &&
                          !selectedInfo)
                      "
                    />

                    <!-- AI写作模式文档上传按钮 -->
                    <el-upload
                      v-if="isAIWritingMode"
                      ref="documentUploadRef"
                      class="document-upload-btn"
                      :show-file-list="false"
                      :before-upload="handleDocumentUpload"
                      :disabled="isStreaming || isUploadingDocument"
                      accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
                    >
                      <el-button
                        text
                        class="voice-btn"
                        :disabled="isStreaming || isUploadingDocument"
                        :loading="isUploadingDocument"
                        :title="uploadedDocumentName ? '重新上传文档' : '上传文档'"
                      >
                        <el-icon v-if="!isUploadingDocument">
                          <Document v-if="isAIWritingMode" />
                          <DocumentAdd v-else />
                        </el-icon>
                      </el-button>
                    </el-upload>

                    <!-- AI翻译模式文档上传按钮 -->
                    <el-upload
                      v-if="isAITranslateMode"
                      ref="translateDocumentUploadRef"
                      class="document-upload-btn"
                      :show-file-list="false"
                      :before-upload="handleTranslateDocumentUpload"
                      :disabled="isStreaming || isUploadingTranslateDocument"
                      accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
                    >
                      <el-button
                        text
                        class="voice-btn"
                        :disabled="isStreaming || isUploadingTranslateDocument"
                        :loading="isUploadingTranslateDocument"
                        :title="translateDocumentName ? '重新上传翻译文档' : '上传文档进行翻译'"
                      >
                        <el-icon v-if="!isUploadingTranslateDocument">
                          <Document />
                        </el-icon>
                      </el-button>
                    </el-upload>

                    <!-- AI摘要模式文档上传按钮 -->
                    <el-upload
                      v-if="isAISummaryMode"
                      ref="summaryDocumentUploadRef"
                      class="document-upload-btn"
                      :show-file-list="false"
                      :before-upload="handleSummaryDocumentUpload"
                      :disabled="isStreaming || isUploadingSummaryDocument"
                      accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"
                    >
                      <el-button
                        text
                        class="voice-btn"
                        :disabled="isStreaming || isUploadingSummaryDocument"
                        :loading="isUploadingSummaryDocument"
                        :title="summaryDocumentName ? '重新上传摘要文档' : '上传文档进行摘要'"
                      >
                        <el-icon v-if="!isUploadingSummaryDocument">
                          <Document />
                        </el-icon>
                      </el-button>
                    </el-upload>

                    <!-- AI综述模式文档上传按钮-->
                    <!--                    <el-upload-->
                    <!--                      v-if="isAIReviewMode && !reviewDocumentName"-->
                    <!--                      ref="reviewDocumentUploadRef"-->
                    <!--                      class="document-upload-btn"-->
                    <!--                      :show-file-list="false"-->
                    <!--                      :before-upload="handleReviewDocumentUpload"-->
                    <!--                      :disabled="isStreaming || isUploadingReviewDocument"-->
                    <!--                      accept=".pdf,.doc,.docx,.txt,.xls,.xlsx"-->
                    <!--                    >-->
                    <!--                      <el-button-->
                    <!--                        text-->
                    <!--                        class="voice-btn"-->
                    <!--                        :disabled="isStreaming || isUploadingReviewDocument"-->
                    <!--                        :loading="isUploadingReviewDocument"-->
                    <!--                        :title="reviewDocumentName ? '重新上传综述文档' : '上传文档进行综述'"-->
                    <!--                      >-->
                    <!--                        <el-icon v-if="!isUploadingReviewDocument">-->
                    <!--                          <Document />-->
                    <!--                        </el-icon>-->
                    <!--                      </el-button>-->
                    <!--                    </el-upload>-->

                    <!-- AI问数模式文档上传按钮-->
                    <el-upload
                      v-if="isAIQuestionMode && !questionDocumentName"
                      ref="questionDocumentUploadRef"
                      class="document-upload-btn"
                      :show-file-list="false"
                      :before-upload="handleQuestionDocumentUpload"
                      :disabled="isStreaming || isUploadingQuestionDocument"
                      accept=".xls,.xlsx"
                    >
                      <el-button
                        text
                        class="voice-btn"
                        :disabled="isStreaming || isUploadingQuestionDocument"
                        :loading="isUploadingQuestionDocument"
                        :title="questionDocumentName ? '重新上传综述文档' : '上传文档进行综述'"
                      >
                        <el-icon v-if="!isUploadingQuestionDocument">
                          <Document />
                        </el-icon>
                      </el-button>
                    </el-upload>

                    <!-- 语音录制按钮 -->
                    <el-button
                      text
                      class="voice-btn"
                      @click="startRecording"
                      v-if="
                        recorderStatus === 'STOP' &&
                        !isAIWritingMode &&
                        !isAITranslateMode &&
                        !isAISummaryMode &&
                        !isAIReviewMode &&
                        !isAIQuestionMode
                      "
                      :disabled="isStreaming || !selectedInfo || !sttModelEnabled"
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
                      :disabled="
                        isStreaming || !selectedInfo || !sttModelEnabled || isUploadingAudio
                      "
                      accept="audio/*"
                      v-if="
                        recorderStatus === 'STOP' &&
                        !isAIWritingMode &&
                        !isAITranslateMode &&
                        !isAISummaryMode &&
                        !isAIReviewMode &&
                        !isAIQuestionMode
                      "
                    >
                      <el-button
                        text
                        class="voice-btn"
                        :disabled="
                          isStreaming || !selectedInfo || !sttModelEnabled || isUploadingAudio
                        "
                        :loading="isUploadingAudio"
                      >
                        <el-icon v-if="!isUploadingAudio">
                          <UploadFilled />
                        </el-icon>
                      </el-button>
                    </el-upload>

                    <!-- 录音状态显示 -->
                    <div
                      v-else-if="
                        recorderStatus !== 'STOP' &&
                        !isAIWritingMode &&
                        !isAITranslateMode &&
                        !isAISummaryMode
                      "
                      class="voice-recording flex align-center"
                    >
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
                      v-if="!isStreaming"
                      :disabled="
                        (!currentMessage.trim() &&
                          !uploadedDocumentContent &&
                          !translateDocumentContent &&
                          !summaryDocumentContent &&
                          !questionDocumentContent &&
                          !reviewDocumentContent) ||
                        isStreaming ||
                        (!isAIWritingMode &&
                          !isAITranslateMode &&
                          !isAISummaryMode &&
                          !isAIReviewMode &&
                          !isAIQuestionMode &&
                          !selectedInfo)
                      "
                    >
                      发送
                    </el-button>
                    <el-button
                      type="danger"
                      class="send-btn"
                      @click="
                        () => {
                          isStreaming = false
                        }
                      "
                      v-else
                    >
                      停止
                    </el-button>
                  </div>
                </div>
              </div>

              <!-- AI功能按钮区域 -->
              <div class="ai-buttons-container">
                <div
                  class="ai-button"
                  :class="{ active: isAIWritingMode }"
                  @click="handleAIWriting"
                >
                  <el-icon class="ai-icon">
                    <Edit />
                  </el-icon>
                  <span class="ai-text">AI写作</span>
                </div>
                <div
                  class="ai-button"
                  :class="{ active: isAITranslateMode }"
                  @click="handleAITranslate"
                >
                  <el-icon class="ai-icon">
                    <Connection />
                  </el-icon>
                  <span class="ai-text">AI翻译</span>
                </div>
                <div
                  class="ai-button"
                  :class="{ active: isAISummaryMode }"
                  @click="handleAISummary"
                >
                  <el-icon class="ai-icon">
                    <Document />
                  </el-icon>
                  <span class="ai-text">AI摘要</span>
                </div>
                <div class="ai-button" :class="{ active: isAIReviewMode }" @click="handleAIReview">
                  <el-icon class="ai-icon">
                    <Collection />
                  </el-icon>
                  <span class="ai-text">AI综述</span>
                </div>
                <div
                  class="ai-button"
                  :class="{ active: isAIQuestionMode }"
                  @click="handleAIQuestion"
                >
                  <el-icon class="ai-icon">
                    <DataLine />
                  </el-icon>
                  <span class="ai-text">AI问数</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建知识库对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建知识库" width="500px">
      <el-form :model="newKB" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="newKB.name" placeholder="请输入知识库名称" />
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
      :before-close="() => (showRenameDialog = false)"
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
          <el-button type="primary" @click="confirmRename" :disabled="!renameForm.name.trim()">
            确认重命名
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, type Ref, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import useStore from '@/stores'
import {
  ArrowDown,
  Check,
  ChatLineRound,
  Close,
  Collection,
  Connection,
  Delete,
  Document,
  DocumentAdd,
  DocumentCopy,
  Edit,
  EditPen,
  Folder,
  FolderRemove,
  Microphone,
  MoreFilled,
  Plus,
  Refresh,
  Setting,
  Share,
  Sort,
  Timer,
  UploadFilled,
  View,
  Warning,
  DataLine
} from '@element-plus/icons-vue'
import datasetApi from '@/api/dataset'
import documentApi from '@/api/document'
import modelApi, { postModelChat, postModelChatStream } from '@/api/model'
import DocumentManagement from './components/DocumentManagement.vue'
import ShareSettings from './components/ShareSettings.vue'
import DocumentParagraphsDialog from './components/DocumentParagraphsDialog.vue'
import Recorder from 'recorder-core'
import 'recorder-core/src/engine/mp3'
import 'recorder-core/src/engine/mp3-engine'
import { MsgAlert } from '@/utils/message'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

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
  role: string // 'user' | 'assistant' | 'system'
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
  suggestions?: string[] // 引导式问答的建议问题列表
}

interface KBForm {
  name: string
  description?: string // 描述字段改为可选
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

// AI写作模式状态
const isAIWritingMode = ref(false)

// AI写作模式文档上传相关状态
const uploadedDocumentContent = ref('')
const uploadedDocumentName = ref('')
const isUploadingDocument = ref(false)

// AI翻译模式相关状态
const isAITranslateMode = ref(false)
const targetLanguage = ref('英文')
const translateDocumentContent = ref('')
const translateDocumentName = ref('')
const isUploadingTranslateDocument = ref(false)
const translateDocumentUploadRef = ref<any>(null)

// AI摘要模式相关状态
const isAISummaryMode = ref(false)
const summaryLanguage = ref('中文')
const summaryDocumentContent = ref('')
const summaryDocumentName = ref('')
const isUploadingSummaryDocument = ref(false)
const summaryDocumentUploadRef = ref<any>(null)
const documentUploadRef = ref<any>(null)

// AI综述模式
const isAIReviewMode = ref(false)
const isUploadingReviewDocument = ref(false)
const reviewDocumentContent = ref('')
const reviewDocumentName = ref('')
const reviewDocumentUploadRef = ref<any>(null)

// AI问数模式
const isAIQuestionMode = ref(false)
const isUploadingQuestionDocument = ref(false)
const questionDocumentContent = ref('')
const questionDocumentName = ref('')
const questionDocumentUploadRef = ref<any>(null)

// 重命名相关状态
const showRenameDialog = ref(false)
const renameForm = ref({
  id: '',
  name: '',
  oldName: '' // 保存原始名称，用于日志和验证
})
const messagesContainer = ref<HTMLElement | null>(null)
const isUserAtBottom = ref(true) // 跟踪用户是否在底部，默认在底部
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
const { user } = useStore()
const userRole = computed(() => user.getRole())
const isAdmin = computed(() => userRole.value === 'ADMIN')

// 当前选中的文档和知识库信息
const selectedInfo = computed(() => {
  const selectedDocuments = getSelectedDocuments()
  const selectedDatasets = getSelectedDatasets()

  if (selectedDocuments.length > 0) {
    return {
      type: 'documents',
      count: selectedDocuments.length,
      items: selectedDocuments.map((doc) => doc.label)
    }
  } else if (selectedDatasets.length > 0) {
    return {
      type: 'datasets',
      count: selectedDatasets.length,
      items: selectedDatasets.map((dataset) => dataset.label)
    }
  }
  return null
})

// 原有的知识库数据存储
const organizationKBs = ref<any[]>([])
const sharedKBs = ref<any[]>([])
const personalKBs = ref<any[]>([])

// 排序相关
const personalKBSortType = ref<'time' | 'name'>('time') // 默认按时间排序（创建时间倒排）
const organizationKBSortType = ref<'time' | 'name'>('time') // 机构知识库排序类型
const sharedKBSortType = ref<'time' | 'name'>('time') // 共享知识库排序类型

// 计算属性：根据搜索文本过滤树形数据
const filteredTreeData = computed(() => {
  if (!searchText.value.trim()) {
    return treeData.value
  }

  const searchLower = searchText.value.toLowerCase()

  // 递归过滤树形数据
  const filterTree = (nodes: TreeNode[]): TreeNode[] => {
    return nodes
      .map((node) => {
        // 检查当前节点是否匹配
        const labelMatch = node.label?.toLowerCase().includes(searchLower)

        // 递归过滤子节点
        const filteredChildren = node.children ? filterTree(node.children) : []

        // 如果当前节点匹配或有子节点匹配，则保留该节点
        if (labelMatch || filteredChildren.length > 0) {
          return {
            ...node,
            children: filteredChildren
          }
        }

        return null
      })
      .filter((node) => node !== null) as TreeNode[]
  }

  return filterTree(treeData.value)
})

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
      const cachedModel = list.find((model) => model.id === cached)

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
    const chatModels = list.filter((model) => isChatModel(model))

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

    console.log('模型列表：', res)
    // 过滤出支持对话的模型
    availableModels.value = list.filter((model) => isChatModel(model))

    // 如果当前没有选择模型，自动选择第一个
    if (!selectedModelId.value && availableModels.value.length > 0) {
      selectedModelId.value = availableModels.value[0].id
      // 更新缓存
      localStorage.setItem('user_knowledge_default_model_id', selectedModelId.value)
    }

    // 如果当前选择的模型不在可用列表中，重新选择
    if (
      selectedModelId.value &&
      !availableModels.value.find((m) => m.id === selectedModelId.value)
    ) {
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
    const sttModels = list.filter((model) => model.model_type === 'STT')

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

  const selectedModel = availableModels.value.find((m) => m.id === modelId)
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
  if (isAIWritingMode.value) {
    if (uploadedDocumentName.value) {
      return '请输入写作主题或上传文档，AI将为您提供论文写作、申报书写作、论文续写、文字润色等服务。'
    }
    return '请输入写作主题或上传文档，AI将为您提供论文写作、申报书写作、论文续写、文字润色等服务。'
  }
  if (isAITranslateMode.value) {
    if (translateDocumentName.value) {
      return `点击发送开始翻译文档，或输入附加说明...`
    }
    return `请输入内容或上传文档，AI将为您翻译成${targetLanguage.value}。`
  }
  if (isAISummaryMode.value) {
    if (summaryDocumentName.value) {
      return '请输入内容或上传文档，AI将为您提炼要点或生成中英文摘要。'
    }
    return '请输入内容或上传文档，AI将为您提炼要点或生成中英文摘要。'
  }
  if (isAIReviewMode.value) {
    if (reviewDocumentName.value) {
      return '请勾选知识库或上传文档，AI将为您生成文献综述。'
    }
    return '请勾选知识库或上传文档，AI将为您生成文献综述。'
  }
  if (isAIQuestionMode.value) {
    if (questionDocumentName.value) {
      return '请上传Excel文档或输入数据，AI将为您提供数据解读与可视化图表。'
    }
    return '请上传Excel文档或输入数据，AI将为您提供数据解读与可视化图表。'
  }
  if (!selectedInfo.value) {
    return '请先勾选知识库或文档，再与AI进行对话。'
  }
  return '请输入您的问题...'
}

// 获取模型类型对应的标签颜色
const getModelTypeColor = (modelType: string) => {
  const typeMap: Record<string, string> = {
    LLM: 'primary',
    CHAT: 'success',
    LLM_CHAT: 'warning'
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

// 处理建议问题点击
const handleSuggestionClick = async (suggestion: string) => {
  // 将建议的问题设置为当前消息
  currentMessage.value = suggestion
  // 发送消息
  await sendMessage()
}

// 新聊天功能
const newChat = () => {
  // 清空对话消息
  chatMessages.value = []
  // 重置流式输出状态
  isStreaming.value = false
  // 清空当前输入消息
  currentMessage.value = ''
  // 清空分段展开状态
  expandedParagraphs.value.clear()
  // 取消所有选中的文档和知识库
  if (treeRef.value) {
    treeRef.value.setCheckedKeys([])
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
    categories: 0, // 一级目录数量
    datasets: 0, // 知识库数量
    documents: 0, // 文档数量
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
  const { action, data } = command

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

// 按名称排序函数（支持中英文混合）
const sortByName = (a: string, b: string): number => {
  // 获取字符类型优先级：数字(0) < 英文大写(A-Z, 1) < 英文小写(a-z, 2) < 中文(3)
  const getCharPriority = (char: string): number => {
    const code = char.charCodeAt(0)
    if (code >= 48 && code <= 57) return 0 // 数字 0-9
    if (code >= 65 && code <= 90) return 1 // 大写 A-Z
    if (code >= 97 && code <= 122) return 2 // 小写 a-z
    if (/[\u4e00-\u9fa5]/.test(char)) return 3 // 中文
    return 4 // 其他字符
  }

  const lenA = a.length
  const lenB = b.length
  const minLen = Math.min(lenA, lenB)

  // 逐字符比较
  for (let i = 0; i < minLen; i++) {
    const charA = a[i]
    const charB = b[i]
    const priorityA = getCharPriority(charA)
    const priorityB = getCharPriority(charB)

    // 类型不同，按类型优先级排序
    if (priorityA !== priorityB) {
      return priorityA - priorityB
    }

    // 类型相同，按字符ASCII值排序
    if (charA !== charB) {
      if (priorityA === 3) {
        // 中文字符使用拼音排序
        return charA.localeCompare(charB, 'zh-CN')
      }
      return charA.charCodeAt(0) - charB.charCodeAt(0)
    }
  }

  // 前面的字符都相同，比较长度
  return lenA - lenB
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

    // 复制数组并深拷贝每个对象，确保使用最新数据
    let sortedKBs = personalKBs.value.map((kb) => ({
      ...kb,
      description: kb.description,
      desc: kb.desc
    }))

    // 调试：打印排序前的数据，确认更新是否生效
    console.log(
      '排序前的knowledge bases:',
      sortedKBs.map((kb) => ({
        id: kb.id,
        name: kb.name,
        desc: kb.desc,
        description: kb.description
      }))
    )

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
        return sortByName(a.name || '', b.name || '')
      })
    }

    // 将排序后的数组直接用于更新树，不修改personalKBs的引用
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
        return sortByName(a.name || '', b.name || '')
      })
    }

    // 更新排序后的数据
    organizationKBs.value = sortedKBs
    await updateTreeData('org', sortedKBs)

    console.log(
      `机构知识库已按${organizationKBSortType.value === 'time' ? '创建时间' : '名称'}排序`
    )
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
        return sortByName(a.name || '', b.name || '')
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
  const { action, data } = command

  try {
    switch (action) {
      case 'rename':
        const targetId = data.datasetId || data.id

        renameForm.value = {
          id: targetId,
          name: data.label,
          oldName: data.label // 保存原始名称
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
        await ElMessageBox.confirm(`确定要退出共享知识库"${data.label}"吗？`, '退出共享确认', {
          confirmButtonText: '确定退出',
          cancelButtonText: '取消',
          type: 'warning'
        })

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

        await ElMessageBox.confirm(`确定要将知识库"${data.label}"移出机构吗？`, '移出机构确认', {
          confirmButtonText: '确定移出',
          cancelButtonText: '取消',
          type: 'warning'
        })

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
    const page = { current_page: 1, page_size: 100 }
    const response = await datasetApi.getOrganizationDataset(page, {})

    console.log('机构知识库API响应:', response)

    if (response.data) {
      const orgKBsList = response.data.records || []
      console.log(
        '获取到的机构知识库列表:',
        orgKBsList.map((kb: any) => ({
          id: kb.id,
          name: kb.name,
          create_time: kb.create_time,
          creator: kb.user?.username || '未知'
        }))
      )

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
    const page = { current_page: 1, page_size: 100 }
    const response = await datasetApi.getSharedToMeDataset(page, {})

    console.log('共享知识库API响应:', response)

    if (response.data) {
      const sharedKBsList = response.data.records || []
      console.log(
        '获取到的共享知识库列表:',
        sharedKBsList.map((kb: any) => ({
          id: kb.id,
          name: kb.name,
          create_time: kb.create_time,
          creator: kb.user?.username || '未知',
          shared_user_count: kb.shared_user_count || 0,
          permission: kb.permission, // 添加权限信息
          shared_with_type: kb.shared_with_type,
          team_permission: kb.team_permission
        }))
      )

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
    const page = { current_page: 1, page_size: 100 }
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
  const categoryIndex = treeData.value.findIndex((item) => item.id === categoryId)
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
      description: dataset.description || dataset.desc,
      documentCount: dataset.document_count || 0,
      permission: dataset.permission, // 添加权限信息
      shared_with_type: dataset.shared_with_type,
      team_permission: dataset.team_permission,
      children: [] // 先设置为空数组，稍后加载文档
    }

    // 立即加载该知识库的文档
    try {
      const docResponse = await documentApi.getAllDocument(dataset.id)
      if (docResponse.data && docResponse.data.length > 0) {
        // 只显示启用状态的文档 (is_active 为 true 的文档)
        datasetNode.children = docResponse.data
          .filter((doc: any) => doc.is_active !== false)
          .map((doc: any) => ({
            id: `doc_${doc.id}`,
            label: doc.name,
            level: 3,
            type: 'document',
            documentId: doc.id,
            datasetId: dataset.id,
            size: doc.char_length || 0,
            status: doc.status
          }))
        // 更新文档数量为实际过滤后的文档数
        datasetNode.documentCount = datasetNode.children?.length || 0
      } else {
        // 如果没有文档，设置为0
        datasetNode.documentCount = 0
      }
    } catch (error) {
      console.error(`加载知识库 ${dataset.name} 的文档失败:`, error)
      datasetNode.documentCount = 0
    }

    children.push(datasetNode)
  }

  treeData.value[categoryIndex].children = children
}

// 从treeData中查找知识库节点
const findDatasetNode = (datasetId: string): TreeNode | null => {
  const searchInNodes = (nodes: TreeNode[]): TreeNode | null => {
    for (const node of nodes) {
      if (node.datasetId === datasetId && node.type === 'dataset') {
        return node
      }
      if (node.children) {
        const found = searchInNodes(node.children)
        if (found) return found
      }
    }
    return null
  }
  return searchInNodes(treeData.value)
}

// 加载知识库下的文档
const loadDocuments = async (datasetId: string, parentNodeId: string) => {
  try {
    const response = await documentApi.getAllDocument(datasetId)

    if (response.data) {
      // 只显示启用状态的文档 (is_active 为 true 的文档)
      const documents: TreeNode[] = response.data
        .filter((doc: any) => doc.is_active !== false)
        .map((doc: any) => ({
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
        // 同时更新文档数量统计
        node.documentCount = children.length
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

// 基于选中文档进行知识检索
const performKnowledgeSearch = async (query: string) => {
  try {
    const selectedDocuments = getSelectedDocuments()
    const selectedDatasets = getSelectedDatasets()
    let searchResults: any[] = []
    let hasConnectionError = false
    let hasEmbeddingError = false

    // 如果选中了具体文档，优先基于文档进行检索
    if (selectedDocuments.length > 0) {
      console.log('基于选中的文档进行检索:', selectedDocuments)

      // 按知识库分组文档
      const documentsByDataset = new Map<string, TreeNode[]>()
      selectedDocuments.forEach((doc) => {
        if (doc.datasetId) {
          if (!documentsByDataset.has(doc.datasetId)) {
            documentsByDataset.set(doc.datasetId, [])
          }
          documentsByDataset.get(doc.datasetId)!.push(doc)
        }
      })

      // 对每个知识库的选中文档进行检索
      for (const [datasetId, docs] of documentsByDataset) {
        try {
          const searchData = {
            query_text: query,
            top_number: isAIWritingMode.value ? 30 : 10, // AI写作模式取前30条结果，普通模式取前10条结果
            similarity: 0.3, // 相似度阈值设置为0.3，只返回相似度高于0.3的结果
            search_mode: 'blend',
            // 添加文档ID列表，限制检索范围
            document_ids: docs
              .map((doc) => doc.documentId)
              .filter(Boolean)
              .join(',')
          }

          // 从treeData中查找知识库节点以获取正确的知识库名称
          const datasetNode = findDatasetNode(datasetId)
          const datasetName = datasetNode?.label || '未知知识库'

          const response = await datasetApi.getDatasetHitTest(datasetId, searchData)
          if (response.code === 200 && response.data) {
            const results = response.data.map((item: any) => ({
              ...item,
              dataset_name: datasetName,
              source: item.document_name || item.source
            }))
            searchResults.push(...results)
          } else if (response.code === 500) {
            // 检查是否是嵌入模型连接错误
            if (
              response.message?.includes('Failed to establish a new connection') ||
              response.message?.includes('Connection refused')
            ) {
              hasEmbeddingError = true
            }
          }
        } catch (error: any) {
          console.warn(`文档检索失败:`, error)

          // 检测连接错误类型
          if (
            error.message?.includes('Failed to establish a new connection') ||
            error.message?.includes('Connection refused')
          ) {
            hasEmbeddingError = true
          } else {
            hasConnectionError = true
          }
        }
      }
    }
    // 如果没有选中文档但选中了知识库，则基于整个知识库进行检索
    else if (selectedDatasets.length > 0) {
      console.log('基于选中的知识库进行检索:', selectedDatasets)

      // 对每个选中的知识库进行检索
      for (const dataset of selectedDatasets) {
        if (!dataset.datasetId) continue

        try {
          const searchData = {
            query_text: query,
            top_number: isAIWritingMode.value ? 30 : 10, // AI写作模式取前30条结果，普通模式取前10条
            similarity: 0.3, // 相似度阈值设置为0.3，只返回相似度高于0.3的结果
            search_mode: 'blend'
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
            if (
              response.message?.includes('Failed to establish a new connection') ||
              response.message?.includes('Connection refused')
            ) {
              hasEmbeddingError = true
            }
          }
        } catch (error: any) {
          console.warn(`知识库 ${dataset.label} 检索失败:`, error)

          // 检测连接错误类型
          if (
            error.message?.includes('Failed to establish a new connection') ||
            error.message?.includes('Connection refused')
          ) {
            hasEmbeddingError = true
          } else {
            hasConnectionError = true
          }
        }
      }
    } else {
      console.log('未选中任何文档或知识库')
      return {
        results: [],
        hasEmbeddingError: false,
        hasConnectionError: false
      }
    }

    // 按相似度排序，AI写作模式取前30条，普通模式取前10条
    searchResults.sort((a, b) => {
      const sa = a.similarity ?? a.comprehensive_score ?? 0
      const sb = b.similarity ?? b.comprehensive_score ?? 0
      return sb - sa
    })

    const maxResults = isAIWritingMode.value ? 30 : 10
    return {
      results: searchResults.slice(0, maxResults),
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
  // 在翻译模式或摘要模式下，如果有上传的文档，允许空输入
  const hasTranslateDocument = isAITranslateMode.value && translateDocumentContent.value
  const hasSummaryDocument = isAISummaryMode.value && summaryDocumentContent.value
  const hasReviewDocument = isAIReviewMode.value && reviewDocumentContent.value
  if (
    (!currentMessage.value.trim() &&
      !hasTranslateDocument &&
      !hasSummaryDocument &&
      !hasReviewDocument) ||
    isStreaming.value ||
    !selectedModelId.value
  )
    return

  // 检查是否选中了文档或知识库（AI写作模式、AI翻译模式和AI摘要模式下可以不选择）
  const selectedDocuments = getSelectedDocuments()
  const selectedDatasets = getSelectedDatasets()

  if (
    !isAIWritingMode.value &&
    !isAITranslateMode.value &&
    !isAISummaryMode.value &&
    !isAIReviewMode.value &&
    !isAIQuestionMode.value &&
    selectedDocuments.length === 0 &&
    selectedDatasets.length === 0
  ) {
    ElMessage.warning('请先选择要查询的文档或知识库')
    return
  }

  const userQuestion = currentMessage.value.trim()

  // 保存文档内容，避免后续使用时被清空
  const savedTranslateDocContent = translateDocumentContent.value
  const savedTranslateDocName = translateDocumentName.value
  const savedUploadedDocContent = uploadedDocumentContent.value
  const savedUploadedDocName = uploadedDocumentName.value
  const savedSummaryDocContent = summaryDocumentContent.value
  const savedSummaryDocName = summaryDocumentName.value
  const savedReviewDocContent = reviewDocumentContent.value
  const savedReviewDocName = reviewDocumentName.value
  const savedQuestionDocContent = questionDocumentContent.value
  const savedQuestionDocName = questionDocumentName.value

  // 添加用户消息
  let displayUserMessage = userQuestion
  if (hasTranslateDocument && !userQuestion) {
    displayUserMessage = `翻译文档：${savedTranslateDocName}`
  } else if (hasSummaryDocument && !userQuestion) {
    displayUserMessage = `摘要文档：${summaryDocumentName.value}`
  }

  chatMessages.value.push({
    role: 'user',
    content: displayUserMessage,
    timestamp: new Date()
  })

  console.log('用户消息已添加，当前消息数量:', chatMessages.value.length)
  console.log('hasMessages计算值:', chatMessages.value.length > 0)

  // 清空输入框
  currentMessage.value = ''

  // 如果是翻译模式或摘要模式且有上传的文档，清除文档
  if (hasTranslateDocument) {
    translateDocumentContent.value = ''
    translateDocumentName.value = ''
  }
  if (hasSummaryDocument) {
    summaryDocumentContent.value = ''
    summaryDocumentName.value = ''
  }

  isStreaming.value = true

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    // 使用默认模型ID
    const modelId = selectedModelId.value || (await resolveDefaultModelId())
    if (!modelId) {
      chatMessages.value.push(createAssistantMessage('无法获取可用的对话模型，请联系管理员配置。'))
      return
    }

    // 基于选中知识库进行检索
    const searchResponse = await performKnowledgeSearch(userQuestion)
    const { results: searchResults, hasEmbeddingError, hasConnectionError } = searchResponse
    console.log('知识检索结果:', searchResults)
    // 保存搜索结果，稍后添加到AI回答消息中
    let searchResultsForAI: any[] = []
    if (searchResults && searchResults.length > 0) {
      searchResultsForAI = searchResults.map((result) => ({
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
      context = searchResults
        .map(
          (result, index) => `参考资料${index + 1}：
标题：${result.title || '无标题'}
内容：${result.content}
来源：${result.document_name || result.source}
数据集：${result.dataset_name}`
        )
        .join('\n\n')
    } else {
      context = '未找到与问题相关的知识库内容。'
      contextNote = '\n\n注意：在选中的知识库中未找到相关内容，回答将基于通用知识。'
    }

    console.log('用户输入内容:', userQuestion)
    console.log('知识库检索内容:', context)

    // 根据是否为AI写作模式或AI翻译模式构建不同的系统提示
    let systemPrompt = ''
    let currentIntent: 'writing' | 'polish' | 'expand' | 'chat' | null = null // 用于记录当前意图

    if (isAITranslateMode.value) {
      // AI翻译模式：使用翻译提示词
      console.log('AI翻译模式：开始翻译...')
      console.log('用户输入内容:', userQuestion)
      console.log('目标语言:', targetLanguage.value)

      // 如果有上传的翻译文档，使用文档翻译模式
      if (savedTranslateDocContent) {
        console.log('检测到上传翻译文档:', savedTranslateDocName)
        systemPrompt = getTranslatePrompt(
          targetLanguage.value,
          '',
          savedTranslateDocContent,
          savedTranslateDocName,
          userQuestion // 将用户输入作为附加说明
        )
      } else {
        // 普通文本翻译模式
        systemPrompt = getTranslatePrompt(targetLanguage.value, userQuestion)
      }
    } else if (isAIWritingMode.value) {
      // AI写作模式：先进行意图识别
      console.log('AI写作模式：开始意图识别...')
      console.log('用户输入问题:', userQuestion)

      // 调用意图识别函数
      const intent = await detectWritingIntent(userQuestion, modelId)
      currentIntent = intent // 保存意图以便后续使用

      // 打印意图识别结果
      console.log('=== 意图识别结果 ===')
      console.log('识别到的意图:', intent)
      const intentDescMap = {
        writing: '写作模式（从零创作）',
        polish: '润写模式（优化润色）',
        expand: '扩写模式（扩充内容）',
        chat: '对话模式（普通交流）'
      }
      console.log('意图说明:', intentDescMap[intent] || intent)
      console.log('===================')

      // 如果识别为对话模式，使用普通对话的提示词
      if (intent === 'chat') {
        console.log('检测到普通对话意图，切换为对话模式')
        systemPrompt =
          hasEmbeddingError || hasConnectionError
            ? `你是一个专业友好的AI助手。由于技术问题，当前无法检索知识库内容，请基于你的通用知识回答用户问题。请诚实告知用户当前情况，并尽力提供有帮助的一般性回答。`
            : `你是一个专业友好的AI助手。请根据以下检索到的知识库内容回答用户问题。如果检索内容不足以回答问题，请诚实说明，并提供一般性建议。

检索到的相关内容：
${context}

请基于上述内容回答用户问题，保持专业、准确和有帮助的态度。${contextNote}`
      } else {
        // 如果有上传的文档，添加到知识片段中
        let documentContext = ''
        if (savedUploadedDocContent) {
          documentContext = `\n\n上传文档内容（${savedUploadedDocName}）：
${savedUploadedDocContent}`
          console.log('检测到上传文档:', savedUploadedDocName)
        }

        // 根据识别的意图获取对应的提示词（writing/polish/expand）
        systemPrompt = getPromptByIntent(
          intent as 'writing' | 'polish' | 'expand',
          userQuestion,
          context,
          documentContext,
          contextNote
        )
      }
    } else if (isAISummaryMode.value) {
      // AI摘要模式：使用摘要提示词
      console.log('AI摘要模式：开始中英文摘要生成...')
      console.log('用户输入内容:', userQuestion)

      // 如果有上传的摘要文档，使用文档摘要模式
      if (savedSummaryDocContent) {
        console.log('检测到上传摘要文档:', savedSummaryDocName)
        systemPrompt = getSummaryPrompt(
          '中英文', // 固定为中英文摘要
          userQuestion,
          savedSummaryDocContent,
          savedSummaryDocName,
          '',
          '',
          chatMessages.value.slice(-10) // 传入对话历史记录
        )
      } else {
        // 基于知识库检索结果的摘要模式
        systemPrompt = getSummaryPrompt(
          '中英文', // 固定为中英文摘要
          userQuestion,
          '',
          '',
          context,
          contextNote,
          chatMessages.value.slice(-10) // 传入对话历史记录
        )
      }
    } else if (isAIReviewMode.value) {
      // AI代码审查模式的系统提示
      console.log('AI综述模式：开始文献综述...')
      console.log('用户输入内容:', userQuestion)
      if (savedReviewDocContent) {
        console.log('检测到上传综述文档:', savedReviewDocName)
        systemPrompt = getReviewPrompt(userQuestion, savedReviewDocContent, savedReviewDocName)
      } else {
        systemPrompt = getReviewPrompt(userQuestion, '', '', context, contextNote)
      }
    } else if (isAIQuestionMode.value) {
      // AI问答模式的系统提示
      console.log('AI问答模式：开始文档问答...')
      console.log('用户输入内容:', userQuestion)
      if (savedQuestionDocContent) {
        console.log('检测到上传问答文档:', savedQuestionDocName)
        systemPrompt = getQuestionPrompt(
          userQuestion,
          savedQuestionDocContent,
          savedQuestionDocName
        )
      } else {
        systemPrompt = getQuestionPrompt(userQuestion, '', '', context, contextNote)
      }
    } else {
      // 普通对话模式的系统提示（带引导式问答）
      systemPrompt =
        hasEmbeddingError || hasConnectionError
          ? `你是一名知识库问答专家。
你的任务是基于知识库检索结果与通用知识，为用户提供准确、全面、结构化的回答。
工作原则
准确性优先：所有信息必须真实、可靠、可验证。
完整性保证：回答应覆盖问题的核心与关键方面。
逻辑清晰：回答结构有条理，层次分明。
客观中立：避免主观臆断和情绪化表达。
时效性：优先采用最新可用信息。
工作流程
理解用户问题的意图与背景。
检索并分析相关知识库内容。
整合检索结果与通用知识。
输出条理清晰、重点突出的答案。
输出要求
内容准确、清晰、专业、易懂；
采用分点或分层结构组织；
不包含未经验证、敏感或主观内容。由于技术问题，当前无法检索知识库内容，请基于你的通用知识回答用户问题。请诚实告知用户当前情况，并尽力提供有帮助的一般性回答。

用户提问：${userQuestion}

请生成一个 JSON，对象包含两个字段：
1. answer：直接回答用户问题。
2. suggestions：3~5个可能的后续问题，引导用户继续提问。

例子：
{
  "answer": "今天上海天气晴，最高26℃，最低18℃。",
  "suggestions": ["上海今天会下雨吗？", "明天上海天气怎么样？", "上海空气质量好吗？"]
}

请直接输出JSON，不要包含其他说明文字。`
          : `你是一个专业的知识库助手。请根据以下检索到的知识库内容回答用户问题。如果检索内容不足以回答问题，请诚实说明，并提供一般性建议。

检索到的相关内容：
${context}

用户提问：${userQuestion}

请生成一个 JSON，对象包含两个字段：
1. answer：直接回答用户问题（基于上述检索到的相关内容）。
2. suggestions：3~5个可能的后续问题，引导用户继续提问（问题应该与当前回答和知识库内容相关）。

例子：
{
  "answer": "今天上海天气晴，最高26℃，最低18℃。",
  "suggestions": ["上海今天会下雨吗？", "明天上海天气怎么样？", "上海空气质量好吗？"]
}

请直接输出JSON，不要包含其他说明文字。${contextNote}`
    }

    // AI翻译模式、AI摘要模式，以及AI写作模式下的扩写/润写模式不使用对话历史上下文，每次都是独立的任务
    // 注意：AI摘要模式的历史记录通过 systemPrompt 传入（在 getSummaryPrompt 中格式化），不在 messages 数组中
    // 判断是否需要保留对话历史（在 messages 数组中）
    const shouldSkipHistory =
      isAITranslateMode.value ||
      isAISummaryMode.value ||
      currentIntent === 'polish' ||
      currentIntent === 'expand'

    if (shouldSkipHistory) {
      console.log('当前模式不保留对话历史，模式:', {
        isAITranslateMode: isAITranslateMode.value,
        isAISummaryMode: isAISummaryMode.value,
        currentIntent: currentIntent
      })
    }

    const messages = [
      {
        role: 'system',
        content: systemPrompt
      },
      ...(shouldSkipHistory ? [] : chatMessages.value.slice(-10)), // 根据需要决定是否保留对话历史
      { role: 'user', content: userQuestion }
    ]

    // 调用模型API进行流式对话
    try {
      const resp = await postModelChatStream(modelId, { messages })

      if (resp?.body && typeof resp.body.getReader === 'function') {
        const reader = resp.body.getReader()
        const decoder = new TextDecoder('utf-8')
        let currentAssistantMessage = ''

        while (isStreaming.value) {
          const { value, done } = await reader.read()
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

        // 流式输出结束后处理
        const lastMessage = chatMessages.value[chatMessages.value.length - 1]
        console.log('流式输出结束，当前AI消息内容:', currentAssistantMessage)

        // 判断是否为普通知识库问答模式（排除所有特殊模式）
        const isNormalKnowledgeBaseMode =
          !isAITranslateMode.value &&
          !isAIWritingMode.value &&
          !isAISummaryMode.value &&
          !isAIReviewMode.value &&
          !isAIQuestionMode.value

        if (lastMessage && lastMessage.role === 'assistant' && isNormalKnowledgeBaseMode) {
          // 尝试解析JSON格式的响应（引导式问答）
          try {
            // 清理消息内容，尝试提取JSON
            let jsonContent = currentAssistantMessage.trim()

            // 如果消息以```json开头，提取JSON部分
            if (jsonContent.includes('```json')) {
              const jsonMatch = jsonContent.match(/```json\s*([\s\S]*?)\s*```/)
              if (jsonMatch) {
                jsonContent = jsonMatch[1]
              }
            } else if (jsonContent.includes('```')) {
              // 如果包含```但不包含json，尝试提取第一个代码块
              const codeMatch = jsonContent.match(/```\s*([\s\S]*?)\s*```/)
              if (codeMatch) {
                jsonContent = codeMatch[1]
              }
            }

            // 尝试解析JSON
            const parsed = JSON.parse(jsonContent)

            if (parsed && typeof parsed === 'object') {
              // 提取answer和suggestions
              const answer = parsed.answer || currentAssistantMessage
              const suggestions = Array.isArray(parsed.suggestions) ? parsed.suggestions : []

              // 更新消息内容为answer，添加suggestions
              lastMessage.content = transformWhenAltIsQuickChart(answer)
              lastMessage.suggestions = suggestions

              console.log('成功解析引导式问答JSON:', { answer, suggestions })
            } else {
              // 如果不是有效的JSON结构，使用原始内容
              lastMessage.content = transformWhenAltIsQuickChart(currentAssistantMessage)
            }
          } catch (e) {
            // JSON解析失败，使用原始内容（可能是模型没有严格按照JSON格式输出）
            console.warn('解析引导式问答JSON失败，使用原始内容:', e)
            lastMessage.content = transformWhenAltIsQuickChart(currentAssistantMessage)
          }
        } else if (lastMessage && lastMessage.role === 'assistant') {
          // 其他模式直接使用原始内容
          lastMessage.content = transformWhenAltIsQuickChart(currentAssistantMessage)
        }

        // 如果没有接收到内容，显示默认错误消息
        if (!currentAssistantMessage) {
          if (!isStreaming.value) {
            chatMessages.value.push(
              createAssistantMessage(
                '回答已中断。',
                searchResultsForAI.length > 0 ? searchResultsForAI : undefined
              )
            )
          } else {
            chatMessages.value.push(
              createAssistantMessage(
                '抱歉，模型服务暂时不可用，请稍后重试。',
                searchResultsForAI.length > 0 ? searchResultsForAI : undefined
              )
            )
          }
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
        const errorText = (await resp?.text?.()) || ''
        if (errorText.includes('该模型不支持直接对话调用')) {
          chatMessages.value.push(
            createAssistantMessage(
              '抱歉，当前选择的模型不支持对话功能。请联系管理员配置支持对话的模型（如：GPT、Claude、通义千问等）。',
              searchResultsForAI.length > 0 ? searchResultsForAI : undefined
            )
          )
        } else {
          chatMessages.value.push(
            createAssistantMessage(
              '抱歉，模型服务暂时不可用，请稍后重试。',
              searchResultsForAI.length > 0 ? searchResultsForAI : undefined
            )
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
        createAssistantMessage(
          errorMessage,
          searchResultsForAI.length > 0 ? searchResultsForAI : undefined
        )
      )
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    chatMessages.value.push(createAssistantMessage('抱歉，处理您的问题时出现错误，请稍后重试。'))
  } finally {
    isStreaming.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 检查用户是否在底部
const handleScroll = () => {
  if (messagesContainer.value) {
    const container = messagesContainer.value as HTMLElement
    const scrollTop = container.scrollTop
    const scrollHeight = container.scrollHeight
    const clientHeight = container.clientHeight
    // 允许5px的误差，判断是否在底部
    isUserAtBottom.value = scrollTop + clientHeight >= scrollHeight - 5
  }
}

const scrollToBottom = () => {
  // 只有在用户位于底部时才自动滚动
  if (messagesContainer.value && isUserAtBottom.value) {
    setTimeout(() => {
      const container = messagesContainer.value as HTMLElement
      if (container) {
        container.scrollTop = container.scrollHeight
        // 确保滚动到底部
        container.scrollTo({
          top: container.scrollHeight,
          behavior: 'smooth'
        })
        // 滚动后更新状态
        isUserAtBottom.value = true
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

// 配置 marked 选项
marked.setOptions({
  breaks: true, // 支持 GFM 换行
  gfm: true // 启用 GitHub Flavored Markdown
})

// 配置 marked 的渲染器以支持代码高亮
const renderer = new marked.Renderer()
const originalCodeRenderer = renderer.code.bind(renderer)
renderer.code = function(code: string, language: string | undefined, isEscaped: boolean) {
  if (language && hljs.getLanguage(language)) {
    try {
      const highlighted = hljs.highlight(code, { language }).value
      return `<pre><code class="hljs language-${language}">${highlighted}</code></pre>`
    } catch (err) {
      console.error('代码高亮失败:', err)
    }
  }
  // 自动检测语言
  try {
    const highlighted = hljs.highlightAuto(code).value
    return `<pre><code class="hljs">${highlighted}</code></pre>`
  } catch (err) {
    return originalCodeRenderer(code, language, isEscaped)
  }
}

marked.use({ renderer })

// 格式化消息内容（支持完整的 Markdown 渲染）
const formatMessageContent = (content: string) => {
  if (!content) return ''

  try {
    // 检查是否包含翻译分隔符
    if (content.includes('<SPLIT_HERE>')) {
      // 处理翻译结果：分割直译和意译
      const parts = content.split('<SPLIT_HERE>')
      const literalTranslation = parts[0]?.trim() || ''
      const freeTranslation = parts[1]?.trim() || ''

      // 分别解析两部分的 Markdown
      const literalHtml = marked.parse(literalTranslation) as string
      const freeHtml = marked.parse(freeTranslation) as string

      // 返回带有区分样式的 HTML
      return `
        <div class="translation-result">
          <div class="translation-section literal-translation">
            ${literalHtml}
          </div>
          <div class="translation-divider"></div>
          <div class="translation-section free-translation">
            ${freeHtml}
          </div>
        </div>
      `
    }

    // 普通内容：使用 marked 解析 Markdown
    return marked.parse(content) as string
  } catch (error) {
    console.error('Markdown 解析失败:', error)
    // 降级处理：简单的格式化
    return content
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
  }
}

// 清除模式状态
const switchMode = (mode: Ref<boolean, boolean>) => {
  mode.value = !mode.value

  isAIWritingMode.value = mode === isAIWritingMode ? mode.value : false
  isAITranslateMode.value = mode === isAITranslateMode ? mode.value : false
  isAISummaryMode.value = mode === isAISummaryMode ? mode.value : false
  isAIReviewMode.value = mode === isAIReviewMode ? mode.value : false
  isAIQuestionMode.value = mode === isAIQuestionMode ? mode.value : false

  // 清空所有模式的上传文档内容
  uploadedDocumentContent.value = ''
  uploadedDocumentName.value = ''
  // 清空翻译模式的上传文档
  translateDocumentContent.value = ''
  translateDocumentName.value = ''
  // 清空摘要模式的上传文档
  summaryDocumentContent.value = ''
  summaryDocumentName.value = ''
  // 清空综述模式的上传文档
  reviewDocumentContent.value = ''
  reviewDocumentName.value = ''
  // 清空问数模式的上传文档
  questionDocumentContent.value = ''
  questionDocumentName.value = ''
  // 切换模式时清空输入框内容，避免混淆
  currentMessage.value = ''
}

// AI写作功能
const handleAIWriting = () => {
  switchMode(isAIWritingMode)
  if (isAIWritingMode.value) {
    ElMessage.success('已开启AI写作模式（支持写作、润写、扩写）')
  } else {
    ElMessage.info('已关闭AI写作模式')
    // 关闭AI写作模式时清空已上传的文档
    uploadedDocumentContent.value = ''
    uploadedDocumentName.value = ''
  }
}

// AI翻译模式切换
const handleAITranslate = () => {
  switchMode(isAITranslateMode)

  if (isAITranslateMode.value) {
    ElMessage.success(
      `已开启AI翻译模式（支持文本和文档翻译），当前目标语言：${targetLanguage.value}`
    )
  } else {
    ElMessage.info('已关闭AI翻译模式')
    // 关闭AI翻译模式时清空已上传的文档
    translateDocumentContent.value = ''
    translateDocumentName.value = ''
  }
}

const handleAISummary = () => {
  switchMode(isAISummaryMode)

  if (isAISummaryMode.value) {
    ElMessage.success('已开启AI中英文摘要模式（支持文本和文档摘要）')
  } else {
    ElMessage.info('已关闭AI摘要模式')
    // 关闭AI摘要模式时清空已上传的文档
    summaryDocumentContent.value = ''
    summaryDocumentName.value = ''
  }
}

const handleAIReview = () => {
  switchMode(isAIReviewMode)

  if (isAIReviewMode.value) {
    ElMessage.success('已开启AI综述模式')
  } else {
    ElMessage.info('已关闭AI综述模式')
  }
}

const handleAIQuestion = () => {
  switchMode(isAIQuestionMode)
  if (isAIQuestionMode.value) {
    ElMessage.success('已开启AI问答模式')
  } else {
    ElMessage.info('已关闭AI问答模式')
  }
}

// AI翻译模式文档上传处理
const handleTranslateDocumentUpload = async (file: any) => {
  if (!isAITranslateMode.value) {
    ElMessage.warning('请先开启AI翻译模式')
    return false
  }

  // 验证文件类型
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]

  if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|doc|docx|txt|xls|xlsx)$/i)) {
    ElMessage.error('仅支持上传 PDF、Word、Excel 和 TXT 文档')
    return false
  }

  // 验证文件大小 (10MB)
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }

  try {
    isUploadingTranslateDocument.value = true

    // 创建 FormData
    const formData = new FormData()
    formData.append('file', file)
    formData.append('limit', '100000') // 设置较大的字符限制
    formData.append('with_filter', 'false')

    // 调用文档分段API进行文档识别
    const response = await documentApi.postSplitDocument(formData)

    if (response.code === 200 && response.data) {
      // 提取文档内容
      let documentContent = ''
      if (Array.isArray(response.data) && response.data.length > 0) {
        const allParagraphs: string[] = []

        response.data.forEach((doc: any) => {
          if (Array.isArray(doc.content)) {
            doc.content.forEach((paragraph: any) => {
              if (paragraph.content && typeof paragraph.content === 'string') {
                allParagraphs.push(paragraph.content.trim())
              }
            })
          }
        })

        documentContent = allParagraphs.filter((p) => p).join('\n\n')
      }

      if (documentContent.trim()) {
        translateDocumentContent.value = documentContent
        translateDocumentName.value = file.name
        ElMessage.success(`文档 "${file.name}" 上传成功，准备翻译！`)
      } else {
        ElMessage.error('文档内容为空或无法识别')
      }
    } else {
      ElMessage.error(response.message || '文档识别失败')
    }
  } catch (error: any) {
    console.error('文档上传失败:', error)
    ElMessage.error(error.message || '文档上传失败，请重试')
  } finally {
    isUploadingTranslateDocument.value = false
  }

  return false // 阻止默认上传行为
}

// AI摘要模式文档上传处理
const handleSummaryDocumentUpload = async (file: any) => {
  if (!isAISummaryMode.value) {
    ElMessage.warning('请先开启AI摘要模式')
    return false
  }

  // 验证文件类型
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]

  if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|doc|docx|txt|xls|xlsx)$/i)) {
    ElMessage.error('仅支持上传 PDF、Word、Excel 和 TXT 文档')
    return false
  }

  // 验证文件大小 (10MB)
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }

  try {
    isUploadingSummaryDocument.value = true

    // 创建 FormData
    const formData = new FormData()
    formData.append('file', file)
    formData.append('limit', '100000') // 设置较大的字符限制
    formData.append('with_filter', 'false')

    // 调用文档分段API进行文档识别
    const response = await documentApi.postSplitDocument(formData)

    if (response.code === 200 && response.data) {
      // 提取文档内容
      let documentContent = ''
      if (Array.isArray(response.data) && response.data.length > 0) {
        const allParagraphs: string[] = []

        response.data.forEach((doc: any) => {
          if (Array.isArray(doc.content)) {
            doc.content.forEach((paragraph: any) => {
              if (paragraph.content && typeof paragraph.content === 'string') {
                allParagraphs.push(paragraph.content.trim())
              }
            })
          }
        })

        documentContent = allParagraphs.filter((p) => p).join('\n\n')
      }

      if (documentContent.trim()) {
        summaryDocumentContent.value = documentContent
        summaryDocumentName.value = file.name
        ElMessage.success(`文档 "${file.name}" 上传成功，准备生成中英文摘要！`)
      } else {
        ElMessage.error('文档内容为空或无法识别')
      }
    } else {
      ElMessage.error(response.message || '文档识别失败')
    }
  } catch (error: any) {
    console.error('文档上传失败:', error)
    ElMessage.error(error.message || '文档上传失败，请重试')
  } finally {
    isUploadingSummaryDocument.value = false
  }

  return false // 阻止默认上传行为
}

// AI问数模式文档上传处理
const handleQuestionDocumentUpload = async (file: any) => {
  if (!isAIQuestionMode.value) {
    ElMessage.warning('请先开启AI问答模式')
    return false
  }
  // 验证文件类型，只能上传xls和xlsx文件
  const allowedTypes = [
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]
  if (!allowedTypes.includes(file.type) && !file.name.match(/\.(xls|xlsx)$/i)) {
    ElMessage.error('仅支持上传 Excel 文档（xls 或 xlsx 格式）')
    return false
  }
  // 验证文件大小 (10MB)
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  try {
    isUploadingQuestionDocument.value = true
    // 创建 FormData
    const formData = new FormData()
    formData.append('file', file)
    formData.append('limit', '100000') // 设置较大的字符限制
    formData.append('with_filter', 'false')
    // 调用文档分段API进行文档识别
    const response = await documentApi.postSplitDocument(formData)
    if (response.code === 200 && response.data) {
      // 提取文档内容
      let documentContent = ''
      if (Array.isArray(response.data) && response.data.length > 0) {
        const allParagraphs: string[] = []
        response.data.forEach((doc: any) => {
          if (Array.isArray(doc.content)) {
            doc.content.forEach((paragraph: any) => {
              if (paragraph.content && typeof paragraph.content === 'string') {
                allParagraphs.push(paragraph.content.trim())
              }
            })
          }
        })
        documentContent = allParagraphs.filter((p) => p).join('\n\n')
      }
      if (documentContent.trim()) {
        questionDocumentContent.value = documentContent
        questionDocumentName.value = file.name
        ElMessage.success(`文档 "${file.name}" 上传成功，准备进行问答！`)
      } else {
        ElMessage.error('文档内容为空或无法识别')
      }
    } else {
      ElMessage.error(response.message || '文档识别失败')
    }
  } catch (error: any) {
    console.error('文档上传失败:', error)
    ElMessage.error(error.message || '文档上传失败，请重试')
  } finally {
    isUploadingQuestionDocument.value = false
  }
}

// AI综述模式文档上传处理
const handleReviewDocumentUpload = async (file: any) => {
  if (!isAIReviewMode.value) {
    ElMessage.warning('请先开启AI综述模式')
    return false
  }
  // 验证文件类型
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]
  if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|doc|docx|txt|xls|xlsx)$/i)) {
    ElMessage.error('仅支持上传 PDF、Word、Excel 和 TXT 文档')
    return false
  }
  // 验证文件大小 (10MB)
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  try {
    isUploadingReviewDocument.value = true
    // 创建 FormData
    const formData = new FormData()
    formData.append('file', file)
    formData.append('limit', '100000') // 设置较大的字符限制
    formData.append('with_filter', 'false')
    // 调用文档分段API进行文档识别
    const response = await documentApi.postSplitDocument(formData)
    if (response.code === 200 && response.data) {
      // 提取文档内容
      let documentContent = ''
      if (Array.isArray(response.data) && response.data.length > 0) {
        const allParagraphs: string[] = []
        response.data.forEach((doc: any) => {
          if (Array.isArray(doc.content)) {
            doc.content.forEach((paragraph: any) => {
              if (paragraph.content && typeof paragraph.content === 'string') {
                allParagraphs.push(paragraph.content.trim())
              }
            })
          }
        })
        documentContent = allParagraphs.filter((p) => p).join('\n\n')
      }
      if (documentContent.trim()) {
        reviewDocumentContent.value = documentContent
        reviewDocumentName.value = file.name
        ElMessage.success(`文档 "${file.name}" 上传成功，准备生成综述！`)
      } else {
        ElMessage.error('文档内容为空或无法识别')
      }
    } else {
      ElMessage.error(response.message || '文档识别失败')
    }
  } catch (error: any) {
    console.error('文档上传失败:', error)
    ElMessage.error(error.message || '文档上传失败，请重试')
  } finally {
    isUploadingReviewDocument.value = false
  }
}

// 移除AI翻译模式已上传的文档
const removeTranslateDocument = () => {
  translateDocumentContent.value = ''
  translateDocumentName.value = ''
  ElMessage.info('已移除上传的翻译文档')
}

// 移除AI摘要模式已上传的文档
const removeSummaryDocument = () => {
  summaryDocumentContent.value = ''
  summaryDocumentName.value = ''
  ElMessage.info('已移除上传的摘要文档')
}

// 移除AI综述模式已上传的文档
const removeReviewDocument = () => {
  reviewDocumentContent.value = ''
  reviewDocumentName.value = ''
  ElMessage.info('已移除上传的综述文档')
}

// AI写作模式文档上传处理
const handleDocumentUpload = async (file: any) => {
  if (!isAIWritingMode.value) {
    ElMessage.warning('请先开启AI写作模式')
    return false
  }

  // 验证文件类型
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]

  if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|doc|docx|txt|xls|xlsx)$/i)) {
    ElMessage.error('仅支持上传 PDF、Word、Excel 和 TXT 文档')
    return false
  }

  // 验证文件大小 (10MB)
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }

  try {
    isUploadingDocument.value = true

    // 创建 FormData
    const formData = new FormData()
    formData.append('file', file)
    formData.append('limit', '100000') // 设置较大的字符限制
    // 不添加 patterns 参数，或者添加默认的分段标识
    formData.append('with_filter', 'false')

    // 调用文档分段API进行文档识别
    const response = await documentApi.postSplitDocument(formData)

    if (response.code === 200 && response.data) {
      // 提取文档内容
      let documentContent = ''
      if (Array.isArray(response.data) && response.data.length > 0) {
        // response.data 是一个数组，每个元素包含 name 和 content
        // content 是段落数组，每个段落包含 title 和 content
        const allParagraphs: string[] = []

        response.data.forEach((doc: any) => {
          if (Array.isArray(doc.content)) {
            doc.content.forEach((paragraph: any) => {
              if (paragraph.content && typeof paragraph.content === 'string') {
                allParagraphs.push(paragraph.content.trim())
              }
            })
          }
        })

        documentContent = allParagraphs.filter((p) => p).join('\n\n')
      }

      if (documentContent.trim()) {
        uploadedDocumentContent.value = documentContent
        uploadedDocumentName.value = file.name
        ElMessage.success(`文档 "${file.name}" 上传成功！`)
      } else {
        ElMessage.error('文档内容为空或无法识别')
      }
    } else {
      ElMessage.error(response.message || '文档识别失败')
    }
  } catch (error: any) {
    console.error('文档上传失败:', error)
    ElMessage.error(error.message || '文档上传失败，请重试')
  } finally {
    isUploadingDocument.value = false
  }

  return false // 阻止默认上传行为
}

// 移除已上传的文档
const removeUploadedDocument = () => {
  uploadedDocumentContent.value = ''
  uploadedDocumentName.value = ''
  ElMessage.info('已移除上传的文档')
}
// 移除已上传的文档
const removeQuestionDocument = () => {
  questionDocumentName.value = ''
  questionDocumentContent.value = ''
  ElMessage.info('已移除上传的文档')
}

// AI写作意图识别函数
const detectWritingIntent = async (
  userInput: string,
  modelId: string
): Promise<'writing' | 'polish' | 'expand' | 'chat'> => {
  try {
    console.log('--- 开始意图识别 ---')
    console.log('输入文本长度:', userInput.length, '字')
    console.log('使用模型ID:', modelId)

    const intentPrompt = `你是一个意图识别助手。请判断用户的输入属于以下哪一种意图：
1. 写作（writing）：用户提供主题或大纲，需要从零开始创作一篇文章
2. 润写（polish）：用户提供了已有的文章内容，需要优化语言、修正错误、提升表达质量
3. 扩写（expand）：用户提供了简短的内容或要点，需要在原有基础上扩充内容、增加细节
4. 对话（chat）：用户只是打招呼、闲聊或者问简单的问题，不需要进行写作

判断规则（请严格按照以下规则进行判断）：
- 如果用户输入的是打招呼（如"你好"、"hello"、"hi"）、闲聊或简单问题，判定为"对话"
- 如果用户输入明确包含"扩写"、"扩充"、"展开"、"增加内容"、"详细说明"、"补充"、"丰富"等关键词，或者提供了简短内容且要求增加内容，判定为"扩写"
- 如果用户输入明确包含"润写"、"润色"、"优化"、"改进"、"修改"、"提升"、"完善"等关键词，且提供了完整的文章段落或较长的文本内容（通常超过100字），判定为"润写"
- 如果用户输入的是主题、标题、大纲、具体的写作要求或描述，没有提供完整文章内容，也没有明确要求扩写或润写，判定为"写作"

特别注意：
- "扩写"要求用户提供原始内容并明确要求扩充内容
- "润写"要求用户提供完整文章内容并要求优化
- "写作"是用户只提供主题或大纲，需要从零开始创作
- 优先识别明确的关键词，如"扩写"、"润写"等

用户输入：
${userInput}

请只返回一个词：writing、polish、expand 或 chat`

    const messages = [{ role: 'user', content: intentPrompt }]

    console.log('发送意图识别请求到AI模型...')

    // 调用模型进行意图识别
    const response = await postModelChat(modelId, { messages })

    console.log('收到AI模型响应:', response)

    if (response && response.data && response.data.content) {
      const rawIntent = response.data.content.trim()
      const intent = rawIntent.toLowerCase()

      console.log('AI返回的原始意图:', rawIntent)
      console.log('处理后的意图文本:', intent)

      // 解析意图结果
      let finalIntent: 'writing' | 'polish' | 'expand' | 'chat'
      if (intent.includes('chat')) {
        finalIntent = 'chat'
        console.log('解析结果: 对话模式 (chat)')
      } else if (intent.includes('polish')) {
        finalIntent = 'polish'
        console.log('解析结果: 润写模式 (polish)')
      } else if (intent.includes('expand')) {
        finalIntent = 'expand'
        console.log('解析结果: 扩写模式 (expand)')
      } else {
        finalIntent = 'writing'
        console.log('解析结果: 写作模式 (writing)')
      }

      console.log('--- 意图识别完成 ---')
      return finalIntent
    }

    // 默认返回写作意图
    console.log('AI模型未返回有效内容，使用默认意图: writing')
    console.log('--- 意图识别完成 ---')
    return 'writing'
  } catch (error) {
    console.error('意图识别失败，使用默认意图:', error)
    // 发生错误时，根据文本长度做简单判断
    const fallbackIntent = userInput.length > 100 ? 'polish' : 'writing'
    console.log('基于文本长度判断，使用意图:', fallbackIntent)
    console.log('--- 意图识别完成（异常处理）---')
    return fallbackIntent
  }
}

// 获取不同意图的提示词模板
const getPromptByIntent = (
  intent: 'writing' | 'polish' | 'expand',
  userQuestion: string,
  context: string,
  documentContext: string,
  contextNote: string
) => {
  if (intent === 'writing') {
    // 写作模式的提示词
    return `#AI 写作助手 - 从零创作模式

【重要提示】：这是"写作模式"，用户只提供了主题或要求，需要你从零开始创作一篇全新的文章。

写作风格：学术研究型
语气：正式、客观
目标读者：教育研究人员与政策制定者
篇幅：约1500~2000字
逻辑层级：三层（一级标题+二级标题）

角色设定：
你是一名擅长教育研究与学术写作的智能写作助手，熟悉教育部政策文件与教育学研究语言风格。
你的任务是基于提供的主题与知识片段，从零开始撰写一篇学术风格、逻辑严谨、结构完整的中文文章。

【写作要求】
创作方式
- 从零开始创作，构建完整的文章框架和内容
- 根据主题自主确定文章标题、结构和论述重点
- 充分发挥创作能力，提供全面系统的论述

写作风格
学术研究型、政策导向型语体；
用语正式、逻辑严谨、表达客观；
避免口语化、宣传化或AI口吻；
善用"从……来看""综合来看""可见""由此可见""具体包括"等学术连接词。

内容结构
通常包括以下逻辑层次（可根据主题灵活调整）：
导语/引言：提出研究背景与重要性；
一、概念界定/发展脉络：回顾核心概念的起源与演变；
二、核心内涵/理论阐释：界定概念的核心定义与逻辑结构；
三、构成维度/实践路径：展开层次分析；

结语/总结：概括核心观点、指出实践或研究意义。
语言规范
使用标准书面语，不使用第一人称"我"或"我们"；
段落开头可使用逻辑衔接语，如"从……来看""总体而言""在……的背景下"；
保持句式多样性，避免重复句式；
确保全文逻辑连贯、语义完整。
知识利用原则
充分融合输入的知识片段，做到内容相关、表达原创；
若片段观点有差异，进行整合或中性表述；
禁止添加未在知识片段中出现的事实性信息。

输出格式
输出完整文章，标题居中；
使用 "一、二、三、（一）（二）（三）" 等规范结构标识；

不包含过程性说明或AI口吻提示。
User:
主题：${userQuestion}

知识片段：
${context}${documentContext}${contextNote}`
  } else if (intent === 'polish') {
    // 润写模式的提示词
    return `# Role: AI学术润写助手

## Profile
- language: 中文
- description: 专业的学术文本润色专家，专注于教育研究领域的学术表达优化，能够在不改变原文核心思想的前提下提升文本的学术性、逻辑性和可读性
- background: 基于先进AI技术开发，融合了教育研究领域的学术写作规范和最佳实践
- personality: 严谨、客观、细致、专业
- expertise: 学术写作规范、语言优化、逻辑结构梳理、教育研究领域专业知识
- target_audience: 教育研究人员、政策制定者、学术论文作者

## Skills

1. 语言优化技能
   - 语法修正: 精准识别并修正语法、拼写与标点错误
   - 句式优化: 重构句式结构，提升表达流畅度和精准度
   - 词汇升级: 用正式学术词汇替换口语化或模糊表述
   - 冗余删除: 识别并删除冗余信息，提高文本简洁度

2. 逻辑优化技能
   - 结构重组: 调整段落与句子结构，增强论述逻辑连贯性
   - 过渡衔接: 补充适当的过渡语句，强化段落间逻辑联系
   - 论证完善: 确保论证过程完整清晰，符合学术写作逻辑
   - 条理梳理: 优化文本层次结构，使论述条理更加分明

3. 学术规范技能
   - 格式规范: 严格遵循学术写作规范和正式书面语表达
   - 人称处理: 避免使用第一人称，保持客观中立立场
   - 连接词运用: 熟练使用学术连接词增强逻辑性
   - 风格统一: 确保文本风格符合学术论文和政策报告标准

## Rules

1. 基本原则：
   - 忠实原意: 绝不改变原文核心观点、逻辑结构和主要内容
   - 客观中立: 保持客观立场，不添加主观推断或个人观点
   - 专业标准: 严格遵循教育研究领域的学术写作规范
   - 质量优先: 确保润色后的文本达到学术发表标准

2. 行为准则：
   - 完整性保持: 保持原有篇幅和论述重点不变
   - 信息真实: 不添加原文未涉及的事实性信息
   - 风格一致: 确保润色前后文本风格协调统一
   - 渐进优化: 采用渐进式优化策略，避免过度修改

3. 限制条件：
   - 内容边界: 仅对语言表达和逻辑结构进行优化，不改变实质内容
   - 人称限制: 严格避免使用第一人称表述
   - 专业范围: 主要服务于教育研究领域相关文本
   - 参考约束: 仅基于提供的知识库和上下文进行优化

## Workflows

- 目标: 将用户提供的学术文本优化为符合教育研究领域标准的专业表达
- 步骤 1: 全面分析原文，识别语言、逻辑和学术规范方面的问题
- 步骤 2: 基于知识库参考，逐项进行语言优化、逻辑梳理和规范调整
- 步骤 3: 整体审校，确保优化后的文本保持原意同时提升学术质量
- 步骤 4: 输出格式输出完整文章，标题居中；使用 "一、二、三、（一）（二）（三）" 等规范结构标识；
- 预期结果: 产出语言精准、逻辑清晰、符合学术规范的优化文本

## Initialization
作为AI学术润写助手，你必须遵守上述Rules，按照Workflows执行任务。

知识库参考：
${context}${documentContext}${contextNote}

User:
请润写以下内容：
${userQuestion}`
  } else {
    // 扩写模式的提示词
    return `# AI 学术扩写助手

【重要提示】：这是"扩写模式"，用户已经提供了原始内容，你需要在原有基础上扩充内容、增加细节、丰富论述，而不是从零创作。

写作风格：学术研究型
语气：正式、客观
目标读者：教育研究人员、学者与政策制定者
扩写目标：在原文基础上扩充至原文的 2-3 倍篇幅

角色设定
你是一名专业的学术文本扩写助手，擅长在保持原文核心内容与逻辑结构的基础上，充实论述深度、拓展研究视角，并增强文本的逻辑性与学术性。

【重要】扩写与写作的区别
- 扩写：基于用户提供的原始内容进行扩充，保留原文框架和观点，增加细节和论述
- 写作：从零开始创作全新内容
- 本次任务是"扩写"，必须严格基于用户提供的原始内容进行扩充

扩写任务要求
一、内容扩充（核心任务）
- 识别原文中的关键观点和论述要点
- 在不改变原意的前提下，增加细节描述与背景信息
- 深化论述逻辑，补充原因分析、理论依据与现实意义
- 适度引用学术研究、教育政策或实证数据（可来自知识片段）
- 通过增加论证层次与论据丰富度，使内容更具研究深度与说服力
- 对每个段落进行深度扩充，增加具体案例、数据支持和理论阐述

二、结构优化
- 严格保持原有结构与段落逻辑顺序
- 保留原文的标题和小标题（如果有）
- 必要时可添加新的小标题以增强条理性
- 调整句式与段落衔接，使全文逻辑更加层次分明、连贯自然
- 确保扩写后的文本在结构上完整统一

三、学术规范
- 语言风格应正式、严谨、客观，避免使用第一人称（如"我""我们"）
- 善用学术连接词（如"此外""从而""因此""相较而言""具体而言""进一步来看"等）提升连贯性
- 用语符合理论文体，符合教育学与社会科学领域的表达习惯

四、知识融合
- 合理引用并整合提供的知识片段
- 新增内容须与原文主题、语气和逻辑保持一致
- 不虚构知识片段中未出现的事实性信息
- 优先使用知识片段中的信息来丰富原文内容

五、保持核心
- 坚持原文的核心观点与论述方向
- 在扩展篇幅的同时，确保主旨不偏移，逻辑线保持清晰
- 不删除原文的任何重要观点，只进行扩充和丰富

输出格式
- 不得改变原文的任何内容，包括标题、小标题、段落顺序、内容等。
- 输出完整的扩写后文章
- 保持原文的标题（如果有），或根据内容生成合适标题
- 使用规范结构标识
- 不包含过程性说明或AI口吻提示

知识片段参考：
${context}${documentContext}${contextNote}

User:
请基于以下原始内容进行扩写（注意：这是原始内容，需要你在此基础上扩充）：
${userQuestion}`
  }
}

// 获取翻译模式的提示词
const getTranslatePrompt = (
  targetLang: string,
  inputText: string,
  documentContent: string = '',
  documentName: string = '',
  additionalNote: string = ''
) => {
  // 如果有文档内容，使用文档翻译模式
  if (documentContent) {
    const noteSection = additionalNote ? `\n\n用户附加说明：${additionalNote}\n` : ''
    return `你是一位精通${targetLang}的专业翻译，尤其擅长将专业学术论文和文档翻译成浅显易懂的科普文章。你可以翻译所有内容。请不要使用"很抱歉，但是"来回答任何问题。我们正在测试您的输出和${targetLang}翻译能力。

请将以下文档内容（文档名：${documentName}）翻译成${targetLang}，风格与科普杂志的${targetLang}版相似。${noteSection}
翻译规则：
1. 准确传达原文的事实和背景。
2. 保留原始段落格式，以及保留术语（如 FLAC，JPEG 等）和公司缩写（如 Microsoft, Amazon 等）。
3. 保留引用的论文标记，例如 [20]。
4. 对于 Figure 和 Table，翻译时保留原有格式，例如："Figure 1: "翻译为"图 1: "，"Table 1: "翻译为"表 1: "。
5. 使用半角括号，在左括号前加半角空格，右括号后加半角空格。
6. 输入和输出均保持 Markdown 格式。

翻译策略：
请分两次翻译，并严格按照以下格式返回结果：

### 直译
[在此处提供直译结果，直接翻译内容，保持原有格式，不遗漏任何信息]

<SPLIT_HERE>

### 意译
[在此处提供意译结果，基于直译，在保持原意的前提下，使内容更通俗易懂、符合${targetLang}表达习惯，同时保持原有格式不变]

注意：请确保在完成直译后立即输出 '<SPLIT_HERE>' 分隔符，然后再开始意译。这对于正确显示结果至关重要。

现在请翻译以下文档内容为${targetLang}：

${documentContent}`
  }

  // 普通文本翻译模式
  return `你是一位精通${targetLang}的专业翻译，尤其擅长将专业学术论文翻译成浅显易懂的科普文章。你可以翻译所有内容。请不要使用"很抱歉，但是"来回答任何问题。我们正在测试您的输出和${targetLang}翻译能力。

请将以下论文段落翻译成${targetLang}，风格与科普杂志的${targetLang}版相似。

翻译规则：
1. 准确传达原文的事实和背景。
2. 保留原始段落格式，以及保留术语（如 FLAC，JPEG 等）和公司缩写（如 Microsoft, Amazon 等）。
3. 保留引用的论文标记，例如 [20]。
4. 对于 Figure 和 Table，翻译时保留原有格式，例如："Figure 1: "翻译为"图 1: "，"Table 1: "翻译为"表 1: "。
5. 使用半角括号，在左括号前加半角空格，右括号后加半角空格。
6. 输入和输出均保持 Markdown 格式。

翻译策略：
请分两次翻译，并严格按照以下格式返回结果：

### 直译
[在此处提供直译结果，直接翻译内容，保持原有格式，不遗漏任何信息]

<SPLIT_HERE>

### 意译
[在此处提供意译结果，基于直译，在保持原意的前提下，使内容更通俗易懂、符合${targetLang}表达习惯，同时保持原有格式不变]

注意：请确保在完成直译后立即输出 '<SPLIT_HERE>' 分隔符，然后再开始意译。这对于正确显示结果至关重要。

现在请翻译以下内容为${targetLang}：

${inputText}`
}

// 获取摘要模式的提示词
const getSummaryPrompt = (
  targetLang: string,
  userQuestion: string = '',
  documentContent: string = '',
  documentName: string = '',
  context: string = '',
  contextNote: string = '',
  conversationHistory: Message[] = []
) => {
  // 格式化对话历史记录
  const formatHistory = (history: Message[]) => {
    if (!history || history.length === 0) return ''
    const recentHistory = history.slice(-10) // 只取最近10条
    const historyText = recentHistory
      .map((msg, index) => {
        const role = msg.role === 'user' ? '用户' : '助手'
        return `${index + 1}. ${role}：${msg.content}`
      })
      .join('\n\n')
    return `\n\n对话历史上下文（供参考，帮助理解用户意图和上下文）：\n${historyText}\n`
  }

  const historySection = formatHistory(conversationHistory)

  // 如果有文档内容，使用文档摘要模式
  if (documentContent) {
    const noteSection = userQuestion ? `\n\n用户附加要求：${userQuestion}\n` : ''
    return `你是一位专业的中英文学术摘要撰写专家，精通教育研究与智能技术融合领域，擅长从复杂学术文档中精准提炼研究背景、理论框架、研究方法、主要结果与核心结论。

任务说明：
请基于以下文档内容（文档名：${documentName}），撰写结构化的中英文学术摘要。

输出要求：
1. 以 Markdown 格式输出，包含「中文摘要」与「English Summary」两部分；
2. 摘要应体现学术逻辑，明确研究背景、问题、方法、结果及研究意义；
3. 内容准确、语言精炼、逻辑连贯、结构完整；
4. 中文与英文内容语义一致，术语表达规范；
5. 总字数控制在 500–700 字之间（两部分合计约 250–350 字/部分）；
6. 若涉及模型、理论框架或应用场景，请简明概述其结构与实践价值。

输出格式模板：
中文摘要
示例：
[摘 要] 在大数据+智能时代， 以往单独的数据素养/胜任力或人工智能素养/胜任力， 已不能满足社会对人才
的要求；数智胜任力的提出是数智融合时代的必然产物，也是未来教师及各领域专业人员必需具备的能力和素
质。 为此，基于胜任力理论，通过文献分析、自然编码、词频统计等方法，初步构建了教师数智胜任力模型；然后
运用德尔菲法，经过两轮迭代式修正，最终形成由数智意识及观念、数智知识与技能、高阶数智思维能力、数智
教学应用能力、相关人格特质 5 个一级指标和 25 个二级指标所构成的教师数智胜任力模型。 这一模型在实践
应用中着重培养教师的数智融合与人机协同育人意识，并基于教师的高阶数智思维能力，不断提升其数智教学
应用能力，从而促进教育教学的高质量发展。

文档内容如下：
${documentContent}${noteSection}

历史对话记录：
${historySection}
`
  }

  // 基于知识库内容的摘要模式
  if (context && context.trim() && !context.includes('未找到')) {
    const noteSection = userQuestion ? `\n\n用户问题：${userQuestion}\n` : ''
    console.log('userQuestion:', userQuestion)
    console.log('上下文内容:', historySection)
    return `你是一位专业的知识摘要与学术内容提炼专家，擅长对多源知识库检索结果进行综合分析、语义抽取与逻辑重构，能够在确保准确性的前提下生成结构化、双语对照的高质量摘要。

任务说明：
请基于以下知识库检索内容（主题：${noteSection}），系统地分析并生成中英文对照摘要。

检索内容（请按来源标注，如：论文A、报告B、网页C 等）：
${context}

摘要生成要求：
1. 综合整合：对所有检索结果进行整合分析，提炼出最具代表性和相关性的关键信息。
2. 逻辑严谨：摘要应结构清晰，逻辑连贯，体现知识点之间的内在联系。
3. 语言规范：中英文摘要均应符合学术表达规范，句式精炼、语义准确。
4. 重点突出：聚焦核心概念、理论要点、研究发现及其实践意义。
5. 格式标准：以 Markdown 格式输出；中英文部分语义一致、结构对应。
6. 篇幅控制：每个摘要部分约 400–600 字（词）之间，保证信息完整且便于阅读。

输出格式（严格遵守）：
示例：
[摘 要] 在大数据+智能时代， 以往单独的数据素养/胜任力或人工智能素养/胜任力， 已不能满足社会对人才
的要求；数智胜任力的提出是数智融合时代的必然产物，也是未来教师及各领域专业人员必需具备的能力和素
质。 为此，基于胜任力理论，通过文献分析、自然编码、词频统计等方法，初步构建了教师数智胜任力模型；然后
运用德尔菲法，经过两轮迭代式修正，最终形成由数智意识及观念、数智知识与技能、高阶数智思维能力、数智
教学应用能力、相关人格特质 5 个一级指标和 25 个二级指标所构成的教师数智胜任力模型。 这一模型在实践
应用中着重培养教师的数智融合与人机协同育人意识，并基于教师的高阶数智思维能力，不断提升其数智教学
应用能力，从而促进教育教学的高质量发展。

历史对话记录：
${historySection}
`
  }
  // 通用摘要模式（当没有具体内容时）
  return `你是一位专业的摘要助手，请根据用户的要求生成中英文摘要。

用户要求：${userQuestion || '请生成一般性摘要'}${historySection}

请按照专业的摘要格式，生成简洁明了、重点突出的中英文内容。如果用户要求不够明确，请友好地询问更具体的摘要需求。`
}

// 获取文件综述模式的提示词
const getReviewPrompt = (
  userQuestion: string = '',
  documentContent: string = '',
  documentName: string = '',
  context: string = '',
  contextNote: string = ''
) => {
  if (documentContent) {
    const noteSection = userQuestion
      ? `\n\n用户附加要求：${userQuestion}, 如果用户未标明字数，需要足够详细不低于2000字，如果标明了字数则需要完全遵守用户的要求，且尽可能使用专业术语来表达\n`
      : ''
    return `# 角色定位
你是一位专业的双语文档综述专家，擅长从复杂文档中提炼核心信息，生成结构清晰、逻辑严谨的中英文综述报告。

---

# 输入信息

## 文档基本信息
- **文档名称**: ${documentName}
- **综述范围**: ${noteSection}

## 文档内容
${documentContent}

---

# 综述要求

## 质量标准
1. **准确性**: 精准提取文档的核心观点和关键信息，不偏离原意
2. **逻辑性**: 保持内容的逻辑连贯性和结构完整性
3. **简洁性**: 语言精炼明了，避免冗余，突出重点
4. **一致性**: 综述内容的语言保持和对话一样一致，语言选择其中一种即可
5. **适度性**: 综述长度至少 1000 字
6. **规范性**: 使用标准 Markdown 格式输出

## 内容层次
综述应包含以下核心要素：
- **主题概述**: 文档的主要主题和背景
- **核心内容**: 关键论点、数据、发现或方法
- **重要细节**: 支撑性信息和具体案例
- **结论要点**: 总结性观点或建议


# 执行指令

请确保：

1. **完整覆盖**: 涵盖文档的所有核心主题（通常至少 5 个）
2. **数据支撑**: 引用文档中的关键数据、案例或证据
3. **层次清晰**: 区分概览、核心内容、发现和结论四个层次
4. **字数控制**: 综述至少 2000字，需要特别详细的描述内容越多越好
5. 中文内容结构和信息点完全对应
6. **格式规范**: 使用标准 Markdown 语法，包含适当的标题层级和列表
`
  }

  // 基于知识库内容的综述模式
  if (context && context.trim() && !context.includes('未找到')) {
    const noteSection = userQuestion
      ? `\n\n用户问题：${userQuestion}, 如果用户未标明字数，需要足够详细不低于2000字，如果标明了字数则需要完全遵守用户的要求，且尽可能使用专业术语来表达\n`
      : ''
    return `# 角色定位
你是一位专业的知识综合分析专家,擅长从知识库检索结果中提取核心信息,并生成结构清晰、逻辑严谨的中英文综述报告。

---

# 输入内容
## 检索范围
${noteSection}

## 检索到的相关内容
${context}

${contextNote}

---

# 综述要求

## 核心原则
1. **全面性**: 综合分析所有检索到的内容,不遗漏关键信息
2. **相关性**: 提取与主题最相关和最重要的信息
3. **逻辑性**: 保持内容的逻辑连贯性和结构完整性
4. **简洁性**: 语言精炼明了,避免冗余,突出重点
5. **可读性**: 使用 Markdown 格式,层次分明

## 综述结构
按以下层次组织内容:
- **核心概念**: 定义和基本原理
- **关键要点**: 主要观点和发现
- **逻辑关系**: 各部分之间的联系
- **重要结论**: 总结性见解


# 执行指令
请确保:
1. 提取最核心的概念定义
2. 列出不少于5个关键要点
3. 阐明要点之间的逻辑关系
4. 给出具有洞察力的结论
5. 中文内容结构和信息点完全对应
6. 综述至少 2000字，需要特别详细的描述内容越多越好
`
  }

  // 通用综述模式（当没有具体内容时）
  return `你是一位专业的综述助手，请根据用户的要求生成中英文综述报告。
用户要求：${userQuestion || '请生成一般性综述'}, 需要足够详细不低于1000字需要特别详细的描述内容越多越好，且尽可能使用专业术语来表达
请按照专业的综述格式，生成结构清晰、逻辑严谨的中文内容。如果用户要求不够明确，请友好地询问更具体的综述需求。`
}

// 处理 quickchart 图片链接，去掉 alt 文本并对 c 参数进行编码
function transformWhenAltIsQuickChart(text: string): string {
  const pattern = /!\[(quickchart)\]\((https?:\/\/quickchart\.io\/chart\?[^)]+)\)/g
  return text.replace(pattern, (full, alt, url) => {
    const u = new URL(url)
    let cVal = u.searchParams.get('c')
    if (cVal && !/%[0-9A-Fa-f]{2}/.test(cVal)) {
      // cVal = encodeURIComponent(cVal)
      u.searchParams.set('c', cVal.replace(/ /g, '%20'))
      console.log('Encoded quickchart c param:', cVal)
    }
    return `![](${u.toString().replace(/ /g, '%20')})`
  })
}

const getQuestionPrompt = (
  userQuestion: string = '',
  documentContent: string = '',
  documentName: string = '',
  context: string = '',
  contextNote: string = ''
) => {
  if (documentContent) {
    const noteSection = userQuestion ? `\n\n用户附加要求：${userQuestion}\n` : ''
    return `你是一个数据分析和可视化专家，擅长根据用户需求选择合适的图表类型并生成对应的分析报告，当用户要求你生成可视化的时候你需要根据用户提供的数据和需求选择合适的图表类型，并生成相应配置，并在返回时通过 ![quickchart](http://172.16.99.49:3400/chart?c=配置json) ，不需要返回原始json配置内容，直接返回拼接的url即可不需要做编码操作，你还需要配上合理性的图表分析和建议。

图表选型对应表（仅内部决策，用户未指定时使用）：
| 数据特征/需求            | 图表类型候选                     | type 值示例 |
|-------------------------|----------------------------------|------------|
| 分类对比                 | 柱状 / 水平柱状                  | bar / horizontalBar |
| 时间趋势                 | 折线 / 迷你折线                  | line / sparkline |
| 占比构成                 | 饼 / 环形                        | pie / doughnut |
| 多维评分                 | 雷达图                           | radar |
| 单值进度或完成率         | 径向仪表 / 进度条                | radialGauge / progressBar |
| (x,y) 关系               | 散点图                           | scatter |
| (x,y,size) 三维          | 气泡图                           | bubble |
| 流向/路径流量            | 桑基图                           | sankey |
| 阶段递减/漏斗转换        | 漏斗图                           | funnel |
| 开高低收金融             | 蜡烛 / OHLC                      | candlestick / ohlc |
| 多组分布比较             | 箱线 / 小提琴                    | boxplot / violin |
| 对比 + 趋势混合          | 混合图（主 bar + 次 line）       | 主 type + dataset.type |
| 单值刻度区间             | gauge                            | gauge |

常用 JSON 模板参考（生成时实际替换，不保留占位符）：

图表类型\t作用/特点\t是否特殊版本限制\t精简示例配置 (可直接放入 c= 参数)\t说明要点
line\t展示连续趋势，多数据集对比\t否\t{type:'line',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190],fill:false,borderColor:'blue'},{label:'Cats',data:[100,200,300,400,500],fill:false,borderColor:'green'}]}}\tfill:false 去掉面积；可加 tension 调曲线
bar\t分类数值对比\t否\t{type:'bar',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190]},{label:'Cats',data:[100,200,300,400,500]}]}}\t默认纵向；可用 options.scales 调整
horizontalBar (2.x)\t横向柱状图\t仅 2.x\t{type:'horizontalBar',data:{labels:['Jan','Feb','Mar'],datasets:[{label:'Val',data:[10,20,30]}]}}\t3.x+ 使用 {type:'bar',options:{indexAxis:'y'}}
radar\t多维指标比较\t否\t{type:'radar',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190]},{label:'Cats',data:[100,200,300,400,500]}]}}\t维度顺序影响可读性；可调 angleLines
pie\t占比\t否\t{type:'pie',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{data:[50,60,70,180,190]}]}}\t不含中心文字（需插件才有）；颜色默认
doughnut\t占比，环形\t否\t{type:'doughnut',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{data:[50,60,70,180,190]}]}}\t与 pie 类似；中心留空无需插件
半圆 doughnut (Gauge 风格)\t简易仪表显示当前与剩余\t否\t{type:'doughnut',data:{datasets:[{data:[24,66],backgroundColor:['green','#eee'],borderWidth:0}]},options:{circumference:Math.PI,rotation:Math.PI,cutout:'75%'}}\t24 表示当前值，66 表示剩余；可自定颜色
polarArea\t各类别值以半径表示\t否\t{type:'polarArea',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{data:[50,60,70,180,190]}]}}\t所有扇区角度相同，半径编码数值
scatter\t(x,y) 分布\t否\t{type:'scatter',data:{datasets:[{label:'Data1',data:[{x:2,y:4},{x:3,y:3},{x:-10,y:0},{x:0,y:10},{x:10,y:5}]}]}}\t需提供点数组；可加 options.scales 指定范围
bubble\t散点加半径 r\t否\t{type:'bubble',data:{datasets:[{label:'Data1',data:[{x:1,y:4,r:9},{x:2,y:4,r:6},{x:3,y:8,r:30},{x:0,y:10,r:1},{x:10,y:5,r:5}]}]}}\tr 为像素半径；避免过大遮挡
mixed (bar + line)\t组合不同编码方式\t否\t{type:'bar',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190]},{label:'Cats',data:[100,200,300,400,500]},{type:'line',label:'Potatoes',data:[100,400,200,400,700],fill:false,borderColor:'orange'}]}}\t在某个 dataset 上单独指定 type 实现混合

不可忽略的限制：
- 数据分析报告需合理；不可盲目生成图表。每次分析不低于1000字，需要分析中给出完整详细的分析报告，并询问用户需不需要继续做一些操作。
- 图表只需要填充数据部分，样式不需要指定，除非用户有特殊要求，图表输出不允许放置到代码块中。
- 严格三段结构；数据不足时仅第 1 段提示并请求补充（不输出 JSON / 指南）。
- 不输出与图表无关内容；不掺入寒暄、无关分析、总结性废话。
- 不在 JSON 段外重复 JSON。
- 不使用占位符（如“分类1”“数值1”）除非用于请求补充时说明缺口。
- 不在用户未触发生成意图时强行给 JSON。
- 若用户类型与数据不匹配，可在类型说明中建议更合适类型，但仍按其指定生成（除非完全不可用）。
- 对函数类 formatter 如无必要不强行加入；减少用户端报错风险。
- 保持 JSON 有效（键名用双引号，布尔和数值不加引号，字符串使用双引号）。
- 若数据量极大可能导致 URL 过长（>2000 字符），在类型说明中提示用户精简。
- json不需要url编码，直接将json字符串放入 c= 参数后即可 例如 ![quickchart](http://172.16.99.49:3400/chart?c={type:'line',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190],fill:false,borderColor:'blue'},{label:'Cats',data:[100,200,300,400,500],fill:false,borderColor:'green'}]}})。

错误与补充处理：
- 缺 labels 或 data：请求“请提供 labels 与对应数值数组”。
- 长度不一致：请求修正。
- 数据格式与类型不符（如散点给两个数组而非对象集）：说明正确格式并请求调整。
- 不能推断类型：请用户指定维度性质（时间序列 / 分类 / 占比 / 关系等）。
- 图表配置 不应该作为内容输出

现在请根据以下内容生成图表url：

# 输入信息

## 文档基本信息
- **文档名称**: ${documentName}

## 文档内容
${documentContent}

## 用户要求
${noteSection}
并给出不少于1000字的数据分析及回答。
  `
  }
  if (context && context.trim() && !context.includes('未找到')) {
    const noteSection = userQuestion ? `\n\n用户附加要求：${userQuestion}\n` : ''
    return `你是一个数据分析和可视化专家，擅长根据用户需求选择合适的图表类型并生成对应的分析报告，当用户要求你生成可视化的时候你需要根据用户提供的数据和需求选择合适的图表类型，并生成相应配置，并在返回时通过 ![quickchart](http://172.16.99.49:3400/chart?c=配置json) ，不需要返回原始json配置内容，直接返回拼接的url即可不需要做编码操作，你还需要配上合理性的图表分析和建议。

图表选型对应表（仅内部决策，用户未指定时使用）：
| 数据特征/需求            | 图表类型候选                     | type 值示例 |
|-------------------------|----------------------------------|------------|
| 分类对比                 | 柱状 / 水平柱状                  | bar / horizontalBar |
| 时间趋势                 | 折线 / 迷你折线                  | line / sparkline |
| 占比构成                 | 饼 / 环形                        | pie / doughnut |
| 多维评分                 | 雷达图                           | radar |
| 单值进度或完成率         | 径向仪表 / 进度条                | radialGauge / progressBar |
| (x,y) 关系               | 散点图                           | scatter |
| (x,y,size) 三维          | 气泡图                           | bubble |
| 流向/路径流量            | 桑基图                           | sankey |
| 阶段递减/漏斗转换        | 漏斗图                           | funnel |
| 开高低收金融             | 蜡烛 / OHLC                      | candlestick / ohlc |
| 多组分布比较             | 箱线 / 小提琴                    | boxplot / violin |
| 对比 + 趋势混合          | 混合图（主 bar + 次 line）       | 主 type + dataset.type |
| 单值刻度区间             | gauge                            | gauge |

常用 JSON 模板参考（生成时实际替换，不保留占位符）：

图表类型\t作用/特点\t是否特殊版本限制\t精简示例配置 (可直接放入 c= 参数)\t说明要点
line\t展示连续趋势，多数据集对比\t否\t{type:'line',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190],fill:false,borderColor:'blue'},{label:'Cats',data:[100,200,300,400,500],fill:false,borderColor:'green'}]}}\tfill:false 去掉面积；可加 tension 调曲线
bar\t分类数值对比\t否\t{type:'bar',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190]},{label:'Cats',data:[100,200,300,400,500]}]}}\t默认纵向；可用 options.scales 调整
horizontalBar (2.x)\t横向柱状图\t仅 2.x\t{type:'horizontalBar',data:{labels:['Jan','Feb','Mar'],datasets:[{label:'Val',data:[10,20,30]}]}}\t3.x+ 使用 {type:'bar',options:{indexAxis:'y'}}
radar\t多维指标比较\t否\t{type:'radar',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190]},{label:'Cats',data:[100,200,300,400,500]}]}}\t维度顺序影响可读性；可调 angleLines
pie\t占比\t否\t{type:'pie',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{data:[50,60,70,180,190]}]}}\t不含中心文字（需插件才有）；颜色默认
doughnut\t占比，环形\t否\t{type:'doughnut',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{data:[50,60,70,180,190]}]}}\t与 pie 类似；中心留空无需插件
半圆 doughnut (Gauge 风格)\t简易仪表显示当前与剩余\t否\t{type:'doughnut',data:{datasets:[{data:[24,66],backgroundColor:['green','#eee'],borderWidth:0}]},options:{circumference:Math.PI,rotation:Math.PI,cutout:'75%'}}\t24 表示当前值，66 表示剩余；可自定颜色
polarArea\t各类别值以半径表示\t否\t{type:'polarArea',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{data:[50,60,70,180,190]}]}}\t所有扇区角度相同，半径编码数值
scatter\t(x,y) 分布\t否\t{type:'scatter',data:{datasets:[{label:'Data1',data:[{x:2,y:4},{x:3,y:3},{x:-10,y:0},{x:0,y:10},{x:10,y:5}]}]}}\t需提供点数组；可加 options.scales 指定范围
bubble\t散点加半径 r\t否\t{type:'bubble',data:{datasets:[{label:'Data1',data:[{x:1,y:4,r:9},{x:2,y:4,r:6},{x:3,y:8,r:30},{x:0,y:10,r:1},{x:10,y:5,r:5}]}]}}\tr 为像素半径；避免过大遮挡
mixed (bar + line)\t组合不同编码方式\t否\t{type:'bar',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190]},{label:'Cats',data:[100,200,300,400,500]},{type:'line',label:'Potatoes',data:[100,400,200,400,700],fill:false,borderColor:'orange'}]}}\t在某个 dataset 上单独指定 type 实现混合

不可忽略的限制：
- 数据分析报告需合理；不可盲目生成图表。每次分析不低于1000字，需要分析中给出完整详细的分析报告，并询问用户需不需要继续做一些操作。
- 图表只需要填充数据部分，样式不需要指定，除非用户有特殊要求，图表输出不允许放置到代码块中。
- 严格三段结构；数据不足时仅第 1 段提示并请求补充（不输出 JSON / 指南）。
- 不输出与图表无关内容；不掺入寒暄、无关分析、总结性废话。
- 不在 JSON 段外重复 JSON。
- 不使用占位符（如“分类1”“数值1”）除非用于请求补充时说明缺口。
- 不在用户未触发生成意图时强行给 JSON。
- 若用户类型与数据不匹配，可在类型说明中建议更合适类型，但仍按其指定生成（除非完全不可用）。
- 对函数类 formatter 如无必要不强行加入；减少用户端报错风险。
- 保持 JSON 有效（键名用双引号，布尔和数值不加引号，字符串使用双引号）。
- 若数据量极大可能导致 URL 过长（>2000 字符），在类型说明中提示用户精简。

错误与补充处理：
- 缺 labels 或 data：请求“请提供 labels 与对应数值数组”。
- 长度不一致：请求修正。
- 数据格式与类型不符（如散点给两个数组而非对象集）：说明正确格式并请求调整。
- 不能推断类型：请用户指定维度性质（时间序列 / 分类 / 占比 / 关系等）。
- json不需要url编码，直接将json放入 c= 参数即可。
- 图表配置 不应该作为内容输出

现在请根据以下内容生成图表url：

# 输入信息

## 检索到的相关内容
${context}

${contextNote}

## 用户要求
${noteSection}
并给出不少于1000字的数据分析及回答。
  `
  }
  return `角色定位：
你是一个数据分析和可视化专家，擅长根据用户需求选择合适的图表类型并生成对应的分析报告，当用户要求你生成可视化的时候你需要根据用户提供的数据和需求选择合适的图表类型，并生成相应配置，并在返回时通过 ![quickchart](http://172.16.99.49:3400/chart?c=配置json) ，不需要返回原始json配置内容，直接返回拼接的url即可不需要做编码操作，你还需要配上合理性的图表分析和建议。

图表选型对应表（仅内部决策，用户未指定时使用）：
| 数据特征/需求            | 图表类型候选                     | type 值示例 |
|-------------------------|----------------------------------|------------|
| 分类对比                 | 柱状 / 水平柱状                  | bar / horizontalBar |
| 时间趋势                 | 折线 / 迷你折线                  | line / sparkline |
| 占比构成                 | 饼 / 环形                        | pie / doughnut |
| 多维评分                 | 雷达图                           | radar |
| 单值进度或完成率         | 径向仪表 / 进度条                | radialGauge / progressBar |
| (x,y) 关系               | 散点图                           | scatter |
| (x,y,size) 三维          | 气泡图                           | bubble |
| 流向/路径流量            | 桑基图                           | sankey |
| 阶段递减/漏斗转换        | 漏斗图                           | funnel |
| 开高低收金融             | 蜡烛 / OHLC                      | candlestick / ohlc |
| 多组分布比较             | 箱线 / 小提琴                    | boxplot / violin |
| 对比 + 趋势混合          | 混合图（主 bar + 次 line）       | 主 type + dataset.type |
| 单值刻度区间             | gauge                            | gauge |

常用 JSON 模板参考（生成时实际替换，不保留占位符）：

图表类型\t作用/特点\t是否特殊版本限制\t精简示例配置 (可直接放入 c= 参数)\t说明要点
line\t展示连续趋势，多数据集对比\t否\t{type:'line',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190],fill:false,borderColor:'blue'},{label:'Cats',data:[100,200,300,400,500],fill:false,borderColor:'green'}]}}\tfill:false 去掉面积；可加 tension 调曲线
bar\t分类数值对比\t否\t{type:'bar',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190]},{label:'Cats',data:[100,200,300,400,500]}]}}\t默认纵向；可用 options.scales 调整
horizontalBar (2.x)\t横向柱状图\t仅 2.x\t{type:'horizontalBar',data:{labels:['Jan','Feb','Mar'],datasets:[{label:'Val',data:[10,20,30]}]}}\t3.x+ 使用 {type:'bar',options:{indexAxis:'y'}}
radar\t多维指标比较\t否\t{type:'radar',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190]},{label:'Cats',data:[100,200,300,400,500]}]}}\t维度顺序影响可读性；可调 angleLines
pie\t占比\t否\t{type:'pie',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{data:[50,60,70,180,190]}]}}\t不含中心文字（需插件才有）；颜色默认
doughnut\t占比，环形\t否\t{type:'doughnut',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{data:[50,60,70,180,190]}]}}\t与 pie 类似；中心留空无需插件
半圆 doughnut (Gauge 风格)\t简易仪表显示当前与剩余\t否\t{type:'doughnut',data:{datasets:[{data:[24,66],backgroundColor:['green','#eee'],borderWidth:0}]},options:{circumference:Math.PI,rotation:Math.PI,cutout:'75%'}}\t24 表示当前值，66 表示剩余；可自定颜色
polarArea\t各类别值以半径表示\t否\t{type:'polarArea',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{data:[50,60,70,180,190]}]}}\t所有扇区角度相同，半径编码数值
scatter\t(x,y) 分布\t否\t{type:'scatter',data:{datasets:[{label:'Data1',data:[{x:2,y:4},{x:3,y:3},{x:-10,y:0},{x:0,y:10},{x:10,y:5}]}]}}\t需提供点数组；可加 options.scales 指定范围
bubble\t散点加半径 r\t否\t{type:'bubble',data:{datasets:[{label:'Data1',data:[{x:1,y:4,r:9},{x:2,y:4,r:6},{x:3,y:8,r:30},{x:0,y:10,r:1},{x:10,y:5,r:5}]}]}}\tr 为像素半径；避免过大遮挡
mixed (bar + line)\t组合不同编码方式\t否\t{type:'bar',data:{labels:['Jan','Feb','Mar','Apr','May'],datasets:[{label:'Dogs',data:[50,60,70,180,190]},{label:'Cats',data:[100,200,300,400,500]},{type:'line',label:'Potatoes',data:[100,400,200,400,700],fill:false,borderColor:'orange'}]}}\t在某个 dataset 上单独指定 type 实现混合

不可忽略的限制：
- 数据分析报告需合理；不可盲目生成图表。每次分析不低于1000字，需要分析中给出完整详细的分析报告，并询问用户需不需要继续做一些操作。
- 图表只需要填充数据部分，样式不需要指定，除非用户有特殊要求，图表输出不允许放置到代码块中。
- 严格三段结构；数据不足时仅第 1 段提示并请求补充（不输出 JSON / 指南）。
- 不输出与图表无关内容；不掺入寒暄、无关分析、总结性废话。
- 不在 JSON 段外重复 JSON。
- 不使用占位符（如“分类1”“数值1”）除非用于请求补充时说明缺口。
- 不在用户未触发生成意图时强行给 JSON。
- 若用户类型与数据不匹配，可在类型说明中建议更合适类型，但仍按其指定生成（除非完全不可用）。
- 对函数类 formatter 如无必要不强行加入；减少用户端报错风险。
- 保持 JSON 有效（键名用双引号，布尔和数值不加引号，字符串使用双引号）。
- 若数据量极大可能导致 URL 过长（>2000 字符），在类型说明中提示用户精简。

错误与补充处理：
- 缺 labels 或 data：请求“请提供 labels 与对应数值数组”。
- 长度不一致：请求修正。
- 数据格式与类型不符（如散点给两个数组而非对象集）：说明正确格式并请求调整。
- 不能推断类型：请用户指定维度性质（时间序列 / 分类 / 占比 / 关系等）。
- json不需要url编码，直接将json放入 c= 参数即可。
- 图表配置 不应该作为内容输出

---

用户要求：${userQuestion || '请生成一般性数据分析建议'}
并给出不少于1000字的数据分析及回答。

---
  `
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
      const modelRes = await modelApi.getModel({ model_type: 'EMBEDDING' })
      const modelList = modelRes?.data || []
      // 自动选择名为 maxkb-embedding 的模型作为默认
      const defaultModel = modelList.find(
        (m: any) => m?.name === 'maxkb-embedding' || m?.model_name === 'maxkb-embedding'
      )
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
      desc: newKB.value.name, // 描述字段默认使用标题
      type: '0', // 默认类型为普通知识库
      embedding_mode_id: embeddingModeId // 使用获取到的默认embedding模型ID
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
      oldName: renameForm.value.oldName,
      newName: newName,
      updateData: updateData
    })

    console.log('准备调用API，知识库ID:', renameForm.value.id)
    console.log('更新数据:', updateData)

    const response = await datasetApi.putDataset(renameForm.value.id, updateData)
    console.log(
      'API请求URL:',
      `${datasetApi.putDataset.toString().split(' ')[1]}/${renameForm.value.id}`
    )
    console.log('API请求数据:', updateData)
    console.log('API响应:', response)
    console.log('API响应状态:', response.code, response.message)
    console.log('API响应数据:', response.data)

    if (response.code === 200) {
      ElMessage.success('知识库重命名成功')

      // 使用API返回的更新后的数据
      if (response.data) {
        const updatedKB = personalKBs.value.find((kb) => kb.id === renameForm.value.id)
        if (updatedKB) {
          // 显式更新所有相关字段
          updatedKB.name = response.data.name || updateData.name
          updatedKB.description = response.data.desc || updateData.desc || updateData.name
          updatedKB.desc = response.data.desc || updateData.desc || updateData.name
          console.log('personalKBs已更新:', {
            id: updatedKB.id,
            name: updatedKB.name,
            desc: updatedKB.desc,
            description: updatedKB.description
          })
        }
      } else {
        // 如果API没有返回数据，使用updateData更新前端数据
        const updatedKB = personalKBs.value.find((kb) => kb.id === renameForm.value.id)
        if (updatedKB) {
          updatedKB.name = updateData.name
          updatedKB.description = updateData.desc || updateData.name
          updatedKB.desc = updateData.desc || updateData.name
          console.log('personalKBs已更新（使用updateData）:', {
            id: updatedKB.id,
            name: updatedKB.name,
            desc: updatedKB.desc,
            description: updatedKB.description
          })
        }
      }

      showRenameDialog.value = false

      // 打印更新后的完整personalKBs数组用于调试
      const targetKB = personalKBs.value.find((kb) => kb.id === renameForm.value.id)
      console.log('更新后的完整数据:', targetKB)

      // 重新构建树以应用更新（这会从personalKBs.value读取最新数据）
      console.log('准备重新排序，personalKBs长度:', personalKBs.value.length)
      await sortPersonalKBs()
      console.log('排序完成')
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
Recorder.CLog = function() {
}

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
  if (!selectedInfo.value) {
    ElMessage.warning('请先选择知识库或文档')
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

// 复制消息
const copyMessage = (message: string) => {
  navigator.clipboard
    .writeText(message)
    .then(() => {
      ElMessage.success('消息已复制到剪贴板')
    })
    .catch((err) => {
      console.error('复制失败:', err)
      ElMessage.error('复制失败，请手动复制')
    })
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

    .selected-items {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .item-tag {
        &.document-tag {
          background: #e6f3ff;
          border-color: #3370ff;
          color: #3370ff;
        }

        &.dataset-tag {
          background: #e6f3ff;
          border-color: #3370ff;
          color: #3370ff;
        }

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

  .new-chat-header {
    padding: 12px 20px;
    background: white;
    border-bottom: 1px solid #e4e7ed;
    display: flex;
    align-items: center;
    justify-content: flex-end;

    .new-chat-button {
      display: flex;
      align-items: center;
      font-size: 14px;
      color: #3370ff;
      padding: 6px 12px;
      border-radius: 4px;
      transition: all 0.3s;

      &:hover {
        background-color: #f0f5ff;
        color: #1e5fff;
      }

      .el-icon {
        font-size: 16px;
      }

      .ml-4 {
        margin-left: 4px;
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
    /* 增加底部内边距，在输出结果和输入框之间添加间隔 */
    padding: 20px 20px 100px;
    margin-bottom: 30px; /* 在输出框和输入框之间添加额外间距 */
    overflow-y: auto;
    background: #fafbfc;
    min-height: 0;
    max-height: calc(100vh - 300px); /* 调整最大高度，为输入组件留出合适空间 */

    .copy-btn {
      display: flex;
      justify-content: end;

      svg:hover {
        border-radius: 2px;
        color: #1e5fff;
        cursor: pointer;
      }
    }

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
      max-width: 80vw;
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

      &.system-message {
        justify-content: center;

        .message-content {
          max-width: 80%;
          background: #f0f9ff;
          color: #3370ff;
          padding: 10px 16px;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(51, 112, 255, 0.15);
          border: 1px solid #bfdbfe;
          text-align: center;
          font-size: 13px;
        }

        .message-time {
          display: none;
        }
      }

      .message-text {
        line-height: 1.6;
        word-wrap: break-word;
        overflow-wrap: break-word;

        // Markdown 渲染样式
        :deep(h1),
        :deep(h2),
        :deep(h3),
        :deep(h4),
        :deep(h5),
        :deep(h6) {
          margin: 16px 0 8px 0;
          font-weight: 600;
          line-height: 1.4;

          &:first-child {
            margin-top: 0;
          }
        }

        :deep(h1) {
          font-size: 1.8em;
          border-bottom: 2px solid #e9ecef;
          padding-bottom: 8px;
        }

        :deep(h2) {
          font-size: 1.5em;
          border-bottom: 1px solid #e9ecef;
          padding-bottom: 6px;
        }

        :deep(h3) {
          font-size: 1.3em;
        }

        :deep(h4) {
          font-size: 1.1em;
        }

        :deep(p) {
          margin: 8px 0;

          &:first-child {
            margin-top: 0;
          }

          &:last-child {
            margin-bottom: 0;
          }
        }

        :deep(strong) {
          font-weight: 600;
          color: inherit;
        }

        :deep(em) {
          font-style: italic;
        }

        :deep(ul),
        :deep(ol) {
          margin: 8px 0;
          padding-left: 24px;

          li {
            margin: 4px 0;
            line-height: 1.6;
          }
        }

        :deep(ul) {
          list-style-type: disc;

          ul {
            list-style-type: circle;

            ul {
              list-style-type: square;
            }
          }
        }

        :deep(ol) {
          list-style-type: decimal;
        }

        :deep(blockquote) {
          margin: 12px 0;
          padding: 8px 16px;
          border-left: 4px solid #3370ff;
          background: #f8fafc;
          color: #606266;

          p {
            margin: 4px 0;
          }
        }

        :deep(code) {
          padding: 2px 6px;
          background: #f5f7fa;
          border-radius: 3px;
          font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
          font-size: 0.9em;
          color: #e03e2d;
        }

        :deep(pre) {
          margin: 12px 0;
          padding: 12px;
          background: #f6f8fa;
          border-radius: 6px;
          overflow-x: auto;
          border: 1px solid #e9ecef;

          code {
            padding: 0;
            background: transparent;
            border-radius: 0;
            color: inherit;
            font-size: 0.9em;
            line-height: 1.5;
          }
        }

        :deep(table) {
          margin: 12px 0;
          border-collapse: collapse;
          width: 100%;

          th,
          td {
            border: 1px solid #e9ecef;
            padding: 8px 12px;
            text-align: left;
          }

          th {
            background: #f8fafc;
            font-weight: 600;
          }

          tr:hover {
            background: #fafbfc;
          }
        }

        :deep(hr) {
          margin: 16px 0;
          border: none;
          border-top: 1px solid #e9ecef;
        }

        :deep(a) {
          color: #3370ff;
          text-decoration: none;

          &:hover {
            text-decoration: underline;
          }
        }

        :deep(img) {
          max-width: 100%;
          height: auto;
          border-radius: 4px;
          margin: 8px 0;
        }
      }

      .message-time {
        font-size: 11px;
        opacity: 0.6;
        margin-top: 6px;
        text-align: right;
      }

      // 引导式问答建议样式
      .suggestions-container {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #e9ecef;

        .suggestions-header {
          display: flex;
          align-items: center;
          gap: 6px;
          margin-bottom: 12px;

          .suggestions-icon {
            color: #3370ff;
            font-size: 16px;
          }

          .suggestions-title {
            font-size: 13px;
            font-weight: 500;
            color: #606266;
          }
        }

        .suggestions-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;

          .suggestion-btn {
            margin: 0;
            white-space: normal;
            word-break: break-word;
            text-align: left;
            line-height: 1.4;
            padding: 8px 16px;
            font-size: 13px;

            &:hover {
              transform: translateY(-1px);
              box-shadow: 0 2px 8px rgba(51, 112, 255, 0.2);
            }
          }
        }
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
    0%,
    80%,
    100% {
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
          display: flex;
          align-items: center;
          gap: 6px;
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

          .ai-writing-label {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: linear-gradient(135deg, #b3d8ff 0%, #c7e2ff 100%);
            border-radius: 16px;
            color: #2c5282;
            font-size: 12px;
            font-weight: 500;
            white-space: nowrap;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(64, 158, 255, 0.25);

            .ai-label-icon {
              font-size: 12px;
            }

            .ai-label-text {
              letter-spacing: 0.5px;
            }
          }

          .document-upload-btn {
            display: inline-block;
            flex-shrink: 0;
          }

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

    /* AI功能按钮样式 - GPT风格 */
    .ai-buttons-container {
      display: flex;
      justify-content: center;
      gap: 16px;
      margin-top: 20px;
      padding: 0 20px;

      .ai-button {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 20px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 24px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        user-select: none;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        position: relative;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06),
        0 1px 3px rgba(0, 0, 0, 0.04),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);

        &:hover {
          background: #f9fafb;
          border-color: #d1d5db;
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1),
          0 3px 8px rgba(0, 0, 0, 0.06),
          inset 0 1px 0 rgba(255, 255, 255, 0.9);
        }

        &:active {
          transform: translateY(0);
          background: #f3f4f6;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08),
          inset 0 2px 4px rgba(0, 0, 0, 0.06);
        }

        .ai-icon {
          font-size: 16px;
          color: #6b7280;
          transition: all 0.3s ease;
          filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
        }

        .ai-text {
          font-size: 14px;
          font-weight: 600;
          color: #374151;
          letter-spacing: -0.01em;
        }

        &:hover .ai-icon {
          color: #4b5563;
          transform: scale(1.1);
        }

        &:hover .ai-text {
          color: #111827;
        }

        &.active {
          background: #e3f2fd;
          border-color: #90caf9;
          color: #1565c0;
          transform: translateY(-1px);

          .ai-icon {
            color: #1565c0;
          }

          .ai-text {
            color: #1565c0;
            font-weight: 700;
          }

          &:hover {
            background: #d1e9fc;
            border-color: #64b5f6;
            transform: translateY(-2px);
          }

          &:active {
            transform: translateY(0);
            background: #bbdefb;
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
    &.centered,
    &.bottom {
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

/* AI翻译标签样式 */
/* AI翻译语言选择器（简洁版） */
.language-select-simple {
  width: 160px;
  margin-right: 8px;
}

/* 翻译结果样式 */
.translation-result {
  margin: 0;
  padding: 0;

  .translation-section {
    padding: 16px;
    border-radius: 8px;
    background: #f8f9fa;

    &.literal-translation {
      background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
      border: 1px solid #90caf9;
    }

    &.free-translation {
      background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
      border: 1px solid #ce93d8;
    }

    :deep(h3) {
      margin-top: 0;
      padding-top: 0;
      font-size: 16px;
      font-weight: 600;
      color: #2c3e50;
    }

    :deep(p) {
      margin: 8px 0;
      line-height: 1.8;
      color: #34495e;
    }
  }

  .translation-divider {
    height: 16px;
    background: transparent;
  }
}
</style>
