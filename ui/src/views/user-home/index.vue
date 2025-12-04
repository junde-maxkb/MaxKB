<template>
  <div class="common-layout">
    <el-container style="height: 100%">
      <transition name="slide-fade">
        <el-aside v-if="!isCollapsed" width="260px" style="background: #f8f1fa">
          <div class="container">
            <div class="first">
              <div class="icon-box">
                <img src="@/assets/JKY.png" alt="JKY" class="logo-img" />
                <div class="home-icon" @click="goToHome">
                  <home-two theme="outline" size="16" fill="#333" />
                </div>
              </div>
              <div class="input-box">
                <el-input
                  v-model="searchText"
                  style="width: 240px"
                  placeholder="搜索..."
                  :suffix-icon="Search"
                />
              </div>

              <div class="add-btn">
                <el-button style="width: 240px" type="primary" :icon="Plus" @click="openCreateKBDialog">新建知识库</el-button>
              </div>

              <div class="line-split"></div>
            </div>

            <div class="knowledge-tree second">
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
                          <svg
                            v-if="data.icon === 'OfficeBuilding'"
                            width="18px"
                            height="18px"
                            viewBox="0 0 18 18"
                            version="1.1"
                            xmlns="http://www.w3.org/2000/svg"
                            xmlns:xlink="http://www.w3.org/1999/xlink"
                          >
                            <g
                              id="页面-1"
                              stroke="none"
                              stroke-width="1"
                              fill="none"
                              fill-rule="evenodd"
                            >
                              <g id="首页" transform="translate(-113, -405)" fill="#6E747E">
                                <g id="编组" transform="translate(113, 405)">
                                  <path
                                    d="M16.8947368,18 L1.10526315,18 C0.505263146,18 0,17.526618 0,16.9644768 L0,11.8460338 C0,11.2838926 0.505263164,10.8105106 1.10526315,10.8105106 L5.87368421,10.8105106 L9,13.7691482 L12.2210526,10.7809243 L16.8947368,10.7809243 C17.4947369,10.7809243 18,11.2543063 18,11.8164474 L18,16.9644768 C18,17.526618 17.4947368,18 16.8947368,18 Z"
                                    id="形状"
                                    fill-rule="nonzero"
                                  ></path>
                                  <path
                                    d="M14.9368421,0 C15.8842105,0 16.6736842,0.739659405 16.6736842,1.62725069 L16.6736842,11.2543063 L15.7263158,11.2543063 L15.7263158,15.2217206 C15.7263158,14.8075113 15.3789474,14.4820612 14.9368421,14.4820612 L5.05263159,14.4820612 C4.61052631,14.4820612 4.26315789,14.8075113 4.26315789,15.2217206 L4.26315789,11.2543063 L3.31578947,11.2543063 L3.31578947,1.62725069 C3.31578947,0.739659405 4.10526316,0 5.05263159,0 L14.9368421,0 Z M13.7684211,7.9998049 L6.22105263,7.9998049 C5.96842105,7.9998049 5.74736841,8.20690954 5.74736841,8.44360054 C5.74736841,8.68029155 5.96842105,8.88739618 6.22105263,8.88739618 L13.7684211,8.88739618 C14.0210526,8.88739618 14.2421053,8.68029155 14.2421053,8.44360054 C14.2421053,8.20690954 14.0210526,7.9998049 13.7684211,7.9998049 Z M13.7684211,3.75746976 L6.22105263,3.75746976 C5.96842105,3.75746976 5.74736841,3.96457439 5.74736841,4.2012654 C5.74736841,4.4379564 5.96842105,4.64506104 6.22105263,4.64506104 L13.7684211,4.64506104 C14.0210526,4.64506104 14.2421053,4.4379564 14.2421053,4.2012654 C14.2421053,3.96457439 14.0210526,3.75746976 13.7684211,3.75746976 Z"
                                    id="形状结合"
                                    fill-rule="nonzero"
                                  ></path>
                                  <path
                                    d="M2.40000001,11.2543063 L1.45263159,11.2543063 L1.45263159,3.66871063 C1.45263159,2.78111935 2.24210528,2.04145994 3.18947368,2.04145994 L3.82105264,2.04145994 L3.82105264,2.92905122 L3.18947368,2.92905122 C2.74736842,2.92905122 2.39999999,3.25450135 2.40000001,3.66871063 L2.40000001,11.2543063 Z"
                                    id="路径"
                                    fill-rule="nonzero"
                                  ></path>
                                </g>
                              </g>
                            </g>
                          </svg>
                          <svg
                            v-else-if="data.icon === 'Share'"
                            width="17px"
                            height="19px"
                            viewBox="0 0 17 19"
                            version="1.1"
                            xmlns="http://www.w3.org/2000/svg"
                            xmlns:xlink="http://www.w3.org/1999/xlink"
                          >
                            <g
                              id="页面-1"
                              stroke="none"
                              stroke-width="1"
                              fill="none"
                              fill-rule="evenodd"
                            >
                              <g
                                id="首页"
                                transform="translate(-114, -458)"
                                fill="#6E747E"
                                fill-rule="nonzero"
                              >
                                <path
                                  d="M127.820709,470.424374 C126.811322,470.424663 125.862079,470.920443 125.26318,471.760145 L119.896345,468.915837 C120.367896,468.12317 120.491297,467.160757 120.235786,466.268523 L125.43443,463.455818 C126.517721,464.719971 128.352642,464.927718 129.675077,463.935937 C130.997511,462.944156 131.375379,461.076893 130.548359,459.620545 C129.721339,458.164197 127.959645,457.594597 126.476944,458.304155 C124.994243,459.013713 124.274979,460.770594 124.81467,462.364446 L119.669032,465.149761 C118.587687,463.748136 116.619213,463.500039 115.243608,464.592003 C113.868003,465.683966 113.592335,467.713477 114.623866,469.154647 C115.655396,470.595816 117.613887,470.917408 119.026847,469.877634 L124.735161,472.902082 C124.400274,474.263397 124.939185,475.694226 126.076479,476.463329 C127.213773,477.232432 128.698233,477.169923 129.771211,476.307747 C130.844189,475.445571 131.268675,473.974175 130.827731,472.645529 C130.386788,471.316884 129.177815,470.424474 127.81867,470.424374 L127.820709,470.424374 Z"
                                  id="形状"
                                ></path>
                              </g>
                            </g>
                          </svg>
                          <svg
                            v-else-if="data.icon === 'User'"
                            width="20px"
                            height="20px"
                            viewBox="0 0 20 20"
                            version="1.1"
                            xmlns="http://www.w3.org/2000/svg"
                            xmlns:xlink="http://www.w3.org/1999/xlink"
                          >
                            <g
                              id="页面-1"
                              stroke="none"
                              stroke-width="1"
                              fill="none"
                              fill-rule="evenodd"
                            >
                              <g id="首页" transform="translate(-114, -511)" fill="#6E747E">
                                <g id="编组" transform="translate(114, 511)">
                                  <path
                                    d="M15.650783,20 L4.34921695,20 C1.91372245,19.8861802 0,17.9584765 0,15.6190088 C0,13.279541 1.91372245,11.3518373 4.34921695,11.2380175 L15.650783,11.2380175 C18.0862775,11.3518373 20,13.279541 20,15.6190088 C20,17.9584765 18.0862775,19.8861802 15.650783,20 L15.650783,20 Z M10,10.1876417 C7.8524452,10.1881084 5.91610451,8.94722804 5.09404608,7.04372074 C4.27198765,5.14021345 4.72613639,2.94902245 6.24468699,1.49207266 C7.7632376,0.0351228752 10.0470736,-0.400603085 12.0310625,0.388108111 C14.0150513,1.17681931 15.3083969,3.0346113 15.3079105,5.0950494 C15.3045954,7.9062919 12.9301037,10.184461 10,10.1876417 L10,10.1876417 Z"
                                    id="形状"
                                    fill-rule="nonzero"
                                  ></path>
                                </g>
                              </g>
                            </g>
                          </svg>
                        </el-icon>
                        <span class="node-label" :title="data.label">{{ data.label }}</span>
                      </div>
                      <el-dropdown trigger="click" @command="handleLevel1Action" @click.stop>
                        <el-icon class="more-actions">
                          <more-one theme="outline" size="24" fill="#333" />
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
                    <div
                      v-else-if="data.level === 2 && data.label != 'CNKI文献（核心）' && data.label != 'CNKI文献（全部）'"
                      class="node-content level-2-content"
                    >
                      <div class="node-left">
                        <el-icon class="node-icon">
                          <svg
                            width="20px"
                            height="20px"
                            viewBox="0 0 20 20"
                            version="1.1"
                            xmlns="http://www.w3.org/2000/svg"
                            xmlns:xlink="http://www.w3.org/1999/xlink"
                          >
                            <g
                              id="图形"
                              stroke="none"
                              fill="none"
                              transform="translate(-0, 0)"
                              fill-rule="nonzero"
                            >
                              <path
                                d="M17.8125,4.06249966 L8.356875,4.06249966 L7.373125,2.223125 C7.1558601,1.81617827 6.73193787,1.56216138 6.270625,1.56249966 L2.1875,1.56249966 C1.498125,1.56249966 0.9375,2.123125 0.9375,2.8125 L0.9375,17.1875 C0.9375,17.876875 1.498125,18.4375 2.1875,18.4375 L17.8125,18.4375 C18.501875,18.4375 19.0625,17.876875 19.0625,17.1875 L19.0625,5.3125 C19.0625,4.623125 18.501875,4.06249966 17.8125,4.06249966 Z M2.1875,2.8125 L6.270625,2.8125 L7.6075,5.3125 L17.8125,5.3125 L17.8125,7.22625 C17.804375,7.22625 17.796875,7.22375 17.78875,7.22375 L2.211875,7.22375 C2.20375,7.22375 2.19625,7.22625 2.1875,7.22625 L2.1875,2.8125 Z M2.1875,17.1875 L2.1875,15.3125 L2.211875,8.47375 L17.8125,8.4975 L17.8125,15.3125 L17.81375,15.3125 L17.81375,17.1875 L2.1875,17.1875 Z"
                                id="形状"
                                fill="#F1BD1E"
                              ></path>
                            </g>
                          </svg>
                        </el-icon>
                        <span class="node-label" :title="data.label">{{ data.label }}</span>
                        <span class="doc-count">({{ data.documentCount || 0 }})</span>
                      </div>

                      <!-- 知识库操作按钮 -->
                      <el-dropdown trigger="click" @command="handleKBAction" @click.stop>
                        <el-icon class="more-actions">
                          <MoreOne />
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
                    <div
                      v-else-if="data.level === 3 || data.label == 'CNKI文献（核心）' || data.label == 'CNKI文献（全部）'"
                      class="node-content level-3-content"
                    >
                      <el-icon class="node-icon">
                        <svg
                          width="20px"
                          height="20px"
                          viewBox="0 0 20 20"
                          version="1.1"
                          xmlns="http://www.w3.org/2000/svg"
                          xmlns:xlink="http://www.w3.org/1999/xlink"
                        >
                          <g
                            id="图形"
                            stroke="none"
                            fill="none"
                            fill-rule="evenodd"
                            stroke-width="1"
                          >
                            <g id="编组" transform="translate(3.125, 1.25)" fill="#6E747E">
                              <path
                                d="M13.5664062,4.38671875 L9.36328125,0.18359375 C9.24609375,0.06640625 9.08789062,0 8.921875,0 L0.625,0 C0.279296875,0 0,0.279296875 0,0.625 L0,16.875 C0,17.2207031 0.279296875,17.5 0.625,17.5 L13.125,17.5 C13.4707031,17.5 13.75,17.2207031 13.75,16.875 L13.75,4.83007812 C13.75,4.6640625 13.6835938,4.50390625 13.5664062,4.38671875 Z M12.3085938,5.1171875 L8.6328125,5.1171875 L8.6328125,1.44140625 L12.3085938,5.1171875 Z M12.34375,16.09375 L1.40625,16.09375 L1.40625,1.40625 L7.3046875,1.40625 L7.3046875,5.625 C7.3046875,6.078125 7.671875,6.4453125 8.125,6.4453125 L12.34375,6.4453125 L12.34375,16.09375 Z"
                                id="形状"
                                fill-rule="nonzero"
                              ></path>
                              <path
                                d="M6.71875,10.8203125 L3.125,10.8203125 C3.0390625,10.8203125 2.96875,10.890625 2.96875,10.9765625 L2.96875,11.9140625 C2.96875,12 3.0390625,12.0703125 3.125,12.0703125 L6.71875,12.0703125 C6.8046875,12.0703125 6.875,12 6.875,11.9140625 L6.875,10.9765625 C6.875,10.890625 6.8046875,10.8203125 6.71875,10.8203125 Z M2.96875,8.3203125 L2.96875,9.2578125 C2.96875,9.34375 3.0390625,9.4140625 3.125,9.4140625 L10.625,9.4140625 C10.7109375,9.4140625 10.78125,9.34375 10.78125,9.2578125 L10.78125,8.3203125 C10.78125,8.234375 10.7109375,8.1640625 10.625,8.1640625 L3.125,8.1640625 C3.0390625,8.1640625 2.96875,8.234375 2.96875,8.3203125 Z"
                                id="形状"
                                fill-rule="nonzero"
                              ></path>
                            </g>
                          </g>
                        </svg>
                      </el-icon>
                      <span class="node-label" :title="data.label">{{ data.label }}</span>
                      <span class="file-size">{{
                        data.label == 'CNKI文献（核心）' ? '' : data.label == 'CNKI文献（全部）' ? '' : formatFileSize(data.size)
                      }}</span>
                    </div>
                  </div>
                </template>
              </el-tree>
            </div>
            <!-- 折叠按钮 -->
            <div class="collapse-btn" @click="toggleCollapse">
              <el-icon :size="20"><DArrowLeft /></el-icon>
            </div>
          </div>
        </el-aside>
      </transition>

      <!-- 展开按钮（侧边栏折叠时显示） -->
      <div v-if="isCollapsed" class="expand-btn" @click="toggleCollapse">
        <el-icon :size="20"><DArrowRight /></el-icon>
      </div>

      <el-container>
        <el-header class="header">
          <div style="height: 100%; display: flex; align-items: center">
            <div class="history-icon" @click="openHistoryPanel">
              <history theme="outline" size="18" fill="#333" style="height: 18px;"/>
            </div>

            <span style="display: flex; align-items: center; width: 100%">
              <el-dropdown trigger="click" @command="handleUserCommand">
                <div class="user-info">
                  <el-badge is-dot v-show="notRead" style="display: flex; align-items: center;">
                    <span class="username">{{ user.userInfo?.username }}</span>
                  </el-badge>

                  <span class="username" v-show="!notRead">{{ user.userInfo?.username }}</span>

                  <el-icon class="dropdown-icon">
                    <ArrowDown />
                  </el-icon>
                </div>

                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="messages">
                      <el-icon><MessageIcon /></el-icon>
                      <el-badge is-dot v-show="notRead"> 消息通知 </el-badge>
                      <span v-show="!notRead"> 消息通知 </span>
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </span>
          </div>

          <el-drawer
            v-model="drawer"
            :beforeClose="closeDrawer"
            title="消息中心"
            direction="rtl"
            class="message-drawer"
          >
            <div
              v-loading="msgLoading"
              style="display: flex; flex-direction: column; gap: 12px; min-height: 100px"
            >
              <MessageCard
                v-for="item in messages"
                :key="item.log_id"
                :msg="item.msg"
                @click="() => readMsg(item.log_id)"
                :create-time="item.create_time"
                :log-read="item.log_read"
              />
            </div>
          </el-drawer>

          <!-- 历史对话面板 -->
          <el-drawer
            v-model="showHistoryPanel"
            :title="`历史聊天记录 - ${currentUsername}`"
            direction="rtl"
            :before-close="closeHistoryPanel"
            class="history-drawer"
          >
            <ChatHistoryPanel
              v-if="showHistoryPanel && currentUserId"
              ref="ChatHistoryPanelRef"
              :user-id="currentUserId"
              :username="currentUsername"
            />
          </el-drawer>

          <!-- 创建知识库对话框 -->
          <el-dialog 
            v-model="showCreateKBDialog" 
            title="创建知识库" 
            width="500px"
            :close-on-click-modal="false"
            class="kb-dialog"
          >
            <el-form :model="newKB" label-width="80px">
              <el-form-item label="名称" required>
                <el-input 
                  v-model="newKB.name" 
                  placeholder="请输入知识库名称" 
                  maxlength="50"
                  show-word-limit
                />
              </el-form-item>
            </el-form>

            <template #footer>
              <el-button @click="showCreateKBDialog = false">取消</el-button>
              <el-button 
                type="primary" 
                @click="createKnowledgeBase" 
                :loading="createKBLoading"
                :disabled="!newKB.name.trim()"
              >
                确认创建
              </el-button>
            </template>
          </el-dialog>

          <!-- 重命名知识库对话框 -->
          <el-dialog
            v-model="showRenameDialog"
            title="重命名知识库"
            width="500px"
            :close-on-click-modal="false"
            class="kb-dialog"
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
              <el-button @click="showRenameDialog = false">取消</el-button>
              <el-button 
                type="primary" 
                @click="confirmRename" 
                :disabled="!renameForm.name.trim()"
              >
                确认重命名
              </el-button>
            </template>
          </el-dialog>

          <!-- 共享设置弹窗 -->
          <el-dialog
            v-model="showShareModal"
            :title="`共享设置 - ${currentDatasetName}`"
            width="80%"
            top="8vh"
            :close-on-click-modal="false"
            class="kb-dialog"
          >
            <ShareSettings
              v-if="showShareModal"
              :dataset-id="currentDatasetId"
              :dataset-name="currentDatasetName"
              @close="showShareModal = false"
            />
          </el-dialog>

          <!-- 文档管理弹窗 -->
          <el-dialog
            v-model="showDocumentModal"
            :title="`文档管理 - ${currentDatasetName}`"
            width="90%"
            top="5vh"
            :close-on-click-modal="false"
            class="kb-dialog"
          >
            <DocumentManagement
              :dataset-id="currentDatasetId"
              :dataset-name="currentDatasetName"
              @close="showDocumentModal = false"
              @document-changed="handleDocumentChanged"
            />
            <template #footer>
              <el-button @click="showDocumentModal = false">关闭</el-button>
            </template>
          </el-dialog>
        </el-header>
        <el-main>
          <HomePage v-if="isHomePage" @start-chat="isHomePage = false" />
          <ChatPage 
            v-else 
            :selected-documents="selectedDocuments"
            :selected-datasets="selectedDatasets"
            :tree-data="treeData"
            :selected-model-id="selectedModelId"
            @manage-selection="handleManageSelection"
            @clear-selection="handleClearSelection"
          />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import {
  ArrowDown,
  Check,
  Close,
  DArrowLeft,
  DArrowRight,
  Delete,
  DocumentCopy,
  Edit,
  EditPen,
  Folder,
  FolderRemove,
  Message as MessageIcon,
  Plus,
  Refresh,
  Search,
  Share,
  Sort,
  SwitchButton,
  Timer,
  View
} from '@element-plus/icons-vue'
import { computed, nextTick, onBeforeMount, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import documentApi from '@/api/document'
import datasetApi from '@/api/dataset'
import useStore from '@/stores'
import { getMessages, type Message, readMessage } from '@/api/messages'
import MessageCard from '@/layout/layout-template/MessageCard.vue'
import modelApi from '@/api/model'
import { MoreOne, HomeTwo, History } from '@icon-park/vue-next'
import HomePage from '@/views/user-home/components/HomePage.vue'
import ChatPage from '@/views/user-home/components/ChatPage.vue'
import ChatHistoryPanel from '@/views/user-manage/component/ChatHistoryPanel.vue'
import DocumentManagement from '@/views/user-knowledge/components/DocumentManagement.vue'
import ShareSettings from '@/views/user-knowledge/components/ShareSettings.vue'

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

const router = useRouter()
const { user } = useStore()
const isHomePage = ref(true)
const drawer = ref(false)
const messages = ref<Message[]>([])
const userRole = computed(() => user.getRole())
const selectedNode = ref<TreeNode | null>(null)
const isAdmin = computed(() => userRole.value === 'ADMIN')
const isCollapsed = ref(false)

// 新建知识库相关
const showCreateKBDialog = ref(false)
const createKBLoading = ref(false)
const newKB = ref({
  name: ''
})

// 切换侧边栏折叠状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
const personalKBSortType = ref<'time' | 'name'>('time') // 默认按时间排序（创建时间倒排）
const sharedKBSortType = ref<'time' | 'name'>('time') // 共享知识库排序类型
const organizationKBSortType = ref<'time' | 'name'>('time') // 机构知识库排序类型
const treeRef = ref<any>(null)
const sharedKBs = ref<any[]>([])
const organizationKBs = ref<any[]>([])
const searchText = ref('')
const selectedKB = ref<TreeNode | null>(null)
const personalKBs = ref<any[]>([])
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

// 树形组件配置
const treeProps = {
  children: 'children',
  label: 'label'
}

const goToHome = () => {
  isHomePage.value = true
}

const useLoading = () => {
  const loading = ref(false)

  const setLoading = (value: boolean) => {
    loading.value = value
  }

  return {
    loading,
    setLoading
  }
}

const { loading: msgLoading, setLoading: setMsgLoading } = useLoading()

const { loading: notRead, setLoading: setNotRead } = useLoading()

// 打开消息通知抽屉
const openDrawer = async () => {
  drawer.value = true
  await loadMessages(true)
}

// 关闭消息通知抽屉
const closeDrawer = () => {
  drawer.value = false
  loadMessages(false)
}

const loadMessages = async (isLoading: boolean) => {
  if (isLoading) {
    setMsgLoading(true)
  }
  setNotRead(false)
  const result = await getMessages()
  if (result.code === 200) {
    messages.value = result.data
    if (!messages.value.some((item) => !item.log_read)) {
      setNotRead(false)
    } else {
      setNotRead(true)
    }
  }
  if (isLoading) {
    setMsgLoading(false)
  }
}

let interval: any
onMounted(() => {
  loadMessages(false)
  interval = setInterval(() => {
    loadMessages(false)
  }, 60000)
})
onBeforeMount(() => {
  clearInterval(interval)
})

// 已读回调
const readMsg = async (log_id: string) => {
  const result = await readMessage(log_id)
  if (result.code === 200) {
    messages.value = messages.value.map((item) => {
      if (item.log_id === log_id) {
        item.log_read = true
      }
      return item
    })
  }
}

// 处理用户下拉菜单命令
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'messages':
      await openDrawer()
      break
    case 'profile':
      ElMessage.info('个人信息功能开发中...')
      break
    case 'settings':
      ElMessage.info('设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '退出确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        await user.logout()
        router.push('/login')
        ElMessage.success('已退出登录')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('退出登录失败')
        }
      }
      break
  }
}

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

// 方法
const selectKnowledgeBase = (kb: TreeNode) => {
  selectedKB.value = kb
  // 清空之前的对话
  // chatMessages.value = [] // 临时注释，测试消息保持
}

// 显示文档详情
const showDocumentDetail = (document: TreeNode) => {
  console.log('显示文档详情:', document)
  // 这里可以在主内容区域显示文档详情
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

// 处理节点展开
const handleNodeExpand = async (data: TreeNode) => {
  // 如果是二级节点（知识库）且还没有加载文档，则加载文档
  if (data.level === 2 && data.datasetId && (!data.children || data.children.length === 0)) {
    await loadDocuments(data.datasetId, data.id)
  }
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

// 用于触发 computed 重新计算的版本号 (必须在 computed 使用之前定义)
const checkVersion = ref(0)

// 获取选中的文档节点
const getSelectedDocuments = (): TreeNode[] => {
  const checkedNodes = treeRef.value?.getCheckedNodes() || []
  console.log('所有勾选的节点:', checkedNodes.map((n: TreeNode) => ({ 
    label: n.label, 
    level: n.level, 
    type: n.type,
    datasetId: n.datasetId, 
    documentId: n.documentId 
  })))
  // 文档节点：level=3 或者特殊的CNKI知识库（摘要和全文）
  const CNKI_DATASET_ID = 'd1f6f1cc-b3c3-11f0-9ffe-1df6b9a97505'
  const CNKI_FULL_DATASET_ID = 'd1f6f1cc-b3c3-11f0-9ffe-1df6b9a97506'
  const docs = checkedNodes.filter((node: TreeNode) => 
    node.level === 3 || 
    node.id === CNKI_DATASET_ID || 
    node.id === CNKI_FULL_DATASET_ID
  )
  console.log('过滤后的文档节点:', docs.length, '个')
  return docs
}

// 为模板提供 computed 包装 (依赖 checkVersion 触发重新计算)
const selectedDocuments = computed(() => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _ = checkVersion.value // 依赖此变量触发重新计算
  return getSelectedDocuments()
})

// 获取选中的知识库节点
const getSelectedDatasets = (): TreeNode[] => {
  const checkedNodes = treeRef.value?.getCheckedNodes() || []
  // 知识库节点：level=2
  const datasets = checkedNodes.filter((node: TreeNode) => node.level === 2)
  console.log('过滤后的知识库节点:', datasets.length, '个')
  return datasets
}

// 为模板提供 computed 包装 (依赖 checkVersion 触发重新计算)
const selectedDatasets = computed(() => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _ = checkVersion.value // 依赖此变量触发重新计算
  return getSelectedDatasets()
})

// 处理管理选择
const handleManageSelection = () => {
  ElMessage.info('请在左侧知识库树中选择或取消选择')
}

// 处理清空选择
const handleClearSelection = () => {
  if (treeRef.value) {
    // 获取所有当前选中的节点键
    const allCheckedKeys = treeRef.value.getCheckedKeys() || []
    const halfCheckedKeys = treeRef.value.getHalfCheckedKeys() || []
    
    console.log('清空前选中的节点:', allCheckedKeys.length, '个', allCheckedKeys)
    console.log('清空前半选中的节点:', halfCheckedKeys.length, '个', halfCheckedKeys)
    
    // 方法1: 遍历所有节点，逐个取消选中
    const store = treeRef.value.store
    if (store && store.nodesMap) {
      Object.values(store.nodesMap).forEach((node: any) => {
        if (node.checked || node.indeterminate) {
          node.setChecked(false, false)
        }
      })
    }
    
    // 方法2: 使用 setCheckedKeys 清空
    treeRef.value.setCheckedKeys([], false)
    
    // 强制刷新树的状态
    nextTick(() => {
      checkVersion.value++ // 清空后也触发更新
      console.log('清空后选中的节点:', treeRef.value?.getCheckedKeys()?.length || 0, '个')
    })
  }
}

// 处理复选框选择
const handleNodeCheck = (data: TreeNode, checkInfo: any) => {
  // 获取所有选中的节点
  const checkedNodes = treeRef.value?.getCheckedNodes() || []
  const checkedKeys = treeRef.value?.getCheckedKeys() || []

  // 分类统计选中的项目
  const selectedStats = getSelectedStats()
  
  // 触发 computed 重新计算
  checkVersion.value++
}

const showRenameDialog = ref(false)
const currentDatasetId = ref('')
const showShareModal = ref(false)
const showDocumentModal = ref(false)
const currentDatasetName = ref('')
const renameForm = ref({
  id: '',
  name: '',
  oldName: '' // 保存原始名称，用于日志和验证
})

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

// 确认重命名知识库
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

    const response = await datasetApi.putDataset(renameForm.value.id, updateData)

    if (response.code === 200) {
      ElMessage.success('知识库重命名成功')

      // 更新本地数据
      const updatedKB = personalKBs.value.find((kb) => kb.id === renameForm.value.id)
      if (updatedKB) {
        updatedKB.name = newName
        updatedKB.description = newName
        updatedKB.desc = newName
      }

      showRenameDialog.value = false

      // 重新排序并更新树
      await sortPersonalKBs()
    } else {
      ElMessage.error(response.message || '重命名失败')
    }
  } catch (error: any) {
    console.error('重命名失败:', error)
    ElMessage.error('重命名失败，请稍后重试')
  }
}

// 处理文档变化事件
const handleDocumentChanged = async () => {
  try {
    // 刷新当前知识库的文档列表
    if (currentDatasetId.value) {
      // 查找当前知识库所在的类型
      for (const category of treeData.value) {
        const kbNode = category.children?.find(
          (child) => child.datasetId === currentDatasetId.value
        )
        if (kbNode) {
          // 重新加载该知识库的文档
          await loadDocuments(currentDatasetId.value, kbNode.id)
          break
        }
      }
    }
  } catch (error) {
    console.error('刷新文档列表失败:', error)
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

      orgKBsList.push({
        id: 'd1f6f1cc-b3c3-11f0-9ffe-1df6b9a97505',
        name: 'CNKI文献（核心）',
        create_time: '2024-01-01T00:00:00Z',
        creator: '系统集成'
      })

      orgKBsList.push({
        id: 'd1f6f1cc-b3c3-11f0-9ffe-1df6b9a97506',
        name: 'CNKI文献（全部）',
        create_time: '2024-01-01T00:00:00Z',
        creator: '系统集成'
      })

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

// 打开创建知识库对话框
const openCreateKBDialog = () => {
  newKB.value = { name: '' }
  showCreateKBDialog.value = true
}

// 创建知识库
const createKnowledgeBase = async () => {
  if (!newKB.value.name.trim()) {
    ElMessage.warning('请输入知识库名称')
    return
  }

  createKBLoading.value = true

  try {
    // 获取默认的 embedding 模型
    let embeddingModeId = ''
    try {
      const modelRes = await modelApi.getModel({ model_type: 'EMBEDDING' })
      const modelList = modelRes.data || []
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

    // 调用API创建知识库
    const newKnowledgeBase = {
      name: newKB.value.name.trim(),
      desc: newKB.value.name.trim(), // 描述默认使用名称
      type: '0', // 默认类型为普通知识库
      embedding_mode_id: embeddingModeId
    }

    await datasetApi.postDataset(newKnowledgeBase)

    ElMessage.success('知识库创建成功')

    // 重置表单并关闭对话框
    newKB.value = { name: '' }
    showCreateKBDialog.value = false

    // 刷新个人知识库列表
    await loadPersonalKBs()
  } catch (error) {
    console.error('创建知识库失败:', error)
    ElMessage.error('知识库创建失败')
  } finally {
    createKBLoading.value = false
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

// 排序个人知识库
const sortPersonalKBs = async () => {
  try {
    // 即使是空列表也需要更新树，确保树能反映最新状态
    if (personalKBs.value.length === 0) {
      await updateTreeData('my', [])
      return
    }

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
          .filter((doc: any) => doc.is_active !== false && doc.status == 'nn2')
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

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (!bytes) return '-'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}
const selectedModelId = ref('')
const currentUserId = ref('')
const currentUsername = ref('')

// 历史对话相关状态
const showHistoryPanel = ref(false)
const ChatHistoryPanelRef = ref<any>(null)

// 打开历史对话面板
const openHistoryPanel = () => {
  showHistoryPanel.value = true
}

// 关闭历史对话面板
const closeHistoryPanel = () => {
  showHistoryPanel.value = false
}

// 获取当前用户信息
const getCurrentUserInfo = () => {
  const userInfo = user.userInfo
  if (userInfo) {
    currentUserId.value = userInfo.id || ''
    currentUsername.value = userInfo.username || ''
  }
}

const modelsLoading = ref(false)
const availableModels = ref<any[]>([])

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

// STT相关状态
const sttModelEnabled = ref(false)
const sttAutoSend = ref(false)
const availableSTTModels = ref<any[]>([])
const selectedSTTModelId = ref('')

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

// 检查上传文档是否完成
const checkUploadCompletion = async (datasetId: string): Promise<boolean> => {
  // 定义状态常量
  const PENDING = 'nn0'
  const STARTED = 'nn1'
  const SUCCESS = 'nn2'
  const FAILURE = 'nn3'
  const REVOKE = 'nn4'
  const REVOKED = 'nn5'

  try {
    const params = {
      current_page: 1,
      page_size: 50
    }
    const response = await documentApi.getDocument(datasetId, params, params)

    if (response.data && response.data.records.length > 0) {
      const records = response.data.records

      // 检查是否有任何文档仍在等待或执行中
      const hasPendingOrStarted = records.some(
        (record: any) => record.status === PENDING || record.status === STARTED
      )

      if (hasPendingOrStarted) {
        // 仍有文档在处理中，继续等待
        console.log('文档仍在处理中，继续等待...')
        return true
      }

      // 所有文档已完成处理，清除定时器
      if (uploadCheckTimer) {
        await loadPersonalKBs()
        window.localStorage.removeItem('uploading_dataset_id')
      }

      // 重新判断所有文档的最终状态
      const allSuccess = records.every((record: any) => record.status === SUCCESS)
      const hasFailure = records.some((record: any) => record.status === FAILURE)
      const hasRevoked = records.some((record: any) => record.status === REVOKED)
      const hasRevoke = records.some((record: any) => record.status === REVOKE)

      if (allSuccess) {
        await loadPersonalKBs()
        ElMessage.success('上传成功：所有文档处理完成')
      } else if (hasFailure) {
        await loadPersonalKBs()
        ElMessage.error('上传失败：部分或全部文档处理失败')
      } else if (hasRevoked) {
        ElMessage.warning('上传已取消')
      } else if (hasRevoke) {
        ElMessage.warning('上传正在取消中')
      } else {
        ElMessage.info('上传状态未知，请检查文档详情')
      }

      return false
    } else {
      console.error('获取文档列表失败，响应数据异常')
      return false
    }
  } catch (error) {
    console.error('检查上传状态失败:', error)
    ElMessage.error('检查上传状态失败')
    return false
  }
}

let uploadCheckTimer: number | null = null

onMounted(async () => {
  // 获取当前用户信息
  getCurrentUserInfo()

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

  // 启动上传状态检查定时器
  if (!uploadCheckTimer) {
    uploadCheckTimer = window.setInterval(() => {
      const uploadDatasetId = window.localStorage.getItem('uploading_dataset_id')
      if (!uploadDatasetId) return
      checkUploadCompletion(uploadDatasetId)
    }, 6000)
  }
})

// 清理上传状态检查定时器
onBeforeUnmount(() => {
  if (uploadCheckTimer) {
    clearInterval(uploadCheckTimer)
    uploadCheckTimer = null
  }
})
</script>

<style lang="scss" scoped>
// 知识库弹窗主题色样式
:deep(.kb-dialog) {
  .el-dialog__header {
    padding: 16px 20px;
    margin-right: 0;
    border-bottom: 1px solid #ebeef5;
    
    .el-dialog__title {
      font-weight: 600;
      font-size: 16px;
      color: #303133;
    }
  }
  
  .el-dialog__body {
    padding: 24px;
  }
  
  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid #ebeef5;
    
    .el-button--primary {
      background-color: #554BDB;
      border-color: #554BDB;
      
      &:hover,
      &:focus {
        background-color: #6B62E0;
        border-color: #6B62E0;
      }
    }
  }
}

:deep(.el-button--primary) {
  --el-color-primary: v-bind('user.themeInfo?.theme || "#5f55e5"');
  --el-button-bg-color: v-bind('user.themeInfo?.theme || "#5f55e5"');
  --el-button-border-color: v-bind('user.themeInfo?.theme || "#5f55e5"');
  
  &:hover,
  &:focus {
    --el-button-hover-bg-color: v-bind('user.themeInfo?.theme || "#5f55e5"');
    --el-button-hover-border-color: v-bind('user.themeInfo?.theme || "#5f55e5"');
    opacity: 0.8;
  }
}

* {
  --text-hover-color: v-bind('user.themeInfo?.theme || "rgb(95, 85, 229)"');
}

.line-split {
  height: 1px;
  background: rgb(209, 214, 226);
  margin: 10px 10px;
}

.common-layout {
  height: 100vh;
  width: 100vw;

  .icon-box {
    width: 100%;
    display: flex;
    justify-content: space-around;
    align-items: center;

    .logo-img {
      height: 60px;
    }

    .home-icon {
      cursor: pointer;
    }
    .home-icon:hover {
      color: #409eff;
    }
  }

  .input-box {
    display: flex;
    justify-content: center;
    margin-top: 18px;

    :deep(.el-input__wrapper) {
      background: #fff;
    }

    :deep(.el-input__wrapper.is-focused) {
      border-color: var(--text-hover-color);
    }
  }

  .add-btn {
    display: flex;
    justify-content: center;
    margin-top: 14px;
  }

  .home-item {
    &:hover {
      color: var(--text-hover-color);
      background: #eaebff;

      :deep(path) {
        fill: var(--text-hover-color);
      }
    }
    cursor: pointer;
    display: flex;
    padding: 10px 0;
    justify-content: center;
    margin-top: 14px;

    .home-item-box {
      width: 240px;
      display: flex;
      justify-content: space-between;

      .arrow-icon {
        display: flex;
        align-items: center;
      }
    }

    .item-icon {
      display: flex;
      align-content: center;
      justify-content: center;

      div,
      span {
        font-size: 16px;
        margin-left: 6px;
        display: flex;
        align-items: center;
      }

      svg {
        color: transparent !important;
        #首页 {
          fill: #626972;
        }
      }
    }
  }

  .header {
    border-bottom: 1px solid rgb(237, 237, 237);
    display: flex;
    justify-content: flex-end;
    align-content: center;

    :deep(.el-dropdown) {
      display: flex;
      align-content: center;
    }

    .user-info {
      height: fit-content;
      display: flex;
      align-items: center;

      .dropdown-icon {
        margin-left: 14px;
        display: flex;
        align-items: center;
      }
    }

    .history-icon {
      height: fit-content;
      display: flex;
      align-items: center;
      margin-right: 10px;
      cursor: pointer;

      &:hover {
        color: #409eff;
      }
    }
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

    :deep(.el-tree-node .is-checked),
    :deep(.el-tree-node .is-indeterminate) {
      .el-tree-node__content {
        background: #eaebff;
      }
      .el-checkbox__inner {
        background: var(--text-hover-color);
        border-color: var(--text-hover-color);
        color: var(--text-hover-color);
      }
    }

    :deep(.el-tree-node) {
      margin-bottom: 4px;

      .el-tree-node__content {
        margin-top: 4px;
        height: auto;
        padding: 4px 0;
        background: transparent;
        border-radius: 6px;

        &:hover {
          background: #edf2fe !important;
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

    :deep(.is-checked path) {
      fill: var(--text-hover-color);
    }
  }

  .tree-node {
    width: 80%;
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

      .node-left {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
        min-width: 0;
      }

      .node-icon {
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

.container {
  display: flex;
  flex-direction: column;
  height: 100vh; /* 或具体高度如 500px */
  position: relative;
}

.first {
  height: fit-content; /* 根据内容自适应 */
}

.second {
  flex: 1; /* 铺满剩余高度 */
}

.collapse-btn {
  position: absolute;
  right: 20px;
  bottom: 20px;
  width: 48px;
  height: 48px;
  background: #ffffff;
  border: 1px solid #e0e0e6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  transition: all 0.2s ease;

  &:hover {
    background: #f5f5f7;
    border-color: #d0d0d6;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: scale(1.1);

    .el-icon {
      color: #303133;
    }
  }

  &:active {
    transform: scale(0.95);
  }

  .el-icon {
    font-size: 12px;
    color: #606266;
    transition: color 0.2s ease;
  }
}

.expand-btn {
  position: fixed;
  left: 20px;
  bottom: 20px;
  width: 48px;
  height: 48px;
  background: #ffffff;
  border: 1px solid #e0e0e6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 999;
  transition: all 0.2s ease;

  &:hover {
    background: #f5f5f7;
    border-color: #d0d0d6;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: scale(1.1);

    .el-icon {
      color: #303133;
    }
  }

  &:active {
    transform: scale(0.95);
  }

  .el-icon {
    font-size: 12px;
    color: #606266;
    transition: color 0.2s ease;
  }
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}
</style>

<!-- 抽屉统一样式 -->
<style lang="scss">
.message-drawer,
.history-drawer {
  .el-drawer__header {
    background: linear-gradient(135deg, #554BDB 0%, #7B6FE8 100%);
    margin-bottom: 0;
    padding: 16px 20px;
    
    .el-drawer__title {
      color: #ffffff;
      font-weight: 600;
      font-size: 16px;
    }
    
    .el-drawer__close-btn {
      color: rgba(255, 255, 255, 0.85);
      
      &:hover {
        color: #ffffff;
      }
    }
  }
  
  .el-drawer__body {
    padding: 16px;
    background: #ffffff;
  }
}
</style>