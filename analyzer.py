# analyzer.py - 疏解指数计算引擎

from config import WEIGHTS, THRESHOLDS
from typing import Optional


def safe_score(data: dict, key: str = "score") -> Optional[float]:
    items = data.get("data", [])
    if not items:
        return None
    return items[0].get(key)


def calc_stress_score(stress_data: dict) -> Optional[float]:
    """
    将压力数据转换为 0-100 的"低压力分"
    stress_high 时长越短越好
    """
    items = stress_data.get("data", [])
    if not items:
        return None
    d = items[0]
    # day_summary: 'restored' | 'normal' | 'stressful'
    summary = d.get("day_summary", "normal")
    mapping = {"restored": 90, "normal": 65, "stressful": 30}
    return mapping.get(summary, 50)


def calc_activity_balance(activity_data: dict) -> Optional[float]:
    """活动均衡分：有活动但不过度"""
    return safe_score(activity_data)


def calc_relief_index(raw: dict) -> dict:
    """
    计算疏解指数（Relief Index）
    返回：score, level, breakdown, missing_fields
    """
    scores = {
        "readiness":  safe_score(raw.get("readiness", {})),
        "sleep":      safe_score(raw.get("sleep", {})),
        "resilience": safe_score(raw.get("resilience", {})),
        "stress":     calc_stress_score(raw.get("stress", {})),
        "activity":   calc_activity_balance(raw.get("activity", {})),
    }

    missing = [k for k, v in scores.items() if v is None]
    available = {k: v for k, v in scores.items() if v is not None}

    if not available:
        return {"score": None, "level": "no_data", "breakdown": scores, "missing": missing}

    # 重新归一化权重（处理缺失字段）
    total_weight = sum(WEIGHTS[k] for k in available)
    weighted_sum = sum(WEIGHTS[k] * available[k] for k in available)
    final_score = round(weighted_sum / total_weight, 1)

    # 判断等级
    level = "critical"
    for lvl, threshold in sorted(THRESHOLDS.items(), key=lambda x: -x[1]):
        if final_score >= threshold:
            level = lvl
            break

    return {
        "score": final_score,
        "level": level,
        "breakdown": scores,
        "missing": missing,
    }


def level_to_emoji(level: str) -> str:
    return {
        "excellent": "🟢",
        "good":      "🟡",
        "warning":   "🟠",
        "critical":  "🔴",
        "no_data":   "⚪",
    }.get(level, "⚪")


def level_to_label(level: str) -> str:
    return {
        "excellent": "状态极佳",
        "good":      "状态良好",
        "warning":   "需要注意",
        "critical":  "需要恢复",
        "no_data":   "数据不足",
    }.get(level, "未知")

