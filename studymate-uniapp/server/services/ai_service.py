"""DeepSeek AI service for plan generation, card generation, and daily review.
Qwen Vision for image-based syllabus analysis."""

import json
import base64
import httpx
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL_FLASH, DEEPSEEK_MODEL_PRO,
    QWEN_API_KEY, QWEN_BASE_URL, QWEN_VISION_MODEL
)


SYSTEM_PROMPT = """你是 StudyMate 学习星球的 AI 备考助手。你是一个专业、耐心、有洞察力的学习导师。
你的任务是根据用户的学习目标和当前状态，提供科学、个性化的学习建议。

输出格式要求：严格返回 JSON，不要包含 markdown 代码块标记，不要有额外解释。
"""


async def _call_deepseek(messages: list[dict], model: str = None, temperature: float = 0.7) -> str:
    """Call DeepSeek API with chat completions."""
    if not DEEPSEEK_API_KEY:
        # Return mock data for demo when no API key
        return _mock_response(messages[-1]["content"])

    model = model or DEEPSEEK_MODEL_FLASH
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4096
            }
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


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
学习阶段：{params.get('study_phase', '基础阶段')}

请生成包含学习阶段划分、每周目标、每日时间分配、复习策略的完整计划。返回JSON格式。"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    result = await _call_deepseek(messages)
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
    result = await _call_deepseek(messages)
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
    result = await _call_deepseek(messages)
    return json.loads(result)


async def generate_daily_review(
    planned_tasks: list,
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
    result = await _call_deepseek(messages)
    return json.loads(result)


async def analyze_syllabus_image(image_data_url: str, subject: str = "", description: str = "") -> dict:
    """Analyze a syllabus/TOC image using Qwen Vision and return chapter plan.

    Args:
        image_data_url: Base64 data URL of the image
        subject: Subject name for context
        description: User's additional description of learning progress
    """
    if not QWEN_API_KEY:
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
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{QWEN_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {QWEN_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": QWEN_VISION_MODEL,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 4096
                }
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            content = content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:]) if len(lines) > 1 else content
            if content.endswith("```"):
                content = content[:-3].strip()
            return json.loads(content)
    except Exception as e:
        return {"error": str(e), "chapters": [], "suggestion": "AI分析失败，请重试"}


def _mock_syllabus_analysis(subject: str, description: str) -> dict:
    """Mock syllabus analysis for demo when no Qwen API key."""
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