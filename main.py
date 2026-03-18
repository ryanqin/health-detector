#!/usr/bin/env python3
# main.py - 运行入口

import sys
from datetime import date
from client import OuraClient
from analyzer import parse_all, calc_relief_index, level_to_emoji, level_to_label
from reporter import generate_report, save_to_obsidian, save_raw_data
from config import OURA_TOKEN


def run(target_date: date = None):
    if not OURA_TOKEN:
        print("⚠️  请先在 config.py 中填入 OURA_TOKEN")
        print("    获取地址：https://cloud.ouraring.com/personal-access-tokens")
        return

    print(f"📡 拉取 Oura 数据 ({target_date or '昨天'})...")
    client = OuraClient()
    raw = client.get_all(target_date)
    save_raw_data(raw, target_date)

    parsed = parse_all(raw)
    relief = calc_relief_index(parsed)

    emoji = level_to_emoji(relief["level"])
    label = level_to_label(relief["level"])
    print(f"\n{emoji} 疏解指数：{relief['score']} / 100 — {label}")

    s = parsed["sleep"]
    h = parsed["heartrate"]
    r = parsed["readiness"]
    st = parsed["stress"]
    a = parsed["activity"]

    print(f"\n😴 睡眠：{s['score']} 分 | {s['total_mins']} 分钟 | 深睡 {s['deep_mins']}m | REM {s['rem_mins']}m | 血氧 {s['spo2_avg']}%")
    print(f"💓 心率：静息 {h['resting_hr']} bpm | 均值 {h['hr_avg']} bpm | HRV {h['hrv_balance']}")
    print(f"⚡ 准备度：{r['score']} 分 | HRV均衡 {r['hrv_balance']} | 恢复指数 {r['recovery_index']}")
    print(f"🧠 压力：{st['day_summary']} | 高压 {st['stress_high_mins']}m | 复原力 {st['resilience_score']}")
    print(f"🏃 活动：{a['score']} 分 | 步数 {a['steps']} | 活动热量 {a['active_calories']} kcal")

    if relief.get("missing"):
        print(f"\n⚠️  缺失：{relief['missing']}")

    report = generate_report(raw, target_date)
    path = save_to_obsidian(report, target_date)
    print(f"\n✅ 报告已写入：{path}")


if __name__ == "__main__":
    target = None
    if len(sys.argv) > 1:
        from datetime import datetime
        target = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    run(target)
