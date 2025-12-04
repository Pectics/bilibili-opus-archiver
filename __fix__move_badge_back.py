#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__fix__move_badge_back.py

对已经爬好的 jsonl 做修改：
- 如果某行 JSON 对象中存在 "badge" 字段，则把它挪到最后。
- 其它字段顺序保持不变。
"""

import json
import sys
from typing import Dict, Any

def move_badge_to_end(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    返回一个新的 dict：
    - 保留原字段顺序
    - 如果存在 'badge' 字段，则将其挪到最后
    """
    if "badge" not in obj:
        return obj

    # 复制一份（不带 badge）
    reordered = {k: v for k, v in obj.items() if k != "badge"}
    # 最后加上 badge
    reordered["badge"] = obj["badge"]
    return reordered


def process_file(input_path: str, output_path: str) -> None:
    count_total = 0
    count_badge = 0

    with open(input_path, "r", encoding="utf-8") as fin, \
            open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue

            count_total += 1

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # 如果这一行不是 JSON，就原样写回（理论上不会发生）
                fout.write(line + "\n")
                continue

            if isinstance(obj, dict) and "badge" in obj:
                obj = move_badge_to_end(obj)
                count_badge += 1

            # 紧凑 JSON 输出
            out_line = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
            fout.write(out_line + "\n")

    print(f"[INFO] Done. total_lines={count_total}, lines_with_badge={count_badge}")
    print(f"[INFO] Output written to: {output_path}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python hotfix.py input.jsonl output.jsonl")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    process_file(input_path, output_path)


if __name__ == "__main__":
    main()
