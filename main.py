#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
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

# ====================== main ======================

def main():
    parser = argparse.ArgumentParser(
        description="Bilibili UP 主 opus 动态爬虫（config.ini + .env/.env.local，支持全量 / 差量更新）"
    )
    parser.add_argument(
        "operation",
        nargs="?",
        default="full",
        choices=["full", "incremental"],
        help="full: 从头全量爬; incremental: 差量更新",
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

    cookie = env.get("BILI_COOKIE", "").strip()
    ua_override = env.get("BILI_USER_AGENT", "").strip() or None

    session = build_session(cfg, cookie, user_agent_override=ua_override)

    host_mid = cfg["host_mid"]
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
