# client.py - Oura API V2 客户端

import requests
from datetime import date, timedelta
from typing import Optional
from config import API_BASE, OURA_TOKEN


class OuraClient:
    def __init__(self, token: str = OURA_TOKEN):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    def _get(self, endpoint: str, params: dict) -> dict:
        url = f"{API_BASE}/usercollection/{endpoint}"
        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def _date_range(self, target_date: Optional[date] = None):
        d = target_date or date.today() - timedelta(days=1)
        return {"start_date": str(d), "end_date": str(d)}

    def get_daily_stress(self, target_date=None) -> dict:
        """压力评分：stress_high / stress_low / recovery_high / recovery_low 时长（分钟）"""
        return self._get("daily_stress", self._date_range(target_date))

    def get_daily_resilience(self, target_date=None) -> dict:
        """复原力：sleep_recovery / daytime_recovery / stress_balance"""
        return self._get("daily_resilience", self._date_range(target_date))

    def get_daily_readiness(self, target_date=None) -> dict:
        """准备度：score / hrv_balance / recovery_index / resting_heart_rate"""
        return self._get("daily_readiness", self._date_range(target_date))

    def get_daily_sleep(self, target_date=None) -> dict:
        """睡眠：score / total_sleep_duration / rem_sleep_duration / deep_sleep_duration"""
        return self._get("daily_sleep", self._date_range(target_date))

    def get_daily_activity(self, target_date=None) -> dict:
        """活动：score / active_calories / sedentary_time / meet_daily_targets"""
        return self._get("daily_activity", self._date_range(target_date))

    def get_daily_spo2(self, target_date=None) -> dict:
        """血氧：spo2_percentage（平均、最小、最大）"""
        return self._get("daily_spo2", self._date_range(target_date))

    def get_heartrate(self, target_date=None) -> dict:
        """分钟级心率数据（用于日内压力波动分析）"""
        d = target_date or date.today() - timedelta(days=1)
        params = {
            "start_datetime": f"{d}T00:00:00",
            "end_datetime": f"{d}T23:59:59",
        }
        return self._get("heartrate", params)

    def get_all(self, target_date=None) -> dict:
        """拉取所有压力相关数据"""
        return {
            "stress":     self.get_daily_stress(target_date),
            "resilience": self.get_daily_resilience(target_date),
            "readiness":  self.get_daily_readiness(target_date),
            "sleep":      self.get_daily_sleep(target_date),
            "activity":   self.get_daily_activity(target_date),
            "spo2":       self.get_daily_spo2(target_date),
        }

