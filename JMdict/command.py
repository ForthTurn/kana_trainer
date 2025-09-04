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

    # 更新词典
    update_jmdict()

    # 询问是否要迁移到数据库
    console.print("\n[cyan]是否要将词典数据迁移到SQLite数据库？[/cyan]")
    console.print("这将提高查询性能并减少内存使用。")

    response = input("是否继续？(y/n): ").lower().strip()
    if response == "y":
        migrate_to_database()
    else:
        console.print("[yellow]跳过数据库迁移[/yellow]")

    console.print("\n[green]词典更新操作完成！[/green]")


def migrate_to_database():
    """将词典数据迁移到SQLite数据库"""
    console.print("\n[cyan]开始数据迁移...[/cyan]")

    try:
        from .migrate_to_sqlite import JMdictMigrator

        # 创建迁移器实例
        json_file_path = os.path.join(os.path.dirname(__file__), "JMdict.json")
        db_path = os.path.join(os.path.dirname(__file__), "jmdict.db")

        if not os.path.exists(json_file_path):
            console.print("[red]错误: 找不到JMdict.json文件，请先更新词典[/red]")
            return

        migrator = JMdictMigrator(json_file_path, db_path)

        # 创建数据库
        migrator.create_database()

        # 加载JSON数据
        data = migrator.load_json_data()

        if not data:
            console.print("[red]错误: 无法加载JSON数据[/red]")
            return

        # 迁移数据
        migrator.migrate_data(data)

        # 关闭连接
        migrator.close()

        console.print(f"[bold green]✓ 数据迁移完成！数据库文件: {db_path}[/bold green]")
        console.print("[cyan]现在你可以使用SQLite数据库进行快速查询了！[/cyan]")

    except ImportError:
        console.print("[red]错误: 无法导入迁移模块，请确保migrate_to_sqlite.py文件存在[/red]")
    except Exception as e:
        console.print(f"[red]数据迁移失败: {e}[/red]")
        console.print("[yellow]你可以稍后手动运行迁移脚本[/yellow]")
