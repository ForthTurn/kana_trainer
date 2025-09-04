#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统计管理模块
处理学习统计、排行榜和图表显示
"""

import os
from datetime import datetime

from InquirerPy import inquirer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from config import BAR_LENGTH, CHART_HEIGHT, CHART_WIDTH, DEFAULT_TOP_N, STATS_FILE
from data_manager import load_json, save_json
from kana_data import kana_romaji

console = Console()

# 检查matplotlib是否可用
try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def clear_screen():
    """清屏函数"""
    os.system("cls" if os.name == "nt" else "clear")


def show_stats_header():
    """显示统计头部"""
    clear_screen()
    title_text = Text("📊 学习统计与趋势", style="bold cyan")
    title_panel = Panel(title_text, border_style="cyan", padding=(0, 2))
    console.print(title_panel)
    console.print()


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
    show_stats_header()

    stats = load_json(STATS_FILE)
    if not stats:
        no_data_text = Text("暂无统计数据（每天答题数/正确数会记录到 stats.json）", style="yellow")
        no_data_panel = Panel(no_data_text, border_style="yellow", padding=(1, 2))
        console.print(no_data_panel)
        return

    # 统计表格
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

    # 趋势图
    console.print("\n[bold cyan]答题趋势（条形图）[/bold cyan]")
    max_val = max(totals) if totals else 1
    for day, tot in zip(sorted_days, totals):
        bar = "█" * int((tot / max_val) * BAR_LENGTH)
        console.print(f"{day} {bar} {tot}")

    if MATPLOTLIB_AVAILABLE:
        console.print("\n[bold yellow]图表选项[/bold yellow]")
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
                error_text = Text(f"无法绘图：{e}", style="red")
                error_panel = Panel(error_text, border_style="red", padding=(1, 2))
                console.print(error_panel)


def show_leaderboard_header():
    """显示排行榜头部"""
    clear_screen()
    title_text = Text("🏆 错题排行榜", style="bold cyan")
    title_panel = Panel(title_text, border_style="cyan", padding=(0, 2))
    console.print(title_panel)
    console.print()


def show_leaderboard(data, top_n=DEFAULT_TOP_N):
    """显示错题排行榜"""
    show_leaderboard_header()

    if not data:
        no_data_text = Text("暂无错题记录", style="yellow")
        no_data_panel = Panel(no_data_text, border_style="yellow", padding=(1, 2))
        console.print(no_data_panel)
        return

    # 按错题次数排序
    sorted_kana = sorted(data.items(), key=lambda x: x[1].get("wrong_count", 0), reverse=True)

    if not sorted_kana:
        no_data_text = Text("暂无错题记录", style="yellow")
        no_data_panel = Panel(no_data_text, border_style="yellow", padding=(1, 2))
        console.print(no_data_panel)
        return

    # 创建排行榜表格
    table = Table(title=f"错题排行榜 (前 {top_n} 名)", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("排名", justify="center")
    table.add_column("假名", justify="center")
    table.add_column("罗马音", justify="center")
    table.add_column("错题次数", justify="center")
    table.add_column("最后复习", justify="center")
    table.add_column("间隔天数", justify="center")

    for i, (kana, info) in enumerate(sorted_kana[:top_n], 1):
        romaji = kana_romaji.get(kana, "未知")
        wrong_count = info.get("wrong_count", 0)
        last_review = info.get("last_review", "从未")
        interval = info.get("interval", 1)

        table.add_row(str(i), kana, romaji, str(wrong_count), last_review, str(interval))

    console.print(table)

    # 显示统计信息
    total_wrong = sum(info.get("wrong_count", 0) for info in data.values())
    total_kana = len(data)

    stats_text = Text(f"总错题数: {total_wrong}\n涉及假名数: {total_kana}", style="cyan")
    stats_panel = Panel(stats_text, border_style="cyan", padding=(1, 2))
    console.print()
    console.print(stats_panel)


def show_leaderboard_interactive(data):
    """交互式排行榜显示"""
    show_leaderboard_header()

    if not data:
        no_data_text = Text("暂无错题记录", style="yellow")
        no_data_panel = Panel(no_data_text, border_style="yellow", padding=(1, 2))
        console.print(no_data_panel)
        return

    # 选择显示数量
    top_n_choice = inquirer.select(
        message="选择显示前几名：",
        choices=[
            {"name": "前 5 名", "value": 5},
            {"name": "前 10 名", "value": 10},
            {"name": "前 20 名", "value": 20},
            {"name": "全部", "value": len(data)},
        ],
        default=10,
    ).execute()

    show_leaderboard(data, top_n_choice)
