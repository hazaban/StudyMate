<template>
  <view class="modal-mask" v-if="visible" @click="handleClose">
    <view class="modal-sheet" @click.stop>
      <view class="modal-top">
        <text class="modal-title">{{ isComplete ? '✓ 任务完成反思' : '未完成原因记录' }}</text>
        <view class="modal-x" @click="handleClose">✕</view>
      </view>
      <view class="modal-body">
        <view class="form-group" v-if="isComplete">
          <text class="form-label">实际用时（分钟）</text>
          <view class="time-controls">
            <view class="time-btn" @click="adjustActualDuration(-5)">−5</view>
            <view class="time-input-wrap">
              <input class="time-input" type="number" v-model="form.actualDuration" placeholder="0" />
            </view>
            <text class="time-unit">分钟</text>
            <view class="time-btn" @click="adjustActualDuration(5)">+5</view>
          </view>
        </view>
        <view class="form-group">
          <text class="form-label">{{ isComplete ? '完成过程中的问题（选填）' : '未完成原因' }}</text>
          <textarea class="textarea-field" v-model="form.notes" :placeholder="isComplete ? '记录完成过程中遇到的问题、难点或收获...' : '请说明未完成的原因...'" />
        </view>
        <view class="quick-tags" v-if="!isComplete">
          <text class="tag-title">快速选择原因</text>
          <view class="tag-list">
            <view class="tag-item" v-for="tag in incompleteTags" :key="tag" @click="selectTag(tag)">
              <text>{{ tag }}</text>
            </view>
          </view>
        </view>
      </view>
      <view class="modal-bot">
        <view class="btn-cancel" @click="handleClose">{{ isComplete ? '跳过' : '暂不记录' }}</view>
        <view class="btn-submit" @click="handleSubmit">{{ isComplete ? '保存并完成' : '保存原因' }}</view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { reactive, watch, computed } from 'vue'
import { createReflection, updateReflection } from '@/api/client'
import { usePlanStore } from '@/stores/plan'

const props = defineProps({
  visible: Boolean,
  task: Object,
  taskDate: String,
  isComplete: Boolean,
  existingReflection: Object,
  defaultDuration: { type: Number, default: 0 }
})

const emit = defineEmits(['close', 'submitted'])

const planStore = usePlanStore()

const form = reactive({
  actualDuration: 0,
  notes: ''
})

const incompleteTags = ['时间不够', '难度太大', '突发事项', '缺乏资料', '状态不佳', '计划调整', '其他']

watch(() => props.visible, (val) => {
  if (val) {
    form.actualDuration = props.existingReflection?.actual_duration || props.defaultDuration || 0
    form.notes = props.existingReflection?.completion_issues || props.existingReflection?.incomplete_reason || ''
  }
})

function adjustActualDuration(d) {
  const n = form.actualDuration + d
  if (n < 0) form.actualDuration = 0
  else form.actualDuration = n
}

function selectTag(tag) {
  if (form.notes) {
    if (!form.notes.includes(tag)) form.notes += '，' + tag
  } else {
    form.notes = tag
  }
}

async function handleSubmit() {
  if (!planStore.currentPlan || !props.task) return

  try {
    const data = {
      task_id: props.task.id,
      plan_id: planStore.currentPlan.id,
      task_date: props.taskDate,
      actual_duration: form.actualDuration,
      completion_issues: props.isComplete ? form.notes : '',
      incomplete_reason: props.isComplete ? '' : form.notes
    }

    if (props.existingReflection) {
      await updateReflection(props.existingReflection.id, {
        actual_duration: data.actual_duration,
        completion_issues: data.completion_issues,
        incomplete_reason: data.incomplete_reason
      })
    } else {
      await createReflection(data)
    }

    emit('submitted', data)
    uni.showToast({ title: '记录成功', icon: 'success' })
  } catch (e) {
    console.warn('Save reflection failed:', e)
    uni.showToast({ title: '记录失败', icon: 'none' })
  }

  handleClose()
}

function handleClose() {
  emit('close')
}
</script>

<style lang="scss" scoped>
.modal-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 100;
  display: flex; align-items: flex-end;
}
.modal-sheet {
  background: #fafbf9; border-radius: 24px 24px 0 0; width: 100%; max-height: 70vh;
  display: flex; flex-direction: column;
  animation: up 0.25s ease;
}
@keyframes up { from { transform: translateY(100%); } to { transform: translateY(0); } }

.modal-top {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 22px; border-bottom: 1px solid #e8ece9;
}
.modal-title { font-size: 17px; font-weight: 700; color: #1a1a2e; }
.modal-x {
  width: 30px; height: 30px; border-radius: 50%; background: #f0f2f1;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; color: #999;
  &:active { background: #e0e4e2; }
}

.modal-body { padding: 16px 22px; flex: 1; overflow-y: auto; }

.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 10px; }

.time-controls { display: flex; align-items: center; gap: 8px; }
.time-btn {
  width: 44px; height: 44px; border-radius: 12px; background: #f0f2f1; color: #2f7d4f;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; border: 1px solid #d0d5d2;
  &:active { transform: scale(0.95); background: #2f7d4f; color: #fff; }
}
.time-input-wrap {
  width: 80px; padding: 4px 2px; border-radius: 12px; background: #fff; border: 1.5px solid #d0d5d2;
  &:focus-within { border-color: #2f7d4f; }
}
.time-input {
  width: 100%; text-align: center; font-size: 18px; font-weight: 700; color: #1a1a2e;
  height: 40px; line-height: 40px;
}
.time-unit { font-size: 14px; color: #999; }

.textarea-field {
  width: 100%; min-height: 100px; font-size: 15px; color: #1a1a2e; line-height: 1.6;
  border: 1.5px solid #d0d5d2; border-radius: 14px; padding: 12px 14px;
  background: #fff; resize: none;
  &:focus { border-color: #2f7d4f; outline: none; }
  &::placeholder { color: #bbb; }
}

.quick-tags { margin-top: 8px; }
.tag-title { display: block; font-size: 12px; color: #999; margin-bottom: 8px; }
.tag-list { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-item {
  padding: 6px 14px; background: #f0f2f1; border-radius: 20px;
  font-size: 13px; color: #666; border: 1px solid #d0d5d2;
  &:active { background: #2f7d4f; color: #fff; border-color: #2f7d4f; }
}

.modal-bot { display: flex; gap: 12px; padding: 16px 22px; border-top: 1px solid #e8ece9; }

.btn-cancel {
  flex: 1; padding: 14px; text-align: center; border-radius: 14px;
  font-size: 15px; color: #999; background: #f0f2f1; font-weight: 500;
  &:active { background: #e0e4e2; }
}
.btn-submit {
  flex: 2; padding: 14px; text-align: center; border-radius: 14px;
  font-size: 15px; color: #fff; background: #2f7d4f; font-weight: 700;
  box-shadow: 0 3px 12px rgba(47,125,79,0.2);
  &:active { transform: scale(0.97); }
}
</style>
