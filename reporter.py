# reporter.py - 健康日报生成 + 写入 Obsidian

import os
import json
from datetime import date, timedelta
from pathlib import Path
from analyzer import parse_all, calc_relief_index, level_to_emoji, level_to_label
from config import OBSIDIAN_VAULT, OBSIDIAN_HEALTH_DIR


def fmt(val, unit="", fallback="-"):
    if val is None:
        return fallback
    return f"{val}{unit}"


def fmt_score(val):
    if val is None:
        return "-"
    if val >= 80:
        return f"{val} 🟢"
    elif val >= 65:
        return f"{val} 🟡"
    elif val >= 50:
        return f"{val} 🟠"
    return f"{val} 🔴"


def generate_report(raw: dict, target_date: date = None) -> str:
    d = target_date or date.today() - timedelta(days=1)
    parsed = parse_all(raw)
    relief = calc_relief_index(parsed)

    score = relief["score"]
    level = relief["level"]
    emoji = level_to_emoji(level)
    label = level_to_label(level)
    score_str = fmt_score(score)

    s = parsed["sleep"]
    h = parsed["heartrate"]
    r = parsed["readiness"]
    st = parsed["stress"]
    a = parsed["activity"]

    lines = [
        f"# 健康日志 · {d}",
        "",
        f"## {emoji} 疏解指数：{score_str} / 100 — {label}",
        "",
        "---",
        "",
        "## 😴 睡眠",
        "",
        f"- **评分：** {fmt_score(s['score'])}",
        f"- **总时长：** {fmt(s['total_mins'], ' 分钟')}",
        f"- **深睡：** {fmt(s['deep_mins'], ' 分钟')}",
        f"- **REM：** {fmt(s['rem_mins'], ' 分钟')}",
        f"- **浅睡：** {fmt(s['light_mins'], ' 分钟')}",
        f"- **睡眠效率：** {fmt(s['efficiency'], '%')}",
        f"- **入睡时长：** {fmt(s['latency_mins'], ' 分钟')}",
        f"- **血氧均值：** {fmt(s['spo2_avg'], '%')}",
        f"- **血氧最低：** {fmt(s['spo2_min'], '%')}",
        "",
        "---",
        "",
        "## 💓 心率",
        "",
        f"- **静息心率：** {fmt(h['resting_hr'], ' bpm')}",
        f"- **日均心率：** {fmt(h['hr_avg'], ' bpm')}",
        f"- **心率范围：** {fmt(h['hr_min'])} - {fmt(h['hr_max'])} bpm",
        f"- **HRV 均衡：** {fmt_score(h['hrv_balance'])}",
        "",
        "---",
        "",
        "## ⚡ 准备度",
        "",
        f"- **综合评分：** {fmt_score(r['score'])}",
        f"- **HRV 均衡：** {fmt_score(r['hrv_balance'])}",
        f"- **恢复指数：** {fmt_score(r['recovery_index'])}",
        f"- **静息心率：** {fmt_score(r['resting_heart_rate'])}",
        f"- **睡眠均衡：** {fmt_score(r['sleep_balance'])}",
        f"- **体温偏差：** {fmt_score(r['body_temperature'])}",
        f"- **活动均衡：** {fmt_score(r['activity_balance'])}",
        "",
        "---",
        "",
        "## 🧠 压力与复原",
        "",
        f"- **今日状态：** {st['day_summary']}",
        f"- **高压时长：** {fmt(st['stress_high_mins'], ' 分钟')}",
        f"- **恢复时长：** {fmt(st['recovery_high_mins'], ' 分钟')}",
        f"- **复原力：** {fmt_score(st['resilience_score'])}",
        f"- **睡眠复原：** {fmt_score(st['sleep_recovery'])}",
        f"- **日间复原：** {fmt_score(st['daytime_recovery'])}",
        "",
        "---",
        "",
        "## 🏃 活动",
        "",
        f"- **评分：** {fmt_score(a['score'])}",
        f"- **步数：** {fmt(a['steps'])}",
        f"- **活动热量：** {fmt(a['active_calories'], ' kcal')}",
        f"- **总热量：** {fmt(a['total_calories'], ' kcal')}",
        f"- **久坐时长：** {fmt(a['sedentary_mins'], ' 分钟')}",
        "",
        "---",
        "",
        "## 📝 当日感受",
        "",
        "<!-- 从日记自动同步或手动填写 -->",
        "",
        "---",
        f"*自动生成 · {date.today()}*",
    ]

    if relief.get("missing"):
        lines.insert(4, f"\n> ⚠️ 数据缺失：{', '.join(relief['missing'])}\n")

    return "\n".join(lines)


def save_to_obsidian(report: str, target_date: date = None) -> str:
    d = target_date or date.today() - timedelta(days=1)
    health_dir = Path(OBSIDIAN_VAULT) / OBSIDIAN_HEALTH_DIR
    health_dir.mkdir(parents=True, exist_ok=True)
    filepath = health_dir / f"{d}.md"
    filepath.write_text(report, encoding="utf-8")
    return str(filepath)


def save_raw_data(raw: dict, target_date: date = None):
    d = target_date or date.today() - timedelta(days=1)
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    filepath = data_dir / f"{d}.json"
    filepath.write_text(json.dumps(raw, indent=2, ensure_ascii=False))
