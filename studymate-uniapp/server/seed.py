"""Seed the database with test data for demo purposes."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import bcrypt
from datetime import date, timedelta
from uuid import uuid4

from database import SessionLocal, engine, Base
from database import get_db, Base, User, StudyPlan, DailyTask, FlashCard, Mistake, Plant, FarmState, FocusRecord
# ── Subject → Tags mapping (tags are linked to subjects) ──
SUBJECT_TAGS = {
    "数据结构": ["二叉树", "遍历", "哈希表", "排序", "BST", "图", "重点", "公式", "易错", "必考"],
    "操作系统": ["进程", "线程", "死锁", "存储", "内存", "重点", "必考", "PV操作", "易错"],
    "计算机网络": ["TCP", "IP", "OSI", "网络", "重点", "必考", "协议", "子网"],
    "计算机组成原理": ["Cache", "流水线", "存储", "必考", "指令", "CPU"],
    "数学": ["公式", "易错", "重点", "必考", "计算"],
    "英语": ["词汇", "语法", "阅读", "重点", "写作"],
    "政治": ["马原", "毛中特", "史纲", "重点", "必考", "时政"],
}

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Clean existing test data ──
for email in ["test@studymate.com", "test@example.com"]:
    u = db.query(User).filter(User.email == email).first()
    if u:
        db.delete(u)
        db.commit()
        print(f"Cleaned existing test user: {email}")

# ── 1. Create test user ──
user_id = uuid4()
hashed = bcrypt.hashpw("test123456".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
user = User(
    id=user_id,
    email="test@example.com",
    nickname="测试学员",
    hashed_password=hashed,
    avatar_url=""
)
db.add(user)
db.flush()
print(f"Created user: test@example.com / test123456")

# ── 2. Create study plan ──
plan_id = uuid4()
plan = StudyPlan(
    id=plan_id,
    user_id=user_id,
    exam_name="考研408计算机专业基础综合",
    exam_date=date.today() + timedelta(days=150),
    target_scores={"数学": 130, "英语": 80, "政治": 70, "408专业课": 120},
    daily_study_time=480,
    weak_points=["数据结构算法题", "操作系统PV操作", "计算机网络子网划分"],
    study_phase="强化阶段",
    notes="每天保证8小时有效学习时间，重点攻克数据结构和操作系统"
)
db.add(plan)
db.flush()
print("Created study plan: 考研408复习计划")

# ── 3. Create tasks ──
today = date.today()
tasks = [
    DailyTask(id=uuid4(), plan_id=plan_id, date=today, type="new_study", subject="数据结构", content="复习数据结构第三章：二叉树遍历算法", duration=60, status="pending"),
    DailyTask(id=uuid4(), plan_id=plan_id, date=today, type="review", subject="数据结构", content="做两道二叉树遍历题（前序+中序）", duration=30, status="completed"),
    DailyTask(id=uuid4(), plan_id=plan_id, date=today, type="new_study", subject="英语", content="背诵英语单词Unit 5（50个词）", duration=30, status="pending"),
    DailyTask(id=uuid4(), plan_id=plan_id, date=today, type="review", subject="政治", content="复习政治马原第二章：唯物辩证法", duration=60, status="pending"),
    DailyTask(id=uuid4(), plan_id=plan_id, date=today, type="mistake", subject="英语", content="做一套英语阅读理解错题回顾", duration=45, status="pending"),
    DailyTask(id=uuid4(), plan_id=plan_id, date=today, type="new_study", subject="操作系统", content="整理操作系统内存管理笔记", duration=60, status="pending"),
]
for t in tasks:
    db.add(t)
print(f"Created {len(tasks)} tasks")

# ── 4. Create knowledge cards ──
cards = [
    # Due today
    FlashCard(id=uuid4(), plan_id=plan_id, question="二叉树的前序遍历、中序遍历、后序遍历分别是什么顺序？", answer="前序：根左右；中序：左根右；后序：左右根。", subject="数据结构", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["二叉树", "遍历"],
        question_images=["https://picsum.photos/seed/binary-tree-q/600/300"], answer_images=["https://picsum.photos/seed/binary-tree-a/600/200"]),
    FlashCard(id=uuid4(), plan_id=plan_id, question="什么是哈希冲突？解决哈希冲突的常见方法有哪些？", answer="哈希冲突是不同关键字映射到同一地址。解决：链地址法、开放地址法（线性探测、二次探测）、再哈希法。", subject="数据结构", mastery_level="familiar", next_review_date=today, review_count=1, tags=["哈希表", "重点"],
        question_images=["https://picsum.photos/seed/hash-q/500/250"]),
    FlashCard(id=uuid4(), plan_id=plan_id, question="进程和线程的区别是什么？", answer="进程是资源分配的基本单位，线程是CPU调度的基本单位。进程间资源独立，线程间共享进程资源。", subject="操作系统", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["进程", "线程"]),
    FlashCard(id=uuid4(), plan_id=plan_id, question="TCP三次握手的过程是怎样的？", answer="1. 客户端发送SYN=1, seq=x；2. 服务器回复SYN=1, ACK=1, seq=y, ack=x+1；3. 客户端发送ACK=1, seq=x+1, ack=y+1。", subject="计算机网络", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["TCP", "重点"],
        question_images=["https://picsum.photos/seed/tcp-q/600/280"], answer_images=["https://picsum.photos/seed/tcp-a1/300/200", "https://picsum.photos/seed/tcp-a2/300/200"]),
    FlashCard(id=uuid4(), plan_id=plan_id, question="cache的三种映射方式是什么？", answer="直接映射、全相联映射、组相联映射。", subject="计算机组成原理", mastery_level="familiar", next_review_date=today, review_count=1, tags=["Cache", "存储"]),
    # Due in future
    FlashCard(id=uuid4(), plan_id=plan_id, question="快速排序的时间复杂度是多少？最好和最坏情况下分别是多少？", answer="平均O(n log n)，最好O(n log n)，最坏O(n²)。", subject="数据结构", mastery_level="unmastered", next_review_date=today + timedelta(days=3), review_count=0, tags=["排序", "公式"]),
    FlashCard(id=uuid4(), plan_id=plan_id, question="死锁的四个必要条件是什么？", answer="互斥条件、请求与保持条件、不可剥夺条件、循环等待条件。", subject="操作系统", mastery_level="familiar", next_review_date=today + timedelta(days=7), review_count=1, tags=["死锁", "重点"]),
    FlashCard(id=uuid4(), plan_id=plan_id, question="OSI七层模型从下到上分别是什么？", answer="物理层、数据链路层、网络层、传输层、会话层、表示层、应用层。", subject="计算机网络", mastery_level="unmastered", next_review_date=today + timedelta(days=1), review_count=0, tags=["OSI", "网络"],
        question_images=["https://picsum.photos/seed/osi-q/550/250"]),
    FlashCard(id=uuid4(), plan_id=plan_id, question="流水线的三种冒险是什么？", answer="结构冒险、数据冒险、控制冒险。", subject="计算机组成原理", mastery_level="mastered", next_review_date=today - timedelta(days=10), review_count=3, tags=["流水线", "必考"]),
]
for c in cards:
    db.add(c)
print(f"Created {len(cards)} knowledge cards")

# ── 5. Create mistakes ──
mistakes = [
    # Due today, not mastered
    Mistake(id=uuid4(), plan_id=plan_id, question="在BST中删除一个有两个子节点的节点，应该如何操作？", answer="找到该节点的中序后继（右子树最小节点），用后继的值替换该节点，然后删除后继节点。", analysis="常见错误：直接删除节点导致树结构破坏。需要用中序后继替换。", subject="数据结构", difficulty="medium", next_review_date=today, correct_count=0, error_count=2, mastered="0", tags=["BST", "易错"],
        question_images=["https://picsum.photos/seed/bst-del/600/300"], answer_images=["https://picsum.photos/seed/bst-ans/500/250"]),
    Mistake(id=uuid4(), plan_id=plan_id, question="页式存储管理中，逻辑地址到物理地址的转换过程？", answer="逻辑地址分为页号和页内偏移，页号通过页表查到对应的物理块号，物理地址=物理块号×页面大小+页内偏移。", analysis="容易忘记页表可能有多级。", subject="操作系统", difficulty="hard", next_review_date=today, correct_count=1, error_count=3, mastered="0", tags=["存储", "重点"],
        question_images=["https://picsum.photos/seed/paging/550/280"]),
    Mistake(id=uuid4(), plan_id=plan_id, question="IPv4地址中，私有地址范围有哪些？", answer="10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16", analysis="容易漏掉172.16.0.0/12这个范围。", subject="计算机网络", difficulty="easy", next_review_date=today, correct_count=1, error_count=1, mastered="0", tags=["IP", "必考"]),
    # Due in future
    Mistake(id=uuid4(), plan_id=plan_id, question="Cache的写策略有哪些？各自的优缺点？", answer="写直达(Write-through)：同时写Cache和主存，简单但慢；写回(Write-back)：只写Cache，替换时写回主存，快但复杂。", analysis="容易混淆两种策略的适用场景。", subject="计算机组成原理", difficulty="medium", next_review_date=today + timedelta(days=1), correct_count=0, error_count=1, mastered="0", tags=["Cache"],
        question_images=["https://picsum.photos/seed/cache-write/500/250"]),
    # Mastered
    Mistake(id=uuid4(), plan_id=plan_id, question="什么是虚拟内存？它的作用是什么？", answer="虚拟内存将磁盘空间作为内存扩展，使得程序可以运行比物理内存大的程序，同时实现内存保护和隔离。", analysis="最初理解有误，把虚拟内存和交换空间混为一谈。", subject="操作系统", difficulty="easy", next_review_date=today - timedelta(days=5), correct_count=3, error_count=1, mastered="1", tags=["内存"]),
]
for m in mistakes:
    db.add(m)
print(f"Created {len(mistakes)} mistakes")

# ── 6. Create farm data ──
plants = [
    Plant(id=uuid4(), plan_id=plan_id, type="growing", subject="数据结构", progress=70, water_count=5, fertilize_count=2),
    Plant(id=uuid4(), plan_id=plan_id, type="harvested", subject="数据结构", progress=100, water_count=0, fertilize_count=0),
    Plant(id=uuid4(), plan_id=plan_id, type="sprout", subject="操作系统", progress=30, water_count=3, fertilize_count=1),
    Plant(id=uuid4(), plan_id=plan_id, type="seed", subject="计算机网络", progress=0, water_count=4, fertilize_count=1),
    Plant(id=uuid4(), plan_id=plan_id, type="sprout", subject="英语", progress=25, water_count=6, fertilize_count=3),
    Plant(id=uuid4(), plan_id=plan_id, type="harvested", subject="英语", progress=100, water_count=0, fertilize_count=0),
    Plant(id=uuid4(), plan_id=plan_id, type="harvested", subject="政治", progress=100, water_count=0, fertilize_count=0),
]
for p in plants:
    db.add(p)
print(f"Created {len(plants)} farm plants")

# ── 7. Create farm state ──
farm_state = FarmState(
    id=uuid4(),
    plan_id=plan_id,
    coins=120,
    experience=70,
    level=2
)
db.add(farm_state)
print("Created farm state: level 2, 120 coins")

# ── 8. Create 30 days of focus records (番茄钟种子数据) ──
import random
random.seed(42)
focus_subjects = ["数据结构", "操作系统", "计算机网络", "英语", "政治"]
subject_chapters = {
    "数据结构": ["二叉树遍历", "哈希表", "排序算法", "图论", "BST操作", "链表", "栈与队列"],
    "操作系统": ["进程管理", "内存管理", "PV操作", "死锁", "文件系统", "设备管理"],
    "计算机网络": ["TCP/IP", "OSI模型", "子网划分", "HTTP协议", "TCP三次握手", "UDP"],
    "英语": ["词汇Unit5", "阅读理解", "长难句分析", "写作练习", "完形填空"],
    "政治": ["马原", "毛中特", "史纲", "时政", "思修"]
}
durations = [25, 25, 25, 25, 50, 50]

focus_records = []
for i in range(29, -1, -1):
    d = today - timedelta(days=i)
    weekday = d.weekday()
    sessions_count = random.randint(3, 6) if weekday >= 5 else random.randint(2, 4)
    for j in range(sessions_count):
        subj = random.choice(focus_subjects)
        chapter = random.choice(subject_chapters[subj])
        duration = random.choice(durations)
        hour = 8 + j * 2 + random.randint(0, 1)
        minute = random.randint(0, 59)
        start_h = max(0, min(23, hour))
        start_m = minute
        end_minutes = start_h * 60 + start_m + duration
        end_h = min(23, end_minutes // 60)
        end_m = end_minutes % 60
        start_time = f"{d.isoformat()} {start_h:02d}:{start_m:02d}:00"
        end_time = f"{d.isoformat()} {end_h:02d}:{end_m:02d}:00"
        focus_records.append(FocusRecord(
            id=uuid4(),
            plan_id=plan_id,
            user_id=user_id,
            date=d,
            type="focus",
            subject=subj,
            task_name=f"{subj} - {chapter}",
            duration=duration,
            start_time=start_time,
            end_time=end_time
        ))

for r in focus_records:
    db.add(r)
print(f"Created {len(focus_records)} focus records (30 days)")

cards_due_today = sum(1 for c in cards if c.next_review_date <= today)
mistakes_due_today = sum(1 for m in mistakes if m.next_review_date <= today and m.mastered == '0')

db.commit()
db.close()

print("\n=== Seed data created successfully! ===")
print("   Login:    test@example.com")
print("   Password: test123456")
print("   Plan:     kaoyan 408 review plan")
print(f"   Tasks:    {len(tasks)} tasks for today")
print(f"   Cards:    {len(cards)} cards ({cards_due_today} due today)")
print(f"   Mistakes: {len(mistakes)} mistakes ({mistakes_due_today} due today)")
print(f"   Plants:   {len(plants)} plants")