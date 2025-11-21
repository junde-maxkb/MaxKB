<template>
  <div class="box">
    <div class="suggestions" @wheel="handleWheel">
    <span
      v-for="(suggestion, index) in suggestions"
      :key="index"
      class="suggestion"
      @click="emit('suggestion-click', suggestion)"
    >
      {{ suggestion.display }}
    </span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  suggestions: {submit: string, display: string}[]
}>()

// 抛出一个点击事件
const emit = defineEmits<{
  (e: 'suggestion-click', suggestion: {submit: string, display: string}): void
}>()

// 处理鼠标滚轮事件，转换为横向滚动
const handleWheel = (event: WheelEvent) => {
  const container = event.currentTarget as HTMLElement
  // 防止默认垂直滚动
  event.preventDefault()
  // 将deltaY（垂直滚动）转换为deltaX（横向滚动）
  container.scrollLeft += event.deltaY
}
</script>

<style scoped lang="scss">
.box {
  overflow: auto;
  max-width: 100%;
  display: inline-block;
}
.suggestions {
  display: flex;
  gap: 5px;
  width: 100%;
  overflow-x: auto;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;

  .suggestion {
    flex-shrink: 0;
    width: fit-content;
    white-space: nowrap;
    font-size: 14px;
    font-weight: 500;
    border-radius: 40px;
    border: 1px solid #E0E0E0;
    padding: 4px 10px;
    background: #fff;

    &:hover {
      background: #f5f5f5;
      cursor: pointer;
    }
  }
}
</style>