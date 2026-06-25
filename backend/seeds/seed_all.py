"""种子数据 — 初始化领域、概念、题目。"""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from app.db.database import async_session, init_db
from app.models.domain import Domain, Concept, ConceptPrerequisite, Question

logger = logging.getLogger(__name__)


# ========== Python 编程 ==========

PYTHON_DOMAIN = {
    "id": "python",
    "name": "Python 编程",
    "category": "编程",
    "description": "从零开始学习 Python 编程语言，涵盖基础语法、数据结构、面向对象等核心概念。",
    "icon": "🐍",
}

PYTHON_CONCEPTS = [
    {"id": "python/variables", "name": "变量与数据类型", "description": "Python 中的变量声明、基本数据类型（int, float, str, bool）", "level": 1, "tags": ["基础"], "prerequisites": []},
    {"id": "python/operators", "name": "运算符", "description": "算术运算符、比较运算符、逻辑运算符", "level": 1, "tags": ["基础"], "prerequisites": ["python/variables"]},
    {"id": "python/conditionals", "name": "条件语句", "description": "if/elif/else 条件判断", "level": 2, "tags": ["控制流"], "prerequisites": ["python/operators"]},
    {"id": "python/loops", "name": "循环", "description": "for 循环和 while 循环，break/continue", "level": 2, "tags": ["控制流"], "prerequisites": ["python/conditionals"]},
    {"id": "python/lists", "name": "列表", "description": "列表的创建、索引、切片、常用方法", "level": 2, "tags": ["数据结构"], "prerequisites": ["python/loops"]},
    {"id": "python/dicts", "name": "字典", "description": "字典的创建、访问、遍历", "level": 3, "tags": ["数据结构"], "prerequisites": ["python/lists"]},
    {"id": "python/functions", "name": "函数", "description": "函数定义、参数、返回值、作用域", "level": 3, "tags": ["函数"], "prerequisites": ["python/lists"]},
    {"id": "python/classes", "name": "类与对象", "description": "面向对象编程：类定义、继承、多态", "level": 4, "tags": ["OOP"], "prerequisites": ["python/functions", "python/dicts"]},
    {"id": "python/exceptions", "name": "异常处理", "description": "try/except/finally，自定义异常", "level": 4, "tags": ["错误处理"], "prerequisites": ["python/functions"]},
    {"id": "python/modules", "name": "模块与包", "description": "import 机制、标准库、第三方包", "level": 4, "tags": ["工程"], "prerequisites": ["python/functions"]},
]

PYTHON_QUESTIONS = [
    # 变量与数据类型
    {"concept_id": "python/variables", "question_type": "choice", "content": "Python 中以下哪个是合法的变量名？", "options": ["A. 2name", "B. my_name", "C. class", "D. my-name"], "answer": "B", "explanation": "变量名不能以数字开头（A），不能是保留字（C），不能包含连字符（D）。下划线是合法的。", "difficulty": 2},
    {"concept_id": "python/variables", "question_type": "choice", "content": "type(3.14) 的结果是什么？", "options": ["A. <class 'int'>", "B. <class 'float'>", "C. <class 'str'>", "D. <class 'decimal'>"], "answer": "B", "explanation": "3.14 是浮点数，type() 返回 <class 'float'>。", "difficulty": 2},
    {"concept_id": "python/variables", "question_type": "fill", "content": "在 Python 中，将整数 42 赋值给变量 x 的语句是：____", "answer": "x = 42", "explanation": "Python 使用单等号 = 进行赋值。", "difficulty": 1},
    # 运算符
    {"concept_id": "python/operators", "question_type": "choice", "content": "Python 中 7 // 2 的结果是？", "options": ["A. 3.5", "B. 3", "C. 4", "D. 1"], "answer": "B", "explanation": "// 是整除运算符，7 // 2 = 3（向下取整）。", "difficulty": 2},
    {"concept_id": "python/operators", "question_type": "choice", "content": "以下哪个表达式的结果为 True？", "options": ["A. 5 > 3 and 2 < 1", "B. not True or False", "C. 3 == 3 and 4 != 4", "D. 1 < 2 or 3 > 5"], "answer": "D", "explanation": "A: True and False = False; B: False or False = False; C: True and False = False; D: True or False = True。", "difficulty": 3},
    # 条件语句
    {"concept_id": "python/conditionals", "question_type": "code", "content": "写一段代码：如果变量 x 大于 0，打印 '正数'；如果等于 0，打印 '零'；否则打印 '负数'。", "answer": "if x > 0:\n    print('正数')\nelif x == 0:\n    print('零')\nelse:\n    print('负数')", "explanation": "使用 if/elif/else 结构进行多条件判断。", "difficulty": 3},
    # 循环
    {"concept_id": "python/loops", "question_type": "code", "content": "使用 for 循环计算 1 到 100 的和。", "answer": "total = 0\nfor i in range(1, 101):\n    total += i\nprint(total)", "explanation": "range(1, 101) 生成 1 到 100 的序列，累加到 total。", "difficulty": 3},
    {"concept_id": "python/loops", "question_type": "choice", "content": "range(0, 10, 2) 生成的序列是？", "options": ["A. [0, 2, 4, 6, 8]", "B. [0, 2, 4, 6, 8, 10]", "C. [2, 4, 6, 8]", "D. [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]"], "answer": "A", "explanation": "range(0, 10, 2) 从 0 开始，步长为 2，到 10 之前结束。", "difficulty": 3},
    # 列表
    {"concept_id": "python/lists", "question_type": "choice", "content": "lst = [1, 2, 3, 4, 5]，lst[1:3] 的结果是？", "options": ["A. [1, 2]", "B. [2, 3]", "C. [1, 2, 3]", "D. [2, 3, 4]"], "answer": "B", "explanation": "切片 [1:3] 取索引 1 到 2（不含 3），即 [2, 3]。", "difficulty": 3},
    {"concept_id": "python/lists", "question_type": "code", "content": "如何向列表末尾添加一个元素？写出代码示例。", "answer": "lst.append(element)", "explanation": "append() 方法在列表末尾添加一个元素。", "difficulty": 2},
    # 字典
    {"concept_id": "python/dicts", "question_type": "choice", "content": "d = {'a': 1, 'b': 2}，d.get('c', 0) 的结果是？", "options": ["A. None", "B. 0", "C. 报错", "D. 'c'"], "answer": "B", "explanation": "get() 方法在键不存在时返回默认值 0。", "difficulty": 3},
    # 函数
    {"concept_id": "python/functions", "question_type": "code", "content": "写一个函数，接收一个列表，返回列表中所有偶数的和。", "answer": "def sum_even(numbers):\n    return sum(n for n in numbers if n % 2 == 0)", "explanation": "使用生成器表达式过滤偶数并求和。", "difficulty": 4},
    # 类与对象
    {"concept_id": "python/classes", "question_type": "code", "content": "定义一个 Animal 类，有 name 属性和 speak() 方法。", "answer": "class Animal:\n    def __init__(self, name):\n        self.name = name\n    \n    def speak(self):\n        return f'{self.name} makes a sound'", "explanation": "使用 __init__ 初始化属性，定义实例方法。", "difficulty": 4},
]


# ========== 金融基础（导数入门） ==========

FINANCE_DOMAIN = {
    "id": "finance-basics",
    "name": "金融基础",
    "category": "金融",
    "description": "金融学入门知识，涵盖货币时间价值、风险与收益、投资基础等核心概念。",
    "icon": "💰",
}

FINANCE_CONCEPTS = [
    {"id": "finance/money-value", "name": "货币时间价值", "description": "今天的 1 元比明天的 1 元更值钱——理解现值与终值", "level": 1, "tags": ["基础"], "prerequisites": []},
    {"id": "finance/interest", "name": "利率与利息", "description": "单利、复利的计算，年利率与实际利率", "level": 1, "tags": ["基础"], "prerequisites": ["finance/money-value"]},
    {"id": "finance/risk-return", "name": "风险与收益", "description": "风险与收益的关系，风险厌恶，风险溢价", "level": 2, "tags": ["投资"], "prerequisites": ["finance/interest"]},
    {"id": "finance/stocks", "name": "股票基础", "description": "什么是股票，股票市场如何运作，市盈率等基本指标", "level": 2, "tags": ["投资"], "prerequisites": ["finance/risk-return"]},
    {"id": "finance/bonds", "name": "债券基础", "description": "债券的定义、种类、定价原理", "level": 3, "tags": ["投资"], "prerequisites": ["finance/interest", "finance/risk-return"]},
    {"id": "finance/portfolio", "name": "投资组合", "description": "分散投资、资产配置、有效前沿", "level": 4, "tags": ["投资"], "prerequisites": ["finance/stocks", "finance/bonds"]},
]

FINANCE_QUESTIONS = [
    {"concept_id": "finance/money-value", "question_type": "choice", "content": "假设年利率 5%，今天的 100 元一年后价值多少？", "options": ["A. 100 元", "B. 105 元", "C. 95 元", "D. 110 元"], "answer": "B", "explanation": "终值 = 本金 × (1 + 利率) = 100 × 1.05 = 105 元。", "difficulty": 2},
    {"concept_id": "finance/interest", "question_type": "choice", "content": "1000 元本金，年利率 6%，复利计算 3 年后的终值是多少？", "options": ["A. 1180 元", "B. 1191.02 元", "C. 1200 元", "D. 1180.02 元"], "answer": "B", "explanation": "复利终值 = 1000 × (1.06)³ = 1000 × 1.191016 ≈ 1191.02 元。", "difficulty": 3},
    {"concept_id": "finance/risk-return", "question_type": "choice", "content": "以下哪种投资通常风险最低？", "options": ["A. 股票", "B. 企业债券", "C. 国债", "D. 期货"], "answer": "C", "explanation": "国债由政府信用背书，违约风险极低，是典型的低风险投资。", "difficulty": 2},
    {"concept_id": "finance/stocks", "question_type": "choice", "content": "市盈率（P/E）的计算公式是？", "options": ["A. 股价 / 每股收益", "B. 每股收益 / 股价", "C. 总市值 / 净利润", "D. A 和 C 都对"], "answer": "D", "explanation": "市盈率 = 股价 / 每股收益 = 总市值 / 净利润，两种表述等价。", "difficulty": 3},
    {"concept_id": "finance/bonds", "question_type": "choice", "content": "当市场利率上升时，已发行债券的价格通常会？", "options": ["A. 上升", "B. 下降", "C. 不变", "D. 不确定"], "answer": "B", "explanation": "利率上升 → 新债券更有吸引力 → 旧债券价格下降以保持竞争力。", "difficulty": 3},
    {"concept_id": "finance/portfolio", "question_type": "choice", "content": "分散投资的主要目的是？", "options": ["A. 提高收益", "B. 降低非系统性风险", "C. 消除所有风险", "D. 降低交易成本"], "answer": "B", "explanation": "分散投资可以降低个别资产的非系统性风险，但无法消除系统性风险。", "difficulty": 3},
]


# ========== CPA 会计 ==========

CPA_DOMAIN = {
    "id": "cpa-accounting",
    "name": "CPA 会计",
    "category": "考证",
    "description": "注册会计师（CPA）考试《会计》科目核心知识点，涵盖会计要素、会计分录、财务报表等。",
    "icon": "📊",
}

CPA_CONCEPTS = [
    {"id": "cpa/elements", "name": "会计要素", "description": "资产、负债、所有者权益、收入、费用、利润六大要素", "level": 1, "tags": ["基础"], "prerequisites": []},
    {"id": "cpa/equation", "name": "会计等式", "description": "资产 = 负债 + 所有者权益", "level": 1, "tags": ["基础"], "prerequisites": ["cpa/elements"]},
    {"id": "cpa/debit-credit", "name": "借贷记账法", "description": "借方与贷方，记账规则：有借必有贷，借贷必相等", "level": 2, "tags": ["核心"], "prerequisites": ["cpa/equation"]},
    {"id": "cpa/entries", "name": "会计分录", "description": "常见经济业务的会计分录编制", "level": 2, "tags": ["核心"], "prerequisites": ["cpa/debit-credit"]},
    {"id": "cpa/assets", "name": "资产类科目", "description": "货币资金、应收账款、存货、固定资产等", "level": 3, "tags": ["科目"], "prerequisites": ["cpa/entries"]},
    {"id": "cpa/liabilities", "name": "负债类科目", "description": "应付账款、应付职工薪酬、应交税费等", "level": 3, "tags": ["科目"], "prerequisites": ["cpa/entries"]},
]

CPA_QUESTIONS = [
    {"concept_id": "cpa/elements", "question_type": "choice", "content": "以下哪项属于资产？", "options": ["A. 应付账款", "B. 预收账款", "C. 应收账款", "D. 实收资本"], "answer": "C", "explanation": "应收账款是企业应收客户的款项，属于资产。应付账款和预收账款是负债，实收资本是所有者权益。", "difficulty": 2},
    {"concept_id": "cpa/equation", "question_type": "choice", "content": "企业资产总额 500 万，负债总额 300 万，所有者权益是多少？", "options": ["A. 800 万", "B. 200 万", "C. 500 万", "D. 300 万"], "answer": "B", "explanation": "资产 = 负债 + 所有者权益 → 所有者权益 = 500 - 300 = 200 万。", "difficulty": 2},
    {"concept_id": "cpa/debit-credit", "question_type": "choice", "content": "在借贷记账法中，资产类账户的增加记在哪方？", "options": ["A. 借方", "B. 贷方", "C. 都可以", "D. 视情况而定"], "answer": "A", "explanation": "资产增加记借方，减少记贷方。", "difficulty": 2},
    {"concept_id": "cpa/entries", "question_type": "code", "content": "企业用银行存款 10 万元购买原材料，请写出会计分录。", "answer": "借：原材料 100,000\n贷：银行存款 100,000", "explanation": "原材料增加（资产增加记借方），银行存款减少（资产减少记贷方）。", "difficulty": 3},
    {"concept_id": "cpa/assets", "question_type": "choice", "content": "以下哪项不属于流动资产？", "options": ["A. 货币资金", "B. 应收账款", "C. 固定资产", "D. 存货"], "answer": "C", "explanation": "固定资产是长期资产，不属于流动资产。", "difficulty": 2},
    {"concept_id": "cpa/liabilities", "question_type": "choice", "content": "企业月末计提员工工资但尚未发放，应贷记的科目是？", "options": ["A. 应付职工薪酬", "B. 应付账款", "C. 其他应付款", "D. 预收账款"], "answer": "A", "explanation": "计提工资贷记「应付职工薪酬」。", "difficulty": 3},
]


# ========== 数学（导数） ==========

MATH_DOMAIN = {
    "id": "math-calculus",
    "name": "微积分入门",
    "category": "数学",
    "description": "微积分核心概念入门，从极限到导数，适合高中生和大学新生。",
    "icon": "📐",
}

MATH_CONCEPTS = [
    {"id": "math/limits", "name": "极限", "description": "函数极限的定义、直观理解、基本计算", "level": 1, "tags": ["基础"], "prerequisites": []},
    {"id": "math/continuity", "name": "连续性", "description": "函数连续的定义、间断点类型", "level": 2, "tags": ["基础"], "prerequisites": ["math/limits"]},
    {"id": "math/derivative-def", "name": "导数的定义", "description": "导数的几何意义（切线斜率）、物理意义（瞬时速度）", "level": 2, "tags": ["核心"], "prerequisites": ["math/limits"]},
    {"id": "math/derivative-rules", "name": "求导法则", "description": "幂函数、指数函数、对数函数的求导，四则运算法则", "level": 3, "tags": ["核心"], "prerequisites": ["math/derivative-def"]},
    {"id": "math/chain-rule", "name": "链式法则", "description": "复合函数的求导：(f(g(x)))' = f'(g(x)) · g'(x)", "level": 4, "tags": ["核心"], "prerequisites": ["math/derivative-rules"]},
    {"id": "math/derivative-app", "name": "导数的应用", "description": "单调性、极值、最值问题", "level": 4, "tags": ["应用"], "prerequisites": ["math/derivative-rules"]},
]

MATH_QUESTIONS = [
    {"concept_id": "math/limits", "question_type": "choice", "content": "lim(x→0) sin(x)/x 的值是？", "options": ["A. 0", "B. 1", "C. ∞", "D. 不存在"], "answer": "B", "explanation": "这是重要极限之一，lim(x→0) sin(x)/x = 1。", "difficulty": 2},
    {"concept_id": "math/continuity", "question_type": "choice", "content": "函数 f(x) = 1/x 在 x=0 处是？", "options": ["A. 连续", "B. 间断（可去）", "C. 间断（跳跃）", "D. 间断（无穷）"], "answer": "D", "explanation": "x→0 时 1/x → ∞，是无穷间断点。", "difficulty": 3},
    {"concept_id": "math/derivative-def", "question_type": "choice", "content": "f(x) = x² 在 x=3 处的导数是？", "options": ["A. 3", "B. 6", "C. 9", "D. 2"], "answer": "B", "explanation": "f'(x) = 2x，f'(3) = 6。几何意义：x=3 处切线斜率为 6。", "difficulty": 2},
    {"concept_id": "math/derivative-rules", "question_type": "code", "content": "求 f(x) = 3x⁴ - 2x² + 5x - 1 的导数。", "answer": "f'(x) = 12x³ - 4x + 5", "explanation": "逐项求导：(3x⁴)' = 12x³, (-2x²)' = -4x, (5x)' = 5, (-1)' = 0。", "difficulty": 3},
    {"concept_id": "math/chain-rule", "question_type": "code", "content": "求 f(x) = sin(2x) 的导数。", "answer": "f'(x) = 2cos(2x)", "explanation": "链式法则：外层 sin(u) 求导得 cos(u)，内层 2x 求导得 2，相乘得 2cos(2x)。", "difficulty": 4},
    {"concept_id": "math/derivative-app", "question_type": "choice", "content": "f(x) = x³ - 3x 的极小值点是？", "options": ["A. x = -1", "B. x = 0", "C. x = 1", "D. x = 3"], "answer": "C", "explanation": "f'(x) = 3x² - 3 = 0 → x = ±1。f''(x) = 6x，f''(1) = 6 > 0，所以 x=1 是极小值点。", "difficulty": 4},
]


# ========== 注册种子数据 ==========

ALL_SEEDS = [
    (PYTHON_DOMAIN, PYTHON_CONCEPTS, PYTHON_QUESTIONS),
    (FINANCE_DOMAIN, FINANCE_CONCEPTS, FINANCE_QUESTIONS),
    (CPA_DOMAIN, CPA_CONCEPTS, CPA_QUESTIONS),
    (MATH_DOMAIN, MATH_CONCEPTS, MATH_QUESTIONS),
]


async def seed_database():
    """写入种子数据。"""
    await init_db()

    async with async_session() as session:
        for domain_data, concepts_data, questions_data in ALL_SEEDS:
            # 检查领域是否已存在
            existing = await session.execute(
                select(Domain).where(Domain.id == domain_data["id"])
            )
            if existing.scalar_one_or_none():
                logger.info(f"领域 {domain_data['name']} 已存在，跳过")
                continue

            # 创建领域
            domain = Domain(**domain_data)
            session.add(domain)

            # 创建概念
            for i, concept_data in enumerate(concepts_data):
                concept = Concept(**concept_data, sort_order=i)
                session.add(concept)

            # 创建前置关系
            for concept_data in concepts_data:
                for prereq_id in concept_data.get("prerequisites", []):
                    prereq = ConceptPrerequisite(
                        concept_id=concept_data["id"],
                        prerequisite_id=prereq_id,
                    )
                    session.add(prereq)

            # 创建题目
            for q_data in questions_data:
                question = Question(
                    domain_id=domain_data["id"],
                    **q_data,
                )
                session.add(question)

            logger.info(f"✅ 注册领域: {domain_data['name']} ({len(concepts_data)} 概念, {len(questions_data)} 题目)")

        await session.commit()
        logger.info("🎉 所有种子数据注册完成！")


if __name__ == "__main__":
    asyncio.run(seed_database())
