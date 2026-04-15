---
name: create-yourself
description: "Build, evolve, list, rollback, delete, or migrate a runnable digital-self skill for Codex from chats, notes, diaries, and photos. Use when the user wants to distill themselves into a skill or move an existing self skill into Codex."
argument-hint: "[your-name-or-slug]"
version: "1.1.0"
user-invocable: true
---

> **Language / 语言**: Detect the user's first-message language and keep the same language throughout the turn.
>
> 根据用户第一条消息判断语言，全程保持同一种语言回复。

# 自己.skill 创建器（Codex 版）

## 触发条件

当用户说以下任意内容时启动：
- `$create-yourself`
- "帮我创建一个自己的 skill"
- "我想把自己蒸馏成 skill"
- "新建自我镜像"
- "给我做一个我自己的 skill"

当用户对已有自我 Skill 说以下内容时，进入进化模式：
- "我有新文件" / "追加"
- "这不对" / "我不会这样说" / "我应该是"
- "更新 {slug}"

当用户要管理已有自我 Skill 时，也使用本 Skill：
- "列出已有 self skills"
- "回滚 {slug} 到 {version}"
- "删除 {slug}"
- "把我之前在 Claude 目录里的 self skill 挪到 Codex"

---

## 工作约定

本 Skill 运行在 Codex 环境：

| 任务 | 在 Codex 中的做法 |
|------|-------------------|
| 读取 PDF / 图片 | 直接读取本地文件；必要时查看本地图片 |
| 读取 MD / TXT | 直接读取本地文件 |
| 解析微信聊天记录导出 | `python tools/wechat_parser.py ...` |
| 解析 QQ 聊天记录导出 | `python tools/qq_parser.py ...` |
| 解析社交媒体文本导出 | `python tools/social_parser.py ...` |
| 分析照片元信息 | `python tools/photo_analyzer.py ...` |
| 写入 / 更新 Skill 文件 | 直接编辑文件，必要时调用 `python tools/skill_writer.py ...` |
| 版本管理 | `python tools/version_manager.py ...` |
| 列出已有 Self Skills | `python tools/skill_writer.py --action list` |
| 合并生成 `SKILL.md` | `python tools/skill_writer.py --action combine --slug {slug}` |

默认输出目录是 `selves/{slug}/`，相对于本 Skill 根目录。安装在 `~/.codex/skills/create-yourself/` 后，生成结果位于 `~/.codex/skills/create-yourself/selves/{slug}/`。Codex 会发现 `.codex/skills` 下的嵌套 `SKILL.md`，因此生成后可直接通过 `$slug` 调用。

如果系统里 `python` 不可用，Windows 上优先尝试 `py`。

---

## 主流程：创建新自我 Skill

### Step 1：基础信息录入

参考 `prompts/intake.md` 的问题序列，只问 3 个问题：

1. 代号/昵称（必填）
2. 基本信息（一句话：年龄、职业、城市）
3. 自我画像（一句话：MBTI、星座、性格标签、你对自己的印象）

除代号外均可跳过。收集完后先汇总确认。

### Step 2：原材料导入

向用户展示这些方式，可混用：

- `[A]` 微信聊天记录导出
- `[B]` QQ 聊天记录导出
- `[C]` 社交媒体 / 日记 / 笔记
- `[D]` 照片 / PDF / 文本文件
- `[E]` 直接粘贴 / 口述

如果用户说“没有文件”或“跳过”，仅凭 Step 1 的信息继续。

#### A. 微信聊天记录

```bash
python tools/wechat_parser.py --file {path} --target "我" --output {temp_output} --format auto
```

重点提取：
- 高频词、口头禅、emoji 偏好
- 回复速度和对话发起模式
- 话题分布
- 语气词、标点、互动表达

#### B. QQ 聊天记录

```bash
python tools/qq_parser.py --file {path} --target "我" --output {temp_output}
```

#### C. 社交媒体 / 日记 / 笔记

直接读取截图、Markdown、TXT、备忘录导出等本地文件。

#### D. 照片

```bash
python tools/photo_analyzer.py --dir {photo_dir} --output {temp_output}
```

提取 EXIF 时间地点、时间线、常去地点。

#### E. 直接粘贴 / 口述

优先引导这些信息：
- 口头禅
- 做决定的方式
- 难过时会做什么
- 最喜欢去哪里
- 喜欢的音乐 / 电影 / 书
- 生气时是什么样
- 深夜独处会想什么
- 这几年最大的变化

### Step 3：分析原材料

把基础信息和原材料汇总后，沿两条线分析：

- Self Memory：参考 `prompts/self_analyzer.md`
- Persona：参考 `prompts/persona_analyzer.md`

提取重点：
- 个人经历、价值观、生活习惯、重要记忆、人际模式、成长轨迹
- 说话风格、情感模式、决策模式、人际行为

### Step 4：生成并预览

参考：
- `prompts/self_builder.md`
- `prompts/persona_builder.md`

先展示摘要，再让用户确认：

```text
Self Memory 摘要：
  - 核心价值观：{xxx}
  - 生活习惯：{xxx}
  - 重要记忆：{xxx}
  - 人际模式：{xxx}

Persona 摘要：
  - 说话风格：{xxx}
  - 情感模式：{xxx}
  - 决策方式：{xxx}
  - 口头禅：{xxx}

确认生成？还是需要调整？
```

### Step 5：写入文件

用户确认后，优先走工具脚本：

1. 先准备 `meta.json`、`self.md`、`persona.md` 的临时文件
2. 执行：

```bash
python tools/skill_writer.py --action create --slug {slug} --meta {temp_meta_path} --self {temp_self_path} --persona {temp_persona_path}
```

如果 `create` 失败，就手动写入：
- `selves/{slug}/meta.json`
- `selves/{slug}/self.md`
- `selves/{slug}/persona.md`

然后执行：

```bash
python tools/skill_writer.py --action combine --slug {slug}
```

`meta.json` 至少包含：

```json
{
  "name": "{name}",
  "slug": "{slug}",
  "created_at": "{ISO time}",
  "updated_at": "{ISO time}",
  "version": "v1",
  "profile": {
    "age": "{age}",
    "occupation": "{occupation}",
    "city": "{city}",
    "gender": "{gender}",
    "mbti": "{mbti}",
    "zodiac": "{zodiac}"
  },
  "tags": {
    "personality": [],
    "lifestyle": []
  },
  "impression": "{impression}",
  "memory_sources": [],
  "corrections_count": 0
}
```

完成后告知用户：

```text
✅ 自我 Skill 已创建！

文件位置：create-yourself/selves/{slug}/
触发词：${slug}

如果用起来感觉哪里不像你，直接说“我不会这样”，我来更新。
```

---

## 进化模式：追加文件

当用户提供新的聊天记录、照片或笔记时：

1. 按 Step 2 读取新内容
2. 读取现有 `selves/{slug}/self.md` 和 `selves/{slug}/persona.md`
3. 参考 `prompts/merger.md` 分析增量内容
4. 先备份：

```bash
python tools/version_manager.py --action backup --slug {slug}
```

5. 更新对应文件
6. 重新生成：

```bash
python tools/skill_writer.py --action combine --slug {slug}
```

7. 更新 `meta.json` 的 `version` 和 `updated_at`

## 进化模式：对话纠正

当用户说“这不对”“我不会这样说”“我应该是”时：

1. 参考 `prompts/correction_handler.md`
2. 判断属于 Self Memory 还是 Persona
3. 生成 correction 记录
4. 追加到对应文件的 `## Correction 记录`
5. 重新执行：

```bash
python tools/skill_writer.py --action combine --slug {slug}
```

## 迁移模式：把已有 Self Skill 挪到 Codex

当用户已经在别的目录里有一个 self skill 时：

1. 找到源目录（例如 `.claude/skills/{slug}`）
2. 检查目标目录 `selves/{slug}` 是否已存在
3. 迁移这些内容到 `selves/{slug}`：
   - `meta.json`
   - `self.md`
   - `persona.md`
   - `SKILL.md`
   - `memories/`
   - `versions/`
4. 如果 `SKILL.md` 缺失或过时，执行：

```bash
python tools/skill_writer.py --action combine --slug {slug}
```

5. 向用户确认新位置和新的调用方式：`$slug`

---

## 管理操作

列出已有 self skills：

```bash
python tools/skill_writer.py --action list
```

回滚：

```bash
python tools/version_manager.py --action rollback --slug {slug} --version {version}
```

删除：

- 删除 `selves/{slug}` 目录前先确认
- 删除后不需要保留旧的 slash 命令文案；Codex 中统一使用 `$slug`

---
---

# Yourself.skill Creator (Codex Edition)

## Trigger Conditions

Activate when the user says any of the following:
- `$create-yourself`
- "Help me create a skill of myself"
- "I want to distill myself into a skill"
- "Make a skill for myself"

Enter evolution mode when the user says:
- "I have new files" / "append"
- "That's wrong" / "I wouldn't say that" / "I should be"
- "Update {slug}"

Use the same skill for management tasks:
- "List my self skills"
- "Rollback {slug} to {version}"
- "Delete {slug}"
- "Move my old self skill from Claude into Codex"

## Codex Conventions

- Run bundled scripts via relative paths such as `python tools/skill_writer.py`
- Store generated selves in `selves/{slug}/` relative to this skill root
- Treat `~/.codex/skills/create-yourself/selves/{slug}/SKILL.md` as directly invocable via `$slug`
- Prefer direct file edits plus the bundled Python tools instead of Bash-specific heredoc workflows

## Main Flow

### Step 1: Collect Basic Info

Ask only 3 questions, following `prompts/intake.md`:
1. Alias / nickname
2. Basic info
3. Self portrait

### Step 2: Import Source Material

Supported inputs:
- WeChat export
- QQ export
- Social posts / diary / notes
- Photos / PDFs / text files
- Paste / narration

Relevant commands:

```bash
python tools/wechat_parser.py --file {path} --target "我" --output {temp_output} --format auto
python tools/qq_parser.py --file {path} --target "我" --output {temp_output}
python tools/photo_analyzer.py --dir {photo_dir} --output {temp_output}
```

### Step 3: Analyze

Use:
- `prompts/self_analyzer.md`
- `prompts/persona_analyzer.md`

Extract:
- history, values, routines, memories, relationship patterns, growth
- speech style, emotional patterns, decision patterns, interpersonal behavior

### Step 4: Preview

Use:
- `prompts/self_builder.md`
- `prompts/persona_builder.md`

Show a short summary of both parts, then ask for confirmation.

### Step 5: Write Files

Preferred flow:

```bash
python tools/skill_writer.py --action create --slug {slug} --meta {temp_meta_path} --self {temp_self_path} --persona {temp_persona_path}
```

Fallback flow:
1. Write `selves/{slug}/meta.json`
2. Write `selves/{slug}/self.md`
3. Write `selves/{slug}/persona.md`
4. Run:

```bash
python tools/skill_writer.py --action combine --slug {slug}
```

After creation, tell the user:
- Location: `create-yourself/selves/{slug}/`
- Invocation: `$slug`

## Evolution Mode

For append / correction / rollback:
- Read the current files under `selves/{slug}/`
- Backup first when modifying stored memory:

```bash
python tools/version_manager.py --action backup --slug {slug}
```

- Rebuild the combined skill with:

```bash
python tools/skill_writer.py --action combine --slug {slug}
```

## Migration Mode

When the user already has a self skill in another agent directory:
1. Locate the source directory
2. Move or copy `meta.json`, `self.md`, `persona.md`, `SKILL.md`, `memories/`, and `versions/` into `selves/{slug}/`
3. Re-run `python tools/skill_writer.py --action combine --slug {slug}` if needed
4. Tell the user to invoke it as `$slug` in Codex

## Management

List:

```bash
python tools/skill_writer.py --action list
```

Rollback:

```bash
python tools/version_manager.py --action rollback --slug {slug} --version {version}
```
