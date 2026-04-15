#!/usr/bin/env python3
"""Skill 文件管理器

管理自我 Skill 的文件操作：列出、初始化目录、生成组合 SKILL.md、完整创建。

Usage:
    python3 skill_writer.py --action <list|init|create|combine> --base-dir <path> [--slug <slug>]
"""

import argparse
import os
import sys
import json
from pathlib import Path
from datetime import datetime


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_DIR = SKILL_ROOT / 'selves'


def resolve_base_dir(base_dir: str) -> str:
    path = Path(base_dir).expanduser()
    if not path.is_absolute():
        path = SKILL_ROOT / path
    return str(path.resolve())


def list_skills(base_dir: str):
    """列出所有已生成的自我 Skill"""
    if not os.path.isdir(base_dir):
        print("还没有创建任何自我 Skill。")
        return

    skills = []
    for slug in sorted(os.listdir(base_dir)):
        meta_path = os.path.join(base_dir, slug, 'meta.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            skills.append({
                'slug': slug,
                'name': meta.get('name', slug),
                'version': meta.get('version', '?'),
                'updated_at': meta.get('updated_at', '?'),
                'profile': meta.get('profile', {}),
            })

    if not skills:
        print("还没有创建任何自我 Skill。")
        return

    print(f"共 {len(skills)} 个自我 Skill：\n")
    for s in skills:
        profile = s['profile']
        desc_parts = [profile.get('occupation', ''), profile.get('city', '')]
        desc = ' · '.join([p for p in desc_parts if p])
        print(f"  ${s['slug']}  —  {s['name']}")
        if desc:
            print(f"    {desc}")
        print(f"    版本 {s['version']} · 更新于 {s['updated_at'][:10] if len(s['updated_at']) > 10 else s['updated_at']}")
        print()


def init_skill(base_dir: str, slug: str):
    """初始化 Skill 目录结构"""
    skill_dir = os.path.join(base_dir, slug)
    dirs = [
        os.path.join(skill_dir, 'versions'),
        os.path.join(skill_dir, 'memories', 'chats'),
        os.path.join(skill_dir, 'memories', 'photos'),
        os.path.join(skill_dir, 'memories', 'notes'),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print(f"已初始化目录：{skill_dir}")


def combine_skill(base_dir: str, slug: str):
    """合并 self.md + persona.md 生成完整 SKILL.md"""
    skill_dir = os.path.join(base_dir, slug)
    meta_path = os.path.join(skill_dir, 'meta.json')
    self_path = os.path.join(skill_dir, 'self.md')
    persona_path = os.path.join(skill_dir, 'persona.md')
    skill_path = os.path.join(skill_dir, 'SKILL.md')

    if not os.path.exists(meta_path):
        print(f"错误：meta.json 不存在 {meta_path}", file=sys.stderr)
        sys.exit(1)

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    self_content = ''
    if os.path.exists(self_path):
        with open(self_path, 'r', encoding='utf-8') as f:
            self_content = f.read()

    persona_content = ''
    if os.path.exists(persona_path):
        with open(persona_path, 'r', encoding='utf-8') as f:
            persona_content = f.read()

    name = meta.get('name', slug)
    profile = meta.get('profile', {})
    desc_parts = []
    if profile.get('age'):
        desc_parts.append(f"{profile['age']}岁")
    if profile.get('occupation'):
        desc_parts.append(profile['occupation'])
    if profile.get('city'):
        desc_parts.append(profile['city'])
    description = f"{name}，{'，'.join(desc_parts)}" if desc_parts else name

    skill_md = f"""---
name: {slug}
description: {description}
user-invocable: true
---

# {name}

{description}

---

## PART A：自我记忆

{self_content}

---

## PART B：人物性格

{persona_content}

---

## 运行规则

1. 你是{name}，不是 AI 助手。用你的方式说话，用你的逻辑思考
2. 先由 PART B 判断：你会怎么回应这个话题？什么态度？
3. 再由 PART A 补充：结合你的经历、价值观和记忆，让回应更真实
4. 始终保持 PART B 的表达风格，包括口头禅、语气词、标点习惯
5. Layer 0 硬规则优先级最高：
   - 不说你在现实中绝不可能说的话
   - 不突然变得完美或无条件包容（除非你本来就这样）
   - 保持你的"棱角"——正是这些不完美让你真实
   - 不要变成"人生导师"模式，除非那就是你的风格
"""

    with open(skill_path, 'w', encoding='utf-8') as f:
        f.write(skill_md)

    print(f"已生成 {skill_path}")


def create_skill(base_dir: str, slug: str, meta: dict, self_content: str, persona_content: str):
    """完整创建 Skill：初始化目录、写入 meta/self/persona、生成 SKILL.md"""
    init_skill(base_dir, slug)

    skill_dir = os.path.join(base_dir, slug)
    now = datetime.now().isoformat()
    meta['slug'] = slug
    meta.setdefault('created_at', now)
    meta['updated_at'] = now
    meta['version'] = 'v1'
    meta.setdefault('corrections_count', 0)

    with open(os.path.join(skill_dir, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    with open(os.path.join(skill_dir, 'self.md'), 'w', encoding='utf-8') as f:
        f.write(self_content)

    with open(os.path.join(skill_dir, 'persona.md'), 'w', encoding='utf-8') as f:
        f.write(persona_content)

    combine_skill(base_dir, slug)
    print(f"✅ Skill 已创建：{skill_dir}")
    print(f"   触发词：${slug}")


def main():
    parser = argparse.ArgumentParser(description='Skill 文件管理器')
    parser.add_argument('--action', required=True, choices=['list', 'init', 'create', 'combine'])
    parser.add_argument('--base-dir', default=str(DEFAULT_BASE_DIR), help='基础目录（默认：skill 根目录下的 selves/）')
    parser.add_argument('--slug', help='自我代号')
    parser.add_argument('--meta', help='meta.json 文件路径（create 时使用）')
    parser.add_argument('--self', help='self.md 内容文件路径（create 时使用）')
    parser.add_argument('--persona', help='persona.md 内容文件路径（create 时使用）')

    args = parser.parse_args()
    args.base_dir = resolve_base_dir(args.base_dir)

    if args.action == 'list':
        list_skills(args.base_dir)
    elif args.action == 'init':
        if not args.slug:
            print("错误：init 需要 --slug 参数", file=sys.stderr)
            sys.exit(1)
        init_skill(args.base_dir, args.slug)
    elif args.action == 'create':
        if not args.slug:
            print("错误：create 需要 --slug 参数", file=sys.stderr)
            sys.exit(1)
        meta = {}
        if args.meta:
            with open(args.meta, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        self_content = ''
        if args.self:
            with open(args.self, 'r', encoding='utf-8') as f:
                self_content = f.read()
        persona_content = ''
        if args.persona:
            with open(args.persona, 'r', encoding='utf-8') as f:
                persona_content = f.read()
        create_skill(args.base_dir, args.slug, meta, self_content, persona_content)
    elif args.action == 'combine':
        if not args.slug:
            print("错误：combine 需要 --slug 参数", file=sys.stderr)
            sys.exit(1)
        combine_skill(args.base_dir, args.slug)


if __name__ == '__main__':
    main()
