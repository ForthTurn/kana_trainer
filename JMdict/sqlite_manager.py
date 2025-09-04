#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JMdict SQLite数据库管理器
用于从SQLite数据库中查询JMdict数据
"""

import random
import sqlite3
from typing import Dict, List, Optional

from rich.console import Console

console = Console()


class JMdictSQLiteManager:
    """JMdict SQLite数据库管理器"""

    def __init__(self, db_path: str = "jmdict.db"):
        """初始化SQLite管理器"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self) -> bool:
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            console.print(f"[green]✓ 成功连接到数据库: {self.db_path}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]✗ 连接数据库失败: {e}[/red]")
            return False

    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            console.print("[green]✓ 数据库连接已断开[/green]")

    def find_words_with_kana(self, kana: str, max_results: int = 5) -> List[Dict]:
        """查找包含指定假名的词汇"""
        if not self.conn:
            console.print("[red]请先连接数据库[/red]")
            return []

        try:
            # 使用LIKE操作符查找包含指定假名的词汇
            query = """
                SELECT DISTINCT w.id, w.kanji, w.kana, w.common
                FROM words w
                WHERE w.kana LIKE ?
                ORDER BY w.common DESC, w.id
                LIMIT ?
            """

            self.cursor.execute(query, (f"%{kana}%", max_results))
            words = self.cursor.fetchall()

            results = []
            for word in words:
                word_id, kanji, kana_text, common = word
                word_info = self._get_word_details(word_id)
                results.append(word_info)

            return results

        except Exception as e:
            console.print(f"[red]查询失败: {e}[/red]")
            return []

    def get_random_word_with_kana(self, kana: str) -> Optional[Dict]:
        """随机获取一个包含指定假名的词汇"""
        words = self.find_words_with_kana(kana, max_results=10)
        if words:
            return random.choice(words)
        return None

    def search_by_kanji(self, kanji: str, max_results: int = 5) -> List[Dict]:
        """根据汉字搜索词汇"""
        if not self.conn:
            console.print("[red]请先连接数据库[/red]")
            return []

        try:
            query = """
                SELECT DISTINCT w.id, w.kanji, w.kana, w.common
                FROM words w
                WHERE w.kanji LIKE ?
                ORDER BY w.common DESC, w.id
                LIMIT ?
            """

            self.cursor.execute(query, (f"%{kanji}%", max_results))
            words = self.cursor.fetchall()

            results = []
            for word in words:
                word_id, kanji_text, kana_text, common = word
                word_info = self._get_word_details(word_id)
                results.append(word_info)

            return results

        except Exception as e:
            console.print(f"[red]查询失败: {e}[/red]")
            return []

    def search_by_meaning(self, meaning: str, max_results: int = 5) -> List[Dict]:
        """根据英文含义搜索词汇"""
        if not self.conn:
            console.print("[red]请先连接数据库[/red]")
            return []

        try:
            query = """
                SELECT DISTINCT w.id, w.kanji, w.kana, w.common
                FROM words w
                JOIN senses s ON w.id = s.word_id
                WHERE s.gloss LIKE ?
                ORDER BY w.common DESC, w.id
                LIMIT ?
            """

            self.cursor.execute(query, (f"%{meaning}%", max_results))
            words = self.cursor.fetchall()

            results = []
            for word in words:
                word_id, kanji_text, kana_text, common = word
                word_info = self._get_word_details(word_id)
                results.append(word_info)

            return results

        except Exception as e:
            console.print(f"[red]查询失败: {e}[/red]")
            return []

    def get_common_words(self, max_results: int = 10) -> List[Dict]:
        """获取常用词汇"""
        if not self.conn:
            console.print("[red]请先连接数据库[/red]")
            return []

        try:
            query = """
                SELECT w.id, w.kanji, w.kana, w.common
                FROM words w
                WHERE w.common = 1
                ORDER BY w.id
                LIMIT ?
            """

            self.cursor.execute(query, (max_results,))
            words = self.cursor.fetchall()

            results = []
            for word in words:
                word_id, kanji_text, kana_text, common = word
                word_info = self._get_word_details(word_id)
                results.append(word_info)

            return results

        except Exception as e:
            console.print(f"[red]查询失败: {e}[/red]")
            return []

    def _get_word_details(self, word_id: str) -> Dict:
        """获取词汇的详细信息"""
        try:
            # 获取基本信息
            self.cursor.execute("SELECT kanji, kana, common FROM words WHERE id = ?", (word_id,))
            kanji, kana, common = self.cursor.fetchone()

            # 获取senses信息
            self.cursor.execute(
                """
                SELECT part_of_speech, related, antonym, field, dialect, misc, info, language_source, gloss
                FROM senses WHERE word_id = ?
            """,
                (word_id,),
            )
            senses = self.cursor.fetchall()

            # 获取examples信息
            self.cursor.execute("SELECT example_text FROM examples WHERE word_id = ? ORDER BY sense_index", (word_id,))
            examples = [row[0] for row in self.cursor.fetchall()]

            word_info = {
                "id": word_id,
                "kanji": kanji.split(", ") if kanji else [],
                "kana": kana.split(", ") if kana else [],
                "common": bool(common),
                "meanings": [],
                "part_of_speech": [],
                "examples": examples,
            }

            # 处理senses信息
            for sense in senses:
                part_of_speech, related, antonym, field, dialect, misc, info, language_source, gloss = sense

                if part_of_speech:
                    word_info["part_of_speech"].extend(part_of_speech.split(", "))

                if gloss:
                    word_info["meanings"].extend(gloss.split(", "))

            # 去重
            word_info["kanji"] = list(set(word_info["kanji"]))
            word_info["kana"] = list(set(word_info["kana"]))
            word_info["meanings"] = list(set(word_info["meanings"]))
            word_info["part_of_speech"] = list(set(word_info["part_of_speech"]))
            word_info["examples"] = list(set(word_info["examples"]))

            return word_info

        except Exception as e:
            console.print(f"[yellow]警告: 获取词汇 {word_id} 详细信息时出错: {e}[/yellow]")
            return {"id": word_id, "error": str(e)}

    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        if not self.conn:
            return {}

        try:
            stats = {}

            # 统计words表
            self.cursor.execute("SELECT COUNT(*) FROM words")
            stats["total_words"] = self.cursor.fetchone()[0]

            # 统计常用词
            self.cursor.execute("SELECT COUNT(*) FROM words WHERE common = 1")
            stats["common_words"] = self.cursor.fetchone()[0]

            # 统计senses表
            self.cursor.execute("SELECT COUNT(*) FROM senses")
            stats["total_senses"] = self.cursor.fetchone()[0]

            # 统计examples表
            self.cursor.execute("SELECT COUNT(*) FROM examples")
            stats["total_examples"] = self.cursor.fetchone()[0]

            return stats

        except Exception as e:
            console.print(f"[red]获取统计信息失败: {e}[/red]")
            return {}

    def format_word_display(self, word_info: Dict) -> str:
        """格式化词汇显示信息"""
        if not word_info:
            return "未找到相关词汇"

        if "error" in word_info:
            return f"获取词汇信息时出错: {word_info['error']}"

        lines = []

        # 汉字
        if word_info["kanji"]:
            lines.append(f"汉字: {' '.join(word_info['kanji'])}")

        # 假名
        if word_info["kana"]:
            lines.append(f"假名: {' '.join(word_info['kana'])}")

        # 常用词标记
        if word_info["common"]:
            lines.append("常用词: 是")

        # 词性
        if word_info["part_of_speech"]:
            lines.append(f"词性: {', '.join(word_info['part_of_speech'][:3])}")  # 只显示前3个词性

        # 含义
        if word_info["meanings"]:
            lines.append(f"含义: {'; '.join(word_info['meanings'][:3])}")  # 只显示前3个含义

        # 例句
        if word_info["examples"]:
            lines.append(f"例句: {word_info['examples'][0]}")  # 只显示第一个例句

        return "\n".join(lines)
