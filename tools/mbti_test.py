#!/usr/bin/env python3
"""MBTI 人格测试模块

提供标准的 MBTI 人格测试问卷，支持交互式答题和批量导入，生成详细的分析报告。

Usage:
    python3 mbti_test.py --mode interactive --slug <user_slug>
    python3 mbti_test.py --mode import --file <answers.json> --slug <user_slug>
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class Dimension(Enum):
    """MBTI 四个维度"""
    EI = "EI"  # 外向/内向
    SN = "SN"  # 感觉/直觉
    TF = "TF"  # 思考/情感
    JP = "JP"  # 判断/知觉


@dataclass
class Question:
    """MBTI 测试题目"""
    id: int
    text: str
    dimension: Dimension
    direction: int  # 1: 正向计分(选A加一分), -1: 反向计分(选B加一分)
    option_a: str
    option_b: str


@dataclass
class DimensionScore:
    """维度得分"""
    dimension: Dimension
    left_score: int  # E/S/T/J 得分
    right_score: int  # I/N/F/P 得分
    left_label: str
    right_label: str
    left_letter: str
    right_letter: str

    @property
    def dominant(self) -> str:
        """返回主导倾向的字母"""
        return self.left_letter if self.left_score >= self.right_score else self.right_letter

    @property
    def percentage(self) -> int:
        """返回主导倾向的百分比"""
        total = self.left_score + self.right_score
        if total == 0:
            return 50
        dominant_score = max(self.left_score, self.right_score)
        return int((dominant_score / total) * 100)


@dataclass
class MBTIResult:
    """MBTI 测试结果"""
    mbti_type: str
    scores: Dict[Dimension, DimensionScore]
    test_date: str
    total_questions: int
    answered_questions: int


# MBTI 标准测试题库（60题）
# 参考主流 MBTI 测试题库设计，覆盖四个维度
MBTI_QUESTIONS: List[Question] = [
    # E/I 维度 - 外向(Extraversion) vs 内向(Introversion)
    # 15题
    Question(1, "在社交场合中，你通常：", Dimension.EI, 1, "感到兴奋，喜欢主动与人交流", "感到有些疲惫，更喜欢与少数熟人交谈"),
    Question(2, "当你需要思考问题时，你倾向于：", Dimension.EI, -1, "独自安静地思考", "通过与他人讨论来理清思路"),
    Question(3, "你更喜欢哪种工作环境？", Dimension.EI, 1, "开放式办公，可以随时与同事交流", "独立办公室，减少外界干扰"),
    Question(4, "在聚会上，你通常会：", Dimension.EI, 1, "主动认识新朋友", "只和熟悉的朋友待在一起"),
    Question(5, "你获取能量的方式是：", Dimension.EI, 1, "参与社交活动，与人互动", "独处时光，做自己喜欢的事"),
    Question(6, "你更倾向于：", Dimension.EI, 1, "边说边想，在交流中产生想法", "想好再说，在内心整理思路"),
    Question(7, "对于周末的安排，你更喜欢：", Dimension.EI, 1, "和朋友一起出去玩", "在家看书或做个人爱好"),
    Question(8, "在团队讨论中，你通常：", Dimension.EI, 1, "积极发言，分享想法", "先倾听他人，再选择性发言"),
    Question(9, "你觉得自己更偏向于：", Dimension.EI, 1, "行动派，想到就做", "思考派，三思而后行"),
    Question(10, "面对新环境，你通常会：", Dimension.EI, 1, "快速融入，主动结识他人", "观察一段时间，慢慢适应"),
    Question(11, "你更喜欢：", Dimension.EI, 1, "电话或面对面交流", "文字信息或邮件沟通"),
    Question(12, "在社交活动中，你：", Dimension.EI, -1, "需要独处时间来恢复精力", "能从社交中获得更多能量"),
    Question(13, "你描述自己时：", Dimension.EI, 1, "很容易向他人敞开心扉", "比较谨慎，只和信任的人分享"),
    Question(14, "你更喜欢的工作方式是：", Dimension.EI, 1, "团队协作，共同完成任务", "独立工作，自主掌控进度"),
    Question(15, "在大型社交活动中，你通常：", Dimension.EI, -1, "期待活动结束，可以回家休息", "享受热闹的氛围，意犹未尽"),

    # S/N 维度 - 感觉(Sensing) vs 直觉(Intuition)
    # 15题
    Question(16, "你更关注：", Dimension.SN, 1, "具体的事实和细节", "整体的模式和可能性"),
    Question(17, "学习新事物时，你更喜欢：", Dimension.SN, 1, "循序渐进，打好基础", "了解整体框架，再填充细节"),
    Question(18, "你更信任：", Dimension.SN, 1, "过往经验和实际案例", "直觉和灵感"),
    Question(19, "描述事物时，你倾向于：", Dimension.SN, 1, "具体、实际、详细", "抽象、比喻、概括"),
    Question(20, "你更感兴趣的是：", Dimension.SN, 1, "已经验证有效的方法", "新颖独特的创意"),
    Question(21, "阅读时，你更关注：", Dimension.SN, 1, "字面意思和具体信息", "隐含意义和象征"),
    Question(22, "你更喜欢讨论：", Dimension.SN, 1, "实际问题和当下事务", "未来可能性和理论概念"),
    Question(23, "你更擅长记住：", Dimension.SN, 1, "具体的事实和数据", "概念和模式"),
    Question(24, "面对问题，你更倾向于：", Dimension.SN, 1, "参考过去类似情况的解决方案", "探索全新的解决思路"),
    Question(25, "你更欣赏的人是：", Dimension.SN, 1, "务实、脚踏实地的人", "富有想象力、有远见的人"),
    Question(26, "你更喜欢的工作是：", Dimension.SN, 1, "有明确步骤和流程的", "需要创新和灵活应变的"),
    Question(27, "你更在意：", Dimension.SN, 1, "当下的现实状况", "未来的发展趋势"),
    Question(28, "学习时，你更喜欢：", Dimension.SN, 1, "通过实践和操作来学习", "通过阅读和思考来学习"),
    Question(29, "你更相信：", Dimension.SN, 1, "眼见为实，实际体验", "第六感和直觉判断"),
    Question(30, "你更喜欢的话题是：", Dimension.SN, 1, "具体的生活琐事和日常", "抽象的哲学思考和理论"),

    # T/F 维度 - 思考(Thinking) vs 情感(Feeling)
    # 15题
    Question(31, "做决定时，你更重视：", Dimension.TF, 1, "逻辑分析和客观标准", "个人价值和对他人的影响"),
    Question(32, "面对冲突，你更倾向于：", Dimension.TF, 1, "直接指出问题，寻求解决方案", "考虑各方感受，维护和谐关系"),
    Question(33, "你更在意：", Dimension.TF, 1, "事情是否正确合理", "是否照顾到他人感受"),
    Question(34, "评价一个决定时，你更看重：", Dimension.TF, 1, "结果的有效性和效率", "过程中的人际关系"),
    Question(35, "你更欣赏的品质是：", Dimension.TF, 1, "公正、理性、能力强", "善良、体贴、有同情心"),
    Question(36, "当朋友向你倾诉烦恼时，你通常会：", Dimension.TF, 1, "帮助分析问题，提供建议", "倾听陪伴，给予情感支持"),
    Question(37, "你更难以忍受的是：", Dimension.TF, 1, "不讲逻辑、混乱无序", "冷漠无情、缺乏同理心"),
    Question(38, "在团队合作中，你更关注：", Dimension.TF, 1, "任务完成的质量和效率", "团队成员的参与感和满意度"),
    Question(39, "你更倾向于：", Dimension.TF, 1, "对事不对人，客观评价", "因人而异，考虑特殊情况"),
    Question(40, "你认为好的批评应该是：", Dimension.TF, 1, "直接、具体、有建设性", "温和、委婉、保护自尊"),
    Question(41, "你更自豪于：", Dimension.TF, 1, "自己的分析能力和判断力", "自己善于理解帮助他人"),
    Question(42, "面对不公平的情况，你更倾向于：", Dimension.TF, 1, "坚持原则，维护公正", "考虑人情，灵活处理"),
    Question(43, "你更重视：", Dimension.TF, 1, "真理和事实", "和谐与融洽"),
    Question(44, "你更擅长：", Dimension.TF, 1, "发现逻辑漏洞和错误", "察觉他人的情绪变化"),
    Question(45, "你更希望自己被视为：", Dimension.TF, 1, "有能力、有才干的人", "善解人意、值得信赖的朋友"),

    # J/P 维度 - 判断(Judging) vs 知觉(Perceiving)
    # 15题
    Question(46, "你更喜欢的生活方式是：", Dimension.JP, 1, "有计划、有条理、按部就班", "灵活、随性、保持开放"),
    Question(47, "面对截止日期，你通常：", Dimension.JP, 1, "提前完成，避免临时赶工", "在截止日期前冲刺完成"),
    Question(48, "你更喜欢：", Dimension.JP, 1, "做决定并确定下来", "保持选择开放，随机应变"),
    Question(49, "你的桌面或房间通常是：", Dimension.JP, 1, "整洁有序，东西各归其位", "有些凌乱，但你知道东西在哪"),
    Question(50, "旅行时，你更喜欢：", Dimension.JP, 1, "提前做好详细攻略", "到了再说，随机探索"),
    Question(51, "你更倾向于：", Dimension.JP, 1, "按照计划执行任务", "根据当下情况调整安排"),
    Question(52, "未完成的任务会让你：", Dimension.JP, 1, "感到焦虑，想尽快完成", "觉得正常，有时间再做"),
    Question(53, "你更喜欢的工作环境是：", Dimension.JP, 1, "有明确的目标和截止时间", "自由安排，弹性工作"),
    Question(54, "面对变化，你通常：", Dimension.JP, -1, "感到兴奋，期待新体验", "需要适应时间，喜欢稳定"),
    Question(55, "你更享受：", Dimension.JP, 1, "完成任务后的成就感", "探索过程中的乐趣"),
    Question(56, "你的日程安排通常是：", Dimension.JP, 1, "提前规划好，按计划执行", "大致安排，随时调整"),
    Question(57, "你更喜欢：", Dimension.JP, 1, "有明确的规则和流程", "根据实际情况灵活处理"),
    Question(58, "新项目开始时，你倾向于：", Dimension.JP, 1, "先制定详细的计划", "直接开始，边做边调整"),
    Question(59, "你更难以忍受的是：", Dimension.JP, 1, "混乱无序、计划被打乱", "被束缚、缺乏自由"),
    Question(60, "你更认同：", Dimension.JP, 1, "早做打算，有备无患", "船到桥头自然直"),
]

# MBTI 类型详细描述
MBTI_DESCRIPTIONS: Dict[str, Dict[str, Union[str, List[str]]]] = {
    "ISTJ": {
        "name": "检查者",
        "traits": ["务实", "可靠", "有条理", "注重细节"],
        "strengths": ["责任心强", "注重实际", "逻辑清晰", "坚持不懈"],
        "weaknesses": ["可能过于固执", "不太善于表达情感", "对变化适应较慢"],
        "description": "ISTJ 是务实可靠的组织者，重视传统和秩序。他们做事认真负责，注重细节，是值得信赖的执行者。",
    },
    "ISFJ": {
        "name": "保护者",
        "traits": ["温暖", "体贴", "尽责", "实际"],
        "strengths": ["善于照顾他人", "记忆力好", "耐心细致", "忠诚可靠"],
        "weaknesses": ["容易过度付出", "回避冲突", "对自己要求过高"],
        "description": "ISFJ 是温暖体贴的守护者，默默付出，关心他人的需求。他们重视和谐，是值得信赖的朋友。",
    },
    "INFJ": {
        "name": "提倡者",
        "traits": ["理想主义", "洞察力强", "有创造力", "坚定"],
        "strengths": ["富有远见", "善于理解他人", "有创造力", "目标明确"],
        "weaknesses": ["容易理想化", "对批评敏感", "容易 burnout"],
        "description": "INFJ 是富有洞察力的理想主义者，追求意义和深度。他们有强烈的价值观，致力于让世界变得更好。",
    },
    "INTJ": {
        "name": "建筑师",
        "traits": ["独立", "有远见", "分析力强", "果断"],
        "strengths": ["战略思维", "高效执行", "知识渊博", "自信"],
        "weaknesses": ["可能显得傲慢", "对情感不够敏感", "过于追求完美"],
        "description": "INTJ 是独立思考的战略家，善于规划和执行长期目标。他们追求知识和能力，是天生的领导者。",
    },
    "ISTP": {
        "name": "鉴赏家",
        "traits": ["灵活", "理性", "实用主义", "观察力强"],
        "strengths": ["动手能力强", "冷静理性", "善于解决问题", "适应力强"],
        "weaknesses": ["可能显得冷漠", "不喜欢承诺", "容易厌倦"],
        "description": "ISTP 是灵活务实的实验者，喜欢探索和解决实际问题。他们冷静理性，善于应对突发状况。",
    },
    "ISFP": {
        "name": "探险家",
        "traits": ["敏感", "艺术气质", "随和", "活在当下"],
        "strengths": ["审美能力强", "灵活适应", "真诚友善", "富有同情心"],
        "weaknesses": ["容易受伤", "难以做决定", "不喜欢长期规划"],
        "description": "ISFP 是敏感温柔的艺术家，享受当下，追求美好的体验。他们重视个人价值观，是忠诚的伙伴。",
    },
    "INFP": {
        "name": "调停者",
        "traits": ["理想主义", "富有同情心", "创造力", "真诚"],
        "strengths": ["富有创意", "善于倾听", "忠于价值观", "适应力强"],
        "weaknesses": ["容易自我批评", "过于理想化", "难以处理批评"],
        "description": "INFP 是理想主义的诗人，追求内心的和谐与意义。他们富有同情心，致力于帮助他人实现潜能。",
    },
    "INTP": {
        "name": "逻辑学家",
        "traits": ["分析力强", "客观", "好奇", "独立"],
        "strengths": ["逻辑思维", "创新能力", "客观公正", "求知欲强"],
        "weaknesses": ["社交困难", "容易分心", "过于理论化"],
        "description": "INTP 是好奇的哲学家，热爱理论和抽象概念。他们追求真理，善于发现系统中的逻辑关系。",
    },
    "ESTP": {
        "name": "企业家",
        "traits": ["活力充沛", "务实", "冒险精神", "观察力强"],
        "strengths": ["行动力强", "适应力佳", "善于谈判", "活在当下"],
        "weaknesses": ["容易冲动", "缺乏耐心", "可能忽视长期后果"],
        "description": "ESTP 是活力四射的行动派，喜欢刺激和挑战。他们善于抓住机会，是天生的创业者和谈判者。",
    },
    "ESFP": {
        "name": "表演者",
        "traits": ["热情", "友好", "自发", "热爱生活"],
        "strengths": ["社交能力强", "乐观积极", "灵活适应", "善于观察"],
        "weaknesses": ["容易分心", "回避冲突", "不喜欢例行公事"],
        "description": "ESFP 是热情奔放的表演者，享受生活的每一刻。他们善于活跃气氛，是聚会的灵魂人物。",
    },
    "ENFP": {
        "name": "竞选者",
        "traits": ["热情", "创造力", "社交能力强", "理想主义"],
        "strengths": ["充满热情", "善于沟通", "创意无限", "善于激励他人"],
        "weaknesses": ["容易分心", "难以专注", "情绪波动大"],
        "description": "ENFP 是热情洋溢的创意者，充满可能性和新想法。他们善于激励他人，追求自由和真实。",
    },
    "ENTP": {
        "name": "辩论家",
        "traits": ["聪明", "好奇", "机智", "创新"],
        "strengths": ["思维敏捷", "善于辩论", "创新能力强", "适应力佳"],
        "weaknesses": ["容易厌倦", "可能过于挑衅", "难以坚持"],
        "description": "ENTP 是机智的创新者，喜欢挑战和辩论。他们善于发现新的可能性，是天生的创业者。",
    },
    "ESTJ": {
        "name": "总经理",
        "traits": ["务实", "果断", "有组织", "可靠"],
        "strengths": ["领导力强", "注重效率", "责任心强", "直接坦诚"],
        "weaknesses": ["可能过于强势", "对情感不够敏感", "固执己见"],
        "description": "ESTJ 是高效务实的管理者，重视秩序和传统。他们善于组织资源，是天生的领导者。",
    },
    "ESFJ": {
        "name": "执政官",
        "traits": ["热心", "有责任感", "善于社交", "传统"],
        "strengths": ["善于合作", "关心他人", "组织能力强", "忠诚可靠"],
        "weaknesses": ["过于在意他人看法", "回避冲突", "需要被认可"],
        "description": "ESFJ 是热心肠的协调者，重视和谐与传统。他们善于照顾他人，是社区和家庭的支柱。",
    },
    "ENFJ": {
        "name": "主人公",
        "traits": ["魅力", "同理心", "领导力", "理想主义"],
        "strengths": ["善于激励", "洞察他人需求", "有魅力", "可靠"],
        "weaknesses": ["过于理想化", "容易过度付出", "对批评敏感"],
        "description": "ENFJ 是富有魅力的领导者，善于理解和激励他人。他们追求共同成长，致力于帮助他人实现潜能。",
    },
    "ENTJ": {
        "name": "指挥官",
        "traits": ["果断", "领导力", "战略思维", "自信"],
        "strengths": ["战略眼光", "高效执行", "自信果断", "善于规划"],
        "weaknesses": ["可能显得专横", "对情感不够敏感", "不耐烦"],
        "description": "ENTJ 是果断自信的领导者，善于制定和执行战略。他们追求效率和成果，是天生的组织者和决策者。",
    },
}

# MBTI 维度与 Persona 五层结构的映射关系
MBTI_TO_PERSONA_MAPPING: Dict[str, Dict[str, Union[str, List[str]]]] = {
    "E": {
        "layer": "人际行为",
        "aspects": ["社交能量来源", "主动发起联系", "群体中的角色"],
        "behavioral_cues": ["消息密度高", "主动开启话题", "喜欢群体互动"],
    },
    "I": {
        "layer": "人际行为",
        "aspects": ["社交能量来源", "边界感强度", "深度交流偏好"],
        "behavioral_cues": ["消息经过思考", "偏好一对一交流", "需要独处时间"],
    },
    "S": {
        "layer": "说话风格",
        "aspects": ["表达方式", "话题偏好"],
        "behavioral_cues": ["具体详细的描述", "关注当下和现实", "实用主义表达"],
    },
    "N": {
        "layer": "说话风格",
        "aspects": ["表达方式", "话题偏好", "思维特点"],
        "behavioral_cues": ["抽象比喻", "关注可能性和未来", "跳跃性思维"],
    },
    "T": {
        "layer": "情感模式",
        "aspects": ["决策模式", "冲突处理", "安慰方式"],
        "behavioral_cues": ["分析问题", "直接指出解决方案", "对事不对人"],
    },
    "F": {
        "layer": "情感模式",
        "aspects": ["情感表达", "冲突处理", "安慰方式"],
        "behavioral_cues": ["情感共鸣", "维护和谐", "因人而异"],
    },
    "J": {
        "layer": "硬规则/身份",
        "aspects": ["生活方式", "工作习惯", "计划性"],
        "behavioral_cues": ["提前规划", "按时完成任务", "喜欢确定性"],
    },
    "P": {
        "layer": "硬规则/身份",
        "aspects": ["生活方式", "工作习惯", "灵活性"],
        "behavioral_cues": ["灵活应变", "保持选择开放", "享受过程"],
    },
}


class MBTITest:
    """MBTI 测试主类"""

    def __init__(self):
        self.questions = MBTI_QUESTIONS
        self.answers: Dict[int, int] = {}  # 题目ID -> 答案(0=A, 1=B)

    def interactive_test(self) -> Dict[int, int]:
        """交互式答题模式"""
        print("\n" + "=" * 60)
        print("欢迎使用 MBTI 人格测试")
        print("=" * 60)
        print("\n说明：")
        print("- 本测试共 60 题，预计用时 10-15 分钟")
        print("- 请根据你的真实倾向选择，而非理想状态")
        print("- 输入 A 或 B 作答，输入 Q 随时退出")
        print("=" * 60 + "\n")

        for question in self.questions:
            print(f"\n【第 {question.id}/60 题】")
            print(f"{question.text}")
            print(f"  A. {question.option_a}")
            print(f"  B. {question.option_b}")

            while True:
                answer = input("\n你的选择 (A/B): ").strip().upper()

                if answer == "Q":
                    print("\n测试已中断。")
                    return self.answers

                if answer in ["A", "B"]:
                    self.answers[question.id] = 0 if answer == "A" else 1
                    break
                else:
                    print("请输入 A 或 B")

        print("\n" + "=" * 60)
        print("测试完成！正在生成分析报告...")
        print("=" * 60)

        return self.answers

    def import_from_json(self, file_path: str) -> Dict[int, int]:
        """从 JSON 文件导入答题结果"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 支持两种格式：
            # 1. {"answers": {"1": 0, "2": 1, ...}}
            # 2. {"1": 0, "2": 1, ...}
            if "answers" in data:
                raw_answers = data["answers"]
            else:
                raw_answers = data

            # 转换为整数键
            self.answers = {int(k): int(v) for k, v in raw_answers.items()}

            print(f"成功导入 {len(self.answers)} 条答题记录")
            return self.answers

        except FileNotFoundError:
            print(f"错误：文件不存在 {file_path}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"错误：JSON 格式无效 {file_path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"错误：导入失败 - {e}", file=sys.stderr)
            sys.exit(1)

    def calculate_scores(self) -> MBTIResult:
        """计算各维度得分"""
        # 初始化各维度得分
        dimension_scores: Dict[Dimension, Tuple[int, int]] = {
            Dimension.EI: (0, 0),  # (E得分, I得分)
            Dimension.SN: (0, 0),  # (S得分, N得分)
            Dimension.TF: (0, 0),  # (T得分, F得分)
            Dimension.JP: (0, 0),  # (J得分, P得分)
        }

        for question in self.questions:
            if question.id not in self.answers:
                continue

            answer = self.answers[question.id]  # 0=A, 1=B
            dim = question.dimension
            left_score, right_score = dimension_scores[dim]

            # 根据题目方向和答案计算得分
            # direction=1: 选A加左维度分，选B加右维度分
            # direction=-1: 选A加右维度分，选B加左维度分
            if question.direction == 1:
                if answer == 0:  # 选A
                    left_score += 1
                else:  # 选B
                    right_score += 1
            else:  # direction == -1
                if answer == 0:  # 选A
                    right_score += 1
                else:  # 选B
                    left_score += 1

            dimension_scores[dim] = (left_score, right_score)

        # 构建 DimensionScore 对象
        scores = {
            Dimension.EI: DimensionScore(
                Dimension.EI,
                dimension_scores[Dimension.EI][0],
                dimension_scores[Dimension.EI][1],
                "外向 (Extraversion)",
                "内向 (Introversion)",
                "E",
                "I",
            ),
            Dimension.SN: DimensionScore(
                Dimension.SN,
                dimension_scores[Dimension.SN][0],
                dimension_scores[Dimension.SN][1],
                "感觉 (Sensing)",
                "直觉 (Intuition)",
                "S",
                "N",
            ),
            Dimension.TF: DimensionScore(
                Dimension.TF,
                dimension_scores[Dimension.TF][0],
                dimension_scores[Dimension.TF][1],
                "思考 (Thinking)",
                "情感 (Feeling)",
                "T",
                "F",
            ),
            Dimension.JP: DimensionScore(
                Dimension.JP,
                dimension_scores[Dimension.JP][0],
                dimension_scores[Dimension.JP][1],
                "判断 (Judging)",
                "知觉 (Perceiving)",
                "J",
                "P",
            ),
        }

        # 生成 MBTI 类型
        mbti_type = (
            scores[Dimension.EI].dominant
            + scores[Dimension.SN].dominant
            + scores[Dimension.TF].dominant
            + scores[Dimension.JP].dominant
        )

        return MBTIResult(
            mbti_type=mbti_type,
            scores=scores,
            test_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_questions=len(self.questions),
            answered_questions=len(self.answers),
        )

    def generate_report(self, result: MBTIResult, slug: str) -> str:
        """生成 Markdown 格式的分析报告"""
        desc = MBTI_DESCRIPTIONS.get(result.mbti_type, {})

        report = f"""# MBTI 人格测试分析报告

## 基本信息

- **测试代号**: {slug}
- **测试日期**: {result.test_date}
- **完成题目**: {result.answered_questions}/{result.total_questions}

---

## 测试结果

### 你的人格类型：{result.mbti_type} - {desc.get("name", "")}

{desc.get("description", "")}

---

## 维度得分明细

### 1. 能量倾向 (E/I)

| 维度 | 得分 | 占比 |
|------|------|------|
| 外向 (E) | {result.scores[Dimension.EI].left_score} | {result.scores[Dimension.EI].percentage if result.scores[Dimension.EI].dominant == "E" else 100 - result.scores[Dimension.EI].percentage}% |
| 内向 (I) | {result.scores[Dimension.EI].right_score} | {result.scores[Dimension.EI].percentage if result.scores[Dimension.EI].dominant == "I" else 100 - result.scores[Dimension.EI].percentage}% |

**主导倾向**: {result.scores[Dimension.EI].dominant} ({result.scores[Dimension.EI].percentage}%)

---

### 2. 信息获取 (S/N)

| 维度 | 得分 | 占比 |
|------|------|------|
| 感觉 (S) | {result.scores[Dimension.SN].left_score} | {result.scores[Dimension.SN].percentage if result.scores[Dimension.SN].dominant == "S" else 100 - result.scores[Dimension.SN].percentage}% |
| 直觉 (N) | {result.scores[Dimension.SN].right_score} | {result.scores[Dimension.SN].percentage if result.scores[Dimension.SN].dominant == "N" else 100 - result.scores[Dimension.SN].percentage}% |

**主导倾向**: {result.scores[Dimension.SN].dominant} ({result.scores[Dimension.SN].percentage}%)

---

### 3. 决策方式 (T/F)

| 维度 | 得分 | 占比 |
|------|------|------|
| 思考 (T) | {result.scores[Dimension.TF].left_score} | {result.scores[Dimension.TF].percentage if result.scores[Dimension.TF].dominant == "T" else 100 - result.scores[Dimension.TF].percentage}% |
| 情感 (F) | {result.scores[Dimension.TF].right_score} | {result.scores[Dimension.TF].percentage if result.scores[Dimension.TF].dominant == "F" else 100 - result.scores[Dimension.TF].percentage}% |

**主导倾向**: {result.scores[Dimension.TF].dominant} ({result.scores[Dimension.TF].percentage}%)

---

### 4. 生活方式 (J/P)

| 维度 | 得分 | 占比 |
|------|------|------|
| 判断 (J) | {result.scores[Dimension.JP].left_score} | {result.scores[Dimension.JP].percentage if result.scores[Dimension.JP].dominant == "J" else 100 - result.scores[Dimension.JP].percentage}% |
| 知觉 (P) | {result.scores[Dimension.JP].right_score} | {result.scores[Dimension.JP].percentage if result.scores[Dimension.JP].dominant == "P" else 100 - result.scores[Dimension.JP].percentage}% |

**主导倾向**: {result.scores[Dimension.JP].dominant} ({result.scores[Dimension.JP].percentage}%)

---

## 类型特征描述

### 核心特质

"""
        # 添加特质列表
        for trait in desc.get("traits", []):
            report += f"- {trait}\n"

        report += f"""
### 优势

"""
        for strength in desc.get("strengths", []):
            report += f"- {strength}\n"

        report += f"""
### 潜在挑战

"""
        for weakness in desc.get("weaknesses", []):
            report += f"- {weakness}\n"

        report += """
---

## 与 Persona 模型的关联建议

以下是将 MBTI 测试结果与现有 persona.md 进行融合的建议：

### 五层人格结构映射

"""

        # 为每个维度生成映射建议
        for letter in result.mbti_type:
            mapping = MBTI_TO_PERSONA_MAPPING.get(letter, {})
            report += f"#### {letter} 维度\n\n"
            report += f"**对应层级**: {mapping.get('layer', 'N/A')}\n\n"

            report += "**相关方面**:\n"
            for aspect in mapping.get("aspects", []):
                report += f"- {aspect}\n"

            report += "\n**行为线索**:\n"
            for cue in mapping.get("behavioral_cues", []):
                report += f"- {cue}\n"

            report += "\n"

        report += f"""---

## 原始答题数据

```json
{json.dumps(self.answers, ensure_ascii=False, indent=2)}
```

---

*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return report

    def save_results(
        self,
        result: MBTIResult,
        report: str,
        slug: str,
        base_dir: str = "selves",
    ) -> str:
        """保存测试结果到用户目录"""
        skill_dir = os.path.join(base_dir, slug)

        # 确保目录存在
        os.makedirs(skill_dir, exist_ok=True)

        # 保存 Markdown 报告
        report_path = os.path.join(skill_dir, "mbti_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        # 保存原始数据 JSON
        data_path = os.path.join(skill_dir, "mbti_data.json")
        data = {
            "mbti_type": result.mbti_type,
            "test_date": result.test_date,
            "scores": {
                dim.value: {
                    "left_score": score.left_score,
                    "right_score": score.right_score,
                    "dominant": score.dominant,
                    "percentage": score.percentage,
                }
                for dim, score in result.scores.items()
            },
            "answers": self.answers,
            "total_questions": result.total_questions,
            "answered_questions": result.answered_questions,
        }
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return report_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="MBTI 人格测试工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 mbti_test.py --mode interactive --slug my_personality
    python3 mbti_test.py --mode import --file answers.json --slug my_personality
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["interactive", "import"],
        required=True,
        help="测试模式: interactive(交互式) 或 import(导入JSON)",
    )

    parser.add_argument(
        "--slug",
        required=True,
        help="用户标识(用于保存结果到 selves/{slug}/ 目录)",
    )

    parser.add_argument(
        "--file",
        help="导入模式下的 JSON 文件路径(包含答题结果)",
    )

    parser.add_argument(
        "--base-dir",
        default="selves",
        help="Skill 基础目录(默认: selves)",
    )

    args = parser.parse_args()

    # 创建测试实例
    test = MBTITest()

    # 根据模式执行
    if args.mode == "interactive":
        test.interactive_test()
    else:  # import mode
        if not args.file:
            print("错误：导入模式需要指定 --file 参数", file=sys.stderr)
            sys.exit(1)
        test.import_from_json(args.file)

    # 检查是否有足够的数据
    if len(test.answers) < 30:
        print(f"\n警告：仅完成 {len(test.answers)}/60 题，结果可能不够准确")
        response = input("是否继续生成报告？(y/n): ").strip().lower()
        if response != "y":
            print("已取消")
            sys.exit(0)

    # 计算得分
    result = test.calculate_scores()

    # 生成报告
    report = test.generate_report(result, args.slug)

    # 保存结果
    report_path = test.save_results(result, report, args.slug, args.base_dir)

    print(f"\n✓ 分析报告已保存: {report_path}")
    print(f"✓ MBTI 类型: {result.mbti_type} - {MBTI_DESCRIPTIONS.get(result.mbti_type, {}).get('name', '')}")

    # 显示得分摘要
    print("\n维度得分摘要:")
    for dim in [Dimension.EI, Dimension.SN, Dimension.TF, Dimension.JP]:
        score = result.scores[dim]
        print(f"  {score.left_letter}/{score.right_letter}: {score.left_score}-{score.right_score} (主导: {score.dominant} {score.percentage}%)")


if __name__ == "__main__":
    main()
