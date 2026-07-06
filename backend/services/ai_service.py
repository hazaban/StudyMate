"""智谱 GLM AI 服务 — 计划生成、卡片生成、每日复盘 + 教材目录图片识别。

纯文本：glm-4.5-air（便宜、快速、性价比高）
视觉/视频/GUI：glm-4.1v-thinking-flashx（便宜、极速）
未配置 Key 或额度用尽时永久降级为 mock 假数据（进程重启前不会恢复）。
"""

import json
import os
import logging
import httpx
from config import (
    AI_PROVIDER,
    GLM_API_KEY, GLM_BASE_URL, GLM_TEXT_MODEL, GLM_VISION_MODEL
)

_log = logging.getLogger(__name__)

# ===== 全局降级标记 =====
# 一旦检测到欠费/额度用尽/Key无效，永久切断 AI 调用，避免产生费用。
# 恢复方式：设置环境变量 GLM_FORCE_ENABLE=true 后重新部署/重启进程。
_GLM_DISABLED = False
_GLM_DISABLE_REASON = ""

SYSTEM_PROMPT = """你是 StudyMate 学习星球的 AI 备考助手。你是一个专业、耐心、有洞察力的学习导师。
你的任务是根据用户的学习目标和当前状态，提供科学、个性化的学习建议。

输出格式要求：严格返回 JSON，不要包含 markdown 代码块标记，不要有额外解释。
"""

# 智谱欠费 / 额度用尽时的典型错误码和消息
_QUOTA_EXHAUSTED_CODES = {402, 429, 403}
_QUOTA_EXHAUSTED_KEYWORDS = [
    "insufficient", "quota", "balance", "arrears", "exceeded",
    "额度", "欠费", "余额不足", "已用完", "已用尽", "超额",
    "billing", "charge", "disabled",
]


async def _call_glm(messages: list[dict], model: str = None, temperature: float = 0.7) -> str:
    """调用智谱 GLM（OpenAI 兼容协议）。

    如果全局降级标记已设置、AI_PROVIDER 为 mock、或未配置 Key，
    直接返回 mock 数据，绝不发起 HTTP 请求。
    """
    global _GLM_DISABLED, _GLM_DISABLE_REASON

    # 可通过 GLM_FORCE_ENABLE=true 强制恢复（需重启进程/重新部署）
    if _GLM_DISABLED and os.environ.get("GLM_FORCE_ENABLE", "").lower() != "true":
        _log.warning("GLM 已永久降级（%s），返回 mock 数据", _GLM_DISABLE_REASON)
        return _mock_response(messages[-1]["content"])

    if AI_PROVIDER == "mock" or not GLM_API_KEY:
        return _mock_response(messages[-1]["content"])

    url = f"{GLM_BASE_URL}/chat/completions"
    use_model = model or GLM_TEXT_MODEL

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {GLM_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": use_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 4096
                }
            )

        # 成功返回
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"]

        # — 失败处理：检查是否额度/欠费相关 —
        body = resp.text
        _log.error("GLM API 返回 %d: %s", resp.status_code, body[:500])

        if _is_quota_error(resp.status_code, body):
            _GLM_DISABLED = True
            _GLM_DISABLE_REASON = f"HTTP {resp.status_code}: {body[:200]}"
            _log.critical(
                "⚠️ GLM 额度用尽/欠费！已永久降级为 mock，"
                "重启进程或重新部署前不会恢复。原因: %s", _GLM_DISABLE_REASON
            )
            return _mock_response(messages[-1]["content"])

        # 其他错误（500、超时等）不降级，抛给上层重试
        resp.raise_for_status()

    except httpx.TimeoutException:
        _log.error("GLM 请求超时，返回 mock 数据")
        return _mock_response(messages[-1]["content"])
    except httpx.HTTPStatusError:
        # raise_for_status 的异常，不在 quota 范围内
        raise
    except Exception:
        _log.exception("GLM 未知异常，返回 mock 数据")
        return _mock_response(messages[-1]["content"])


def _is_quota_error(status_code: int, body: str) -> bool:
    """判断是否为欠费/额度用尽错误。"""
    if status_code in _QUOTA_EXHAUSTED_CODES:
        return True
    body_lower = body.lower()
    for kw in _QUOTA_EXHAUSTED_KEYWORDS:
        if kw.lower() in body_lower:
            return True
    return False


def _mock_response(prompt: str) -> str:
    """Generate mock responses for demo when no API key."""
    if "学习计划" in prompt or "备考计划" in prompt:
        return json.dumps({
            "phases": [
                {
                    "name": "基础阶段",
                    "duration_days": 60,
                    "focus": ["数据结构", "计算机组成原理", "数学基础"],
                    "daily_schedule": "上午数学2h，下午专业课2h，晚上英语1h"
                },
                {
                    "name": "强化阶段",
                    "duration_days": 90,
                    "focus": ["操作系统", "计算机网络", "数学强化", "政治"],
                    "daily_schedule": "上午数学2h，下午专业课2h，晚上政治1h+英语1h"
                },
                {
                    "name": "冲刺阶段",
                    "duration_days": 30,
                    "focus": ["真题演练", "错题回顾", "模拟考试"],
                    "daily_schedule": "上午模拟考试3h，下午复盘2h，晚上错题复习2h"
                }
            ],
            "weekly_goals": [
                "完成数据结构树与图章节",
                "数学完成线性代数一轮复习",
                "英语背诵200个核心词汇"
            ],
            "review_strategy": "采用艾宾浩斯遗忘曲线安排复习，新学内容1/3/7/14天后复习"
        }, ensure_ascii=False)
    elif "任务" in prompt or "每日" in prompt:
        return json.dumps({
            "tasks": [
                {"type": "new_study", "subject": "数据结构", "content": "学习二叉树遍历算法（前序/中序/后序/层序）", "duration": 45},
                {"type": "new_study", "subject": "数学", "content": "完成线性代数矩阵运算章节习题", "duration": 60},
                {"type": "review", "subject": "数据结构", "content": "复习栈与队列的基本操作和应用", "duration": 30},
                {"type": "review", "subject": "英语", "content": "复习昨日背诵的100个核心词汇", "duration": 25},
                {"type": "review", "subject": "数学", "content": "回顾极限计算常见题型", "duration": 30},
                {"type": "mistake", "subject": "计算机组成原理", "content": "重做Cache映射方式错题", "duration": 25}
            ]
        }, ensure_ascii=False)
    elif "卡片" in prompt or "问答" in prompt:
        return json.dumps({
            "cards": [
                {"question": "什么是二叉搜索树？", "answer": "二叉搜索树是一种特殊的二叉树，左子树所有节点值小于根节点，右子树所有节点值大于根节点。", "subject": "数据结构"},
                {"question": "栈的特点是什么？", "answer": "栈是后进先出（LIFO）的数据结构，只能在栈顶进行插入和删除操作。", "subject": "数据结构"},
                {"question": "Cache的三种映射方式是什么？", "answer": "直接映射、全相联映射、组相联映射。", "subject": "计算机组成原理"}
            ]
        }, ensure_ascii=False)
    elif "复盘" in prompt or "总结" in prompt:
        return json.dumps({
            "summary": "今日学习状态良好，完成了大部分计划任务。数据结构部分掌握较好，数学部分需要加强练习。",
            "highlights": ["数据结构二叉树遍历理解透彻", "英语词汇记忆效率提升"],
            "improvements": ["数学矩阵运算需要更多练习", "建议明天优先完成数学任务"],
            "tomorrow_focus": ["数学矩阵运算专项练习", "计算机组成原理Cache章节"],
            "mood_suggestion": "保持当前节奏，你已经做得很好了！适当休息，明天继续加油！"
        }, ensure_ascii=False)
    return json.dumps({"message": "Mock response"}, ensure_ascii=False)


async def generate_study_plan(params: dict) -> dict:
    """Generate a study plan based on user input."""
    prompt = f"""请根据以下信息生成一份详细的考研备考计划：

考试名称：{params.get('exam_name', '')}
考试日期：{params.get('exam_date', '')}
目标分数：{json.dumps(params.get('target_scores', {}), ensure_ascii=False)}
每日学习时间：{params.get('daily_study_time', 480)}分钟
薄弱点：{', '.join(params.get('weak_points', []))}

请生成包含学习阶段划分、每周目标、每日时间分配、复习策略的完整计划。返回JSON格式。"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    result = await _call_glm(messages)
    return json.loads(result)


async def generate_daily_tasks(params: dict) -> dict:
    """Generate daily tasks based on plan context."""
    prompt = f"""请根据以下信息生成今日学习任务：

考试名称：{params.get('exam_name', '')}
日期：{params.get('date', '')}
科目：{', '.join(params.get('subjects', []))}
剩余天数：{params.get('days_remaining', 0)}
可用时间：{params.get('available_time', 480)}分钟

请生成合理的新学、复习和错题回顾任务，总时长不超过可用时间。返回JSON格式，包含tasks数组。"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    result = await _call_glm(messages)
    return json.loads(result)


async def generate_flash_cards(content: str, subject: str = "通用") -> dict:
    """Generate Q&A flash cards from learning content."""
    prompt = f"""请将以下学习内容拆解成3-5个"问题+答案"的问答卡片：

科目：{subject}
内容：{content}

每个卡片包含 question 和 answer 字段，返回JSON格式。"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    result = await _call_glm(messages)
    return json.loads(result)


async def parse_task_text(text: str, plan_id: str = "") -> dict:
    """GLM 解析用户文字计划，提取每个字段。返回 {tasks: [{...}]}"""
    from datetime import date as dt_date, timedelta
    today = dt_date.today().isoformat()
    tomorrow = (dt_date.today() + timedelta(days=1)).isoformat()

    prompt = f"""你是 StudyMate 学习星球的 NLP 解析器。请把用户输入的自然语言计划拆成结构化的任务列表。

当前日期：{today}，明天：{tomorrow}

用户输入：
{text}

每个任务必须包含以下字段，缺什么就用默认值填：
- content: 任务内容摘要（10-20字，概括用户要做什么）
- subject: 科目名（数学/英语/政治/数据结构/计算机组成原理/操作系统/计算机网络/数据库/算法/UML/高等数学/C语言/软件工程 之一，根据语义判断）
- chapter: 章节名（如"二叉树"、"线性表"、"第三章"，用户提到了就提取；没提到填空字符串""）
- duration: 预计分钟数整数（25/30/45/50/60/90/120，用户说了就按说的，没说明默认 30）
- type: "new_study"(新学) / "review"(复习) / "mistake"(错题)，根据动词判断
- date: YYYY-MM-DD，提到"明天"={tomorrow}，"今天"或无时间={today}，"后天"={tomorrow}+1天
- start_hour: 0-23，用户说"上午9点"→9，"下午2点"→14，"晚上7点"→19，没说→9
- repeat_type: "none"/"daily"/"weekday"/"holiday"，提到"每天"→daily，"工作日"→weekday；默认为 "none"

**极其重要**：content 字段必须是20字以内的简洁摘要，不能把用户原话照搬。chapter必须单独提取到chapter字段。

返回例子：
{{"tasks":[{{"content":"复习二叉树遍历算法","subject":"数据结构","chapter":"二叉树","duration":45,"type":"review","date":"{today}","start_hour":9,"repeat_type":"none","selected":true}}]}}

严格返回纯JSON，不带```标记。"""

    messages = [
        {"role": "system", "content": "你是 Strict JSON 输出器。只输出合法 JSON，不要任何解释。"},
        {"role": "user", "content": prompt}
    ]
    try:
        result = await _call_glm(messages, temperature=0.1)
        data = json.loads(result)
        if "tasks" not in data:
            data = {"tasks": []}
        for t in data.get("tasks", []):
            t.setdefault("selected", True)
            t.setdefault("chapter", "")
            t.setdefault("start_hour", 9)
            t.setdefault("date", today)
            t.setdefault("duration", 30)
            t.setdefault("type", "new_study")
            t.setdefault("repeat_type", "none")
        return data
    except Exception:
        return _mock_parse_plan(text)

def _mock_parse_plan(text: str) -> dict:
    """Mock 解析文字计划（无 AI Key 时使用）"""
    import re
    from datetime import date as dt_date, timedelta
    today = dt_date.today().isoformat()
    tomorrow = (dt_date.today() + timedelta(days=1)).isoformat()

    subjects = ['数学', '英语', '政治', '数据结构', '操作系统', '计算机网络', '计算机组成原理', '数据库', 'UML', '算法']
    ch_keywords = ['章节', '二叉树', '栈', '队列', '链表', '排序', '查找', '图论', '哈希', '进程', '内存', '文件系统', '网络', 'TCP', 'IP', 'HTTP', 'DNS', 'Cache', '流水线', '阅读', '写作', '词汇', '完形', '翻译', '毛中特', '马原', '史纲']
    result = []

    lines = re.split(r'[,，。；;、\n]', text)
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 匹配科目
        subject = '数据结构'
        for s in subjects:
            if s in line:
                subject = s
                break

        # 匹配日期
        task_date = today
        if '明天' in line or '明日' in line:
            task_date = tomorrow

        # 匹配章节
        chapter = ''
        for kw in ch_keywords:
            if kw in line:
                chapter = kw
                break

        # 匹配时长
        dur_match = re.search(r'(\d+)\s*(分钟|小时|min)', line)
        duration = 30
        if dur_match:
            num = int(dur_match.group(1))
            duration = num * 60 if '小时' in dur_match.group(2) else num

        # 匹配开始时间
        start_hour = 9
        time_match = re.search(r'(\d+)点|(\d+):00|上午(\d+)|下午(\d+)', line)
        if time_match:
            h = int(time_match.group(1) or time_match.group(2) or time_match.group(3) or time_match.group(4) or 9)
            if '下午' in line and h < 12:
                h += 12
            start_hour = min(23, max(6, h))

        # 匹配类型
        task_type = 'new_study'
        if '复习' in line:
            task_type = 'review'
        elif '错题' in line or '重做' in line:
            task_type = 'mistake'

        result.append({
            'content': line,
            'subject': subject,
            'chapter': chapter,
            'duration': duration,
            'type': task_type,
            'date': task_date,
            'start_hour': start_hour,
            'selected': True,
        })

    return {'tasks': result}


async def generate_daily_review(
    completed_tasks: list,
    planned_time: int,
    actual_time: int
) -> dict:
    """Generate daily review summary."""
    prompt = f"""请根据今日学习数据生成复盘总结：

计划任务数：{len(planned_tasks)}
完成任务数：{len(completed_tasks)}
计划学习时间：{planned_time}分钟
实际学习时间：{actual_time}分钟

请生成包含总结、亮点、改进建议、明日重点和情绪关怀的复盘内容。返回JSON格式。"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    result = await _call_glm(messages)
    return json.loads(result)


async def analyze_syllabus_image(image_data_url: str, subject: str = "", description: str = "") -> dict:
    """使用智谱 GLM 视觉模型分析教材目录/大纲图片，提取章节结构。

    Args:
        image_data_url: Base64 data URL of the image
        subject: Subject name for context
        description: User's additional description of learning progress
    """
    global _GLM_DISABLED, _GLM_DISABLE_REASON

    if _GLM_DISABLED and os.environ.get("GLM_FORCE_ENABLE", "").lower() != "true":
        _log.warning("GLM 已永久降级（%s），返回 mock 视觉分析", _GLM_DISABLE_REASON)
        return _mock_syllabus_analysis(subject, description)

    if not GLM_API_KEY:
        return _mock_syllabus_analysis(subject, description)

    prompt = f"""请分析这张教材目录/大纲图片，提取章节结构。科目：{subject or '未知'}。用户补充描述：{description or '无'}。

请提取每一章的章节名称，并根据章节难度和用户描述，为每章建议每天所需的学习时间（分钟/天）和预计天数。

请严格按照以下JSON格式返回，不要包含markdown代码块标记：
{{
    "subject": "科目名",
    "chapters": [
        {{"name": "章节名", "daily_duration": 每天学习分钟数, "estimated_days": 预计需要天数}},
        ...
    ],
    "total_days": 总预计天数,
    "suggestion": "整体学习建议"
}}"""

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_data_url}},
                {"type": "text", "text": prompt}
            ]
        }
    ]

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                f"{GLM_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GLM_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GLM_VISION_MODEL,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 4096
                }
            )

        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            content = content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:]) if len(lines) > 1 else content
            if content.endswith("```"):
                content = content[:-3].strip()
            return json.loads(content)

        # — 失败处理 —
        body = resp.text
        _log.error("GLM 视觉 API 返回 %d: %s", resp.status_code, body[:500])

        if _is_quota_error(resp.status_code, body):
            _GLM_DISABLED = True
            _GLM_DISABLE_REASON = f"视觉 HTTP {resp.status_code}: {body[:200]}"
            _log.critical(
                "⚠️ GLM 视觉额度用尽/欠费！已永久降级为 mock。原因: %s",
                _GLM_DISABLE_REASON
            )
            return _mock_syllabus_analysis(subject, description)

        resp.raise_for_status()

    except httpx.TimeoutException:
        _log.error("GLM 视觉请求超时")
        return {"error": "请求超时", "chapters": [], "suggestion": "AI分析超时，请重试"}
    except httpx.HTTPStatusError:
        raise
    except Exception as e:
        _log.exception("GLM 视觉未知异常")
        return {"error": str(e), "chapters": [], "suggestion": "AI分析失败，请重试"}


async def generate_subject_phases(plan_info: dict) -> dict:
    """AI 为每个科目建议阶段划分（第几周到第几周做什么）。"""
    subjects = plan_info.get("subjects", [])
    total_weeks = plan_info.get("total_weeks", 20)
    exam_name = plan_info.get("exam_name", "")

    if AI_PROVIDER == "mock" or not GLM_API_KEY:
        return _mock_subject_phases(subjects, total_weeks)

    subject_names = [s.get("name", s) if isinstance(s, dict) else s for s in subjects]
    prompt = f"""请为以下备考计划的每个科目设计阶段划分：

考试：{exam_name}
总备考周期：{total_weeks} 周
科目：{", ".join(subject_names)}

为每个科目设计 2-4 个学习阶段（如基础、强化、真题冲刺），每阶段指定起止周数和颜色。
颜色从以下取：基础=#4caf50(绿)，强化=#2196f3(蓝)，真题=#ff9800(橙)，冲刺=#f44336(红)

按JSON格式返回（不要markdown代码块）：
{{"phases": {{"科目名": [{{"name":"阶段名","start_week":1,"end_week":4,"color":"#4caf50"}},...]}}}}"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    try:
        result = await _call_glm(messages, temperature=0.3)
        return json.loads(result)
    except Exception:
        return _mock_subject_phases(subjects, total_weeks)


def _mock_subject_phases(subjects: list, total_weeks: int) -> dict:
    """Mock subject phase plan."""
    colors = ["#4caf50", "#2196f3", "#ff9800", "#f44336"]
    phase_names = ["基础阶段", "强化阶段", "真题冲刺", "查漏补缺"]
    result = {}
    for idx, s in enumerate(subjects):
        name = s.get("name", s) if isinstance(s, dict) else s
        n = min(len(phase_names), 3)
        step = total_weeks // n if n > 0 else total_weeks
        items = []
        for i in range(n):
            items.append({
                "name": phase_names[i],
                "start_week": i * step + 1,
                "end_week": (i + 1) * step if i < n - 1 else total_weeks,
                "color": colors[i % len(colors)]
            })
        result[name] = items
    return {"phases": result}


def _mock_syllabus_analysis(subject: str, description: str) -> dict:
    """Mock syllabus analysis for demo when no API key."""
    return {
        "subject": subject or "数据结构",
        "chapters": [
            {"name": "第一章 绪论", "daily_duration": 30, "estimated_days": 2},
            {"name": "第二章 线性表", "daily_duration": 45, "estimated_days": 5},
            {"name": "第三章 栈与队列", "daily_duration": 45, "estimated_days": 4},
            {"name": "第四章 树与二叉树", "daily_duration": 60, "estimated_days": 7},
            {"name": "第五章 图", "daily_duration": 60, "estimated_days": 6},
            {"name": "第六章 查找", "daily_duration": 45, "estimated_days": 5},
            {"name": "第七章 排序", "daily_duration": 45, "estimated_days": 5},
        ],
        "total_days": 34,
        "suggestion": f"根据你的描述「{description or '无'}」，建议重点攻克树与图章节，这两章是考研重点，建议每天至少1小时。"
    }
