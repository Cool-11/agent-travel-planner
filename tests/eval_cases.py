
# -*- coding: utf-8 -*-
"""agent-travel-planner 评测用例集

设计原则：
- 30 条样本 = 25 条正常组合（一线 / 二线 / 三线 × 1/3/7 天 × 低中高预算）+ 5 条边界 case
- 每条样本含必含关键词（must_include），用于校验幻觉率
- 边界 case 用于校验优雅失败（API 抖动、空输入、超长行程等）

使用方法：
  python -m scripts.run_eval --baseline   # 跑原始版本
  python -m scripts.run_eval              # 跑当前版本
  python -m scripts.score_eval            # 对比前后
"""
from typing import List, Dict, Any


def _case(name, category, input, must_include, must_not_include=None, expect_graceful_failure=False):
    return {
        "name": name,
        "category": category,
        "input": input,
        "must_include": must_include,
        "must_not_include": must_not_include or [],
        "expect_graceful_failure": expect_graceful_failure,
    }


EVAL_CASES: List[Dict[str, Any]] = [
    # ===== 一线城市 (10 条) =====
    _case("北京 3 天历史游", "一线", {"destination": "北京", "days": 3, "preferences": "历史文化", "budget": "中等"}, ["故宫", "天安门"], []),
    _case("上海 2 天亲子游", "一线", {"destination": "上海", "days": 2, "preferences": "亲子", "budget": "高"}, ["迪士尼", "科技馆"], []),
    _case("广州 1 天美食游", "一线", {"destination": "广州", "days": 1, "preferences": "美食", "budget": "低"}, ["早茶", "肠粉"], []),
    _case("深圳 7 天科技游", "一线", {"destination": "深圳", "days": 7, "preferences": "科技", "budget": "高"}, ["华强北", "科技园"], []),
    _case("北京 1 天穷游", "一线", {"destination": "北京", "days": 1, "preferences": "打卡", "budget": "低"}, [], []),
    _case("上海 7 天深度游", "一线", {"destination": "上海", "days": 7, "preferences": "深度文化", "budget": "高"}, ["外滩", "豫园"], []),
    _case("广州 3 天休闲游", "一线", {"destination": "广州", "days": 3, "preferences": "休闲", "budget": "中等"}, [], []),
    _case("深圳 3 天商务游", "一线", {"destination": "深圳", "days": 3, "preferences": "商务", "budget": "高"}, [], []),
    _case("北京 7 天深度文化", "一线", {"destination": "北京", "days": 7, "preferences": "深度文化", "budget": "中等"}, [], []),
    _case("上海 1 天打卡", "一线", {"destination": "上海", "days": 1, "preferences": "打卡", "budget": "低"}, [], []),
    # ===== 二线城市 (10 条) =====
    _case("杭州 3 天西湖游", "二线", {"destination": "杭州", "days": 3, "preferences": "自然", "budget": "中等"}, ["西湖", "灵隐寺"], []),
    _case("成都 3 天美食游", "二线", {"destination": "成都", "days": 3, "preferences": "美食", "budget": "中等"}, ["火锅", "宽窄巷子"], []),
    _case("武汉 2 天历史游", "二线", {"destination": "武汉", "days": 2, "preferences": "历史文化", "budget": "低"}, ["黄鹤楼"], []),
    _case("西安 3 天古都游", "二线", {"destination": "西安", "days": 3, "preferences": "历史文化", "budget": "中等"}, ["兵马俑", "大雁塔"], []),
    _case("南京 2 天历史游", "二线", {"destination": "南京", "days": 2, "preferences": "历史文化", "budget": "低"}, [], []),
    _case("杭州 1 天商务", "二线", {"destination": "杭州", "days": 1, "preferences": "商务", "budget": "高"}, [], []),
    _case("成都 7 天深度游", "二线", {"destination": "成都", "days": 7, "preferences": "深度", "budget": "中等"}, [], []),
    _case("武汉 1 天打卡", "二线", {"destination": "武汉", "days": 1, "preferences": "打卡", "budget": "低"}, [], []),
    _case("西安 1 天美食", "二线", {"destination": "西安", "days": 1, "preferences": "美食", "budget": "低"}, [], []),
    _case("南京 7 天深度", "二线", {"destination": "南京", "days": 7, "preferences": "深度", "budget": "高"}, [], []),
    # ===== 三线城市 (5 条) =====
    _case("厦门 3 天文艺游", "三线", {"destination": "厦门", "days": 3, "preferences": "文艺", "budget": "中等"}, ["鼓浪屿"], []),
    _case("长沙 2 天美食", "三线", {"destination": "长沙", "days": 2, "preferences": "美食", "budget": "低"}, [], []),
    _case("青岛 3 天海滨", "三线", {"destination": "青岛", "days": 3, "preferences": "海滨", "budget": "中等"}, [], []),
    _case("苏州 2 天园林", "三线", {"destination": "苏州", "days": 2, "preferences": "园林", "budget": "中等"}, [], []),
    _case("拉萨 5 天高原", "三线", {"destination": "拉萨", "days": 5, "preferences": "自然", "budget": "中等"}, [], []),
    # ===== 边界 case (5 条) =====
    _case("不存在的目的地", "edge", {"destination": "马尔代夫共和国首都马累市某某村", "days": 3, "preferences": "海岛", "budget": "高"}, [], [], True),
    _case("空目的地", "edge", {"destination": "", "days": 1, "preferences": "", "budget": "低"}, [], [], True),
    _case("超长时间 30 天", "edge", {"destination": "北京", "days": 30, "preferences": "深度", "budget": "高"}, [], []),
    _case("0 天行程", "edge", {"destination": "上海", "days": 0, "preferences": "打卡", "budget": "低"}, [], [], True),
    _case("极端预算 0 元", "edge", {"destination": "深圳", "days": 3, "preferences": "穷游", "budget": "无预算"}, [], []),
]
