<template>
  <div class="intro-animation-container" :class="{ 'leaving': isLeaving }" v-if="show">
    <div class="intro-animation-content" :class="{ 'mobile': isMobile }">
      <!-- 视频背景 -->
      <video
        ref="videoRef"
        class="background-video"
        :src="videoSrc"
        :poster="posterSrc"
        preload="auto"
        muted
        loop
        @loadeddata="onVideoLoaded"
        @ended="onVideoEnded"
        @error="onVideoError"
      >
        您的浏览器不支持视频播放
      </video>
      
      <!-- 跳过按钮 -->
      <div class="skip-control">
        <el-button 
          type="info" 
          text 
          @click="skipAnimation"
          class="skip-button"
        >
          跳过 ({{ skipCountdown }}s)
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import useStore from '@/stores'

const props = withDefaults(defineProps<{
  show: boolean
  skipTimeout?: number
  videoSrc?: string
  posterSrc?: string
}>(), {
  skipTimeout: 5000,
  videoSrc: '/ui/videos/intro-animation.mp4',
  posterSrc: '/images/intro-poster.jpg'
})

const emit = defineEmits(['complete', 'skip', 'error'])

const { common } = useStore()
const videoRef = ref<HTMLVideoElement>()
const skipCountdown = ref(props.skipTimeout / 1000)
const countdownTimer = ref<number | undefined>()
const isLeaving = ref(false)

const isMobile = computed(() => common.isMobile())

// 视频事件处理
const onVideoLoaded = () => {
  if (videoRef.value) {
    videoRef.value.play()
  }
}

const onVideoEnded = () => {
  // 视频循环播放，不需要特殊处理
}

const onVideoError = (e: Event) => {
  console.error('视频加载失败:', e)
}

// 跳过动画
const skipAnimation = () => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
  }
  if (videoRef.value) {
    videoRef.value.pause()
  }
  isLeaving.value = true
  setTimeout(() => {
    emit('skip')
  }, 300)
}

// 开始倒计时
const startCountdown = () => {
  countdownTimer.value = window.setInterval(() => {
    if (skipCountdown.value > 0) {
      skipCountdown.value--
    } else {
      if (countdownTimer.value) {
        clearInterval(countdownTimer.value)
      }
      // 自动完成动画
      isLeaving.value = true
      setTimeout(() => {
        emit('complete')
      }, 300)
    }
  }, 1000)
}

// 组件挂载
onMounted(() => {
  if (props.show) {
    startCountdown()
  }
})

// 组件卸载
onBeforeUnmount(() => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
  }
  if (videoRef.value) {
    videoRef.value.pause()
  }
})

// 监听show属性变化
watch(() => props.show, (newVal) => {
  if (newVal) {
    skipCountdown.value = props.skipTimeout / 1000
    isLeaving.value = false
    startCountdown()
  } else {
    if (countdownTimer.value) {
      clearInterval(countdownTimer.value)
    }
  }
})
</script>

<style lang="scss" scoped>
.intro-animation-container {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 9999;
  animation: fadeIn 0.5s ease-out;
}

.intro-animation-content {
  position: relative;
  width: 210px; // 9:16 竖版宽度
  height: 220px; // 9:16 竖版高度
  border-radius: 12px;
  overflow: hidden;
  
  &.mobile {
    width: 162px; // 保持9:16
    height: 288px;
  }
}

.background-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

.intro-animation-container.leaving {
  animation: fadeOut 0.3s ease-in forwards;
}

.skip-control {
  position: absolute;
  top: 12px;
  right: 12px;
  
  .skip-button {
    color: rgba(255, 255, 255, 0.8);
    font-size: 12px;
    padding: 4px 8px;
    
    &:hover { color: white; }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .intro-animation-container {
    bottom: 10px;
    right: 10px;
  }
}
</style>

