/** Export utility: CSV / Excel / PDF generation for uni-app.
 *  Each export function accepts an opts.includeAnswer flag (default true).
 *  Supports image export in Excel/PDF formats.
 */

const SUBJECT_TAGS = {
  "数据结构": ["二叉树", "遍历", "哈希表", "排序", "BST", "图", "重点", "公式", "易错", "必考"],
  "操作系统": ["进程", "线程", "死锁", "存储", "内存", "重点", "必考", "PV操作", "易错"],
  "计算机网络": ["TCP", "IP", "OSI", "网络", "重点", "必考", "协议", "子网"],
  "计算机组成原理": ["Cache", "流水线", "存储", "必考", "指令", "CPU"],
  "数学": ["公式", "易错", "重点", "必考", "计算"],
  "英语": ["词汇", "语法", "阅读", "重点", "写作"],
  "政治": ["马原", "毛中特", "史纲", "重点", "必考", "时政"],
}

function getDefaultTags(subject) { return SUBJECT_TAGS[subject] || [] }
function formatDate(dateStr) { if (!dateStr) return ''; try { return new Date(dateStr).toLocaleDateString('zh-CN') } catch (e) { return dateStr } }

// ─── Image column builder ───
// Excel: explicit width/height attributes keep cell sizing predictable.
// Each image is wrapped in a <div> and followed by a <br> to force Edge
// to flow them vertically inside the cell instead of side-by-floating.
function imgCell(images) {
  if (!images || images.length === 0) return ''
  return images.map(img => {
    const src = (img && (img.startsWith('data:') || img.startsWith('http') || img.startsWith('blob:') || img.startsWith('/'))) ? img : ''
    if (!src) return '<div style="font-size:11px;color:#999">[图片]</div>'
    return `<div style="margin:2px 0"><a href="${esc(src)}" target="_blank"><img src="${esc(src)}" width="160" height="120" style="border:1px solid #ccc;border-radius:4px;display:block" /></a></div>`
  }).join('')
}
function excelImgCell(images) { return imgCell(images) }
function imgCSV(images) { return (images || []).join(' | ') }

// ─── Cards CSV ───
function cardsToCSV(cards, includeAnswer) {
  // Only include text columns that have ANY content across all cards
  const hasTextQ = cards.some(c => (c.question || '').trim())
  const hasImgQ = cards.some(c => (c.question_images || []).length > 0)
  const hasTextA = cards.some(c => (c.answer || '').trim())
  const hasImgA = cards.some(c => (c.answer_images || []).length > 0)
  const headers = []
  headers.push('科目', '标签')
  if (hasTextQ) headers.push('问题')
  if (hasImgQ) headers.push('问题图片')
  if (includeAnswer) {
    if (hasTextA) headers.push('答案')
    if (hasImgA) headers.push('答案图片')
  }
  headers.push('掌握程度', '复习次数', '下次复习日期', '创建日期')
  const rows = [headers.join(',')]
  for (const c of cards) {
    const row = [escapeCSV(c.subject), escapeCSV((c.tags||[]).join('；'))]
    if (hasTextQ) row.push(escapeCSV(c.question))
    if (hasImgQ) row.push(imgCSV(c.question_images || []))
    if (includeAnswer) {
      if (hasTextA) row.push(escapeCSV(c.answer))
      if (hasImgA) row.push(imgCSV(c.answer_images))
    }
    row.push(masteryCN(c.mastery_level), c.review_count, formatDate(c.next_review_date), formatDate(c.created_at))
    rows.push(row.join(','))
  }
  return '﻿' + rows.join('\n')
}

// ─── Mistakes CSV ───
function mistakesToCSV(mistakes, includeAnswer) {
  const hasTextQ = mistakes.some(m => (m.question || '').trim())
  const hasImgQ = mistakes.some(m => (m.question_images || []).length > 0)
  const hasTextA = mistakes.some(m => (m.answer || '').trim())
  const hasImgA = mistakes.some(m => (m.answer_images || []).length > 0)
  const hasAnalysis = mistakes.some(m => (m.analysis || '').trim())
  const headers = ['科目', '标签']
  if (hasTextQ) headers.push('题目')
  if (hasImgQ) headers.push('题目图片')
  if (includeAnswer) {
    if (hasTextA) headers.push('正确答案')
    if (hasImgA) headers.push('答案图片')
    if (hasAnalysis) headers.push('错误分析')
  }
  headers.push('难度', '错误次数', '正确次数', '已掌握', '创建日期')
  const rows = [headers.join(',')]
  for (const m of mistakes) {
    const row = [escapeCSV(m.subject), escapeCSV((m.tags||[]).join('；'))]
    if (hasTextQ) row.push(escapeCSV(m.question))
    if (hasImgQ) row.push(imgCSV(m.question_images || []))
    if (includeAnswer) {
      if (hasTextA) row.push(escapeCSV(m.answer))
      if (hasImgA) row.push(imgCSV(m.answer_images || []))
      if (hasAnalysis) row.push(escapeCSV(m.analysis||''))
    }
    row.push(difficultyCN(m.difficulty), m.error_count, m.correct_count, m.mastered==='1'?'是':'否', formatDate(m.created_at))
    rows.push(row.join(','))
  }
  return '﻿' + rows.join('\n')
}

// ─── Cards Excel (compact thumbnails, clickable for full-size) ───
function cardsToExcel(cards, includeAnswer) {
  const hasTextQ = cards.some(c => (c.question || '').trim())
  const hasImgQ = cards.some(c => (c.question_images || []).length > 0)
  const hasTextA = cards.some(c => (c.answer || '').trim())
  const hasImgA = cards.some(c => (c.answer_images || []).length > 0)
  const headers = ['科目', '标签']
  if (hasTextQ) headers.push('问题')
  if (hasImgQ) headers.push('问题图片')
  if (includeAnswer) { if (hasTextA) headers.push('答案'); if (hasImgA) headers.push('答案图片') }
  headers.push('掌握程度', '复习次数', '下次复习', '创建日期')
  let html = `<table border="1" style="border-collapse:collapse;width:100%"><tr>${headers.map(h => `<th style="background:#6b4ce6;color:#fff;padding:8px;text-align:center">${esc(h)}</th>`).join('')}</tr>`
  for (const c of cards) {
    html += `<tr>`
    html += `<td style="padding:6px;white-space:nowrap">${esc(c.subject)}</td>`
    html += `<td style="padding:6px;max-width:120px;word-break:break-all">${esc((c.tags||[]).join('；'))}</td>`
    if (hasTextQ) html += `<td style="padding:6px;max-width:200px;word-break:break-all">${esc(c.question)}</td>`
    if (hasImgQ) html += `<td style="padding:6px;width:175px">${imgCell(c.question_images)}</td>`
    if (includeAnswer) {
      if (hasTextA) html += `<td style="padding:6px;max-width:200px;word-break:break-all">${esc(c.answer)}</td>`
      if (hasImgA) html += `<td style="padding:6px;width:175px">${imgCell(c.answer_images)}</td>`
    }
    html += `<td style="padding:6px;text-align:center;white-space:nowrap">${esc(masteryCN(c.mastery_level))}</td>`
    html += `<td style="padding:6px;text-align:center">${c.review_count}</td>`
    html += `<td style="padding:6px;white-space:nowrap">${formatDate(c.next_review_date)}</td>`
    html += `<td style="padding:6px;white-space:nowrap">${formatDate(c.created_at)}</td>`
    html += `</tr>`
  }
  html += `</table>`
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>知识卡片导出</title><style>body{font-family:'Microsoft YaHei',sans-serif;padding:10px;}a img{border:1px solid #ccc;border-radius:4px}</style></head><body>${html}</body></html>`
}

// ─── Mistakes Excel (compact thumbnails, clickable for full-size) ───
function mistakesToExcel(mistakes, includeAnswer) {
  const hasTextQ = mistakes.some(m => (m.question || '').trim())
  const hasImgQ = mistakes.some(m => (m.question_images || []).length > 0)
  const hasTextA = mistakes.some(m => (m.answer || '').trim())
  const hasImgA = mistakes.some(m => (m.answer_images || []).length > 0)
  const hasAnalysis = mistakes.some(m => (m.analysis || '').trim())
  const headers = ['科目', '标签']
  if (hasTextQ) headers.push('题目')
  if (hasImgQ) headers.push('题目图片')
  if (includeAnswer) {
    if (hasTextA) headers.push('正确答案')
    if (hasImgA) headers.push('答案图片')
    if (hasAnalysis) headers.push('错误分析')
  }
  headers.push('难度', '错误次数', '正确次数', '已掌握', '创建日期')
  let html = `<table border="1" style="border-collapse:collapse;width:100%"><tr>${headers.map(h => `<th style="background:#ef5350;color:#fff;padding:8px;text-align:center">${esc(h)}</th>`).join('')}</tr>`
  for (const m of mistakes) {
    html += `<tr>`
    html += `<td style="padding:6px;white-space:nowrap">${esc(m.subject)}</td>`
    html += `<td style="padding:6px;max-width:120px;word-break:break-all">${esc((m.tags||[]).join('；'))}</td>`
    if (hasTextQ) html += `<td style="padding:6px;max-width:200px;word-break:break-all">${esc(m.question)}</td>`
    if (hasImgQ) html += `<td style="padding:6px;width:175px">${imgCell(m.question_images)}</td>`
    if (includeAnswer) {
      if (hasTextA) html += `<td style="padding:6px;max-width:200px;word-break:break-all">${esc(m.answer)}</td>`
      if (hasImgA) html += `<td style="padding:6px;width:175px">${imgCell(m.answer_images)}</td>`
      if (hasAnalysis) html += `<td style="padding:6px;max-width:200px;word-break:break-all">${esc(m.analysis||'')}</td>`
    }
    html += `<td style="padding:6px;text-align:center;white-space:nowrap">${esc(difficultyCN(m.difficulty))}</td>`
    html += `<td style="padding:6px;text-align:center">${m.error_count}</td>`
    html += `<td style="padding:6px;text-align:center">${m.correct_count}</td>`
    html += `<td style="padding:6px;text-align:center">${m.mastered==='1'?'是':'否'}</td>`
    html += `<td style="padding:6px;white-space:nowrap">${formatDate(m.created_at)}</td>`
    html += `</tr>`
  }
  html += `</table>`
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>错题本导出</title><style>body{font-family:'Microsoft YaHei',sans-serif;padding:10px;}a img{border:1px solid #ccc;border-radius:4px}</style></head><body>${html}</body></html>`
}

// ─── PDF HTML (portrait A4, vertical card layout) ───

function pdfImgCell(images) {
  if (!images || images.length === 0) return ''
  // Stack images vertically, each at a comfortable reading width.
  // max-width: 650px gives ~120mm on print — readable text without over-stretching.
  return images.map(img => {
    const src = (img && (img.startsWith('data:') || img.startsWith('http') || img.startsWith('blob:') || img.startsWith('/'))) ? img : ''
    if (!src) return '<div class="img-wrap">[图片]</div>'
    return `<div class="img-wrap"><img src="${esc(src)}" /></div>`
  }).join('')
}

function buildPDFCardsHTML(cards, includeAnswer) {
  const rows = cards.map((c, i) => {
    let html = `<div class="card"><div class="card-header"><span class="card-num">#${i+1}</span><span class="card-subject">${esc(c.subject)}</span><span class="card-tags">${esc((c.tags||[]).join(' · '))}</span></div>`
    html += `<div class="card-section"><div class="card-label">📍 问题</div>`
    if ((c.question||'').trim()) html += `<div class="card-text">${esc(c.question)}</div>`
    if ((c.question_images||[]).length > 0) html += `<div class="card-images">${pdfImgCell(c.question_images)}</div>`
    html += `</div>`
    if (includeAnswer) {
      html += `<div class="card-section"><div class="card-label answer-label">✅ 答案</div>`
      if ((c.answer||'').trim()) html += `<div class="card-text">${esc(c.answer)}</div>`
      if ((c.answer_images||[]).length > 0) html += `<div class="card-images">${pdfImgCell(c.answer_images)}</div>`
      html += `</div>`
    }
    html += `<div class="card-meta"><span>${masteryCN(c.mastery_level)}</span><span>第${c.review_count}次复习</span><span>下次: ${formatDate(c.next_review_date)}</span><span>创建: ${formatDate(c.created_at)}</span></div></div>`
    return html
  }).join('')
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>知识卡片导出</title>
<style>@page{size:A4;margin:8mm}body{font-family:'Microsoft YaHei',sans-serif;font-size:13px;color:#1a1a2e;background:#fff;line-height:1.7}
h2{text-align:center;font-size:20px;margin:0 0 16px;padding-bottom:8px;border-bottom:2px solid #6b4ce6}
.card{border:1px solid #d9e7dd;border-radius:10px;padding:12px;margin-bottom:12px;page-break-inside:avoid;background:#fafbfa;}
.card-header{display:flex;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.card-num{font-size:12px;color:#999;font-weight:700}
.card-subject{font-size:14px;font-weight:700;color:#6b4ce6;background:#f3f0ff;padding:3px 12px;border-radius:12px}
.card-tags{font-size:12px;color:#65746d}
.card-section{margin-bottom:12px}
.card-label{font-size:13px;font-weight:700;color:#6b4ce6;margin-bottom:4px}
.card-label.answer-label{color:#2e7d32}
.card-text{font-size:14px;color:#1a1a2e;white-space:pre-wrap}
.card-images{margin-top:6px}.img-wrap{margin-bottom:8px;text-align:center}img{display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #ddd;border-radius:6px}
.card-meta{display:flex;gap:12px;flex-wrap:wrap;font-size:11px;color:#999;padding-top:8px;border-top:1px solid #e8ece9}
.card-meta span{background:#f5f5f5;padding:2px 8px;border-radius:6px}
</style><title>知识卡片导出</title></head><body><h2>📚 知识卡片导出 (${cards.length}张)</h2>${rows}</body></html>`
}

function buildPDFMistakesHTML(mistakes, includeAnswer) {
  const rows = mistakes.map((m, i) => {
    let html = `<div class="card"><div class="card-header"><span class="card-num">#${i+1}</span><span class="card-subject mistake-subj">${esc(m.subject)}</span><span class="card-tags">${esc((m.tags||[]).join(' · '))}</span><span class="card-diff ${m.difficulty}">${difficultyCN(m.difficulty)}</span></div>`
    html += `<div class="card-section"><div class="card-label mistake-lbl">📍 题目</div>`
    if ((m.question||'').trim()) html += `<div class="card-text">${esc(m.question)}</div>`
    if ((m.question_images||[]).length > 0) html += `<div class="card-images">${pdfImgCell(m.question_images)}</div>`
    html += `</div>`
    if (includeAnswer) {
      html += `<div class="card-section"><div class="card-label answer-label">✅ 正确答案</div>`
      if ((m.answer||'').trim()) html += `<div class="card-text">${esc(m.answer)}</div>`
      if ((m.answer_images||[]).length > 0) html += `<div class="card-images">${pdfImgCell(m.answer_images)}</div>`
      html += `</div>`
      if ((m.analysis||'').trim()) html += `<div class="card-section"><div class="card-label analysis-label">💡 错误分析</div><div class="card-text">${esc(m.analysis)}</div></div>`
    }
    html += `<div class="card-meta"><span>错误${m.error_count}次</span><span>正确${m.correct_count}次</span><span>${m.mastered==='1'?'已掌握':'待攻克'}</span><span>创建: ${formatDate(m.created_at)}</span></div></div>`
    return html
  }).join('')
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>错题本导出</title>
<style>@page{size:A4;margin:8mm}body{font-family:'Microsoft YaHei',sans-serif;font-size:13px;color:#1a1a2e;background:#fff;line-height:1.7}
h2{text-align:center;font-size:20px;margin:0 0 16px;padding-bottom:8px;border-bottom:2px solid #ef5350}
.card{border:1px solid #ffcdd2;border-radius:10px;padding:12px;margin-bottom:12px;page-break-inside:avoid;background:#fffafa;}
.card-header{display:flex;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.card-num{font-size:12px;color:#999;font-weight:700}
.card-subject{font-size:14px;font-weight:700;background:#f3f0ff;padding:3px 12px;border-radius:12px}
.card-subject.mistake-subj{color:#ef5350;background:#ffebee}
.card-tags{font-size:12px;color:#65746d}
.card-diff{font-size:11px;padding:2px 8px;border-radius:8px;font-weight:600}
.card-diff.easy{background:#e8f5e9;color:#2e7d32}
.card-diff.medium{background:#fff3e0;color:#e65100}
.card-diff.hard{background:#ffebee;color:#c62828}
.card-section{margin-bottom:12px}
.card-label{font-size:13px;font-weight:700;color:#6b4ce6;margin-bottom:4px}
.card-label.mistake-lbl{color:#ef5350}
.card-label.answer-label{color:#2e7d32}
.card-label.analysis-label{color:#65746d}
.card-text{font-size:14px;color:#1a1a2e;white-space:pre-wrap}
.card-images{margin-top:6px}.img-wrap{margin-bottom:8px;text-align:center}img{display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #ddd;border-radius:6px}
.card-meta{display:flex;gap:12px;flex-wrap:wrap;font-size:11px;color:#999;padding-top:8px;border-top:1px solid #e8ece9}
.card-meta span{background:#f5f5f5;padding:2px 8px;border-radius:6px}
</style><title>错题本导出</title></head><body><h2>📝 错题本导出 (${mistakes.length}道)</h2>${rows}</body></html>`
}

// ─── Save ───
function saveFile(content, filename, mime) {
  // #ifdef H5
  const blob = new Blob([content], { type: mime || 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob); const a = document.createElement('a')
  a.href = url; a.download = filename; document.body.appendChild(a); a.click()
  document.body.removeChild(a); URL.revokeObjectURL(url)
  // #endif
  // #ifndef H5
  uni.showToast({ title: '请在电脑端使用导出功能', icon: 'none' })
  // #endif
}
function openPrint(html) {
  // #ifdef H5
  const win = window.open('', '_blank')
  if (win) { win.document.write(html); win.document.close(); setTimeout(() => win.print(), 500) }
  // #endif
  // #ifndef H5
  uni.showToast({ title: '请在电脑端使用导出功能', icon: 'none' })
  // #endif
}

export function exportCardsCSV(cards, opts = {}) { saveFile(cardsToCSV(cards, opts.includeAnswer !== false), '知识卡片.csv') }
export function exportCardsExcel(cards, opts = {}) { saveFile(cardsToExcel(cards, opts.includeAnswer !== false), '知识卡片.xls', 'text/html;charset=utf-8') }
export function exportCardsPDF(cards, opts = {}) { openPrint(buildPDFCardsHTML(cards, opts.includeAnswer !== false)) }
export function exportMistakesCSV(mistakes, opts = {}) { saveFile(mistakesToCSV(mistakes, opts.includeAnswer !== false), '错题本.csv') }
export function exportMistakesExcel(mistakes, opts = {}) { saveFile(mistakesToExcel(mistakes, opts.includeAnswer !== false), '错题本.xls', 'text/html;charset=utf-8') }
export function exportMistakesPDF(mistakes, opts = {}) { openPrint(buildPDFMistakesHTML(mistakes, opts.includeAnswer !== false)) }
export { getDefaultTags, SUBJECT_TAGS }

// ─── Helpers ───
function esc(s) { return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;') }
function escapeCSV(s) { const str = String(s||'').replace(/"/g,'""'); return str.includes(',')||str.includes('\n')||str.includes('"') ? `"${str}"` : str }
function masteryCN(l) { const m={unmastered:'未掌握',familiar:'较熟悉',mastered:'已掌握'}; return m[l]||l }
function difficultyCN(d) { const m={easy:'简单',medium:'中等',hard:'困难'}; return m[d]||d }
