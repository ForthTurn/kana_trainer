#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据管理模块
处理JSON文件的读写、日期计算等基础功能
"""

import json
import os
import random
from datetime import datetime, timedelta

from config import MAX_WEIGHT


def today_str():
    """获取今天的日期字符串，格式：YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")


def load_json(file):
    """加载JSON文件，如果文件不存在或读取失败则返回空字典"""
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_json(file, data):
    """保存数据到JSON文件"""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def due_for_review(data):
    """获取需要复习的假名列表"""
    today = datetime.now().date()
    due = []
    for kana, info in data.items():
        try:
            last = datetime.strptime(info["last_review"], "%Y-%m-%d").date()
            interval = int(info.get("interval", 1))
            if last + timedelta(days=interval) <= today:
                due.append(kana)
        except Exception:
            due.append(kana)
    return due


def build_weighted_list(data):
    """构建带权重的假名列表，错题次数越多权重越大"""
    weighted = []
    from kana_data import kana_romaji

    for kana in kana_romaji:
        weight = 1 + data.get(kana, {}).get("wrong_count", 0)
        weight = max(1, min(weight, MAX_WEIGHT))  # 限制权重在1-20之间
        weighted.extend([kana] * weight)
    return weighted


def pick_kana(data, review_list):
    """选择假名：优先从复习列表中选择，否则从权重列表中选择"""
    if review_list:
        return random.choice(review_list)
    wl = build_weighted_list(data)
    return random.choice(wl)
