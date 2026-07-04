"""Seed demo data — comprehensive test coverage for all features."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import bcrypt, random
from datetime import date, timedelta
from uuid import uuid4

from database import SessionLocal, engine, Base
from database import User, StudyPlan, DailyTask, FlashCard, Mistake, Plant, FarmState, FocusRecord, UserSubject

random.seed(42)
today = date.today()

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Clean ──
for email in ["test@studymate.com", "test@example.com"]:
    u = db.query(User).filter(User.email == email).first()
    if u: db.delete(u); db.commit(); print(f"  cleaned: {email}")

# ═══════════════════════════════════════════════════════════════════
# 1. User
# ═══════════════════════════════════════════════════════════════════
uid = uuid4()
hashed = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()
db.add(User(id=uid, email="test@studymate.com", nickname="测试学员", hashed_password=hashed, avatar_url=""))
db.flush()

# ═══════════════════════════════════════════════════════════════════
# 2. Two plans
# ═══════════════════════════════════════════════════════════════════
pid408 = uuid4()
db.add(StudyPlan(id=pid408, user_id=uid, exam_name="考研408计算机专业基础综合", exam_date=today+timedelta(days=150), target_scores={"数学":130,"英语":80,"政治":70,"408专业课":120}, daily_study_time=480, weak_points=["算法题","PV操作","子网划分"], study_phase="强化阶段", notes="每天8小时，重点攻克数据结构和操作系统"))
db.flush()

pidSoft = uuid4()
db.add(StudyPlan(id=pidSoft, user_id=uid, exam_name="软考中级-软件设计师", exam_date=today+timedelta(days=90), target_scores={"基础知识":75,"应用技术":75}, daily_study_time=240, weak_points=["数据库设计","UML建模"], study_phase="基础阶段", notes="利用碎片时间备考软考"))
db.flush()

# ═══════════════════════════════════════════════════════════════════
# 3. Tasks — 考研408 (6) + 软考 (4)
# ═══════════════════════════════════════════════════════════════════
task408 = [
    DailyTask(id=uuid4(), plan_id=pid408, date=today, type="new_study", subject="数据结构", content="二叉树遍历算法（前序/中序/后序/层序）", duration=60, status="completed", actual_duration=65),
    DailyTask(id=uuid4(), plan_id=pid408, date=today, type="review", subject="数据结构", content="两道二叉树遍历真题（前序+中序）", duration=30, status="completed", actual_duration=25),
    DailyTask(id=uuid4(), plan_id=pid408, date=today, type="new_study", subject="英语", content="背诵英语单词Unit5（50词）", duration=30, status="pending"),
    DailyTask(id=uuid4(), plan_id=pid408, date=today, type="review", subject="政治", content="马原第二章：唯物辩证法", duration=60, status="pending"),
    DailyTask(id=uuid4(), plan_id=pid408, date=today, type="mistake", subject="英语", content="英语阅读理解错题回顾", duration=45, status="pending"),
    DailyTask(id=uuid4(), plan_id=pid408, date=today, type="new_study", subject="操作系统", content="整理内存管理笔记（分页/分段/段页式）", duration=60, status="completed", actual_duration=55),
]
for t in task408: db.add(t)

taskSoft = [
    DailyTask(id=uuid4(), plan_id=pidSoft, date=today, type="new_study", subject="数据库", content="学习数据库范式设计（1NF-3NF）", duration=60, status="completed", actual_duration=50),
    DailyTask(id=uuid4(), plan_id=pidSoft, date=today, type="review", subject="UML", content="复习类图/时序图/用例图绘制", duration=45, status="pending"),
    DailyTask(id=uuid4(), plan_id=pidSoft, date=today, type="new_study", subject="算法", content="动态规划专项练习（背包/最短路径）", duration=60, status="completed", actual_duration=70),
    DailyTask(id=uuid4(), plan_id=pidSoft, date=today, type="new_study", subject="操作系统", content="PV操作信号量经典题型", duration=45, status="pending"),
]
for t in taskSoft: db.add(t)

# ═══════════════════════════════════════════════════════════════════
# 4. Knowledge cards — 考研408 (9) + 软考 (4)
# ═══════════════════════════════════════════════════════════════════
card408 = [
    # ── due today ──
    FlashCard(id=uuid4(), plan_id=pid408, question="二叉树的前序/中序/后序遍历顺序？", answer="前序：根左右；中序：左根右；后序：左右根。", subject="数据结构", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["二叉树","遍历"],
        question_images=["https://picsum.photos/seed/bt-order/600/250"]),
    FlashCard(id=uuid4(), plan_id=pid408, question="什么是哈希冲突？常见解决方法？", answer="哈希冲突：不同关键字映射到同一地址。解决：链地址法、开放地址法、再哈希法。", subject="数据结构", mastery_level="familiar", next_review_date=today, review_count=1, tags=["哈希表","重点"],
        question_images=["https://picsum.photos/seed/hash-q/500/250"]),
    FlashCard(id=uuid4(), plan_id=pid408, question="进程和线程的区别？", answer="进程是资源分配的基本单位，线程是CPU调度的基本单位。进程间资源独立，线程共享进程资源。", subject="操作系统", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["进程","线程"]),
    FlashCard(id=uuid4(), plan_id=pid408, question="TCP三次握手过程？", answer="1.客户端SYN=1,seq=x；2.服务器SYN+ACK,seq=y,ack=x+1；3.客户端ACK,seq=x+1,ack=y+1。", subject="计算机网络", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["TCP","重点"],
        answer_images=["https://picsum.photos/seed/tcp-hand/550/280"]),
    FlashCard(id=uuid4(), plan_id=pid408, question="Cache三种映射方式？", answer="直接映射、全相联映射、组相联映射。", subject="计算机组成原理", mastery_level="familiar", next_review_date=today, review_count=1, tags=["Cache","存储"]),
    # ── 纯图片卡片 (问题/答案仅图片) ──
    FlashCard(id=uuid4(), plan_id=pid408, question="", answer="",
        subject="数据结构", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["公式","必考"],
        question_images=["https://picsum.photos/seed/q-tree-array/600/300","https://picsum.photos/seed/q-tree-detail/450/250"],
        answer_images=["https://picsum.photos/seed/a-tree-formula/500/300"]),
    # ── due in future ──
    FlashCard(id=uuid4(), plan_id=pid408, question="快速排序时间复杂度？最好/最坏？", answer="平均O(n log n)，最坏O(n²)。", subject="数据结构", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["排序","公式"]),
    FlashCard(id=uuid4(), plan_id=pid408, question="死锁四个必要条件？", answer="互斥、请求与保持、不可剥夺、循环等待。", subject="操作系统", mastery_level="familiar", next_review_date=today+timedelta(days=7), review_count=1, tags=["死锁","重点"]),
    FlashCard(id=uuid4(), plan_id=pid408, question="OSI七层模型从下到上？", answer="物理层→数据链路层→网络层→传输层→会话层→表示层→应用层。", subject="计算机网络", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["OSI","网络"],
        question_images=["https://picsum.photos/seed/osi-model/550/250"]),
    FlashCard(id=uuid4(), plan_id=pid408, question="流水线的三种冒险？", answer="结构冒险、数据冒险、控制冒险。", subject="计算机组成原理", mastery_level="mastered", next_review_date=today, review_count=3, tags=["流水线","必考"]),
    # ── 纯图片卡片(已掌握) ──
    FlashCard(id=uuid4(), plan_id=pid408, question="", answer="",
        subject="计算机组成原理", mastery_level="mastered", next_review_date=today+timedelta(days=14), review_count=5, tags=["存储","必考"],
        question_images=["https://picsum.photos/seed/q-cache-struct/500/300"],
        answer_images=["https://picsum.photos/seed/a-cache-diag/550/280","https://picsum.photos/seed/a-cache-tbl/480/250"]),
]
for c in card408: db.add(c)

cardSoft = [
    FlashCard(id=uuid4(), plan_id=pidSoft, question="数据库三大范式的要求？", answer="1NF:属性不可再分;2NF:消除部分依赖;3NF:消除传递依赖。", subject="数据库", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["范式","重点"]),
    FlashCard(id=uuid4(), plan_id=pidSoft, question="", answer="", subject="UML", mastery_level="familiar", next_review_date=today, review_count=2, tags=["类图","必考"],
        question_images=["https://picsum.photos/seed/q-uml-class/600/350"], answer_images=["https://picsum.photos/seed/a-uml-example/500/300"]),
    FlashCard(id=uuid4(), plan_id=pidSoft, question="动态规划的核心思想？", answer="将大问题分解为重叠子问题，自底向上求解，用表存储中间结果避免重复计算。", subject="算法", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["DP","公式"]),
    FlashCard(id=uuid4(), plan_id=pidSoft, question="PV操作中P/V的含义？", answer="P(proberen):申请资源,信号量-1;V(verhogen):释放资源,信号量+1。", subject="操作系统", mastery_level="familiar", next_review_date=today+timedelta(days=5), review_count=1, tags=["PV操作","重点"]),
]
for c in cardSoft: db.add(c)

# ═══════════════════════════════════════════════════════════════════
# 5. Mistakes — 考研408 (5) + 软考 (4)
# ═══════════════════════════════════════════════════════════════════
mist408 = [
    Mistake(id=uuid4(), plan_id=pid408, question="BST中删除双子树节点如何操作？", answer="找到该节点的中序后继（右子树最小节点），用后继值替换，删除后继。", analysis="常见错误：直接删除导致树结构破坏。", subject="数据结构", difficulty="medium", next_review_date=today, correct_count=0, error_count=2, mastered="0", tags=["BST","易错"],
        question_images=["https://picsum.photos/seed/bst-del/600/300"]),
    Mistake(id=uuid4(), plan_id=pid408, question="页式存储中逻辑地址→物理地址转换过程？", answer="逻辑地址=页号+页内偏移；页号→页表→物理块号；物理地址=块号×页大小+偏移。", analysis="容易忘记页表可能有多级。", subject="操作系统", difficulty="hard", next_review_date=today, correct_count=1, error_count=3, mastered="0", tags=["存储","重点"],
        question_images=["https://picsum.photos/seed/paging-err/550/280"]),
    Mistake(id=uuid4(), plan_id=pid408, question="IPv4私有地址范围？", answer="10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16", analysis="容易漏掉172.16.0.0/12。", subject="计算机网络", difficulty="easy", next_review_date=today, correct_count=1, error_count=1, mastered="0", tags=["IP","必考"]),
    Mistake(id=uuid4(), plan_id=pid408, question="", answer="写回比写直达快但更复杂。写直达每次都写内存，写回只在替换时写回。",
        analysis="混淆两种策略的适用场景：写回适合CPU-Cache频繁交互。", subject="计算机组成原理", difficulty="medium", next_review_date=today, correct_count=0, error_count=1, mastered="0", tags=["Cache"],
        question_images=["https://picsum.photos/seed/q-cache-write/500/300","https://picsum.photos/seed/q-cache-compare/480/280"]),
    Mistake(id=uuid4(), plan_id=pid408, question="什么是虚拟内存？作用？", answer="将磁盘空间作为内存扩展，使程序可运行超过物理内存的程序。", analysis="把虚拟内存和交换空间混为一谈。", subject="操作系统", difficulty="easy", next_review_date=today+timedelta(days=14), correct_count=3, error_count=1, mastered="1", tags=["内存"]),
]
for m in mist408: db.add(m)

mistSoft = [
    Mistake(id=uuid4(), plan_id=pidSoft, question="2NF和3NF的区别？", answer="2NF消除非主属性对码的部分函数依赖；3NF消除非主属性对码的传递函数依赖。", analysis="忘记区分部分依赖和传递依赖。", subject="数据库", difficulty="medium", next_review_date=today, correct_count=0, error_count=3, mastered="0", tags=["范式","易错"]),
    Mistake(id=uuid4(), plan_id=pidSoft, question="", answer="",
        analysis="看错了题干的约束条件，多对多关系需要转换为关联实体。", subject="UML", difficulty="hard", next_review_date=today, correct_count=1, error_count=4, mastered="0", tags=["类图","易错"],
        question_images=["https://picsum.photos/seed/q-uml-err/600/350"], answer_images=["https://picsum.photos/seed/a-uml-correct/550/300"]),
    Mistake(id=uuid4(), plan_id=pidSoft, question="动态规划最优子结构的含义？", answer="问题的最优解包含其子问题的最优解，这是DP适用的前提条件。", analysis="把最优子结构和贪心选择性质混淆。", subject="算法", difficulty="medium", next_review_date=today, correct_count=0, error_count=2, mastered="0", tags=["DP","易错"]),
    Mistake(id=uuid4(), plan_id=pidSoft, question="读写者问题中写者优先的PV实现要点？", answer="增加互斥信号量wmutex，写者到达后阻塞后续读者。需要计数器记录等待写者数。", analysis="容易忘记写者离开后需要同时唤醒读者和写者。", subject="操作系统", difficulty="hard", next_review_date=today+timedelta(days=7), correct_count=2, error_count=5, mastered="0", tags=["PV操作","重点"]),
]
for m in mistSoft: db.add(m)

# ═══════════════════════════════════════════════════════════════════
# 6. Farm
# ═══════════════════════════════════════════════════════════════════
for p in [
    Plant(id=uuid4(), plan_id=pid408, type="growing", subject="数据结构", progress=70),
    Plant(id=uuid4(), plan_id=pid408, type="harvested", subject="数据结构", progress=100),
    Plant(id=uuid4(), plan_id=pid408, type="sprout", subject="操作系统", progress=30),
    Plant(id=uuid4(), plan_id=pid408, type="seed", subject="计算机网络", progress=0),
    Plant(id=uuid4(), plan_id=pid408, type="sprout", subject="英语", progress=25),
    Plant(id=uuid4(), plan_id=pid408, type="harvested", subject="政治", progress=100),
    Plant(id=uuid4(), plan_id=pidSoft, type="growing", subject="数据库", progress=55),
    Plant(id=uuid4(), plan_id=pidSoft, type="sprout", subject="算法", progress=20),
]:
    db.add(p)

db.add(FarmState(id=uuid4(), plan_id=pid408, coins=120, experience=70, level=2))
db.add(FarmState(id=uuid4(), plan_id=pidSoft, coins=45, experience=25, level=1))

# ═══════════════════════════════════════════════════════════════════
# 7. User-defined subjects (后端持久化)
# ═══════════════════════════════════════════════════════════════════
for name in ["高等数学", "C语言", "软件工程"]:
    db.add(UserSubject(id=uuid4(), user_id=uid, name=name))

# ═══════════════════════════════════════════════════════════════════
# 8. Focus records — 30 days, varied
# ═══════════════════════════════════════════════════════════════════
subjects_cfg = {
    "数据结构": ["二叉树遍历","哈希表","排序算法","图论","BST操作","链表","栈与队列"],
    "操作系统": ["进程管理","内存管理","PV操作","死锁","文件系统","设备管理"],
    "计算机网络": ["TCP/IP","OSI模型","子网划分","HTTP协议","三次握手"],
    "英语": ["词汇Unit5","阅读理解","长难句","写作练习","完形填空"],
    "政治": ["马原","毛中特","史纲","时政","思修"],
}
durations = [25,25,25,25,50,50]
for i in range(29,-1,-1):
    d = today - timedelta(days=i)
    n = random.randint(3,6) if d.weekday()>=5 else random.randint(2,4)
    for j in range(n):
        subj = random.choice(list(subjects_cfg.keys()))
        ch = random.choice(subjects_cfg[subj])
        dur = random.choice(durations)
        db.add(FocusRecord(id=uuid4(), plan_id=pid408 if random.random()>0.25 else pidSoft, user_id=uid, date=d, type="focus", subject=subj, task_name=f"{subj} - {ch}", duration=dur))

# ═══════════════════════════════════════════════════════════════════
# Summary & Commit
# ═══════════════════════════════════════════════════════════════════
cdue = sum(1 for c in card408 if c.next_review_date<=today) + sum(1 for c in cardSoft if c.next_review_date<=today)
mdue = sum(1 for m in mist408 if m.next_review_date<=today and m.mastered=="0") + sum(1 for m in mistSoft if m.next_review_date<=today and m.mastered=="0")
fcnt = sum(1 for _ in [1])  # placeholder, real count requires query

print(f"""\n  Seed complete:
    Login:    test@studymate.com / 123456
    Plans:    考研408 + 软考
    Tasks:    {len(task408)} (408) + {len(taskSoft)} (软考)
    Cards:    {len(card408)} (408) + {len(cardSoft)} (软考) ({cdue} due today)
    Mistakes: {len(mist408)} (408) + {len(mistSoft)} (软考) ({mdue} due today)
    Plants:   6 (408) + 2 (软考)
    Subjects: 高数/C语言/软件工程
    Focus records: 30 days""")

db.commit()
db.close()
