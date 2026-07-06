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

SYSTEM_PROMPT = """你是 StudyMate 学习星球的 AI 备考助手。你是专业、耐心、有洞察力的学习导师。
输出格式要求：严格返回 JSON，不含 markdown 代码块标记。"""

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
    result = await _call_glm([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}])
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
    result = await _call_glm([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}])
    return json.loads(result)


# ═══════════════════════════════════════════════════════════════════
# 卡片生成
# ═══════════════════════════════════════════════════════════════════

async def generate_flash_cards(content, subject="通用"):
    prompt = f"""请将以下学习内容拆解成3-5个"问题+答案"的问答卡片：

科目：{subject}
内容：{content}

每个卡片包含 question 和 answer 字段，返回JSON格式。"""
    result = await _call_glm([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}])
    return json.loads(result)


# ═══════════════════════════════════════════════════════════════════
# 文字计划 → 结构化任务
# ═══════════════════════════════════════════════════════════════════

async def parse_task_text(text, plan_id=""):
    from datetime import date as dt_date, timedelta
    today = dt_date.today().isoformat()
    tomorrow = (dt_date.today() + timedelta(days=1)).isoformat()

    prompt = f"""你是 Strict JSON 输出器。只输出合法 JSON。

当前日期：{today}，明天：{tomorrow}

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
        [{"role": "system", "content": "你是 Strict JSON 输出器。"}, {"role": "user", "content": prompt}],
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
    result = await _call_glm([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}])
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

    messages = [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": image_data_url}},
        {"type": "text", "text": prompt}
    ]}]

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
        result = await _call_glm([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}], temperature=0.3)
        return json.loads(result)
    except Exception:
        raise
