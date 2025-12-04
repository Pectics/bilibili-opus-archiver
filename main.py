#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import shutil
import sys

from lib.crawler import (
    fetch_all_opus_full,
    fetch_new_opus_incremental,
)
from lib.files import (
    write_full_jsonl,
    append_incremental_jsonl,
    load_existing_opus_ids,
)
from lib.utils import (
    load_config,
    load_env_files,
    build_session,
)

# ====================== default file handling ======================

def get_bundled_path(filename: str) -> str:
    """
    获取打包资源的路径。
    PyInstaller 打包后资源文件在 sys._MEIPASS 目录下，
    普通运行时在脚本所在目录。
    """
    if getattr(sys, 'frozen', False):
        # 打包后的 exe
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    else:
        # 普通 Python 脚本运行
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)


def ensure_default_files() -> None:
    """
    检查当前目录是否存在 config.ini 和 .env 文件，
    如果不存在则从默认模板复制。
    """
    files_to_check = [
        ("config.ini", os.path.join("lib", "defaults", "config.ini.default")),
        (".env", os.path.join("lib", "defaults", ".env.default")),
    ]

    for target_file, default_file in files_to_check:
        if not os.path.exists(target_file):
            default_path = get_bundled_path(default_file)
            if os.path.exists(default_path):
                shutil.copy(default_path, target_file)
                print(f"[INFO] Created default {target_file} from template. Please edit it with your settings and restart the program.")
            else:
                print(f"[WARN] Default template {default_file} not found, skipping.")


def wait_and_exit(code: int = 1) -> None:
    """
    等待用户输入后退出程序。
    用于避免双击 .exe 运行时因错误而闪退。
    """
    print()
    input("按 Enter 键退出程序...")
    sys.exit(code)


# ====================== main ======================

def main():
    # 首先确保默认配置文件存在
    ensure_default_files()

    parser = argparse.ArgumentParser(
        description="Bilibili UP主动态数据爬虫（支持全量/差量更新）"
    )
    parser.add_argument(
        "operation",
        nargs="?",
        default="full",
        help="full: 全量更新; incremental: 差量更新",
    )

    args = parser.parse_args()
    op = args.operation.lower()

    op_map = {
        "full": "full",
        "incremental": "incremental",
        "inc": "incremental",
    }

    if op not in op_map:
        print(f"[ERROR] Unknown operation: {args.operation}")
        print("Use: full or incremental/inc")
        sys.exit(1)

    operation = op_map[op]

    cfg = load_config("config.ini")
    env = load_env_files([".env", ".env.local"])

    # 检查 host_mid 是否已填写
    host_mid = cfg["host_mid"]
    if host_mid is None:
        print("[ERROR] 未填写 UP 主的 mid！")
        print("[INFO] 请在 config.ini 文件中填写 host_mid 参数（UP 主的数字 ID）。")
        print("[INFO] 例如：host_mid = 123456789")
        wait_and_exit(1)

    cookie = env.get("BILI_COOKIE", "").strip()
    ua_override = env.get("BILI_USER_AGENT", "").strip() or None

    session = build_session(cfg, cookie, user_agent_override=ua_override)

    output_path = cfg["output_path"]
    delay = cfg["delay"]
    web_location = cfg["web_location"]

    if operation == "full":
        print("[INFO] Operation: FULL (rewrite output file)")
        items = fetch_all_opus_full(session, host_mid, delay, web_location)
        if not items:
            print("[WARN] No items fetched, nothing to save.")
            return
        write_full_jsonl(items, output_path)
    else:
        print("[INFO] Operation: INCREMENTAL (append new items)")
        existing_ids = load_existing_opus_ids(output_path)
        if not existing_ids:
            print("[INFO] No existing file or no opus_id found, fallback to FULL fetch.")
            items = fetch_all_opus_full(session, host_mid, delay, web_location)
            if not items:
                print("[WARN] No items fetched, nothing to save.")
                return
            write_full_jsonl(items, output_path)
            return

        new_items = fetch_new_opus_incremental(session, host_mid, existing_ids, delay, web_location)
        append_incremental_jsonl(new_items, output_path)


if __name__ == "__main__":
    main()
