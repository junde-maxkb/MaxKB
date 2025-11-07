<template>
  <div class="message-card" :class="{'is-read': isRead}">
    <div class="message-card__header">
      <span class="message-card__status" :class="isRead ? 'read' : 'unread'">
        {{ isRead ? '已读' : '未读' }}
      </span>
      <span class="message-card__time">{{ formattedTime }}</span>
    </div>
    <div class="message-card__body">
      <p class="message-card__text">{{ msg }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  msg: { type: String, required: true },
  createTime: { type: [String, Number, Date], required: true },
  logRead: { type: [Boolean, Number], default: false }
})

// 兼容数值或布尔
const isRead = computed(() => {
  if (typeof props.logRead === 'number') return props.logRead !== 0
  return !!props.logRead
})

// 简单格式化时间（可按需替换为 dayjs 等）
const formattedTime = computed(() => {
  const d = new Date(props.createTime)
  if (isNaN(d.getTime())) return props.createTime
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
})
</script>

<style scoped>
.message-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 12px 14px;
  background: #fff;
  box-shadow: 0 2px 6px rgba(0,0,0,.06);
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border-color .2s, box-shadow .2s;
}
.message-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0,0,0,.08);
}

.message-card.is-read {
  opacity: 0.85;
}

.message-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #64748b;
}

.message-card__status {
  padding: 2px 6px;
  border-radius: 6px;
  font-weight: 500;
  letter-spacing: .5px;
}
.message-card__status.read {
  background: #ecfdf5;
  color: #059669;
}
.message-card__status.unread {
  background: #fef2f2;
  color: #dc2626;
}

.message-card__time {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.message-card__body {
  line-height: 1.5;
}
.message-card__text {
  margin: 0;
  font-size: 14px;
  color: #334155;
  word-break: break-word;
}
</style>