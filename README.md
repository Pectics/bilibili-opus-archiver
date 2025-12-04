<div align="center">

# 📦 bilibili-opus-archiver

**一个用于爬取和归档B站UP主动态数据的轻量级命令行工具。**  
支持全量爬取、增量更新、本地数据持久化，适合作为个人存档或数据分析的基础。

</div>

## ✨ 功能特性

- 🧲 **全量爬取**：从最早到最新获取所有动态
- 🔄 **差量更新**：只追加新增动态，避免重复爬取
- 🔐 **支持登录**：`.env` 可注入 Cookie，可访问充电专属动态
- 🧹 **字段清洗**：`badge` 字段放到 JSON 对象末尾，便于阅读
- 🗃️ **标准存储**：数据保存为 `.jsonl`，按 **时间从早到晚** 排序
- 📦 **自动配置**：首次运行时自动生成默认配置文件

## 📁 项目结构

```
bilibili-opus-archiver/
├─ lib/
|  ├─ defaults/
|  |  ├─ config.ini.default  # 通用配置模板
|  |  └─ .env.default        # 环境变量配置模板
|  ├─ crawler.py    # 封装所有网络请求 & 翻页逻辑
|  ├─ files.py      # 读写 jsonl、增量追加、字段清洗
|  └─ utils.py      # 通用工具：env 加载、cookie 解析、参数处理
├─ .env             # 环境变量配置（首次运行自动生成）
├─ config.ini       # 通用配置（首次运行自动生成）
└─ main.py          # 主入口：full / incremental(inc) 两种模式
```

## ⚙️ 安装依赖

```bash
pip install -r requirements.txt
```

或直接运行

```bash
pip install requests
```

## 🔧 配置说明

### 1. `config.ini`（通用配置）

```ini
[common]
host_mid = 1199517996 ; UP主的mid
output_path = 1199517996_opus.jsonl ; 输出jsonl文件名

[http]
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...Edg/142.0.0.0" ; 默认UA
accept_language = "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
origin = https://space.bilibili.com
referer = https://space.bilibili.com/1199517996/upload/opus

[fetch]
delay = 0.3 ; 每页请求间隔（秒）
web_location = 333.1387 ; 与浏览器参数保持一致即可
```

### 2. `.env`（敏感配置）

```bash
BILI_COOKIE="buvid_fp_plain=...; SESSDATA=...; bili_jct=...; ..."
BILI_USER_AGENT=    # 可选：填写后将覆盖 config.ini 中的 UA
```

你可以用浏览器 DevTools → Network → Request Headers 中的 Cookie。

> **💡 提示**：使用预编译的 exe 版本时，首次运行会自动在当前目录生成 `config.ini` 和 `.env` 配置文件，无需手动创建。

## 🚀 使用方式

### 📦 全量爬取（重写 jsonl）

```bash
python main.py full
```

效果：

* 覆盖原文件
* 从最早到最新保存所有动态

### 🔄 差量更新（追加最新动态）

```bash
python main.py incremental
# 或
python main.py inc
```

效果：

* 读取已有 jsonl 的所有 opus_id
* 从最新往下抓
* 一直抓到“遇到已存在的 opus_id”停止
* 按时间顺序追加到文件末尾

## 🧪 输出格式（jsonl）

每行一个动态对象：

```json
{"opus_id":"114514...","content":"blabla","jump_url":"...","stat":{"like":42},"badge":{"text":"充电专属"}}
```

* 使用紧凑 JSON（`","`、`":"` 无空格）
* 字段顺序经过清洗，确保 `badge` 在最后
* 整个文件按时间从**早 → 晚**排序

## 💡 一些可扩展想法

你可以轻松基于这个脚手架实现：

* 导出 Markdown / CSV / HTML
* 按时间区间过滤动态
* 检测重复内容、分析发布频率
* 做一个「UP 主动态时间线」网页
* 日志监控、自动备份、定时任务 crontab

## 🧑‍💻 开发者说

你可以通过以下方式快速定位模块：

| 模块 | 作用 |
| --- | --- |
| `lib/crawler.py`  | 所有 API 请求、翻页逻辑、差量检测 |
| `lib/files.py`    | 文件读写、jsonl 排序、badge 清洗 |
| `lib/utils.py`    | env 加载、cookie 解析、参数映射 |
| `main.py`         | CLI 入口，处理 full/inc 逻辑 |

如果你要扩展 CLI，可以在主程序里继续加命令，或者使用 `argparse` 子命令模式。

## 🏁 License

本项目采用 MIT 许可证，详情见 [LICENSE](LICENSE) 文件。
