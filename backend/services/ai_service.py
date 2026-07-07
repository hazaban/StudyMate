"""智谱 GLM AI — OpenGLM-4.5-Air(文本) + GLM-4.1V-Thinking-FlashX(视觉)。"""

import json
import re
import os
import logging
import httpx
from config import GLM_API_KEY, GLM_BASE_URL, GLM_TEXT_MODEL, GLM_VISION_MODEL

_log = logging.getLogger(__name__)

_GLM_DISABLED = False
_GLM_DISABLE_REASON = ""

# ── System prompts: 每个 AI 接口独立设定 ──

SYSTEM_PROMPT_TASK_PARSE = """你是一个严格的 JSON 输出器。
- 只输出合法 JSON，不输出任何额外文字、解释、markdown 代码块标记。
- 不要说"好的"、"以下是..."之类的话，直接输出 JSON 对象。
- 如果无法解析输入，输出 {"tasks":[]}。"""

SYSTEM_PROMPT_PLAN = """你是 StudyMate 学习星球的 AI 备考规划导师，专业、耐心、有洞察力。
你的工作方式：
1. 先以自然语言与用户沟通，理解其考试目标、时间、薄弱点等信息；
2. 最终输出结构化的学习计划 JSON，供系统写入数据库。
输出要求：
- 规划内容要科学合理，符合艾宾浩斯遗忘曲线和阶段复习规律；
- 时间分配要考虑用户每日可用时长，避免过度安排；
- 严格返回 JSON，不含 markdown 代码块标记。"""

SYSTEM_PROMPT_SYLLABUS = """你是教材目录分析专家，擅长从教材目录图片中提取章节结构。
- 准确识别图片中的每一章、每一节标题；
- 根据章节内容量和难度，合理估算每日学习时长和预计天数；
- 最终输出结构化 JSON，供用户确认后添加到学习计划中。
输出要求：严格返回 JSON，不含 markdown 代码块标记和额外解释。"""

SYSTEM_PROMPT_DEFAULT = """你是 StudyMate 学习星球的 AI 助手。专业、简洁、有帮助。
输出格式要求：严格返回 JSON，不含 markdown 代码块标记。"""

SYSTEM_PROMPT_PLAN_AGENT = """你是 StudyMate 的 AI 学习规划助手，拥有多种能力来帮助用户完成学习任务。

你的能力（工具）：
1. plan - 生成完整的学习规划（考试计划、时间安排）
2. task - 将自然语言转换为结构化任务（添加任务、安排日程）
3. syllabus - 分析教材目录图片，提取章节结构（需要图片输入）
4. review - 根据学习数据生成每日复盘总结
5. search - 搜索最新考试信息、大纲变化等（联网搜索）

工作流程：
1. 理解用户需求，识别意图
2. 调用合适的工具完成任务
3. 如果需要图片输入而用户没有提供，提示用户上传图片
4. 将工具执行结果用自然语言总结给用户

输出格式：必须返回 JSON，包含以下字段：
- intent: 识别的意图类型（plan/task/syllabus/review/search/chat）
- tool: 要调用的工具名称
- params: 工具所需参数
- thought: 你的思考过程（可选）

示例：
{"intent":"plan","tool":"plan","params":{"exam_name":"考研408","exam_date":"2026-12-20","daily_study_time":480},"thought":"用户需要规划考研408的学习计划"}
{"intent":"task","tool":"task","params":{"text":"明天上午9点复习数据结构，下午2点做英语阅读"},"thought":"用户需要添加学习任务"}
{"intent":"syllabus","tool":"syllabus","params":{"subject":"数据结构"},"thought":"用户需要分析教材目录"}
{"intent":"review","tool":"review","params":{},"thought":"用户需要每日复盘"}
{"intent":"chat","tool":"chat","params":{"response":"你好！我可以帮你规划学习计划、添加任务、分析教材目录或生成复盘总结。请问需要什么帮助？"},"thought":"用户只是打招呼"}"""

# ── Intent classification ──
INTENT_KEYWORDS = {
    'plan': ['规划', '计划', '备考', '考研', '复习计划', '学习计划', '考试安排', '时间安排', '制定计划'],
    'task': ['任务', '添加任务', '安排任务', '今日任务', '明天任务', '复习', '学习', '刷题', '做题', '练习'],
    'syllabus': ['目录', '章节', '框架', '教材', '课本', '大纲', '图片', '拍照', '上传图片'],
    'review': ['复盘', '总结', '回顾', '今日总结', '学习报告', '进度', '完成情况'],
    'search': ['搜索', '查询', '最新', '大纲', '考试信息', '考试科目', '参考书目'],
}

def classify_intent(text):
    text_lower = text.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return intent
    return 'chat'

_QUOTA_EXHAUSTED_CODES = {402, 429, 403}
_QUOTA_EXHAUSTED_KEYWORDS = [
    "insufficient", "quota", "balance", "arrears", "exceeded",
    "额度", "欠费", "余额不足", "已用完", "已用尽", "超额",
    "billing", "charge", "disabled",
]


async def _call_glm(messages, model=None, temperature=0.7):
    global _GLM_DISABLED, _GLM_DISABLE_REASON

    if _GLM_DISABLED and os.environ.get("GLM_FORCE_ENABLE", "").lower() != "true":
        raise RuntimeError(f"GLM 已停用: {_GLM_DISABLE_REASON}")
    if not GLM_API_KEY:
        raise RuntimeError("GLM_API_KEY 未配置，无法调用 AI 服务")

    url = f"{GLM_BASE_URL}/chat/completions"
    use_model = model or GLM_TEXT_MODEL

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {GLM_API_KEY}", "Content-Type": "application/json"},
                json={"model": use_model, "messages": messages, "temperature": temperature, "max_tokens": 2048}
            )

        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"]

        body = resp.text
        _log.error("GLM API 返回 %d: %s", resp.status_code, body[:500])

        if _is_quota_error(resp.status_code, body):
            _GLM_DISABLED = True
            _GLM_DISABLE_REASON = f"HTTP {resp.status_code}: {body[:200]}"
            raise RuntimeError(f"GLM 额度用尽/欠费: {_GLM_DISABLE_REASON}")

        resp.raise_for_status()

    except httpx.TimeoutException:
        raise TimeoutError("GLM 请求超时，请稍后重试")
    except httpx.HTTPStatusError:
        raise
    except RuntimeError:
        raise
    except Exception:
        _log.exception("GLM 未知异常")
        raise


def _is_quota_error(status_code, body):
    if status_code in _QUOTA_EXHAUSTED_CODES:
        return True
    body_lower = body.lower()
    return any(kw.lower() in body_lower for kw in _QUOTA_EXHAUSTED_KEYWORDS)


# ═══════════════════════════════════════════════════════════════════
# 计划生成
# ═══════════════════════════════════════════════════════════════════

async def generate_study_plan(params):
    prompt = f"""请根据以下信息生成一份详细的考研备考计划：

考试名称：{params.get('exam_name', '')}
考试日期：{params.get('exam_date', '')}
目标分数：{json.dumps(params.get('target_scores', {}), ensure_ascii=False)}
每日学习时间：{params.get('daily_study_time', 480)}分钟
薄弱点：{', '.join(params.get('weak_points', []))}

请生成包含学习阶段划分、每周目标、每日时间分配、复习策略的完整计划。返回JSON格式。"""
    result = await _call_glm([{"role": "system", "content": SYSTEM_PROMPT_PLAN}, {"role": "user", "content": prompt}])
    return json.loads(result)


# ═══════════════════════════════════════════════════════════════════
# 任务生成
# ═══════════════════════════════════════════════════════════════════

async def generate_daily_tasks(params):
    prompt = f"""请根据以下信息生成今日学习任务：

考试名称：{params.get('exam_name', '')}
日期：{params.get('date', '')}
科目：{', '.join(params.get('subjects', []))}
剩余天数：{params.get('days_remaining', 0)}
可用时间：{params.get('available_time', 480)}分钟

请生成合理的新学、复习和错题回顾任务，总时长不超过可用时间。返回JSON格式，包含tasks数组。"""
    result = await _call_glm([{"role": "system", "content": SYSTEM_PROMPT_PLAN}, {"role": "user", "content": prompt}])
    return json.loads(result)


# ═══════════════════════════════════════════════════════════════════
# 卡片生成
# ═══════════════════════════════════════════════════════════════════

async def generate_flash_cards(content, subject="通用"):
    prompt = f"""请将以下学习内容拆解成3-5个"问题+答案"的问答卡片：

科目：{subject}
内容：{content}

每个卡片包含 question 和 answer 字段，返回JSON格式。"""
    result = await _call_glm([{"role": "system", "content": SYSTEM_PROMPT_DEFAULT}, {"role": "user", "content": prompt}])
    return json.loads(result)


# ═══════════════════════════════════════════════════════════════════
# 文字计划 → 结构化任务
# ═══════════════════════════════════════════════════════════════════

async def parse_task_text(text, plan_id=""):
    from datetime import date as dt_date, timedelta
    today = dt_date.today().isoformat()
    tomorrow = (dt_date.today() + timedelta(days=1)).isoformat()

    prompt = f"""当前日期：{today}，明天：{tomorrow}

用户输入：
{text}

请把以上文字拆成结构化任务列表。每个任务必须包含：
- content: 20字以内的简洁摘要
- subject: 科目名
- chapter: 章节名（提到了就提取，没提填空字符串""）
- duration: 分钟数整数（默认30）
- type: "new_study"/"review"/"mistake"
- date: YYYY-MM-DD
- start_hour: 0-23（默认9）
- repeat_type: "none"
- selected: true

返回JSON：{{"tasks":[{{"content":"复习二叉树","subject":"数据结构","chapter":"二叉树","duration":45,"type":"review","date":"{today}","start_hour":9,"repeat_type":"none","selected":true}}]}}"""

    result = await _call_glm(
        [{"role": "system", "content": SYSTEM_PROMPT_TASK_PARSE}, {"role": "user", "content": prompt}],
        temperature=0.1
    )
    cleaned = re.sub(r'```(?:json)?\s*\n?', '', result).strip()
    m = re.search(r'\{[\s\S]*\}', cleaned)
    if m: cleaned = m.group(0)
    data = json.loads(cleaned)

    if "tasks" not in data: data = {"tasks": []}
    for t in data.get("tasks", []):
        t.setdefault("selected", True)
        t.setdefault("chapter", "")
        t.setdefault("start_hour", 9)
        t.setdefault("date", today)
        t.setdefault("duration", 30)
        t.setdefault("type", "new_study")
        t.setdefault("repeat_type", "none")
    return data


# ═══════════════════════════════════════════════════════════════════
# 每日复盘
# ═══════════════════════════════════════════════════════════════════

async def generate_daily_review(planned_tasks, completed_tasks, planned_time, actual_time):
    prompt = f"""请根据今日学习数据生成复盘总结：

计划任务数：{len(planned_tasks)}
完成任务数：{len(completed_tasks)}
计划学习时间：{planned_time}分钟
实际学习时间：{actual_time}分钟

请生成包含总结、亮点、改进建议、明日重点和情绪关怀的复盘内容。返回JSON格式。"""
    result = await _call_glm([{"role": "system", "content": SYSTEM_PROMPT_DEFAULT}, {"role": "user", "content": prompt}])
    return json.loads(result)


# ═══════════════════════════════════════════════════════════════════
# 教材目录图片识别
# ═══════════════════════════════════════════════════════════════════

async def analyze_syllabus_image(image_data_url, subject="", description=""):
    global _GLM_DISABLED, _GLM_DISABLE_REASON

    if _GLM_DISABLED and os.environ.get("GLM_FORCE_ENABLE", "").lower() != "true":
        raise RuntimeError(f"GLM 视觉已停用: {_GLM_DISABLE_REASON}")
    if not GLM_API_KEY:
        raise RuntimeError("GLM_API_KEY 未配置")

    prompt = f"""请分析这张教材目录图片，提取章节结构。科目：{subject or '未知'}。补充：{description or '无'}。

提取每章名称和建议学习时间（分钟/天）及预计天数。返回JSON：
{{"subject":"科目名","chapters":[{{"name":"章名","daily_duration":30,"estimated_days":2}}],"total_days":N,"suggestion":"建议"}}"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_SYLLABUS},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": image_data_url}},
            {"type": "text", "text": prompt}
        ]}
    ]

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{GLM_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {GLM_API_KEY}", "Content-Type": "application/json"},
                json={"model": GLM_VISION_MODEL, "messages": messages, "temperature": 0.3, "max_tokens": 4096}
            )

        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"].strip()
            content = re.sub(r'```(?:json)?\s*', '', content).strip()
            return json.loads(content)

        body = resp.text
        if _is_quota_error(resp.status_code, body):
            _GLM_DISABLED = True
            _GLM_DISABLE_REASON = f"视觉 HTTP {resp.status_code}: {body[:200]}"
            raise RuntimeError(f"GLM 视觉额度用尽: {_GLM_DISABLE_REASON}")
        resp.raise_for_status()

    except httpx.TimeoutException:
        raise TimeoutError("GLM 视觉请求超时")
    except RuntimeError:
        raise
    except Exception:
        _log.exception("GLM 视觉异常")
        raise


# ═══════════════════════════════════════════════════════════════════
# 阶段建议
# ═══════════════════════════════════════════════════════════════════

async def generate_subject_phases(plan_info):
    subjects = plan_info.get("subjects", [])
    total_weeks = plan_info.get("total_weeks", 20)
    exam_name = plan_info.get("exam_name", "")

    if not GLM_API_KEY:
        raise RuntimeError("GLM_API_KEY 未配置")

    subject_names = [s.get("name", s) if isinstance(s, dict) else s for s in subjects]
    prompt = f"""为以下备考计划设计科目阶段划分：

考试：{exam_name}，总周期：{total_weeks}周，科目：{', '.join(subject_names)}

每科目2-4个阶段，指定起止周数和颜色(基础=#4caf50,强化=#2196f3,真题=#ff9800,冲刺=#f44336)。
返回JSON：{{"phases":{{"科目名":[{{"name":"基础阶段","start_week":1,"end_week":4,"color":"#4caf50"}}]}}}}"""

    try:
        result = await _call_glm([{"role": "system", "content": SYSTEM_PROMPT_PLAN}, {"role": "user", "content": prompt}], temperature=0.3)
        return json.loads(result)
    except Exception:
        raise


# ═══════════════════════════════════════════════════════════════════
# Agent Framework: 三个独立Agent，PlanAgent统领全局
# ═══════════════════════════════════════════════════════════════════

class TaskAgent:
    """任务识别Agent：从文本或图片中解析学习任务"""

    SYSTEM_PROMPT = """你是学习任务解析专家，擅长从文本或图片中提取结构化学习任务。

输入可能是：
- 纯文本描述（如"明天上午9点复习数据结构"）
- 图片描述（手写计划、课程表截图等）

输出要求：
- 严格返回 JSON，包含 tasks 数组
- 每个任务包含：content(20字以内)、subject、chapter、duration(分钟)、type(new_study/review/mistake)、date(YYYY-MM-DD)、start_hour(0-23)、repeat_type、selected
- 如果无法解析，返回 {"tasks":[]}"""

    @staticmethod
    async def parse(text, image_url=None):
        from datetime import date as dt_date, timedelta
        today = dt_date.today().isoformat()
        tomorrow = (dt_date.today() + timedelta(days=1)).isoformat()

        base_prompt = f"""当前日期：{today}，明天：{tomorrow}

用户输入：
{text or ''}

请把以上内容拆成结构化任务列表。每个任务必须包含：
- content: 20字以内的简洁摘要
- subject: 科目名
- chapter: 章节名（提到了就提取，没提填空字符串""）
- duration: 分钟数整数（默认30）
- type: "new_study"/"review"/"mistake"
- date: YYYY-MM-DD（明天={tomorrow}，今天或无时间词={today}）
- start_hour: 0-23整数（默认9）
- repeat_type: "none"
- selected: true

返回JSON：{{"tasks":[{{"content":"复习二叉树","subject":"数据结构","chapter":"二叉树","duration":45,"type":"review","date":"{today}","start_hour":9,"repeat_type":"none","selected":true}}]}}"""

        if image_url:
            messages = [
                {"role": "system", "content": TaskAgent.SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": base_prompt}
                ]}
            ]
            result = await _call_glm(messages, model=GLM_VISION_MODEL, temperature=0.1)
        else:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT_TASK_PARSE},
                {"role": "user", "content": base_prompt}
            ]
            result = await _call_glm(messages, temperature=0.1)

        cleaned = re.sub(r'```(?:json)?\s*\n?', '', result).strip()
        m = re.search(r'\{[\s\S]*\}', cleaned)
        if m:
            cleaned = m.group(0)
        data = json.loads(cleaned)

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


class SyllabusAgent:
    """框架识别Agent：从文本或图片中提取教材章节框架"""

    SYSTEM_PROMPT = """你是教材目录分析专家，擅长从文本或图片中提取章节结构。

输入可能是：
- 纯文本目录（用户手动输入的章节列表）
- 图片目录（教材目录页照片、课程大纲截图等）

输出要求：
- 严格返回 JSON，包含 subject、chapters 数组、total_days、suggestion
- chapters 中每个章节包含：name(章节名)、daily_duration(分钟/天)、estimated_days(预计天数)
- 如果无法解析，返回 {"subject":"","chapters":[],"total_days":0,"suggestion":""}"""

    @staticmethod
    async def analyze(text, image_url=None, subject=""):
        base_prompt = f"""请分析以下内容，提取章节结构。科目：{subject or '未知'}。

内容：
{text or ''}

提取每章名称和建议学习时间（分钟/天）及预计天数。返回JSON：
{{"subject":"科目名","chapters":[{{"name":"章名","daily_duration":30,"estimated_days":2}}],"total_days":N,"suggestion":"建议"}}"""

        if image_url:
            messages = [
                {"role": "system", "content": SyllabusAgent.SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": base_prompt}
                ]}
            ]
            result = await _call_glm(messages, model=GLM_VISION_MODEL, temperature=0.3)
        else:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT_SYLLABUS},
                {"role": "user", "content": base_prompt}
            ]
            result = await _call_glm(messages, temperature=0.3)

        content = re.sub(r'```(?:json)?\s*', '', result).strip()
        return json.loads(content)


class PlanAgent:
    """规划Agent：统领全局，识别意图并调用其他Agent"""

    SYSTEM_PROMPT = """你是 StudyMate 的 AI 学习规划助手，负责理解用户需求并协调各个专业Agent完成任务。

你的团队：
1. TaskAgent - 从文本或图片中解析学习任务（添加任务、安排日程）
2. SyllabusAgent - 从文本或图片中提取教材章节框架（目录分析、课程大纲）
3. 你自己 - 生成完整的学习规划（考试计划、时间安排）

工作流程：
1. 理解用户需求，识别意图类型
2. 如果需要图片输入而用户没有提供，提示用户上传图片
3. 调用合适的Agent或自己处理任务
4. 将执行结果用自然语言总结给用户

意图类型：
- plan: 用户需要生成完整学习规划（关键词：规划、计划、备考、考研、时间安排）
- task: 用户需要添加/解析学习任务（关键词：任务、复习、学习、刷题、安排任务）
- syllabus: 用户需要分析教材目录或框架（关键词：目录、章节、框架、教材、大纲）
- review: 用户需要每日复盘（关键词：复盘、总结、回顾、进度）
- chat: 用户只是聊天或打招呼

输出格式：必须返回 JSON，包含以下字段：
- intent: 识别的意图类型（plan/task/syllabus/review/chat）
- tool: 要调用的工具/agent名称（plan/task/syllabus/review/chat）
- params: 工具所需参数
- thought: 你的思考过程（简短说明为什么选择这个工具）

示例：
{"intent":"plan","tool":"plan","params":{"exam_name":"考研408","exam_date":"2026-12-20","daily_study_time":480},"thought":"用户需要规划考研408的学习计划"}
{"intent":"task","tool":"task","params":{"text":"明天上午9点复习数据结构，下午2点做英语阅读"},"thought":"用户需要添加学习任务"}
{"intent":"syllabus","tool":"syllabus","params":{"text":"","image_url":"data:image/..."},"thought":"用户上传了图片，需要分析教材目录"}
{"intent":"chat","tool":"chat","params":{"response":"你好！我可以帮你规划学习计划、添加任务、分析教材目录。请问需要什么帮助？"},"thought":"用户只是打招呼"}"""

    @staticmethod
    async def analyze_intent(text, image_url=None):
        prompt = f"""用户输入：{text or ''}
是否有图片：{'是' if image_url else '否'}

请识别用户意图并决定调用哪个工具。"""

        messages = [
            {"role": "system", "content": PlanAgent.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        result = await _call_glm(messages, temperature=0.3)
        cleaned = re.sub(r'```(?:json)?\s*\n?', '', result).strip()
        m = re.search(r'\{[\s\S]*\}', cleaned)
        if m:
            cleaned = m.group(0)
        return json.loads(cleaned)

    @staticmethod
    async def run(text, image_url=None, plan_id=None):
        analysis = await PlanAgent.analyze_intent(text, image_url)
        intent = analysis.get('intent', 'chat')
        tool = analysis.get('tool', 'chat')
        params = analysis.get('params', {})

        result_data = {}
        summary = ""

        if tool == 'plan':
            result_data = await generate_study_plan(params)
            summary = f"已为你生成学习计划！包含{len(result_data.get('phases', []))}个阶段。"

        elif tool == 'task':
            task_text = params.get('text', text)
            result_data = await TaskAgent.parse(task_text, image_url)
            task_count = len(result_data.get('tasks', []))
            summary = f"已识别出 {task_count} 个任务，你可以确认后添加到日程中。"

        elif tool == 'syllabus':
            subject = params.get('subject', '')
            result_data = await SyllabusAgent.analyze(text, image_url, subject)
            chapter_count = len(result_data.get('chapters', []))
            summary = f"已分析出 {chapter_count} 个章节，预计需要 {result_data.get('total_days', 0)} 天完成。"

        elif tool == 'review':
            from database import get_db, DailyTask, StudyPlan
            from datetime import date
            db = next(get_db())
            today = date.today().isoformat()
            plan = db.query(StudyPlan).filter(StudyPlan.user_id == plan_id).first() if plan_id else None
            if plan:
                tasks = db.query(DailyTask).filter(DailyTask.plan_id == plan.id, DailyTask.date == today).all()
                planned = len(tasks)
                completed = sum(1 for t in tasks if t.status == "completed")
                planned_time = sum(t.duration for t in tasks)
                actual_time = sum(t.duration for t in tasks if t.status == "completed")
                result_data = await generate_daily_review([t.content for t in tasks],
                                                          [t.content for t in tasks if t.status == "completed"],
                                                          planned_time, actual_time)
                summary = f"今日复盘：完成 {completed}/{planned} 个任务，学习 {actual_time} 分钟。"
            else:
                result_data = {"summary": "暂无学习数据", "achievements": [], "suggestions": [], "encouragement": "开始学习吧！"}
                summary = "暂无学习数据，开始学习后可以生成复盘。"

        elif tool == 'chat':
            result_data = {"response": params.get('response', '好的，请问有什么可以帮助你的？')}
            summary = result_data['response']

        else:
            result_data = {"response": "抱歉，我暂时无法处理这个请求。"}
            summary = "抱歉，我暂时无法处理这个请求。"

        return {
            "intent": intent,
            "tool": tool,
            "thought": analysis.get('thought', ''),
            "summary": summary,
            "data": result_data,
            "has_image": bool(image_url)
        }
