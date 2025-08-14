#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
训练模块
包含核心的假名练习逻辑
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from config import DATA_FILE, INTERVAL_MULTIPLIER, MAX_INTERVAL
from data_manager import due_for_review, pick_kana, save_json, today_str
from kana_data import kana_romaji
from stats_manager import update_stats

console = Console()


def clear_screen():
    """清屏函数"""
    os.system("cls" if os.name == "nt" else "clear")


def show_quiz_header(mode_name, correct_count, total_count):
    """显示练习头部信息"""
    clear_screen()

    # 标题
    title_text = Text(f"🎯 {mode_name} 模式", style="bold cyan")
    title_panel = Panel(title_text, border_style="cyan", padding=(0, 2))
    console.print(title_panel)

    # 进度信息
    if total_count > 0:
        rate = correct_count / total_count * 100
        progress_text = Text(f"当前进度: {correct_count}/{total_count} ({rate:.1f}%)", style="yellow")
        progress_panel = Panel(progress_text, border_style="yellow", padding=(0, 2))
        console.print(progress_panel)

    console.print()


def quiz_mode(data, mode="free"):
    """练习模式主函数"""
    review_list = due_for_review(data) if mode == "review" else []
    correct_count = 0
    total_count = 0

    mode_name = "每日复习" if mode == "review" else "自由练习"

    while True:
        if not review_list and mode == "review":
            show_quiz_header(mode_name, correct_count, total_count)
            console.print("[green]今日复习题已全部完成！[/green]")
            break

        kana = pick_kana(data, review_list)
        romaji = kana_romaji[kana]

        # 显示练习界面
        show_quiz_header(mode_name, correct_count, total_count)

        # 显示假名并获取用户输入
        kana_text = Text(f"请问假名 {kana} 的罗马音是：", style="bold white")
        kana_panel = Panel(kana_text, border_style="white", padding=(1, 2))
        console.print(kana_panel)

        user = input("请输入答案 (输入 'q' 退出): ").strip().lower()

        if user == "q":
            break

        total_count += 1

        if user == romaji:
            # 答对的情况
            result_text = Text("✅ 正确！", style="bold green")
            result_panel = Panel(result_text, border_style="green", padding=(1, 2))
            console.print(result_panel)
            correct_count += 1

            if kana in data:
                # 增加间隔，减少错题次数
                current_interval = int(data[kana].get("interval", 1))
                data[kana]["interval"] = max(1, current_interval * INTERVAL_MULTIPLIER)
                data[kana]["last_review"] = today_str()
                current_wrong = int(data[kana].get("wrong_count", 0))
                data[kana]["wrong_count"] = max(0, current_wrong - 1)

                # 如果错题次数为0且间隔足够长，从错题记录中删除
                if data[kana]["wrong_count"] == 0 and data[kana]["interval"] > MAX_INTERVAL:
                    del data[kana]
        else:
            # 答错的情况
            result_text = Text(f"❌ 错误，正确答案是: {romaji}", style="bold red")
            result_panel = Panel(result_text, border_style="red", padding=(1, 2))
            console.print(result_panel)

            if kana not in data:
                data[kana] = {"wrong_count": 0, "last_review": today_str(), "interval": 1}

            current_wrong = int(data[kana].get("wrong_count", 0))
            data[kana]["wrong_count"] = current_wrong + 1
            data[kana]["interval"] = 1
            data[kana]["last_review"] = today_str()

        # 保存数据
        save_json(DATA_FILE, data)

        # 如果是复习模式，从复习列表中移除已练习的假名
        if mode == "review" and kana in review_list:
            review_list.remove(kana)

        # 显示当前正确率
        if total_count > 0:
            rate = correct_count / total_count * 100
            rate_text = Text(f"当前正确率: {correct_count}/{total_count} ({rate:.1f}%)", style="cyan")
            rate_panel = Panel(rate_text, border_style="cyan", padding=(0, 2))
            console.print(rate_panel)

        # 等待用户确认继续
        input("\n按 Enter 键继续下一题...")

    # 更新统计并结束
    update_stats(total_count, correct_count)

    # 显示最终结果
    show_quiz_header(mode_name, correct_count, total_count)
    if total_count > 0:
        final_rate = correct_count / total_count * 100
        final_text = Text(
            f"练习完成！\n总题数: {total_count}\n正确数: {correct_count}\n正确率: {final_rate:.1f}%", style="bold green"
        )
        final_panel = Panel(final_text, border_style="green", padding=(1, 2))
        console.print(final_panel)
    else:
        console.print("[yellow]本次没有完成任何练习。[/yellow]")

    console.print("\n[green]练习会话结束并已保存统计。[/green]")
