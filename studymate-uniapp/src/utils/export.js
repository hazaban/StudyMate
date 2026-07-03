/** Export utility: CSV / Excel / PDF generation for uni-app.
 *  Each export function accepts an opts.includeAnswer flag (default true).
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

function getDefaultTags(subject) {
  return SUBJECT_TAGS[subject] || []
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  try { return new Date(dateStr).toLocaleDateString('zh-CN') } catch (e) { return dateStr }
}

// ─── Cards CSV ───
function cardsToCSV(cards, includeAnswer) {
  const headers = includeAnswer
    ? ['科目', '标签', '问题', '答案', '掌握程度', '复习次数', '下次复习日期', '创建日期']
    : ['科目', '标签', '问题', '掌握程度', '复习次数', '下次复习日期', '创建日期']
  const rows = [headers.join(',')]
  for (const c of cards) {
    const row = [
      escapeCSV(c.subject),
      escapeCSV((c.tags || []).join('；')),
      escapeCSV(c.question),
    ]
    if (includeAnswer) row.push(escapeCSV(c.answer))
    row.push(masteryCN(c.mastery_level), c.review_count, formatDate(c.next_review_date), formatDate(c.created_at))
    rows.push(row.join(','))
  }
  return rows.join('\n')
}

// ─── Mistakes CSV ───
function mistakesToCSV(mistakes, includeAnswer) {
  const headers = includeAnswer
    ? ['科目', '标签', '题目', '正确答案', '错误分析', '难度', '错误次数', '正确次数', '已掌握', '创建日期']
    : ['科目', '标签', '题目', '难度', '错误次数', '正确次数', '已掌握', '创建日期']
  const rows = [headers.join(',')]
  for (const m of mistakes) {
    const row = [
      escapeCSV(m.subject),
      escapeCSV((m.tags || []).join('；')),
      escapeCSV(m.question),
    ]
    if (includeAnswer) {
      row.push(escapeCSV(m.answer), escapeCSV(m.analysis || ''))
    }
    row.push(difficultyCN(m.difficulty), m.error_count, m.correct_count, m.mastered === '1' ? '是' : '否', formatDate(m.created_at))
    rows.push(row.join(','))
  }
  return rows.join('\n')
}

// ─── Cards Excel ───
function cardsToExcel(cards, includeAnswer) {
  const headers = includeAnswer
    ? ['科目', '标签', '问题', '答案', '掌握程度', '复习次数', '下次复习', '创建日期']
    : ['科目', '标签', '问题', '掌握程度', '复习次数', '下次复习', '创建日期']
  let html = `<table border="1"><tr>${headers.map(h => `<th>${esc(h)}</th>`).join('')}</tr>`
  for (const c of cards) {
    html += `<tr>`
    html += `<td>${esc(c.subject)}</td>`
    html += `<td>${esc((c.tags || []).join('；'))}</td>`
    html += `<td>${esc(c.question)}</td>`
    if (includeAnswer) html += `<td>${esc(c.answer)}</td>`
    html += `<td>${esc(masteryCN(c.mastery_level))}</td>`
    html += `<td>${c.review_count}</td>`
    html += `<td>${formatDate(c.next_review_date)}</td>`
    html += `<td>${formatDate(c.created_at)}</td>`
    html += `</tr>`
  }
  html += `</table>`
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>知识卡片导出</title></head><body>${html}</body></html>`
}

// ─── Mistakes Excel ───
function mistakesToExcel(mistakes, includeAnswer) {
  const headers = includeAnswer
    ? ['科目', '标签', '题目', '正确答案', '错误分析', '难度', '错误次数', '正确次数', '已掌握', '创建日期']
    : ['科目', '标签', '题目', '难度', '错误次数', '正确次数', '已掌握', '创建日期']
  let html = `<table border="1"><tr>${headers.map(h => `<th>${esc(h)}</th>`).join('')}</tr>`
  for (const m of mistakes) {
    html += `<tr>`
    html += `<td>${esc(m.subject)}</td>`
    html += `<td>${esc((m.tags || []).join('；'))}</td>`
    html += `<td>${esc(m.question)}</td>`
    if (includeAnswer) {
      html += `<td>${esc(m.answer)}</td>`
      html += `<td>${esc(m.analysis || '')}</td>`
    }
    html += `<td>${esc(difficultyCN(m.difficulty))}</td>`
    html += `<td>${m.error_count}</td>`
    html += `<td>${m.correct_count}</td>`
    html += `<td>${m.mastered === '1' ? '是' : '否'}</td>`
    html += `<td>${formatDate(m.created_at)}</td>`
    html += `</tr>`
  }
  html += `</table>`
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>错题本导出</title></head><body>${html}</body></html>`
}

// ─── PDF-ready HTML ───
function buildPDFHTML(title, headers, rows) {
  const h = headers.map(h => `<th>${esc(h)}</th>`).join('')
  const r = rows.map(row => `<tr>${row.map(cell => `<td>${esc(String(cell))}</td>`).join('')}</tr>`).join('')
  return `<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>body{font-family:'Microsoft YaHei',sans-serif;padding:20px;}h2{text-align:center;margin-bottom:10px;}
table{border-collapse:collapse;width:100%;font-size:12px;}
th,td{border:1px solid #ccc;padding:6px 8px;text-align:left;}
th{background:#f5f5f5;font-weight:600;}</style>
<title>${title}</title></head><body><h2>${title}</h2><table>${h}${r}</table></body></html>`
}

function cardsToPDFHTML(cards, includeAnswer) {
  const headers = includeAnswer
    ? ['科目', '标签', '问题', '答案', '掌握程度', '复习次数', '下次复习', '创建日期']
    : ['科目', '标签', '问题', '掌握程度', '复习次数', '下次复习', '创建日期']
  const rows = cards.map(c => {
    const row = [c.subject, (c.tags||[]).join('；'), c.question]
    if (includeAnswer) row.push(c.answer)
    row.push(masteryCN(c.mastery_level), c.review_count, formatDate(c.next_review_date), formatDate(c.created_at))
    return row
  })
  return buildPDFHTML('知识卡片导出', headers, rows)
}

function mistakesToPDFHTML(mistakes, includeAnswer) {
  const headers = includeAnswer
    ? ['科目', '标签', '题目', '正确答案', '错误分析', '难度', '错误次数', '正确次数', '已掌握', '创建日期']
    : ['科目', '标签', '题目', '难度', '错误次数', '正确次数', '已掌握', '创建日期']
  const rows = mistakes.map(m => {
    const row = [m.subject, (m.tags||[]).join('；'), m.question]
    if (includeAnswer) row.push(m.answer, m.analysis||'')
    row.push(difficultyCN(m.difficulty), m.error_count, m.correct_count, m.mastered==='1'?'是':'否', formatDate(m.created_at))
    return row
  })
  return buildPDFHTML('错题本导出', headers, rows)
}

// ─── Save file ───
function saveToFile(content, filename) {
  // #ifdef H5
  const blob = new Blob(['﻿' + content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename
  document.body.appendChild(a); a.click()
  document.body.removeChild(a); URL.revokeObjectURL(url)
  // #endif
  // #ifndef H5
  uni.showToast({ title: '请在小程序端使用分享功能', icon: 'none' })
  // #endif
}

function saveHTMLFile(html, filename) {
  // #ifdef H5
  const blob = new Blob(['﻿' + html], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename
  document.body.appendChild(a); a.click()
  document.body.removeChild(a); URL.revokeObjectURL(url)
  // #endif
  // #ifndef H5
  uni.showToast({ title: '请在小程序端使用分享功能', icon: 'none' })
  // #endif
}

function openPrintWindow(html) {
  // #ifdef H5
  const win = window.open('', '_blank')
  if (win) { win.document.write(html); win.document.close(); win.print() }
  // #endif
  // #ifndef H5
  uni.showToast({ title: '请在小程序端使用分享功能', icon: 'none' })
  // #endif
}

// ─── Public API ───
// Each accepts: (data, { includeAnswer: true })

export function exportCardsCSV(cards, opts = {}) {
  saveToFile(cardsToCSV(cards, opts.includeAnswer !== false), '知识卡片.csv')
}
export function exportCardsExcel(cards, opts = {}) {
  saveHTMLFile(cardsToExcel(cards, opts.includeAnswer !== false), '知识卡片.xls')
}
export function exportCardsPDF(cards, opts = {}) {
  openPrintWindow(cardsToPDFHTML(cards, opts.includeAnswer !== false))
}

export function exportMistakesCSV(mistakes, opts = {}) {
  saveToFile(mistakesToCSV(mistakes, opts.includeAnswer !== false), '错题本.csv')
}
export function exportMistakesExcel(mistakes, opts = {}) {
  saveHTMLFile(mistakesToExcel(mistakes, opts.includeAnswer !== false), '错题本.xls')
}
export function exportMistakesPDF(mistakes, opts = {}) {
  openPrintWindow(mistakesToPDFHTML(mistakes, opts.includeAnswer !== false))
}

export { getDefaultTags, SUBJECT_TAGS }

// ─── Helpers ───
function esc(s) { return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;') }
function escapeCSV(s) {
  const str = String(s || '').replace(/"/g, '""')
  return str.includes(',') || str.includes('\n') || str.includes('"') ? `"${str}"` : str
}
function masteryCN(lvl) { const m={unmastered:'未掌握',familiar:'较熟悉',mastered:'已掌握'}; return m[lvl]||lvl }
function difficultyCN(d) { const m={easy:'简单',medium:'中等',hard:'困难'}; return m[d]||d }
