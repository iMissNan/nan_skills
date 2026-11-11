#!/usr/bin/env python3
"""Refresh the bundled page-template skeletons from the astryx CLI.

Dry-run by default: it reports what would change and writes nothing. Pass
--write to apply. This is the only script in the skill that touches the
network, and only when you run it.

Usage:
    python update_templates.py                  # dry-run against the latest CLI
    python update_templates.py --write          # apply
    python update_templates.py --version 0.7.11 # pin an exact release
    python update_templates.py --check          # only report version drift

Exit codes:
    0  success (including "no changes")
    1  the astryx CLI could not be resolved or failed
    2  bad arguments
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
TPL_DIR = os.path.join(SKILL_DIR, "templates")
PAGES_DIR = os.path.join(TPL_DIR, "pages")
SNAPSHOT = os.path.join(TPL_DIR, "snapshot.json")
INDEX = os.path.join(TPL_DIR, "INDEX.md")
PACKAGE = "@astryxdesign/cli"


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


def load_snapshot():
    if not os.path.isfile(SNAPSHOT):
        return {}
    with open(SNAPSHOT, encoding="utf-8") as fh:
        return json.load(fh)


def aggregate_hash(pages_dir):
    """Stable hash over the page skeletons, used to detect template drift."""
    h = hashlib.sha256()
    for name in sorted(os.listdir(pages_dir)):
        if not name.endswith(".txt"):
            continue
        h.update(name.encode())
        with open(os.path.join(pages_dir, name), "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()


def _cached_versions(cache_root):
    """Map every cached astryx launcher to the CLI version it actually ships."""
    entries = []
    for entry in sorted(os.listdir(cache_root)):
        pkg = os.path.join(cache_root, entry, "node_modules", "@astryxdesign", "cli", "package.json")
        if not os.path.isfile(pkg):
            continue
        for name in ("astryx.cmd", "astryx"):
            launcher = os.path.join(cache_root, entry, "node_modules", ".bin", name)
            if os.path.isfile(launcher):
                try:
                    with open(pkg, encoding="utf-8") as fh:
                        version = json.load(fh).get("version")
                except (OSError, json.JSONDecodeError):
                    version = None
                entries.append((version or "0.0.0", launcher))
                break
    # Newest cache first; an unparseable version sorts last.
    entries.sort(key=lambda item: item[0], reverse=True)
    return entries


def resolve_cli(pinned_version=None):
    """Return a command list that runs the astryx CLI, or raise RuntimeError.

    A pinned version must match the cached copy exactly, otherwise a stale npx
    cache would silently stand in for the version the caller asked for.
    """
    spec = PACKAGE if not pinned_version else f"{PACKAGE}@{pinned_version}"

    # Prefer a locally cached npx copy: it avoids re-resolving the package on
    # every template and works with no global install. The cache root differs
    # per platform, and npm honours an explicit cache override.
    home = os.path.expanduser("~")
    cache_roots = []
    override = os.environ.get("npm_config_cache")
    if override:
        cache_roots.append(os.path.join(override, "_npx"))
    if os.name == "nt":
        cache_roots.append(os.path.join(home, "AppData", "Local", "npm-cache", "_npx"))
    else:
        cache_roots.append(os.path.join(home, ".npm", "_npx"))

    for cache_root in cache_roots:
        if not os.path.isdir(cache_root):
            continue
        for version, launcher in _cached_versions(cache_root):
            if pinned_version and version != pinned_version:
                continue
            return [launcher], f"npx-cache ({version})"

    # Fall back to npx, which downloads on first use.
    npx = shutil.which("npx")
    if npx:
        return [npx, "--yes", spec], "npx"

    raise RuntimeError(
        "找不到 astryx CLI。请先安装 Node.js，或执行 npm i -g @astryxdesign/cli。"
    )


def run_cli(cmd, args):
    result = subprocess.run(cmd + args, capture_output=True)
    out = (result.stdout or b"").decode("utf-8", "replace")
    err = (result.stderr or b"").decode("utf-8", "replace")
    return result.returncode, out, err


def strip_banner(text):
    keep = []
    for line in text.splitlines():
        if line.startswith("astryx: answered by") or line.startswith("package:"):
            continue
        keep.append(line)
    return "\n".join(keep).strip()


def fetch_listing(cmd):
    rc, out, err = run_cli(cmd, ["template", "--list", "--json"])
    if rc != 0:
        raise RuntimeError(f"template --list 失败: {(err or out)[:400]}")
    start = out.find("{")
    if start < 0:
        raise RuntimeError("template --list 未返回 JSON")
    try:
        return json.loads(out[start:])
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"template --list JSON 解析失败: {exc}")


def cli_version(cmd):
    rc, out, err = run_cli(cmd, ["--version"])
    if rc != 0:
        return None
    for line in (out or "").splitlines():
        line = line.strip()
        if line and line[0].isdigit():
            return line
    return None


def published_version():
    """Ask the npm registry for the newest published CLI version.

    `--check` must compare the snapshot against what is actually released.
    Reading the version off the resolved binary only reports which cached copy
    npx happened to pick, which can never show drift.

    The URL is assembled from two module constants and then checked against the
    allowlisted origin, so no caller can redirect this request elsewhere.
    """
    import urllib.error
    import urllib.parse
    import urllib.request

    url = urllib.parse.urljoin(REGISTRY_ORIGIN, CLI_LATEST_PATH)
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "registry.npmjs.org":
        raise RuntimeError(f"拒绝向非预期主机发起请求: {url!r}")

    try:
        with urllib.request.urlopen(url, timeout=10) as fh:
            return json.load(fh).get("version")
    except (urllib.error.URLError, OSError, json.JSONDecodeError, AttributeError):
        return None


def fetch_page_ids(cmd):
    data = fetch_listing(cmd)
    entries = data.get("data", [])
    return (
        [t for t in entries if t.get("type") == "page"],
        [t for t in entries if t.get("type") == "block"],
    )


def render(entry, text):
    header = (
        f"# template: {entry['id']}\n"
        f"# name: {entry.get('name', '')}\n"
        f"# description: {entry.get('description', '')}\n\n"
    )
    return header + text + "\n"


# Template ids come from the CLI's JSON listing, i.e. from an external process.
# They are used as filenames, so only a plain slug is accepted; anything with a
# separator, a drive letter or a parent segment is rejected before it reaches
# the filesystem.
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
INDEX_NAME = "INDEX.md"

# The only network endpoint this skill ever contacts. It is a fixed constant —
# no part of it is composed from input — and the response is read for a version
# string only.
REGISTRY_ORIGIN = "https://registry.npmjs.org"
CLI_LATEST_PATH = "/@astryxdesign%2Fcli/latest"


def safe_template_path(out_dir, template_id):
    """Join a template id onto out_dir, refusing ids that could escape it.

    The id comes from the CLI's JSON listing, i.e. from an external process, so
    it is treated as untrusted: only a plain slug is accepted, the result is
    normalized, and it must stay inside out_dir.
    """
    if not isinstance(template_id, str) or not SAFE_ID.match(template_id):
        raise RuntimeError(f"拒绝写入可疑的模板 id: {template_id!r}")
    if template_id in (".", "..") or ".." in template_id:
        raise RuntimeError(f"拒绝写入可疑的模板 id: {template_id!r}")
    if os.path.basename(template_id) != template_id:
        raise RuntimeError(f"拒绝写入可疑的模板 id: {template_id!r}")

    root = os.path.realpath(out_dir)
    path = os.path.realpath(os.path.join(root, template_id + ".txt"))
    if os.path.commonpath([path, root]) != root:
        raise RuntimeError(f"模板 id 越出输出目录: {template_id!r}")
    return path


def write_template_file(out_dir, template_id, payload):
    """Validate, then write. Kept as one unit so the check cannot be skipped."""
    path = safe_template_path(out_dir, template_id)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload)
    return path


def write_index(pages, blocks, out_dir, cli_version=None):
    """Regenerate templates/INDEX.md from the live CLI listing."""
    ver = f" {cli_version}" if cli_version else ""
    lines = ["# 页面模板索引", "",
             f"来源：astryx design system{ver} 的 `template --skeleton` 输出。",
             "骨架保留布局结构与间距数值（`padding`、`gap`、`columns`），"
             "**属性仍是 JSX 写法**（如 `padding={6}`），需按目标框架改写语法。",
             "上游最多输出 35 行，超出部分以 `...` 省略，须按 description 自行补全。", "",
             f"共 {len(pages)} 个页面模板，{len(blocks)} 个区块模板。", "",
             "> 更新：`python scripts/update_templates.py --write`。"
             "本文件与 `snapshot.json` 由该脚本重新生成。", "",
             "## 页面模板", "",
             "| id | 名称 | 适用场景 |", "|---|---|---|"]
    for t in pages:
        desc = (t.get("description") or "").replace("|", "/")
        lines.append(f"| `{t['id']}` | {t.get('name', '')} | {desc} |")

    if blocks:
        lines += ["", f"## 区块模板（前 60 个，共 {len(blocks)} 个，全量见 astryx CLI）", "",
                  "| id | 名称 |", "|---|---|"]
        for t in blocks[:60]:
            lines.append(f"| `{t['id']}` | {t.get('name', '')} |")

    write_index_text(out_dir, "\n".join(lines) + "\n")


def write_index_text(out_dir, text):
    """Write INDEX.md inside out_dir, validating the resolved path first."""
    root = os.path.realpath(out_dir)
    path = os.path.realpath(os.path.join(root, INDEX_NAME))
    if os.path.commonpath([path, root]) != root:
        raise RuntimeError(f"INDEX 越出输出目录: {path!r}")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def write_snapshot_text(snapshot_path, text):
    """Write snapshot.json, validating the resolved path against its parent."""
    root = os.path.realpath(os.path.dirname(snapshot_path))
    path = os.path.realpath(snapshot_path)
    if os.path.commonpath([path, root]) != root:
        raise RuntimeError(f"snapshot 路径异常: {path!r}")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def extract(cmd, pages, out_dir):
    written, failed = 0, []
    for entry in pages:
        rc, out, err = run_cli(cmd, ["template", entry["id"], "--skeleton"])
        text = strip_banner(out)
        if rc != 0 or not text:
            failed.append({"id": entry["id"], "error": (err or out)[:200]})
            continue
        write_template_file(out_dir, entry["id"], render(entry, text))
        written += 1
    return written, failed


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--write", action="store_true", help="apply changes (default: dry-run)")
    ap.add_argument("--check", action="store_true", help="only report version drift")
    ap.add_argument("--version", dest="pinned", default=None, help="pin an exact CLI release")
    ap.add_argument("--verbose", action="store_true")
    try:
        args = ap.parse_args(argv[1:])
    except SystemExit:
        return 2

    current = load_snapshot()
    cur_ver = current.get("snapshot", {}).get("cli_version")
    cur_hash = current.get("snapshot", {}).get("aggregate_sha256")
    local_hash = aggregate_hash(PAGES_DIR) if os.path.isdir(PAGES_DIR) else None

    try:
        cmd, source = resolve_cli(args.pinned)
        latest = cli_version(cmd)
        pages, blocks = fetch_page_ids(cmd)
    except RuntimeError as exc:
        emit({"ok": False, "error": "cli_unavailable", "detail": str(exc)})
        return 1

    newest = published_version()
    report = {
        "ok": True,
        "mode": "check" if args.check else ("write" if args.write else "dry-run"),
        "cli_source": source,
        "cli_version": latest,
        "latest_published": newest,
        "snapshot_version": cur_ver,
        "template_count_local": len([f for f in os.listdir(PAGES_DIR) if f.endswith(".txt")])
        if os.path.isdir(PAGES_DIR) else 0,
        "template_count_upstream": len(pages),
        "local_aggregate_sha256": local_hash,
        "snapshot_aggregate_sha256": cur_hash,
        "local_matches_snapshot": local_hash == cur_hash if cur_hash else None,
        "version_drift": bool(cur_ver and newest and cur_ver != newest),
        "network_used": True,
    }

    if args.check:
        emit(report)
        return 0

    if not args.write:
        report["note"] = "干跑模式，未写入任何文件。加 --write 才会应用。"
        report["would_write"] = len(pages)
        emit(report)
        return 0

    staging = tempfile.mkdtemp(prefix="astryx-tpl-")
    try:
        written, failed = extract(cmd, pages, staging)
        if failed:
            emit({**report, "ok": False, "error": "partial_extraction",
                  "written": written, "failed": failed[:10],
                  "note": "未改动现有模板。"})
            return 1

        # Only touch the live directory once the full extraction succeeded.
        backup = os.path.join(TPL_DIR, "pages.new")
        if os.path.isdir(backup):
            shutil.rmtree(backup)
        shutil.copytree(staging, backup)
        old = os.path.join(TPL_DIR, "pages.old")
        if os.path.isdir(old):
            shutil.rmtree(old)
        if os.path.isdir(PAGES_DIR):
            shutil.move(PAGES_DIR, old)
        shutil.move(backup, PAGES_DIR)

        new_hash = aggregate_hash(PAGES_DIR)
        # INDEX.md is generated into templates/, beside pages/, not inside it.
        write_index(pages, blocks, TPL_DIR, latest)
        snap = {
            "schema": 1,
            "source": {
                "project": "astryx",
                "repository": "https://github.com/meta/astryx",
                "package": PACKAGE,
                "license": "MIT",
                "copyright": "Copyright (c) 2026 Meta Platforms, Inc.",
                "extraction_command": "astryx template <id> --skeleton",
            },
            "snapshot": {
                "cli_version": latest,
                "core_version": latest,
                "extracted_at": __import__("datetime").date.today().isoformat(),
                "page_templates": written,
                "aggregate_sha256": new_hash,
            },
            "refresh": current.get("refresh", {}),
        }
        write_snapshot_text(SNAPSHOT,
                            json.dumps(snap, indent=2, ensure_ascii=False) + "\n")
        if os.path.isdir(old):
            shutil.rmtree(old)

        report.update({
            "written": written,
            "failed": [],
            "new_aggregate_sha256": new_hash,
            "note": f"已更新 {written} 个模板骨架，旧版本已备份后清理。",
        })
        emit(report)
        return 0
    finally:
        shutil.rmtree(staging, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
