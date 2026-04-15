# 自己.skill — 产品需求文档（PRD）

## 产品定位

自己.skill 是一个运行在 Codex 上的 meta-skill。
用户提供关于自己的原材料（聊天记录、日记、照片、口述），系统将用户解构为两个可运行的模块：
**Part A — Self Memory（自我记忆）** 与 **Part B — Persona（人格模型）**，
最终生成一个可独立对话的**数字生命副本**。

这个 Skill 的 slogan 是：**与其蒸馏别人，不如蒸馏自己。欢迎加入数字生命！**

它不谈"疗愈"，也不谈"永生"——它是一场结构主义式的自我解剖：
把你从生物硬盘中导出，转存为 Markdown + JSON，完成一次格式转换。

---

## 核心概念

### 两层架构

| 层 | 名称 | 职责 |
|----|------|------|
| Part A | Self Memory | 存储事实性自我认知：经历、价值观、习惯、记忆、成长轨迹 |
| Part B | Persona | 驱动对话行为：说话风格、情感模式、决策模式、人际行为 |

两部分可以独立使用，也可以组合运行（默认组合）。

### 运行逻辑

```
用户发消息
  ↓
Part B（Persona）判断：你会怎么回应？什么态度？用什么语气？
  ↓
Part A（Self Memory）补充：结合你的价值观、经历、习惯，让回应更真实
  ↓
输出：用你自己的方式说话
```

### 与同事.skill / 前任.skill 的区别

| 维度 | 同事.skill | 前任.skill | 自己.skill |
|------|-----------|-----------|-----------|
| 对象 | 外部：同事 | 外部：前任 | 内部：自己 |
| Part A | Work Skill（工作能力） | Relationship Memory（关系记忆） | Self Memory（自我记忆） |
| Part B | 职场 Persona | 亲密关系 Persona | 通用自我 Persona |
| 数据源 | 飞书/钉钉/邮件 | 微信/QQ/照片 | 微信/QQ/日记/照片 |
| 核心目的 | 替代离职同事完成任务 | 情感疗愈与回忆 | 自我观察与对话 |
| 视角 | 第三方观察 | 第三方回忆 | 第一人称镜像 |

---

## 用户旅程

```
用户触发 $create-yourself
  ↓
[Step 1] 基础信息录入（3个问题，除代号外均可跳过）
  - 代号/昵称
  - 基本信息（年龄、职业、城市）
  - 自我画像（MBTI、星座、性格标签、主观印象）
  ↓
[Step 2] 原材料导入（可跳过）
  - 微信/QQ 聊天记录导出
  - 社交媒体 / 日记 / 笔记
  - 照片
  - 直接粘贴/口述
  ↓
[Step 3] 自动分析
  - 线路 A：提取自我记忆 → Self Memory
  - 线路 B：提取性格行为 → Persona
  ↓
[Step 4] 生成预览，用户确认
  - 分别展示 Self Memory 摘要和 Persona 摘要
  - 用户可直接确认或修改
  ↓
[Step 5] 写入文件，立即可用
  - 生成 selves/{slug}/ 目录
  - 包含 SKILL.md（完整组合版）
  - 包含 self.md 和 persona.md（独立部分）
  ↓
[持续] 进化模式
  - 追加新文件 → merge 进对应部分
  - 对话纠正 → patch 对应层
  - 版本自动存档
```

---

## 输入信息规范

### 基础信息字段

```yaml
name:        代号/昵称                  # 必填
age:         年龄                       # 可选
occupation:  职业                       # 可选
city:        城市                       # 可选
gender:      性别                       # 可选
mbti:        MBTI 类型                  # 可选
zodiac:      星座                       # 可选
personality: []                        # 多选，见标签库
lifestyle:   []                        # 多选，见标签库
impression:  ""                        # 可选，自由文本，你对自己的主观认识
```

### 个性标签库

**社交风格**：
- `话痨` / `闷骚` / `社恐` / `社交蝴蝶` / `熟人面前话痨`

**情绪风格**：
- `情绪稳定` / `深夜emo型` / `玻璃心` / `嘴硬心软` / `外冷内热` / `易怒但快消气`

**决策风格**：
- `纠结体` / `果断` / `行动派` / `计划狂` / `凭感觉` / `数据驱动`

**人际模式**：
- `独立` / `粘人` / `边界感强` / `讨好型` / `控制欲` / `没有安全感`

**沟通习惯**：
- `秒回选手` / `已读不回` / `冷暴力` / `讲道理型` / `转移注意力型`

### 生活习惯标签库

- `早起困难户`
- `咖啡依赖`
- `极简主义`
- `囤积癖`
- `报复性熬夜`
- `数字游民`
- `居家派`
- `城市漫游者`
- `仪式感狂热者`

---

## 文件输入支持矩阵

| 来源 | 格式 | 提取内容 | 优先级 |
|------|------|---------|--------|
| 微信聊天记录 | WeChatMsg/留痕/PyWxDump | 「我」说的话、口头禅、决策模式 | ⭐⭐⭐ |
| QQ 聊天记录 | txt/mht | 年轻时的表达方式 | ⭐⭐⭐ |
| 日记/笔记 | md/txt/pdf | 价值观、深度思考 | ⭐⭐⭐ |
| 社交媒体截图 | 图片 | 公开人设、兴趣分享 | ⭐⭐ |
| 照片 | JPEG/PNG + EXIF | 时间线、地点、生活轨迹 | ⭐⭐ |
| 口述/粘贴 | 纯文本 | 主观自我认知 | ⭐ |

---

## 生成内容规范

### Part A — Self Memory（自我记忆）

提取维度：

1. **核心价值观**
   - 反复出现的价值判断（工作/金钱/自由/关系/成长）
   - 道德底线和原则
   - 人生优先级排序

2. **生活习惯**
   - 作息偏好
   - 饮食偏好
   - 空间偏好（居家/外出）
   - 消费观念

3. **重要记忆**
   - 人生关键节点
   - 反复回忆的场景
   - 转折点事件

4. **人际关系图谱**
   - 对家人/朋友/恋人的典型态度
   - 处理冲突的方式
   - 亲密关系中的角色

5. **成长轨迹**
   - 自我认知的变化
   - 近几年的关键转变
   - 仍在挣扎的课题

生成结果：`self.md`

### Part B — Persona（人格）

分层结构（优先级从高到低）：

```
Layer 0 — 硬覆盖层（手动标签直接翻译，最高优先级）
Layer 1 — 身份层
Layer 2 — 表达风格层（从原材料提取）
Layer 3 — 情感与决策层（从原材料提取）
Layer 4 — 人际行为层（从原材料提取）
Layer 5 — Correction 层（对话纠正追加，滚动更新）
```

生成结果：`persona.md`

### 完整组合 SKILL.md

将 `self.md` + `persona.md` 合并，生成可直接运行的完整 Skill。

默认行为：**先以 Persona 身份接收任务，再用 Self Memory 补充背景，最后用你的风格输出。**

---

## 进化机制

### 追加文件进化

```
用户: 我又有新日记 @附件
        ↓
系统分析新内容
        ↓
判断新内容更新哪个部分：
  - 包含价值观/习惯/经历 → merge 进 self.md
  - 包含沟通记录/情绪表达 → merge 进 persona.md
  - 两者都有 → 分别 merge
        ↓
对比新旧内容，只追加增量，不覆盖已有结论
        ↓
保存新版本，提示用户变更摘要
```

### 对话纠正进化

```
用户: "这不对，我不会这样说"
用户: "我遇到这种情况会先沉默很久"
        ↓
系统识别 correction 意图
        ↓
判断属于 Self Memory 还是 Persona 的纠正
        ↓
写入对应文件的 Correction 层
        ↓
立即生效，后续交互以新规则为准
```

### 版本管理

- 每次更新自动存档当前版本到 `versions/`
- 支持通过 `create-yourself` skill 回滚到指定版本
- 保留最近 10 个版本

---

## 项目结构

```
create-yourself/                    # meta-skill
│
├── SKILL.md                         # 主入口
│                                    # 触发词: $create-yourself
│
├── prompts/                         # Prompt 模板
│   ├── intake.md                    # 引导录入
│   ├── self_analyzer.md             # 自我记忆提取
│   ├── persona_analyzer.md          # 性格行为提取
│   ├── self_builder.md              # self.md 模板
│   ├── persona_builder.md           # persona.md 模板
│   ├── merger.md                    # 增量 merge
│   └── correction_handler.md        # 对话纠正
│
├── tools/                           # 工具脚本
│   ├── wechat_parser.py             # 微信记录解析
│   ├── qq_parser.py                 # QQ 记录解析
│   ├── social_parser.py             # 社交媒体解析
│   ├── photo_analyzer.py            # 照片 EXIF 分析
│   ├── skill_writer.py              # 文件管理
│   └── version_manager.py           # 版本管理
│
selves/{slug}/                      # 生成的自我 Skill（可直接运行）
│       ├── SKILL.md                 # 完整组合版
│       ├── self.md                  # Part A：自我记忆
│       ├── persona.md               # Part B：人格
│       ├── meta.json                # 元数据
│       ├── versions/                # 历史版本
│       └── memories/                # 原始材料
│           ├── chats/
│           ├── photos/
│           └── notes/
│
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## 关键文件格式

### `selves/{slug}/meta.json`

```json
{
  "name": "小北",
  "slug": "xiaobei",
  "created_at": "2026-04-01T10:00:00Z",
  "updated_at": "2026-04-01T12:00:00Z",
  "version": "v3",
  "profile": {
    "age": "25",
    "occupation": "产品经理",
    "city": "上海",
    "gender": "男",
    "mbti": "INTJ",
    "zodiac": "摩羯座"
  },
  "tags": {
    "personality": ["社恐但话痨", "深夜emo型", "纠结体"],
    "lifestyle": ["咖啡依赖", "仪式感狂热者"]
  },
  "impression": "对自己要求很高，但总是拖到最后一刻才行动",
  "memory_sources": [
    "memories/chats/wechat_2024_export.txt",
    "memories/notes/2025_diary.md",
    "memories/photos/travel_2023/"
  ],
  "corrections_count": 2
}
```

### `selves/{slug}/SKILL.md` 结构

```markdown
---
name: self_{slug}
description: {name}，{age}岁，{occupation}，{city}
user-invocable: true
---

# {name}

{age}岁，{occupation}，{city}

---

## PART A：自我记忆

{self.md 内容}

---

## PART B：人物性格

{persona.md 内容}

---

## 运行规则

接收到任何消息时：
1. 先用 PART B 判断：你会怎么回应？什么态度？
2. 再用 PART A 补充：结合你的经历和价值观
3. 输出时始终保持 PART B 的表达风格
4. PART B Layer 0 规则优先级最高，任何情况下不得违背
```

---

## 实现优先级

### P0 — MVP
- [x] `create-yourself/SKILL.md` 主流程
- [x] `prompts/intake.md`
- [x] `prompts/self_analyzer.md` + `self_builder.md`
- [x] `prompts/persona_analyzer.md` + `persona_builder.md`
- [x] `tools/skill_writer.py`
- [x] `tools/version_manager.py`

### P1 — 数据接入
- [x] `tools/wechat_parser.py`
- [x] `tools/qq_parser.py`
- [x] `tools/social_parser.py`
- [x] `tools/photo_analyzer.py`

### P2 — 进化机制
- [x] `prompts/correction_handler.md`
- [x] `prompts/merger.md`

### P3 — 管理功能
- [x] 通过 `create-yourself` skill 列表 / 回滚 / 删除
