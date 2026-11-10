#!/usr/bin/env python3
"""Pick a page template skeleton by matching keywords, and render its component map.

Prints one JSON object. Uses only the Python standard library.

Usage:
    python pick_template.py "admin dashboard with filters"
    python pick_template.py "登录页" --framework vue --library naive-ui
    python pick_template.py --list
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TPL_DIR = os.path.join(os.path.dirname(HERE), "templates")
PAGES_DIR = os.path.join(TPL_DIR, "pages")
MAP_PATH = os.path.join(TPL_DIR, "component-map.json")

# Chinese and English intent words mapped to template ids. Order matters only
# for reporting ties; scoring below decides the winner.
INTENT = {
    "登录": ["login", "login-card", "login-split", "login-sso"],
    "注册": ["login-card"],
    "注册页": ["login-card"],
    "后台": ["dashboard", "dashboard-scorecard", "shell-side-nav", "shell-top-nav"],
    "管理台": ["dashboard", "dashboard-scorecard", "shell-side-nav"],
    "仪表盘": ["dashboard", "dashboard-scorecard", "dashboard-alert-rail"],
    "报表": ["dashboard", "dashboard-scorecard"],
    "监控": ["dashboard-alert-rail", "incident-console"],
    "告警": ["dashboard-alert-rail", "incident-console"],
    "列表": ["table", "table-page", "table-filter", "table-grouped"],
    "表格": ["table", "table-page", "table-filter", "table-grouped"],
    "筛选": ["table-filter", "table-page"],
    "表单": ["form-two-column", "form-wizard", "settings"],
    "设置": ["settings", "settings-sidebar", "settings-dialog"],
    "配置": ["settings", "settings-sidebar"],
    "详情": ["detail-page", "product-detail", "work-item-detail"],
    "商品": ["product-detail", "product-gallery"],
    "产品": ["product-detail", "product-gallery"],
    "画廊": ["classic-gallery", "mixed-gallery", "side-gallery", "gallery-hero"],
    "首页": ["centered-hero", "gallery-hero", "ai-chat-landing"],
    "落地页": ["centered-hero", "gallery-hero"],
    "聊天": ["ai-chat", "messaging-shell"],
    "对话": ["ai-chat", "messaging-shell"],
    "ai": ["ai-chat", "ai-chat-landing"],
    "文档": ["documentation", "documentation-design", "documentation-technical"],
    "看板": ["kanban-board"],
    "任务": ["kanban-board", "work-item-detail"],
    "结算": ["checkout-wizard", "payment-form"],
    "支付": ["payment-form", "checkout-wizard"],
    "订单": ["detail-page", "table-page"],
    "步骤": ["form-wizard", "checkout-wizard", "form-wizard-vertical"],
    "编辑": ["editor", "canvas-editor"],
    "文件": ["file-explorer"],
    "通知": ["table-inbox"],
    "收件": ["table-inbox"],
    "dashboard": ["dashboard", "dashboard-scorecard", "dashboard-comparison"],
    "admin": ["dashboard", "dashboard-scorecard", "shell-side-nav"],
    "login": ["login", "login-card", "login-split", "login-sso"],
    "table": ["table", "table-page", "table-filter"],
    "form": ["form-two-column", "form-wizard", "settings"],
    "gallery": ["classic-gallery", "mixed-gallery", "side-gallery"],
    "chat": ["ai-chat", "messaging-shell"],
    "settings": ["settings", "settings-sidebar", "settings-dialog"],
    "kanban": ["kanban-board"],
    "checkout": ["checkout-wizard", "payment-form"],
    "docs": ["documentation", "documentation-technical"],
}

# Template id -> what the page is for, in Chinese, for the report.
CATEGORY_ZH = {
    "ai-chat": "AI 对话界面",
    "ai-chat-landing": "AI 对话落地页",
    "dashboard": "分析仪表盘（KPI + 图表 + 表格）",
    "login": "登录页（极简居中）",
    "blank": "空白骨架",
    "canvas-editor": "画布编辑器",
    "library": "卡片网格（可搜索）",
    "centered-hero": "居中大标题落地页",
    "payment-form": "支付表单",
    "checkout-wizard": "分步结算",
    "classic-gallery": "经典画廊",
    "table-collapsible": "可折叠表格",
    "table-comparison": "对比表格",
    "contact-form": "联系表单",
    "dashboard-comparison": "数据对比仪表盘",
    "form-wizard-dialog": "弹窗式分步表单",
    "documentation": "文档目录",
    "documentation-design": "设计文档页",
    "documentation-technical": "技术文档页",
    "dashboard-scorecard": "高管摘要仪表盘",
    "file-explorer": "文件浏览器",
    "table-filter": "可筛选表格",
    "form-wizard": "分步表单",
    "dashboard-cohort-funnel": "漏斗与同期群仪表盘",
    "gallery-hero": "画廊式首页",
    "table-grouped": "分组表格",
    "ide": "代码编辑器布局",
    "table-inbox": "收件箱表格",
    "incident-console": "故障控制台",
    "form-wizard-inline": "行内向导表单",
    "kanban-board": "看板",
    "login-card": "登录卡片",
    "login-split": "左右分栏登录",
    "login-sso": "SSO 登录",
    "messaging-shell": "即时通讯布局",
    "mixed-gallery": "混合画廊",
    "detail-page": "订单详情页",
    "editor": "页面编辑器",
    "dashboard-composition": "投资组合仪表盘",
    "product-detail": "商品详情页",
    "product-gallery": "商品画廊",
    "dashboard-progress": "项目进度仪表盘",
    "table-page": "可搜索表格页",
    "dashboard-alert-rail": "服务监控仪表盘",
    "settings-dialog": "设置弹窗",
    "settings": "设置表单",
    "settings-sidebar": "分栏设置面板",
    "shell-nav": "带导航的应用外壳",
    "side-gallery": "侧栏画廊",
    "shell-side-nav": "侧边导航外壳",
    "table": "简单表格",
    "theme-showcase": "主题展示页",
    "shell-top-nav": "顶部导航外壳",
    "table-tree": "树形表格",
    "form-two-column": "双列表单",
    "form-wizard-vertical": "垂直分步表单",
    "work-item-detail": "工作项详情",
}

LIBRARY_KEY = {
    "naive-ui": "naive-ui",
    "element-plus": "element-plus",
    "mui": "mui",
    "shadcn": "shadcn",
    "html": "html",
}


def load_index():
    pages = {}
    if not os.path.isdir(PAGES_DIR):
        return pages
    for name in sorted(os.listdir(PAGES_DIR)):
        if not name.endswith(".txt"):
            continue
        tid = name[:-4]
        path = os.path.join(PAGES_DIR, name)
        text = open(path, encoding="utf-8").read()
        title = ""
        meta = re.search(r"^# name: (.+)$", text, re.M)
        if meta:
            title = meta.group(1).strip()
        pages[tid] = {
            "id": tid,
            "name": title,
            "zh": CATEGORY_ZH.get(tid, title),
            "path": path,
            "bytes": len(text),
        }
    return pages


def score(query, pages):
    q = query.lower()
    hits = {}
    for word, ids in INTENT.items():
        if word in q:
            for rank, tid in enumerate(ids):
                hits[tid] = hits.get(tid, 0) + (len(ids) - rank)
    # direct id or english name matches win
    for tid, info in pages.items():
        if tid in q:
            hits[tid] = hits.get(tid, 0) + 100
        name = (info["name"] or "").lower()
        if name and name in q:
            hits[tid] = hits.get(tid, 0) + 50
    ranked = sorted(hits.items(), key=lambda kv: (-kv[1], kv[0]))
    return [tid for tid, _ in ranked if tid in pages]


def translate(skeleton, library):
    """Rewrite component tags to target-library names using the map."""
    mp = json.load(open(MAP_PATH, encoding="utf-8"))
    flat = {}
    for cat, items in mp.items():
        if cat.startswith("_"):
            continue
        for comp, targets in items.items():
            flat[comp] = targets.get(library) or targets.get("html")

    # Only layout/primitive tags are rewritten; composite tags stay as roles
    # the agent implements.
    out = skeleton
    for comp, target in flat.items():
        out = re.sub(rf"<{comp}(\s|/|>)", f"[{target}]<{comp}\\1", out)
    return out


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


def main(argv):
    args = argv[1:]
    if not args:
        emit({"ok": False, "error": "missing_query"})
        return 2

    if args[0] == "--list":
        pages = load_index()
        emit({"ok": True, "count": len(pages),
              "templates": [{"id": p["id"], "zh": p["zh"]} for p in pages.values()]})
        return 0

    query = args[0]
    library = "html"
    if "--library" in args:
        raw = args[args.index("--library") + 1]
        library = LIBRARY_KEY.get(raw, "html")

    pages = load_index()
    if not pages:
        emit({"ok": False, "error": "no_templates"})
        return 1

    ranked = score(query, pages)
    if not ranked:
        emit({"ok": False, "error": "no_match", "query": query,
              "hint": "换个说法重试，或用 --list 看全部模板",
              "available": [{"id": p["id"], "zh": p["zh"]} for p in pages.values()]})
        return 0

    top = ranked[0]
    info = pages[top]
    skeleton = open(info["path"], encoding="utf-8").read()
    emit({
        "ok": True,
        "query": query,
        "library": library,
        "chosen": {"id": top, "name": info["name"], "zh": info["zh"]},
        "alternatives": [{"id": t, "zh": pages[t]["zh"]} for t in ranked[1:4]],
        "skeleton": skeleton,
        "translated": translate(skeleton, library),
    })
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
