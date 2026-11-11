#!/usr/bin/env python3
"""Regression tests for the routing scripts.

These exist because every defect found in audit was a script that ran fine and
returned a wrong answer. Only assertions catch that class of bug.

Run with:  python -m unittest discover -s tests -v
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCRIPTS = os.path.join(SKILL, "scripts")
PY = sys.executable


def run(script, *args):
    proc = subprocess.run(
        [PY, os.path.join(SCRIPTS, script), *args],
        capture_output=True,
    )
    out = proc.stdout.decode("utf-8", "replace")
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        payload = {"_raw": out, "_stderr": proc.stderr.decode("utf-8", "replace")}
    return proc.returncode, payload


class Fixture:
    """A throwaway project directory holding one package.json."""

    def __init__(self, deps, dev=None, extra=None):
        self.dir = tempfile.mkdtemp(prefix="uisr-test-")
        pkg = {"name": "fixture", "dependencies": deps}
        if dev:
            pkg["devDependencies"] = dev
        if extra:
            pkg.update(extra)
        with open(os.path.join(self.dir, "package.json"), "w", encoding="utf-8") as fh:
            json.dump(pkg, fh)

    def child(self, rel, deps):
        path = os.path.join(self.dir, rel)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "package.json"), "w", encoding="utf-8") as fh:
            json.dump({"name": "child", "dependencies": deps}, fh)

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class TemplateRoutingTest(unittest.TestCase):
    """The template picker must never resolve a query to the wrong template."""

    def test_every_id_resolves_to_itself(self):
        _, listing = run("pick_template.py", "--list")
        self.assertTrue(listing.get("ok"))
        for entry in listing["templates"]:
            tid = entry["id"]
            _, out = run("pick_template.py", tid)
            self.assertEqual(
                out.get("chosen", {}).get("id"), tid,
                f"{tid!r} resolved to {out.get('chosen', {}).get('id')!r}",
            )

    def test_english_substrings_do_not_match(self):
        # "ai" in email/remainder, "form" in information, "ide" in side-gallery.
        for query in ("remainder", "container 管理", "detail page",
                      "performance information"):
            _, out = run("pick_template.py", query)
            chosen = (out.get("chosen") or {}).get("id")
            self.assertNotIn(
                chosen, ("ai-chat", "ai-chat-landing", "form-two-column"),
                f"{query!r} matched a substring-only template: {chosen}",
            )

    def test_chinese_intents_still_work(self):
        cases = {
            "做个登录页": "login",
            "后台管理系统 带表格和筛选": "dashboard",
            "看板": "kanban-board",
            "商品详情页": "product-detail",
        }
        for query, expected in cases.items():
            _, out = run("pick_template.py", query)
            self.assertEqual(out.get("chosen", {}).get("id"), expected, query)

    def test_library_value_required(self):
        rc, out = run("pick_template.py", "登录", "--library")
        self.assertEqual(rc, 2)
        self.assertEqual(out.get("error"), "missing_library_value")

    def test_unknown_library_is_rejected_not_silently_html(self):
        rc, out = run("pick_template.py", "登录", "--library", "bootstrap")
        self.assertEqual(rc, 2)
        self.assertEqual(out.get("error"), "unknown_library")

    def test_annotation_field_name(self):
        _, out = run("pick_template.py", "登录页", "--library", "naive-ui")
        self.assertIn("annotated", out)
        self.assertNotIn("translated", out)


class StackRoutingTest(unittest.TestCase):
    def setUp(self):
        self.fixtures = []

    def tearDown(self):
        for fx in self.fixtures:
            fx.cleanup()

    def plan_for(self, deps, dev=None):
        fx = Fixture(deps, dev)
        self.fixtures.append(fx)
        _, out = run("route_stack.py", fx.dir)
        return out["plan"]

    def test_uniapp_does_not_get_a_web_library(self):
        plan = self.plan_for({"@dcloudio/uni-app": "^3.0.0", "vue": "^3.4.0"})
        self.assertEqual(plan["framework"], "uniapp")
        self.assertNotEqual(plan["primary"], "naive-ui")

    def test_taro_does_not_get_a_web_library(self):
        plan = self.plan_for({"@tarojs/taro": "^4.0.0", "react": "^18.0.0"})
        self.assertEqual(plan["framework"], "taro")
        self.assertNotIn("astryx", plan["package"])

    def test_astro_is_not_greenfield(self):
        plan = self.plan_for({"astro": "^5.0.0", "react": "^19.0.0"})
        self.assertNotEqual(plan["decision"], "greenfield")
        self.assertNotEqual(plan["primary"], "naive-ui")

    def test_qwik_is_not_greenfield(self):
        plan = self.plan_for({"@builder.io/qwik": "^1.0.0"})
        self.assertNotEqual(plan["decision"], "greenfield")

    def test_tailwind_only_still_gets_a_component_library(self):
        plan = self.plan_for({"react": "^19.0.0"}, dev={"tailwindcss": "^4.0.0"})
        self.assertEqual(plan["decision"], "install_primary")
        self.assertTrue(plan["has_tailwind"])

    def test_vue2_is_not_told_to_install_naive_ui(self):
        plan = self.plan_for({"vue": "^2.7.16"})
        self.assertEqual(plan["decision"], "incompatible_version")
        self.assertNotEqual(plan["package"], "naive-ui")

    def test_existing_library_wins_over_route_default(self):
        plan = self.plan_for({"vue": "^3.4.0", "element-plus": "^2.7.0"})
        self.assertEqual(plan["decision"], "reuse_existing")
        self.assertEqual(plan["package"], "element-plus")

    def test_greenfield_design_stack_follows_starter(self):
        tmp = tempfile.mkdtemp(prefix="uisr-empty-")
        try:
            _, out = run("route_stack.py", tmp)
            plan = out["plan"]
            self.assertEqual(plan["decision"], "greenfield")
            self.assertEqual(plan["design_search_stack"], "vue")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_monorepo_resolves_to_the_app_package(self):
        fx = Fixture({"turbo": "^2.0.0"}, extra={"private": True,
                                                  "workspaces": ["apps/*"]})
        self.fixtures.append(fx)
        fx.child(os.path.join("apps", "web"),
                 {"react": "^19.0.0", "antd": "^5.0.0"})
        _, out = run("route_stack.py", fx.dir)
        self.assertEqual(out["detected"]["framework"], "react")
        self.assertEqual(out["plan"]["decision"], "reuse_existing")
        self.assertIn("antd", out["plan"]["already_installed"])

    def test_monorepo_without_root_manifest(self):
        fx = Fixture({"turbo": "^2.0.0"})
        self.fixtures.append(fx)
        os.remove(os.path.join(fx.dir, "package.json"))
        fx.child(os.path.join("apps", "web"), {"vue": "^3.4.0", "naive-ui": "^2.38.0"})
        _, out = run("route_stack.py", fx.dir)
        self.assertEqual(out["detected"]["framework"], "vue")


class UpdateTemplateSafetyTest(unittest.TestCase):
    """Template ids come from an external CLI, so they must not escape the dir."""

    def test_rejects_traversal_ids(self):
        sys.path.insert(0, SCRIPTS)
        import update_templates as U

        workdir = tempfile.mkdtemp(prefix="uisr-safe-")
        try:
            self.assertTrue(U.safe_template_path(workdir, "dashboard").endswith("dashboard.txt"))
            self.assertTrue(U.safe_template_path(workdir, "form-wizard.v2").endswith("form-wizard.v2.txt"))
            for bad in ("../evil", "..\\evil", "/etc/passwd", "C:\\x", "a/b",
                        "..", ".", "", "a\x00b", "a.b..c"):
                with self.assertRaises(RuntimeError, msg=bad):
                    U.safe_template_path(workdir, bad)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    def test_write_helpers_stay_inside_dir(self):
        sys.path.insert(0, SCRIPTS)
        import update_templates as U

        workdir = tempfile.mkdtemp(prefix="uisr-write-")
        try:
            path = U.write_template_file(workdir, "dashboard", "x")
            self.assertTrue(os.path.isfile(path))
            U.write_index_text(workdir, "hello")
            self.assertTrue(os.path.isfile(os.path.join(workdir, "INDEX.md")))
            snap = os.path.join(workdir, "snapshot.json")
            U.write_snapshot_text(snap, "{}")
            self.assertTrue(os.path.isfile(snap))
            with self.assertRaises(RuntimeError):
                U.write_template_file(workdir, "../escape", "x")
        finally:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
