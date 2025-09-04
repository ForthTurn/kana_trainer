import os
import zipfile

import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from config import (
    JMDICT_ASSET_PREFIX,
    JMDICT_ASSET_SUFFIX,
    JMDICT_LOCAL_PATH,
    JMDICT_URL,
    JMDICT_ZIP_PATH,
    PROXY,
    TEMP_DIR,
)

from .schema import GithubRelease

console = Console()


def get_latest_release() -> GithubRelease | None:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("正在获取最新发布版本...", total=None)

        try:
            response = requests.get(JMDICT_URL, proxies={"http": PROXY, "https": PROXY})
            if response.status_code == 200:
                release = GithubRelease.model_validate_json(response.text)
                progress.update(task, description="✓ 获取发布版本成功")
                return release
            else:
                progress.update(task, description=f"✗ 获取发布版本失败: HTTP {response.status_code}")
                console.print(f"[red]错误信息: {response.text}[/red]")
                return None
        except Exception as e:
            progress.update(task, description=f"✗ 获取发布版本出错: {e}")
            return None


def update_jmdict():
    console.print(f"[yellow]正在更新 {JMDICT_LOCAL_PATH}...[/yellow]")

    release = get_latest_release()
    if not release:
        error_text = Text("未找到可用的发布版本", style="red")
        error_panel = Panel(error_text, border_style="red", padding=(1, 2))
        console.print(error_panel)
        return

    # 查找合适的资源文件
    target_asset = None
    for asset in release.assets:
        if asset.name.startswith(JMDICT_ASSET_PREFIX) and asset.name.endswith(JMDICT_ASSET_SUFFIX):
            target_asset = asset
            break

    if not target_asset:
        error_text = Text("未找到合适的词典文件", style="red")
        error_panel = Panel(error_text, border_style="red", padding=(1, 2))
        console.print(error_panel)
        return

    # 显示资源信息
    asset_info = Text(
        f"找到资源: {target_asset.name}\n"
        f"创建时间: {target_asset.created_at}\n"
        f"上传者: {target_asset.uploader.login}\n"
        f"文件大小: {target_asset.size / 1024 / 1024:.1f} MB",
        style="cyan",
    )
    asset_panel = Panel(asset_info, border_style="cyan", padding=(1, 2))
    console.print(asset_panel)

    # 下载文件
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        download_task = progress.add_task("正在下载词典文件...", total=None)

        try:
            response = requests.get(target_asset.browser_download_url, proxies={"http": PROXY, "https": PROXY})
            with open(os.path.join(TEMP_DIR, JMDICT_ZIP_PATH), "wb") as f:
                f.write(response.content)
            progress.update(download_task, description="✓ 下载完成")
        except Exception as e:
            progress.update(download_task, description=f"✗ 下载失败: {e}")
            return

    # 解压文件
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        extract_task = progress.add_task("正在解压词典文件...", total=None)

        try:
            with zipfile.ZipFile(os.path.join(TEMP_DIR, JMDICT_ZIP_PATH), "r") as zip_ref:
                # 获取zip文件中的文件列表
                file_list = zip_ref.namelist()
                if len(file_list) == 1:
                    # 如果zip中只有一个文件，直接解压并移动
                    zip_ref.extract(file_list[0], TEMP_DIR)
                    temp_file = os.path.join(TEMP_DIR, file_list[0])
                    if os.path.exists(JMDICT_LOCAL_PATH):
                        os.remove(JMDICT_LOCAL_PATH)
                    os.replace(temp_file, JMDICT_LOCAL_PATH)
                    progress.update(extract_task, description="✓ 解压完成")
                else:
                    progress.update(extract_task, description="✗ zip文件包含多个文件")
                    error_text = Text(f"zip文件中包含多个文件，请手动解压到 {JMDICT_LOCAL_PATH} 目录下", style="red")
                    error_panel = Panel(error_text, border_style="red", padding=(1, 2))
                    console.print(error_panel)
                    return
        except Exception as e:
            progress.update(extract_task, description=f"✗ 解压失败: {e}")
            return

    # 清理临时文件
    try:
        os.remove(os.path.join(TEMP_DIR, JMDICT_ZIP_PATH))
    except:
        pass

    # 显示成功信息
    success_text = Text(f"✓ 词典更新完成！\n文件路径: {JMDICT_LOCAL_PATH}", style="bold green")
    success_panel = Panel(success_text, border_style="green", padding=(1, 2))
    console.print(success_panel)
