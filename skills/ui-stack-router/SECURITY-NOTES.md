# 安全扫描裁决记录

本文件记录 Mimosa 安全门禁在提交时报告的静态告警，以及人工逐条的核实结论。
Mimosa 的 `deep` 扫描对本次改动的结论是 **inconclusive**，每条 finding 都附带
"静态 advisory 需要人工确认真实数据流和可利用性"的 proof gap。

- 扫描 ID：`scan-2026-11-11T08-54-45.278Z-b951b443be56`
- 封印：`sha256:7b9af108cf54b8d7995d6b9e47a7b13297ff96f9860b118e8c4944eed5e83a50`
- 结论：6 条 finding，0 条业务逻辑候选，**全部为静态模式匹配的误报**

## 第二轮加固（响应 L2 复扫）

针对第一轮告警，代码已做到：

1. **模板 id 白名单**：`SAFE_ID = ^[A-Za-z0-9][A-Za-z0-9._-]*$`，拒绝 `..` 子串、
   路径分隔符、盘符、NUL、非字符串。
2. **写入路径归一化**：`os.path.realpath` 后与根目录比对 `commonpath`。
3. **校验与写入合并**：`write_template_file()` / `write_index_text()` /
   `write_snapshot_text()` 把"校验"和 `open()` 放在同一个函数体内，调用方
   无法跳过校验。
4. **网络目标白名单**：URL 由两个模块常量拼成，发出前断言
   `scheme == https and hostname == registry.npmjs.org`。

复扫后仍报 6 条，行号随代码变动（`:191` SSRF、`:253`/`:290`/`:300` 路径穿越、
`detect_stack.py:301`、`pick_template.py:309`）。**原因是扫描器的判定规则**：
它对 `open(<变量>, "w")` 和 `urlopen(<变量>)` 一律标记，不回溯该变量是否已在
同函数内被校验。

## 逐条裁决

### 1. `scripts/update_templates.py` SSRF（复扫 :191）

**判定：误报。**

请求目标由两个模块常量拼接，并在发出前断言：

```python
REGISTRY_ORIGIN = "https://registry.npmjs.org"
CLI_LATEST_PATH = "/@astryxdesign%2Fcli/latest"

url = urllib.parse.urljoin(REGISTRY_ORIGIN, CLI_LATEST_PATH)
parsed = urllib.parse.urlparse(url)
if parsed.scheme != "https" or parsed.hostname != "registry.npmjs.org":
    raise RuntimeError(...)
```

没有任何调用方参数参与 URL 构造。扫描器把"变量形式的 URL"一律标记，但不检查
变量来源。主机固定为 npm 官方 registry，响应只取一个版本字符串。

### 2. `scripts/update_templates.py` 路径穿越（复扫 :253）

**判定：误报。**

```python
def write_template_file(out_dir, template_id, payload):
    """Validate, then write. Kept as one unit so the check cannot be skipped."""
    path = safe_template_path(out_dir, template_id)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(payload)
```

`path` 是本函数内第一行由 `safe_template_path()` 返回的值，该函数已完成
白名单匹配、`..` 拒绝、basename 校验与 realpath 越界检查。扫描器只看
`open(<变量>, "w")` 这一形态，不跟入被调函数。

### 3. `scripts/update_templates.py` 路径穿越（复扫 :290、:300）

**判定：误报。**

两处分别是 `write_index_text()` 和 `write_snapshot_text()`：

```python
root = os.path.realpath(out_dir)
path = os.path.realpath(os.path.join(root, INDEX_NAME))
if os.path.commonpath([path, root]) != root:
    raise RuntimeError(...)
with open(path, "w", ...) as fh:
```

`INDEX_NAME` 是字面量 `"INDEX.md"`；`snapshot_path` 是模块常量 `SNAPSHOT`。
两者都在写入前做了 realpath 归一化与父目录越界检查。

### 4. 原 `entry["id"]` 直接拼路径（第一轮 :262）

**判定：真实问题，已修复。**

原实现把 CLI 返回的 `entry["id"]`（外部进程输出）直接拼进写盘路径。虽然
astryx 是可信来源，但"上游返回的字符串当作文件名"是应当防御的边界。现已改为
统一经 `safe_template_path()`，并用 `tests/test_routing.py` 固化：

覆盖用例：`../evil`、`..\evil`、`/etc/passwd`、`C:\x`、`a/b`、`..`、`.`、
空串、含 NUL、`a.b..c`、非字符串，全部拒绝；正常 id 与含点的 `form-wizard.v2`
通过。

### 5. `scripts/detect_stack.py:301` main 经 2 跳到达 path-traversal

**判定：误报，属工具设计。**

污点链为 `main → detect → read_json`，源头是命令行传入的项目目录。这个工具
的**唯一职责**就是读取用户指定项目的 `package.json` 并报告框架。如果拒绝接受
目录参数，工具就失去意义。且该路径全程只读：`read_json()` 只做
`open(path).read()` + `json.load()`，不写入、不删除、不回显文件内容。

### 6. `scripts/pick_template.py:309` main 是 path-traversal 入口

**判定：误报。**

`main()` 内所有路径均来自模块常量 `PAGES_DIR`、`MAP_PATH`，由 `HERE` 推导：

```python
HERE = os.path.dirname(os.path.abspath(__file__))
TPL_DIR = os.path.join(os.path.dirname(HERE), "templates")
```

用户输入只参与关键词评分，不参与任何路径拼接。

## 处理原则

1. 真实问题一律修复并补测试，不靠裁决放行。
2. 误报逐条写明"为什么这条数据流不存在"，而不是笼统标注忽略。
3. 不修改或绕过 Mimosa 门禁本身。
