#!/usr/bin/env python3
"""Query the bundled design-style snapshot (143 styles from luckymaomi/ui).

Offline: reads templates/styles.json.gz, no network. Uses only the Python
standard library.

Usage:
    python search_style.py "拟物 按钮"                 # keyword search
    python search_style.py --slug skeuomorphism        # full entry by slug
    python search_style.py --list                      # all slugs + names

Output: UTF-8 JSON on stdout (GBK-console safe).
"""

import argparse
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT = os.path.join(os.path.dirname(HERE), "templates", "styles.json.gz")

_sc = None


def load_styles():
    global _sc
    if _sc is None:
        with gzip.open(SNAPSHOT, "rt", encoding="utf-8") as fh:
            _sc = json.load(fh)
    return _sc


def emit(payload):
    data = json.dumps(payload, indent=2, ensure_ascii=False)
    stream = getattr(sys.stdout, "buffer", None)
    if stream is not None:
        sys.stdout.flush()
        stream.write(data.encode("utf-8"))
        stream.write(b"\n")
        stream.flush()
    else:
        print(data)


def score(style, terms):
    """Higher is better. Name/slug matches weigh most, then keywords/tags."""
    hay_name = (style.get("name", "") + " " + style.get("nameEn", "")).lower()
    hay_slug = style.get("slug", "").lower()
    hay_kw = " ".join(style.get("keywords") or []).lower()
    hay_kw += " " + " ".join(style.get("keywordsEn") or []).lower()
    hay_tags = " ".join(style.get("tags") or []).lower()
    hay_desc = (style.get("description") or "").lower()
    hay_cat = (style.get("category") or "").lower()

    total = 0
    for t in terms:
        s = 0
        if t in hay_slug:
            s += 40
        if t in hay_name:
            s += 30
        if t in hay_tags:
            s += 12
        if t in hay_kw:
            s += 8
        if t in hay_desc:
            s += 3
        if t in hay_cat:
            s += 6
        total += s
    return total


def cmd_search(query, limit):
    styles = load_styles()
    q = query.lower()
    # split on spaces; also try the whole phrase for CJK queries
    terms = [t for t in re.split(r"[\s,，]+", q) if t]
    scored = []
    for s in styles:
        sc = score(s, terms)
        if sc > 0:
            scored.append((sc, s))
    scored.sort(key=lambda x: (-x[0], x[1].get("slug", "")))
    hits = scored[:limit]
    emit({
        "ok": True,
        "query": query,
        "found": len(hits),
        "results": [
            {
                "slug": s.get("slug"),
                "name": s.get("name"),
                "nameEn": s.get("nameEn"),
                "category": s.get("category"),
                "description": s.get("description"),
                "colors": s.get("colors"),
                "score": sc,
                "hint": f'python "{os.path.abspath(__file__)}" --slug {s.get("slug")} 查看完整规则与组件配方',
            }
            for sc, s in hits
        ],
    })


def cmd_slug(slug):
    styles = load_styles()
    for s in styles:
        if s.get("slug") == slug:
            emit({"ok": True, "style": s})
            return 0
    emit({"ok": False, "error": "not_found", "slug": slug,
          "hint": "用 --list 查看全部可用 slug"})
    return 1


def cmd_list():
    styles = load_styles()
    emit({
        "ok": True,
        "count": len(styles),
        "styles": [
            {"slug": s.get("slug"), "name": s.get("name"), "nameEn": s.get("nameEn"),
             "category": s.get("category")}
            for s in styles
        ],
    })


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", help="关键词（中文或英文）")
    ap.add_argument("--slug", help="按 slug 取完整条目")
    ap.add_argument("--list", action="store_true", help="列出全部风格")
    ap.add_argument("--limit", type=int, default=5)
    try:
        args = ap.parse_args(argv[1:])
    except SystemExit:
        return 2

    if not os.path.isfile(SNAPSHOT):
        emit({"ok": False, "error": "snapshot_missing", "path": SNAPSHOT})
        return 1

    if args.list:
        cmd_list()
        return 0
    if args.slug:
        return cmd_slug(args.slug)
    if args.query:
        cmd_search(args.query, args.limit)
        return 0
    emit({"ok": False, "error": "missing_query",
          "usage": 'search_style.py "关键词" | --slug <id> | --list'})
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
