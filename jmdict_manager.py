#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JMdict词典管理器
用于查找包含特定假名的词汇
支持SQLite数据库查询
"""

from typing import Dict, List, Optional

from JMdict.sqlite_manager import JMdictSQLiteManager


class JMdictManager:
    """JMdict词典管理器 - 使用SQLite数据库"""

    def __init__(self, db_path: str = "JMdict/jmdict.db"):
        """初始化JMdict管理器"""
        self.db_path = db_path
        self.sqlite_manager = JMdictSQLiteManager(db_path)

    def load_data(self) -> bool:
        """加载JMdict数据（连接SQLite数据库）"""
        return self.sqlite_manager.connect()

    def find_words_with_kana(self, kana: str, max_results: int = 5) -> List[Dict]:
        """查找包含指定假名的词汇"""
        return self.sqlite_manager.find_words_with_kana(kana, max_results)

    def get_random_word_with_kana(self, kana: str) -> Optional[Dict]:
        """随机获取一个包含指定假名的词汇"""
        return self.sqlite_manager.get_random_word_with_kana(kana)

    def format_word_display(self, word_info: Dict) -> str:
        """格式化词汇显示信息"""
        return self.sqlite_manager.format_word_display(word_info)


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

        # 断开数据库连接
        manager.sqlite_manager.disconnect()


if __name__ == "__main__":
    test_jmdict_manager()
