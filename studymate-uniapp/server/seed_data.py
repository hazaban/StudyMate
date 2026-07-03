"""Seed the database with test data for the StudyMate app.

Run independently:  python seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import uuid
from datetime import date, timedelta

import bcrypt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import (
    Base, get_db, SessionLocal, engine,
    User, StudyPlan, DailyTask, FlashCard, Mistake, Plant, FarmState,
)
from config import SECRET_KEY, ALGORITHM

# passlib password context (bcrypt) — preferred, compatible with auth.py's bcrypt.checkpw
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password.

    Tries passlib's pwd_context.hash() first (as used in the codebase).
    Falls back to bcrypt directly (the exact method auth.py uses) if the
    passlib backend is unavailable — e.g. passlib 1.7.4 is incompatible
    with bcrypt >= 4.0. Both produce standard bcrypt hashes verifiable by
    auth.py's verify_password() (bcrypt.checkpw).
    """
    try:
        return pwd_context.hash(password)
    except Exception:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# Ensure tables exist
Base.metadata.create_all(bind=engine)

TEST_EMAIL = "test@studymate.com"
TEST_PASSWORD = "test123456"
TEST_NICKNAME = "测试学习者"


def run():
    db: Session = SessionLocal()
    try:
        # ── 1. Clean old data (if exists) ──
        old_user = db.query(User).filter(User.email == TEST_EMAIL).first()
        if old_user:
            db.delete(old_user)
            db.commit()
            print("已删除旧的测试用户及其关联数据")

        # ── 2. Create test user ──
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=TEST_EMAIL,
            nickname=TEST_NICKNAME,
            avatar_url="",
            hashed_password=hash_password(TEST_PASSWORD),
        )
        db.add(user)
        db.flush()
        print(f"创建用户: {TEST_EMAIL} / {TEST_PASSWORD} ({TEST_NICKNAME})")

        # ── 3. Create study plan ──
        plan_id = uuid.uuid4()
        subjects = [
            {
                "name": "高等数学",
                "target_score": 130,
                "chapters": [
                    {"name": "函数与极限", "duration": 60},
                    {"name": "导数与微分", "duration": 90},
                    {"name": "多元函数微积分", "duration": 120},
                ],
            },
            {
                "name": "英语",
                "target_score": 80,
                "chapters": [
                    {"name": "阅读理解", "duration": 60},
                    {"name": "完形填空", "duration": 45},
                ],
            },
            {
                "name": "数据结构",
                "target_score": 120,
                "chapters": [
                    {"name": "二叉树", "duration": 60},
                    {"name": "图论", "duration": 90},
                    {"name": "排序算法", "duration": 75},
                ],
            },
            {
                "name": "计算机组成原理",
                "target_score": 110,
                "chapters": [
                    {"name": "存储系统", "duration": 60},
                    {"name": "中央处理器", "duration": 90},
                ],
            },
        ]
        plan = StudyPlan(
            id=plan_id,
            user_id=user_id,
            exam_name="2026考研冲刺",
            exam_date=date(2026, 12, 21),
            target_scores={"高等数学": 130, "英语": 80, "数据结构": 120, "计算机组成原理": 110},
            daily_study_time=480,
            weak_points=["多元函数极值", "英语长难句", "AVL树旋转"],
            study_phase="强化阶段",
            notes="冲刺阶段每天保证8小时有效学习，重点攻克数学和数据结构",
            subjects=subjects,
        )
        db.add(plan)
        db.flush()
        print("创建学习计划: 2026考研冲刺 (考试日期: 2026-12-21, 阶段: 强化阶段)")

        # ── 4. Create daily tasks (5条, 不同科目、不同类型) ──
        today = date.today()
        tasks = [
            DailyTask(
                id=uuid.uuid4(), plan_id=plan_id, date=today,
                type="new_study", subject="高等数学", chapter="多元函数微积分",
                content="学习多元函数偏导数计算与全微分", duration=90, status="pending",
            ),
            DailyTask(
                id=uuid.uuid4(), plan_id=plan_id, date=today,
                type="review", subject="英语", chapter="阅读理解",
                content="复习2010-2015年考研阅读理解真题", duration=60, status="completed",
            ),
            DailyTask(
                id=uuid.uuid4(), plan_id=plan_id, date=today,
                type="mistake", subject="数据结构", chapter="二叉树",
                content="回顾二叉树遍历相关错题并重做", duration=45, status="pending",
            ),
            DailyTask(
                id=uuid.uuid4(), plan_id=plan_id, date=today,
                type="new_study", subject="计算机组成原理", chapter="中央处理器",
                content="学习CPU指令流水线原理与冲突处理", duration=75, status="doing",
            ),
            DailyTask(
                id=uuid.uuid4(), plan_id=plan_id, date=today,
                type="review", subject="数据结构", chapter="图论",
                content="复习图的遍历算法(DFS/BFS)", duration=50, status="pending",
            ),
        ]
        for t in tasks:
            db.add(t)
        print(f"创建今日任务: {len(tasks)} 条")

        # ── 5. Create flash cards (6张, 不同科目、不同掌握程度, 带标签) ──
        cards = [
            FlashCard(
                id=uuid.uuid4(), plan_id=plan_id,
                question="洛必达法则的适用条件是什么？",
                answer="满足0/0或∞/∞型未定式，且分子分母可导，导数比的极限存在或为无穷。",
                subject="高等数学", mastery_level="unmastered",
                next_review_date=today, review_count=0,
                tags=["极限", "重点"],
            ),
            FlashCard(
                id=uuid.uuid4(), plan_id=plan_id,
                question="泰勒展开式的作用是什么？常见函数的泰勒展开？",
                answer="用多项式逼近函数。e^x=1+x+x²/2!+...; sin(x)=x-x³/3!+x⁵/5!-...",
                subject="高等数学", mastery_level="familiar",
                next_review_date=today + timedelta(days=2), review_count=2,
                tags=["泰勒", "公式"],
            ),
            FlashCard(
                id=uuid.uuid4(), plan_id=plan_id,
                question="英语虚拟语气的常见结构和用法？",
                answer="if引导的与现在/过去/将来事实相反的从句，主从句时态需相应变化；wish/would rather后也用虚拟语气。",
                subject="英语", mastery_level="unmastered",
                next_review_date=today, review_count=1,
                tags=["语法", "虚拟语气"],
            ),
            FlashCard(
                id=uuid.uuid4(), plan_id=plan_id,
                question="快速排序的平均时间复杂度和最坏时间复杂度分别是多少？",
                answer="平均O(n log n)，最坏O(n²)（当数组已有序时）。",
                subject="数据结构", mastery_level="mastered",
                next_review_date=today + timedelta(days=7), review_count=5,
                tags=["排序", "必考"],
            ),
            FlashCard(
                id=uuid.uuid4(), plan_id=plan_id,
                question="什么是哈希冲突？常见的解决方法有哪些？",
                answer="不同关键字映射到同一地址。解决方法：链地址法、开放地址法(线性探测/二次探测)、再哈希法。",
                subject="数据结构", mastery_level="familiar",
                next_review_date=today + timedelta(days=1), review_count=3,
                tags=["哈希表", "重点"],
            ),
            FlashCard(
                id=uuid.uuid4(), plan_id=plan_id,
                question="Cache的三种映射方式是什么？",
                answer="直接映射、全相联映射、组相联映射。",
                subject="计算机组成原理", mastery_level="mastered",
                next_review_date=today - timedelta(days=3), review_count=4,
                tags=["Cache", "存储"],
            ),
        ]
        for c in cards:
            db.add(c)
        print(f"创建知识卡片: {len(cards)} 张")

        # ── 6. Create mistakes (5条, 不同科目、不同难度、不同掌握状态, 带标签和错误分析) ──
        mistakes = [
            Mistake(
                id=uuid.uuid4(), plan_id=plan_id,
                question="求函数 f(x,y)=x³+y³-3xy 的极值。",
                answer="令偏导数为0: fx=3x²-3y=0, fy=3y²-3x=0，解得(0,0)和(1,1)。用判别式AC-B²判断：(0,0)非极值点，(1,1)为极小值点。",
                analysis="容易忘记用判别式判断驻点是否为极值点，直接把驻点当作极值点。",
                subject="高等数学", difficulty="hard",
                error_count=3, correct_count=0, mastered="0",
                next_review_date=today,
                tags=["多元函数", "极值", "易错"],
            ),
            Mistake(
                id=uuid.uuid4(), plan_id=plan_id,
                question="分析长难句: The book that I bought yesterday, which was recommended by my teacher, is very useful.",
                answer="主句: The book is very useful. that引导定语从句修饰book, which引导非限制性定语从句补充说明book。",
                analysis="容易把which的先行词找错，误认为修饰yesterday或teacher。",
                subject="英语", difficulty="medium",
                error_count=2, correct_count=1, mastered="0",
                next_review_date=today + timedelta(days=1),
                tags=["长难句", "定语从句"],
            ),
            Mistake(
                id=uuid.uuid4(), plan_id=plan_id,
                question="在AVL树中插入节点导致不平衡时，四种旋转(LL/RR/LR/RL)分别在什么情况下使用？",
                answer="LL型用右旋，RR型用左旋，LR型先左旋后右旋，RL型先右旋后左旋。",
                analysis="容易混淆LR和RL的旋转顺序，导致平衡失败。",
                subject="数据结构", difficulty="hard",
                error_count=4, correct_count=0, mastered="0",
                next_review_date=today,
                tags=["AVL树", "旋转", "难点"],
            ),
            Mistake(
                id=uuid.uuid4(), plan_id=plan_id,
                question="IEEE754单精度浮点数如何表示？",
                answer="1位符号位+8位阶码(偏移量127)+23位尾数。规格化数隐含最高位1。",
                analysis="最初忘记阶码的偏移量是127而不是128。",
                subject="计算机组成原理", difficulty="medium",
                error_count=1, correct_count=3, mastered="1",
                next_review_date=today - timedelta(days=5),
                tags=["浮点数", "IEEE754"],
            ),
            Mistake(
                id=uuid.uuid4(), plan_id=plan_id,
                question="栈和队列的区别是什么？",
                answer="栈是后进先出(LIFO)，只能在栈顶操作；队列是先进先出(FIFO)，队尾入队、队头出队。",
                analysis="概念理解不清，曾把队列的入队出队方向弄反。",
                subject="数据结构", difficulty="easy",
                error_count=1, correct_count=4, mastered="1",
                next_review_date=today - timedelta(days=10),
                tags=["栈", "队列", "基础"],
            ),
        ]
        for m in mistakes:
            db.add(m)
        print(f"创建错题: {len(mistakes)} 条")

        # ── 7. Create farm data (plants + farm state) ──
        plants = [
            Plant(
                id=uuid.uuid4(), plan_id=plan_id,
                type="growing", subject="高等数学", progress=65,
            ),
            Plant(
                id=uuid.uuid4(), plan_id=plan_id,
                type="sprout", subject="数据结构", progress=30,
            ),
            Plant(
                id=uuid.uuid4(), plan_id=plan_id,
                type="mature", subject="计算机组成原理", progress=100,
            ),
        ]
        for p in plants:
            db.add(p)

        farm_state = FarmState(
            id=uuid.uuid4(),
            plan_id=plan_id,
            coins=150,
            experience=320,
            level=3,
        )
        db.add(farm_state)
        print(f"创建农场数据: {len(plants)} 株植物, 农场等级 {farm_state.level} ({farm_state.coins} 金币, {farm_state.experience} 经验)")

        db.commit()

        # ── Summary ──
        cards_due_today = sum(1 for c in cards if c.next_review_date <= today)
        mistakes_due_today = sum(1 for m in mistakes if m.next_review_date <= today and m.mastered == "0")

        print("\n" + "=" * 50)
        print("✅ 种子数据创建成功！")
        print("=" * 50)
        print(f"  登录邮箱:  {TEST_EMAIL}")
        print(f"  登录密码:  {TEST_PASSWORD}")
        print(f"  昵称:      {TEST_NICKNAME}")
        print(f"  学习计划:  2026考研冲刺 (强化阶段)")
        print(f"  科目数量:  {len(subjects)} 个 (含 {sum(len(s['chapters']) for s in subjects)} 章节)")
        print(f"  今日任务:  {len(tasks)} 条")
        print(f"  知识卡片:  {len(cards)} 张 ({cards_due_today} 张今日待复习)")
        print(f"  错题记录:  {len(mistakes)} 条 ({mistakes_due_today} 条今日待复习)")
        print(f"  农场植物:  {len(plants)} 株")
        print(f"  农场等级:  {farm_state.level} 级")
        print("=" * 50)
    except Exception as e:
        db.rollback()
        print(f"❌ 种子数据创建失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
