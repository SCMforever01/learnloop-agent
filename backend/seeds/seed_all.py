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


# ========== 英语学习 ==========

ENGLISH_DOMAIN = {
    "id": "english",
    "name": "英语学习",
    "category": "语言",
    "description": "英语核心语法与词汇学习，涵盖音标、时态、从句、写作等。",
    "icon": "🇬🇧",
}

ENGLISH_CONCEPTS = [
    {"id": "english/phonetics", "name": "音标基础", "description": "48个国际音标、元音与辅音、拼读规则", "level": 1, "tags": ["基础"], "prerequisites": []},
    {"id": "english/nouns", "name": "名词与代词", "description": "可数/不可数名词、人称代词、物主代词", "level": 1, "tags": ["基础"], "prerequisites": ["english/phonetics"]},
    {"id": "english/tenses", "name": "动词时态", "description": "一般现在/过去/将来、现在进行、现在完成等8种时态", "level": 2, "tags": ["核心"], "prerequisites": ["english/nouns"]},
    {"id": "english/passive", "name": "被动语态", "description": "被动语态的构成与用法、各时态的被动形式", "level": 3, "tags": ["核心"], "prerequisites": ["english/tenses"]},
    {"id": "english/clauses", "name": "定语从句", "description": "关系代词 who/which/that、关系副词 when/where/why", "level": 3, "tags": ["核心"], "prerequisites": ["english/tenses"]},
    {"id": "english/subjunctive", "name": "虚拟语气", "description": "if条件句的虚拟、wish/suggest等词的虚拟用法", "level": 4, "tags": ["进阶"], "prerequisites": ["english/tenses"]},
    {"id": "english/writing", "name": "写作基础", "description": "段落结构、主题句、连接词、常见文体", "level": 4, "tags": ["应用"], "prerequisites": ["english/clauses"]},
]

ENGLISH_QUESTIONS = [
    {"concept_id": "english/phonetics", "question_type": "choice", "content": "以下哪个是双元音？", "options": ["A. /i:/", "B. /aɪ/", "C. /p/", "D. /m/"], "answer": "B", "explanation": "/aɪ/ 是双元音，由 /a/ 滑向 /ɪ/。/i:/ 是长元音，/p/ /m/ 是辅音。", "difficulty": 1},
    {"concept_id": "english/nouns", "question_type": "choice", "content": "以下哪个是不可数名词？", "options": ["A. apple", "B. water", "C. book", "D. cat"], "answer": "B", "explanation": "water（水）是不可数名词，不能直接加 s。apple/book/cat 都是可数名词。", "difficulty": 1},
    {"concept_id": "english/tenses", "question_type": "choice", "content": "She ___ to school every day. 填什么？", "options": ["A. go", "B. goes", "C. going", "D. went"], "answer": "B", "explanation": "主语 She 是第三人称单数，一般现在时动词加 s/es。", "difficulty": 2},
    {"concept_id": "english/tenses", "question_type": "choice", "content": "I ___ this book since last week. 填什么？", "options": ["A. read", "B. am reading", "C. have read", "D. will read"], "answer": "C", "explanation": "since last week 表示从过去持续到现在，用现在完成时 have read。", "difficulty": 3},
    {"concept_id": "english/passive", "question_type": "choice", "content": "The cake ___ by my mom yesterday. 填什么？", "options": ["A. made", "B. was made", "C. is made", "D. has made"], "answer": "B", "explanation": "yesterday 表过去，蛋糕是被做的，用过去时被动 was made。", "difficulty": 3},
    {"concept_id": "english/clauses", "question_type": "choice", "content": "The boy ___ is standing there is my brother. 填什么？", "options": ["A. who", "B. which", "C. where", "D. what"], "answer": "A", "explanation": "先行词 boy 是人，用 who 引导定语从句。", "difficulty": 3},
    {"concept_id": "english/subjunctive", "question_type": "choice", "content": "If I ___ you, I would study harder. 填什么？", "options": ["A. am", "B. was", "C. were", "D. be"], "answer": "C", "explanation": "虚拟语气中，if 从句用 were（不论人称），表示与现在事实相反。", "difficulty": 4},
    {"concept_id": "english/writing", "question_type": "choice", "content": "以下哪个是最好的主题句？", "options": ["A. I like dogs.", "B. Dogs are popular pets for three reasons.", "C. Dogs bark.", "D. My dog is brown."], "answer": "B", "explanation": "B 明确表达了段落主题和方向（三个原因），是最好的主题句。", "difficulty": 3},
]


# ========== JavaScript 编程 ==========

JAVASCRIPT_DOMAIN = {
    "id": "javascript",
    "name": "JavaScript 编程",
    "category": "编程",
    "description": "JavaScript 核心概念，从变量到异步编程，适合前端和全栈开发者。",
    "icon": "⚡",
}

JAVASCRIPT_CONCEPTS = [
    {"id": "js/variables", "name": "变量与类型", "description": "var/let/const、基本类型、类型转换", "level": 1, "tags": ["基础"], "prerequisites": []},
    {"id": "js/functions", "name": "函数", "description": "函数声明、箭头函数、参数、闭包", "level": 2, "tags": ["核心"], "prerequisites": ["js/variables"]},
    {"id": "js/arrays", "name": "数组与对象", "description": "数组方法、对象操作、解构赋值", "level": 2, "tags": ["核心"], "prerequisites": ["js/variables"]},
    {"id": "js/async", "name": "异步编程", "description": "Promise、async/await、回调、事件循环", "level": 3, "tags": ["核心"], "prerequisites": ["js/functions"]},
    {"id": "js/dom", "name": "DOM 操作", "description": "选择元素、事件处理、DOM 修改", "level": 3, "tags": ["前端"], "prerequisites": ["js/functions"]},
    {"id": "js/es6", "name": "ES6+ 特性", "description": "模板字符串、展开运算符、模块、Symbol、Map/Set", "level": 3, "tags": ["进阶"], "prerequisites": ["js/arrays"]},
]

JAVASCRIPT_QUESTIONS = [
    {"concept_id": "js/variables", "question_type": "choice", "content": "以下哪个声明的变量不能被重新赋值？", "options": ["A. var", "B. let", "C. const", "D. 都可以"], "answer": "C", "explanation": "const 声明的变量不能重新赋值（但对象/数组的属性可以修改）。", "difficulty": 1},
    {"concept_id": "js/variables", "question_type": "choice", "content": "typeof null 的结果是？", "options": ["A. 'null'", "B. 'undefined'", "C. 'object'", "D. 'boolean'"], "answer": "C", "explanation": "这是 JavaScript 的历史 bug，typeof null 返回 'object'。", "difficulty": 2},
    {"concept_id": "js/functions", "question_type": "choice", "content": "箭头函数和普通函数的主要区别是？", "options": ["A. 语法更短", "B. 没有自己的 this", "C. 不能有参数", "D. 不能返回值"], "answer": "B", "explanation": "箭头函数没有自己的 this，它继承外层作用域的 this。", "difficulty": 2},
    {"concept_id": "js/arrays", "question_type": "choice", "content": "[1,2,3].map(x => x * 2) 的结果是？", "options": ["A. [1,2,3]", "B. [2,4,6]", "C. 6", "D. [1,4,9]"], "answer": "B", "explanation": "map 方法对每个元素执行回调，x*2 后返回新数组 [2,4,6]。", "difficulty": 2},
    {"concept_id": "js/async", "question_type": "choice", "content": "Promise.all 的行为是？", "options": ["A. 任一完成即返回", "B. 全部完成才返回", "C. 按顺序执行", "D. 忽略错误"], "answer": "B", "explanation": "Promise.all 等待所有 Promise 完成，任一 reject 则立即 reject。", "difficulty": 3},
    {"concept_id": "js/dom", "question_type": "choice", "content": "document.querySelector('.box') 返回什么？", "options": ["A. 所有匹配元素的数组", "B. 第一个匹配的元素", "C. 元素的数量", "D. 元素的 innerHTML"], "answer": "B", "explanation": "querySelector 返回第一个匹配的元素。querySelectorAll 才返回所有匹配。", "difficulty": 2},
    {"concept_id": "js/es6", "question_type": "choice", "content": "const {name, age} = obj 这行代码叫什么？", "options": ["A. 模板字符串", "B. 展开运算符", "C. 解构赋值", "D. 箭头函数"], "answer": "C", "explanation": "这是对象解构赋值，从 obj 中提取 name 和 age 属性。", "difficulty": 2},
]


# ========== 法律基础 ==========

LAW_DOMAIN = {
    "id": "law-basics",
    "name": "法律基础",
    "category": "考证",
    "description": "法律入门知识，涵盖民法、刑法、合同法、劳动法、知识产权等核心概念。",
    "icon": "⚖️",
}

LAW_CONCEPTS = [
    {"id": "law/basics", "name": "法律基本概念", "description": "法律的定义、分类、法律关系、法律渊源", "level": 1, "tags": ["基础"], "prerequisites": []},
    {"id": "law/civil", "name": "民法基础", "description": "民事主体、民事权利、民事行为能力", "level": 2, "tags": ["核心"], "prerequisites": ["law/basics"]},
    {"id": "law/criminal", "name": "刑法基础", "description": "犯罪构成、刑罚种类、正当防卫、紧急避险", "level": 2, "tags": ["核心"], "prerequisites": ["law/basics"]},
    {"id": "law/contract", "name": "合同法", "description": "合同的成立、生效、履行、违约责任", "level": 3, "tags": ["核心"], "prerequisites": ["law/civil"]},
    {"id": "law/labor", "name": "劳动法", "description": "劳动合同、工资、工时、劳动争议", "level": 3, "tags": ["实用"], "prerequisites": ["law/civil"]},
    {"id": "law/ip", "name": "知识产权", "description": "著作权、专利权、商标权的基本概念", "level": 3, "tags": ["实用"], "prerequisites": ["law/civil"]},
]

LAW_QUESTIONS = [
    {"concept_id": "law/basics", "question_type": "choice", "content": "以下哪个不是法律的渊源？", "options": ["A. 宪法", "B. 行政法规", "C. 学术论文", "D. 司法解释"], "answer": "C", "explanation": "学术论文不是法律渊源。法律渊源包括宪法、法律、行政法规、地方性法规、司法解释等。", "difficulty": 1},
    {"concept_id": "law/civil", "question_type": "choice", "content": "16周岁以上不满18周岁的公民，以自己的劳动收入为主要生活来源的，视为？", "options": ["A. 无民事行为能力人", "B. 限制民事行为能力人", "C. 完全民事行为能力人", "D. 以上都不是"], "answer": "C", "explanation": "民法典规定，16-18周岁以劳动收入为主要生活来源的，视为完全民事行为能力人。", "difficulty": 2},
    {"concept_id": "law/criminal", "question_type": "choice", "content": "正当防卫超过必要限度造成重大损害的，应当？", "options": ["A. 不负刑事责任", "B. 负刑事责任，但应减轻或免除处罚", "C. 负完全刑事责任", "D. 由法院决定"], "answer": "B", "explanation": "防卫过当应当负刑事责任，但应当减轻或者免除处罚。", "difficulty": 3},
    {"concept_id": "law/contract", "question_type": "choice", "content": "以下哪种合同是无效的？", "options": ["A. 书面合同", "B. 口头合同", "C. 违反法律强制性规定的合同", "D. 电子邮件合同"], "answer": "C", "explanation": "违反法律、行政法规的强制性规定的合同无效。口头合同和电子邮件合同都是有效的。", "difficulty": 2},
    {"concept_id": "law/labor", "question_type": "choice", "content": "劳动法规定，试用期最长不得超过？", "options": ["A. 1个月", "B. 3个月", "C. 6个月", "D. 12个月"], "answer": "C", "explanation": "劳动合同期限三年以上的，试用期不得超过六个月。", "difficulty": 2},
    {"concept_id": "law/ip", "question_type": "choice", "content": "著作权的保护期限一般是？", "options": ["A. 作者终身", "B. 作者终身及死后50年", "C. 发表后50年", "D. 永久保护"], "answer": "B", "explanation": "公民作品的著作权保护期为作者终身及其死亡后50年。", "difficulty": 2},
]


# ========== 注册种子数据 ==========

ALL_SEEDS = [
    (PYTHON_DOMAIN, PYTHON_CONCEPTS, PYTHON_QUESTIONS),
    (FINANCE_DOMAIN, FINANCE_CONCEPTS, FINANCE_QUESTIONS),
    (CPA_DOMAIN, CPA_CONCEPTS, CPA_QUESTIONS),
    (MATH_DOMAIN, MATH_CONCEPTS, MATH_QUESTIONS),
    (ENGLISH_DOMAIN, ENGLISH_CONCEPTS, ENGLISH_QUESTIONS),
    (JAVASCRIPT_DOMAIN, JAVASCRIPT_CONCEPTS, JAVASCRIPT_QUESTIONS),
    (LAW_DOMAIN, LAW_CONCEPTS, LAW_QUESTIONS),
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

            # 创建概念（去掉 prerequisites 字段，避免和 ORM relationship 冲突）
            for i, concept_data in enumerate(concepts_data):
                clean_data = {k: v for k, v in concept_data.items() if k != "prerequisites"}
                concept = Concept(**clean_data, domain_id=domain_data["id"], sort_order=i)
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
