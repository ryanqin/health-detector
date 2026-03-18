# Oura 压力疏解检测系统

基于 Oura Ring API V2 的个人压力与恢复状态追踪。

## 核心理念

不只是"压力高不高"，而是检测**压力-恢复平衡**：
- 压力输入了多少？
- 身体恢复了多少？
- 今天的疏解指数是多少？

## 数据来源（Oura API V2）

| 端点 | 数据 | 用途 |
|------|------|------|
| `daily_stress` | 压力评分、紧张/平静时长 | 直接压力信号 |
| `daily_resilience` | 复原力评分 | 压力抵抗能力 |
| `daily_readiness` | 准备度、HRV 均衡、心率恢复 | 综合恢复状态 |
| `daily_sleep` | 睡眠评分、深睡、REM | 夜间恢复质量 |
| `heartrate` | 分钟级心率 | 实时压力波动 |
| `daily_spo2` | 血氧饱和度 | 睡眠质量辅助 |
| `daily_activity` | 活动量、久坐时长 | 身体压力 |

## 疏解指数（Relief Index）

综合评分 0-100，越高越好：

```
Relief Index = (
  readiness_score × 0.30 +
  sleep_score     × 0.25 +
  resilience      × 0.20 +
  (100 - stress)  × 0.15 +
  activity_balance × 0.10
)
```

## 目录结构

```
oura-stress-detector/
├── README.md
├── config.py          # API token、权重配置
├── client.py          # Oura API 客户端
├── analyzer.py        # 疏解指数计算引擎
├── reporter.py        # 日报生成 + 推送到 Obsidian
└── data/              # 本地缓存
```
