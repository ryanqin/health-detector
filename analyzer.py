# analyzer.py - 健康数据分析引擎

from config import WEIGHTS, THRESHOLDS
from typing import Optional


def safe_get(data: dict, *keys):
    """安全取嵌套值"""
    items = data.get("data", [])
    if not items:
        return None
    d = items[0]
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def safe_score(data: dict) -> Optional[float]:
    return safe_get(data, "score")


# ─────────────────────────────────────────
# 睡眠分析
# ─────────────────────────────────────────
def parse_sleep(sleep_data: dict, spo2_data: dict) -> dict:
    def mins(seconds):
        return round(seconds / 60) if seconds else None

    total = safe_get(sleep_data, "total_sleep_duration")
    deep  = safe_get(sleep_data, "deep_sleep_duration")
    rem   = safe_get(sleep_data, "rem_sleep_duration")
    light = safe_get(sleep_data, "light_sleep_duration")
    efficiency = safe_get(sleep_data, "efficiency")
    latency    = safe_get(sleep_data, "sleep_latency")
    spo2_avg   = safe_get(spo2_data, "spo2_percentage", "average")
    spo2_min   = safe_get(spo2_data, "spo2_percentage", "minimum")

    return {
        "score":      safe_score(sleep_data),
        "total_mins": mins(total),
        "deep_mins":  mins(deep),
        "rem_mins":   mins(rem),
        "light_mins": mins(light),
        "efficiency": efficiency,
        "latency_mins": mins(latency),
        "spo2_avg":   spo2_avg,
        "spo2_min":   spo2_min,
    }


# ─────────────────────────────────────────
# 心率分析
# ─────────────────────────────────────────
def parse_heartrate(hr_data: dict, readiness_data: dict) -> dict:
    items = hr_data.get("data", [])
    bpm_values = [item["bpm"] for item in items if item.get("bpm")]

    hr_min = min(bpm_values) if bpm_values else None
    hr_max = max(bpm_values) if bpm_values else None
    hr_avg = round(sum(bpm_values) / len(bpm_values)) if bpm_values else None

    resting_hr = safe_get(readiness_data, "contributors", "resting_heart_rate")
    hrv_balance = safe_get(readiness_data, "contributors", "hrv_balance")

    return {
        "resting_hr":  resting_hr,
        "hr_avg":      hr_avg,
        "hr_min":      hr_min,
        "hr_max":      hr_max,
        "hrv_balance": hrv_balance,
    }


# ─────────────────────────────────────────
# 准备度分析
# ─────────────────────────────────────────
def parse_readiness(readiness_data: dict) -> dict:
    contributors = safe_get(readiness_data, "contributors") or {}
    return {
        "score":             safe_score(readiness_data),
        "hrv_balance":       contributors.get("hrv_balance"),
        "recovery_index":    contributors.get("recovery_index"),
        "resting_heart_rate": contributors.get("resting_heart_rate"),
        "sleep_balance":     contributors.get("sleep_balance"),
        "body_temperature":  contributors.get("body_temperature"),
        "activity_balance":  contributors.get("activity_balance"),
    }


# ─────────────────────────────────────────
# 压力与复原力分析
# ─────────────────────────────────────────
def parse_stress(stress_data: dict, resilience_data: dict) -> dict:
    summary = safe_get(stress_data, "day_summary") or "normal"
    stress_high = safe_get(stress_data, "stress_high")
    recovery_high = safe_get(stress_data, "recovery_high")

    resilience_score = safe_score(resilience_data)
    sleep_recovery = safe_get(resilience_data, "contributors", "sleep_recovery")
    daytime_recovery = safe_get(resilience_data, "contributors", "daytime_recovery")

    summary_map = {"restored": "已恢复 🟢", "normal": "正常 🟡", "stressful": "高压 🔴"}
    score_map = {"restored": 90, "normal": 65, "stressful": 30}

    return {
        "day_summary":       summary_map.get(summary, summary),
        "stress_score":      score_map.get(summary, 50),
        "stress_high_mins":  round(stress_high / 60) if stress_high else None,
        "recovery_high_mins": round(recovery_high / 60) if recovery_high else None,
        "resilience_score":  resilience_score,
        "sleep_recovery":    sleep_recovery,
        "daytime_recovery":  daytime_recovery,
    }


# ─────────────────────────────────────────
# 活动分析
# ─────────────────────────────────────────
def parse_activity(activity_data: dict) -> dict:
    return {
        "score":            safe_score(activity_data),
        "active_calories":  safe_get(activity_data, "active_calories"),
        "total_calories":   safe_get(activity_data, "total_calories"),
        "steps":            safe_get(activity_data, "steps"),
        "sedentary_mins":   round(safe_get(activity_data, "sedentary_time") / 60)
                            if safe_get(activity_data, "sedentary_time") else None,
        "daily_movement":   safe_get(activity_data, "daily_movement"),
    }


# ─────────────────────────────────────────
# 综合疏解指数
# ─────────────────────────────────────────
def calc_relief_index(parsed: dict) -> dict:
    scores = {
        "readiness":  parsed["readiness"].get("score"),
        "sleep":      parsed["sleep"].get("score"),
        "resilience": parsed["stress"].get("resilience_score"),
        "stress":     parsed["stress"].get("stress_score"),
        "activity":   parsed["activity"].get("score"),
    }

    missing = [k for k, v in scores.items() if v is None]
    available = {k: v for k, v in scores.items() if v is not None}

    if not available:
        return {"score": None, "level": "no_data", "missing": missing}

    total_weight = sum(WEIGHTS[k] for k in available)
    weighted_sum = sum(WEIGHTS[k] * available[k] for k in available)
    final_score = round(weighted_sum / total_weight, 1)

    level = "critical"
    for lvl, threshold in sorted(THRESHOLDS.items(), key=lambda x: -x[1]):
        if final_score >= threshold:
            level = lvl
            break

    return {"score": final_score, "level": level, "missing": missing}


# ─────────────────────────────────────────
# 全量解析入口
# ─────────────────────────────────────────
def parse_all(raw: dict) -> dict:
    return {
        "sleep":      parse_sleep(raw.get("sleep", {}), raw.get("spo2", {})),
        "heartrate":  parse_heartrate(raw.get("heartrate", {}), raw.get("readiness", {})),
        "readiness":  parse_readiness(raw.get("readiness", {})),
        "stress":     parse_stress(raw.get("stress", {}), raw.get("resilience", {})),
        "activity":   parse_activity(raw.get("activity", {})),
    }


def level_to_emoji(level: str) -> str:
    return {"excellent": "🟢", "good": "🟡", "warning": "🟠",
            "critical": "🔴", "no_data": "⚪"}.get(level, "⚪")


def level_to_label(level: str) -> str:
    return {"excellent": "状态极佳", "good": "状态良好", "warning": "需要注意",
            "critical": "需要恢复", "no_data": "数据不足"}.get(level, "未知")
