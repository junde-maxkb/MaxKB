<template>
  <div class="animation-demo">
    <div class="demo-header">
      <h1>🎬 MaxKB 动画系统演示</h1>
      <p>右下角弹出式动画效果</p>
    </div>
    
    <div class="demo-content">
      <!-- 动画说明 -->
      <div class="demo-section">
        <h2>✨ 动画特性</h2>
        <div class="features">
          <div class="feature-item">
            <h3>🎯 右下角定位</h3>
            <p>动画不再全屏覆盖，而是优雅地显示在右下角</p>
          </div>
          <div class="feature-item">
            <h3>🎭 渐入渐出</h3>
            <p>从右侧滑入，播放完成后向右滑出</p>
          </div>
          <div class="feature-item">
            <h3>📱 响应式设计</h3>
            <p>在移动设备上自动调整大小和位置</p>
          </div>
          <div class="feature-item">
            <h3>🔊 音频支持</h3>
            <p>支持带声音的视频播放，可调节音量</p>
          </div>
        </div>
      </div>
      
      <!-- 动画测试 -->
      <div class="demo-section">
        <h2>🧪 动画测试</h2>
        <div class="test-controls">
          <el-button type="primary" @click="testIntroAnimation">
            🎬 测试开场动画
          </el-button>
          <el-button type="success" @click="testAnswerAnimation">
            🤖 测试回答动画
          </el-button>
          <el-button type="warning" @click="resetAnimations">
            🔄 重置动画状态
          </el-button>
        </div>
        
        <div class="test-info">
          <p><strong>提示：</strong>动画将显示在页面右下角，不会遮挡主要内容</p>
          <p><strong>操作：</strong>点击动画区域可以跳过，或等待自动播放完成</p>
        </div>
      </div>
      
      <!-- 动画状态 -->
      <div class="demo-section">
        <h2>📊 动画状态</h2>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="开场动画状态">
            <el-tag :type="animationState.intro.isPlaying ? 'success' : 'info'">
              {{ animationState.intro.isPlaying ? '播放中' : '未播放' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开场动画已播放">
            <el-tag :type="animationState.intro.hasPlayed ? 'warning' : 'info'">
              {{ animationState.intro.hasPlayed ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="回答动画状态">
            <el-tag :type="animationState.answer.isPlaying ? 'success' : 'info'">
              {{ animationState.answer.isPlaying ? '播放中' : '未播放' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="回答动画播放次数">
            <el-tag type="primary">{{ animationState.answer.playCount }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 模拟对话 -->
      <div class="demo-section">
        <h2>💬 模拟对话</h2>
        <div class="chat-simulation">
          <div class="chat-input">
            <el-input
              v-model="chatInput"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 4 }"
              placeholder="输入消息来模拟AI回答动画..."
            />
            <el-button type="primary" @click="simulateChat" :loading="isSimulating">
              发送消息
            </el-button>
          </div>
          
          <div class="chat-history">
            <div
              v-for="(message, index) in chatHistory"
              :key="index"
              class="chat-message"
              :class="message.role"
            >
              <div class="message-content">
                {{ message.content }}
              </div>
              <div class="message-time">
                {{ message.time }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 调试工具 -->
      <div class="demo-section">
        <h2>🔧 调试工具</h2>
        <div class="debug-controls">
          <el-button @click="showDebugInfo">查看调试信息</el-button>
          <el-button @click="forcePlayIntro">强制播放开场动画</el-button>
          <el-button @click="forcePlayAnswer">强制播放回答动画</el-button>
        </div>
        <p class="debug-tip">💡 打开浏览器控制台查看更多调试信息</p>
      </div>
    </div>
    
    <!-- 动画组件 -->
    <IntroAnimation
      :show="showIntroAnimation"
      :video-src="introVideoSrc"
      :poster-src="introPosterSrc"
      :auto-play="true"
      :skip-timeout="5000"
      @complete="onIntroComplete"
      @skip="onIntroSkip"
      @error="onIntroError"
    />
    
    <AnswerAnimation
      :show="showAnswerAnimation"
      :video-src="answerVideoSrc"
      :poster-src="answerPosterSrc"
      :auto-play="true"
      :muted="false"
      :volume="0.7"
      @complete="onAnswerAnimationComplete"
      @skip="onAnswerAnimationSkip"
      @error="onAnswerAnimationError"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import IntroAnimation from '@/components/ai-chat/component/intro-animation/index.vue'
import AnswerAnimation from '@/components/ai-chat/component/answer-animation/index.vue'
import animationManager from '@/utils/animation-manager'
import { animationDebug } from '@/utils/animation-debug'

// 动画状态
const showIntroAnimation = ref(false)
const showAnswerAnimation = ref(false)
const introVideoSrc = ref('/videos/intro-animation.mp4')
const introPosterSrc = ref('/images/intro-poster.jpg')
const answerVideoSrc = ref('/videos/answer-animation.mp4')
const answerPosterSrc = ref('/images/answer-poster.jpg')

// 动画管理器状态
const animationState = reactive(animationManager.getState())

// 模拟对话状态
const chatInput = ref('')
const chatHistory = ref<Array<{ role: 'user' | 'assistant'; content: string; time: string }>>([])
const isSimulating = ref(false)

// 动画事件处理
const onIntroComplete = () => {
  showIntroAnimation.value = false
  ElMessage.success('🎬 开场动画播放完成')
}

const onIntroSkip = () => {
  showIntroAnimation.value = false
  ElMessage.info('⏭️ 开场动画被跳过')
}

const onIntroError = (error: string) => {
  showIntroAnimation.value = false
  ElMessage.error(`❌ 开场动画播放错误: ${error}`)
}

const onAnswerAnimationComplete = () => {
  showAnswerAnimation.value = false
  ElMessage.success('🤖 回答动画播放完成')
}

const onAnswerAnimationSkip = () => {
  showAnswerAnimation.value = false
  ElMessage.info('⏭️ 回答动画被跳过')
}

const onAnswerAnimationError = (error: string) => {
  showAnswerAnimation.value = false
  ElMessage.error(`❌ 回答动画播放错误: ${error}`)
}

// 测试动画
const testIntroAnimation = () => {
  animationManager.resetAll()
  showIntroAnimation.value = true
  ElMessage.success('🎬 开场动画测试已启动')
}

const testAnswerAnimation = () => {
  showAnswerAnimation.value = true
  ElMessage.success('🤖 回答动画测试已启动')
}

const resetAnimations = () => {
  animationManager.resetAll()
  ElMessage.success('🔄 动画状态已重置')
}

// 模拟对话
const simulateChat = async () => {
  const content = chatInput.value.trim()
  if (!content) {
    ElMessage.warning('请输入消息内容')
    return
  }
  
  // 添加用户消息
  chatHistory.value.push({
    role: 'user',
    content,
    time: new Date().toLocaleTimeString()
  })
  
  chatInput.value = ''
  isSimulating.value = true
  
  // 模拟AI处理时间
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  // 触发回答动画
  if (animationManager.shouldPlayAnswer()) {
    showAnswerAnimation.value = true
  }
  
  // 模拟AI回答
  setTimeout(() => {
    chatHistory.value.push({
      role: 'assistant',
      content: `这是对"${content}"的模拟回答。动画系统正在工作！`,
      time: new Date().toLocaleTimeString()
    })
    isSimulating.value = false
  }, 2000)
}

// 调试工具
const showDebugInfo = () => {
  animationDebug.logAll()
  ElMessage.info('📊 调试信息已输出到控制台')
}

const forcePlayIntro = () => {
  animationDebug.forcePlayIntro()
  showIntroAnimation.value = true
  ElMessage.success('🎬 强制播放开场动画')
}

const forcePlayAnswer = () => {
  animationDebug.forcePlayAnswer()
  showAnswerAnimation.value = true
  ElMessage.success('🤖 强制播放回答动画')
}

// 监听动画状态变化
watch(() => animationManager.getState(), (newState) => {
  Object.assign(animationState, newState)
}, { deep: true })

onMounted(() => {
  // 页面加载时显示开场动画
  setTimeout(() => {
    if (animationManager.shouldPlayIntro()) {
      showIntroAnimation.value = true
    }
  }, 1000)
})
</script>

<style lang="scss" scoped>
.animation-demo {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.demo-header {
  text-align: center;
  margin-bottom: 40px;
  
  h1 {
    color: #303133;
    margin-bottom: 8px;
    font-size: 2.5em;
  }
  
  p {
    color: #606266;
    font-size: 18px;
  }
}

.demo-content {
  display: grid;
  gap: 30px;
}

.demo-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  
  h2 {
    color: #303133;
    margin-bottom: 20px;
    font-size: 20px;
    font-weight: 600;
  }
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  
  .feature-item {
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #409eff;
    
    h3 {
      color: #303133;
      margin-bottom: 8px;
      font-size: 16px;
    }
    
    p {
      color: #606266;
      margin: 0;
    }
  }
}

.test-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.test-info {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 6px;
  padding: 12px;
  
  p {
    margin: 4px 0;
    color: #1890ff;
    font-size: 14px;
  }
}

.chat-simulation {
  .chat-input {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    
    .el-input {
      flex: 1;
    }
  }
  
  .chat-history {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    padding: 16px;
    
    .chat-message {
      margin-bottom: 16px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      &.user {
        text-align: right;
        
        .message-content {
          background: #409eff;
          color: white;
          display: inline-block;
          padding: 8px 12px;
          border-radius: 12px;
          max-width: 70%;
        }
      }
      
      &.assistant {
        text-align: left;
        
        .message-content {
          background: #f4f4f5;
          color: #303133;
          display: inline-block;
          padding: 8px 12px;
          border-radius: 12px;
          max-width: 70%;
        }
      }
      
      .message-time {
        font-size: 12px;
        color: #909399;
        margin-top: 4px;
      }
    }
  }
}

.debug-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.debug-tip {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

// 响应式设计
@media (max-width: 768px) {
  .animation-demo {
    padding: 10px;
  }
  
  .demo-header h1 {
    font-size: 2em;
  }
  
  .test-controls,
  .debug-controls {
    flex-direction: column;
  }
  
  .chat-simulation .chat-input {
    flex-direction: column;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
}
</style>
