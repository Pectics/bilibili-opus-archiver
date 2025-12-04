#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, Any, List

# ====================== 写文件 ======================

def move_badge_to_end(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    把 badge 字段挪到最后，别挡视线。
    """
    if "badge" not in obj:
        return obj
    reordered = {k: v for k, v in obj.items() if k != "badge"}
    reordered["badge"] = obj["badge"]
    return reordered


def write_full_jsonl(items: List[Dict[str, Any]], output_path: str) -> None:
    """
    全量重写 jsonl，按时间从早到晚（最早在前）。
    """
    items_earliest_first = list(reversed(items))

    with open(output_path, "w", encoding="utf-8") as f:
        for item in items_earliest_first:
            item = move_badge_to_end(item)
            line = json.dumps(item, ensure_ascii=False, separators=(",", ":"))
            f.write(line + "\n")

    print(f"[INFO] [FULL] Saved {len(items_earliest_first)} items to {output_path}")


def append_incremental_jsonl(new_items: List[Dict[str, Any]], output_path: str) -> None:
    """
    差量追加到已有 jsonl 末尾：
    - 旧文件已经是“早 -> 晚”
    - new_items 是“新 -> 旧”，所以要反转成“旧 -> 新”再 append
    """
    if not new_items:
        print("[INFO] No new items to append.")
        return

    items_earliest_first = list(reversed(new_items))

    with open(output_path, "a", encoding="utf-8") as f:
        for item in items_earliest_first:
            item = move_badge_to_end(item)
            line = json.dumps(item, ensure_ascii=False, separators=(",", ":"))
            f.write(line + "\n")

    print(f"[INFO] [INCR] Appended {len(items_earliest_first)} new items to {output_path}")


def load_existing_opus_ids(output_path: str) -> set:
    existing_ids = set()
    if not os.path.exists(output_path):
        return existing_ids

    count = 0
    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            if isinstance(obj, dict):
                opus_id = obj.get("opus_id")
                if opus_id:
                    existing_ids.add(opus_id)
                    count += 1

    print(f"[INFO] Loaded {count} existing opus_ids from {output_path}")
    return existing_ids
