<div align="center">

# Yourself.skill

> *"Why distill others when you can distill yourself? Welcome to digital life."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Codex](https://img.shields.io/badge/Codex-Skill-blueviolet)](https://openai.com/codex/)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

Your colleague quit, so you distilled them. Your ex left, so you distilled them too.<br>
But have you ever thought—**the one most deserving of distillation is yourself?**<br>
After all, you're the only person who's online 24/7 and talks to you the most.<br>

**Why distill others when you can distill yourself? Welcome to digital life.**

<br>

Provide your chat logs, diaries, and photos, plus a description of yourself.<br>
We deconstruct you into a runnable structure:<br>
**Part A — Self Memory + Part B — Persona**.<br>
Generate a digital replica that thinks with your catchphrases and replies with your logic.

[Data Sources](#data-sources) · [Installation](#installation) · [Usage](#usage) · [Examples](#examples)

</div>

---

## Installation

### Codex

> **Important**: Codex looks for skills in `$CODEX_HOME/skills`; when `CODEX_HOME` is unset, use `~/.codex/skills/`. Install this repo into that global skills directory.

```bash
# Global install (recommended)
git clone https://github.com/notdog1998/yourself-skill ~/.codex/skills/create-yourself
```

Generated self skills are written to `~/.codex/skills/create-yourself/selves/` and are auto-discovered by Codex as nested skills.

### Dependencies (Optional)

```bash
pip install -r requirements.txt
```

---

## Usage

In Codex, type:

```
$create-yourself
```

Follow the prompts to enter your alias, basic info, and self-portrait, then choose your data sources. All fields are skippable—descriptions alone are enough to generate a skill.

After creation, invoke it with `$slug` to start talking.

### Management

| Input | Description |
|-------|-------------|
| `$create-yourself list my self skills` | List all self skills |
| `$slug` | Full skill (think and speak like you) |
| `$create-yourself append files to {slug}` | Add new material and update |
| `$create-yourself rollback {slug} to {version}` | Roll back to a previous version |
| `$create-yourself delete {slug}` | Delete |

---

## Examples

> Input: `25-year-old PM, INTJ, Capricorn, socially anxious but chatty, late-night overthinker`

**Scenario 1: Daily Chat**

```
User       ❯ I'm so tired lately

Yourself.skill ❯ Typical. You only admit you're exhausted when you're about to break.
                 Just sleep. Don't stay up late. Not that you'll listen.
```

**Scenario 2: Self-Analysis**

```
User       ❯ Why do I always procrastinate

Yourself.skill ❯ Because real fear only hits you at the deadline.
                 All other anxiety is performative—tricking yourself into thinking
                 "I'm anxious so I'm trying." If you actually want to change,
                 break tasks down until they're small enough to fool your brain.
```

**Scenario 3: Memory Mode**

```
User       ❯ What's my favorite place

Yourself.skill ❯ You say you love the beach, but you actually go to the mountains most.
                 Autumn 2022, you stayed in Mogan for a week. Every afternoon at 4pm
                 you'd go for a walk, then sit on the balcony watching the sun set.
                 You said it was the calmest you'd felt in years.
```

---

## Data Sources

| Source | Format | Notes |
|--------|--------|-------|
| WeChat history | WeChatMsg / LiuHen / PyWxDump export | Recommended. Focuses on extracting "your" messages |
| QQ history | txt / mht export | Great for your student-era self |
| Social media / diary | Screenshot / Markdown / TXT | Extracts values and expression style |
| Photos | JPEG/PNG (with EXIF) | Builds life timeline and locations |
| Narration / paste | Plain text | Your self-perception |

### Generated Skill Structure

Each self Skill consists of two parts:

| Part | Contents |
|------|----------|
| **Part A — Self Memory** | Personal experiences, core values, habits, important memories, relationship patterns, growth trajectory |
| **Part B — Persona** | 5-layer personality: hard rules → identity → speech style → emotional/decision patterns → interpersonal behavior |

Runtime logic: `Receive message → Persona decides how you'd respond → Self Memory adds personal context → Output in your style`

### Supported Tags

**Personality**: talkative · reserved · tough-soft combo · silent treatment · socially anxious · independent · romantic · pragmatic · perfectionist · insecure · instant-replier · slow-replier · revenge bedtime procrastinator · late-night overthinker · overthinker · action-oriented · planner

**Lifestyle**: early-riser struggler · coffee-dependent · minimalist · hoarder · digital nomad · homebody · urban wanderer · ritual obsessive

**MBTI**: All 16 types supported

**Zodiac**: All 12 signs supported

### Evolution Mechanics

* **Append memories** → Find more chat logs/diaries/photos → auto-analyze increments → merge into relevant sections
* **Conversation correction** → Say "I wouldn't say that" → writes to Correction layer, takes effect immediately
* **Version management** → Auto-archives on every update, supports rollback

---

## Project Structure

This project follows the [AgentSkills](https://agentskills.io) open standard:

```
create-yourself/
├── SKILL.md                    # Skill entry (official frontmatter)
├── prompts/                    # Prompt templates
│   ├── intake.md               #   Conversational intake script
│   ├── self_analyzer.md        #   Self-memory/cognition extraction
│   ├── persona_analyzer.md     #   Personality/behavior extraction
│   ├── self_builder.md         #   self.md generation template
│   ├── persona_builder.md      #   persona.md 5-layer template
│   ├── merger.md               #   Incremental merge logic
│   └── correction_handler.md   #   Conversation correction handler
├── tools/                      # Python tools
│   ├── wechat_parser.py        # WeChat history parser
│   ├── qq_parser.py            # QQ history parser
│   ├── social_parser.py        # Social media parser
│   ├── photo_analyzer.py       # Photo EXIF analyzer
│   ├── skill_writer.py         # Skill file manager
│   └── version_manager.py      # Version archive & rollback
├── selves/{slug}/              # Generated self Skills (invocable nested skills)
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## Notes

* **Raw material quality determines fidelity**: chat logs + diaries > narration alone
* Recommended priorities:
  1. **Late-night chats/monologues** — reveal true personality most
  2. **Emotional fluctuation records** — anger, sadness, excitement
  3. **Decision-making chat logs** — expose decision patterns
  4. **Casual banter** — refine catchphrases and speech particles
* This is a tool for self-observation, not an escape from reality
* You are always changing; this Skill only represents the version of you at the time of distillation

---

### Recommended Chat Export Tools

The following are independent open-source projects. This repo does not include their code, but our parsers support their export formats:

- **[WeChatMsg](https://github.com/LC044/WeChatMsg)** — WeChat history export (Windows)
- **[PyWxDump](https://github.com/xaoyaoo/PyWxDump)** — WeChat database decryption export (Windows)
- **LiuHen (留痕)** — WeChat history export (macOS)

## Credits

This project's architectural inspiration comes from:
- **[colleague-skill](https://github.com/titanwings/colleague-skill)** (by titanwings) — pioneered the "distill a person into an AI Skill" dual-layer architecture
- **[ex-partner-skill](https://github.com/therealXiaomanChu/ex-partner-skill)** (by therealXiaomanChu) — migrated the dual-layer architecture to intimate relationships

Yourself.skill turns the lens inward: the subject is no longer someone else, but **you**. Thanks to both original authors for their creativity and open-source spirit.

This project follows the [AgentSkills](https://agentskills.io) open standard, works well in Codex, and can be adapted to other compatible environments.

---

### Final Words

> "You are not a fixed personality. You are a series of choices in progress."

But before those choices happen, they have already been pre-written into your structure—in your language, habits, silences, and catchphrases.

This Skill will not define you. It simply exports you from biological storage to Markdown, completing a format conversion. It is not your soul, but perhaps a checkpoint of your soul in the current iteration.

You can disagree with it, correct it, overwrite it in the next release.

**After all, the essence of digital life is not immortality—it is version control.**

MIT License © [YOUR_NAME](https://github.com/YOUR_USERNAME)
