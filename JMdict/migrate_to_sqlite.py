#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JMdict数据迁移脚本
将JSON数据迁移到SQLite数据库中
"""

import json
import os
import sqlite3
from typing import Any, Dict, List

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class JMdictMigrator:
    """JMdict数据迁移器"""

    def __init__(self, json_file_path: str, db_path: str):
        """初始化迁移器"""
        self.json_file_path = json_file_path
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def create_database(self):
        """创建数据库和表结构"""
        try:
            # 连接数据库（如果不存在则创建）
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            # 创建words表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY,
                    kanji TEXT,
                    kana TEXT,
                    common BOOLEAN
                )
            """)

            # 创建senses表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS senses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word_id INTEGER,
                    part_of_speech TEXT,
                    related TEXT,
                    antonym TEXT,
                    field TEXT,
                    dialect TEXT,
                    misc TEXT,
                    info TEXT,
                    language_source TEXT,
                    gloss TEXT,
                    FOREIGN KEY (word_id) REFERENCES words (id)
                )
            """)

            # 创建examples表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS examples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word_id INTEGER,
                    sense_index INTEGER,
                    example_text TEXT,
                    FOREIGN KEY (word_id) REFERENCES words (id)
                )
            """)

            # 创建索引以提高查询性能
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_words_id ON words (id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_senses_word_id ON senses (word_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_examples_word_id ON examples (word_id)")

            self.conn.commit()
            console.print("[green]✓ 数据库和表结构创建成功[/green]")

        except Exception as e:
            console.print(f"[red]✗ 创建数据库失败: {e}[/red]")
            raise

    def load_json_data(self) -> Dict[str, Any]:
        """加载JSON数据"""
        try:
            with open(self.json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            console.print(f"[green]✓ 成功加载JSON数据，包含 {len(data.get('words', []))} 个词条[/green]")
            return data
        except Exception as e:
            console.print(f"[red]✗ 加载JSON数据失败: {e}[/red]")
            raise

    def migrate_data(self, data: Dict[str, Any]):
        """迁移数据到数据库"""
        words = data.get("words", [])

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
        ) as progress:
            task = progress.add_task("正在迁移数据...", total=len(words))

            for word in words:
                try:
                    # 插入words表
                    word_id = word.get("id")
                    kanji_text = self._extract_kanji_text(word.get("kanji", []))
                    kana_text = self._extract_kana_text(word.get("kana", []))
                    is_common = self._is_common_word(word.get("kana", []))

                    self.cursor.execute(
                        """
                        INSERT OR REPLACE INTO words (id, kanji, kana, common)
                        VALUES (?, ?, ?, ?)
                    """,
                        (word_id, kanji_text, kana_text, is_common),
                    )

                    # 插入senses表
                    for sense_index, sense in enumerate(word.get("sense", [])):
                        self._insert_sense(word_id, sense)

                        # 插入examples表
                        self._insert_examples(word_id, sense_index, sense.get("examples", []))

                    progress.update(task, advance=1)

                except Exception as e:
                    console.print(f"[yellow]警告: 迁移词条 {word.get('id', 'unknown')} 时出错: {e}[/yellow]")
                    continue

            self.conn.commit()
            progress.update(task, description="✓ 数据迁移完成")

    def _extract_kanji_text(self, kanji_list: List[Dict]) -> str:
        """提取汉字文本"""
        if not kanji_list:
            return ""
        texts = [kanji.get("text", "") for kanji in kanji_list if kanji.get("text")]
        return ", ".join(texts)

    def _extract_kana_text(self, kana_list: List[Dict]) -> str:
        """提取假名文本"""
        if not kana_list:
            return ""
        texts = [kana.get("text", "") for kana in kana_list if kana.get("text")]
        return ", ".join(texts)

    def _is_common_word(self, kana_list: List[Dict]) -> bool:
        """判断是否为常用词"""
        return any(kana.get("common", False) for kana in kana_list)

    def _insert_sense(self, word_id: str, sense: Dict) -> int:
        """插入sense数据并返回sense_id"""
        part_of_speech = ", ".join([str(item) for item in sense.get("partOfSpeech", [])])
        related = ", ".join([", ".join([str(item) for item in rel]) for rel in sense.get("related", [])])
        antonym = ", ".join([", ".join([str(item) for item in ant]) for ant in sense.get("antonym", [])])
        field = ", ".join([str(item) for item in sense.get("field", [])])
        dialect = ", ".join([str(item) for item in sense.get("dialect", [])])
        misc = ", ".join([str(item) for item in sense.get("misc", [])])
        info = ", ".join([str(item) for item in sense.get("info", [])])
        language_source = self._format_language_source(sense.get("languageSource", []))
        gloss = ", ".join([str(g.get("text", "")) for g in sense.get("gloss", [])])

        self.cursor.execute(
            """
            INSERT INTO senses (word_id, part_of_speech, related, antonym, field, 
                              dialect, misc, info, language_source, gloss)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (word_id, part_of_speech, related, antonym, field, dialect, misc, info, language_source, gloss),
        )

        return self.cursor.lastrowid

    def _format_language_source(self, language_source_list: List[Dict]) -> str:
        """格式化语言来源信息"""
        if not language_source_list:
            return ""
        sources = []
        for source in language_source_list:
            lang = str(source.get("lang", ""))
            text = str(source.get("text", ""))
            if lang and text:
                sources.append(f"{lang}:{text}")
        return ", ".join(sources)

    def _insert_examples(self, word_id: str, sense_index: int, examples: List[Dict]):
        """插入示例数据"""
        for example in examples:
            if "sentences" in example:
                for sentence in example["sentences"]:
                    if sentence.get("land") == "jpn" and sentence.get("text"):
                        self.cursor.execute(
                            """
                            INSERT INTO examples (word_id, sense_index, example_text)
                            VALUES (?, ?, ?)
                        """,
                            (word_id, sense_index, sentence["text"]),
                        )

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            console.print("[green]✓ 数据库连接已关闭[/green]")


def main():
    """主函数"""
    json_file_path = "JMdict.json"
    db_path = "jmdict.db"

    if not os.path.exists(json_file_path):
        console.print(f"[red]错误: 找不到JSON文件 {json_file_path}[/red]")
        return

    migrator = JMdictMigrator(json_file_path, db_path)

    try:
        # 创建数据库
        migrator.create_database()

        # 加载JSON数据
        data = migrator.load_json_data()

        # 迁移数据
        migrator.migrate_data(data)

        console.print(f"[bold green]✓ 数据迁移完成！数据库文件: {db_path}[/bold green]")

    except Exception as e:
        console.print(f"[red]✗ 迁移失败: {e}[/red]")
    finally:
        migrator.close()


if __name__ == "__main__":
    main()
