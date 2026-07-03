const DEEPSEEK_API_KEY = process.env.VUE_APP_DEEPSEEK_API_KEY
const DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

async function callDeepSeek(prompt, model = 'deepseek-v4-flash') {
  try {
    const response = await fetch(DEEPSEEK_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEEPSEEK_API_KEY}`
      },
      body: JSON.stringify({
        model,
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.7,
        max_tokens: 2000
      })
    })

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`)
    }

    const data = await response.json()
    return data.choices[0].message.content
  } catch (error) {
    console.error('DeepSeek API error:', error)
    throw error
  }
}

export const ai = {
  async generateStudyPlan(params) {
    const prompt = `
你是一个专业的考研规划师。请根据以下信息为用户生成一份详细的学习计划：

考试信息：
- 考试名称：${params.exam_name || '2026考研'}
- 考试日期：${params.exam_date}
- 目标分数：${JSON.stringify(params.target_scores)}
- 每日学习时间：${params.daily_study_time}分钟
- 薄弱科目：${params.weak_points?.join(', ') || '无'}
- 学习阶段：${params.study_phase || '基础阶段'}

请生成包含以下内容的JSON格式学习计划：
{
  "plan_name": "计划名称",
  "phases": [
    {
      "name": "阶段名称",
      "start_date": "开始日期",
      "end_date": "结束日期",
      "goals": ["目标1", "目标2"],
      "subjects": {
        "科目名": ["任务1", "任务2"]
      }
    }
  ],
  "estimated_total_hours": 总预估学习小时数
}

请确保JSON格式正确，不要包含Markdown格式。
`
    const result = await callDeepSeek(prompt)
    try {
      return JSON.parse(result)
    } catch {
      return { success: false, error: 'AI返回格式错误', raw: result }
    }
  },

  async generateDailyTasks(params) {
    const prompt = `
你是一个专业的学习助手。请根据以下信息为用户生成今日学习任务：

计划信息：
- 考试名称：${params.exam_name}
- 日期：${params.date}
- 科目：${params.subjects?.join(', ') || '全部科目'}
- 剩余天数：${params.days_remaining}天
- 今日可用时间：${params.available_time}分钟

请生成包含以下内容的JSON格式任务列表：
{
  "tasks": [
    {
      "id": "唯一标识",
      "type": "new_study/review/mistake",
      "subject": "科目",
      "content": "任务内容",
      "duration": 预计时长（分钟）,
      "priority": "high/medium/low"
    }
  ]
}

请确保JSON格式正确，不要包含Markdown格式。
`
    const result = await callDeepSeek(prompt)
    try {
      return JSON.parse(result)
    } catch {
      return { success: false, error: 'AI返回格式错误', raw: result }
    }
  },

  async generateFlashCards(content) {
    const prompt = `
你是一个专业的教育专家。请将以下学习内容转换为复习卡片（问题-答案形式）：

学习内容：
${content}

请生成包含以下内容的JSON格式卡片列表：
{
  "cards": [
    {
      "question": "问题",
      "answer": "答案",
      "subject": "所属科目",
      "difficulty": "easy/medium/hard"
    }
  ]
}

每个卡片应该是一个知识点的问答形式，确保问题能够有效检验对知识点的理解。
请确保JSON格式正确，不要包含Markdown格式。
`
    const result = await callDeepSeek(prompt)
    try {
      return JSON.parse(result)
    } catch {
      return { success: false, error: 'AI返回格式错误', raw: result }
    }
  },

  async generateDailyReview(params) {
    const prompt = `
你是一个专业的学习复盘助手。请根据以下信息为用户生成今日学习复盘：

学习信息：
- 日期：${params.date}
- 计划任务数：${params.planned_count}
- 完成任务数：${params.completed_count}
- 学习时长：${params.study_duration}分钟
- 完成的任务：${params.completed_tasks?.join(', ') || '无'}
- 未完成的任务：${params.pending_tasks?.join(', ') || '无'}

请生成包含以下内容的JSON格式复盘：
{
  "summary": "今日学习总结",
  "achievements": ["成就1", "成就2"],
  "suggestions": ["建议1", "建议2"],
  "encouragement": "鼓励语"
}

请确保JSON格式正确，不要包含Markdown格式。
`
    const result = await callDeepSeek(prompt)
    try {
      return JSON.parse(result)
    } catch {
      return { success: false, error: 'AI返回格式错误', raw: result }
    }
  },

  async generateMistakeAnalysis(content) {
    const prompt = `
你是一个专业的错题分析专家。请分析以下错题并生成复习建议：

错题内容：
${content}

请生成包含以下内容的JSON格式分析结果：
{
  "analysis": "错误原因分析",
  "key_points": ["关键知识点1", "关键知识点2"],
  "suggestion": "复习建议",
  "related_topics": ["相关知识点1", "相关知识点2"]
}

请确保JSON格式正确，不要包含Markdown格式。
`
    const result = await callDeepSeek(prompt)
    try {
      return JSON.parse(result)
    } catch {
      return { success: false, error: 'AI返回格式错误', raw: result }
    }
  }
}