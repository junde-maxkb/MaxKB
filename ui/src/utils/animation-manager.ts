import { ref, reactive } from 'vue'
import { getAnimationConfig, saveAnimationConfig, type AnimationConfig } from '@/config/animation'

export interface AnimationState {
  intro: {
    isPlaying: boolean
    hasPlayed: boolean
  }
  answer: {
    isPlaying: boolean
    playCount: number
  }
}

class AnimationManager {
  private config = reactive<AnimationConfig>(getAnimationConfig())
  private state = reactive<AnimationState>({
    intro: {
      isPlaying: false,
      hasPlayed: false
    },
    answer: {
      isPlaying: false,
      playCount: 0
    }
  })

  // 获取配置
  getConfig(): AnimationConfig {
    return this.config
  }

  // 更新配置
  updateConfig(newConfig: Partial<AnimationConfig>) {
    Object.assign(this.config, newConfig)
    saveAnimationConfig(newConfig)
  }

  // 获取状态
  getState(): AnimationState {
    return this.state
  }

  // 检查是否应该播放开场动画
  shouldPlayIntro(): boolean {
    return this.config.intro.enabled && 
           this.config.intro.showOnFirstLoad && 
           !this.state.intro.hasPlayed
  }

  // 检查是否应该播放回答动画
  shouldPlayAnswer(): boolean {
    return this.config.answer.enabled && 
           this.config.answer.showOnEveryAnswer
  }

  // 开始播放开场动画
  startIntro() {
    this.state.intro.isPlaying = true
  }

  // 结束开场动画
  endIntro() {
    this.state.intro.isPlaying = false
    this.state.intro.hasPlayed = true
  }

  // 开始播放回答动画
  startAnswer() {
    this.state.answer.isPlaying = true
    this.state.answer.playCount++
  }

  // 结束回答动画
  endAnswer() {
    this.state.answer.isPlaying = false
  }

  // 跳过开场动画
  skipIntro() {
    this.state.intro.isPlaying = false
    this.state.intro.hasPlayed = true
  }

  // 跳过回答动画
  skipAnswer() {
    this.state.answer.isPlaying = false
  }

  // 重置开场动画状态
  resetIntro() {
    this.state.intro.isPlaying = false
    this.state.intro.hasPlayed = false
  }

  // 重置回答动画状态
  resetAnswer() {
    this.state.answer.isPlaying = false
    this.state.answer.playCount = 0
  }

  // 重置所有状态
  resetAll() {
    this.resetIntro()
    this.resetAnswer()
  }

  // 获取统计信息
  getStats() {
    return {
      introPlayed: this.state.intro.hasPlayed,
      answerPlayCount: this.state.answer.playCount,
      config: this.config
    }
  }
}

const animationManager = new AnimationManager()
export default animationManager
