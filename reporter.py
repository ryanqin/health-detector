# reporter.py - 日报生成 + 推送到 Obsidian

import os
import json
from datetime import date, timedelta
from pathlib import Path
from analyzer import calc_relief_index, level_to_emoji, level_to_label
from config import OBSIDIAN_VAULT, OBSIDIAN_HEALTH_DIR


def generate_report(raw: dict, target_date: date = None) -> str:
    d = target_date or date.today() - timedelta(days=1)
    result = calc_relief_index(raw)

    score = result["score"]
    level = result["level"]
    breakdown = result["breakdown"]
    missing = result["missing"]

    emoji = level_to_emoji(level)
    label = level_to_label(level)

    score_str = f"{score}" if score is not None else "N/A"

    lines = [
        f"# 健康日志 · {d}",
        "",
        f"## {emoji} 疏解指数：{score_str} / 100 — {label}",
        "",
        "## 📊 分项数据",
        "",
        "| 维度 | 分数 |",
        "|------|------|",
        f"| 综合准备度 (Readiness) | {breakdown.get('readiness') or '-'} |",
        f"| 睡眠质量 (Sleep) | {breakdown.get('sleep') or '-'} |",
        f"| 复原力 (Resilience) | {breakdown.get('resilience') or '-'} |",
        f"| 低压力分 (Stress↓) | {breakdown.get('stress') or '-'} |",
        f"| 活动均衡 (Activity) | {breakdown.get('activity') or '-'} |",
    ]

    if missing:
        lines += ["", f"> ⚠️ 以下数据缺失：{', '.join(missing)}"]

    lines += [
        "",
        "## 📝 当日感受",
        "",
        "<!-- 从日记自动同步或手动填写 -->",
        "",
        "---",
        f"*自动生成 · {date.today()}*",
    ]

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

