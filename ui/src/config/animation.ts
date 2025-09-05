// 动画配置文件
export interface AnimationConfig {
  // 开场动画配置
  intro: {
    enabled: boolean
    videoSrc: string
    posterSrc: string
    autoPlay: boolean
    skipTimeout: number
    showOnFirstLoad: boolean
  }
  
  // 回答前动画配置
  answer: {
    enabled: boolean
    videoSrc: string
    posterSrc: string
    autoPlay: boolean
    showOnEveryAnswer: boolean
    muted: boolean
    volume: number
  }
}

// 默认配置
export const defaultAnimationConfig: AnimationConfig = {
  intro: {
    enabled: true,
    videoSrc: '/videos/intro-animation.mp4',
    posterSrc: '/images/intro-poster.jpg',
    autoPlay: true,
    skipTimeout: 5000,
    showOnFirstLoad: true
  },
  answer: {
    enabled: true,
    videoSrc: '/videos/answer-animation.mp4',
    posterSrc: '/images/answer-poster.jpg',
    autoPlay: true,
    showOnEveryAnswer: true,
    muted: false,
    volume: 0.7
  }
}

// 获取动画配置
export const getAnimationConfig = (): AnimationConfig => {
  // 可以从localStorage或API获取配置
  const storedConfig = localStorage.getItem('animationConfig')
  if (storedConfig) {
    try {
      return { ...defaultAnimationConfig, ...JSON.parse(storedConfig) }
    } catch (error) {
      console.error('解析动画配置失败:', error)
    }
  }
  return defaultAnimationConfig
}

// 保存动画配置
export const saveAnimationConfig = (config: Partial<AnimationConfig>) => {
  const currentConfig = getAnimationConfig()
  const newConfig = { ...currentConfig, ...config }
  localStorage.setItem('animationConfig', JSON.stringify(newConfig))
}

// 检查是否支持视频播放
export const isVideoSupported = (): boolean => {
  const video = document.createElement('video')
  return !!video.canPlayType
}

// 检查是否支持音频播放
export const isAudioSupported = (): boolean => {
  return 'AudioContext' in window || 'webkitAudioContext' in window
}

// 预加载视频资源
export const preloadVideo = (src: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video')
    video.preload = 'metadata'
    video.onloadedmetadata = () => resolve()
    video.onerror = () => reject(new Error('视频预加载失败'))
    video.src = src
  })
}

// 检查网络连接状态
export const checkNetworkStatus = (): Promise<boolean> => {
  return new Promise((resolve) => {
    if ('navigator' in window && 'onLine' in navigator) {
      resolve(navigator.onLine)
    } else {
      // 通过尝试加载一个小图片来检测网络状态
      const img = new Image()
      img.onload = () => resolve(true)
      img.onerror = () => resolve(false)
      img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
    }
  })
}

