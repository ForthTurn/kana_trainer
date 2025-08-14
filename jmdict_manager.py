#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JMdict词典管理器
用于查找包含特定假名的词汇
"""

import json
import os
import random
from typing import List, Dict, Optional


class JMdictManager:
    """JMdict词典管理器"""

    def __init__(self, file_path: str = "JMdict/JMdict.json"):
        """初始化JMdict管理器"""
        self.file_path = file_path
        self.data = None
        self.words = []
        self.kana_index = {}  # 假名到词条索引的映射

    def load_data(self) -> bool:
        """加载JMdict数据"""
        if not os.path.exists(self.file_path):
            print(f"JMdict文件不存在: {self.file_path}")
            return False

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

            if "words" in self.data:
                self.words = self.data["words"]
                print(f"✓ 成功加载 {len(self.words)} 个词条")
                self._build_kana_index()
                return True
            else:
                print("JMdict文件格式错误：缺少words字段")
                return False

        except Exception as e:
            print(f"加载JMdict文件时出错: {e}")
            return False

    def _build_kana_index(self):
        """构建假名索引"""
        print("正在构建假名索引...")
        self.kana_index = {}

        for i, word in enumerate(self.words):
            if "kana" in word and word["kana"]:
                for kana_item in word["kana"]:
                    if "text" in kana_item:
                        kana_text = kana_item["text"]
                        # 将假名分解为单个字符
                        for char in kana_text:
                            if char not in self.kana_index:
                                self.kana_index[char] = []
                            self.kana_index[char].append(i)

        print(f"✓ 索引构建完成，包含 {len(self.kana_index)} 个假名字符")

    def find_words_with_kana(self, kana: str, max_results: int = 5) -> List[Dict]:
        """查找包含指定假名的词汇"""
        if not self.data:
            print("请先加载JMdict数据")
            return []

        if kana not in self.kana_index:
            return []

        # 获取包含该假名的词条索引
        word_indices = self.kana_index[kana]

        # 随机选择一些词条
        selected_indices = random.sample(word_indices, min(max_results, len(word_indices)))

        results = []
        for idx in selected_indices:
            word = self.words[idx]
            word_info = self._extract_word_info(word)
            results.append(word_info)

        return results

    def _extract_word_info(self, word: Dict) -> Dict:
        """提取词条的关键信息"""
        word_info = {
            "id": word.get("id", ""),
            "kanji": [],
            "kana": [],
            "meanings": [],
            "part_of_speech": [],
            "examples": [],
        }

        # 提取汉字
        if "kanji" in word and word["kanji"]:
            for kanji_item in word["kanji"]:
                if "text" in kanji_item:
                    word_info["kanji"].append(kanji_item["text"])

        # 提取假名
        if "kana" in word and word["kana"]:
            for kana_item in word["kana"]:
                if "text" in kana_item:
                    word_info["kana"].append(kana_item["text"])

        # 提取含义和词性
        if "sense" in word and word["sense"]:
            for sense_item in word["sense"]:
                # 词性
                if "partOfSpeech" in sense_item:
                    word_info["part_of_speech"].extend(sense_item["partOfSpeech"])

                # 含义
                if "gloss" in sense_item:
                    for gloss_item in sense_item["gloss"]:
                        if "text" in gloss_item:
                            word_info["meanings"].append(gloss_item["text"])

                # 例句
                if "examples" in sense_item and sense_item["examples"]:
                    for example in sense_item["examples"]:
                        if "sentences" in example:
                            for sentence in example["sentences"]:
                                if sentence.get("land") == "jpn" and "text" in sentence:
                                    word_info["examples"].append(sentence["text"])

        # 去重
        word_info["kanji"] = list(set(word_info["kanji"]))
        word_info["kana"] = list(set(word_info["kana"]))
        word_info["meanings"] = list(set(word_info["meanings"]))
        word_info["part_of_speech"] = list(set(word_info["part_of_speech"]))
        word_info["examples"] = list(set(word_info["examples"]))

        return word_info

    def get_random_word_with_kana(self, kana: str) -> Optional[Dict]:
        """随机获取一个包含指定假名的词汇"""
        words = self.find_words_with_kana(kana, max_results=10)
        if words:
            return random.choice(words)
        return None

    def format_word_display(self, word_info: Dict) -> str:
        """格式化词汇显示信息"""
        if not word_info:
            return "未找到相关词汇"

        lines = []

        # 汉字
        if word_info["kanji"]:
            lines.append(f"汉字: {' '.join(word_info['kanji'])}")

        # 假名
        if word_info["kana"]:
            lines.append(f"假名: {' '.join(word_info['kana'])}")

        # 词性
        if word_info["part_of_speech"]:
            lines.append(f"词性: {', '.join(word_info['part_of_speech'])}")

        # 含义
        if word_info["meanings"]:
            lines.append(f"含义: {'; '.join(word_info['meanings'][:3])}")  # 只显示前3个含义

        # 例句
        if word_info["examples"]:
            lines.append(f"例句: {word_info['examples'][0]}")  # 只显示第一个例句

        return "\n".join(lines)


def test_jmdict_manager():
    """测试JMdict管理器"""
    manager = JMdictManager()

    if manager.load_data():
        # 测试查找包含假名"あ"的词汇
        print("\n" + "=" * 50)
        print("测试：查找包含假名'あ'的词汇")
        print("=" * 50)

        words = manager.find_words_with_kana("あ", max_results=3)
        for i, word in enumerate(words):
            print(f"\n词汇 {i + 1}:")
            print(manager.format_word_display(word))

        # 测试查找包含假名"い"的词汇
        print("\n" + "=" * 50)
        print("测试：查找包含假名'い'的词汇")
        print("=" * 50)

        words = manager.find_words_with_kana("い", max_results=3)
        for i, word in enumerate(words):
            print(f"\n词汇 {i + 1}:")
            print(manager.format_word_display(word))


if __name__ == "__main__":
    test_jmdict_manager()
