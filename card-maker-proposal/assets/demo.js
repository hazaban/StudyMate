(function () {
  'use strict';

  function qsa(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  /* ---------- 1. 卡片类型选择 ---------- */
  qsa('[data-type-selector]').forEach(function (group) {
    var next = group.parentNode.querySelector('[data-type-next]');
    var labels = {
      basic: '下一步：填写问答',
      cloze: '下一步：编辑挖空',
      occlusion: '下一步：框选遮挡'
    };

    qsa('.type-card', group).forEach(function (card) {
      card.addEventListener('click', function () {
        qsa('.type-card', group).forEach(function (item) {
          item.classList.remove('is-active');
        });
        card.classList.add('is-active');
        if (next) {
          next.textContent = labels[card.getAttribute('data-type')] || '下一步';
        }
      });
    });
  });

  /* ---------- 2. 挖空编辑器：标记 / 取消标记 ---------- */
  var clozeEditor = document.getElementById('clozeEditor');
  var markButton = document.querySelector('[data-mark-cloze]');

  if (clozeEditor && markButton) {
    var preview = clozeEditor.parentNode.querySelector('.preview-box');

    clozeEditor.classList.add('editor-on');
    markButton.textContent = '取消标记';

    markButton.addEventListener('click', function () {
      var marked = clozeEditor.classList.toggle('editor-on');
      markButton.textContent = marked ? '取消标记' : '标记挖空';

      if (preview) {
        qsa('.blank', preview).forEach(function (blank) {
          blank.classList.toggle('is-open', !marked);
        });
      }
    });
  }

  /* ---------- 3. 单个空：点击揭示 ---------- */
  document.addEventListener('click', function (event) {
    var target = event.target;
    if (!target || !target.closest) return;

    var blank = target.closest('.blank');
    if (blank) {
      blank.classList.toggle('is-open');
    }
  });

  /* ---------- 4. 复习挖空卡：显示答案 ---------- */
  qsa('[data-reveal-cloze]').forEach(function (button) {
    button.addEventListener('click', function () {
      var scope = button.closest('.p-block') || document;
      qsa('.blank', scope).forEach(function (blank) {
        blank.classList.add('is-open');
      });
      button.textContent = '已全部揭示';
    });
  });

  /* ---------- 5. 遮挡编辑器：框选模式 ---------- */
  var occlusionEditor = document.getElementById('occlusionEditor');
  var drawButton = document.querySelector('[data-draw-mask]');

  if (occlusionEditor && drawButton) {
    occlusionEditor.setAttribute('data-drawing', 'true');
    drawButton.textContent = '完成框选';

    drawButton.addEventListener('click', function () {
      var drawing = occlusionEditor.getAttribute('data-drawing') !== 'true';
      occlusionEditor.setAttribute('data-drawing', drawing ? 'true' : 'false');
      drawButton.textContent = drawing ? '完成框选' : '框选遮罩';
    });
  }

  /* ---------- 6. 遮罩列表：单块显示 / 隐藏 ---------- */
  qsa('[data-mask-chip]').forEach(function (chip) {
    chip.addEventListener('click', function () {
      var active = chip.classList.toggle('is-on');
      if (!occlusionEditor) return;

      var mask = occlusionEditor.querySelector('.mask[data-mask="' + chip.getAttribute('data-mask-chip') + '"]');
      if (mask) {
        mask.classList.toggle('is-hidden', !active);
      }
    });
  });

  /* ---------- 7. 复习遮挡卡：逐块揭示 ---------- */
  var occlusionReview = document.getElementById('occlusionReview');
  if (occlusionReview) {
    qsa('.mask', occlusionReview).forEach(function (mask) {
      mask.addEventListener('click', function () {
        mask.classList.toggle('is-open');
      });
    });
  }

  /* ---------- 8. 复习遮挡卡：全部揭示 ---------- */
  qsa('[data-reveal-mask]').forEach(function (button) {
    button.addEventListener('click', function () {
      var scope = button.closest('.p-block') || document;
      qsa('.mask', scope).forEach(function (mask) {
        mask.classList.add('is-open');
      });
      button.textContent = '已全部揭示';
    });
  });
})();
