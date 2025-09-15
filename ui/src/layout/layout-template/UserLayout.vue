<template>
  <div class="user-layout">
    <div class="user-header">
      <div class="header-left">
        <div class="logo">
          <img src="@/assets/JKY.png" alt="JKY" class="logo-img" />
        </div>
      </div>
      
      <div class="header-center">
        <nav class="user-nav">
          <router-link
            v-for="tab in userTabs"
            :key="tab.path"
            :to="tab.path"
            class="nav-item"
            :class="{ active: $route.path === tab.path }"
          >
            <el-icon class="nav-icon">
              <component :is="tab.icon" />
            </el-icon>
            <span class="nav-text">{{ tab.title }}</span>
          </router-link>
        </nav>
      </div>
      
      <div class="header-right">
        <el-dropdown trigger="click" @command="handleUserCommand">
          <div class="user-info">
            <el-avatar :size="32" class="user-avatar">
              {{ user.userInfo?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <span class="username">{{ user.userInfo?.username }}</span>
            <el-icon class="dropdown-icon">
              <ArrowDown />
            </el-icon>
          </div>
          
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人信息
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <div class="user-main">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  House,
  Document,
  ChatDotSquare,
  ArrowDown,
  User,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'
import useStore from '@/stores'

const router = useRouter()
const { user } = useStore()

// 用户导航标签
const userTabs = ref([
  {
    path: '/user-home',
    title: '首页',
    icon: 'House'
  },
  {
    path: '/user-knowledge',
    title: '知识库',
    icon: 'Document'
  },
  {
    path: '/user-ai-apps',
    title: 'AI应用',
    icon: 'ChatDotSquare'
  }
])

// 处理用户下拉菜单命令
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能开发中...')
      break
    case 'settings':
      ElMessage.info('设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '退出确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
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
</script>

<style lang="scss" scoped>
.user-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.user-header {
  height: 64px;
  background: #ffffff;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-left {
  .logo {
    display: flex;
    align-items: center;
    
    .logo-img {
      height: 40px;
      width: auto;
      max-width: 120px;
      object-fit: contain;
    }
  }
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
  
  .user-nav {
    display: flex;
    gap: 4px;
    background: #f8fafc;
    padding: 4px;
    border-radius: 8px;
    border: 1px solid #e9ecef;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
    
    .nav-item {
      display: flex;
      align-items: center;
      padding: 8px 16px;
      border-radius: 6px;
      text-decoration: none;
      color: #4a5568;
      transition: all 0.3s ease;
      font-weight: 500;
      font-size: 14px;
      
      &:hover {
        color: var(--el-color-primary);
        background: rgba(64, 158, 255, 0.08);
      }
      
      &.active {
        color: #ffffff;
        background: var(--el-color-primary);
        box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
      }
      
      .nav-icon {
        margin-right: 6px;
        font-size: 16px;
      }
      
      .nav-text {
        font-size: 14px;
      }
    }
  }
}

.header-right {
  .user-info {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 6px 12px;
    border-radius: 6px;
    transition: all 0.3s ease;
    
    &:hover {
      background: #f5f7fa;
    }
    
    .user-avatar {
      margin-right: 8px;
      background: #3370ff;
      color: white;
      font-weight: 600;
    }
    
    .username {
      margin-right: 8px;
      color: #303133;
      font-weight: 500;
    }
    
    .dropdown-icon {
      color: #909399;
      font-size: 12px;
      transition: transform 0.3s ease;
    }
    
    &:hover .dropdown-icon {
      transform: rotate(180deg);
    }
  }
}

.user-main {
  flex: 1;
  overflow: hidden;
}

@media (max-width: 768px) {
  .user-header {
    padding: 0 16px;
    
    .header-center .user-nav {
      gap: 4px;
      
      .nav-item {
        padding: 6px 12px;
        
        .nav-text {
          display: none;
        }
      }
    }
    
    .username {
      display: none !important;
    }
  }
}

@media (max-width: 480px) {
  .header-left .logo .logo-img {
    max-width: 80px;
    height: 32px;
  }
  
  .header-center .user-nav {
    .nav-item {
      padding: 6px 8px;
    }
  }
}
</style>
