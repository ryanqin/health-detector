# config.py - Oura 压力检测配置

# Oura Personal Access Token
# 获取：https://cloud.ouraring.com/personal-access-tokens
OURA_TOKEN = ""  # 拿到戒指后填入

# API 基础配置
API_BASE = "https://api.ouraring.com/v2"

# 疏解指数权重（总和=1.0）
WEIGHTS = {
    "readiness": 0.30,   # 综合准备度（含 HRV）
    "sleep":     0.25,   # 睡眠质量
    "resilience": 0.20,  # 复原力
    "stress":    0.15,   # 压力（反向：低压力 = 高分）
    "activity":  0.10,   # 活动均衡
}

# 疏解指数阈值
THRESHOLDS = {
    "excellent": 80,   # 🟢 状态极佳
    "good":      65,   # 🟡 状态良好
    "warning":   50,   # 🟠 需要注意
    "critical":  0,    # 🔴 需要恢复
}

# Obsidian 输出路径
OBSIDIAN_VAULT = ""  # 你的 Obsidian vault 绝对路径
OBSIDIAN_HEALTH_DIR = "健康"  # 会自动创建
