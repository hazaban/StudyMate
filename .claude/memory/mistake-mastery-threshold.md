---
name: mistake-mastery-threshold
description: 错题自动掌握的连续正确次数阈值是3，前后端各有一处硬编码
metadata:
  type: project
---

错题自动掌握规则：连续做对 **3 次** 自动标记 mastered=1，30 天后复习。

**后端**：`server/routes/mistakes.py:213` — `if mistake.correct_count >= 3:`

**前端**：`src/pages/review/index.vue:412` — `正确 {{ mistake.correct_count }}/3 次`

**规则详情**（`mistakes.py:193-225` review_mistake）：
- 做对：correct_count+1，按艾宾浩斯间隔推下次复习（1/3/7/14/30天）
- correct_count >= 3：自动 mastered='1'，next_review = 30天后
- 做错：correct_count 清零，error_count+1，mastered='0'，明天复习
- 手动标记已掌握：mastered='1'，next_review=30天后（mark_mastered）
- 重新攻克（retry）：error_count+1，correct_count=0，mastered='0'

**Why:** 阈值从 2 改到 3 时，index.vue 里有一份重复模板代码没改（/2 还是 /3），因为 review/index.vue 合并了 mistake-book.vue 后旧文件未删除。

**How to apply:** 以后再改这个阈值时，grep `correct_count >=` 和 `correct_count.*次` 找到所有硬编码位置。不要在 review/ 目录下新增独立页面文件——所有复习相关 UI 都在 index.vue 中通过 currentView 切换。
