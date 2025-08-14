import os
import zipfile
import requests
from rich.console import Console
from .schema import GithubRelease

from config import (
    JMDICT_URL,
    PROXY,
    TEMP_DIR,
    JMDICT_LOCAL_PATH,
    JMDICT_ASSET_PREFIX,
    JMDICT_ASSET_SUFFIX,
    JMDICT_ZIP_PATH,
)

console = Console()


def get_latest_release() -> GithubRelease | None:
    response = requests.get(JMDICT_URL, proxies={"http": PROXY, "https": PROXY})
    if response.status_code == 200:
        release = GithubRelease.model_validate_json(response.text)
        return release
    else:
        console.print(f"[red]获取发布版本失败: HTTP {response.status_code}[/red]")
        console.print(f"[red]错误信息: {response.text}[/red]")
        return None


def update_jmdict():
    console.print(f"[yellow]正在更新 {JMDICT_LOCAL_PATH}...[/yellow]")
    release = get_latest_release()
    if release:
        for asset in release.assets:
            if asset.name.startswith(JMDICT_ASSET_PREFIX) and asset.name.endswith(JMDICT_ASSET_SUFFIX):
                console.print(f"[green]找到资源: {asset.name}[/green]")
                console.print(f"[blue]创建时间: {asset.created_at}, 上传者: {asset.uploader.login}[/blue]")
                console.print(f"[yellow]正在下载 {asset.name}...[/yellow]")

                response = requests.get(asset.browser_download_url, proxies={"http": PROXY, "https": PROXY})
                with open(os.path.join(TEMP_DIR, JMDICT_ZIP_PATH), "wb") as f:
                    f.write(response.content)

                console.print(f"[yellow]正在解压到 {JMDICT_LOCAL_PATH}...[/yellow]")
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
                    else:
                        console.print(f"[red]zip文件中包含多个文件，请手动解压到 {JMDICT_LOCAL_PATH} 目录下[/red]")
                        return

                console.print(f"[green]✓ 更新完成: {JMDICT_LOCAL_PATH}[/green]")
                break
    else:
        console.print("[red]未找到可用的发布版本[/red]")
