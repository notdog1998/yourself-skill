#!/usr/bin/env python3
"""MBTI 人格测试模块

实现标准 MBTI 测试问卷，支持交互式答题和批量导入，
计算四个维度得分并生成人格分析报告。

Usage:
    # 交互式答题
    python3 mbti_test.py --interactive --output <output_path> --slug <slug>

    # 从 JSON 文件导入
    python3 mbti_test.py --import <json_file> --output <output_path> --slug <slug>
"""

import argparse
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional


MBTI_QUESTIONS: List[Dict] = [
    {"id": 1, "dimension": "EI", "direction": "E", "text": "在社交聚会中，你通常会主动与陌生人交谈，而不是等待别人来接近你。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 2, "dimension": "EI", "direction": "I", "text": "独处时你感到精力充沛，而社交活动后往往需要时间恢复。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 3, "dimension": "SN", "direction": "S", "text": "你更关注当下的具体事实和细节，而不是未来的可能性。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 4, "dimension": "SN", "direction": "N", "text": "你常常会思考事物背后的含义和联系，而不仅仅是表面现象。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 5, "dimension": "TF", "direction": "T", "text": "做决定时，你更倾向于依据逻辑分析，而不是考虑他人感受。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 6, "dimension": "TF", "direction": "F", "text": "你认为在决策中，和谐的人际关系比客观的逻辑更重要。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 7, "dimension": "JP", "direction": "J", "text": "你喜欢提前制定计划，并按照计划行事。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 8, "dimension": "JP", "direction": "P", "text": "你更喜欢保持选项开放，随机应变而不是过早做决定。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 9, "dimension": "EI", "direction": "E", "text": "你喜欢成为众人关注的焦点，在群体中感到自在。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 10, "dimension": "EI", "direction": "I", "text": "你更喜欢一对一的深入交流，而不是大型社交活动。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 11, "dimension": "SN", "direction": "S", "text": "你更信任自己的直接经验和观察，而不是理论推测。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 12, "dimension": "SN", "direction": "N", "text": "你经常会有直觉性的想法，即使没有具体证据支持。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 13, "dimension": "TF", "direction": "T", "text": "你认为公平和正义比同情和怜悯更重要。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 14, "dimension": "TF", "direction": "F", "text": "你很容易感受到他人的情绪，并受到影响。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 15, "dimension": "JP", "direction": "J", "text": "完成任务后，你会有强烈的成就感；未完成时会感到焦虑。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 16, "dimension": "JP", "direction": "P", "text": "你享受生活中的意外和惊喜，不喜欢一切都在计划中。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 17, "dimension": "EI", "direction": "E", "text": "你倾向于通过与他人交流来理清自己的想法。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 18, "dimension": "EI", "direction": "I", "text": "在发言之前，你需要时间在内心整理思路。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 19, "dimension": "SN", "direction": "S", "text": "你更关注实际可行的解决方案，而不是创新的想法。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 20, "dimension": "SN", "direction": "N", "text": "你喜欢探索新概念和理论，即使它们暂时没有实际应用。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 21, "dimension": "TF", "direction": "T", "text": "在争论中，你更关注论点的正确性，而不是争论的方式是否得体。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 22, "dimension": "TF", "direction": "F", "text": "你很难对亲近的人提出批评，即使他们确实做错了。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 23, "dimension": "JP", "direction": "J", "text": "你的工作空间通常整洁有序，物品都有固定位置。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 24, "dimension": "JP", "direction": "P", "text": "你的工作方式比较灵活，可能会同时进行多个项目。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 25, "dimension": "EI", "direction": "E", "text": "你有很多朋友和熟人，社交圈比较广泛。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 26, "dimension": "EI", "direction": "I", "text": "你更喜欢有几个深交的朋友，而不是很多泛泛之交。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 27, "dimension": "SN", "direction": "S", "text": "你更擅长处理具体、实际的问题，而不是抽象的概念。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 28, "dimension": "SN", "direction": "N", "text": "你经常能发现别人忽略的模式和可能性。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 29, "dimension": "TF", "direction": "T", "text": "你认为诚实比照顾他人感受更重要。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 30, "dimension": "TF", "direction": "F", "text": "你会为了避免伤害他人而选择善意的谎言。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 31, "dimension": "JP", "direction": "J", "text": "你喜欢把事情尽早完成，不喜欢拖延到最后一刻。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 32, "dimension": "JP", "direction": "P", "text": "你在压力下反而更有动力，经常在截止日期前高效工作。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 33, "dimension": "EI", "direction": "E", "text": "在团队中，你通常愿意承担领导或协调的角色。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 34, "dimension": "EI", "direction": "I", "text": "你更喜欢独立工作，或者在小团队中扮演支持角色。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 35, "dimension": "SN", "direction": "S", "text": "你更重视传统的、经过验证的方法。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 36, "dimension": "SN", "direction": "N", "text": "你对新奇和变化感到兴奋，喜欢尝试新事物。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 37, "dimension": "TF", "direction": "T", "text": "你做决定时很少受到他人情绪的影响。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 38, "dimension": "TF", "direction": "F", "text": "你认为每个人都有自己的处境，不应该用统一标准评判。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 39, "dimension": "JP", "direction": "J", "text": "你制定日程表并尽量遵守，不喜欢计划被打乱。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 40, "dimension": "JP", "direction": "P", "text": "你不喜欢过于严格的计划，更愿意顺其自然。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 41, "dimension": "EI", "direction": "E", "text": "参加社交活动后，你感到精力充沛而不是疲惫。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 42, "dimension": "EI", "direction": "I", "text": "你需要大量的独处时间来思考和充电。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 43, "dimension": "SN", "direction": "S", "text": "你更关注眼前需要解决的问题，而不是长远的愿景。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 44, "dimension": "SN", "direction": "N", "text": "你经常思考未来的各种可能性，有时会忽略眼前的现实。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 45, "dimension": "TF", "direction": "T", "text": "你认为原则和规则应该被遵守，特殊情况不应成为借口。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 46, "dimension": "TF", "direction": "F", "text": "你更容易被他人的故事打动，而不是被数据说服。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 47, "dimension": "JP", "direction": "J", "text": "你喜欢把事情安排得井井有条，不喜欢混乱。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 48, "dimension": "JP", "direction": "P", "text": "你认为一定程度的混乱是创造力的体现。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 49, "dimension": "EI", "direction": "E", "text": "你喜欢热闹的环境，安静的环境让你感到无聊。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 50, "dimension": "EI", "direction": "I", "text": "你更喜欢安静的环境，噪音和干扰会让你烦躁。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 51, "dimension": "SN", "direction": "S", "text": "你更信任可以测量和验证的信息。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 52, "dimension": "SN", "direction": "N", "text": "你经常有预感或直觉，而且它们往往是正确的。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 53, "dimension": "TF", "direction": "T", "text": "在批评他人时，你更关注事实而非方式。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 54, "dimension": "TF", "direction": "F", "text": "你很难拒绝他人的请求，即使这会给自己带来麻烦。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 55, "dimension": "JP", "direction": "J", "text": "你喜欢列清单，把要做的事情写下来。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 56, "dimension": "JP", "direction": "P", "text": "你更喜欢即兴发挥，而不是按部就班。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 57, "dimension": "EI", "direction": "E", "text": "你很容易与新认识的人建立联系。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 58, "dimension": "EI", "direction": "I", "text": "你需要时间才能信任他人，不会轻易敞开心扉。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 59, "dimension": "SN", "direction": "S", "text": "你更喜欢按既定程序做事，而不是自己发明新方法。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 60, "dimension": "SN", "direction": "N", "text": "你喜欢思考抽象的概念和理论问题。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 61, "dimension": "TF", "direction": "T", "text": "你认为逻辑一致性比人际和谐更重要。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 62, "dimension": "TF", "direction": "F", "text": "你很容易与他人产生共情，理解他们的感受。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 63, "dimension": "JP", "direction": "J", "text": "完成任务的截止日期对你来说很重要，你会努力按时完成。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 64, "dimension": "JP", "direction": "P", "text": "你认为截止日期是灵活的，质量比速度更重要。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 65, "dimension": "EI", "direction": "E", "text": "你喜欢在群体中表达自己的观点和想法。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 66, "dimension": "EI", "direction": "I", "text": "你更喜欢倾听而不是发言，尤其是在大型会议中。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 67, "dimension": "SN", "direction": "S", "text": "你更关注细节，经常注意到别人忽略的小事。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 68, "dimension": "SN", "direction": "N", "text": "你更喜欢从宏观角度看问题，而不是纠结于细节。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 69, "dimension": "TF", "direction": "T", "text": "你认为客观真理比个人感受更重要。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 70, "dimension": "TF", "direction": "F", "text": "你做决定时会优先考虑对他人的影响。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 71, "dimension": "JP", "direction": "J", "text": "你喜欢有明确的目标和方向，不喜欢模棱两可。", "options": {"A": "同意", "B": "不同意"}},
    {"id": 72, "dimension": "JP", "direction": "P", "text": "你喜欢探索多种可能性，不喜欢过早下结论。", "options": {"A": "同意", "B": "不同意"}},
]

MBTI_DESCRIPTIONS: Dict[str, Dict] = {
    "INTJ": {
        "name": "建筑师",
        "keywords": ["独立", "战略性", "果断", "完美主义"],
        "summary": "富有想象力和战略性的思想家，一切皆在计划之中。",
        "strengths": ["理性客观", "意志坚定", "追求卓越", "善于规划"],
        "weaknesses": ["过于自信", "可能傲慢", "不善社交", "过于挑剔"],
        "career": ["科学家", "工程师", "战略顾问", "投资分析师"],
    },
    "INTP": {
        "name": "逻辑学家",
        "keywords": ["分析性", "创新", "好奇", "理论性"],
        "summary": "富有创造力的发明家，对知识有着永不满足的渴望。",
        "strengths": ["思维开放", "客观公正", "诚实直接", "善于分析"],
        "weaknesses": ["情感迟钝", "容易分心", "过度思考", "不善执行"],
        "career": ["程序员", "科学家", "数学家", "哲学家"],
    },
    "ENTJ": {
        "name": "指挥官",
        "keywords": ["领导力", "果断", "自信", "战略性"],
        "summary": "大胆、富有想象力的领导者，总能找到解决方法或创造方法。",
        "strengths": ["自信果断", "意志坚强", "高效执行", "善于激励"],
        "weaknesses": ["固执己见", "可能傲慢", "不善共情", "过于挑剔"],
        "career": ["企业高管", "律师", "管理顾问", "创业者"],
    },
    "ENTP": {
        "name": "辩论家",
        "keywords": ["创新", "好奇", "机智", "挑战性"],
        "summary": "聪明好奇的思想家，无法抗拒智力上的挑战。",
        "strengths": ["思维敏捷", "富有创意", "善于辩论", "乐观自信"],
        "weaknesses": ["喜欢争论", "不耐烦", "容易分心", "不善执行"],
        "career": ["创业者", "律师", "记者", "营销策划"],
    },
    "INFJ": {
        "name": "提倡者",
        "keywords": ["理想主义", "有洞察力", "有原则", "追求意义"],
        "summary": "安静而神秘，但能深刻启发和感染他人。",
        "strengths": ["富有洞察", "有原则", "善于倾听", "有同情心"],
        "weaknesses": ["过于理想", "容易倦怠", "隐私意识强", "完美主义"],
        "career": ["心理咨询师", "作家", "教师", "非营利组织工作者"],
    },
    "INFP": {
        "name": "调停者",
        "keywords": ["理想主义", "有创造力", "有同理心", "寻求和谐"],
        "summary": "诗意、善良的利他主义者，总是渴望帮助善良的事业。",
        "strengths": ["富有同情心", "有创造力", "思想开放", "充满激情"],
        "weaknesses": ["过于理想", "不切实际", "情感脆弱", "难以专注"],
        "career": ["作家", "心理咨询师", "艺术家", "社会工作者"],
    },
    "ENFJ": {
        "name": "主人公",
        "keywords": ["有魅力", "有影响力", "有同理心", "负责任"],
        "summary": "富有魅力的领导者，能够激励听众。",
        "strengths": ["领导力强", "善于沟通", "有同理心", "可靠负责"],
        "weaknesses": ["过于理想", "过度敏感", "自我牺牲", "优柔寡断"],
        "career": ["教师", "人力资源", "公关", "政治家"],
    },
    "ENFP": {
        "name": "竞选者",
        "keywords": ["热情", "有创造力", "社交性强", "精力充沛"],
        "summary": "热情、有创造力的社交达人，总能找到微笑的理由。",
        "strengths": ["观察力强", "热情洋溢", "善于沟通", "适应力强"],
        "weaknesses": ["注意力分散", "过度思考", "情绪化", "缺乏专注"],
        "career": ["记者", "演员", "营销", "创业者"],
    },
    "ISTJ": {
        "name": "物流师",
        "keywords": ["可靠", "有条理", "务实", "负责任"],
        "summary": "务实、专注于事实的个体，其可靠性不容置疑。",
        "strengths": ["诚实直接", "意志坚定", "负责任", "注重细节"],
        "weaknesses": ["固执己见", "不善变通", "过于挑剔", "喜欢评判"],
        "career": ["会计师", "审计师", "公务员", "数据分析师"],
    },
    "ISFJ": {
        "name": "守卫者",
        "keywords": ["忠诚", "有同情心", "有条理", "支持性强"],
        "summary": "非常敬业和忠诚的守护者，随时准备保护所爱之人。",
        "strengths": ["支持性强", "可靠耐心", "观察力强", "热情忠诚"],
        "weaknesses": ["过于谦逊", "不善拒绝", "过度付出", "不喜欢变化"],
        "career": ["护士", "教师", "行政助理", "社会工作者"],
    },
    "ESTJ": {
        "name": "总经理",
        "keywords": ["有条理", "果断", "直接", "有领导力"],
        "summary": "出色的管理者，在管理事务和人员方面无与伦比。",
        "strengths": ["尽职尽责", "意志坚定", "直接诚实", "忠诚可靠"],
        "weaknesses": ["固执己见", "不善共情", "过于传统", "喜欢评判"],
        "career": ["管理人员", "法官", "财务主管", "项目经理"],
    },
    "ESFJ": {
        "name": "执政官",
        "keywords": ["有同情心", "有条理", "社交性强", "忠诚"],
        "summary": "极有同情心、爱交际的人，总是热心帮助他人。",
        "strengths": ["忠诚可靠", "善于社交", "有同情心", "乐于助人"],
        "weaknesses": ["过于敏感", "需要认可", "不善接受批评", "过于无私"],
        "career": ["护士", "教师", "人力资源", "活动策划"],
    },
    "ISTP": {
        "name": "鉴赏家",
        "keywords": ["务实", "分析性", "独立", "适应性强"],
        "summary": "大胆而实际的实验家，善于使用各种工具。",
        "strengths": ["乐观自信", "善于应变", "动手能力强", "理性客观"],
        "weaknesses": ["情感迟钝", "喜欢冒险", "不善承诺", "隐私意识强"],
        "career": ["工程师", "技师", "运动员", "飞行员"],
    },
    "ISFP": {
        "name": "探险家",
        "keywords": ["有创造力", "敏感", "独立", "有艺术感"],
        "summary": "灵活而有魅力的艺术家，随时准备探索和体验新事物。",
        "strengths": ["富有魅力", "敏感细腻", "思想开放", "艺术天赋"],
        "weaknesses": ["过于独立", "难以预测", "容易倦怠", "不善规划"],
        "career": ["艺术家", "设计师", "音乐家", "厨师"],
    },
    "ESTP": {
        "name": "企业家",
        "keywords": ["精力充沛", "行动导向", "实际", "社交性强"],
        "summary": "聪明、精力充沛、善于感知的人，真正享受生活边缘。",
        "strengths": ["观察力强", "直接务实", "善于社交", "行动力强"],
        "weaknesses": ["情感迟钝", "不耐烦", "喜欢冒险", "不善承诺"],
        "career": ["销售", "运动员", "企业家", "消防员"],
    },
    "ESFP": {
        "name": "表演者",
        "keywords": ["外向", "友好", "接受力强", "热爱生活"],
        "summary": "自发的、精力充沛的艺人，生活永远不会无聊。",
        "strengths": ["大胆热情", "善于观察", "富有魅力", "适应力强"],
        "weaknesses": ["注意力分散", "不善规划", "逃避冲突", "缺乏耐心"],
        "career": ["演员", "主持人", "销售", "活动策划"],
    },
}

DIMENSION_NAMES: Dict[str, Tuple[str, str]] = {
    "EI": ("外向 (E)", "内向 (I)"),
    "SN": ("感觉 (S)", "直觉 (N)"),
    "TF": ("思考 (T)", "情感 (F)"),
    "JP": ("判断 (J)", "感知 (P)"),
}


def calculate_scores(answers: List[Dict]) -> Dict[str, Dict]:
    """计算各维度得分"""
    scores = {
        "EI": {"E": 0, "I": 0, "total": 0},
        "SN": {"S": 0, "N": 0, "total": 0},
        "TF": {"T": 0, "F": 0, "total": 0},
        "JP": {"J": 0, "P": 0, "total": 0},
    }

    for answer in answers:
        qid = answer.get("question_id")
        choice = answer.get("choice", "").upper()
        question = next((q for q in MBTI_QUESTIONS if q["id"] == qid), None)

        if not question or choice not in ["A", "B"]:
            continue

        dim = question["dimension"]
        direction = question["direction"]

        if choice == "A":
            scores[dim][direction] += 1
        else:
            opposite = "I" if direction == "E" else "E" if direction == "I" else \
                       "N" if direction == "S" else "S" if direction == "N" else \
                       "F" if direction == "T" else "T" if direction == "F" else \
                       "P" if direction == "J" else "J"
            scores[dim][opposite] += 1

        scores[dim]["total"] += 1

    return scores


def determine_mbti_type(scores: Dict[str, Dict]) -> str:
    """根据得分确定 MBTI 类型"""
    mbti = ""

    e_score = scores["EI"]["E"]
    i_score = scores["EI"]["I"]
    mbti += "E" if e_score >= i_score else "I"

    s_score = scores["SN"]["S"]
    n_score = scores["SN"]["N"]
    mbti += "S" if s_score >= n_score else "N"

    t_score = scores["TF"]["T"]
    f_score = scores["TF"]["F"]
    mbti += "T" if t_score >= f_score else "F"

    j_score = scores["JP"]["J"]
    p_score = scores["JP"]["P"]
    mbti += "J" if j_score >= p_score else "P"

    return mbti


def generate_report(mbti_type: str, scores: Dict[str, Dict], slug: str) -> str:
    """生成 Markdown 格式的分析报告"""
    desc = MBTI_DESCRIPTIONS.get(mbti_type, {})
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# MBTI 人格测试报告

**测试者**: {slug}
**测试时间**: {now}
**人格类型**: **{mbti_type}** — {desc.get('name', '未知类型')}

---

## 一、维度得分明细

| 维度 | 倾向 A | 得分 | 倾向 B | 得分 | 结果 |
|------|--------|------|--------|------|------|
| 能量来源 | {DIMENSION_NAMES['EI'][0]} | {scores['EI']['E']} | {DIMENSION_NAMES['EI'][1]} | {scores['EI']['I']} | **{mbti_type[0]}** |
| 信息获取 | {DIMENSION_NAMES['SN'][0]} | {scores['SN']['S']} | {DIMENSION_NAMES['SN'][1]} | {scores['SN']['N']} | **{mbti_type[1]}** |
| 决策方式 | {DIMENSION_NAMES['TF'][0]} | {scores['TF']['T']} | {DIMENSION_NAMES['TF'][1]} | {scores['TF']['F']} | **{mbti_type[2]}** |
| 生活态度 | {DIMENSION_NAMES['JP'][0]} | {scores['JP']['J']} | {DIMENSION_NAMES['JP'][1]} | {scores['JP']['P']} | **{mbti_type[3]}** |

### 维度解读

**1. 能量来源 ({mbti_type[0]})**
"""
    if mbti_type[0] == "E":
        report += """
- 从外部世界获取能量
- 喜欢社交互动和外部刺激
- 倾向于先行动后思考
- 在人群中感到精力充沛
"""
    else:
        report += """
- 从内心世界获取能量
- 需要独处时间来恢复精力
- 倾向于先思考后行动
- 在安静环境中感到舒适
"""

    report += f"""
**2. 信息获取 ({mbti_type[1]})**
"""
    if mbti_type[1] == "S":
        report += """
- 关注具体事实和细节
- 信任经验和可验证的信息
- 注重当下和现实
- 偏好实际可行的方案
"""
    else:
        report += """
- 关注整体模式和可能性
- 信任直觉和灵感
- 注重未来和潜在性
- 偏好创新和理论探索
"""

    report += f"""
**3. 决策方式 ({mbti_type[2]})**
"""
    if mbti_type[2] == "T":
        report += """
- 依据逻辑和客观分析做决定
- 重视公平和一致性
- 可能忽略情感因素
- 倾向于直接坦诚的沟通
"""
    else:
        report += """
- 依据价值观和他人感受做决定
- 重视和谐和人际关系
- 容易受情感影响
- 倾向于委婉体贴的沟通
"""

    report += f"""
**4. 生活态度 ({mbti_type[3]})**
"""
    if mbti_type[3] == "J":
        report += """
- 喜欢计划和组织
- 追求确定性和完成感
- 注重目标达成
- 偏好有条理的生活方式
"""
    else:
        report += """
- 喜欢灵活和开放
- 追求可能性和体验
- 注重过程享受
- 偏好随性的生活方式
"""

    report += f"""
---

## 二、人格类型描述

### {mbti_type} — {desc.get('name', '未知类型')}

> {desc.get('summary', '')}

### 关键特质
"""
    for kw in desc.get("keywords", []):
        report += f"- {kw}\n"

    report += """
### 优势
"""
    for s in desc.get("strengths", []):
        report += f"- {s}\n"

    report += """
### 潜在盲点
"""
    for w in desc.get("weaknesses", []):
        report += f"- {w}\n"

    report += f"""
### 适合的职业方向
"""
    for c in desc.get("career", []):
        report += f"- {c}\n"

    report += f"""
---

## 三、与 Persona 模型的关联建议

MBTI 测试结果可以作为 persona.md 中 **Layer 1（身份层）** 的重要补充。
以下是具体的融合建议：

### Layer 1：身份层

在 `persona.md` 的身份层中，可以添加：

```markdown
- MBTI：{mbti_type}（{desc.get('name', '')}）
```

### Layer 2：说话风格层

根据 MBTI 类型，说话风格可能呈现以下特点：

"""
    if mbti_type[0] == "E":
        report += "- **表达倾向**：更愿意主动表达，喜欢通过交流理清思路\n"
    else:
        report += "- **表达倾向**：倾向于深思熟虑后发言，喜欢倾听\n"

    if mbti_type[1] == "S":
        report += "- **表达内容**：更关注具体细节和实际经验\n"
    else:
        report += "- **表达内容**：更关注抽象概念和未来可能\n"

    if mbti_type[2] == "T":
        report += "- **表达方式**：更直接、逻辑性强，可能显得不够委婉\n"
    else:
        report += "- **表达方式**：更温和、注重他人感受，可能显得不够直接\n"

    if mbti_type[3] == "J":
        report += "- **表达结构**：更有条理，喜欢给出明确结论\n"
    else:
        report += "- **表达结构**：更开放，喜欢探讨多种可能性\n"

    report += f"""
### Layer 3：情感与决策模式层

MBTI 的 T/F 和 J/P 维度与情感决策模式高度相关：

**决策偏好**：
- 理性 vs 感性：{'偏向理性（T）' if mbti_type[2] == "T" else '偏向感性（F）'}
- 计划 vs 随性：{'偏向计划（J）' if mbti_type[3] == "J" else '偏向随性（P）'}

**建议在 persona.md 中补充**：
```markdown
### 决策模式
- 理性 vs 感性：{'偏向理性，依据逻辑分析做决定' if mbti_type[2] == "T" else '偏向感性，考虑他人感受做决定'}
- 计划 vs 随性：{'偏向计划，喜欢提前安排' if mbti_type[3] == "J" else '偏向随性，喜欢保持灵活'}
```

### Layer 4：人际行为层

MBTI 的 E/I 维度与人际行为直接相关：

"""
    if mbti_type[0] == "E":
        report += """**社交特点**：
- 在群体中感到精力充沛
- 喜欢广泛的社交圈
- 倾向于主动发起互动
- 通过交流建立连接
"""
    else:
        report += """**社交特点**：
- 需要独处时间恢复精力
- 偏好深度而非广度的社交
- 倾向于被动等待互动
- 通过共同经历建立连接
"""

    report += """
---

## 四、下一步建议

1. **整合到 persona.md**：将 MBTI 类型添加到身份层，并根据上述建议丰富各层内容
2. **交叉验证**：对比聊天记录分析结果与 MBTI 测试结果，寻找一致性或差异
3. **动态更新**：MBTI 类型可能随时间微调，建议定期重新测试
4. **深度探索**：阅读更多关于该类型的资料，加深自我认知

---

*本报告由 yourself-skill MBTI 测试模块自动生成*
"""

    return report


def run_interactive_test() -> List[Dict]:
    """运行交互式测试"""
    print("\n" + "=" * 60)
    print("MBTI 人格测试")
    print("=" * 60)
    print("\n说明：本测试共 72 道题，请根据您的真实情况作答。")
    print("每道题请选择 A（同意）或 B（不同意），没有对错之分。\n")
    print("输入 'q' 可随时退出并保存当前进度。\n")

    answers = []
    for i, q in enumerate(MBTI_QUESTIONS, 1):
        print(f"\n[{i}/{len(MBTI_QUESTIONS)}] {q['text']}")
        print(f"  A. {q['options']['A']}")
        print(f"  B. {q['options']['B']}")
        print("  请选择 (A/B): ", end="", flush=True)

        while True:
            try:
                choice = input().strip().upper()
                if choice == "Q":
                    print("\n测试已中断。")
                    return answers
                if choice in ["A", "B"]:
                    answers.append({
                        "question_id": q["id"],
                        "choice": choice,
                    })
                    break
                print("  请输入 A 或 B: ", end="", flush=True)
            except EOFError:
                print("\n\n测试已中断。")
                return answers

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    return answers


def import_from_json(json_path: str) -> List[Dict]:
    """从 JSON 文件导入答题结果"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "answers" in data:
        return data["answers"]
    else:
        raise ValueError("JSON 格式错误，应为答案列表或包含 'answers' 字段的字典")


def main():
    parser = argparse.ArgumentParser(description="MBTI 人格测试")
    parser.add_argument("--interactive", action="store_true", help="交互式答题模式")
    parser.add_argument("--import", dest="import_file", help="从 JSON 文件导入答题结果")
    parser.add_argument("--output", required=True, help="输出报告路径")
    parser.add_argument("--slug", default="user", help="用户标识")

    args = parser.parse_args()

    answers = []
    if args.interactive:
        answers = run_interactive_test()
    elif args.import_file:
        print(f"从 {args.import_file} 导入答题结果...")
        answers = import_from_json(args.import_file)
    else:
        print("错误：请指定 --interactive 或 --import", file=sys.stderr)
        sys.exit(1)

    if not answers:
        print("错误：没有有效的答题数据", file=sys.stderr)
        sys.exit(1)

    print(f"\n共 {len(answers)} 道题目作答，正在计算结果...\n")

    scores = calculate_scores(answers)
    mbti_type = determine_mbti_type(scores)
    report = generate_report(mbti_type, scores, args.slug)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"MBTI 类型: {mbti_type}")
    print(f"报告已保存到: {args.output}")


if __name__ == "__main__":
    main()
