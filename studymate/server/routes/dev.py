"""开发工具路由 — 种子数据初始化API。"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/dev", tags=["dev"])


class SeedResponse(BaseModel):
    success: bool
    message: str
    details: dict = {}


def _run_seed():
    """执行种子数据初始化，返回统计信息。"""
    import bcrypt, random
    from datetime import date, timedelta
    from uuid import uuid4
    from database import SessionLocal, Base, engine
    from database import (
        User, StudyPlan, DailyTask, FlashCard, Mistake,
        Plant, FarmState, FocusRecord, UserSubject
    )

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    random.seed(42)
    today = date.today()

    # 清理旧数据
    for email in ["test@studymate.com", "test@example.com"]:
        u = db.query(User).filter(User.email == email).first()
        if u:
            db.delete(u)
            db.commit()

    # 用户
    uid = uuid4()
    hashed = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()
    db.add(User(id=uid, email="test@studymate.com", nickname="测试学员",
                hashed_password=hashed, avatar_url=""))
    db.flush()

    # 计划
    pid408 = uuid4()
    db.add(StudyPlan(id=pid408, user_id=uid, exam_name="考研408计算机专业基础综合",
                     exam_date=today + timedelta(days=150),
                     target_scores={"数学": 130, "英语": 80, "政治": 70, "408专业课": 120},
                     daily_study_time=480, weak_points=["算法题", "PV操作", "子网划分"],
                     study_phase="强化阶段", notes="每天8小时，重点攻克数据结构和操作系统"))
    db.flush()

    pidSoft = uuid4()
    db.add(StudyPlan(id=pidSoft, user_id=uid, exam_name="软考中级-软件设计师",
                     exam_date=today + timedelta(days=90),
                     target_scores={"基础知识": 75, "应用技术": 75},
                     daily_study_time=240, weak_points=["数据库设计", "UML建模"],
                     study_phase="基础阶段", notes="利用碎片时间备考软考"))
    db.flush()

    # ── 任务数据 ──
    task408 = []
    day_names = [
        (today - timedelta(days=6), [
            ("数据结构", "链表基础操作复习", "new_study", 45, "completed", 50, 9, "important_urgent"),
            ("英语", "单词Unit1复习", "review", 30, "completed", 35, 14, "urgent_not_important"),
        ]),
        (today - timedelta(days=5), [
            ("操作系统", "进程概念与状态转换", "new_study", 60, "completed", 55, 8, "important_urgent"),
            ("政治", "绪论部分复习", "review", 30, "completed", 40, 19, "not_important_not_urgent"),
            ("数据结构", "链表错题复习", "mistake", 25, "completed", 30, 20, "important_not_urgent"),
        ]),
        (today - timedelta(days=4), [
            ("计算机组成原理", "数据表示与运算", "new_study", 60, "completed", 65, 10, "important_not_urgent"),
            ("英语", "单词Unit2复习", "review", 30, "completed", 25, 14, "urgent_not_important"),
        ]),
        (today - timedelta(days=3), [
            ("计算机网络", "网络体系结构概述", "new_study", 50, "completed", 45, 9, "important_not_urgent"),
            ("操作系统", "进程管理复习", "review", 40, "completed", 50, 15, "important_urgent"),
        ]),
        (today - timedelta(days=2), [
            ("操作系统", "进程与线程概念", "new_study", 60, "completed", 60, 8, "important_urgent"),
            ("政治", "马原第一章：马克思主义概述", "review", 40, "completed", 45, 19, "not_important_not_urgent"),
            ("数据结构", "栈与队列基础", "new_study", 45, "completed", 40, 14, "important_not_urgent"),
        ]),
        (today - timedelta(days=1), [
            ("数据结构", "哈希表与冲突解决", "new_study", 60, "completed", 70, 9, "important_urgent"),
            ("英语", "阅读理解专项训练", "review", 45, "completed", 40, 14, "urgent_not_important"),
            ("计算机组成原理", "Cache存储器映射方式", "new_study", 50, "completed", 55, 16, "important_not_urgent"),
            ("计算机网络", "网络协议错题复习", "mistake", 30, "completed", 25, 19, "urgent_not_important"),
        ]),
        (today, [
            ("数据结构", "二叉树遍历算法（前序/中序/后序/层序）", "new_study", 60, "completed", 65, 8, "important_urgent"),
            ("数据结构", "两道二叉树遍历真题（前序+中序）", "review", 30, "completed", 25, 10, "important_not_urgent"),
            ("英语", "背诵英语单词Unit5（50词）", "new_study", 30, "pending", 0, 14, "urgent_not_important"),
            ("政治", "马原第二章：唯物辩证法", "review", 60, "pending", 0, 15, "not_important_not_urgent"),
            ("英语", "英语阅读理解错题回顾", "mistake", 45, "pending", 0, 19, "important_urgent"),
            ("操作系统", "整理内存管理笔记（分页/分段/段页式）", "new_study", 60, "completed", 55, 20, "important_not_urgent"),
        ]),
        (today + timedelta(days=1), [
            ("数据结构", "图的存储与遍历（DFS/BFS）", "new_study", 90, "pending", 0, 9, "important_urgent"),
            ("英语", "英语单词Unit5复习", "review", 30, "pending", 0, 14, "urgent_not_important"),
            ("计算机网络", "TCP/IP协议栈详解", "new_study", 60, "pending", 0, 15, "important_not_urgent"),
        ]),
        (today + timedelta(days=2), [
            ("操作系统", "进程调度算法", "new_study", 60, "pending", 0, 10, "important_not_urgent"),
            ("数据结构", "二叉树遍历错题复习", "mistake", 30, "pending", 0, 14, "urgent_not_important"),
            ("计算机组成原理", "运算器复习", "review", 40, "pending", 0, 19, "important_not_urgent"),
        ]),
        (today + timedelta(days=3), [
            ("数据结构", "图的最短路径算法", "new_study", 80, "pending", 0, 9, "important_urgent"),
            ("政治", "马原复习", "review", 50, "pending", 0, 14, "not_important_not_urgent"),
        ]),
        (today + timedelta(days=4), [
            ("操作系统", "内存管理章节复习", "review", 60, "pending", 0, 14, "important_not_urgent"),
            ("英语", "长难句解析练习", "new_study", 45, "pending", 0, 19, "urgent_not_important"),
        ]),
        (today + timedelta(days=5), [
            ("政治", "毛中特第一章", "new_study", 60, "pending", 0, 10, "not_important_not_urgent"),
            ("计算机网络", "HTTP协议详解", "new_study", 50, "pending", 0, 15, "important_not_urgent"),
        ]),
        (today + timedelta(days=6), [
            ("数据结构", "本周知识点复习", "review", 90, "pending", 0, 9, "important_urgent"),
            ("英语", "英语作文模板学习", "new_study", 45, "pending", 0, 15, "urgent_not_important"),
        ]),
        (today + timedelta(days=7), [
            ("数据结构", "查找算法（顺序/折半/B树）", "new_study", 70, "pending", 0, 9, "important_urgent"),
            ("计算机组成原理", "存储系统复习", "review", 50, "pending", 0, 14, "important_not_urgent"),
        ]),
        (today + timedelta(days=8), [
            ("操作系统", "文件系统原理", "new_study", 60, "pending", 0, 10, "important_not_urgent"),
            ("计算机网络", "网络层错题复习", "mistake", 30, "pending", 0, 15, "urgent_not_important"),
        ]),
        (today + timedelta(days=9), [
            ("数据结构", "排序算法（插入/交换/选择）", "new_study", 80, "pending", 0, 9, "important_urgent"),
            ("英语", "单词Unit6复习", "review", 30, "pending", 0, 14, "urgent_not_important"),
        ]),
        (today + timedelta(days=10), [
            ("计算机网络", "应用层协议DNS/HTTP", "new_study", 50, "pending", 0, 14, "important_not_urgent"),
            ("政治", "毛中特复习", "review", 40, "pending", 0, 19, "not_important_not_urgent"),
        ]),
        (today + timedelta(days=11), [
            ("计算机组成原理", "指令系统", "new_study", 60, "pending", 0, 10, "important_not_urgent"),
            ("操作系统", "文件系统错题", "mistake", 25, "pending", 0, 15, "urgent_not_important"),
        ]),
        (today + timedelta(days=12), [
            ("数据结构", "排序算法复习", "review", 60, "pending", 0, 9, "important_urgent"),
        ]),
        (today + timedelta(days=13), [
            ("操作系统", "设备管理", "new_study", 50, "pending", 0, 14, "important_not_urgent"),
            ("英语", "作文练习", "review", 45, "pending", 0, 19, "urgent_not_important"),
        ]),
        (today + timedelta(days=14), [
            ("数据结构", "本周总结复习", "review", 90, "pending", 0, 9, "important_urgent"),
            ("计算机网络", "网络安全基础", "new_study", 40, "pending", 0, 14, "important_not_urgent"),
            ("政治", "本周错题复习", "mistake", 30, "pending", 0, 19, "not_important_not_urgent"),
        ]),
    ]

    for d, tasks in day_names:
        for subj, content, ttype, dur, status, actual, hour, imp in tasks:
            task408.append(DailyTask(
                id=uuid4(), plan_id=pid408, date=d, type=ttype, subject=subj,
                content=content, duration=dur, status=status,
                actual_duration=actual if status == "completed" else None,
                start_hour=hour, importance=imp
            ))
    for t in task408:
        db.add(t)

    # 软考任务
    taskSoft = [
        DailyTask(id=uuid4(), plan_id=pidSoft, date=today - timedelta(days=5), type="new_study", subject="数据库", content="数据库系统概述", duration=45, status="completed", actual_duration=50, start_hour=10, importance="important_urgent"),
        DailyTask(id=uuid4(), plan_id=pidSoft, date=today - timedelta(days=3), type="review", subject="UML", content="UML基础概念复习", duration=30, status="completed", actual_duration=35, start_hour=14, importance="important_not_urgent"),
        DailyTask(id=uuid4(), plan_id=pidSoft, date=today - timedelta(days=1), type="new_study", subject="算法", content="排序算法练习", duration=50, status="completed", actual_duration=55, start_hour=16, importance="important_urgent"),
        DailyTask(id=uuid4(), plan_id=pidSoft, date=today, type="new_study", subject="数据库", content="学习数据库范式设计（1NF-3NF）", duration=60, status="completed", actual_duration=50, start_hour=9, importance="important_urgent"),
        DailyTask(id=uuid4(), plan_id=pidSoft, date=today, type="review", subject="UML", content="复习类图/时序图/用例图绘制", duration=45, status="pending", start_hour=14, importance="important_not_urgent"),
        DailyTask(id=uuid4(), plan_id=pidSoft, date=today, type="new_study", subject="算法", content="动态规划专项练习（背包/最短路径）", duration=60, status="completed", actual_duration=70, start_hour=19, importance="important_urgent"),
        DailyTask(id=uuid4(), plan_id=pidSoft, date=today + timedelta(days=1), type="new_study", subject="操作系统", content="PV操作信号量经典题型", duration=45, status="pending", start_hour=10, importance="urgent_not_important"),
        DailyTask(id=uuid4(), plan_id=pidSoft, date=today + timedelta(days=5), type="review", subject="数据库", content="范式设计复习", duration=40, status="pending", start_hour=14, importance="important_not_urgent"),
        DailyTask(id=uuid4(), plan_id=pidSoft, date=today + timedelta(days=10), type="new_study", subject="UML", content="设计模式与UML", duration=50, status="pending", start_hour=15, importance="important_not_urgent"),
        DailyTask(id=uuid4(), plan_id=pidSoft, date=today + timedelta(days=14), type="review", subject="算法", content="算法总复习", duration=60, status="pending", start_hour=9, importance="important_urgent"),
    ]
    for t in taskSoft:
        db.add(t)

    # ── 知识卡片 ──
    card408 = [
        FlashCard(id=uuid4(), plan_id=pid408, question="二叉树的前序/中序/后序遍历顺序？", answer="前序：根左右；中序：左根右；后序：左右根。", subject="数据结构", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["二叉树", "遍历"]),
        FlashCard(id=uuid4(), plan_id=pid408, question="什么是哈希冲突？常见解决方法？", answer="哈希冲突：不同关键字映射到同一地址。解决：链地址法、开放地址法、再哈希法。", subject="数据结构", mastery_level="familiar", next_review_date=today, review_count=1, tags=["哈希表", "重点"]),
        FlashCard(id=uuid4(), plan_id=pid408, question="进程和线程的区别？", answer="进程是资源分配的基本单位，线程是CPU调度的基本单位。进程间资源独立，线程共享进程资源。", subject="操作系统", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["进程", "线程"]),
        FlashCard(id=uuid4(), plan_id=pid408, question="TCP三次握手过程？", answer="1.客户端SYN=1,seq=x；2.服务器SYN+ACK,seq=y,ack=x+1；3.客户端ACK,seq=x+1,ack=y+1。", subject="计算机网络", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["TCP", "重点"]),
        FlashCard(id=uuid4(), plan_id=pid408, question="Cache三种映射方式？", answer="直接映射、全相联映射、组相联映射。", subject="计算机组成原理", mastery_level="familiar", next_review_date=today, review_count=1, tags=["Cache", "存储"]),
        FlashCard(id=uuid4(), plan_id=pid408, question="快速排序时间复杂度？最好/最坏？", answer="平均O(n log n)，最坏O(n²)。", subject="数据结构", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["排序", "公式"]),
        FlashCard(id=uuid4(), plan_id=pid408, question="死锁四个必要条件？", answer="互斥、请求与保持、不可剥夺、循环等待。", subject="操作系统", mastery_level="familiar", next_review_date=today + timedelta(days=3), review_count=1, tags=["死锁", "重点"]),
        FlashCard(id=uuid4(), plan_id=pid408, question="OSI七层模型从下到上？", answer="物理层→数据链路层→网络层→传输层→会话层→表示层→应用层。", subject="计算机网络", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["OSI", "网络"]),
        FlashCard(id=uuid4(), plan_id=pid408, question="流水线的三种冒险？", answer="结构冒险、数据冒险、控制冒险。", subject="计算机组成原理", mastery_level="mastered", next_review_date=today, review_count=3, tags=["流水线", "必考"]),
    ]
    for c in card408:
        db.add(c)

    cardSoft = [
        FlashCard(id=uuid4(), plan_id=pidSoft, question="数据库三大范式的要求？", answer="1NF:属性不可再分;2NF:消除部分依赖;3NF:消除传递依赖。", subject="数据库", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["范式", "重点"]),
        FlashCard(id=uuid4(), plan_id=pidSoft, question="动态规划的核心思想？", answer="将大问题分解为重叠子问题，自底向上求解，用表存储中间结果避免重复计算。", subject="算法", mastery_level="unmastered", next_review_date=today, review_count=0, tags=["DP", "公式"]),
        FlashCard(id=uuid4(), plan_id=pidSoft, question="PV操作中P/V的含义？", answer="P(proberen):申请资源,信号量-1;V(verhogen):释放资源,信号量+1。", subject="操作系统", mastery_level="familiar", next_review_date=today + timedelta(days=5), review_count=1, tags=["PV操作", "重点"]),
    ]
    for c in cardSoft:
        db.add(c)

    # ── 错题 ──
    mist408 = [
        Mistake(id=uuid4(), plan_id=pid408, question="BST中删除双子树节点如何操作？", answer="找到该节点的中序后继（右子树最小节点），用后继值替换，删除后继。", analysis="常见错误：直接删除导致树结构破坏。", subject="数据结构", difficulty="medium", next_review_date=today, correct_count=0, error_count=2, mastered="0", tags=["BST", "易错"]),
        Mistake(id=uuid4(), plan_id=pid408, question="页式存储中逻辑地址→物理地址转换过程？", answer="逻辑地址=页号+页内偏移；页号→页表→物理块号；物理地址=块号×页大小+偏移。", analysis="容易忘记页表可能有多级。", subject="操作系统", difficulty="hard", next_review_date=today, correct_count=1, error_count=3, mastered="0", tags=["存储", "重点"]),
        Mistake(id=uuid4(), plan_id=pid408, question="IPv4私有地址范围？", answer="10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16", analysis="容易漏掉172.16.0.0/12。", subject="计算机网络", difficulty="easy", next_review_date=today, correct_count=1, error_count=1, mastered="0", tags=["IP", "必考"]),
        Mistake(id=uuid4(), plan_id=pid408, question="什么是虚拟内存？作用？", answer="将磁盘空间作为内存扩展，使程序可运行超过物理内存的程序。", analysis="把虚拟内存和交换空间混为一谈。", subject="操作系统", difficulty="easy", next_review_date=today + timedelta(days=14), correct_count=3, error_count=1, mastered="1", tags=["内存"]),
        Mistake(id=uuid4(), plan_id=pid408, question="浮点数IEEE754中规格化数的范围？", answer="单精度：正数约1.2e-38到3.4e38，尾数隐含1.", analysis="忘记隐含的1导致范围计算错误。", subject="计算机组成原理", difficulty="medium", next_review_date=today, correct_count=0, error_count=2, mastered="0", tags=["浮点数", "重点"]),
    ]
    for m in mist408:
        db.add(m)

    mistSoft = [
        Mistake(id=uuid4(), plan_id=pidSoft, question="2NF和3NF的区别？", answer="2NF消除非主属性对码的部分函数依赖；3NF消除非主属性对码的传递函数依赖。", analysis="忘记区分部分依赖和传递依赖。", subject="数据库", difficulty="medium", next_review_date=today, correct_count=0, error_count=3, mastered="0", tags=["范式", "易错"]),
        Mistake(id=uuid4(), plan_id=pidSoft, question="动态规划最优子结构的含义？", answer="问题的最优解包含其子问题的最优解，这是DP适用的前提条件。", analysis="把最优子结构和贪心选择性质混淆。", subject="算法", difficulty="medium", next_review_date=today, correct_count=0, error_count=2, mastered="0", tags=["DP", "易错"]),
        Mistake(id=uuid4(), plan_id=pidSoft, question="读写者问题中写者优先的PV实现要点？", answer="增加互斥信号量wmutex，写者到达后阻塞后续读者。", analysis="容易忘记写者离开后需要同时唤醒读者和写者。", subject="操作系统", difficulty="hard", next_review_date=today + timedelta(days=7), correct_count=2, error_count=5, mastered="0", tags=["PV操作", "重点"]),
        Mistake(id=uuid4(), plan_id=pidSoft, question="UML中聚合和组合的区别？", answer="聚合是弱关联（部分可独立存在），组合是强关联（部分不能独立存在）。", analysis="容易混淆两种关系的强度。", subject="UML", difficulty="easy", next_review_date=today, correct_count=1, error_count=1, mastered="0", tags=["类图", "易错"]),
    ]
    for m in mistSoft:
        db.add(m)

    # ── 农场 ──
    plants = [
        Plant(id=uuid4(), plan_id=pid408, type="growing", subject="数据结构", progress=70),
        Plant(id=uuid4(), plan_id=pid408, type="harvested", subject="数据结构", progress=100),
        Plant(id=uuid4(), plan_id=pid408, type="sprout", subject="操作系统", progress=30),
        Plant(id=uuid4(), plan_id=pid408, type="seed", subject="计算机网络", progress=0),
        Plant(id=uuid4(), plan_id=pid408, type="sprout", subject="英语", progress=25),
        Plant(id=uuid4(), plan_id=pid408, type="harvested", subject="政治", progress=100),
        Plant(id=uuid4(), plan_id=pidSoft, type="growing", subject="数据库", progress=55),
        Plant(id=uuid4(), plan_id=pidSoft, type="sprout", subject="算法", progress=20),
    ]
    for p in plants:
        db.add(p)

    db.add(FarmState(id=uuid4(), plan_id=pid408, coins=120, experience=70, level=2))
    db.add(FarmState(id=uuid4(), plan_id=pidSoft, coins=45, experience=25, level=1))

    # ── 用户自定义科目 ──
    for name in ["高等数学", "C语言", "软件工程"]:
        db.add(UserSubject(id=uuid4(), user_id=uid, name=name))

    # ── 番茄钟记录（30天）──
    subjects_cfg = {
        "数据结构": ["二叉树遍历", "哈希表", "排序算法", "图论", "BST操作", "链表", "栈与队列"],
        "操作系统": ["进程管理", "内存管理", "PV操作", "死锁", "文件系统", "设备管理"],
        "计算机网络": ["TCP/IP", "OSI模型", "子网划分", "HTTP协议", "三次握手"],
        "英语": ["词汇Unit5", "阅读理解", "长难句", "写作练习", "完形填空"],
        "政治": ["马原", "毛中特", "史纲", "时政", "思修"],
    }
    durations = [25, 25, 25, 25, 50, 50]
    focus_count = 0
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        n = random.randint(3, 6) if d.weekday() >= 5 else random.randint(2, 4)
        for j in range(n):
            subj = random.choice(list(subjects_cfg.keys()))
            ch = random.choice(subjects_cfg[subj])
            dur = random.choice(durations)
            db.add(FocusRecord(id=uuid4(), plan_id=pid408 if random.random() > 0.25 else pidSoft,
                               user_id=uid, date=d, type="focus", subject=subj,
                               task_name=f"{subj} - {ch}", duration=dur))
            focus_count += 1

    db.commit()
    db.close()

    return {
        "tasks_408": len(task408),
        "tasks_soft": len(taskSoft),
        "cards_408": len(card408),
        "cards_soft": len(cardSoft),
        "mistakes_408": len(mist408),
        "mistakes_soft": len(mistSoft),
        "plants": len(plants),
        "focus_records": focus_count,
    }


@router.post("/seed", response_model=SeedResponse)
def seed_data():
    """初始化测试种子数据。部署后调用此API将数据写入Supabase。"""
    try:
        details = _run_seed()
        return SeedResponse(
            success=True,
            message="种子数据初始化成功！测试账号: test@studymate.com / 123456",
            details=details
        )
    except Exception as e:
        return SeedResponse(
            success=False,
            message=f"初始化失败: {str(e)}",
            details={}
        )
