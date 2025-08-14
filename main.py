#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
假名记忆器主程序
提供主菜单和程序入口
"""

from InquirerPy import inquirer
from rich.console import Console

from config import DATA_FILE
from data_manager import load_json
from stats_manager import show_leaderboard, show_stats
from trainer import quiz_mode

console = Console()


def main():
    """主程序入口"""
    data = load_json(DATA_FILE)
    console.print("[bold magenta]=== 假名记忆器 Kana Trainer ===[/bold magenta]")

    while True:
        choice = inquirer.select(
            message="请选择模式:",
            choices=[
                {"name": "📅 每日复习（优先出到期题）", "value": "review"},
                {"name": "🎯 自由练习（全部假名，按错题权重）", "value": "free"},
                {"name": "📊 查看统计与趋势", "value": "stats"},
                {"name": "🏆 错题排行榜", "value": "leader"},
                {"name": "🚪 退出", "value": "quit"},
            ],
            pointer=">",
            instruction="(用上下键选择，Enter确认)",
        ).execute()

        if choice == "quit":
            console.print("[bold]再见！祝学习顺利 : )[/bold]")
            break
        elif choice == "stats":
            show_stats()
        elif choice == "leader":
            show_leaderboard(data)
        elif choice in ("review", "free"):
            quiz_mode(data, mode=choice)
        else:
            console.print("未知选项，请重试。")


if __name__ == "__main__":
    main()
