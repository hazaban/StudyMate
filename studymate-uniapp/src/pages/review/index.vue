<template>
  <view class="page">
    <!-- Header -->
    <view class="header" :class="currentView === 'mistakes' ? 'header-red' : 'header-purple'">
      <view class="header-top">
        <view class="header-left">
          <text class="title">{{ currentView === 'mistakes' ? '错题本' : '抗遗忘卡片' }}</text>
          <text class="subtitle">{{ currentView === 'mistakes' ? '记录每一次错误，让知识不再溜走' : '艾宾浩斯记忆曲线，科学对抗遗忘' }}</text>
        </view>
        <view class="header-right">
          <view class="export-btn" @click="showExportModal = true">
            <text class="export-icon">📤</text>
            <text class="export-text">导出</text>
          </view>
        </view>
      </view>
      <view class="stats-row">
        <view class="stat-item" v-if="currentView === 'cards'">
          <text class="stat-num">{{ pendingCardsCount }}</text>
          <text class="stat-label">待复习</text>
        </view>
        <view class="stat-item" v-if="currentView === 'cards'">
          <text class="stat-num">{{ cards.length }}</text>
          <text class="stat-label">总卡片</text>
        </view>
        <view class="stat-item" v-if="currentView === 'cards'">
          <text class="stat-num">{{ masteredCardsCount }}</text>
          <text class="stat-label">已掌握</text>
        </view>
        <view class="stat-item" v-if="currentView === 'mistakes'">
          <text class="stat-num">{{ mistakes.length }}</text>
          <text class="stat-label">总错题</text>
        </view>
        <view class="stat-item" v-if="currentView === 'mistakes'">
          <text class="stat-num">{{ masteredMistakesCount }}</text>
          <text class="stat-label">已掌握</text>
        </view>
        <view class="stat-item" v-if="currentView === 'mistakes'">
          <text class="stat-num">{{ activeMistakesCount }}</text>
          <text class="stat-label">待攻克</text>
        </view>
      </view>
    </view>

    <!-- Sub Navigation -->
    <view class="sub-nav">
      <view class="sub-nav-item" :class="{ active: currentView === 'cards' }" @click="switchView('cards')">知识卡片</view>
      <view class="sub-nav-item" :class="{ active: currentView === 'mistakes' }" @click="switchView('mistakes')">错题本</view>
    </view>

    <!-- ==================== 知识卡片视图 ==================== -->
    <template v-if="currentView === 'cards'">
      <view class="mode-toggle">
        <view class="mode-btn" :class="{ active: viewMode === 'pending' }" @click="switchCardMode('pending')">今日复习</view>
        <view class="mode-btn" :class="{ active: viewMode === 'all' }" @click="switchCardMode('all')">查看全部</view>
      </view>

      <view class="filter-section">
        <view class="filter-row">
          <scroll-view scroll-x class="filter-scroll">
            <view class="filter-list">
              <view class="filter-item" :class="{ active: activeSubject === '' }" @click="onSubjectChange('')">全部科目</view>
              <view class="filter-item" v-for="s in allSubjects" :key="s" :class="{ active: activeSubject === s }" @click="onSubjectChange(s)">{{ s }}</view>
            </view>
          </scroll-view>
          <view class="filter-manage-btn" @click="showManageSubjects = true">⚙</view>
        </view>
      </view>

      <view class="filter-section" v-if="availableCardTags.length > 0">
        <view class="filter-row">
          <scroll-view scroll-x class="filter-scroll">
            <view class="filter-list">
              <view class="filter-item tag-item" :class="{ active: activeTags.length === 0 }" @click="activeTags = []; tagLogic = 'or'">全部标签</view>
              <view class="filter-item tag-item" v-for="t in availableCardTags" :key="t" :class="{ active: activeTags.includes(t) }" @click="toggleTag(t)">{{ t }}</view>
            </view>
          </scroll-view>
          <view class="tag-logic-btn" v-if="activeTags.length > 1" @click="tagLogic = tagLogic === 'or' ? 'and' : 'or'">
            <text>{{ tagLogic === 'or' ? '或' : '且' }}</text>
          </view>
        </view>
      </view>

      <view class="filter-section">
        <scroll-view scroll-x class="filter-scroll">
          <view class="filter-list">
            <view class="filter-item mastery-item" :class="{ active: activeMastery === '' }" @click="activeMastery = ''">全部掌握</view>
            <view class="filter-item mastery-item unmastered" :class="{ active: activeMastery === 'unmastered' }" @click="activeMastery = 'unmastered'">未掌握</view>
            <view class="filter-item mastery-item familiar" :class="{ active: activeMastery === 'familiar' }" @click="activeMastery = 'familiar'">较熟悉</view>
            <view class="filter-item mastery-item mastered" :class="{ active: activeMastery === 'mastered' }" @click="activeMastery = 'mastered'">已掌握</view>
          </view>
        </scroll-view>
      </view>

      <!-- Review Mode -->
      <view class="review-card" v-if="reviewMode && reviewCards.length > 0">
        <text class="review-counter">{{ reviewIndex + 1 }} / {{ reviewCards.length }}</text>
        <view class="review-card-body">
          <view class="review-subject">{{ reviewCards[reviewIndex].subject }}</view>
          <view class="review-question"><text class="question-label">Q</text><text class="question-text">{{ reviewCards[reviewIndex].question }}</text></view>
          <view class="image-gallery" v-if="reviewCards[reviewIndex].question_images && reviewCards[reviewIndex].question_images.length > 0">
            <image v-for="(url, idx) in reviewCards[reviewIndex].question_images" :key="'rq'+idx" :src="url" mode="widthFix" class="review-image" @click="previewImage(url, reviewCards[reviewIndex].question_images)" />
          </view>
          <view class="review-answer" v-if="reviewShowAnswer">
            <view class="answer-divider"></view>
            <view class="answer-content"><text class="answer-label">A</text><text class="answer-text">{{ reviewCards[reviewIndex].answer }}</text></view>
            <view class="image-gallery" v-if="reviewCards[reviewIndex].answer_images && reviewCards[reviewIndex].answer_images.length > 0" style="margin-top: 10px;">
              <image v-for="(url, idx) in reviewCards[reviewIndex].answer_images" :key="'ra'+idx" :src="url" mode="widthFix" class="review-image" @click="previewImage(url, reviewCards[reviewIndex].answer_images)" />
            </view>
          </view>
        </view>
        <view class="review-actions">
          <view class="show-answer-btn" v-if="!reviewShowAnswer" @click="reviewShowAnswer = true"><text>点击查看答案</text></view>
          <view class="review-result-btns" v-else>
            <view class="result-btn fail" @click="reviewCardResult('unmastered')"><text class="result-icon">😣</text><text class="result-text">未掌握</text></view>
            <view class="result-btn ok" @click="reviewCardResult('familiar')"><text class="result-icon">🤔</text><text class="result-text">较熟悉</text></view>
            <view class="result-btn great" @click="reviewCardResult('mastered')"><text class="result-icon">😎</text><text class="result-text">已掌握</text></view>
          </view>
        </view>
      </view>
      <view class="review-complete" v-if="reviewMode && reviewCards.length === 0">
        <text class="complete-icon">🎉</text><text class="complete-text">今天没有需要复习的卡片</text>
        <view class="back-btn" @click="exitCardReview">查看全部</view>
      </view>
      <view class="review-complete" v-if="reviewComplete">
        <text class="complete-icon">🏆</text><text class="complete-text">复习完成！</text>
        <view class="back-btn" @click="exitCardReview">返回卡片列表</view>
      </view>

      <view v-if="!reviewMode && !reviewComplete">
        <view class="section-header" v-if="viewMode === 'pending' && filteredCards.length > 0">
          <text class="section-title">今日待复习 · {{ filteredCards.length }} 张</text>
          <view class="start-review-btn purple" @click="startCardReview"><text>开始复习</text></view>
        </view>
        <view class="section-header" v-if="viewMode === 'all'">
          <text class="section-title">全部卡片</text>
          <text class="section-count">{{ filteredCards.length }}张</text>
        </view>
        <view class="empty" v-if="filteredCards.length === 0">
          <text class="empty-icon">📖</text><text class="empty-text">{{ viewMode === 'pending' ? '今天没有需要复习的卡片' : '暂无卡片' }}</text>
          <text class="empty-hint">点击右下角按钮，手动添加知识卡片</text>
        </view>
        <view class="load-more" v-if="filteredCards.length > cardsPageSize" @click="showAllCards">
          <text>展开全部 {{ filteredCards.length }} 张卡片 ▾</text>
        </view>
        <view class="card-item" v-for="card in displayedCards" :key="card.id" :class="{ 'not-today': card.next_review_date > today }">
          <view class="card-item-header">
            <text class="card-item-subject">{{ card.subject }}</text>
            <view class="card-item-tags">
              <view class="card-tag" v-for="t in (card.tags || [])" :key="t">{{ t }}</view>
              <view class="mastery-badge" :class="getMasteryClass(card.mastery_level)">{{ getMasteryLabel(card.mastery_level) }}</view>
            </view>
          </view>
          <view class="card-item-question"><text class="section-label">问题</text><text class="card-question-text">{{ card.question }}</text>
            <view class="card-images" v-if="card.question_images && card.question_images.length > 0">
              <image v-for="(img, i) in card.question_images" :key="i" :src="img" mode="aspectFill" class="card-img-item" @click="previewImage(img, card.question_images)" />
            </view>
          </view>
          <view class="card-item-footer">
            <text class="review-count">第{{ card.review_count }}次复习</text>
            <text class="review-date" v-if="card.next_review_date && card.next_review_date > today">下次 {{ formatDate(card.next_review_date) }}</text>
            <view class="card-item-actions">
              <view class="action-btn edit-btn" @click="openEditCard(card)">编辑</view>
              <view class="action-btn del-btn" @click="removeCard(card)">删除</view>
            </view>
          </view>
        </view>
      </view>

      <!-- Add Card Modal -->
      <view class="modal-overlay" v-if="showCardForm" @click="showCardForm = false">
        <view class="modal-content" @click.stop>
          <view class="modal-header"><text class="modal-title">添加知识卡片</text><view class="modal-close" @click="showCardForm = false">✕</view></view>
          <scroll-view scroll-y class="modal-body">
            <view class="form-group"><text class="form-label">科目</text>
              <view class="subject-grid">
                <view class="subject-item" v-for="s in allSubjects" :key="s" :class="{ active: cardForm.subject === s }" @click="cardForm.subject = s">{{ s }}</view>
                <view class="subject-item subject-add" @click="showCardSubjectInput = !showCardSubjectInput">
                  <text v-if="!showCardSubjectInput">+ 自定义</text><text v-else>收起</text>
                </view>
              </view>
              <view class="input-wrapper" v-if="showCardSubjectInput" style="margin-top: 10px;">
                <input class="input-field" v-model="customSubject" placeholder="输入自定义科目..." @confirm="addCardCustomSubject" />
              </view>
            </view>
            <view class="form-group"><text class="form-label">标签</text>
              <!-- Existing tags chips from all records -->
              <view class="tag-picker" v-if="cardAvailableTags.length > 0">
                <view class="tag-picker-chip" v-for="t in cardAvailableTags" :key="t" :class="{ picked: cardForm.tags.includes(t) }" @click="toggleFormTag('card', t)">{{ t }}</view>
              </view>
              <!-- Custom tag input -->
              <view class="input-wrapper" style="margin-top: 8px;">
                <input class="input-field" v-model="tagInput" placeholder="输入新标签，逗号分隔..." @blur="parseTags" @confirm="parseTags" />
              </view>
              <view class="tag-preview" v-if="cardForm.tags.length > 0"><view class="tag-chip" v-for="(t, idx) in cardForm.tags" :key="idx">{{ t }}<text class="tag-remove" @click="cardForm.tags.splice(idx, 1)">✕</text></view></view>
            </view>
            <view class="form-group"><text class="form-label">问题（选填）</text><view class="input-wrapper"><textarea class="textarea-field" v-model="cardForm.question" placeholder="可留空，仅上传图片" maxlength="2000" /></view></view>
            <view class="form-group"><text class="form-label">答案（选填）</text><view class="input-wrapper"><textarea class="textarea-field" v-model="cardForm.answer" placeholder="可留空，仅上传图片" maxlength="2000" /></view></view>
            <view class="form-group"><text class="form-label">问题图片（可选）</text>
              <view class="image-upload-area">
                <view class="image-item" v-for="(img, idx) in cardForm.questionImages" :key="'q'+idx">
                  <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, cardForm.questionImages)" />
                  <view class="image-remove" @click="cardForm.questionImages.splice(idx, 1)">✕</view>
                </view>
                <view class="upload-actions">
                  <view class="upload-action-btn" @click="takePhoto('card_q')"><text class="action-icon">📷</text><text class="action-text">拍照</text></view>
                  <view class="upload-action-btn" @click="pickAlbum('card_q')"><text class="action-icon">🖼️</text><text class="action-text">相册</text></view>
                  <view class="upload-action-btn paste-btn" :class="{ active: activePasteTarget === 'card_q' }" @click="setPasteTarget('card_q')"><text class="action-icon">📋</text><text class="action-text">粘贴</text></view>
                </view>
              </view>
              <text class="paste-hint">💡 手机端可拍照或从相册选择，电脑端点击「粘贴」后按 Ctrl+V</text>
            </view>
            <view class="form-group"><text class="form-label">答案图片（可选）</text>
              <view class="image-upload-area">
                <view class="image-item" v-for="(img, idx) in cardForm.answerImages" :key="'a'+idx">
                  <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, cardForm.answerImages)" />
                  <view class="image-remove" @click="cardForm.answerImages.splice(idx, 1)">✕</view>
                </view>
                <view class="upload-actions">
                  <view class="upload-action-btn" @click="takePhoto('card_a')"><text class="action-icon">📷</text><text class="action-text">拍照</text></view>
                  <view class="upload-action-btn" @click="pickAlbum('card_a')"><text class="action-icon">🖼️</text><text class="action-text">相册</text></view>
                  <view class="upload-action-btn paste-btn" :class="{ active: activePasteTarget === 'card_a' }" @click="setPasteTarget('card_a')"><text class="action-icon">📋</text><text class="action-text">粘贴</text></view>
                </view>
              </view>
              <text class="paste-hint">💡 手机端可拍照或从相册选择，电脑端点击「粘贴」后按 Ctrl+V</text>
            </view>
          </scroll-view>
          <view class="modal-footer"><view class="cancel-btn" @click="showCardForm = false">取消</view><view class="submit-btn" @click="submitCard">提交</view></view>
        </view>
      </view>

      <!-- Edit Card Modal -->
      <view class="modal-overlay" v-if="showEditCard" @click="showEditCard = false">
        <view class="modal-content" @click.stop>
          <view class="modal-header"><text class="modal-title">编辑知识卡片</text><view class="modal-close" @click="showEditCard = false">✕</view></view>
          <scroll-view scroll-y class="modal-body">
            <view class="form-group"><text class="form-label">科目</text>
              <view class="subject-grid"><view class="subject-item" v-for="s in allSubjects" :key="s" :class="{ active: editForm.subject === s }" @click="editForm.subject = s">{{ s }}</view></view>
            </view>
            <view class="form-group"><text class="form-label">标签</text>
              <view class="tag-picker" v-if="cardAvailableTags.length > 0">
                <view class="tag-picker-chip" v-for="t in cardAvailableTags" :key="t" :class="{ picked: editForm.tags.includes(t) }" @click="toggleEditTag(t)">{{ t }}</view>
              </view>
              <view class="input-wrapper" style="margin-top: 8px;">
                <input class="input-field" v-model="editTagInput" placeholder="输入新标签，逗号分隔..." @blur="parseEditTags" @confirm="parseEditTags" />
              </view>
              <view class="tag-preview" v-if="editForm.tags.length > 0"><view class="tag-chip" v-for="(t, idx) in editForm.tags" :key="idx">{{ t }}<text class="tag-remove" @click="editForm.tags.splice(idx, 1)">✕</text></view></view>
            </view>
            <view class="form-group"><text class="form-label">问题（选填）</text><view class="input-wrapper"><textarea class="textarea-field" v-model="editForm.question" placeholder="可留空" maxlength="2000" /></view></view>
            <view class="form-group"><text class="form-label">答案（选填）</text><view class="input-wrapper"><textarea class="textarea-field" v-model="editForm.answer" placeholder="可留空" maxlength="2000" /></view></view>
            <view class="form-group"><text class="form-label">问题图片（可选）</text>
              <view class="image-upload-area">
                <view class="image-item" v-for="(img, idx) in editForm.questionImages" :key="'eq'+idx">
                  <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, editForm.questionImages)" />
                  <view class="image-remove" @click="editForm.questionImages.splice(idx, 1)">✕</view>
                </view>
                <view class="upload-actions">
                  <view class="upload-action-btn" @click="takePhoto('edit_card_q')"><text class="action-icon">📷</text><text class="action-text">拍照</text></view>
                  <view class="upload-action-btn" @click="pickAlbum('edit_card_q')"><text class="action-icon">🖼️</text><text class="action-text">相册</text></view>
                  <view class="upload-action-btn paste-btn" :class="{ active: activePasteTarget === 'edit_card_q' }" @click="setPasteTarget('edit_card_q')"><text class="action-icon">📋</text><text class="action-text">粘贴</text></view>
                </view>
              </view>
            </view>
            <view class="form-group"><text class="form-label">答案图片（可选）</text>
              <view class="image-upload-area">
                <view class="image-item" v-for="(img, idx) in editForm.answerImages" :key="'ea'+idx">
                  <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, editForm.answerImages)" />
                  <view class="image-remove" @click="editForm.answerImages.splice(idx, 1)">✕</view>
                </view>
                <view class="upload-actions">
                  <view class="upload-action-btn" @click="takePhoto('edit_card_a')"><text class="action-icon">📷</text><text class="action-text">拍照</text></view>
                  <view class="upload-action-btn" @click="pickAlbum('edit_card_a')"><text class="action-icon">🖼️</text><text class="action-text">相册</text></view>
                  <view class="upload-action-btn paste-btn" :class="{ active: activePasteTarget === 'edit_card_a' }" @click="setPasteTarget('edit_card_a')"><text class="action-icon">📋</text><text class="action-text">粘贴</text></view>
                </view>
              </view>
            </view>
          </scroll-view>
          <view class="modal-footer"><view class="cancel-btn" @click="showEditCard = false">取消</view><view class="submit-btn" @click="saveEditCard">保存</view></view>
        </view>
      </view>

      <!-- Card FAB -->
      <view class="fab purple" @click="showCardForm = true"><text class="fab-icon">+</text></view>
    </template>

    <!-- ==================== 错题本视图 ==================== -->
    <template v-if="currentView === 'mistakes'">
      <view class="mode-toggle">
        <view class="mode-btn" :class="{ active: mistakeViewMode === 'pending' }" @click="switchMistakeMode('pending')">今日复习</view>
        <view class="mode-btn" :class="{ active: mistakeViewMode === 'all' }" @click="switchMistakeMode('all')">查看全部</view>
      </view>

      <!-- Mistake Subject Filter (一级) -->
      <view class="filter-section">
        <view class="filter-row">
          <scroll-view scroll-x class="filter-scroll">
            <view class="filter-list">
              <view class="filter-item" :class="{ active: activeSubject === '' }" @click="onSubjectChange('')">全部科目</view>
              <view class="filter-item" v-for="s in allSubjects" :key="s" :class="{ active: activeSubject === s }" @click="onSubjectChange(s)">{{ s }}</view>
            </view>
          </scroll-view>
          <view class="filter-manage-btn" @click="showManageSubjects = true">⚙</view>
        </view>
      </view>

      <!-- Mistake Tag Filter (二级，联动科目) -->
      <view class="filter-section" v-if="availableMistakeTags.length > 0">
        <view class="filter-row">
          <scroll-view scroll-x class="filter-scroll">
            <view class="filter-list">
              <view class="filter-item tag-item" :class="{ active: activeTags.length === 0 }" @click="activeTags = []; tagLogic = 'or'">全部标签</view>
              <view class="filter-item tag-item" v-for="t in availableMistakeTags" :key="t" :class="{ active: activeTags.includes(t) }" @click="toggleTag(t)">{{ t }}</view>
            </view>
          </scroll-view>
          <view class="tag-logic-btn" v-if="activeTags.length > 1" @click="tagLogic = tagLogic === 'or' ? 'and' : 'or'">
            <text>{{ tagLogic === 'or' ? '或' : '且' }}</text>
          </view>
        </view>
      </view>

      <!-- Mistake Error Count Filter -->
      <view class="filter-section">
        <scroll-view scroll-x class="filter-scroll">
          <view class="filter-list">
            <view class="filter-item err-item" :class="{ active: activeErrorCount === '' }" @click="activeErrorCount = ''">全部次数</view>
            <view class="filter-item err-item err-1" :class="{ active: activeErrorCount === '1' }" @click="activeErrorCount = '1'">做错1次</view>
            <view class="filter-item err-item err-2" :class="{ active: activeErrorCount === '2' }" @click="activeErrorCount = '2'">做错2次</view>
            <view class="filter-item err-item err-3" :class="{ active: activeErrorCount === '3+' }" @click="activeErrorCount = '3+'">做错3次+</view>
          </view>
        </scroll-view>
      </view>

      <!-- Mistake Review Mode -->
      <view class="review-card" v-if="mistakeReviewMode && mistakeReviewCards.length > 0">
        <text class="review-counter">{{ mistakeReviewIndex + 1 }} / {{ mistakeReviewCards.length }}</text>
        <view class="review-card-body">
          <view class="review-subject">{{ mistakeReviewCards[mistakeReviewIndex].subject }}</view>
          <view class="review-question"><text class="question-label red">Q</text><text class="question-text">{{ mistakeReviewCards[mistakeReviewIndex].question }}</text></view>
          <view class="review-answer" v-if="mistakeShowAnswer">
            <view class="answer-divider"></view>
            <view class="answer-content"><text class="answer-label">A</text><text class="answer-text">{{ mistakeReviewCards[mistakeReviewIndex].answer }}</text></view>
            <view v-if="mistakeReviewCards[mistakeReviewIndex].analysis" class="analysis-content">
              <text class="analysis-label">分析</text><text class="analysis-text">{{ mistakeReviewCards[mistakeReviewIndex].analysis }}</text>
            </view>
          </view>
        </view>
        <view class="review-actions">
          <view class="show-answer-btn red-bg" v-if="!mistakeShowAnswer" @click="mistakeShowAnswer = true"><text>点击查看答案</text></view>
          <view class="review-result-btns" v-else>
            <view class="result-btn wrong" @click="reviewMistakeResult(false)"><text class="result-icon">❌</text><text class="result-text">做错了</text></view>
            <view class="result-btn correct" @click="reviewMistakeResult(true)"><text class="result-icon">✅</text><text class="result-text">做对了</text></view>
          </view>
        </view>
      </view>
      <view class="review-complete" v-if="mistakeReviewMode && mistakeReviewCards.length === 0">
        <text class="complete-icon">🎉</text><text class="complete-text">今天没有需要复习的错题</text>
        <view class="back-btn" @click="exitMistakeReview">查看全部</view>
      </view>
      <view class="review-complete" v-if="mistakeReviewComplete">
        <text class="complete-icon">🏆</text><text class="complete-text">复习完成！</text>
        <text class="complete-hint">正确 {{ reviewCorrect }} / {{ reviewTotal }} 道</text>
        <view class="back-btn" @click="exitMistakeReview">返回错题列表</view>
      </view>

      <view v-if="!mistakeReviewMode && !mistakeReviewComplete">
        <view class="section-header" v-if="mistakeViewMode === 'pending' && filteredMistakes.length > 0">
          <text class="section-title">今日待复习 · {{ filteredMistakes.length }} 道</text>
          <view class="start-review-btn red" @click="startMistakeReview"><text>开始复习</text></view>
        </view>
        <view class="empty" v-if="filteredMistakes.length === 0">
          <text class="empty-icon">📝</text><text class="empty-text">{{ mistakeViewMode === 'pending' ? '今天没有需要复习的错题' : '暂无错题' }}</text>
          <text class="empty-hint">点击右下角按钮，手动录入错题</text>
        </view>
        <view class="load-more" v-if="filteredMistakes.length > mistakesPageSize" @click="showAllMistakes">
          <text>展开全部 {{ filteredMistakes.length }} 道错题 ▾</text>
        </view>
        <view class="mistake-card" v-for="mistake in displayedMistakes" :key="mistake.id" :class="{ mastered: mistake.mastered === '1' }">
          <view class="mistake-header">
            <text class="mistake-subject">{{ mistake.subject }}</text>
            <view class="mistake-tags">
              <view class="mistake-tag" v-for="t in (mistake.tags || [])" :key="t">{{ t }}</view>
              <view class="mistake-tag" :class="mistake.difficulty">{{ getDifficultyLabel(mistake.difficulty) }}</view>
              <view class="mistake-tag mastered-tag" v-if="mistake.mastered === '1'">已掌握</view>
            </view>
          </view>
          <view class="mistake-question-section"><text class="section-label">题目</text><text class="mistake-question">{{ mistake.question }}</text>
            <view class="card-images" v-if="mistake.question_images && mistake.question_images.length > 0">
              <image v-for="(img, i) in mistake.question_images" :key="i" :src="img" mode="aspectFill" class="card-img-item" @click="previewImage(img, mistake.question_images)" />
            </view>
          </view>
          <view class="mistake-answer-section"><text class="section-label">正确答案</text><text class="mistake-answer">{{ mistake.answer }}</text></view>
          <view class="mistake-analysis-section" v-if="mistake.analysis"><text class="section-label">错误分析</text><text class="mistake-analysis">{{ mistake.analysis }}</text></view>
          <view class="mistake-footer">
            <text class="mistake-date">{{ formatDate(mistake.created_at) }}</text>
            <text class="correct-progress" v-if="!mistake.mastered || mistake.mastered === '0'">正确 {{ mistake.correct_count }}/2 次</text>
            <text class="error-count">做错 {{ mistake.error_count }} 次</text>
            <view class="mistake-actions">
              <view class="action-btn edit-btn" @click="openEditMistake(mistake)">编辑</view>
              <view class="action-btn master-btn" @click="toggleMastered(mistake)">{{ mistake.mastered === '1' ? '重新攻克' : '已掌握' }}</view>
              <view class="action-btn del-btn" @click="removeMistake(mistake)">删除</view>
            </view>
          </view>
        </view>
      </view>

      <!-- Add Mistake Modal -->
      <view class="modal-overlay" v-if="showMistakeForm" @click="showMistakeForm = false">
        <view class="modal-content" @click.stop>
          <view class="modal-header"><text class="modal-title">添加错题</text><view class="modal-close" @click="showMistakeForm = false">✕</view></view>
          <scroll-view scroll-y class="modal-body">
            <view class="form-group"><text class="form-label">科目</text>
              <view class="subject-grid">
                <view class="subject-item" v-for="s in allSubjects" :key="s" :class="{ active: mistakeForm.subject === s }" @click="mistakeForm.subject = s">{{ s }}</view>
                <view class="subject-item subject-add" @click="showMistakeSubjectInput = !showMistakeSubjectInput">
                  <text v-if="!showMistakeSubjectInput">+ 自定义</text><text v-else>收起</text>
                </view>
              </view>
              <view class="input-wrapper" v-if="showMistakeSubjectInput" style="margin-top: 10px;">
                <input class="input-field" v-model="customMistakeSubject" placeholder="输入自定义科目..." @confirm="addMistakeCustomSubject" />
              </view>
            </view>
            <view class="form-group"><text class="form-label">标签</text>
              <view class="tag-picker" v-if="mistakeAvailableTags.length > 0">
                <view class="tag-picker-chip" v-for="t in mistakeAvailableTags" :key="t" :class="{ picked: mistakeForm.tags.includes(t) }" @click="toggleMistakeFormTag(t)">{{ t }}</view>
              </view>
              <view class="input-wrapper" style="margin-top: 8px;">
                <input class="input-field" v-model="mistakeTagInput" placeholder="输入新标签，逗号分隔..." @blur="parseMistakeTags" @confirm="parseMistakeTags" />
              </view>
              <view class="tag-preview" v-if="mistakeForm.tags.length > 0"><view class="tag-chip red-chip" v-for="(t, idx) in mistakeForm.tags" :key="idx">{{ t }}<text class="tag-remove red-remove" @click="mistakeForm.tags.splice(idx, 1)">✕</text></view></view>
            </view>
            <view class="form-group"><text class="form-label">题目内容（选填）</text><view class="input-wrapper"><textarea class="textarea-field" v-model="mistakeForm.question" placeholder="可留空，仅上传图片" maxlength="2000" /></view></view>
            <view class="form-group"><text class="form-label">正确答案（选填）</text><view class="input-wrapper"><textarea class="textarea-field" v-model="mistakeForm.answer" placeholder="可留空，仅上传图片" maxlength="2000" /></view></view>
            <view class="form-group"><text class="form-label">错误分析（可选）</text><view class="input-wrapper"><textarea class="textarea-field" v-model="mistakeForm.analysis" placeholder="分析错误原因..." maxlength="2000" /></view></view>
            <view class="form-group"><text class="form-label">难度</text>
              <view class="difficulty-row">
                <view class="diff-item" :class="{ active: mistakeForm.difficulty === 'easy' }" @click="mistakeForm.difficulty = 'easy'">简单</view>
                <view class="diff-item" :class="{ active: mistakeForm.difficulty === 'medium' }" @click="mistakeForm.difficulty = 'medium'">中等</view>
                <view class="diff-item" :class="{ active: mistakeForm.difficulty === 'hard' }" @click="mistakeForm.difficulty = 'hard'">困难</view>
              </view>
            </view>
            <view class="form-group"><text class="form-label">题目图片（可选）</text>
              <view class="image-upload-area">
                <view class="image-item" v-for="(img, idx) in mistakeForm.questionImages" :key="'mq'+idx">
                  <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, mistakeForm.questionImages)" />
                  <view class="image-remove" @click="mistakeForm.questionImages.splice(idx, 1)">✕</view>
                </view>
                <view class="upload-actions">
                  <view class="upload-action-btn" @click="takePhoto('mistake_q')"><text class="action-icon">📷</text><text class="action-text">拍照</text></view>
                  <view class="upload-action-btn" @click="pickAlbum('mistake_q')"><text class="action-icon">🖼️</text><text class="action-text">相册</text></view>
                  <view class="upload-action-btn paste-btn" :class="{ active: activePasteTarget === 'mistake_q' }" @click="setPasteTarget('mistake_q')"><text class="action-icon">📋</text><text class="action-text">粘贴</text></view>
                </view>
              </view>
              <text class="paste-hint">💡 手机端可拍照或从相册选择，电脑端点击「粘贴」后按 Ctrl+V</text>
            </view>
            <view class="form-group"><text class="form-label">答案图片（可选）</text>
              <view class="image-upload-area">
                <view class="image-item" v-for="(img, idx) in mistakeForm.answerImages" :key="'ma'+idx">
                  <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, mistakeForm.answerImages)" />
                  <view class="image-remove" @click="mistakeForm.answerImages.splice(idx, 1)">✕</view>
                </view>
                <view class="upload-actions">
                  <view class="upload-action-btn" @click="takePhoto('mistake_a')"><text class="action-icon">📷</text><text class="action-text">拍照</text></view>
                  <view class="upload-action-btn" @click="pickAlbum('mistake_a')"><text class="action-icon">🖼️</text><text class="action-text">相册</text></view>
                  <view class="upload-action-btn paste-btn" :class="{ active: activePasteTarget === 'mistake_a' }" @click="setPasteTarget('mistake_a')"><text class="action-icon">📋</text><text class="action-text">粘贴</text></view>
                </view>
              </view>
              <text class="paste-hint">💡 手机端可拍照或从相册选择，电脑端点击「粘贴」后按 Ctrl+V</text>
            </view>
          </scroll-view>
          <view class="modal-footer"><view class="cancel-btn" @click="showMistakeForm = false">取消</view><view class="submit-btn red-btn" @click="submitMistake">提交</view></view>
        </view>
      </view>

      <!-- Edit Mistake Modal -->
      <view class="modal-overlay" v-if="showEditMistake" @click="showEditMistake = false">
        <view class="modal-content" @click.stop>
          <view class="modal-header"><text class="modal-title">编辑错题</text><view class="modal-close" @click="showEditMistake = false">✕</view></view>
          <scroll-view scroll-y class="modal-body">
            <view class="form-group"><text class="form-label">科目</text>
              <view class="subject-grid"><view class="subject-item" v-for="s in allSubjects" :key="s" :class="{ active: editMistakeForm.subject === s }" @click="editMistakeForm.subject = s">{{ s }}</view>
                <view class="subject-item subject-add" @click="showEditMistakeSubjectInput = !showEditMistakeSubjectInput">
                  <text v-if="!showEditMistakeSubjectInput">+ 自定义</text><text v-else>收起</text>
                </view>
              </view>
              <view class="input-wrapper" v-if="showEditMistakeSubjectInput" style="margin-top: 10px;">
                <input class="input-field" v-model="customEditMistakeSubject" placeholder="输入自定义科目..." @confirm="addEditMistakeCustomSubject" />
              </view>
            </view>
            <view class="form-group"><text class="form-label">标签</text>
              <view class="tag-picker" v-if="mistakeAvailableTags.length > 0">
                <view class="tag-picker-chip" v-for="t in mistakeAvailableTags" :key="t" :class="{ picked: editMistakeForm.tags.includes(t) }" @click="toggleEditMistakeTag(t)">{{ t }}</view>
              </view>
              <view class="input-wrapper" style="margin-top: 8px;">
                <input class="input-field" v-model="editMistakeTagInput" placeholder="输入新标签，逗号分隔..." @blur="parseEditMistakeTags" @confirm="parseEditMistakeTags" />
              </view>
            </view>
            <view class="form-group"><text class="form-label">题目内容（选填）</text><view class="input-wrapper"><textarea class="textarea-field" v-model="editMistakeForm.question" placeholder="可留空" maxlength="2000" /></view></view>
            <view class="form-group"><text class="form-label">正确答案（选填）</text><view class="input-wrapper"><textarea class="textarea-field" v-model="editMistakeForm.answer" placeholder="可留空" maxlength="2000" /></view></view>
            <view class="form-group"><text class="form-label">错误分析（可选）</text><view class="input-wrapper"><textarea class="textarea-field" v-model="editMistakeForm.analysis" placeholder="分析错误原因..." maxlength="2000" /></view></view>
            <view class="form-group"><text class="form-label">难度</text>
              <view class="difficulty-row">
                <view class="diff-item" :class="{ active: editMistakeForm.difficulty === 'easy' }" @click="editMistakeForm.difficulty = 'easy'">简单</view>
                <view class="diff-item" :class="{ active: editMistakeForm.difficulty === 'medium' }" @click="editMistakeForm.difficulty = 'medium'">中等</view>
                <view class="diff-item" :class="{ active: editMistakeForm.difficulty === 'hard' }" @click="editMistakeForm.difficulty = 'hard'">困难</view>
              </view>
            </view>
            <view class="form-group"><text class="form-label">题目图片（可选）</text>
              <view class="image-upload-area">
                <view class="image-item" v-for="(img, idx) in editMistakeForm.questionImages" :key="'emq'+idx">
                  <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, editMistakeForm.questionImages)" />
                  <view class="image-remove" @click="editMistakeForm.questionImages.splice(idx, 1)">✕</view>
                </view>
                <view class="upload-actions">
                  <view class="upload-action-btn" @click="takePhoto('edit_mistake_q')"><text class="action-icon">📷</text><text class="action-text">拍照</text></view>
                  <view class="upload-action-btn" @click="pickAlbum('edit_mistake_q')"><text class="action-icon">🖼️</text><text class="action-text">相册</text></view>
                  <view class="upload-action-btn paste-btn" :class="{ active: activePasteTarget === 'edit_mistake_q' }" @click="setPasteTarget('edit_mistake_q')"><text class="action-icon">📋</text><text class="action-text">粘贴</text></view>
                </view>
              </view>
            </view>
            <view class="form-group"><text class="form-label">答案图片（可选）</text>
              <view class="image-upload-area">
                <view class="image-item" v-for="(img, idx) in editMistakeForm.answerImages" :key="'ema'+idx">
                  <image :src="img" mode="aspectFill" class="uploaded-image" @click="previewImage(img, editMistakeForm.answerImages)" />
                  <view class="image-remove" @click="editMistakeForm.answerImages.splice(idx, 1)">✕</view>
                </view>
                <view class="upload-actions">
                  <view class="upload-action-btn" @click="takePhoto('edit_mistake_a')"><text class="action-icon">📷</text><text class="action-text">拍照</text></view>
                  <view class="upload-action-btn" @click="pickAlbum('edit_mistake_a')"><text class="action-icon">🖼️</text><text class="action-text">相册</text></view>
                  <view class="upload-action-btn paste-btn" :class="{ active: activePasteTarget === 'edit_mistake_a' }" @click="setPasteTarget('edit_mistake_a')"><text class="action-icon">📋</text><text class="action-text">粘贴</text></view>
                </view>
              </view>
            </view>
          </scroll-view>
          <view class="modal-footer"><view class="cancel-btn" @click="showEditMistake = false">取消</view><view class="submit-btn red-btn" @click="saveEditMistake">保存</view></view>
        </view>
      </view>

      <!-- Mistake FAB -->
      <view class="fab red" @click="showMistakeForm = true"><text class="fab-icon">+</text></view>
    </template>

    <!-- Export Modal -->
    <view class="export-overlay" v-if="showExportModal" @click="showExportModal = false">
      <view class="export-dialog" @click.stop>
        <view class="export-dialog-top"><text class="export-dialog-title">{{ currentView === 'mistakes' ? '导出错题本' : '导出知识卡片' }}</text>
          <view class="export-dialog-close" @click="showExportModal = false">✕</view>
        </view>
        <view class="export-dialog-body">
          <view class="export-option" @click="doExport('csv')"><text class="export-opt-icon">📄</text><view class="export-opt-right"><text class="export-opt-label">导出 CSV</text><text class="export-opt-desc">表格数据，可用 Excel 打开</text></view></view>
          <view class="export-option" @click="doExport('excel')"><text class="export-opt-icon">📊</text><view class="export-opt-right"><text class="export-opt-label">导出 Excel</text><text class="export-opt-desc">HTML 表格格式，兼容 Excel</text></view></view>
          <view class="export-option" @click="doExport('pdf')"><text class="export-opt-icon">🖨</text><view class="export-opt-right"><text class="export-opt-label">导出 PDF</text><text class="export-opt-desc">调用浏览器打印，保存为 PDF</text></view></view>
          <view class="export-answer-toggle"><text class="export-toggle-label">导出内容包含答案</text>
            <view class="export-switch" :class="{ on: exportIncludeAnswer }" @click.stop="exportIncludeAnswer = !exportIncludeAnswer"><view class="export-switch-dot"></view></view>
          </view>
        </view>
      </view>
    </view>

    <!-- Manage Subjects Modal -->
    <view class="export-overlay" v-if="showManageSubjects" @click="showManageSubjects = false">
      <view class="export-dialog" @click.stop>
        <view class="export-dialog-top"><text class="export-dialog-title">管理科目</text><view class="export-dialog-close" @click="showManageSubjects = false">✕</view></view>
        <view class="export-dialog-body">
          <view class="manage-item" v-for="s in allSubjects" :key="s">
            <view class="manage-left"><text class="manage-name">{{ s }}</text><text class="manage-badge" v-if="!customSubjects.includes(s)">预设</text><text class="manage-badge custom-badge" v-else>自定义</text></view>
            <view class="manage-del-btn" v-if="customSubjects.includes(s)" @click="removeSubject(s)">删除</view>
          </view>
          <view class="manage-add-row"><input class="manage-add-input" v-model="manageNewSubject" placeholder="输入新科目名称" @confirm="addManageSubject" /><view class="manage-add-btn" @click="addManageSubject">添加</view></view>
        </view>
      </view>
    </view>

    <view class="bottom-space"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { usePlanStore } from '@/stores/plan'
import { useUserStore } from '@/stores/user'
import * as api from '@/api/client'
import { exportCardsCSV, exportCardsExcel, exportCardsPDF, exportMistakesCSV, exportMistakesExcel, exportMistakesPDF, getDefaultTags, SUBJECT_TAGS } from '@/utils/export'

const planStore = usePlanStore()
const userStore = useUserStore()

const currentView = ref('cards')  // 'cards' | 'mistakes'
const today = new Date().toISOString().split('T')[0]

// ── Shared ──
const exportIncludeAnswer = ref(true)
const showExportModal = ref(false)
const showManageSubjects = ref(false)
const manageNewSubject = ref('')
const activeSubject = ref('')
const activeTags = ref([])
const tagLogic = ref('or') // 'or' = any tag match, 'and' = all tags must match

const defaultSubjects = Object.keys(SUBJECT_TAGS)
const allSubjects = ref([...defaultSubjects])
const customSubjects = ref([])

async function loadSubjects() {
  if (!userStore.isLoggedIn) return
  try {
    const res = await api.getUserSubjects()
    const saved = res.subjects || []
    customSubjects.value = saved.filter(s => !defaultSubjects.includes(s))
    // Merge: defaults first, then custom
    allSubjects.value = [...defaultSubjects]
    saved.forEach(s => { if (!allSubjects.value.includes(s)) allSubjects.value.push(s) })
  } catch (e) { /* offline: keep defaults */ }
}
async function saveSubjectToBackend(name) {
  try { await api.addUserSubject(name) } catch (e) { /* ignore */ }
}
async function deleteSubjectFromBackend(name) {
  try { await api.removeUserSubject(name) } catch (e) { /* ignore */ }
}

// ── Cards state ──
const cards = ref([])
const viewMode = ref('pending')
const activeMastery = ref('')
const showCardForm = ref(false)
const showCardSubjectInput = ref(false)
const customSubject = ref('')
const tagInput = ref('')
// Mistake form subject customization
const showMistakeSubjectInput = ref(false)
const customMistakeSubject = ref('')
const showEditMistakeSubjectInput = ref(false)
const customEditMistakeSubject = ref('')
const reviewMode = ref(false)
const reviewShowAnswer = ref(false)
const reviewIndex = ref(0)
const reviewComplete = ref(false)

const cardForm = ref({ subject: '数据结构', question: '', answer: '', tags: [], questionImages: [], answerImages: [] })
const editForm = ref({ subject: '', question: '', answer: '', tags: [], questionImages: [], answerImages: [] })
const editTagInput = ref('')
const showEditCard = ref(false)
const editingCardId = ref(null)

const pendingCardsCount = computed(() => cards.value.filter(c => c.next_review_date && c.next_review_date <= today).length)
const masteredCardsCount = computed(() => cards.value.filter(c => c.mastery_level === 'mastered').length)
const availableCardTags = computed(() => {
  if (activeSubject.value) return getDefaultTags(activeSubject.value)
  const set = new Set(); cards.value.forEach(c => (c.tags || []).forEach(t => set.add(t))); return [...set]
})

const availableMistakeTags = computed(() => {
  if (activeSubject.value) return getDefaultTags(activeSubject.value)
  const set = new Set(); mistakes.value.forEach(m => (m.tags || []).forEach(t => set.add(t))); return [...set]
})

// Tags available for picker in forms (from all cards/mistakes)
const cardAvailableTags = computed(() => {
  const set = new Set()
  cards.value.forEach(c => (c.tags || []).forEach(t => set.add(t)))
  return [...set].sort()
})
const mistakeAvailableTags = computed(() => {
  const set = new Set()
  mistakes.value.forEach(m => (m.tags || []).forEach(t => set.add(t)))
  return [...set].sort()
})

// Tag toggle helpers for forms
function toggleFormTag(formType, tag) {
  const arr = cardForm.value.tags
  const idx = arr.indexOf(tag)
  if (idx >= 0) arr.splice(idx, 1); else arr.push(tag)
}
function toggleEditTag(tag) {
  const arr = editForm.value.tags
  const idx = arr.indexOf(tag)
  if (idx >= 0) arr.splice(idx, 1); else arr.push(tag)
}
function toggleMistakeFormTag(tag) {
  const arr = mistakeForm.value.tags
  const idx = arr.indexOf(tag)
  if (idx >= 0) arr.splice(idx, 1); else arr.push(tag)
}
function toggleEditMistakeTag(tag) {
  const arr = editMistakeForm.value.tags
  const idx = arr.indexOf(tag)
  if (idx >= 0) arr.splice(idx, 1); else arr.push(tag)
}

function addMistakeCustomSubject() {
  const n = customMistakeSubject.value.trim()
  if (!n) return
  if (!allSubjects.value.includes(n)) { allSubjects.value.push(n); customSubjects.value.push(n); saveSubjectToBackend(n) }
  mistakeForm.value.subject = n; customMistakeSubject.value = ''; showMistakeSubjectInput.value = false
}
function addEditMistakeCustomSubject() {
  const n = customEditMistakeSubject.value.trim()
  if (!n) return
  if (!allSubjects.value.includes(n)) { allSubjects.value.push(n); customSubjects.value.push(n); saveSubjectToBackend(n) }
  editMistakeForm.value.subject = n; customEditMistakeSubject.value = ''; showEditMistakeSubjectInput.value = false
}

const filteredCards = computed(() => {
  let r = cards.value
  if (activeSubject.value) r = r.filter(c => c.subject === activeSubject.value)
  if (activeTags.value.length > 0) {
    r = tagLogic.value === 'and'
      ? r.filter(c => activeTags.value.every(t => (c.tags || []).includes(t)))
      : r.filter(c => activeTags.value.some(t => (c.tags || []).includes(t)))
  }
  if (activeMastery.value) r = r.filter(c => c.mastery_level === activeMastery.value)
  return r
})
const cardsPageSize = ref(10)
const displayedCards = computed(() => filteredCards.value.slice(0, cardsPageSize.value))
function showAllCards() { cardsPageSize.value = filteredCards.value.length }
const reviewCards = computed(() => filteredCards.value.filter(c => c.next_review_date && c.next_review_date <= today))

// ── Mistakes state ──
const mistakes = ref([])
const mistakeViewMode = ref('pending')
const activeErrorCount = ref('')
const showMistakeForm = ref(false)
const mistakeTagInput = ref('')
const mistakeReviewMode = ref(false)
const mistakeShowAnswer = ref(false)
const mistakeReviewIndex = ref(0)
const reviewCorrect = ref(0)
const reviewTotal = ref(0)
const mistakeReviewComplete = ref(false)
const showEditMistake = ref(false)
const editingMistakeId = ref(null)
const editMistakeTagInput = ref('')
const editMistakeForm = ref({ subject: '', question: '', answer: '', analysis: '', difficulty: 'medium', tags: [], questionImages: [], answerImages: [] })
const mistakeForm = ref({ subject: '数据结构', question: '', answer: '', analysis: '', difficulty: 'medium', tags: [], questionImages: [], answerImages: [] })

const masteredMistakesCount = computed(() => mistakes.value.filter(m => m.mastered === '1').length)
const activeMistakesCount = computed(() => mistakes.value.filter(m => m.mastered === '0').length)
const filteredMistakes = computed(() => {
  let r = mistakes.value
  if (activeSubject.value) r = r.filter(m => m.subject === activeSubject.value)
  if (activeTags.value.length > 0) {
    r = tagLogic.value === 'and'
      ? r.filter(m => activeTags.value.every(t => (m.tags || []).includes(t)))
      : r.filter(m => activeTags.value.some(t => (m.tags || []).includes(t)))
  }
  if (activeErrorCount.value === '1') r = r.filter(m => m.error_count === 1)
  else if (activeErrorCount.value === '2') r = r.filter(m => m.error_count === 2)
  else if (activeErrorCount.value === '3+') r = r.filter(m => m.error_count >= 3)
  return r
})
const mistakesPageSize = ref(10)
const displayedMistakes = computed(() => filteredMistakes.value.slice(0, mistakesPageSize.value))
function showAllMistakes() { mistakesPageSize.value = filteredMistakes.value.length }
const mistakeReviewCards = computed(() => filteredMistakes.value.filter(m => m.mastered === '0'))

// ── Helpers ──
function getMasteryLabel(l) { const m = { unmastered: '未掌握', familiar: '较熟悉', mastered: '已掌握' }; return m[l] || l }
function getMasteryClass(l) { const m = { unmastered: 'badge-red', familiar: 'badge-orange', mastered: 'badge-green' }; return m[l] || '' }
function getNextReviewHint(card) {
  const intervals = { unmastered: [1,1,2,3,5,8,14,21,30], familiar: [3,5,8,14,21,30], mastered: [7,14,30] }
  const levels = intervals[card.mastery_level] || intervals.unmastered
  const idx = Math.min(card.review_count, levels.length - 1)
  const days = levels[idx]
  const next = new Date()
  next.setDate(next.getDate() + days)
  return `${days}天后 (${next.getMonth()+1}月${next.getDate()}日)`
function getDifficultyLabel(d) { const m = { easy: '简单', medium: '中等', hard: '困难' }; return m[d] || d }
function formatDate(s) { if (!s) return ''; const d = new Date(s); return `${d.getMonth()+1}月${d.getDate()}日` }

// ── View switching ──
function switchView(view) {
  if (currentView.value === view) return
  currentView.value = view
  activeSubject.value = ''; activeTags.value = []; activeMastery.value = ''; activeErrorCount.value = ''
  if (view === 'cards') loadCards()
  else loadMistakes()
}

function onSubjectChange(s) { activeSubject.value = s; activeTags.value = []; tagLogic.value = 'or'; activeMastery.value = ''; activeErrorCount.value = ''; cardsPageSize.value = 10; mistakesPageSize.value = 10 }
function toggleTag(tag) {
  const idx = activeTags.value.indexOf(tag)
  if (idx >= 0) activeTags.value.splice(idx, 1)
  else activeTags.value.push(tag)
}

// ── Subject management ──
function addManageSubject() {
  const n = manageNewSubject.value.trim()
  if (!n) return
  if (!allSubjects.value.includes(n)) { allSubjects.value.push(n); customSubjects.value.push(n); saveSubjectToBackend(n) }
  manageNewSubject.value = ''
}
function removeSubject(n) {
  uni.showModal({ title: '删除科目', content: `确定要删除「${n}」吗？`, success: r => {
    if (r.confirm) {
      customSubjects.value = customSubjects.value.filter(s => s !== n)
      allSubjects.value = allSubjects.value.filter(s => s !== n)
      deleteSubjectFromBackend(n)
      if (activeSubject.value === n) { activeSubject.value = ''; activeTags.value = [] }
    }
  }})
}

// ── Cards functions ──
function addCardCustomSubject() { const n = customSubject.value.trim(); if (!n) return; if (!allSubjects.value.includes(n)) { allSubjects.value.push(n); customSubjects.value.push(n); saveSubjectToBackend(n) }; cardForm.value.subject = n; customSubject.value = ''; showCardSubjectInput.value = false }
// ── Image upload: 拍照 / 相册 / Ctrl+V 粘贴 ──
const activePasteTarget = ref('')
function setPasteTarget(target) {
  activePasteTarget.value = target
  // #ifdef H5
  uni.showToast({ title: '请按 Ctrl+V 粘贴图片', icon: 'none', duration: 1500 })
  // #endif
}
function getTargetArray(target) {
  if (!target) return null
  if (target === 'card_q') return cardForm.value.questionImages
  if (target === 'card_a') return cardForm.value.answerImages
  if (target === 'edit_card_q') return editForm.value.questionImages
  if (target === 'edit_card_a') return editForm.value.answerImages
  if (target === 'mistake_q') return mistakeForm.value.questionImages
  if (target === 'mistake_a') return mistakeForm.value.answerImages
  if (target === 'edit_mistake_q') return editMistakeForm.value.questionImages
  if (target === 'edit_mistake_a') return editMistakeForm.value.answerImages
  return null
}
// ── Convert any image source to base64 data URL ──
function imgSrcToBase64(src) {
  return new Promise((resolve) => {
    // Already base64
    if (typeof src === 'string' && src.startsWith('data:')) return resolve(src)
    // #ifdef H5
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas')
        const maxW = 1200; const maxH = 1200
        let w = img.naturalWidth; let h = img.naturalHeight
        if (w > maxW || h > maxH) { const r = Math.min(maxW / w, maxH / h); w = Math.round(w * r); h = Math.round(h * r) }
        canvas.width = w; canvas.height = h
        canvas.getContext('2d').drawImage(img, 0, 0, w, h)
        resolve(canvas.toDataURL('image/jpeg', 0.75))
      } catch (e) { resolve(src) }
    }
    img.onerror = () => resolve(src)
    img.src = src
    // #endif
    // #ifndef H5
    // For mini-program, read file as base64
    try {
      const fs = uni.getFileSystemManager()
      const data = fs.readFileSync(src, 'base64')
      resolve(`data:image/jpeg;base64,${data}`)
    } catch (e) { resolve(src) }
    // #endif
  })
}

function takePhoto(target) {
  uni.chooseImage({
    count: 1, sizeType: ['compressed'], sourceType: ['camera'],
    success: async (res) => {
      const arr = getTargetArray(target)
      if (!arr) return
      for (const fp of res.tempFilePaths) { arr.push(await imgSrcToBase64(fp)) }
    }
  })
}
function pickAlbum(target) {
  uni.chooseImage({
    count: 9, sizeType: ['compressed'], sourceType: ['album'],
    success: async (res) => {
      const arr = getTargetArray(target)
      if (!arr) return
      for (const fp of res.tempFilePaths) { arr.push(await imgSrcToBase64(fp)) }
    }
  })
}
async function handleGlobalPaste(e) {
  if (!activePasteTarget.value) return
  const items = e.clipboardData?.items
  if (!items) return
  const files = []
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) files.push(file)
    }
  }
  if (files.length === 0) return
  e.preventDefault()
  const arr = getTargetArray(activePasteTarget.value)
  if (arr) {
    for (const file of files) {
      const blobUrl = URL.createObjectURL(file)
      const b64 = await imgSrcToBase64(blobUrl)
      URL.revokeObjectURL(blobUrl)
      arr.push(b64)
    }
    uni.showToast({ title: `已粘贴 ${files.length} 张图片`, icon: 'success' })
  }
}
function parseTags() { if (!tagInput.value.trim()) return; const t = tagInput.value.split(/[,，]/).map(s => s.trim()).filter(Boolean); cardForm.value.tags = [...new Set([...cardForm.value.tags, ...t])]; tagInput.value = '' }
function parseEditTags() { if (!editTagInput.value.trim()) return; const t = editTagInput.value.split(/[,，]/).map(s => s.trim()).filter(Boolean); editForm.value.tags = [...new Set([...editForm.value.tags, ...t])]; editTagInput.value = '' }
function switchCardMode(m) {
  viewMode.value = m
  reviewMode.value = false
  reviewComplete.value = false
  reviewIndex.value = 0
  cardsPageSize.value = 10
  loadCards()
}
function switchMistakeMode(m) {
  mistakeViewMode.value = m
  mistakeReviewMode.value = false
  mistakeReviewComplete.value = false
  mistakeReviewIndex.value = 0
  mistakesPageSize.value = 10
  loadMistakes()
}
function previewImage(c, u) { uni.previewImage({ current: c, urls: u }) }

async function submitCard() {
  const hasQ = cardForm.value.question.trim() || cardForm.value.questionImages.length > 0
  const hasA = cardForm.value.answer.trim() || cardForm.value.answerImages.length > 0
  if (!hasQ) { uni.showToast({ title: '请至少填写问题或上传问题图片', icon: 'none' }); return }
  if (!hasA) { uni.showToast({ title: '请至少填写答案或上传答案图片', icon: 'none' }); return }
  if (!planStore.currentPlan) { uni.showToast({ title: '请先创建学习计划', icon: 'none' }); return }
  uni.showLoading({ title: '保存中...' })
  try {
    await api.createCard({ plan_id: planStore.currentPlan.id, question: cardForm.value.question, answer: cardForm.value.answer, subject: cardForm.value.subject, mastery_level: 'unmastered', next_review_date: today, question_images: cardForm.value.questionImages, answer_images: cardForm.value.answerImages, tags: cardForm.value.tags })
    showCardForm.value = false; cardForm.value = { subject: '数据结构', question: '', answer: '', tags: [], questionImages: [], answerImages: [] }
    uni.showToast({ title: '添加成功', icon: 'success' }); await loadCards()
  } catch (e) { uni.showToast({ title: e.message || '保存失败', icon: 'none' }) } finally { uni.hideLoading() }
}

function openEditCard(card) {
  editingCardId.value = card.id; editForm.value = { subject: card.subject, question: card.question, answer: card.answer, tags: [...(card.tags || [])], questionImages: [...(card.question_images || [])], answerImages: [...(card.answer_images || [])] }; editTagInput.value = ''; showEditCard.value = true
}
async function saveEditCard() {
  const hasQ = editForm.value.question.trim() || editForm.value.questionImages.length > 0
  const hasA = editForm.value.answer.trim() || editForm.value.answerImages.length > 0
  if (!hasQ || !hasA) { uni.showToast({ title: '请至少保证问题和答案有一方非空', icon: 'none' }); return }
  uni.showLoading({ title: '保存中...' })
  try { await api.updateCard(editingCardId.value, { question: editForm.value.question, answer: editForm.value.answer, subject: editForm.value.subject, tags: editForm.value.tags, question_images: editForm.value.questionImages, answer_images: editForm.value.answerImages }); showEditCard.value = false; uni.showToast({ title: '编辑成功', icon: 'success' }); await loadCards() }
  catch (e) { uni.showToast({ title: e.message || '保存失败', icon: 'none' }) } finally { uni.hideLoading() }
}
async function removeCard(card) {
  const r = await new Promise(r => uni.showModal({ title: '删除确认', content: '确定删除吗？', success: r }))
  if (r.confirm) { try { await api.deleteCard(card.id); cards.value = cards.value.filter(c => c.id !== card.id); uni.showToast({ title: '已删除', icon: 'success' }) } catch (e) { uni.showToast({ title: '删除失败', icon: 'none' }) } }
}
function startCardReview() { reviewMode.value = true; reviewShowAnswer.value = false; reviewIndex.value = 0; reviewComplete.value = false }
async function reviewCardResult(level) {
  const c = reviewCards.value[reviewIndex.value]
  const updated = await api.reviewCard(c.id, level)
  // Immediately sync next_review_date + mastery to the in-memory card
  if (updated) {
    c.mastery_level = updated.mastery_level
    c.next_review_date = updated.next_review_date
    c.review_count = updated.review_count
  }
  if (reviewIndex.value < reviewCards.value.length - 1) { reviewIndex.value++; reviewShowAnswer.value = false }
  else { reviewMode.value = false; reviewComplete.value = true; await loadCards() }
}
function exitCardReview() { reviewMode.value = false; reviewComplete.value = false; reviewIndex.value = 0; viewMode.value = 'all'; activeSubject.value = ''; activeTags.value = []; activeMastery.value = ''; loadCards() }
async function loadCards() { if (!planStore.currentPlan) return; try { const p = viewMode.value === 'pending'; const r = await api.getCards(planStore.currentPlan.id, activeSubject.value || null, null, p); cards.value = r.cards || [] } catch (e) { console.error('loadCards:', e) } }

// ── Mistakes functions ──
function parseMistakeTags() { if (!mistakeTagInput.value.trim()) return; const t = mistakeTagInput.value.split(/[,，]/).map(s => s.trim()).filter(Boolean); mistakeForm.value.tags = [...new Set([...mistakeForm.value.tags, ...t])]; mistakeTagInput.value = '' }
function parseEditMistakeTags() { if (!editMistakeTagInput.value.trim()) return; const t = editMistakeTagInput.value.split(/[,，]/).map(s => s.trim()).filter(Boolean); editMistakeForm.value.tags = [...new Set([...editMistakeForm.value.tags, ...t])]; editMistakeTagInput.value = '' }

async function submitMistake() {
  const hasQ = mistakeForm.value.question.trim() || mistakeForm.value.questionImages.length > 0
  const hasA = mistakeForm.value.answer.trim() || mistakeForm.value.answerImages.length > 0
  if (!hasQ) { uni.showToast({ title: '请至少填写题目或上传题目图片', icon: 'none' }); return }
  if (!hasA) { uni.showToast({ title: '请至少填写答案或上传答案图片', icon: 'none' }); return }
  if (!planStore.currentPlan) { uni.showToast({ title: '请先创建学习计划', icon: 'none' }); return }
  uni.showLoading({ title: '保存中...' })
  try {
    await api.createMistake({ plan_id: planStore.currentPlan.id, question: mistakeForm.value.question, answer: mistakeForm.value.answer, analysis: mistakeForm.value.analysis, subject: mistakeForm.value.subject, difficulty: mistakeForm.value.difficulty, question_images: mistakeForm.value.questionImages, answer_images: mistakeForm.value.answerImages, tags: mistakeForm.value.tags })
    showMistakeForm.value = false; mistakeForm.value = { subject: '数据结构', question: '', answer: '', analysis: '', difficulty: 'medium', tags: [], questionImages: [], answerImages: [] }
    uni.showToast({ title: '添加成功', icon: 'success' }); await loadMistakes()
  } catch (e) { uni.showToast({ title: e.message || '保存失败', icon: 'none' }) } finally { uni.hideLoading() }
}
function openEditMistake(m) { editingMistakeId.value = m.id; editMistakeForm.value = { subject: m.subject, question: m.question, answer: m.answer, analysis: m.analysis || '', difficulty: m.difficulty, tags: [...(m.tags || [])], questionImages: [...(m.question_images || [])], answerImages: [...(m.answer_images || [])] }; editMistakeTagInput.value = ''; showEditMistake.value = true }
async function saveEditMistake() {
  const hasQ = editMistakeForm.value.question.trim() || editMistakeForm.value.questionImages.length > 0
  const hasA = editMistakeForm.value.answer.trim() || editMistakeForm.value.answerImages.length > 0
  if (!hasQ || !hasA) { uni.showToast({ title: '请至少保证题目和答案有一方非空', icon: 'none' }); return }
  uni.showLoading({ title: '保存中...' })
  try { await api.updateMistake(editingMistakeId.value, { question: editMistakeForm.value.question, answer: editMistakeForm.value.answer, analysis: editMistakeForm.value.analysis, subject: editMistakeForm.value.subject, difficulty: editMistakeForm.value.difficulty, tags: editMistakeForm.value.tags, question_images: editMistakeForm.value.questionImages, answer_images: editMistakeForm.value.answerImages }); showEditMistake.value = false; uni.showToast({ title: '编辑成功', icon: 'success' }); await loadMistakes() }
  catch (e) { uni.showToast({ title: e.message || '保存失败', icon: 'none' }) } finally { uni.hideLoading() }
}
async function toggleMastered(m) { try { if (m.mastered === '1') await api.updateMistake(m.id, { mastered: '0' }); else await api.markMistakeMastered(m.id); await loadMistakes() } catch (e) { uni.showToast({ title: '操作失败', icon: 'none' }) } }
async function removeMistake(m) { const r = await new Promise(r => uni.showModal({ title: '删除确认', content: '确定删除吗？', success: r })); if (r.confirm) { try { await api.deleteMistake(m.id); mistakes.value = mistakes.value.filter(x => x.id !== m.id); uni.showToast({ title: '已删除', icon: 'success' }) } catch (e) { uni.showToast({ title: '删除失败', icon: 'none' }) } } }
function startMistakeReview() { mistakeReviewMode.value = true; mistakeShowAnswer.value = false; mistakeReviewIndex.value = 0; reviewCorrect.value = 0; reviewTotal.value = mistakeReviewCards.value.length; mistakeReviewComplete.value = false }
async function reviewMistakeResult(correct) {
  if (correct) reviewCorrect.value++
  const m = mistakeReviewCards.value[mistakeReviewIndex.value]
  const updated = await api.reviewMistake(m.id, correct)
  // Immediately sync next_review_date + mastered to the in-memory mistake
  if (updated) {
    m.correct_count = updated.correct_count
    m.error_count = updated.error_count
    m.mastered = updated.mastered
    m.next_review_date = updated.next_review_date
  }
  if (mistakeReviewIndex.value < mistakeReviewCards.value.length - 1) { mistakeReviewIndex.value++; mistakeShowAnswer.value = false }
  else { mistakeReviewMode.value = false; mistakeReviewComplete.value = true; await loadMistakes() }
}
function exitMistakeReview() { mistakeReviewMode.value = false; mistakeReviewComplete.value = false; mistakeReviewIndex.value = 0; mistakeViewMode.value = 'all'; activeSubject.value = ''; activeTags.value = []; activeErrorCount.value = ''; loadMistakes() }
async function loadMistakes() { if (!planStore.currentPlan) return; try { const p = mistakeViewMode.value === 'pending'; const r = await api.getMistakes(planStore.currentPlan.id, activeSubject.value || null, null, p); mistakes.value = r.mistakes || [] } catch (e) { console.error('loadMistakes:', e) } }

// ── Export ──
async function sanitizeImages(items) {
  // Convert any non-base64 image URLs to base64 data URLs so they render in exports
  for (const item of items) {
    for (const key of ['question_images', 'answer_images']) {
      if (!item[key] || !item[key].length) continue
      const converted = []
      for (const src of item[key]) {
        if (typeof src === 'string' && !src.startsWith('data:')) {
          converted.push(await imgSrcToBase64(src))
        } else {
          converted.push(src)
        }
      }
      item[key] = converted
    }
  }
  return items
}

async function doExport(format) {
  showExportModal.value = false
  if (!planStore.currentPlan) { uni.showToast({ title: '请先创建学习计划', icon: 'none' }); return }
  uni.showLoading({ title: '加载数据...' })
  try {
    const opts = { includeAnswer: exportIncludeAnswer.value }
    if (currentView.value === 'cards') {
      const r = await api.getCards(planStore.currentPlan.id, activeSubject.value || null, null, false)
      let d = r.cards || []
      if (activeTags.value.length > 0) {
        d = tagLogic.value === 'and'
          ? d.filter(c => activeTags.value.every(t => (c.tags || []).includes(t)))
          : d.filter(c => activeTags.value.some(t => (c.tags || []).includes(t)))
      }
      if (activeMastery.value) d = d.filter(c => c.mastery_level === activeMastery.value)
      if (!d.length) { uni.showToast({ title: '没有可导出的数据', icon: 'none' }); return }
      d = await sanitizeImages(d)
      if (format === 'csv') exportCardsCSV(d, opts); else if (format === 'excel') exportCardsExcel(d, opts); else if (format === 'pdf') exportCardsPDF(d, opts)
    } else {
      const r = await api.getMistakes(planStore.currentPlan.id, activeSubject.value || null, null, false)
      let d = r.mistakes || []
      if (activeTags.value.length > 0) {
        d = tagLogic.value === 'and'
          ? d.filter(m => activeTags.value.every(t => (m.tags || []).includes(t)))
          : d.filter(m => activeTags.value.some(t => (m.tags || []).includes(t)))
      }
      if (activeErrorCount.value === '1') d = d.filter(m => m.error_count === 1)
      else if (activeErrorCount.value === '2') d = d.filter(m => m.error_count === 2)
      else if (activeErrorCount.value === '3+') d = d.filter(m => m.error_count >= 3)
      if (!d.length) { uni.showToast({ title: '没有可导出的数据', icon: 'none' }); return }
      d = await sanitizeImages(d)
      if (format === 'csv') exportMistakesCSV(d, opts); else if (format === 'excel') exportMistakesExcel(d, opts); else if (format === 'pdf') exportMistakesPDF(d, opts)
    }
  } catch (e) { console.error('Export error:', e); uni.showToast({ title: e.message || '导出失败', icon: 'none' }) } finally { uni.hideLoading() }
}

onMounted(async () => {
  await userStore.getUserInfo()
  if (userStore.isLoggedIn) { await planStore.getPlansByUserId(); await loadSubjects(); await loadCards(); await loadMistakes() }
  document.addEventListener('paste', handleGlobalPaste)
})
onUnmounted(() => {
  document.removeEventListener('paste', handleGlobalPaste)
})
watch(() => planStore.currentPlan?.id, async (n, o) => { if (n && n !== o) { await loadCards(); await loadMistakes() } })
</script>

<style lang="scss" scoped>
/* ===== Header ===== */
.header { padding: 60px 0 20px; border-radius: 0 0 32px 32px; margin: 0 -20px 16px; padding-left: 20px; padding-right: 20px; }
.header-purple { background: linear-gradient(135deg, var(--color-header-purple-start, #6b4ce6) 0%, var(--color-header-purple-end, #8b6ef5) 100%); }
.header-red { background: linear-gradient(135deg, var(--color-header-red-start, #ef5350) 0%, var(--color-header-red-end, #f27573) 100%); }
.header-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.header-left { .title { display: block; font-size: 26px; font-weight: 700; color: #fff; margin-bottom: 4px; } .subtitle { font-size: 14px; color: rgba(255,255,255,0.8); } }
.header-right { position: relative; }
.export-btn { display: flex; align-items: center; gap: 4px; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 20px; border: 1px solid rgba(255,255,255,0.3); &:active { background: rgba(255,255,255,0.35); } .export-icon { font-size: 14px; } .export-text { font-size: 13px; color: #fff; font-weight: 500; } }
.stats-row { display: flex; background: rgba(255,255,255,0.12); border-radius: 16px; padding: 16px; border: 1px solid rgba(255,255,255,0.15); }
.stat-item { flex: 1; text-align: center; .stat-num { display: block; font-size: 22px; font-weight: 700; color: #fff; } .stat-label { font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 2px; } }

/* ===== Sub Nav ===== */
.sub-nav { display: flex; margin-bottom: 14px; background: #f5f7f5; border-radius: 12px; padding: 4px; }
.sub-nav-item { flex: 1; text-align: center; padding: 10px; border-radius: 10px; font-size: 14px; color: #65746d; transition: all 0.2s; &.active { background: #fff; color: #6b4ce6; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.08); } }

/* ===== Mode Toggle ===== */
.mode-toggle { display: flex; margin-bottom: 14px; background: #f5f7f5; border-radius: 12px; padding: 4px; }
.mode-btn { flex: 1; text-align: center; padding: 10px; border-radius: 10px; font-size: 14px; color: #65746d; transition: all 0.2s; &.active { background: #fff; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.08); } }
.mode-toggle .mode-btn.active { color: #6b4ce6; }

/* ===== Filters ===== */
.filter-section { margin-bottom: 10px; }
.filter-row { display: flex; align-items: center; gap: 6px; }
.filter-scroll { white-space: nowrap; width: 100%; flex: 1; min-width: 0; }
.filter-list { display: inline-flex; gap: 8px; padding: 2px 0; }
.filter-item { display: inline-block; padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; white-space: nowrap; transition: all 0.2s; &.active { background: #6b4ce6; color: #fff; } }
.tag-item { &.active { background: #8b6ef5; } }
.mastery-item { &.active { background: #6b4ce6; color: #fff; } &.unmastered.active { background: #ef5350; } &.familiar.active { background: #ffb74d; } &.mastered.active { background: #66bb6a; } }
.err-item { &.active { background: #ef5350; color: #fff; } &.err-1.active { background: #ffb74d; } &.err-2.active { background: #ef5350; } &.err-3.active { background: #c62828; } }
.filter-manage-btn { width: 32px; height: 32px; border-radius: 50%; background: #f5f7f5; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; border: 1px solid #e0e0e0; &:active { background: #e8e0ff; } }
.tag-logic-btn {
  width: 36px; height: 36px; border-radius: 50%; background: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 13px; color: #6b4ce6; font-weight: 700; flex-shrink: 0; border: 1.5px solid #6b4ce6;
  &:active { background: #f3f0ff; }
}

/* ===== Section ===== */
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; .section-title { font-size: 18px; font-weight: 600; color: #1a1a2e; } .section-count { font-size: 13px; color: #999; } }
.start-review-btn { color: #fff; padding: 8px 20px; border-radius: 20px; font-size: 14px; font-weight: 500; &:active { transform: scale(0.96); } &.purple { background: #6b4ce6; } &.red { background: #ef5350; } }
.load-more { text-align: center; padding: 12px; margin-top: 8px; color: #6b4ce6; font-size: 13px; font-weight: 500; cursor: pointer; &:active { color: #4a35a0; } }
.empty { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; .empty-icon { font-size: 48px; margin-bottom: 12px; } .empty-text { font-size: 16px; color: #65746d; margin-bottom: 8px; } .empty-hint { font-size: 13px; color: #999; text-align: center; } }

/* ===== Card Item ===== */
.card-item { background: #fff; border-radius: 16px; padding: 18px; margin-bottom: 12px; border: 1px solid #e8ece9; box-shadow: 0 1px 4px rgba(0,0,0,0.03); &.not-today { opacity: 0.6; } }
.card-item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; .card-item-subject { font-size: 12px; padding: 4px 12px; background: #f3f0ff; border-radius: 20px; color: #6b4ce6; } }
.card-item-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.card-tag { font-size: 11px; padding: 3px 8px; border-radius: 8px; background: #f5f5f5; color: #65746d; }
.mastery-badge { font-size: 11px; padding: 3px 10px; border-radius: 12px; font-weight: 500; &.badge-red { background: #ffebee; color: #c62828; } &.badge-orange { background: #fff3e0; color: #e65100; } &.badge-green { background: #e8f5e9; color: #2e7d32; } }
.section-label { display: block; font-size: 12px; color: #6b4ce6; margin-bottom: 6px; font-weight: 500; }
.card-question-text { font-size: 15px; color: #1a1a2e; line-height: 1.6; display: block; }
.card-item-footer { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-top: 12px; .review-count { font-size: 12px; color: #999; } .review-date { font-size: 12px; color: #6b4ce6; } .card-item-actions { display: flex; gap: 8px; margin-left: auto; } }
.action-btn { padding: 6px 14px; border-radius: 8px; font-size: 13px; background: #f5f5f5; color: #999; }
.edit-btn { background: #f3f0ff; color: #6b4ce6; &:active { background: #e8e0ff; } }
.del-btn { &:active { background: #ffebee; color: #c62828; } }
.master-btn { background: #e8f5e9; color: #2e7d32; }

/* ===== Mistake Card ===== */
.mistake-card { background: #fff; border-radius: 16px; padding: 18px; margin-bottom: 12px; border: 1px solid #e8ece9; box-shadow: 0 1px 4px rgba(0,0,0,0.03); &.mastered { opacity: 0.6; } }
.mistake-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; .mistake-subject { font-size: 12px; padding: 4px 12px; background: #ffebee; border-radius: 20px; color: #ef5350; } }
.mistake-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.mistake-tag { font-size: 11px; padding: 3px 8px; border-radius: 8px; background: #f5f5f5; color: #65746d; &.easy { background: #e8f5e9; color: #2e7d32; } &.medium { background: #fff3e0; color: #e65100; } &.hard { background: #ffebee; color: #c62828; } &.mastered-tag { background: #e8f5e9; color: #2e7d32; } }
.mistake-question { font-size: 15px; color: #1a1a2e; line-height: 1.6; display: block; margin-bottom: 12px; }
.mistake-answer-section, .mistake-analysis-section { margin-bottom: 12px; }
.mistake-answer { font-size: 14px; color: #2e7d32; line-height: 1.6; display: block; font-weight: 500; }
.mistake-analysis { font-size: 14px; color: #65746d; line-height: 1.6; display: block; }
.mistake-footer { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; .mistake-date { font-size: 12px; color: #999; } .correct-progress { font-size: 12px; color: #2e7d32; font-weight: 500; } .error-count { font-size: 12px; color: #ef5350; } .mistake-actions { display: flex; gap: 6px; margin-left: auto; } }

/* ===== Review Card ===== */
.review-card { background: #fff; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); margin-bottom: 20px; }
.review-counter { display: block; font-size: 14px; font-weight: 600; margin-bottom: 16px; }
.header-purple .review-counter { color: #6b4ce6; }
.header-red .review-counter { color: #ef5350; }
.review-card-body { min-height: 160px; }
.review-subject { font-size: 13px; color: #6b4ce6; background: #f3f0ff; padding: 4px 12px; border-radius: 12px; display: inline-block; margin-bottom: 16px; }
.review-question { display: flex; gap: 12px; margin-bottom: 16px; }
.question-label { font-size: 32px; font-weight: 800; line-height: 1; flex-shrink: 0; color: #6b4ce6; &.red { color: #ef5350; } }
.question-text { font-size: 18px; color: #1a1a2e; line-height: 1.6; font-weight: 500; }
.image-gallery { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
.review-image { width: 120px; border-radius: 8px; border: 1px solid #e8ece9; }
.answer-divider { height: 1px; background: #e8ece9; margin: 16px 0; }
.answer-content { display: flex; gap: 12px; margin-bottom: 12px; }
.answer-label { font-size: 32px; font-weight: 800; color: #2e7d32; line-height: 1; flex-shrink: 0; }
.answer-text { font-size: 16px; color: #1a1a2e; line-height: 1.7; }
.analysis-content { margin-top: 12px; }
.analysis-label { display: block; font-size: 12px; color: #ef5350; margin-bottom: 4px; font-weight: 500; }
.analysis-text { font-size: 14px; color: #65746d; line-height: 1.6; }
.review-actions { margin-top: 20px; }
.show-answer-btn { text-align: center; padding: 16px; background: #f3f0ff; border-radius: 14px; &:active { transform: scale(0.98); background: #e8e0ff; } text { font-size: 16px; color: #6b4ce6; font-weight: 600; } &.red-bg { background: #ffebee; text { color: #ef5350; } &:active { background: #ffcdd2; } } }
.review-result-btns { display: flex; gap: 12px; }
.result-btn { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 8px; border-radius: 14px; &:active { transform: scale(0.96); } &.fail { background: #fff0f0; .result-text { color: #c62828; } } &.ok { background: #fff8f0; .result-text { color: #e65100; } } &.great { background: #f0fff4; .result-text { color: #2e7d32; } } &.wrong { background: #fff0f0; .result-text { color: #c62828; } } &.correct { background: #f0fff4; .result-text { color: #2e7d32; } } .result-icon { font-size: 24px; } .result-text { font-size: 13px; font-weight: 500; } }
.review-complete { display: flex; flex-direction: column; align-items: center; padding: 60px 20px; .complete-icon { font-size: 56px; margin-bottom: 12px; } .complete-text { font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 8px; } .complete-hint { font-size: 14px; color: #65746d; margin-bottom: 20px; } .back-btn { padding: 12px 28px; border-radius: 25px; font-size: 15px; font-weight: 500; color: #fff; } }
.header-purple .back-btn { background: #6b4ce6; }
.header-red .back-btn { background: #ef5350; }

/* ===== FAB ===== */
.fab { position: fixed; right: 20px; bottom: 60px; z-index: 50; width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(0,0,0,0.35); &:active { transform: scale(0.92); } &.purple { background: #6b4ce6; } &.red { background: #ef5350; } .fab-icon { font-size: 28px; color: #fff; font-weight: 300; } }

/* ===== Modal ===== */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 24px; }
.modal-content { background: #fff; border-radius: 20px; width: 100%; max-width: 440px; max-height: 75vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #f0f0f0; }
.modal-title { font-size: 17px; font-weight: 700; color: #1a1a2e; }
.modal-close { font-size: 18px; color: #999; padding: 4px; }
.modal-body { padding: 16px 20px; flex: 1; overflow-y: auto; }
.modal-footer { display: flex; gap: 12px; padding: 16px 20px; border-top: 1px solid #f0f0f0; }
.cancel-btn { flex: 1; padding: 13px; text-align: center; border-radius: 12px; font-size: 15px; color: #65746d; background: #f5f7f5; font-weight: 500; }
.submit-btn { flex: 2; padding: 13px; text-align: center; border-radius: 12px; font-size: 15px; color: #fff; background: #6b4ce6; font-weight: 700; }
.red-btn { background: #ef5350; }

.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 14px; font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.subject-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.subject-item { padding: 8px 16px; border-radius: 20px; font-size: 13px; color: #65746d; background: #f5f7f5; &.active { background: #6b4ce6; color: #fff; } &.subject-add { background: #fff; border: 1.5px dashed #d0d5d2; color: #6b4ce6; } }
.tag-preview { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.tag-chip { padding: 4px 10px; border-radius: 12px; font-size: 12px; background: #f3f0ff; color: #6b4ce6; display: flex; align-items: center; gap: 4px; }
.red-chip { background: #ffebee; color: #ef5350; }
.tag-remove { font-size: 14px; color: #6b4ce6; }
.red-remove { color: #ef5350; }
.input-wrapper { border: 1.5px solid #e8ece9; border-radius: 14px; padding: 12px 16px; background: #fafafa; &:focus-within { border-color: #6b4ce6; } }
.input-field { width: 100%; font-size: 15px; color: #1a1a2e; border: none; outline: none; background: transparent; }
.textarea-field { width: 100%; min-height: 80px; font-size: 15px; color: #1a1a2e; line-height: 1.6; border: none; outline: none; background: transparent; resize: none; }
.difficulty-row { display: flex; gap: 10px; }
.diff-item { flex: 1; padding: 10px; text-align: center; border-radius: 12px; font-size: 14px; color: #65746d; background: #f5f7f5; transition: all 0.2s; &.active { background: #ef5350; color: #fff; } }

/* ===== Image Upload ===== */
.image-upload-area { display: flex; gap: 10px; flex-wrap: wrap; }
.image-item { position: relative; width: 80px; height: 80px; }
.uploaded-image { width: 80px; height: 80px; border-radius: 10px; object-fit: cover; }
.image-remove { position: absolute; top: -6px; right: -6px; width: 22px; height: 22px; border-radius: 50%; background: #ef5350; color: #fff; font-size: 12px; display: flex; align-items: center; justify-content: center; }
.upload-actions { display: flex; gap: 8px; }
.upload-action-btn {
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  width: 80px; height: 80px; border-radius: 10px; border: 2px dashed #d0d5d2; background: #fafafa;
  transition: all 0.15s;
  &:active { background: #f3f0ff; border-color: #6b4ce6; }
  .action-icon { font-size: 22px; }
  .action-text { font-size: 11px; color: #999; }
}
.paste-btn {
  &.active { border-color: #6b4ce6; background: #f3f0ff; .action-text { color: #6b4ce6; } }
}
.paste-hint { font-size: 11px; color: #999; margin-top: 6px; display: block; }

/* ===== Tag Picker Chips ===== */
.tag-picker { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 0; }
.tag-picker-chip {
  padding: 5px 12px; border-radius: 14px; font-size: 12px;
  background: #f5f5f5; color: #65746d; border: 1.5px solid transparent;
  transition: all 0.15s;
  &.picked { background: #f3f0ff; color: #6b4ce6; border-color: #6b4ce6; }
}

/* ===== Image in list cards ===== */
.card-images { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0; }
.card-img-item { width: 60px; height: 60px; border-radius: 6px; border: 1px solid #e0e0e0; object-fit: cover; }

/* ===== Export Modal ===== */
.export-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 250; display: flex; align-items: center; justify-content: center; padding: 30px; }
.export-dialog { background: #fff; border-radius: 20px; width: 100%; max-width: 360px; box-shadow: 0 16px 48px rgba(0,0,0,0.15); overflow: hidden; }
.export-dialog-top { display: flex; justify-content: space-between; align-items: center; padding: 20px 20px 14px; }
.export-dialog-title { font-size: 17px; font-weight: 700; color: #1a1a2e; }
.export-dialog-close { width: 28px; height: 28px; border-radius: 50%; background: #f5f5f5; display: flex; align-items: center; justify-content: center; font-size: 14px; color: #999; &:active { background: #e0e0e0; } }
.export-dialog-body { padding: 0 20px 20px; }
.export-option { display: flex; align-items: center; gap: 12px; padding: 12px 14px; margin-bottom: 8px; background: #f5f7f5; border-radius: 12px; border: 1.5px solid transparent; &:active { border-color: #6b4ce6; background: #f3f0ff; } }
.export-opt-icon { font-size: 28px; flex-shrink: 0; }
.export-opt-right { flex: 1; }
.export-opt-label { font-size: 15px; font-weight: 600; color: #1a1a2e; display: block; }
.export-opt-desc { font-size: 12px; color: #999; margin-top: 2px; display: block; }
.export-answer-toggle { display: flex; align-items: center; justify-content: space-between; padding: 16px 4px 0; margin-top: 6px; border-top: 1px solid #e0e0e0; }
.export-toggle-label { font-size: 14px; color: #65746d; font-weight: 500; }
.export-switch { width: 48px; height: 28px; border-radius: 14px; background: #d0d5d2; padding: 2px; display: flex; align-items: center; transition: background 0.25s; flex-shrink: 0; &.on { background: #6b4ce6; justify-content: flex-end; } }
.export-switch-dot { width: 24px; height: 24px; border-radius: 50%; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.2); transition: none; }

/* ===== Manage ===== */
.manage-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; border-radius: 10px; margin-bottom: 6px; background: #f5f7f5; }
.manage-left { display: flex; align-items: center; gap: 8px; }
.manage-name { font-size: 14px; color: #1a1a2e; font-weight: 500; }
.manage-badge { font-size: 10px; padding: 2px 8px; border-radius: 10px; background: #e8e0ff; color: #6b4ce6; }
.custom-badge { background: #fff3e0; color: #e65100; }
.manage-del-btn { font-size: 12px; padding: 5px 12px; border-radius: 8px; background: #ffebee; color: #c62828; font-weight: 500; &:active { background: #ffcdd2; } }
.manage-add-row { display: flex; gap: 8px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #e0e0e0; }
.manage-add-input { flex: 1; padding: 10px 12px; border: 1.5px solid #e0e0e0; border-radius: 10px; font-size: 14px; color: #1a1a2e; background: #f5f7f5; height: 44px; line-height: 24px; &:focus { border-color: #6b4ce6; } }
.manage-add-btn { padding: 10px 20px; border-radius: 10px; background: #6b4ce6; color: #fff; font-size: 14px; font-weight: 600; white-space: nowrap; &:active { opacity: 0.85; } }

.bottom-space { height: 100px; }
</style>
