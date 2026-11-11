# ui-stack-router

一个给 AI 编码助手用的技能：**先判断项目框架，再选对的 UI 组件库，最后按页面模板骨架搭页面**——而不是从零手写。

解决一个具体问题：让 AI 生成的前端界面不再"能跑但难看"。

---

## 它解决什么

AI 写 UI 显丑，通常不是不会写 CSS，而是**没做布局决策**。组件库只给零件（`<Button>`、`<Card>`），页面怎么摆全靠模型临场发挥。

本技能把三件事固定下来：

| 步骤 | 做什么 |
|---|---|
| 1. 探测框架 | 读 `package.json`，认出 React / Vue / Nuxt / Svelte / Angular / uni-app |
| 2. 按数据选库 | 依据真实下载量与星数，不做凭印象的推荐；项目已有库则直接复用 |
| 3. 套页面模板 | 用 58 个布局骨架搭结构，再把组件名映射到目标库 |

## 关键区别：组件库 vs 设计规则库

| | 组件库 | 设计规则库 |
|---|---|---|
| 例子 | astryx、Naive UI、MUI | ui-ux-pro-max |
| 附带 CSS | 有 | **无** |
| 附带组件 | 有 | **无** |
| 不写 CSS 就好看 | **是** | 否（只提升 agent 手写质量） |

**两者不能互相替代。** 本技能把"规则库"当作配色/字体建议来源，把"组件库"当作实现手段，不混为一谈。

## 为什么内置模板骨架

`astryx`（Meta 的设计系统）开箱好看，很大程度来自它附带 **58 个页面模板 + 721 个区块模板**（免费，一条命令生成）。而 MUI、Naive UI、Element Plus **都不带页面模板**，只发组件。

本技能把 astryx 的模板用 `--skeleton` 抽成**布局骨架**——保留嵌套层级和 `padding`／`gap`／`columns` 的语义值，组件名仍是 astryx 的，属性仍是 JSX 写法（`padding={6}`），需按目标框架改写语法。

> **两个使用约束**（见 SKILL.md 第三步）：骨架最多 35 行，超出部分以 `...` 标记，须按模板 `description` 补全；`MetricCard` 等复合件不在映射表中，需按角色自行实现。

## 安装

```bash
# 在 nan_skills 仓库根目录执行
mkdir -p ~/.zcode/skills
cp -r skills/ui-stack-router ~/.zcode/skills/
```

其他客户端的技能目录见仓库根 README。重启客户端后生效。

## 使用

技能会自动触发。也可以显式调用：

```bash
# 探测框架并得到选型建议
python "$SKILL_DIR/scripts/route_stack.py" "<项目目录>"

# 按产品描述选页面模板（支持中文）
python "$SKILL_DIR/scripts/pick_template.py" "后台管理系统 带表格和筛选" --library naive-ui

# 列出全部 58 个模板
python "$SKILL_DIR/scripts/pick_template.py" --list
```

`$SKILL_DIR` 指本技能目录：
- 用户级安装：`~/.zcode/skills/ui-stack-router`
- 其他客户端：对应 skills 根目录下的 `ui-stack-router`

## 运行要求

- **Python 3.8+**，仅用标准库，无第三方依赖。
- **运行时零网络**：模板、组件映射、选型数据全部随包提供，断网可用。
- 无需 Node。仅"更新模板快照"这一步需要 Node（用 astryx CLI 重新抽取）。

## 测试

```bash
python -m unittest discover -s tests -v
```

16 项回归测试覆盖模板匹配、路由决策与异常输入。改动 `scripts/` 后请先跑它。

## 内置风格库

内置 **143 种设计风格**的离线快照（来源 [luckymaomi/ui](https://github.com/luckymaomi/ui)，MIT），
每种风格含中文说明、配色、AI 实现规则、设计 token、组件配方（Tailwind 类）。

```bash
# 按气质搜风格
python "$SKILL_DIR/scripts/search_style.py" "拟物"

# 取完整规则与组件配方
python "$SKILL_DIR/scripts/search_style.py" --slug skeuomorphism

# 列出全部 143 种
python "$SKILL_DIR/scripts/search_style.py" --list
```

运行时零网络；快照更新随仓库版本走。

## 模板更新机制

模板是**随包分发的离线快照**，不联网、不依赖 astryx 安装即可用。

### 检查是否有新版

```bash
python "$SKILL_DIR/scripts/update_templates.py" --check
```

输出会告诉你三件事：本地快照版本 vs 上游最新版本、模板数量差异、内容校验和是否一致。

```json
{
  "cli_version": "0.7.11",
  "snapshot_version": "0.7.11",
  "template_count_local": 58,
  "template_count_upstream": 58,
  "local_matches_snapshot": true,
  "version_drift": false
}
```

### 更新模板

```bash
# 1. 先干跑（默认行为，不写任何文件）
python "$SKILL_DIR/scripts/update_templates.py"

# 2. 确认后写入
python "$SKILL_DIR/scripts/update_templates.py" --write

# 3. 复现某个确切版本
python "$SKILL_DIR/scripts/update_templates.py" --version 0.7.11 --write
```

**安全性设计**：

- 默认 **dry-run**，不传 `--write` 绝不改文件
- 全量抽取成功后才替换，中途失败不动现有模板
- 替换前备份为 `pages.old`，成功后清理
- `INDEX.md` 与 `snapshot.json` 同步重新生成
- 更新是**幂等**的：同版本重跑不产生内容漂移

### 快照元数据

`templates/snapshot.json` 记录来源与版本：

```json
{
  "source": {
    "repository": "https://github.com/meta/astryx",
    "license": "MIT",
    "copyright": "Copyright (c) 2026 Meta Platforms, Inc."
  },
  "snapshot": {
    "cli_version": "0.7.11",
    "extracted_at": "2026-11-10",
    "page_templates": 58,
    "aggregate_sha256": "ac689c73..."
  }
}
```

校验和可用于确认模板未被意外改动。

## 可选同级技能

`ui-ux-pro-max`——用于取配色、字体、风格 token。未安装时自动跳过该步骤，其余功能不受影响。

```bash
python "$SKILL_DIR/scripts/route_stack.py" --framework vue
# 输出 plan.design_search_available: true/false 指示是否可用
```

## 目录结构

```
ui-stack-router/
├── SKILL.md                    技能说明与工作流
├── LICENSE                     MIT + 第三方归因
├── scripts/
│   ├── detect_stack.py         框架探测
│   ├── route_stack.py          选型路由（含权衡信息）
│   ├── pick_template.py        模板选取 + 组件名标注
│   ├── search_style.py         设计风格检索（143 种）
│   └── update_templates.py     模板快照更新（dry-run 默认）
├── tests/
│   └── test_routing.py         回归测试（16 项）
└── templates/
    ├── INDEX.md                58 个模板索引
    ├── snapshot.json           模板快照元数据（版本/日期/校验和）
    ├── component-map.json      109 个原子组件 → 5 种目标库
    ├── pages/*.txt             58 个布局骨架
    ├── styles.json.gz          143 种设计风格离线快照（luckymaomi/ui，MIT）
    └── styles-snapshot.json    风格快照元数据（来源/日期/校验和）
```

## 选型依据

表内数字为 2026-11 实测，可复现：

```bash
curl -s "https://api.npmjs.org/downloads/point/last-week/naive-ui"
curl -s "https://api.github.com/repos/tusen-ai/naive-ui"
```

**Vue 生态**

| 库 | 周下载 | 星数 | 开箱好看 | 上手 |
|---|---|---|---|---|
| Vuetify | 1,310,471 | 41,033 | 中（Material） | 中 |
| PrimeVue | 1,043,015 | 14,452 | 中上 | 中 |
| Element Plus | 797,315 | 27,845 | 中上 | 最易 |
| ant-design-vue | 311,430 | 21,709 | 中上 | 中 |
| **Naive UI** | 197,042 | 18,607 | **最高** | 易 |
| shadcn-vue | 135,301 | 10,794 | 高（可定制） | 难 |

**React 生态**

| 库 | 周下载 | 开箱好看 | 备注 |
|---|---|---|---|
| MUI | 13,836,129 | 中（Material） | 生态第一 |
| antd | 5,359,099 | 中上 | 国内企业后台标准 |
| astryx | 661,968 | **最高** | 要求 React ≥19，**Beta** |

> **关于 astryx**：仓库 2026-01 建仓，版本 0.7.11，README 自述 "Currently in Beta"。好看主要来自模板而非组件本身。做原型值得选，长期生产项目需权衡 API 变动风险。

## 许可证

MIT。含两个第三方数据来源，均 MIT，完整归因见 [LICENSE](LICENSE)：

- 页面模板骨架：[meta/astryx](https://github.com/meta/astryx)，版权归 Meta Platforms, Inc.
- 设计风格库：[luckymaomi/ui](https://github.com/luckymaomi/ui)，143 种风格规则与组件配方

## 贡献

选型数据会过时。若发现数字不准，请附上实测命令与输出更新 `SKILL.md` 与 `scripts/route_stack.py`。
