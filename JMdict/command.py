import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from .load_jmdict import update_jmdict

console = Console()


def clear_screen():
    """清屏函数"""
    os.system("cls" if os.name == "nt" else "clear")


def show_jmdict_header():
    """显示JMdict更新头部"""
    clear_screen()
    title_text = Text("🔄 更新JMdict词典", style="bold cyan")
    title_panel = Panel(title_text, border_style="cyan", padding=(0, 2))
    console.print(title_panel)
    console.print()


def update_jmdict_command():
    """JMdict更新命令"""
    show_jmdict_header()
    console.print("[yellow]正在检查并更新JMdict词典...[/yellow]")
    console.print()

    update_jmdict()

    console.print("\n[green]词典更新操作完成！[/green]")
