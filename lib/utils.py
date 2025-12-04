#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import os
import sys
from typing import Dict, Any, List

import requests

# ====================== 工具函数 ======================

def parse_cookie_string(cookie_str: str) -> Dict[str, str]:
    cookies: Dict[str, str] = {}
    for part in cookie_str.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        cookies[k.strip()] = v.strip()
    return cookies


def load_env_files(paths: List[str]) -> Dict[str, str]:
    """
    读取一组 .env 文件，后面的覆盖前面的：
    - 支持格式：KEY=VALUE
    - 忽略空行和以 # 开头的行
    - 自动去掉成对的引号
    """
    env: Dict[str, str] = {}
    for path in paths:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                # strip quotes if present
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                env[key] = val
    return env


def load_config(path: str = "config.ini") -> Dict[str, Any]:
    if not os.path.exists(path):
        print(f"[ERROR] config file not found: {path}")
        sys.exit(1)

    # 关掉 % 插值，开启行内注释
    cfg = configparser.ConfigParser(
        interpolation=None,
        inline_comment_prefixes=("#", ";")
    )
    cfg.read(path, encoding="utf-8")

    try:
        # host_mid 可能为空，需要特殊处理
        host_mid_str = cfg.get("common", "host_mid", fallback="").strip()
        host_mid = int(host_mid_str) if host_mid_str else None

        output_path = cfg.get("common", "output_path")

        user_agent = cfg.get("http", "user_agent")
        accept_language = cfg.get("http", "accept_language", fallback="zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7")
        origin = cfg.get("http", "origin", fallback="https://space.bilibili.com")
        # 如果 host_mid 为空，referer 使用默认值
        default_referer = f"https://space.bilibili.com/{host_mid}/upload/opus" if host_mid else "https://space.bilibili.com"
        referer = cfg.get("http", "referer", fallback=default_referer)

        delay = cfg.getfloat("fetch", "delay", fallback=0.3)
        web_location = cfg.get("fetch", "web_location", fallback="333.1387")
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        print(f"[ERROR] config format error: {e}")
        sys.exit(1)
    except ValueError:
        # host_mid 不是有效的整数
        host_mid = None
        output_path = cfg.get("common", "output_path")
        user_agent = cfg.get("http", "user_agent")
        accept_language = cfg.get("http", "accept_language", fallback="zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7")
        origin = cfg.get("http", "origin", fallback="https://space.bilibili.com")
        referer = cfg.get("http", "referer", fallback="https://space.bilibili.com")
        delay = cfg.getfloat("fetch", "delay", fallback=0.3)
        web_location = cfg.get("fetch", "web_location", fallback="333.1387")

    return {
        "host_mid": host_mid,
        "output_path": output_path,
        "user_agent": user_agent,
        "accept_language": accept_language,
        "origin": origin,
        "referer": referer,
        "delay": delay,
        "web_location": web_location,
    }


def build_session(cfg: Dict[str, Any], cookie_str: str, user_agent_override: str | None = None) -> requests.Session:
    ua = user_agent_override or cfg["user_agent"]

    session = requests.Session()
    session.headers.update({
        "User-Agent": ua,
        "Accept": "*/*",
        "Accept-Language": cfg["accept_language"],
        "Origin": cfg["origin"],
        "Referer": cfg["referer"],
    })

    cookie_str = cookie_str.strip()
    if cookie_str:
        cookies = parse_cookie_string(cookie_str)
        if not cookies:
            print("[WARN] Cookie string provided but parsing resulted in empty dict.")
        session.cookies.update(cookies)
    else:
        print("[WARN] No cookie provided. Some content may be hidden (e.g., charge-only posts).")

    return session
