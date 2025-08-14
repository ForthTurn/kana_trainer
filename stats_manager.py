#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统计管理模块
处理学习统计、排行榜和图表显示
"""

from datetime import datetime

from InquirerPy import inquirer
from rich import box
from rich.console import Console
from rich.table import Table

from config import (BAR_LENGTH, CHART_HEIGHT, CHART_WIDTH, DEFAULT_TOP_N,
                    STATS_FILE)
from data_manager import load_json, save_json
from kana_data import kana_romaji

console = Console()

# 检查matplotlib是否可用
try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def update_stats(total, correct):
    """更新学习统计数据"""
    stats = load_json(STATS_FILE)
    from data_manager import today_str

    day = today_str()
    if day not in stats:
        stats[day] = {"total": 0, "correct": 0}
    stats[day]["total"] += total
    stats[day]["correct"] += correct
    save_json(STATS_FILE, stats)


def show_stats():
    """显示学习统计和趋势图"""
    stats = load_json(STATS_FILE)
    if not stats:
        console.print(
            "[yellow]暂无统计数据（每天答题数/正确数会记录到 stats.json）[/yellow]"
        )
        return

    table = Table(title="学习统计（答题数/正确数）", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("日期", justify="left")
    table.add_column("答题数", justify="right")
    table.add_column("正确数", justify="right")
    table.add_column("正确率", justify="right")

    sorted_days = sorted(stats.keys())
    totals = []
    corrects = []
    for day in sorted_days:
        tot = stats[day].get("total", 0)
        cor = stats[day].get("correct", 0)
        rate = f"{(cor / tot * 100):.1f}%" if tot > 0 else "0.0%"
        table.add_row(day, str(tot), str(cor), rate)
        totals.append(tot)
        corrects.append(cor)

    console.print(table)

    console.print("\n[bold cyan]答题趋势（条形）[/bold cyan]")
    max_val = max(totals) if totals else 1
    for day, tot in zip(sorted_days, totals):
        bar = "█" * int((tot / max_val) * BAR_LENGTH)
        console.print(f"{day} {bar} {tot}")

    if MATPLOTLIB_AVAILABLE:
        use_plot = inquirer.confirm(
            message="用 matplotlib 弹出折线图？（需要图形界面，取消则只看终端图）",
            default=False,
        ).execute()
        if use_plot:
            try:
                x = [datetime.strptime(d, "%Y-%m-%d") for d in sorted_days]
                y_tot = totals
                y_cor = corrects
                plt.figure(figsize=(CHART_WIDTH, CHART_HEIGHT))
                plt.plot(x, y_tot, marker="o", label="Total")
                plt.plot(x, y_cor, marker="o", label="Correct")
                plt.fill_between(x, y_tot, alpha=0.1)
                plt.xlabel("Date")
                plt.ylabel("Count")
                plt.title("Study Progress")
                plt.legend()
                plt.tight_layout()
                plt.show()
            except Exception as e:
                console.print(f"[red]无法绘图：{e}[/red]")


def show_leaderboard(data, top_n=DEFAULT_TOP_N):
    """显示错题排行榜"""
    if not data:
        console.print("[green]当前没有错题记录，太棒了！[/green]")
        return

    items = sorted(
        data.items(), key=lambda kv: kv[1].get("wrong_count", 0), reverse=True
    )
    table = Table(title=f"错题排行榜（前 {top_n}）", box=box.SIMPLE)
    table.add_column("排名", justify="right")
    table.add_column("假名", justify="center")
    table.add_column("罗马音", justify="center")
    table.add_column("错题次数", justify="right")
    table.add_column("间隔(天)", justify="right")
    table.add_column("上次复习", justify="center")

    for idx, (kana, info) in enumerate(items[:top_n], start=1):
        table.add_row(
            str(idx),
            kana,
            kana_romaji.get(kana, "?"),
            str(info.get("wrong_count", 0)),
            str(info.get("interval", 1)),
            info.get("last_review", "-"),
        )

    console.print(table)
