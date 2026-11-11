#!/usr/bin/env python3
"""Detect the frontend framework of a project directory.

Prints one JSON object. Uses only the Python standard library.

Usage:
    python detect_stack.py <project-dir>
    python detect_stack.py <project-dir> --json
"""

import glob
import json
import os
import sys

# Ordered most-specific first: a Next.js app also declares `react`,
# and Nuxt also declares `vue`, so the meta-framework wins.
FRAMEWORK_MARKERS = [
    ("next", "react", "Next.js"),
    ("nuxt", "vue", "Nuxt"),
    ("nuxt3", "vue", "Nuxt"),
    ("@remix-run/react", "react", "Remix"),
    ("astro", "astro", "Astro"),
    ("@sveltejs/kit", "svelte", "SvelteKit"),
    ("svelte", "svelte", "Svelte"),
    ("@angular/core", "angular", "Angular"),
    ("solid-js", "solid", "Solid"),
    ("@builder.io/qwik", "qwik", "Qwik"),
    ("react", "react", "React"),
    ("vue", "vue", "Vue"),
    ("preact", "react", "Preact"),
]

# Mini-program / cross-platform runtimes, which need their own component sets.
RUNTIME_MARKERS = [
    ("uview-plus", "uniapp", "uni-app (uview-plus)"),
    ("@dcloudio/uni-app", "uniapp", "uni-app"),
    ("@tarojs/taro", "taro", "Taro"),
    ("uni-app", "uniapp", "uni-app"),
]

# UI libraries already present, so the router does not recommend a second one.
# Every name here must exist on npm; `antdv`, `element-plus-vite` and
# `@radix-ui/react` were removed because they are not published packages.
# `tailwindcss` is a CSS utility, not a component library, so it is tracked
# separately as `has_tailwind`.
EXISTING_UI = [
    "naive-ui",
    "element-plus",
    "shadcn-vue",
    "reka-ui",
    "radix-vue",
    "vuetify",
    "@nuxt/ui",
    "@headlessui/vue",
    "primevue",
    "ant-design-vue",
    "@arco-design/web-vue",
    "vant",
    "quasar",
    "uview-plus",
    "@astryxdesign/core",
    "antd",
    "@mui/material",
    "@chakra-ui/react",
    "@mantine/core",
    "shadcn",
    "shadcn-ui",
    "@shadcn/ui",
    "@headlessui/react",
]

CONFIG_FILES = [
    ("next.config.js", "react", "Next.js"),
    ("next.config.mjs", "react", "Next.js"),
    ("next.config.ts", "react", "Next.js"),
    ("nuxt.config.ts", "vue", "Nuxt"),
    ("nuxt.config.js", "vue", "Nuxt"),
    ("vite.config.ts", "unknown", "Vite"),
    ("vite.config.js", "unknown", "Vite"),
    ("angular.json", "angular", "Angular"),
    ("svelte.config.js", "svelte", "Svelte"),
    ("astro.config.mjs", "astro", "Astro"),
]


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def collect_deps(pkg):
    deps = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        section = pkg.get(key)
        if isinstance(section, dict):
            deps.update(section)
    return deps


# Files that mark a directory as a workspace container rather than an app.
WORKSPACE_MARKERS = (
    "pnpm-workspace.yaml",
    "turbo.json",
    "nx.json",
    "lerna.json",
    "rush.json",
)


def _deps_of(path):
    try:
        return collect_deps(read_json(path))
    except (OSError, json.JSONDecodeError):
        return {}


def _is_workspace_container(path):
    """True when a package.json only declares workspaces, not an application."""
    try:
        pkg = read_json(path)
    except (OSError, json.JSONDecodeError):
        return False
    if pkg.get("workspaces"):
        return True
    # A private root with no runtime dependencies is a container too.
    return bool(pkg.get("private")) and not pkg.get("dependencies")


def _candidate_packages(root):
    """package.json files one or two levels below a workspace root.

    Skips node_modules and dot-directories so a deep dependency cannot be
    mistaken for the project's own application.
    """
    found = []
    patterns = (
        os.path.join("apps", "*", "package.json"),
        os.path.join("apps", "*", "*", "package.json"),
        os.path.join("packages", "*", "package.json"),
        os.path.join("packages", "*", "*", "package.json"),
        os.path.join("frontend", "*", "package.json"),
        os.path.join("services", "*", "package.json"),
        os.path.join("*", "package.json"),
    )
    for pattern in patterns:
        for path in sorted(glob.glob(os.path.join(root, pattern))):
            parts = os.path.relpath(path, root).split(os.sep)
            if any(p.startswith(".") or p == "node_modules" for p in parts):
                continue
            if path not in found:
                found.append(path)
    return found


def find_package_json(root):
    """Return the package.json that best represents this project's application.

    A workspace root (pnpm / turbo / nx / npm `workspaces`) carries no framework
    of its own. Reporting it as "unknown" would send the project down the
    greenfield path and recommend a brand-new Vue stack into an existing React
    repo, so the root is resolved to the most app-like package beneath it.
    """
    direct = os.path.join(root, "package.json")
    if os.path.isfile(direct) and not _is_workspace_container(direct):
        return direct

    is_workspace = any(
        os.path.isfile(os.path.join(root, marker)) for marker in WORKSPACE_MARKERS
    ) or (os.path.isfile(direct) and _is_workspace_container(direct))

    # No manifest anywhere at the root: the project may still be a workspace
    # laid out with apps/ or packages/ but no root package.json.
    if not is_workspace and not os.path.isfile(direct):
        is_workspace = any(
            os.path.isdir(os.path.join(root, name))
            for name in ("apps", "packages")
        )

    if is_workspace:
        best, best_score = None, -1
        for path in _candidate_packages(root):
            deps = _deps_of(path)
            score = 0
            if any(marker in deps for marker, _, _ in FRAMEWORK_MARKERS):
                score += 2
            if any(marker in deps for marker, _, _ in RUNTIME_MARKERS):
                score += 2
            if any(name in deps for name in EXISTING_UI):
                score += 1
            if score > best_score:
                best, best_score = path, score
        if best:
            return best
        if os.path.isfile(direct):
            return direct

    for name in ("frontend", "web", "app", "client", "ui"):
        candidate = os.path.join(root, name, "package.json")
        if os.path.isfile(candidate):
            return candidate

    return None


def detect(root):
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        return {
            "ok": False,
            "error": "not_a_directory",
            "detail": f"no such directory: {root}",
        }

    pkg_path = find_package_json(root)
    result = {
        "ok": True,
        "root": root,
        "package_json": pkg_path,
        "package_json_is_root": pkg_path == os.path.join(root, "package.json"),
        "has_package_json": pkg_path is not None,
        "framework": None,
        "framework_label": None,
        "runtime": None,
        "runtime_label": None,
        "versions": {},
        "existing_ui": [],
        "has_tailwind": False,
        "config_hints": [],
    }

    if pkg_path:
        try:
            pkg = read_json(pkg_path)
        except (OSError, json.JSONDecodeError) as exc:
            result["ok"] = False
            result["error"] = "unreadable_package_json"
            result["detail"] = str(exc)
            return result

        deps = collect_deps(pkg)

        for marker, framework, label in RUNTIME_MARKERS:
            if marker in deps:
                result["runtime"] = framework
                result["runtime_label"] = label
                result["versions"][marker] = deps[marker]
                break

        for marker, framework, label in FRAMEWORK_MARKERS:
            if marker in deps:
                result["framework"] = framework
                result["framework_label"] = label
                result["versions"][marker] = deps[marker]
                break

        result["existing_ui"] = [name for name in EXISTING_UI if name in deps]
        result["has_tailwind"] = "tailwindcss" in deps

        for marker, _, _ in FRAMEWORK_MARKERS + RUNTIME_MARKERS:
            if marker in deps and marker not in result["versions"]:
                result["versions"][marker] = deps[marker]

    for filename, framework, label in CONFIG_FILES:
        if os.path.isfile(os.path.join(root, filename)):
            result["config_hints"].append({"file": filename, "framework": framework, "label": label})
            if result["framework"] is None and framework != "unknown":
                result["framework"] = framework
                result["framework_label"] = label

    if result["framework"] is None and result["runtime"] is None:
        result["framework"] = "unknown"

    return result


def emit(payload):
    """Write JSON as UTF-8 regardless of the console code page (Windows GBK)."""
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
    if len(argv) < 2:
        emit({"ok": False, "error": "missing_argument"})
        return 2

    result = detect(argv[1])
    emit(result)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
