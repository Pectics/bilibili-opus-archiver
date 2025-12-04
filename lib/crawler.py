#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
from typing import Dict, Any, List

import requests

# ====================== 抓取逻辑 ======================

BASE_URL = "https://api.bilibili.com/x/polymer/web-dynamic/v1/opus/feed/space"

def fetch_all_opus_full(
    session: requests.Session,
    host_mid: int,
    delay: float,
    web_location: str,
) -> List[Dict[str, Any]]:
    """
    全量爬取：从第一条到最新所有动态。
    返回 items 列表，默认顺序为接口原始顺序（通常是“新 -> 旧”）。
    """
    all_items: List[Dict[str, Any]] = []

    params = {
        "host_mid": host_mid,
        "type": "all",
        "page": 1,
        "web_location": web_location,
    }

    page = 1
    while True:
        params["page"] = page
        print(f"[INFO] [FULL] Fetching page {page} with params={params} ...")
        resp = session.get(BASE_URL, params=params, timeout=10)

        if resp.status_code != 200:
            print(f"[ERROR] HTTP {resp.status_code}: {resp.text[:200]}")
            break

        try:
            data = resp.json()
        except json.JSONDecodeError:
            print("[ERROR] Failed to decode JSON.")
            break

        if data.get("code") != 0:
            print(f"[ERROR] API error code={data.get('code')}, message={data.get('message')}")
            break

        d = data.get("data") or {}
        items = d.get("items") or []
        if not items:
            print("[INFO] No items in this page, stop.")
            break

        all_items.extend(items)
        print(f"[INFO] Got {len(items)} items, total={len(all_items)}")

        has_more = d.get("has_more")
        if not has_more:
            print("[INFO] has_more = False, finished full fetch.")
            break

        last_opus_id = items[-1].get("opus_id")
        if not last_opus_id:
            print("[WARN] last item has no opus_id, stop.")
            break

        params["offset"] = last_opus_id
        page += 1
        time.sleep(delay)

    return all_items


def fetch_new_opus_incremental(
    session: requests.Session,
    host_mid: int,
    existing_ids: set,
    delay: float,
    web_location: str,
) -> List[Dict[str, Any]]:
    """
    差量更新：从最新往下爬，直到遇见已有的 opus_id 为止。
    返回“新增的 items”列表，顺序为接口原始顺序（“新 -> 旧”）。
    """
    new_items: List[Dict[str, Any]] = []

    params = {
        "host_mid": host_mid,
        "type": "all",
        "page": 1,
        "web_location": web_location,
    }

    page = 1
    stop = False

    while True:
        params["page"] = page
        print(f"[INFO] [INCR] Fetching page {page} with params={params} ...")
        resp = session.get(BASE_URL, params=params, timeout=10)

        if resp.status_code != 200:
            print(f"[ERROR] HTTP {resp.status_code}: {resp.text[:200]}")
            break

        try:
            data = resp.json()
        except json.JSONDecodeError:
            print("[ERROR] Failed to decode JSON.")
            break

        if data.get("code") != 0:
            print(f"[ERROR] API error code={data.get('code')}, message={data.get('message')}")
            break

        d = data.get("data") or {}
        items = d.get("items") or []
        if not items:
            print("[INFO] No items in this page, stop.")
            break

        for item in items:
            opus_id = item.get("opus_id")
            if opus_id and opus_id in existing_ids:
                print(f"[INFO] Found existing opus_id={opus_id}, stop incremental fetch.")
                stop = True
                break
            new_items.append(item)

        print(f"[INFO] Got {len(items)} items, new_items_total={len(new_items)}")

        if stop:
            break

        has_more = d.get("has_more")
        if not has_more:
            print("[INFO] has_more = False, finished incremental fetch.")
            break

        last_opus_id = items[-1].get("opus_id")
        if not last_opus_id:
            print("[WARN] last item has no opus_id, stop.")
            break

        params["offset"] = last_opus_id
        page += 1
        time.sleep(delay)

    return new_items
