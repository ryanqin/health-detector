#!/usr/bin/env python3
# main.py - 运行入口

import sys
from datetime import date
from client import OuraClient
from analyzer import calc_relief_index, level_to_emoji, level_to_label
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

    # 保存原始数据
    save_raw_data(raw, target_date)

    # 计算疏解指数
    result = calc_relief_index(raw)
    score = result["score"]
    level = result["level"]
    emoji = level_to_emoji(level)
    label = level_to_label(level)

    print(f"\n{emoji} 疏解指数：{score} / 100 — {label}")
    print("\n分项：")
    for k, v in result["breakdown"].items():
        print(f"  {k}: {v or 'N/A'}")

    if result["missing"]:
        print(f"\n⚠️  缺失数据：{result['missing']}")

    # 生成报告并写入 Obsidian
    report = generate_report(raw, target_date)
    path = save_to_obsidian(report, target_date)
    print(f"\n✅ 报告已写入：{path}")


if __name__ == "__main__":
    target = None
    if len(sys.argv) > 1:
        from datetime import datetime
        target = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    run(target)

