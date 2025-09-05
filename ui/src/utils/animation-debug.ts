// 动画系统调试工具
import animationManager from './animation-manager'

export class AnimationDebugger {
  private static instance: AnimationDebugger
  private debugMode = false

  static getInstance(): AnimationDebugger {
    if (!AnimationDebugger.instance) {
      AnimationDebugger.instance = new AnimationDebugger()
    }
    return AnimationDebugger.instance
  }

  // 启用调试模式
  enableDebug() {
    this.debugMode = true
    console.log('🎬 动画系统调试模式已启用')
  }

  // 禁用调试模式
  disableDebug() {
    this.debugMode = false
    console.log('🎬 动画系统调试模式已禁用')
  }

  // 打印动画配置
  logConfig() {
    if (!this.debugMode) return
    
    const config = animationManager.getConfig()
    console.log('🎬 动画配置:', config)
  }

  // 打印动画状态
  logState() {
    if (!this.debugMode) return
    
    const state = animationManager.getState()
    console.log('🎬 动画状态:', state)
  }

  // 打印动画统计
  logStats() {
    if (!this.debugMode) return
    
    const stats = animationManager.getStats()
    console.log('🎬 动画统计:', stats)
  }

  // 检查是否应该播放开场动画
  checkIntroPlay() {
    if (!this.debugMode) return false
    
    const shouldPlay = animationManager.shouldPlayIntro()
    console.log('🎬 是否应该播放开场动画:', shouldPlay)
    return shouldPlay
  }

  // 检查是否应该播放回答动画
  checkAnswerPlay() {
    if (!this.debugMode) return false
    
    const shouldPlay = animationManager.shouldPlayAnswer()
    console.log('🎬 是否应该播放回答动画:', shouldPlay)
    return shouldPlay
  }

  // 重置动画状态
  resetState() {
    if (!this.debugMode) return
    
    animationManager.resetAll()
    console.log('🎬 动画状态已重置')
  }

  // 强制播放开场动画
  forcePlayIntro() {
    if (!this.debugMode) return
    
    animationManager.resetAll()
    animationManager.startIntro()
    console.log('🎬 强制播放开场动画')
  }

  // 强制播放回答动画
  forcePlayAnswer() {
    if (!this.debugMode) return
    
    animationManager.startAnswer()
    console.log('🎬 强制播放回答动画')
  }

  // 打印完整的调试信息
  logAll() {
    if (!this.debugMode) return
    
    console.group('🎬 动画系统完整调试信息')
    this.logConfig()
    this.logState()
    this.logStats()
    console.log('🎬 开场动画检查:', this.checkIntroPlay())
    console.log('🎬 回答动画检查:', this.checkAnswerPlay())
    console.groupEnd()
  }
}

// 创建全局调试实例
export const animationDebug = AnimationDebugger.getInstance()

// 在开发环境下自动启用调试
if (import.meta.env.DEV) {
  animationDebug.enableDebug()
}

// 将调试工具添加到全局对象（仅开发环境）
if (import.meta.env.DEV && typeof window !== 'undefined') {
  (window as any).animationDebug = animationDebug
  console.log('🎬 动画调试工具已添加到全局对象，可通过 window.animationDebug 访问')
}
