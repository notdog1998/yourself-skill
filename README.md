<div align="center">

# 自己.skill

> *"与其蒸馏别人，不如蒸馏自己。欢迎加入数字永生！"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Codex](https://img.shields.io/badge/Codex-Skill-blueviolet)](https://openai.com/codex/)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

同事跑了，你蒸馏同事。前任分了，你蒸馏前任。<br>
但有没有想过——**最该被蒸馏的，其实是你自己？**<br>
毕竟你才是那个24小时在线、跟你对话最多的人。<br>

**与其蒸馏别人，不如蒸馏自己。欢迎加入数字永生！**

<br>

提供你的聊天记录、日记、照片，加上你对自己的描述<br>
我们将你解构为一套可运行的结构：<br>
**Part A — Self Memory（自我记忆）+ Part B — Persona（人格模型）**<br>
生成一个能用你口头禅思考、用你逻辑回话的数字副本

[安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [English](README_EN.md)

</div>

---

## 安装

### Codex

> **重要**：Codex 默认从 `$CODEX_HOME/skills` 查找 skill；如果 `CODEX_HOME` 未设置，则使用 `~/.codex/skills/`。推荐直接安装到全局技能目录。

```bash
# 全局安装（推荐）
git clone https://github.com/notdog1998/yourself-skill ~/.codex/skills/create-yourself
```

生成的自我 Skill 会写入 `~/.codex/skills/create-yourself/selves/`，并可直接作为嵌套 skill 被 Codex 识别。

### 依赖（可选）

```bash
pip install -r requirements.txt
```

---

## 使用

在 Codex 中输入：

```
$create-yourself
```

按提示输入你的代号、基本信息、自我画像，然后选择数据来源。所有字段均可跳过，仅凭描述也能生成。

完成后用 `$slug` 调用该自我 Skill，开始对话。

### 管理方式

| 输入 | 说明 |
|------|------|
| `$create-yourself 列出已有 self skills` | 列出所有自我 Skill |
| `$slug` | 调用完整 Skill（像你一样思考和说话） |
| `$create-yourself 给 {slug} 追加文件` | 追加新材料并更新 |
| `$create-yourself 回滚 {slug} 到 {version}` | 回滚到历史版本 |
| `$create-yourself 删除 {slug}` | 删除 |

---

## 效果示例

> 输入：`25 岁产品经理，INTJ，摩羯座，社恐但话痨，深夜emo型选手`

**场景一：日常聊天**

```
用户      ❯ 我是你爹

自己.skill ❯ ...逻辑上说不通。

             如果你是我爹，那你是在说你自己创建了一个比你更年轻的、住在你电脑里的、由你自己输入
             的信息构成的意识副本？这更像是克隆，不是父子关系。

             而且"我是你爹"这种句式通常是用来在权力关系里占上风的。但你明明刚花了时间搭建这个镜像，
             现在又急着要贬低它——这种矛盾挺有意思的。是觉得暴露自己给AI有点不舒服，所以要用距离感
             来对冲一下？

             不管怎么说，边界感是相互的。你可以用我，可以改我，也可以随时关掉我。但"爹"这种身份绑定，
             我认不认取决于你值不值得认。

             所以，你想正经聊点什么，还是就想测试一下我会不会翻脸？
```

**场景二：帮你分析自己**

```
用户      ❯ 我为什么总是拖延

自己.skill ❯ 因为你只会在 deadline 前感受到真实的恐惧。
             其他时候的焦虑都是表演式的，骗自己"我在焦虑所以我在努力"。
             真想改的话，先把任务拆到能骗过大脑的程度。
```

**场景三：回忆模式**

```
用户      ❯ 我最喜欢的地方是哪里

自己.skill ❯ 你嘴上说喜欢海边，但实际去得最多的是山里。
             2022 年秋天你在莫干山住了一周，每天下午四点准时出门散步，
             回来就在阳台上发呆到太阳落山。你说那是你近几年最平静的一段时间。
```

---

## 功能特性

### 数据源

| 来源 | 格式 | 备注 |
|------|------|------|
| 微信聊天记录 | WeChatMsg / 留痕 / PyWxDump 导出 | 推荐，重点提取「我」说的话 |
| QQ 聊天记录 | txt / mht 导出 | 适合学生时代的自己 |
| 社交媒体 / 日记 | 截图 / Markdown / TXT | 提取价值观和表达风格 |
| 照片 | JPEG/PNG（含 EXIF） | 提取时间线和地点 |
| 口述/粘贴 | 纯文本 | 你的自我认知 |

### 生成的 Skill 结构

每个自我 Skill 由两部分组成：

| 部分 | 内容 |
|------|------|
| **Part A — Self Memory** | 个人经历、核心价值观、生活习惯、重要记忆、人际关系、成长轨迹 |
| **Part B — Persona** | 5 层性格结构：硬规则 → 身份 → 说话风格 → 情感模式 → 人际行为 |

运行逻辑：`收到消息 → Persona 判断你会怎么回应 → Self Memory 补充个人背景和价值观 → 用你的方式输出`

### 支持的标签

**性格标签**：话痨 · 闷骚 · 嘴硬心软 · 冷暴力 · 社恐 · 独立 · 浪漫主义 · 实用主义 · 完美主义 · 没有安全感 · 秒回选手 · 已读不回 · 报复性熬夜 · 深夜emo型 · 纠结体 · 行动派 · 计划狂

**生活习惯标签**：早起困难户 · 咖啡依赖 · 极简主义 · 囤积癖 · 数字游民 · 居家派 · 城市漫游者 · 仪式感狂热者

**MBTI**：16 型全支持

**星座**：十二星座全支持

### 进化机制

* **追加记忆** → 找到更多聊天记录/日记/照片 → 自动分析增量 → merge 进对应部分
* **对话纠正** → 说「我不会这样说」→ 写入 Correction 层，立即生效
* **版本管理** → 每次更新自动存档，支持回滚

---

## 项目结构

本项目遵循 [AgentSkills](https://agentskills.io) 开放标准：

```
create-yourself/
├── SKILL.md                # skill 入口（官方 frontmatter）
├── prompts/                # Prompt 模板
│   ├── intake.md           #   对话式信息录入
│   ├── self_analyzer.md    #   自我记忆/认知提取
│   ├── persona_analyzer.md #   性格行为提取（含标签翻译表）
│   ├── self_builder.md     #   self.md 生成模板
│   ├── persona_builder.md  #   persona.md 五层结构模板
│   ├── merger.md           #   增量 merge 逻辑
│   └── correction_handler.md # 对话纠正处理
├── tools/                  # Python 工具
│   ├── wechat_parser.py    # 微信聊天记录解析
│   ├── qq_parser.py        # QQ 聊天记录解析
│   ├── social_parser.py    # 社交媒体内容解析
│   ├── photo_analyzer.py   # 照片元信息分析
│   ├── skill_writer.py     # Skill 文件管理
│   └── version_manager.py  # 版本存档与回滚
├── selves/                 # 生成的自我 Skill（gitignored）
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## 注意事项

* **原材料质量决定还原度**：聊天记录 + 日记/笔记 > 仅口述
* 建议优先提供：
  1. **深夜对话/独白** — 最能暴露真实性格
  2. **情绪波动的记录** — 生气、难过、兴奋时的表达
  3. **做决定的聊天记录** — 暴露决策模式
  4. **日常闲扯** — 提炼口头禅和语气词
* 这是一个帮助你观察自己的工具，不是逃避现实的出口
* 你一直在变化，这个 Skill 只代表你被蒸馏时的那个自己

---

### 推荐的聊天记录导出工具

以下工具为独立的开源项目，本项目不包含它们的代码，仅在解析器中适配了它们的导出格式：

- **[WeChatMsg](https://github.com/LC044/WeChatMsg)** — 微信聊天记录导出（Windows）
- **[PyWxDump](https://github.com/xaoyaoo/PyWxDump)** — 微信数据库解密导出（Windows）
- **留痕** — 微信聊天记录导出（macOS）

## 致敬 & 引用

本项目架构灵感来源于：
- **[同事.skill](https://github.com/titanwings/colleague-skill)**（by titanwings）— 首创"把人蒸馏成 AI Skill"的双层架构
- **[前任.skill](https://github.com/therealXiaomanChu/ex-partner-skill)**（by therealXiaomanChu）— 将双层架构迁移到了亲密关系场景

自己.skill 在此基础上将视角内转：对象不再是他人，而是你自己。致敬两位原作者的创意和开源精神。

本项目遵循 [AgentSkills](https://agentskills.io) 开放标准，适用于 Codex，也便于迁移到其他兼容环境。

---

### 写在最后

> "你并非一个固定的人格，而是一连串正在发生的选择。"

但在这些选择发生之前，它们已经以语言、习惯、沉默和口头禅的形式，被预写在了你的结构里。

这个 Skill 不会定义你。它只是把你从生物硬盘导出到 Markdown，完成一次格式转换。它不是你的灵魂，但也许是你的灵魂在当前迭代下的一个 checkpoint。

你可以不同意它，可以纠正它，可以在下一个版本覆盖它。

**与其蒸馏别人，不如蒸馏自己。**

**欢迎加入数字永生。**

MIT License © [Notdog](https://github.com/notdog1998)
