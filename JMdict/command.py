import os

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .load_jmdict import update_jmdict
from .sqlite_manager import JMdictSQLiteManager

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


def show_search_header():
    """显示查词功能头部"""
    clear_screen()
    title_text = Text("📖 查词功能", style="bold green")
    title_panel = Panel(title_text, border_style="green", padding=(0, 2))
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


def search_word_command():
    """查词功能命令"""
    show_search_header()

    # 检查数据库文件是否存在
    db_path = os.path.join(os.path.dirname(__file__), "jmdict.db")
    if not os.path.exists(db_path):
        console.print("[red]错误: 找不到数据库文件，请先更新词典并迁移到数据库[/red]")
        console.print("[yellow]提示: 请先选择'更新词典'选项[/yellow]")
        return

    # 创建数据库管理器
    manager = JMdictSQLiteManager(db_path)

    if not manager.connect():
        console.print("[red]错误: 无法连接到数据库[/red]")
        return

    try:
        while True:
            choice = inquirer.select(
                message="请选择查询方式:",
                choices=[
                    {"name": "🔤 按假名查询", "value": "kana"},
                    {"name": "🈯 按汉字查询", "value": "kanji"},
                    {"name": "🇺🇸 按英文含义查询", "value": "meaning"},
                    {"name": "🔤 按罗马音查询", "value": "romaji"},
                    {"name": "⭐ 查看常用词汇", "value": "common"},
                    {"name": "🔙 返回主菜单", "value": "back"},
                ],
                pointer=">",
                instruction="(用上下键选择，Enter确认)",
            ).execute()

            if choice == "back":
                break
            elif choice == "kana":
                search_by_kana(manager)
            elif choice == "kanji":
                search_by_kanji(manager)
            elif choice == "meaning":
                search_by_meaning(manager)
            elif choice == "romaji":
                search_by_romaji(manager)
            elif choice == "common":
                show_common_words(manager)

    finally:
        manager.disconnect()


def search_by_kana(manager: JMdictSQLiteManager):
    """按假名查询"""
    console.print("\n[bold cyan]🔤 按假名查询[/bold cyan]")
    kana = input("请输入假名: ").strip()

    if not kana:
        console.print("[red]请输入有效的假名[/red]")
        return

    console.print(f"\n[green]正在查询包含假名 '{kana}' 的词汇...[/green]")
    words = manager.find_words_with_kana(kana, max_results=10)

    if words:
        console.print(f"\n[bold]找到 {len(words)} 个相关词汇:[/bold]")
        for i, word in enumerate(words, 1):
            console.print(f"\n[bold cyan]词汇 {i}:[/bold cyan]")
            console.print(manager.format_word_display(word))
    else:
        console.print("[yellow]未找到相关词汇[/yellow]")

    input("\n按 Enter 键继续...")
    clear_screen()
    show_search_header()


def search_by_kanji(manager: JMdictSQLiteManager):
    """按汉字查询"""
    console.print("\n[bold cyan]🈯 按汉字查询[/bold cyan]")
    kanji = input("请输入汉字: ").strip()

    if not kanji:
        console.print("[red]请输入有效的汉字[/red]")
        return

    console.print(f"\n[green]正在查询包含汉字 '{kanji}' 的词汇...[/green]")
    words = manager.search_by_kanji(kanji, max_results=10)

    if words:
        console.print(f"\n[bold]找到 {len(words)} 个相关词汇:[/bold]")
        for i, word in enumerate(words, 1):
            console.print(f"\n[bold cyan]词汇 {i}:[/bold cyan]")
            console.print(manager.format_word_display(word))
    else:
        console.print("[yellow]未找到相关词汇[/yellow]")

    input("\n按 Enter 键继续...")
    clear_screen()
    show_search_header()


def search_by_meaning(manager: JMdictSQLiteManager):
    """按英文含义查询"""
    console.print("\n[bold cyan]🇺🇸 按英文含义查询[/bold cyan]")
    meaning = input("请输入英文含义: ").strip()

    if not meaning:
        console.print("[red]请输入有效的英文含义[/red]")
        return

    console.print(f"\n[green]正在查询含义包含 '{meaning}' 的词汇...[/green]")
    words = manager.search_by_meaning(meaning, max_results=10)

    if words:
        console.print(f"\n[bold]找到 {len(words)} 个相关词汇:[/bold]")
        for i, word in enumerate(words, 1):
            console.print(f"\n[bold cyan]词汇 {i}:[/bold cyan]")
            console.print(manager.format_word_display(word))
    else:
        console.print("[yellow]未找到相关词汇[/yellow]")

    input("\n按 Enter 键继续...")
    clear_screen()
    show_search_header()


def search_by_romaji(manager: JMdictSQLiteManager):
    """按罗马音查询"""
    console.print("\n[bold cyan]🔤 按罗马音查询[/bold cyan]")
    romaji = input("请输入罗马音: ").strip()

    if not romaji:
        console.print("[red]请输入有效的罗马音[/red]")
        return

    console.print(f"\n[green]正在查询罗马音包含 '{romaji}' 的词汇...[/green]")
    words = manager.search_by_romaji(romaji, max_results=10)

    if words:
        console.print(f"\n[bold]找到 {len(words)} 个相关词汇:[/bold]")
        for i, word in enumerate(words, 1):
            console.print(f"\n[bold cyan]词汇 {i}:[/bold cyan]")
            console.print(manager.format_word_display(word))
    else:
        console.print("[yellow]未找到相关词汇[/yellow]")

    input("\n按 Enter 键继续...")
    clear_screen()
    show_search_header()


def show_common_words(manager: JMdictSQLiteManager):
    """显示常用词汇"""
    console.print("\n[bold cyan]⭐ 常用词汇列表[/bold cyan]")

    try:
        count = input("请输入要显示的词汇数量 (默认10): ").strip()
        count = int(count) if count.isdigit() else 10
    except ValueError:
        count = 10

    console.print(f"\n[green]正在获取 {count} 个常用词汇...[/green]")
    words = manager.get_common_words(max_results=count)

    if words:
        console.print(f"\n[bold]常用词汇 (共 {len(words)} 个):[/bold]")
        for i, word in enumerate(words, 1):
            console.print(f"\n[bold cyan]词汇 {i}:[/bold cyan]")
            console.print(manager.format_word_display(word))
    else:
        console.print("[yellow]未找到常用词汇[/yellow]")

    input("\n按 Enter 键继续...")
    clear_screen()
    show_search_header()


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
