#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置文件
管理程序中的常量和配置项
"""

# 文件路径配置
DATA_FILE = "wrong_kana.json"
STATS_FILE = "stats.json"

# 学习参数配置
MAX_WEIGHT = 20  # 最大权重
MIN_INTERVAL = 1  # 最小复习间隔（天）
MAX_INTERVAL = 90  # 最大复习间隔（天）
INTERVAL_MULTIPLIER = 2  # 答对后间隔倍数

# 排行榜配置
DEFAULT_TOP_N = 15  # 默认排行榜显示数量

# 图表配置
CHART_WIDTH = 8
CHART_HEIGHT = 4
BAR_LENGTH = 40  # 终端条形图长度
