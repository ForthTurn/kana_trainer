#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
假名记忆器主程序
提供主菜单和程序入口
"""

import os

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from config import DATA_FILE
from data_manager import load_json
from JMdict.command import search_word_command, update_jmdict_command
from stats_manager import show_leaderboard, show_stats
from trainer import quiz_mode

console = Console()


def clear_screen():
    """清屏函数"""
    os.system("cls" if os.name == "nt" else "clear")


def show_header():
    """显示程序头部"""
    header_text = Text("=== 假名记忆器 Kana Trainer ===", style="bold magenta")
    header_panel = Panel(header_text, border_style="magenta", padding=(0, 2))
    console.print(header_panel)
    console.print()


def main():
    """主程序入口"""
    data = load_json(DATA_FILE)

    while True:
        clear_screen()
        show_header()

        choice = inquirer.select(
            message="请选择模式:",
            choices=[
                {"name": "📅 每日复习（优先出到期题）", "value": "review"},
                {"name": "🎯 自由练习（全部假名，按错题权重）", "value": "free"},
                {"name": "📖 查词功能", "value": "search"},
                {"name": "📊 查看统计与趋势", "value": "stats"},
                {"name": "🏆 错题排行榜", "value": "leader"},
                {"name": "🔄 更新词典", "value": "update_jmdict"},
                {"name": "🚪 退出", "value": "quit"},
            ],
            pointer=">",
            instruction="(用上下键选择，Enter确认)",
        ).execute()

        if choice == "quit":
            clear_screen()
            console.print("[bold]再见！祝学习顺利 : )[/bold]")
            break
        elif choice == "stats":
            clear_screen()
            show_header()
            show_stats()
            input("\n按 Enter 键返回主菜单...")
        elif choice == "leader":
            clear_screen()
            show_header()
            show_leaderboard(data)
            input("\n按 Enter 键返回主菜单...")
        elif choice in ("review", "free"):
            clear_screen()
            show_header()
            quiz_mode(data, mode=choice)
            input("\n按 Enter 键返回主菜单...")
        elif choice == "search":
            clear_screen()
            show_header()
            search_word_command()
            input("\n按 Enter 键返回主菜单...")
        elif choice == "update_jmdict":
            clear_screen()
            show_header()
            update_jmdict_command()
            input("\n按 Enter 键返回主菜单...")
        else:
            console.print("未知选项，请重试。")


if __name__ == "__main__":
    main()
