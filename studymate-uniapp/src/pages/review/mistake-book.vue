<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      <text class="page-title">错题本</text>
      <view class="placeholder"></view>
    </view>

    <view class="filter-section">
      <scroll-view scroll-x class="filter-scroll">
        <view class="filter-list">
          <view class="filter-item" :class="{ active: activeFilter === 'all' }" @click="activeFilter = 'all'">
            全部
          </view>
          <view class="filter-item" :class="{ active: activeFilter === subject }" v-for="subject in subjects" :key="subject" @click="activeFilter = subject">
            {{ subject }}
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="mistake-list">
      <view class="empty-state" v-if="filteredMistakes.length === 0">
        <text class="empty-icon">📝</text>
        <text class="empty-text">暂无错题</text>
        <text class="empty-hint">记录错题有助于更好地复习</text>
      </view>

      <view class="mistake-card" v-for="mistake in filteredMistakes" :key="mistake.id">
        <view class="mistake-header">
          <text class="mistake-subject">{{ mistake.subject }}</text>
          <view class="mistake-tag" :class="mistake.difficulty">
            {{ mistake.difficulty === 'hard' ? '困难' : mistake.difficulty === 'medium' ? '中等' : '简单' }}
          </view>
        </view>

        <text class="mistake-question">{{ mistake.question }}</text>

        <view class="mistake-answer-section">
          <text class="answer-label">正确答案</text>
          <text class="mistake-answer">{{ mistake.answer }}</text>
        </view>

        <view class="mistake-analysis-section">
          <text class="analysis-label">错误分析</text>
          <text class="mistake-analysis">{{ mistake.analysis }}</text>
        </view>

        <view class="mistake-footer">
          <text class="mistake-date">{{ mistake.date }}</text>
          <view class="mistake-actions">
            <view class="action-btn" @click="reviewMistake(mistake)">复习</view>
            <view class="action-btn secondary" @click="markMastered(mistake)">已掌握</view>
          </view>
        </view>
      </view>
    </view>

    <view class="fab-area">
      <view class="fab" @click="addMistake">
        <text class="fab-icon">+</text>
        <text class="fab-text">添加错题</text>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { dateUtil } from '@/utils/date'

const activeFilter = ref('all')

const subjects = ['数学', '英语', '政治', '数据结构', '计算机组成原理', '操作系统', '计算机网络']

const mistakes = ref([
  {
    id: 1,
    subject: '数学',
    question: '设函数 f(x) 在 x=0 处连续，且 lim(x→0) f(x)/x = 2，则 f(0) = ?',
    answer: '0',
    analysis: '因为 f(x) 在 x=0 处连续，所以 lim(x→0) f(x) = f(0)。又因为 lim(x→0) f(x)/x = 2 存在，且分母趋于0，所以分子必须也趋于0，即 f(0) = 0。',
    difficulty: 'medium',
    date: dateUtil.today(),
    review_count: 2
  },
  {
    id: 2,
    subject: '数据结构',
    question: '在一棵具有 n 个结点的二叉树中，所有结点的度数之和为？',
    answer: 'n-1',
    analysis: '除了根结点外，每个结点都有且仅有一条边与其父结点相连，所以总边数为 n-1。而每条边对应父结点的一个度，所以所有结点的度数之和等于边数，即 n-1。',
    difficulty: 'hard',
    date: dateUtil.today(),
    review_count: 1
  },
  {
    id: 3,
    subject: '英语',
    question: 'The manager demanded that all employees _____ on time.',
    answer: '(should) be',
    analysis: 'demand 后面的宾语从句需要使用虚拟语气，谓语动词用 should + 动词原形，should 可以省略。',
    difficulty: 'easy',
    date: dateUtil.yesterday(),
    review_count: 3
  }
])

const filteredMistakes = computed(() => {
  if (activeFilter.value === 'all') {
    return mistakes.value
  }
  return mistakes.value.filter(m => m.subject === activeFilter.value)
})

function goBack() {
  uni.navigateBack()
}

function addMistake() {
  uni.showModal({
    title: '添加错题',
    editable: true,
    placeholderText: '请输入错题内容',
    success: (res) => {
      if (res.confirm && res.content) {
        uni.showToast({ title: '添加成功', icon: 'success' })
      }
    }
  })
}

function reviewMistake(mistake) {
  uni.showModal({
    title: mistake.subject,
    content: `问题：${mistake.question}\n\n答案：${mistake.answer}\n\n分析：${mistake.analysis}`,
    showCancel: false
  })
}

function markMastered(mistake) {
  uni.showModal({
    title: '标记已掌握',
    content: '确定已掌握这道题了吗？',
    success: (res) => {
      if (res.confirm) {
        mistakes.value = mistakes.value.filter(m => m.id !== mistake.id)
        uni.showToast({ title: '已标记', icon: 'success' })
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 60px 20px 20px;
  
  .back-btn {
    width: 40px;
    height: 40px;
    background: $bg2;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .back-icon {
      font-size: 20px;
      color: $ink;
    }
  }
  
  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: $ink;
  }
  
  .placeholder {
    width: 40px;
  }
}

.filter-scroll {
  white-space: nowrap;
  margin-bottom: 20px;
}

.filter-list {
  display: inline-flex;
  gap: 8px;
}

.filter-item {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  background: $bg2;
  color: $muted;
  border: 1px solid $rule;
  
  &.active {
    background: #ef5350;
    color: #fff;
    border-color: #ef5350;
  }
}

.mistake-list {
  padding-bottom: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  .empty-text {
    font-size: 18px;
    color: $ink;
    margin-bottom: 8px;
  }
  
  .empty-hint {
    font-size: 14px;
    color: $muted;
  }
}

.mistake-card {
  background: $bg2;
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 12px;
  border: 1px solid $rule;
}

.mistake-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  
  .mistake-subject {
    font-size: 12px;
    padding: 4px 12px;
    background: $soft;
    border-radius: 20px;
    color: $accent;
  }
}

.mistake-tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 8px;
  
  &.easy {
    background: #e8f5e9;
    color: #2e7d32;
  }
  
  &.medium {
    background: #fff3e0;
    color: #e65100;
  }
  
  &.hard {
    background: #ffebee;
    color: #c62828;
  }
}

.mistake-question {
  display: block;
  font-size: 16px;
  color: $ink;
  line-height: 1.6;
  margin-bottom: 12px;
}

.mistake-answer-section, .mistake-analysis-section {
  margin-bottom: 12px;
  
  .answer-label, .analysis-label {
    display: block;
    font-size: 12px;
    color: $accent;
    margin-bottom: 4px;
    font-weight: 500;
  }
  
  .mistake-answer, .mistake-analysis {
    font-size: 14px;
    color: $ink;
    line-height: 1.6;
  }
  
  .mistake-analysis {
    color: $muted;
  }
}

.mistake-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .mistake-date {
    font-size: 12px;
    color: $muted;
  }
}

.mistake-actions {
  display: flex;
  gap: 8px;
  
  .action-btn {
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 13px;
    background: #ef5350;
    color: #fff;
    
    &.secondary {
      background: $soft;
      color: $accent;
    }
  }
}

.fab-area {
  position: fixed;
  right: 20px;
  bottom: 60px;
}

.fab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  background: #ef5350;
  border-radius: 50px;
  box-shadow: 0 4px 12px rgba(239, 83, 80, 0.3);
  
  .fab-icon {
    font-size: 20px;
    color: #fff;
  }
  
  .fab-text {
    font-size: 15px;
    color: #fff;
    font-weight: 500;
  }
}

.bottom-space {
  height: 100px;
}
</style>