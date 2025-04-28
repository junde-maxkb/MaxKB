<template>
  <router-view v-slot="{ Component }">
    <transition appear name="fade-transform" mode="out-in">
      <keep-alive :include="cachedViews">
        <component :is="Component" :key="route.fullPath" />
      </keep-alive>
    </transition>
  </router-view>
</template>

<script setup lang="ts">
import { ref, onBeforeUpdate, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const cachedViews: any = ref([])
onBeforeUpdate(() => {
  const { name, meta } = route
  if (name && !cachedViews.value.includes(name)) {
    cachedViews.value.push(name)
  }
})

// 监听路由变化,确保组件更新
// watch(() => route.fullPath, () => {
//   // 强制组件更新
//   const component = document.querySelector('.view-container')
//   if (component) {
//     component.innerHTML = ''
//   }
// })
</script>
