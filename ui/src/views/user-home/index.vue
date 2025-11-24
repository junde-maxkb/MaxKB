<template>
  <div class="home-container">
    <div>
      <img src="https://picsum.photos/1455/218">
    </div>
    <h2 style="margin-top: 24px">
      您好，欢迎进入AI知识库系统～
    </h2>

    <div style="margin-top: 20px; color: rgb(146, 146, 146); font-size: 16px;">
      中国教育科学研究院 AI 知识库系统是一款聚焦教育科研领域的智能知识管理与应用平台，整合三大核心知识库模块，融合 AI 技术赋能高效知识交互。
    </div>
    <div class="home-card" >
      <h2>
        核心知识库模块
      </h2>
      <ul>
        <li>
          机构知识库：汇聚中国教育科学研究院各类科研成果、政策文件、研究报告等核心资源，实现机构知识资产的系统化沉淀与管理。
        </li>
        <li>
          共享知识库：搭建开放共享的知识交流空间，支持跨部门、跨领域的知识流通，促进科研经验与成果的共建共用。
        </li>
        <li>
          我的知识库：提供个性化知识存储功能，用户可自定义收藏、整理专属知识内容，打造私人化知识管理中心。
        </li>
      </ul>
    </div>
    <div class="home-card" >
      <h2>
        核心知识库模块
      </h2>
      <ul>
        <li>
          机构知识库：汇聚中国教育科学研究院各类科研成果、政策文件、研究报告等核心资源，实现机构知识资产的系统化沉淀与管理。
        </li>
        <li>
          共享知识库：搭建开放共享的知识交流空间，支持跨部门、跨领域的知识流通，促进科研经验与成果的共建共用。
        </li>
        <li>
          我的知识库：提供个性化知识存储功能，用户可自定义收藏、整理专属知识内容，打造私人化知识管理中心。
        </li>
      </ul>
    </div>

    <div class="btn">
      <el-button type="primary">
        新手指南<el-icon class="el-icon--right"><ArrowRight /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()

const goToHome = () => {
  router.push('/user-home')
}
</script>

<style lang="scss" scoped>
.home-container {
  width: 100%;
  overflow: hidden;
  .home-card {
    margin-top: 16px;
    padding: 10px 18px;
    border-radius:11px;
    background:rgba(223, 234, 251, .4);
  }

  ul {
    margin-left: 16px;
    li {
      list-style: disc;  /* 实心圆点 */
      color: rgba(146, 146, 146, 1);
      font-family: SourceHanSansCN-Regular;
      font-weight: 400;
      font-size: 16px;
      line-height: 32px;
    }
  }

  .btn {
    display: flex;
    justify-content: center;
    margin-top: 16px;
  }
}
</style>
