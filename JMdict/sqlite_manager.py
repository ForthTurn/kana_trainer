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

from kana_data import kana_romaji, romaji_hiragana, romaji_katakana, special_romaji_mappings

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
        """查找包含指定假名的词汇，优先返回常用词"""
        if not self.conn:
            console.print("[red]请先连接数据库[/red]")
            return []

        try:
            # 优先查找常用词，然后查找其他词汇
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
        """随机获取一个包含指定假名的词汇，优先选择常用词"""
        words = self.find_words_with_kana(kana, max_results=10)
        if not words:
            return None

        # 优先选择常用词
        common_words = [word for word in words if word.get("common", False)]
        if common_words:
            return random.choice(common_words)

        # 如果没有常用词，则随机选择一个
        return random.choice(words)

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

    def _kana_to_romaji(self, kana: str) -> str:
        """使用kana_data中的映射进行假名到罗马音转换，处理特殊情况"""
        if not kana:
            return ""

        result = ""
        i = 0
        while i < len(kana):
            char = kana[i]

            # 处理特殊情况
            if char == "は" and i > 0:
                # 在助词位置（通常是第二个字符或更后）读作wa
                result += "wa"
            elif char == "へ" and i > 0:
                # 在助词位置读作e
                result += "e"
            elif char == "を" and i > 0:
                # 在助词位置读作o
                result += "o"
            # 直接查找映射
            elif char in kana_romaji:
                result += kana_romaji[char]
            # 处理小字符（如ゃ、ゅ、ょ）
            elif i > 0 and char in ["ゃ", "ゅ", "ょ", "ャ", "ュ", "ョ"]:
                # 替换前一个字符的最后一个字母
                if result and result[-1] == "i":
                    result = result[:-1] + char.replace("ゃ", "a").replace("ゅ", "u").replace("ょ", "o").replace(
                        "ャ", "a"
                    ).replace("ュ", "u").replace("ョ", "o")
                else:
                    result += char
            # 其他字符保持原样
            else:
                result += char

            i += 1

        return result

    def _romaji_to_kana(self, romaji: str) -> List[str]:
        """使用kana_data中的映射将罗马音转换为可能的假名组合"""
        if not romaji:
            return []

        # 生成可能的假名组合
        possible_kanas = set()

        # 处理特殊情况（助词）
        if romaji in special_romaji_mappings:
            possible_kanas.update(special_romaji_mappings[romaji])

        # 直接匹配平假名
        if romaji in romaji_hiragana:
            possible_kanas.add(romaji_hiragana[romaji])

        # 直接匹配片假名
        if romaji in romaji_katakana:
            possible_kanas.add(romaji_katakana[romaji])

        # 尝试将罗马音分解为更小的部分进行匹配
        # 例如 "nori" 可以分解为 "no" + "ri"
        for i in range(1, len(romaji)):
            part1 = romaji[:i]
            part2 = romaji[i:]

            # 查找两个部分对应的假名
            kana1_list = []
            kana2_list = []

            if part1 in romaji_hiragana:
                kana1_list.append(romaji_hiragana[part1])
            if part1 in romaji_katakana:
                kana1_list.append(romaji_katakana[part1])

            if part2 in romaji_hiragana:
                kana2_list.append(romaji_hiragana[part2])
            if part2 in romaji_katakana:
                kana2_list.append(romaji_katakana[part2])

            # 组合可能的假名
            for kana1 in kana1_list:
                for kana2 in kana2_list:
                    possible_kanas.add(kana1 + kana2)

        # 尝试更复杂的分解（最多3个部分）
        if len(romaji) > 3:
            for i in range(1, len(romaji) - 1):
                for j in range(i + 1, len(romaji)):
                    part1 = romaji[:i]
                    part2 = romaji[i:j]
                    part3 = romaji[j:]

                    # 查找三个部分对应的假名
                    kana1_list = []
                    kana2_list = []
                    kana3_list = []

                    if part1 in romaji_hiragana:
                        kana1_list.append(romaji_hiragana[part1])
                    if part1 in romaji_katakana:
                        kana1_list.append(romaji_katakana[part1])

                    if part2 in romaji_hiragana:
                        kana2_list.append(romaji_hiragana[part2])
                    if part2 in romaji_katakana:
                        kana2_list.append(romaji_katakana[part2])

                    if part3 in romaji_hiragana:
                        kana3_list.append(romaji_hiragana[part3])
                    if part3 in romaji_katakana:
                        kana3_list.append(romaji_katakana[part3])

                    # 组合可能的假名
                    for kana1 in kana1_list:
                        for kana2 in kana2_list:
                            for kana3 in kana3_list:
                                possible_kanas.add(kana1 + kana2 + kana3)

        return list(possible_kanas)

    def search_by_romaji(self, romaji: str, max_results: int = 5) -> List[Dict]:
        """根据罗马音搜索词汇（优化版本）"""
        if not self.conn:
            console.print("[red]请先连接数据库[/red]")
            return []

        try:
            # 将罗马音转换为可能的假名组合
            possible_kanas = self._romaji_to_kana(romaji.lower())

            if not possible_kanas:
                return []

            # 构建SQL查询条件
            conditions = []
            params = []

            for kana in possible_kanas:
                conditions.append("w.kana LIKE ?")
                params.append(f"%{kana}%")

            # 使用OR条件查询包含任何匹配假名的词汇
            query = f"""
                SELECT DISTINCT w.id, w.kanji, w.kana, w.common
                FROM words w
                WHERE {" OR ".join(conditions)}
                ORDER BY w.common DESC, w.id
                LIMIT ?
            """

            params.append(max_results)
            self.cursor.execute(query, params)
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
