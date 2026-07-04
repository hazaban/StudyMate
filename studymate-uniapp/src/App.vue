<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

function applyDarkMode() {
  const dark = uni.getStorageSync('studymate_dark_mode')
  if (dark) {
    document.documentElement.classList.add('dark-mode')
  } else {
    document.documentElement.classList.remove('dark-mode')
  }
}

onLaunch(() => {
  console.log('StudyMate 学习星球启动')
  applyDarkMode()
})

onShow(() => {
  console.log('App Show')
  applyDarkMode()
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
@import './styles/global.scss';
</style>