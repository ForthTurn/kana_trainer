# JMdict 词典管理

## 概述

JMdict是一个日语词典项目，提供完整的日语词汇数据，包括汉字、假名、词性、含义、例句等信息。本项目支持两种数据格式：

1. **JSON格式**: 原始数据格式，适合小规模使用
2. **SQLite数据库**: 优化后的数据库格式，适合大规模查询和长期使用

## 主要功能

### 1. 词典更新 (`load_jmdict.py`)
- 自动从GitHub获取最新版本的JMdict数据
- 支持代理设置
- 自动下载、解压和更新词典文件
- 显示详细的更新进度和状态信息

### 2. 数据迁移 (`migrate_to_sqlite.py`)
- 将JSON数据迁移到SQLite数据库
- 自动创建数据库表结构和索引
- 支持错误处理和进度显示
- 优化查询性能

### 3. 数据库管理 (`sqlite_manager.py`)
- 提供完整的数据库查询接口
- 支持多种查询方式：
  - 按假名查找词汇
  - 按汉字搜索
  - 按英文含义搜索
  - 获取常用词汇
- 包含数据库统计功能
- 友好的结果显示格式

## 文件结构

```
JMdict/
├── JMdict.json          # 词典数据文件
├── load_jmdict.py       # 词典更新脚本
├── migrate_to_sqlite.py # 数据迁移脚本
├── sqlite_manager.py    # SQLite数据库管理器
├── schema.py            # 数据模式定义
├── command.py           # 命令行工具
├── __init__.py          # 包初始化文件
├── README.md            # 本文档
└── .gitignore           # Git忽略文件配置


```

## 数据库表结构

### words 表
- `id`: 词汇ID（主键）
- `kanji`: 汉字表示（多个用逗号分隔）
- `kana`: 假名表示（多个用逗号分隔）
- `common`: 是否为常用词

### senses 表
- `id`: 自增ID（主键）
- `word_id`: 关联到words表的外键
- `part_of_speech`: 词性
- `related`: 相关词
- `antonym`: 反义词
- `field`: 领域
- `dialect`: 方言
- `misc`: 其他信息
- `info`: 附加信息
- `language_source`: 语言来源
- `gloss`: 释义

### examples 表
- `id`: 自增ID（主键）
- `word_id`: 关联到words表的外键
- `sense_index`: 意义索引
- `example_text`: 示例句子

## 使用方法

### 1. 通过主菜单使用功能
在主菜单中可以选择：
- **📖 查词功能**: 查询日语词汇（需要先更新词典并迁移到数据库）
- **🔄 更新词典**: 更新JMdict.json文件并迁移到数据库

### 2. 查词功能使用
查词功能提供以下查询方式：
- **按假名查询**: 输入假名查找包含该假名的词汇
- **按汉字查询**: 输入汉字查找包含该汉字的词汇  
- **按英文含义查询**: 输入英文含义查找相关词汇
- **查看常用词汇**: 浏览常用词汇列表

### 3. 手动更新词典
```bash
cd JMdict
python load_jmdict.py
```

### 4. 手动迁移到数据库
```bash
python migrate_to_sqlite.py
```

### 5. 使用数据库查询
```python
from JMdict.sqlite_manager import JMdictSQLiteManager

manager = JMdictSQLiteManager("jmdict.db")
if manager.connect():
    try:
        # 查找包含假名"あ"的词汇
        words = manager.find_words_with_kana("あ", max_results=5)
        
        # 根据汉字搜索
        words = manager.search_by_kanji("明", max_results=5)
        
        # 根据英文含义搜索
        words = manager.search_by_meaning("hello", max_results=5)
        
        # 获取常用词汇
        common_words = manager.get_common_words(max_results=10)
        
    finally:
        manager.disconnect()
```

## 主要特性

### 性能优化
- 使用SQLite索引提高查询速度
- 支持批量查询
- 内存使用优化（不再需要加载整个JSON文件）

### 功能完整性
- 保持了与原始JSON数据结构的一致性
- 支持所有主要字段的查询
- 提供了灵活的查询接口

### 易用性
- 简单的API接口
- 详细的错误处理和日志
- 丰富的示例代码

## 配置说明

### 代理设置
在`config.py`中配置代理服务器：
```python
PROXY = "http://your-proxy-server:port"
```

### 临时目录
设置临时文件存储目录：
```python
TEMP_DIR = "/path/to/temp/directory"
```

## 注意事项

1. 首次迁移需要时间，取决于JSON文件大小
2. 需要确保有足够的磁盘空间
3. 迁移完成后可以删除原始JSON文件以节省空间
4. 建议定期更新词典数据以获取最新内容

## 故障排除

### 常见问题

1. **词典更新失败**
   - 检查网络连接和代理设置
   - 确认GitHub API访问权限

2. **数据库连接失败**
   - 检查文件路径是否正确
   - 确保有写入权限

3. **迁移过程中断**
   - 删除数据库文件重新开始
   - 检查JSON文件是否完整

4. **查询结果为空**
   - 确认数据库已成功迁移
   - 检查查询条件是否正确

### 日志和调试

所有脚本都会显示详细的进度信息和错误信息，帮助诊断问题。

## 未来改进

1. 添加使用频率统计功能
2. 支持更复杂的查询条件
3. 添加数据备份和恢复功能
4. 优化查询性能
5. 添加缓存机制
6. 支持更多数据格式

## 总结

JMdict项目提供了完整的日语词典解决方案，从数据获取、更新到高效查询，支持多种使用场景。通过SQLite数据库的引入，显著提升了查询性能和内存效率，为后续功能扩展奠定了良好基础。
