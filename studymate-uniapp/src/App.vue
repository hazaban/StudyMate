<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('StudyMate学习星球启动')

  // Apply dark mode from storage
  // #ifdef H5
  const isDark = uni.getStorageSync('studymate_dark_mode')
  if (isDark) {
    document.documentElement.classList.add('dark-mode')
  }
  // #endif
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
@import './styles/global.scss';
</style>