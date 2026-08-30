# -*- coding: utf-8 -*-
"""样例题目种子脚本：为「题库 / 相似题推荐」页面填充一批跨考点样例数据。

覆盖领域词汇表中的 6 大迷思概念类别（化学平衡 / 氧化还原反应 / 摩尔计算 /
有机化学 / 化学用语 / 物构知识），题型、难度多样，便于在页面验证「查相似题」。

用法（需在 chemai-backend 目录下执行，让 ``sqlite:///./chemai.db`` 指向 dev 库）::

    ./venv/bin/python scripts/seed_sample_questions.py

幂等：以 ``source_name == "样例题库"`` 标记，已存在则跳过，不重复导入。
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import select

# 让脚本能在任意子目录下被直接执行时仍 import 到 app 包（项目根目录）。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.core.enums import Difficulty, QuestionType
from app.models import Question, Teacher
from app.services.vector_search import vector_search

SAMPLE_MARKER = "样例题库"

# 每道题字段与 Question 模型列一一对应（type/difficulty 传枚举成员）。
QUESTIONS: list[dict] = [
    # ---------------- 化学平衡 ----------------
    {
        "content": "可逆反应 2NO2(g) ⇌ N2O4(g)（正反应为放热反应）达到平衡后，下列措施能使平衡向正反应方向移动的是（　）",
        "type": QuestionType.SINGLE_CHOICE,
        "difficulty": Difficulty.MEDIUM,
        "options": ["A. 升高温度", "B. 降低温度", "C. 加入催化剂", "D. 减小压强"],
        "answer": "B",
        "analysis": "正反应放热，降低温度平衡向放热方向（正反应）移动；催化剂不影响平衡；该反应气体分子数减少，减小压强平衡逆向移动。",
        "knowledge_points": ["化学平衡", "勒夏特列原理"],
        "score": 3.0,
    },
    {
        "content": "在一定条件下，可逆反应 H2(g) + I2(g) ⇌ 2HI(g) 达到化学平衡状态的标志是（　）",
        "type": QuestionType.SINGLE_CHOICE,
        "difficulty": Difficulty.HARD,
        "options": ["A. 正反应速率与逆反应速率相等", "B. 混合气体总压强不再改变", "C. H2、I2、HI 浓度之比为 1:1:2", "D. 单位时间生成 n mol H2 同时生成 2n mol HI"],
        "answer": "A",
        "analysis": "该反应前后气体分子数不变，压强始终不变，B 不能作为标志；浓度比 1:1:2 只是偶然比值，C 错；D 描述的生成方向相同，不能体现正逆相等。正逆速率相等是平衡的本质标志，A 正确。",
        "knowledge_points": ["化学平衡", "平衡状态判断"],
        "score": 3.0,
    },
    {
        "content": "已知反应 N2(g) + 3H2(g) ⇌ 2NH3(g) 的平衡常数 K = c²(NH3)/[c(N2)·c³(H2)]。某温度下平衡时 c(N2)=1.0 mol/L，c(H2)=1.0 mol/L，c(NH3)=2.0 mol/L，该反应的平衡常数 K 为（　）",
        "type": QuestionType.CALCULATION,
        "difficulty": Difficulty.HARD,
        "options": ["A. 2", "B. 4", "C. 1", "D. 0.5"],
        "answer": "B",
        "analysis": "K = 2.0² / (1.0 × 1.0³) = 4。",
        "knowledge_points": ["化学平衡", "平衡常数"],
        "score": 4.0,
    },
    {
        "content": "对可逆反应，升高温度时吸热反应方向的速率增大得更快，平衡向吸热方向移动。",
        "type": QuestionType.TRUE_FALSE,
        "difficulty": Difficulty.MEDIUM,
        "answer": "对",
        "analysis": "温度对吸热反应方向的速率影响更大，升温平衡向吸热方向移动，符合勒夏特列原理。",
        "knowledge_points": ["化学平衡", "勒夏特列原理"],
        "score": 2.0,
    },
    {
        "content": "下列措施中，能提高合成氨反应 N2(g) + 3H2(g) ⇌ 2NH3(g)（正反应放热）的 NH3 产率的是（　）",
        "type": QuestionType.MULTI_CHOICE,
        "difficulty": Difficulty.HARD,
        "options": ["A. 增大压强", "B. 升高温度", "C. 及时分离出 NH3", "D. 使用高效催化剂"],
        "answer": "A,C",
        "analysis": "增大压强平衡向气体分子数减少的正方向移动，提高产率；及时分离 NH3 使平衡正向移动；正反应放热，升温使产率下降；催化剂只改速率不改平衡。",
        "knowledge_points": ["化学平衡", "勒夏特列原理"],
        "score": 4.0,
    },

    # ---------------- 摩尔计算 ----------------
    {
        "content": "标准状况（0 ℃、101 kPa）下，22.4 L CO2 的物质的量约为（　）",
        "type": QuestionType.SINGLE_CHOICE,
        "difficulty": Difficulty.EASY,
        "options": ["A. 1 mol", "B. 2 mol", "C. 0.5 mol", "D. 44 mol"],
        "answer": "A",
        "analysis": "标准状况下气体摩尔体积约为 22.4 L/mol，22.4 L ÷ 22.4 L/mol = 1 mol。",
        "knowledge_points": ["摩尔计算", "气体摩尔体积"],
        "score": 2.0,
    },
    {
        "content": "将 5.85 g NaCl（摩尔质量 58.5 g/mol）溶于适量水配成 500 mL 溶液，所得溶液的物质的量浓度为（　）",
        "type": QuestionType.CALCULATION,
        "difficulty": Difficulty.MEDIUM,
        "options": ["A. 0.1 mol/L", "B. 0.2 mol/L", "C. 0.5 mol/L", "D. 1.0 mol/L"],
        "answer": "B",
        "analysis": "n(NaCl) = 5.85 g ÷ 58.5 g/mol = 0.1 mol；c = 0.1 mol ÷ 0.5 L = 0.2 mol/L。",
        "knowledge_points": ["摩尔计算", "物质的量浓度"],
        "score": 3.0,
    },
    {
        "content": "设 NA 为阿伏加德罗常数的值。下列说法正确的是（　）",
        "type": QuestionType.SINGLE_CHOICE,
        "difficulty": Difficulty.MEDIUM,
        "options": ["A. 18 g H2O 中含有的水分子数为 NA", "B. 1 mol Cl2 中含有的原子数为 NA", "C. 标准状况下 22.4 L 苯中含有的分子数为 NA", "D. 1 L 0.1 mol/L 的 NaCl 溶液中含 Na+ 数为 0.5NA"],
        "answer": "A",
        "analysis": "18 g H2O 为 1 mol，含 NA 个水分子，A 对；1 mol Cl2 含 2 mol 原子，B 错；标准状况下苯为液体，C 错；1 L 0.1 mol/L NaCl 含 0.1 mol Na+，D 错。",
        "knowledge_points": ["摩尔计算", "阿伏加德罗常数"],
        "score": 3.0,
    },
    {
        "content": "标准状况下，2.24 L O2 与足量 H2 反应生成水（2H2 + O2 = 2H2O），消耗 H2 的质量为____ g。",
        "type": QuestionType.FILL_BLANK,
        "difficulty": Difficulty.HARD,
        "answer": "0.4",
        "analysis": "n(O2) = 2.24/22.4 = 0.1 mol；按方程式 n(H2) = 2×n(O2) = 0.2 mol；m(H2) = 0.2×2 = 0.4 g。",
        "knowledge_points": ["摩尔计算", "化学方程式计算"],
        "score": 4.0,
    },

    # ---------------- 有机化学 ----------------
    {
        "content": "下列物质中，属于烃的是（　）",
        "type": QuestionType.SINGLE_CHOICE,
        "difficulty": Difficulty.EASY,
        "options": ["A. CH4", "B. C2H5OH", "C. CH3COOH", "D. CCl4"],
        "answer": "A",
        "analysis": "只含碳、氢两种元素的有机物称为烃。CH4 是烃，其余含氧或氯元素。",
        "knowledge_points": ["有机化学", "烃"],
        "score": 2.0,
    },
    {
        "content": "乙醇与乙酸在浓硫酸催化、加热条件下反应的产物是（　）",
        "type": QuestionType.SINGLE_CHOICE,
        "difficulty": Difficulty.MEDIUM,
        "options": ["A. 乙酸乙酯", "B. 乙醚", "C. 乙烯", "D. 乙醛"],
        "answer": "A",
        "analysis": "醇与羧酸在浓硫酸催化下发生酯化反应生成酯和水，产物为乙酸乙酯。",
        "knowledge_points": ["有机化学", "酯化反应"],
        "score": 3.0,
    },
    {
        "content": "某有机物 A 能与 Na 反应放出 H2，能使酸性 KMnO4 溶液褪色，且能发生酯化反应。则 A 分子中一定含有的官能团是（　）",
        "type": QuestionType.INFERENCE,
        "difficulty": Difficulty.HARD,
        "options": ["A. 羟基", "B. 醛基", "C. 碳碳双键", "D. 羧基"],
        "answer": "A",
        "analysis": "能与 Na 反应放 H2 且能酯化，说明含羟基（醇）或羧基；能使酸性 KMnO4 褪色的醇羟基符合，故一定含羟基。",
        "knowledge_points": ["有机化学", "官能团"],
        "score": 4.0,
    },
    {
        "content": "苯分子中的碳碳键是介于碳碳单键和碳碳双键之间的一种特殊化学键，既能使溴水褪色，也能使酸性 KMnO4 溶液褪色。",
        "type": QuestionType.TRUE_FALSE,
        "difficulty": Difficulty.MEDIUM,
        "answer": "错",
        "analysis": "苯的特殊键结构描述正确，但苯不能使溴水和酸性 KMnO4 溶液褪色（特殊稳定性掩盖不饱和键特性），故整体判断为错。",
        "knowledge_points": ["有机化学", "苯的结构"],
        "score": 2.0,
    },

    # ---------------- 化学用语 ----------------
    {
        "content": "下列物质的化学式书写正确的是（　）",
        "type": QuestionType.SINGLE_CHOICE,
        "difficulty": Difficulty.EASY,
        "options": ["A. 硫酸 H2SO4", "B. 碳酸钠 NaCO3", "C. 氢氧化钙 CaOH2", "D. 氯化铁 FeCl2"],
        "answer": "A",
        "analysis": "碳酸钠为 Na2CO3，氢氧化钙为 Ca(OH)2，氯化铁为 FeCl3（FeCl2 为氯化亚铁），只有 H2SO4 正确。",
        "knowledge_points": ["化学用语", "化学式"],
        "score": 2.0,
    },
    {
        "content": "配平化学方程式：____Fe + ____O2 点燃 ____Fe3O4（依次填系数，用逗号分隔）。",
        "type": QuestionType.FILL_BLANK,
        "difficulty": Difficulty.MEDIUM,
        "answer": "3,2,1",
        "analysis": "3Fe + 2O2 = Fe3O4，系数依次为 3、2、1。",
        "knowledge_points": ["化学用语", "化学方程式配平"],
        "score": 3.0,
    },
    {
        "content": "在化合物中，金属元素一定显正价，非金属元素一定显负价。",
        "type": QuestionType.TRUE_FALSE,
        "difficulty": Difficulty.EASY,
        "answer": "错",
        "analysis": "非金属元素在化合物中也可显正价（如 HClO 中 Cl 为 +1 价），故判断错误。",
        "knowledge_points": ["化学用语", "化合价"],
        "score": 2.0,
    },

    # ---------------- 物构知识 ----------------
    {
        "content": "决定元素化学性质的主要因素是（　）",
        "type": QuestionType.SINGLE_CHOICE,
        "difficulty": Difficulty.MEDIUM,
        "options": ["A. 质子数", "B. 中子数", "C. 最外层电子数", "D. 核电荷数"],
        "answer": "C",
        "analysis": "元素的化学性质主要取决于原子的最外层电子数。",
        "knowledge_points": ["物构知识", "核外电子排布"],
        "score": 3.0,
    },
    {
        "content": "决定元素种类的是（　）",
        "type": QuestionType.SINGLE_CHOICE,
        "difficulty": Difficulty.EASY,
        "options": ["A. 质子数（核电荷数）", "B. 中子数", "C. 电子数", "D. 相对原子质量"],
        "answer": "A",
        "analysis": "元素是质子数（核电荷数）相同的一类原子的总称，决定元素种类的是质子数。",
        "knowledge_points": ["物构知识", "元素"],
        "score": 2.0,
    },
    {
        "content": "原子核由质子和中子构成，但氢原子（氕）的原子核中没有中子。",
        "type": QuestionType.TRUE_FALSE,
        "difficulty": Difficulty.EASY,
        "answer": "对",
        "analysis": "普通氢原子（氕）的原子核只有一个质子，不含中子。",
        "knowledge_points": ["物构知识", "原子结构"],
        "score": 2.0,
    },
    {
        "content": "下列关于元素周期表的说法中，正确的是（　）",
        "type": QuestionType.SINGLE_CHOICE,
        "difficulty": Difficulty.HARD,
        "options": ["A. 同一周期元素从左到右，原子半径逐渐增大", "B. 同一主族元素从上到下，金属性逐渐增强", "C. 最外层电子数相同的元素一定在同一族", "D. 元素周期表共有 7 个副族"],
        "answer": "B",
        "analysis": "同周期从左到右原子半径减小，A 错；同主族从上到下金属性增强，B 对；He 与 Mg 最外层电子数相同但不同族，C 错；元素周期表含 7 个主族、7 个副族、1 个 0 族和 1 个第 VIII 族，D 表述不完整。",
        "knowledge_points": ["物构知识", "元素周期表"],
        "score": 4.0,
    },

    # ---------------- 氧化还原反应 ----------------
    {
        "content": "在反应 2Fe + 3Cl2 点燃 2FeCl3 中，被氧化的物质是（　）",
        "type": QuestionType.SINGLE_CHOICE,
        "difficulty": Difficulty.MEDIUM,
        "options": ["A. Fe", "B. Cl2", "C. FeCl3", "D. 无法判断"],
        "answer": "A",
        "analysis": "Fe 由 0 价升高到 +3 价，失电子被氧化，作还原剂。",
        "knowledge_points": ["氧化还原反应", "氧化剂与还原剂"],
        "score": 3.0,
    },
    {
        "content": "反应 CuO + H2 加热 Cu + H2O 中，H2 作还原剂，CuO 作氧化剂。",
        "type": QuestionType.TRUE_FALSE,
        "difficulty": Difficulty.EASY,
        "answer": "对",
        "analysis": "H2 中 H 由 0 价升高到 +1 价，失电子作还原剂；CuO 中 Cu 由 +2 价降低到 0 价，得电子作氧化剂。",
        "knowledge_points": ["氧化还原反应", "氧化剂与还原剂"],
        "score": 2.0,
    },
]


def seed() -> None:
    """导入样例题目（幂等：已存在则跳过）。"""
    with SessionLocal() as db:
        teacher = db.execute(select(Teacher)).scalars().first()
        if teacher is None:
            print("未找到教师账号，请先运行 scripts/seed_dev_account.py")
            return

        existing = db.execute(
            select(Question).where(Question.source_name == SAMPLE_MARKER)
        ).scalars().first()
        if existing is not None:
            total = db.query(Question).filter(Question.source_name == SAMPLE_MARKER).count()
            print(f"样例题目已存在（共 {total} 道），跳过。")
            return

        created: list[Question] = []
        for raw in QUESTIONS:
            q = Question(
                teacher_id=teacher.id,
                source_name=SAMPLE_MARKER,
                region="北京市",
                year=2024,
                **raw,
            )
            db.add(q)
            created.append(q)

        db.flush()  # 让每个题目拿到自增 id，供向量索引使用
        for q in created:
            vector_search.index_question(q)
        db.commit()

        print(f"✓ 已导入 {len(created)} 道样例题目（source_name={SAMPLE_MARKER!r}）")
        print("  刷新题库页面即可看到新题目；点击「查相似题」验证相似题推荐。")


if __name__ == "__main__":
    seed()
