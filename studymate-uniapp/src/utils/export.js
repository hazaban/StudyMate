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
function imgCell(images) {
  if (!images || images.length === 0) return ''
  return images.map(img => {
    if (img.startsWith('data:')) return `<img src="${esc(img)}" style="max-width:120px;max-height:80px;margin:2px;border:1px solid #ddd;border-radius:4px;" />`
    if (img.startsWith('http') || img.startsWith('blob:')) return `<img src="${esc(img)}" style="max-width:120px;max-height:80px;margin:2px;border:1px solid #ddd;border-radius:4px;" />`
    if (img.startsWith('/')) return `<img src="${esc(img)}" style="max-width:120px;max-height:80px;margin:2px;border:1px solid #ddd;border-radius:4px;" />`
    return `[图片:${img}]`
  }).join('')
}
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

// ─── Cards Excel ───
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
  let html = `<table border="1" style="border-collapse:collapse;width:100%"><tr>${headers.map(h => `<th style="background:#6b4ce6;color:#fff;padding:8px">${esc(h)}</th>`).join('')}</tr>`
  for (const c of cards) {
    html += `<tr>`
    html += `<td style="padding:6px">${esc(c.subject)}</td>`
    html += `<td style="padding:6px">${esc((c.tags||[]).join('；'))}</td>`
    if (hasTextQ) html += `<td style="padding:6px">${esc(c.question)}</td>`
    if (hasImgQ) html += `<td style="padding:6px">${imgCell(c.question_images)}</td>`
    if (includeAnswer) {
      if (hasTextA) html += `<td style="padding:6px">${esc(c.answer)}</td>`
      if (hasImgA) html += `<td style="padding:6px">${imgCell(c.answer_images)}</td>`
    }
    html += `<td style="padding:6px">${esc(masteryCN(c.mastery_level))}</td>`
    html += `<td style="padding:6px;text-align:center">${c.review_count}</td>`
    html += `<td style="padding:6px">${formatDate(c.next_review_date)}</td>`
    html += `<td style="padding:6px">${formatDate(c.created_at)}</td>`
    html += `</tr>`
  }
  html += `</table>`
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>知识卡片导出</title><style>body{font-family:'Microsoft YaHei',sans-serif;padding:10px;}</style></head><body>${html}</body></html>`
}

// ─── Mistakes Excel ───
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
  let html = `<table border="1" style="border-collapse:collapse;width:100%"><tr>${headers.map(h => `<th style="background:#ef5350;color:#fff;padding:8px">${esc(h)}</th>`).join('')}</tr>`
  for (const m of mistakes) {
    html += `<tr>`
    html += `<td style="padding:6px">${esc(m.subject)}</td>`
    html += `<td style="padding:6px">${esc((m.tags||[]).join('；'))}</td>`
    if (hasTextQ) html += `<td style="padding:6px">${esc(m.question)}</td>`
    if (hasImgQ) html += `<td style="padding:6px">${imgCell(m.question_images)}</td>`
    if (includeAnswer) {
      if (hasTextA) html += `<td style="padding:6px">${esc(m.answer)}</td>`
      if (hasImgA) html += `<td style="padding:6px">${imgCell(m.answer_images)}</td>`
      if (hasAnalysis) html += `<td style="padding:6px">${esc(m.analysis||'')}</td>`
    }
    html += `<td style="padding:6px">${esc(difficultyCN(m.difficulty))}</td>`
    html += `<td style="padding:6px;text-align:center">${m.error_count}</td>`
    html += `<td style="padding:6px;text-align:center">${m.correct_count}</td>`
    html += `<td style="padding:6px;text-align:center">${m.mastered==='1'?'是':'否'}</td>`
    html += `<td style="padding:6px">${formatDate(m.created_at)}</td>`
    html += `</tr>`
  }
  html += `</table>`
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>错题本导出</title><style>body{font-family:'Microsoft YaHei',sans-serif;padding:10px;}</style></head><body>${html}</body></html>`
}

// ─── PDF HTML ───
function cardsToPDFHTML(cards, includeAnswer) {
  const hasTextQ = cards.some(c => (c.question||'').trim()); const hasImgQ = cards.some(c => (c.question_images||[]).length > 0)
  const hasTextA = cards.some(c => (c.answer||'').trim()); const hasImgA = cards.some(c => (c.answer_images||[]).length > 0)
  const headers = ['科目', '标签']; if (hasTextQ) headers.push('问题'); if (hasImgQ) headers.push('问题图片')
  if (includeAnswer) { if (hasTextA) headers.push('答案'); if (hasImgA) headers.push('答案图片') }
  headers.push('掌握程度', '复习次数', '下次复习', '创建日期')
  const rows = cards.map(c => {
    const r = [c.subject, (c.tags||[]).join('；')]; if (hasTextQ) r.push(c.question); if (hasImgQ) r.push(imgCell(c.question_images))
    if (includeAnswer) { if (hasTextA) r.push(c.answer); if (hasImgA) r.push(imgCell(c.answer_images)) }
    r.push(masteryCN(c.mastery_level), c.review_count, formatDate(c.next_review_date), formatDate(c.created_at)); return r
  })
  return buildPDFHTML('知识卡片导出', headers, rows)
}
function mistakesToPDFHTML(mistakes, includeAnswer) {
  const hasTextQ = mistakes.some(m => (m.question||'').trim()); const hasImgQ = mistakes.some(m => (m.question_images||[]).length > 0)
  const hasTextA = mistakes.some(m => (m.answer||'').trim()); const hasImgA = mistakes.some(m => (m.answer_images||[]).length > 0)
  const hasAnalysis = mistakes.some(m => (m.analysis||'').trim())
  const headers = ['科目', '标签']; if (hasTextQ) headers.push('题目'); if (hasImgQ) headers.push('题目图片')
  if (includeAnswer) { if (hasTextA) headers.push('正确答案'); if (hasImgA) headers.push('答案图片'); if (hasAnalysis) headers.push('错误分析') }
  headers.push('难度', '错误次数', '正确次数', '已掌握', '创建日期')
  const rows = mistakes.map(m => {
    const r = [m.subject, (m.tags||[]).join('；')]; if (hasTextQ) r.push(m.question); if (hasImgQ) r.push(imgCell(m.question_images))
    if (includeAnswer) { if (hasTextA) r.push(m.answer); if (hasImgA) r.push(imgCell(m.answer_images)); if (hasAnalysis) r.push(m.analysis||'') }
    r.push(difficultyCN(m.difficulty), m.error_count, m.correct_count, m.mastered==='1'?'是':'否', formatDate(m.created_at)); return r
  })
  return buildPDFHTML('错题本导出', headers, rows)
}
function buildPDFHTML(title, headers, rows) {
  const h = headers.map(h => `<th style="background:#333;color:#fff;padding:6px 8px;font-size:11px">${esc(h)}</th>`).join('')
  const r = rows.map(row => `<tr>${row.map(cell => `<td style="padding:4px 6px;font-size:10px;vertical-align:top">${String(cell)}</td>`).join('')}</tr>`).join('')
  return `<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>@page{size:A4 landscape;margin:10mm}body{font-family:'Microsoft YaHei',sans-serif;font-size:10px}
table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccc}</style>
<title>${title}</title></head><body><h3>${title}</h3><table>${h}${r}</table></body></html>`
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
export function exportCardsPDF(cards, opts = {}) { openPrint(cardsToPDFHTML(cards, opts.includeAnswer !== false)) }
export function exportMistakesCSV(mistakes, opts = {}) { saveFile(mistakesToCSV(mistakes, opts.includeAnswer !== false), '错题本.csv') }
export function exportMistakesExcel(mistakes, opts = {}) { saveFile(mistakesToExcel(mistakes, opts.includeAnswer !== false), '错题本.xls', 'text/html;charset=utf-8') }
export function exportMistakesPDF(mistakes, opts = {}) { openPrint(mistakesToPDFHTML(mistakes, opts.includeAnswer !== false)) }
export { getDefaultTags, SUBJECT_TAGS }

// ─── Helpers ───
function esc(s) { return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;') }
function escapeCSV(s) { const str = String(s||'').replace(/"/g,'""'); return str.includes(',')||str.includes('\n')||str.includes('"') ? `"${str}"` : str }
function masteryCN(l) { const m={unmastered:'未掌握',familiar:'较熟悉',mastered:'已掌握'}; return m[l]||l }
function difficultyCN(d) { const m={easy:'简单',medium:'中等',hard:'困难'}; return m[d]||d }
