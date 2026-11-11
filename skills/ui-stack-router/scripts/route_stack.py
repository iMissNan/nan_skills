#!/usr/bin/env python3
"""Route a detected frontend stack to the right UI library and skill workflow.

Reads the JSON from detect_stack.py and prints a decision plan. Uses only the
Python standard library.

Usage:
    python route_stack.py <project-dir>
    python route_stack.py --framework vue
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DETECT = os.path.join(HERE, "detect_stack.py")


def find_uiux_skill():
    """Locate the optional ui-ux-pro-max skill without hardcoding a user path.

    Searches the skill roots ZCode and other agent hosts use, relative to the
    current user's home. Returns the absolute path to its search.py, or None
    when the companion skill is not installed.
    """
    home = os.path.expanduser("~")
    roots = [
        os.path.join(home, ".zcode", "skills"),
        os.path.join(home, ".claude", "skills"),
        os.path.join(home, ".agents", "skills"),
        os.path.join(home, ".config", "agents", "skills"),
    ]
    for root in roots:
        candidate = os.path.join(root, "ui-ux-pro-max", "scripts", "search.py")
        if os.path.isfile(candidate):
            return candidate
    return None


UIUX = find_uiux_skill()

# framework -> routing decision.
# `weekly_downloads` and `stars` are measured 2026-11; keep them with the
# recommendation so the choice carries its evidence instead of an impression.
ROUTES = {
    "react": {
        "tier": "组件库",
        "primary": "astryx",
        "package": "@astryxdesign/core",
        "install": "npm install @astryxdesign/core @astryxdesign/theme-neutral @stylexjs/stylex && npm install -D @astryxdesign/cli",
        "requires": "React >= 19.0.0",
        "why": "Meta 设计系统：150+ 组件、预编译 CSS、页面模板，另有 agent CLI。开箱最精致。",
        "agent_setup": "npx @astryxdesign/cli init",
        "weekly_downloads": 661968,
        "tradeoff": "周下载量约为 MUI 的 1/21，属新贵而非主流；生态答案较少。要稳妥选 MUI 或 antd。",
        "mainstream": "MUI (13,836,129/周) 或 antd (5,359,099/周)",
        "fallback": "shadcn/ui（React + Tailwind，组件复制进项目）",
        "fallback_package": "shadcn",
    },
    "vue": {
        "tier": "组件库",
        "primary": "naive-ui",
        "package": "naive-ui",
        "install": "npm install naive-ui",
        "requires": "Vue >= 3.0",
        "why": "Vue 3 原生，约 90 个组件，主题用 JS 对象覆盖，默认样式最精致，最接近 astryx 那种开箱质感。",
        "agent_setup": "n/a - 组件库，无需 agent CLI",
        "weekly_downloads": 197042,
        "tradeoff": "生态不如 Vuetify(131万) 与 Element Plus(79万)；出问题时中文资料较少。",
        "mainstream": "Vuetify (1,310,471/周) 或 Element Plus (797,315/周，中文文档最全)",
        "fallback": "shadcn-vue（Vue + Tailwind + reka-ui，组件复制进项目，设计可控性更高）",
        "fallback_package": "shadcn-vue",
    },
    "svelte": {
        "tier": "组件库",
        "primary": "shadcn-svelte",
        "package": "shadcn-svelte",
        "install": "npx shadcn-svelte@latest init",
        "requires": "Svelte >= 5",
        "why": "Svelte 生态下载量最高(300,511/周)，组件复制进项目，可深度定制。",
        "agent_setup": "n/a",
        "weekly_downloads": 300511,
        "tradeoff": "需要 Tailwind；比 skeleton 多一步配置。",
        "mainstream": "shadcn-svelte (300,511/周)",
        "fallback": "@skeletonlabs/skeleton（93,565/周，主题系统完整）",
        "fallback_package": "@skeletonlabs/skeleton",
    },
    "solid": {
        "tier": "组件库",
        "primary": "park-ui",
        "package": "@park-ui/presets",
        "install": "npm install @park-ui/presets",
        "requires": "SolidJS",
        "why": "Solid 版的 Radix/shadcn 模式。",
        "agent_setup": "n/a",
        "weekly_downloads": None,
        "tradeoff": "生态较小，需自行评估。",
        "mainstream": "Kobalte (headless 原语)",
        "fallback": "Kobalte（Solid headless 原语）",
        "fallback_package": "@kobalte/core",
    },
    "astro": {
        "tier": "岛屿架构",
        "primary": "跟随岛屿框架",
        "package": "n/a",
        "install": "先确定岛屿框架（React/Vue/Svelte），再按对应路线走",
        "requires": "Astro",
        "why": "Astro 渲染 islands，UI 库取决于项目实际使用的岛屿框架。",
        "agent_setup": "n/a",
        "weekly_downloads": None,
        "tradeoff": "无单一答案，取决于岛屿框架。",
        "mainstream": "取决于岛屿框架",
        "fallback": "纯 CSS + 设计 token",
        "fallback_package": "n/a",
    },
    "qwik": {
        "tier": "框架专有",
        "primary": "无成熟组件库",
        "package": "n/a",
        "install": "Qwik 生态暂无稳定 UI 组件库，用 @builder.io/qwik 原语自行实现",
        "requires": "Qwik",
        "why": "Qwik 的可恢复性模型与主流组件库不兼容，社区组件库均为早期状态。",
        "agent_setup": "n/a",
        "weekly_downloads": None,
        "tradeoff": "无可靠第三方组件库，样式需自建。",
        "mainstream": "Qwik 官方样式方案（CSS Modules / Tailwind）",
        "fallback": "Tailwind + 设计 token",
        "fallback_package": "tailwindcss",
    },
    "taro": {
        "tier": "跨端小程序组件库",
        "primary": "@nutui/nutui-react-taro",
        "package": "@nutui/nutui-react-taro",
        "install": "npm install @nutui/nutui-react-taro",
        "requires": "Taro",
        "why": "Taro 编译到小程序与 App，Web 组件库（依赖 DOM）在端内不可用。",
        "agent_setup": "n/a",
        "weekly_downloads": None,
        "tradeoff": "仅限 Taro 生态；React 版与 Vue 版需按宿主框架选择。",
        "mainstream": "NutUI Taro 版（京东官方）",
        "fallback": "Taro UI（旧版，维护放缓）",
        "fallback_package": "taro-ui",
    },
    "angular": {
        "tier": "组件库",
        "primary": "@angular/material",
        "package": "@angular/material",
        "install": "ng add @angular/material",
        "requires": "Angular",
        "why": "Angular 官方组件库，Material Design 默认样式。",
        "agent_setup": "n/a",
        "weekly_downloads": None,
        "tradeoff": "Material 风格明显，定制成本较高。",
        "mainstream": "PrimeNG (22.x)",
        "fallback": "PrimeNG（组件更全）",
        "fallback_package": "primeng",
    },
    "uniapp": {
        "tier": "跨端小程序组件库",
        "primary": "uview-plus",
        "package": "uview-plus",
        "install": "npm install uview-plus",
        "requires": "uni-app",
        "why": "uni-app 编译到小程序/App/H5，通用 Web 组件库在这些端上无法运行。",
        "agent_setup": "n/a",
        "weekly_downloads": None,
        "tradeoff": "仅限 uni-app 生态，跨端样式需分别验证。",
        "mainstream": "uview-plus（uni-app 生态主流）",
        "fallback": "wot-design-uni",
        "fallback_package": "wot-design-uni",
    },
    "unknown": {
        "tier": "未识别",
        "primary": "无",
        "package": "n/a",
        "install": "n/a",
        "requires": "n/a",
        "why": "没有 package.json 或不认识框架。必须先问用户用什么技术栈，不得凭空推荐。",
        "agent_setup": "n/a",
        "weekly_downloads": None,
        "tradeoff": "无数据，不做推荐。",
        "mainstream": "n/a",
        "fallback": "纯 CSS + 设计 token",
        "fallback_package": "n/a",
    },
}

# Default stack offered when a project has no framework yet. Chosen for a
# non-specialist who wants a good-looking result with minimal setup:
# Vue 3 is the gentlest start, Naive UI has the best out-of-the-box polish in
# the Vue ecosystem, and Vite needs no configuration.
STARTER_STACK = {
    "framework": "vue",
    "framework_label": "Vue 3 + Vite",
    "primary": "naive-ui",
    "package": "naive-ui",
    "install": "npm create vite@latest my-app -- --template vue-ts && cd my-app && npm install naive-ui",
    "requires": "Node 18+（无需全局安装）",
    "why": "Vue 3 上手最快，Naive UI 在 Vue 生态里默认样式最精致，Vite 零配置。",
    "design_search_stack": "vue",
}

# Map a detected framework to the ui-ux-pro-max stack data file to search.
STACK_DATA = {
    "react": "react",
    "vue": "vue",
    "svelte": "svelte",
    "solid": "react",
    "astro": "astro",
    "qwik": "react",
    "angular": "angular",
    "uniapp": "vue",
    "taro": "react",
    "unknown": "html-tailwind",
}

# Runtimes that compile to a non-DOM host (mini-program, app shell). A Web
# component library cannot run there, so the runtime outranks the framework
# the project happens to declare alongside it.
HOST_RUNTIMES = ("uniapp", "taro")


def major_version(spec):
    """Return the major version of a semver range, or None when unknown.

    Handles the ranges that actually appear in package.json: "^3.4.0",
    "~2.7.16", ">=3", "3.x", "workspace:*" (unknown), "latest" (unknown).
    """
    if not isinstance(spec, str):
        return None
    match = re.search(r"(\d+)", spec)
    return int(match.group(1)) if match else None


def run_detect(root):
    proc = subprocess.run(
        [sys.executable, "-I", DETECT, root],
        capture_output=True,
    )
    out = (proc.stdout or b"").decode("utf-8", "replace")
    err = (proc.stderr or b"").decode("utf-8", "replace")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"ok": False, "error": "detect_failed", "detail": (out + err)[:800]}


def build_plan(detected):
    # A mini-program runtime owns the stack even when the project also declares
    # react/vue: those are the host framework, not the rendering target.
    runtime = detected.get("runtime")
    if runtime in HOST_RUNTIMES:
        framework = runtime
    else:
        framework = detected.get("framework") or "unknown"

    route = dict(ROUTES.get(framework, ROUTES["unknown"]))
    route["framework"] = framework
    route["framework_label"] = detected.get("framework_label") or detected.get("runtime_label") or "unknown"
    if runtime and runtime != framework:
        route["host_runtime"] = runtime
        route["host_runtime_label"] = detected.get("runtime_label")

    existing = detected.get("existing_ui") or []
    route["already_installed"] = existing
    route["has_tailwind"] = bool(detected.get("has_tailwind"))
    has_pkg = bool(detected.get("has_package_json", detected.get("package_json")))

    # Version gate: naive-ui needs Vue 3. A Vue 2 project must not be told to
    # install it. Reported as its own decision so the caller sees the reason.
    versions = detected.get("versions") or {}
    vue_major = major_version(versions.get("vue"))
    vue2 = framework == "vue" and vue_major is not None and vue_major < 3

    if existing:
        installed_primary = route["package"] in existing
        route["decision"] = "reuse_existing"
        route["decision_detail"] = (
            f"项目已依赖 {', '.join(existing)}。直接用它，不要新增第二个 UI 库（除非用户明确要求）。"
        )
        if installed_primary:
            route["decision_detail"] = (
                f"项目已依赖 {route['primary']}（{route['package']}）。直接使用其组件，无需安装。"
            )
        else:
            # The routed default is not what this project actually uses, so the
            # plan must not keep advertising it as the primary choice.
            route["primary"] = existing[0]
            route["package"] = existing[0]
            route["install"] = "n/a - 已安装，直接 import 使用"
            route["why"] = f"项目现有的 UI 库是 {existing[0]}，复用它而不是引入第二套。"
    elif vue2:
        route["decision"] = "incompatible_version"
        route["decision_detail"] = (
            f"检测到 Vue {versions.get('vue')}，而 {route['primary']} 需要 {route['requires']}。"
            "不要安装它——Vue 2 项目请用 Element UI（Vue 2 版）或 Vuetify 2，"
            "或先迁移到 Vue 3。"
        )
        route["primary"] = "element-ui"
        route["package"] = "element-ui"
        route["install"] = "npm install element-ui"
        route["requires"] = "Vue 2.x"
        route["mainstream"] = "Element UI (Vue 2) 或 Vuetify 2"
        route["vue_major"] = vue_major
    elif not has_pkg and framework == "unknown":
        # No package.json at all: a genuinely empty project. This must NOT block
        # the design work. Offer a starter stack instead of interrogating them.
        route["decision"] = "greenfield"
        route["decision_detail"] = (
            "这是一个还没有技术栈的新项目。不要卡住追问框架——先按下面的默认组合开始设计，"
            "同时用一句话告诉用户选了什么、可以随时改。"
        )
        route["starter"] = STARTER_STACK
        route["starter_note"] = (
            f"默认组合：{STARTER_STACK['framework_label']} + {STARTER_STACK['primary']}。"
            "若用户已说明用别的框架，改用对应路线。"
        )
        route["primary"] = STARTER_STACK["primary"]
        route["package"] = STARTER_STACK["package"]
        route["install"] = STARTER_STACK["install"]
        route["requires"] = STARTER_STACK["requires"]
        route["why"] = STARTER_STACK["why"]
        route["framework"] = STARTER_STACK["framework"]
        route["framework_label"] = STARTER_STACK["framework_label"]
        route["new_project"] = True
    elif route["package"] == "n/a":
        # Recognised framework with no single library answer (Astro、Qwik、未识别
        # 但有 package.json 的项目)。It is NOT a new project — say so instead of
        # silently rewriting the stack to Vue.
        route["decision"] = "framework_specific"
        if framework == "unknown":
            route["decision_detail"] = (
                "检测到项目已有 package.json，但没识别出前端框架或 UI 库。"
                "先读依赖清单并向用户报告探测结果，确认技术栈后再选库，不要当成新项目开工。"
            )
        else:
            route["decision_detail"] = (
                f"{route['framework_label']} 的组件库取决于实际渲染层，没有唯一答案。"
                "先确认项目内使用的岛屿/宿主框架（React / Vue / Svelte），再按对应路线走。"
                "不要套用其他框架的默认组合。"
            )
    else:
        route["decision"] = "install_primary"
        route["decision_detail"] = f"未检测到 UI 库。安装 {route['primary']}（{route['package']}）。"
        if route["has_tailwind"]:
            route["decision_detail"] += (
                " 项目已有 Tailwind（样式层，不含组件）；若想与 Tailwind 同栈，"
                "可优先考虑 shadcn 系（shadcn-vue / shadcn）。"
            )

    # The design-search stack must follow the framework actually decided on,
    # including the greenfield starter, so it is assigned exactly once here.
    route["design_search_stack"] = STACK_DATA.get(route["framework"], "html-tailwind")
    # ui-ux-pro-max is an optional companion skill. Report the resolved path
    # when present, and an explicit null when it is not installed, so callers
    # never receive a command pointing at a path that does not exist.
    if UIUX:
        route["design_search_available"] = True
        route["design_search_command"] = (
            f'python "{UIUX}" "<产品关键词>" --design-system -p "<项目名>"'
        )
    else:
        route["design_search_available"] = False
        route["design_search_command"] = None
        route["design_search_hint"] = (
            "未安装可选的 ui-ux-pro-max 技能；跳过配色/字体 token 检索，"
            "直接按库的主题默认值实现。"
        )
    return route


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

    if argv[1] == "--framework":
        if len(argv) < 3:
            emit({"ok": False, "error": "missing_framework_value"})
            return 2
        detected = {"ok": True, "framework": argv[2].lower(), "framework_label": argv[2], "existing_ui": []}
    else:
        detected = run_detect(argv[1])
        if not detected.get("ok"):
            emit(detected)
            return 1

    plan = build_plan(detected)
    emit({"detected": detected, "plan": plan})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
