#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
训练模块
包含核心的假名练习逻辑
"""

from rich.console import Console

from config import DATA_FILE, INTERVAL_MULTIPLIER, MAX_INTERVAL
from data_manager import due_for_review, pick_kana, save_json, today_str
from kana_data import kana_romaji
from stats_manager import update_stats

console = Console()


def quiz_mode(data, mode="free"):
    """练习模式主函数"""
    review_list = due_for_review(data) if mode == "review" else []
    correct_count = 0
    total_count = 0
    
    mode_name = "每日复习" if mode == "review" else "自由练习"
    console.print(f"[cyan]进入 {mode_name} 模式。输入 q 随时退出。[/cyan]")
    
    while True:
        if not review_list and mode == "review":
            console.print("[green]今日复习题已全部完成！回到主菜单。[/green]")
            break
            
        kana = pick_kana(data, review_list)
        romaji = kana_romaji[kana]

        # 显示假名并获取用户输入
        console.print(f"请问假名 [bold]{kana}[/bold] 的罗马音是：", end="")
        user = input().strip().lower()

        if user == "q":
            break
            
        total_count += 1
        
        if user == romaji:
            # 答对的情况
            console.print("✅ 正确！", style="bold green")
            correct_count += 1
            
            if kana in data:
                # 增加间隔，减少错题次数
                current_interval = int(data[kana].get("interval", 1))
                data[kana]["interval"] = max(1, current_interval * INTERVAL_MULTIPLIER)
                data[kana]["last_review"] = today_str()
                current_wrong = int(data[kana].get("wrong_count", 0))
                data[kana]["wrong_count"] = max(0, current_wrong - 1)
                
                # 如果错题次数为0且间隔足够长，从错题记录中删除
                if (data[kana]["wrong_count"] == 0 and 
                    data[kana]["interval"] > MAX_INTERVAL):
                    del data[kana]
        else:
            # 答错的情况
            console.print(f"❌ 错误，正确答案是: {romaji}", style="bold red")
            
            if kana not in data:
                data[kana] = {
                    "wrong_count": 0, 
                    "last_review": today_str(), 
                    "interval": 1
                }
            
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
        rate = (correct_count / total_count * 100) if total_count > 0 else 0
        console.print(f"[cyan]当前正确率: {correct_count}/{total_count} ({rate:.1f}%)[/cyan]")

    # 更新统计并结束
    update_stats(total_count, correct_count)
    console.print("[green]练习会话结束并已保存统计。[/green]")
