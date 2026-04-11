#!/usr/bin/env python3
"""MBTI 人格测试工具

基于荣格心理类型理论的标准 MBTI 测试，包含 60 道题目，覆盖四个维度：
- E/I：外向（Extraversion）- 内向（Introversion）
- S/N：感觉（Sensing）- 直觉（Intuition）
- T/F：思考（Thinking）- 情感（Feeling）
- J/P：判断（Judging）- 知觉（Perceiving）

Usage:
    交互式测试:
        python3 tools/mbti_test.py --slug <slug> --mode interactive

    从 JSON 文件导入结果:
        python3 tools/mbti_test.py --slug <slug> --mode file --input answers.json

    仅生成报告模板:
        python3 tools/mbti_test.py --slug <slug> --mode template
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

MBTI_QUESTIONS = [
    {"id": 1, "dimension": "E/I", "direction": "I", "text": "在社交聚会中，你通常会主动与很多人攀谈，还是只与少数熟悉的人交流？A. 主动与很多人交流 B. 只与少数熟悉的人交流"},
    {"id": 2, "dimension": "E/I", "direction": "E", "text": "你更喜欢团队合作还是独立工作？A. 团队合作 B. 独立工作"},
    {"id": 3, "dimension": "E/I", "direction": "I", "text": "周末休息时，你更倾向于出门参加活动还是在家独处？A. 出门参加活动 B. 在家独处"},
    {"id": 4, "dimension": "E/I", "direction": "E", "text": "打电话给陌生人时，你通常感到自然还是有些紧张？A. 自然 B. 有些紧张"},
    {"id": 5, "dimension": "E/I", "direction": "I", "text": "你更喜欢表达自己的想法还是倾听他人的意见？A. 表达自己的想法 B. 倾听他人的意见"},
    {"id": 6, "dimension": "E/I", "direction": "E", "text": "在人群中你通常是注意力的中心还是尽量不引人注意？A. 注意力中心 B. 尽量不引人注意"},
    {"id": 7, "dimension": "E/I", "direction": "I", "text": "长时间社交后你需要独处来恢复精力吗？A. 不需要 B. 需要"},
    {"id": 8, "dimension": "E/I", "direction": "E", "text": "你说话的速度比较快还是比较慢？A. 比较快 B. 比较慢"},
    {"id": 9, "dimension": "E/I", "direction": "I", "text": "你更倾向于先思考再说话还是边说边想？A. 边说边想 B. 先思考再说话"},
    {"id": 10, "dimension": "E/I", "direction": "E", "text": "你喜欢热闹的环境还是安静的环境？A. 热闹的环境 B. 安静的环境"},
    {"id": 11, "dimension": "E/I", "direction": "I", "text": "朋友通常形容你为外向还是内向？A. 外向 B. 内向"},
    {"id": 12, "dimension": "E/I", "direction": "E", "text": "你更容易在与人交流中获得能量还是在独处中？A. 与人交流中 B. 独处中"},
    {"id": 13, "dimension": "E/I", "direction": "I", "text": "你倾向于广交朋友还是深交少数人？A. 广交朋友 B. 深交少数人"},
    {"id": 14, "dimension": "E/I", "direction": "E", "text": "你更喜欢参加派对还是小型聚会？A. 派对 B. 小型聚会"},
    {"id": 15, "dimension": "E/I", "direction": "I", "text": "遇到问题时你更倾向于自己解决还是找人讨论？A. 找人讨论 B. 自己解决"},
    {"id": 16, "dimension": "S/N", "direction": "N", "text": "你更关注事物的实际细节还是未来的可能性？A. 实际细节 B. 未来可能性"},
    {"id": 17, "dimension": "S/N", "direction": "S", "text": "你更擅长处理具体的事实还是抽象的概念？A. 具体事实 B. 抽象概念"},
    {"id": 18, "dimension": "S/N", "direction": "N", "text": "你更喜欢按常规方式做事还是尝试新方法？A. 常规方式 B. 尝试新方法"},
    {"id": 19, "dimension": "S/N", "direction": "S", "text": "你更相信亲身经验还是直觉灵感？A. 亲身经验 B. 直觉灵感"},
    {"id": 20, "dimension": "S/N", "direction": "N", "text": "你更注重实用性还是创新性？A. 实用性 B. 创新性"},
    {"id": 21, "dimension": "S/N", "direction": "S", "text": "你更喜欢执行具体任务还是进行头脑风暴？A. 执行具体任务 B. 头脑风暴"},
    {"id": 22, "dimension": "S/N", "direction": "N", "text": "你更倾向于看重大局还是关注细节？A. 关注细节 B. 看重大局"},
    {"id": 23, "dimension": "S/N", "direction": "S", "text": "你更擅长总结经验还是提出新想法？A. 总结经验 B. 提出新想法"},
    {"id": 24, "dimension": "S/N", "direction": "N", "text": "你更喜欢处理已知的事物还是探索未知的领域？A. 已知事物 B. 未知领域"},
    {"id": 25, "dimension": "S/N", "direction": "S", "text": "你更注重现实情况还是理论假设？A. 现实情况 B. 理论假设"},
    {"id": 26, "dimension": "S/N", "direction": "N", "text": "你更擅长观察细节还是发现规律？A. 观察细节 B. 发现规律"},
    {"id": 27, "dimension": "S/N", "direction": "S", "text": "你更喜欢循序渐进还是跳跃式思考？A. 循序渐进 B. 跳跃式思考"},
    {"id": 28, "dimension": "S/N", "direction": "N", "text": "你更倾向于务实还是有想象力？A. 务实 B. 有想象力"},
    {"id": 29, "dimension": "S/N", "direction": "S", "text": "你更善于模仿还是创造？A. 模仿 B. 创造"},
    {"id": 30, "dimension": "S/N", "direction": "N", "text": "你更重视稳定还是变化？A. 稳定 B. 变化"},
    {"id": 31, "dimension": "T/F", "direction": "F", "text": "做决定时你更看重逻辑分析还是人情关系？A. 逻辑分析 B. 人情关系"},
    {"id": 32, "dimension": "T/F", "direction": "T", "text": "你更容易注意到别人的逻辑漏洞还是情感需求？A. 逻辑漏洞 B. 情感需求"},
    {"id": 33, "dimension": "T/F", "direction": "F", "text": "批评他人时你会直接指出还是委婉表达？A. 直接指出 B. 委婉表达"},
    {"id": 34, "dimension": "T/F", "direction": "T", "text": "你更倾向于客观公正还是和谐友好？A. 客观公正 B. 和谐友好"},
    {"id": 35, "dimension": "T/F", "direction": "F", "text": "遇到争论时你会坚持原则还是寻求妥协？A. 坚持原则 B. 寻求妥协"},
    {"id": 36, "dimension": "T/F", "direction": "T", "text": "你更擅长解决技术问题还是人际关系问题？A. 技术问题 B. 人际关系问题"},
    {"id": 37, "dimension": "T/F", "direction": "F", "text": "你更容易被感人的故事打动还是被严谨的论证说服？A. 严谨的论证 B. 感人的故事"},
    {"id": 38, "dimension": "T/F", "direction": "T", "text": "你更注重效率还是考虑他人感受？A. 注重效率 B. 考虑他人感受"},
    {"id": 39, "dimension": "T/F", "direction": "F", "text": "你更倾向于理性还是感性？A. 理性 B. 感性"},
    {"id": 40, "dimension": "T/F", "direction": "T", "text": "评价他人时你更看重能力还是品德？A. 能力 B. 品德"},
    {"id": 41, "dimension": "T/F", "direction": "F", "text": "你更容易生气还是容易感动？A. 容易生气 B. 容易感动"},
    {"id": 42, "dimension": "T/F", "direction": "T", "text": "你更善于发现问题还是给予支持？A. 发现问题 B. 给予支持"},
    {"id": 43, "dimension": "T/F", "direction": "F", "text": "你说话比较直接还是比较委婉？A. 比较直接 B. 比较委婉"},
    {"id": 44, "dimension": "T/F", "direction": "T", "text": "你更看重真相还是和谐？A. 真相 B. 和谐"},
    {"id": 45, "dimension": "T/F", "direction": "F", "text": "你更容易同情他人还是保持客观？A. 保持客观 B. 同情他人"},
    {"id": 46, "dimension": "J/P", "direction": "P", "text": "你更喜欢提前规划还是随机应变？A. 提前规划 B. 随机应变"},
    {"id": 47, "dimension": "J/P", "direction": "J", "text": "你做事通常有条不紊还是随性而为？A. 有条不紊 B. 随性而为"},
    {"id": 48, "dimension": "J/P", "direction": "P", "text": "你更倾向于尽快完成任务还是拖延到最后？A. 尽快完成 B. 拖延到最后"},
    {"id": 49, "dimension": "J/P", "direction": "J", "text": "你更喜欢有明确规则还是保持灵活性？A. 明确规则 B. 灵活性"},
    {"id": 50, "dimension": "J/P", "direction": "P", "text": "你更擅长按计划执行还是即兴发挥？A. 按计划执行 B. 即兴发挥"},
    {"id": 51, "dimension": "J/P", "direction": "J", "text": "你更重视准时还是不介意迟到？A. 严格准时 B. 不介意迟到"},
    {"id": 52, "dimension": "J/P", "direction": "P", "text": "你更喜欢确定性还是开放性？A. 确定性 B. 开放性"},
    {"id": 53, "dimension": "J/P", "direction": "J", "text": "你通常把工作放在娱乐之前吗？A. 是的 B. 不是"},
    {"id": 54, "dimension": "J/P", "direction": "P", "text": "你更倾向于做出明确结论还是保持选项开放？A. 明确结论 B. 保持开放"},
    {"id": 55, "dimension": "J/P", "direction": "J", "text": "你更擅长组织管理还是适应变化？A. 组织管理 B. 适应变化"},
    {"id": 56, "dimension": "J/P", "direction": "P", "text": "你喜欢清单和日程表还是讨厌被束缚？A. 喜欢清单日程 B. 讨厌被束缚"},
    {"id": 57, "dimension": "J/P", "direction": "J", "text": "你做事追求完美还是差不多就行？A. 追求完美 B. 差不多就行"},
    {"id": 58, "dimension": "J/P", "direction": "P", "text": "你更喜欢开始项目还是完成项目？A. 完成项目 B. 开始项目"},
    {"id": 59, "dimension": "J/P", "direction": "J", "text": "你更倾向于秩序还是自由？A. 秩序 B. 自由"},
    {"id": 60, "dimension": "J/P", "direction": "P", "text": "你做决定通常比较快还是比较慢？A. 比较快 B. 比较慢"},
]

MBTI_DESCRIPTIONS = {
    "INTJ": {
        "name": "建筑师",
        "summary": "富有想象力和战略性思维的规划者，一切皆在计划之中",
        "traits": ["独立思考", "战略眼光", "高标准", "追求知识", "坚定果断"]
    },
    "INTP": {
        "name": "逻辑学家",
        "summary": "具有创新精神的发明家，对知识有着永不满足的渴望",
        "traits": ["逻辑分析", "好奇心强", "客观公正", "创造力", "善于反思"]
    },
    "ENTJ": {
        "name": "指挥官",
        "summary": "大胆、富有想象力且意志强大的领导者",
        "traits": ["领导能力", "决断力强", "高效直接", "雄心勃勃", "战略思维"]
    },
    "ENTP": {
        "name": "辩论家",
        "summary": "聪明好奇的思想家，不会放过任何智力挑战",
        "traits": ["反应敏捷", "足智多谋", "求知欲强", "打破常规", "魅力四射"]
    },
    "INFJ": {
        "name": "提倡者",
        "summary": "安静而神秘，同时鼓舞人心且不知疲倦的理想主义者",
        "traits": ["富有洞察力", "坚守原则", "利他主义", "创造力", "意志力强"]
    },
    "INFP": {
        "name": "调停者",
        "summary": "诗意、善良的利他主义者，总是热情地为正当理由提供帮助",
        "traits": ["理想主义", "善解人意", "创造力", "真诚开放", "忠于价值观"]
    },
    "ENFJ": {
        "name": "主人公",
        "summary": "富有魅力且鼓舞人心的领导者，有迷住听众的能力",
        "traits": ["感染力强", "善于激励", "责任感强", "利他主义", "影响力大"]
    },
    "ENFP": {
        "name": "竞选者",
        "summary": "热情、有创造力、社交自由的人，总能找到微笑的理由",
        "traits": ["热情洋溢", "想象力丰富", "善于社交", "好奇心强", "精力充沛"]
    },
    "ISTJ": {
        "name": "物流师",
        "summary": "实际且注重事实的个人，可靠性不容置疑",
        "traits": ["认真负责", "注重细节", "务实可靠", "遵守规则", "有条不紊"]
    },
    "ISFJ": {
        "name": "守卫者",
        "summary": "非常专注、热情的保护者，时刻准备着守护所爱之人",
        "traits": ["支持可靠", "耐心周到", "观察力强", "忠诚坚定", "乐于助人"]
    },
    "ESTJ": {
        "name": "总经理",
        "summary": "出色的管理者，在管理事物或人方面无与伦比",
        "traits": ["组织能力", "脚踏实地", "直接坦诚", "遵守规则", "领导力强"]
    },
    "ESFJ": {
        "name": "执政官",
        "summary": "极有同情心、爱交际、受欢迎的人，总是热心帮助他人",
        "traits": ["善于社交", "忠诚可靠", "细心体贴", "传统价值观", "组织协调"]
    },
    "ISTP": {
        "name": "鉴赏家",
        "summary": "大胆而实际的实验家，擅长使用各种工具",
        "traits": ["务实理性", "技术天赋", "冷静沉着", "即兴能力", "敢于冒险"]
    },
    "ISFP": {
        "name": "探险家",
        "summary": "灵活有魅力的艺术家，时刻准备着探索和体验新鲜事物",
        "traits": ["艺术天赋", "敏感细腻", "开放包容", "温和谦逊", "活在当下"]
    },
    "ESTP": {
        "name": "企业家",
        "summary": "聪明、精力充沛、善于感知的人，真正享受生活在边缘",
        "traits": ["行动力强", "适应力强", "善于观察", "直接务实", "追求刺激"]
    },
    "ESFP": {
        "name": "表演者",
        "summary": "自发的、精力充沛的艺人，生活在他们周围永不乏味",
        "traits": ["乐观开朗", "擅长表演", "热情友好", "活在当下", "适应力强"]
    }
}


def calculate_score(answers: Dict[int, str]) -> Tuple[Dict[str, Tuple[int, int]], str]:
    """根据答题结果计算四个维度的得分"""
    dimensions = {
        "E/I": {"E": 0, "I": 0},
        "S/N": {"S": 0, "N": 0},
        "T/F": {"T": 0, "F": 0},
        "J/P": {"J": 0, "P": 0}
    }

    for q in MBTI_QUESTIONS:
        qid = q["id"]
        answer = answers.get(qid, "B")
        dim = q["dimension"]
        direction = q["direction"]
        
        pole1, pole2 = dim.split("/")
        if answer == "A":
            if direction == pole1:
                dimensions[dim][pole1] += 1
            else:
                dimensions[dim][pole2] += 1
        else:
            if direction == pole2:
                dimensions[dim][pole2] += 1
            else:
                dimensions[dim][pole1] += 1

    result = {}
    mbti_type = ""
    
    for dim, scores in dimensions.items():
        pole1, pole2 = dim.split("/")
        score1 = scores[pole1]
        score2 = scores[pole2]
        result[dim] = (score1, score2)
        
        if score1 >= score2:
            mbti_type += pole1
        else:
            mbti_type += pole2

    return result, mbti_type


def generate_report(mbti_type: str, scores: Dict[str, Tuple[int, int]], 
                   persona_path: Optional[str] = None) -> str:
    """生成 Markdown 格式的分析报告"""
    desc = MBTI_DESCRIPTIONS.get(mbti_type, {
        "name": "未知类型",
        "summary": "待分析",
        "traits": []
    })

    report = f"""# MBTI 人格测试分析报告

## 测试结果

**人格类型：{mbti_type} - {desc.get('name', '未知')}**

> {desc.get('summary', '')}

---

## 各维度得分明细

| 维度 | 倾向 | 得分比例 |
|------|------|----------|
| **E/I** | **{('E' if scores['E/I'][0] >= scores['E/I'][1] else 'I')}** | 外向 {scores['E/I'][0]:2d} : {scores['E/I'][1]:2d} 内向 |
| **S/N** | **{('S' if scores['S/N'][0] >= scores['S/N'][1] else 'N')}** | 感觉 {scores['S/N'][0]:2d} : {scores['S/N'][1]:2d} 直觉 |
| **T/F** | **{('T' if scores['T/F'][0] >= scores['T/F'][1] else 'F')}** | 思考 {scores['T/F'][0]:2d} : {scores['T/F'][1]:2d} 情感 |
| **J/P** | **{('J' if scores['J/P'][0] >= scores['J/P'][1] else 'P')}** | 判断 {scores['J/P'][0]:2d} : {scores['J/P'][1]:2d} 知觉 |

---

## 核心特质

"""

    for trait in desc.get("traits", []):
        report += f"- ✅ {trait}\n"

    report += """
---

## 与 Persona 模型关联建议

### Layer 1：身份锚定
- 建议在 persona.md Layer 1 中添加 MBTI 类型：`- MBTI：""" + mbti_type + "`\n"

    if mbti_type[0] == "E":
        report += "- 社交能量定位：从社交互动中获取能量\n"
    else:
        report += "- 社交能量定位：独处时恢复能量\n"

    report += """
### Layer 2：说话风格
"""
    if mbti_type[2] == "T":
        report += "- 表达倾向：更直接、逻辑性强，注重事实陈述\n"
    else:
        report += "- 表达倾向：更委婉、情感丰富，注重氛围和谐\n"
    
    if mbti_type[1] == "N":
        report += "- 思维特征：善于使用比喻、类比，倾向抽象表达\n"
    else:
        report += "- 思维特征：偏好具体实例，注重实际细节\n"

    report += """
### Layer 3：情感与决策模式
"""
    if mbti_type[2] == "T":
        report += "- 决策模式：基于逻辑分析，追求客观公正\n"
    else:
        report += "- 决策模式：考虑他人感受，寻求和谐共识\n"
    
    if mbti_type[3] == "J":
        report += "- 行动方式：偏好计划和确定性，追求完成\n"
    else:
        report += "- 行动方式：保持灵活性开放，适应变化\n"

    report += """
### Layer 4：人际行为
"""
    if mbti_type[0] == "E":
        report += "- 社交主动性：主动发起对话，群体中的活跃者\n"
    else:
        report += "- 社交主动性：被动回应较多，群体中的倾听者\n"
    
    if mbti_type[3] == "J":
        report += "- 边界感：较强，喜欢明确的规则\n"
    else:
        report += "- 边界感：灵活，适应模糊地带\n"

    report += """
---

## 使用建议

1. **融合优先级**：MBTI 作为辅助参考，真实行为数据优先级更高
2. **冲突处理**：当 MBTI 推断与聊天记录矛盾时，以真实记录为准
3. **修正机制**：建议在 persona 迭代中验证 MBTI 特征与真实表现的匹配度
4. **丰富维度**：将 MBTI 作为 persona 缺失维度的合理补充来源
"""

    return report


def run_interactive() -> Dict[int, str]:
    """运行交互式答题模式"""
    answers = {}
    
    print("\n" + "=" * 60)
    print("📝 MBTI 人格测试（共 60 题）")
    print("=" * 60)
    print("\n请根据实际情况选择 A 或 B，输入其他选项默认为 B\n")
    
    for i, q in enumerate(MBTI_QUESTIONS, 1):
        while True:
            print(f"\n[{i}/60] {q['text']}")
            ans = input("你的选择（A/B）：").strip().upper()
            if ans in ["A", "B", ""]:
                answers[q["id"]] = ans if ans else "B"
                break
            print("请输入 A 或 B\n")
    
    return answers


def load_answers_from_file(filepath: str) -> Dict[int, str]:
    """从 JSON 文件加载答题结果"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        answers = {}
        for item in data:
            qid = int(item.get("id", 0))
            ans = item.get("answer", "B").upper()
            if qid > 0:
                answers[qid] = ans if ans in ["A", "B"] else "B"
        return answers
    except Exception as e:
        print(f"❌ 加载文件失败：{e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='MBTI 人格测试工具')
    parser.add_argument('--slug', required=True, help='自我代号')
    parser.add_argument('--mode', choices=['interactive', 'file', 'template'], 
                       default='interactive', help='运行模式')
    parser.add_argument('--input', help='答题结果 JSON 文件（file 模式使用）')
    parser.add_argument('--base-dir', default='./selves', help='基础目录')
    parser.add_argument('--persona-path', help='现有 persona.md 文件路径')

    args = parser.parse_args()

    skill_dir = os.path.join(args.base_dir, args.slug)
    os.makedirs(skill_dir, exist_ok=True)

    if args.mode == 'interactive':
        answers = run_interactive()
    elif args.mode == 'file':
        if not args.input:
            print("❌ file 模式需要 --input 参数", file=sys.stderr)
            sys.exit(1)
        answers = load_answers_from_file(args.input)
    else:
        answers = {q["id"]: "B" for q in MBTI_QUESTIONS}

    scores, mbti_type = calculate_score(answers)

    print("\n" + "=" * 60)
    print(f"🎉 测试完成！你的 MBTI 类型是：{mbti_type}")
    print("=" * 60)
    
    print("\n各维度得分：")
    for dim, (s1, s2) in scores.items():
        p1, p2 = dim.split("/")
        print(f"  {dim}: {p1}={s1}, {p2}={s2}")

    report = generate_report(mbti_type, scores, args.persona_path)
    report_path = os.path.join(skill_dir, f"mbti_{mbti_type}.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 分析报告已保存至：{report_path}")
    print(f"\n💡 建议：将 MBTI 类型更新到 persona.md 的 Layer 1 身份字段中")
    
    answers_json_path = os.path.join(skill_dir, "mbti_answers.json")
    answers_export = [{"id": k, "answer": v} for k, v in answers.items()]
    with open(answers_json_path, 'w', encoding='utf-8') as f:
        json.dump(answers_export, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
