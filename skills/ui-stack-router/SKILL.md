---
name: ui-stack-router
description: >
  做前端界面时选定 UI 组件库与页面模板，再写代码。新项目（还没有技术栈）
  和已有项目都适用：新项目直接用默认组合开工，已有项目先读 package.json
  再定库。当用户要做界面、改样式、美化页面、觉得 UI 难看或像 AI 生成时使用；
  也用于组件库与框架不匹配、或多个模板不知道选哪个的情况。内含 57 个页面
  模板骨架与 108 个组件到多框架的映射表，避免从零手写页面。
---

# UI 技术栈路由

先判断框架，再选库。**框架未知时不得推荐任何组件库。**

## 为什么需要这个 skill

UI 组件库与框架绑定。React 组件库无法在 Vue 项目中使用：JSX 是内嵌在
JavaScript 里的标记，而 Vue 使用 `.vue` 单文件组件与 `<template>` 语法，
两者无法互相调用。所以"用哪个 UI 库"这个问题，在"用什么框架"有答案之前
根本不存在答案。

两个必须分清的类别：

- **组件库**（`@astryxdesign/core`、`naive-ui`）：附带编译好的 CSS 和现成
  组件。不写自定义 CSS 就是好看的。**非设计背景的用户应该用这个。**
- **设计规则库**（`ui-ux-pro-max`）：只有 CSV 指导文本，**零 CSS、零组件**。
  它能提升 agent 手写代码的质量，但本身产不出任何可渲染的东西。
  **不要把它当成组件库的替代品。**

对用户描述时，绝不要把规则库称作"设计系统"，也绝不要说装了规则库就能
达到组件库演示站的效果。

## 工作流程

> **脚本路径约定**：下文所有 `SKILL_DIR` 指本 skill 所在目录。按安装方式展开：
>
> - 作为用户级 skill 安装：`~/.zcode/skills/ui-stack-router`
> - 作为插件安装：`${CLAUDE_PLUGIN_ROOT}/skills/ui-stack-router`
>
> 先确认脚本存在再执行。若路径不符，从 `SKILL.md` 所在目录向上查找同级
> `scripts/` 目录，而不是猜测绝对路径。

### 第一步：判断项目状态

```bash
python "$SKILL_DIR/scripts/route_stack.py" "<项目目录>"
```

输出 JSON，含 `detected` 与 `plan`。`plan.decision` 字段即指令：

| `plan.decision` | 含义 |
| --- | --- |
| `reuse_existing` | `package.json` 里已有 UI 库。直接用它，**不要新增第二个**。 |
| `install_primary` | 未发现 UI 库。安装 `plan.primary`。 |
| `greenfield` | **新项目，还没有技术栈。直接开工，不用追问。** |

**`greenfield` 是本 skill 最重要的分支**，处理不好就会卡住用户。

用户说"我要做一个 XX 系统/页面，要好看"，而目录是空的或不存在时：

- **不要**反问"你用什么框架"。用户来问设计，正是因为他不想操心技术选型。
- **直接**采用 `plan.starter` 给出的默认组合（Vue 3 + Vite + Naive UI），
  一句话同步给用户："我先用 Vue 3 + Naive UI 起，样式最省事，你要换随时说。"
- 然后**立刻进入第二、三步**选模板、定设计。技术细节后置。

只有当用户**主动**说了框架（"我要用 React"）时，才按该框架走。

```bash
# 用户已明确框架时
python "$SKILL_DIR/scripts/route_stack.py" --framework vue
```

### 第二步：按数据选型，不许凭印象

选型必须依据下面这张表。表内数字为 2026-11 实测的 npm 周下载量与
GitHub 星数；若表与实测不符，以实测为准，并更新本表。

**Vue 生态**

| 库 | 周下载 | 星数 | 开箱好看 | 上手 | 定位 |
| --- | --- | --- | --- | --- | --- |
| Vuetify | 1,310,471 | 41,033 | 中（Material） | 中 | 生态最强，稳妥 |
| Element Plus | 797,315 | 27,845 | 中上 | 最易 | 国内后台事实标准，中文文档全 |
| PrimeVue | 1,043,015 | 14,452 | 中上 | 中 | 组件最全 |
| **Naive UI** | 197,042 | 18,607 | **最高** | 易 | **追求精致感首选** |
| shadcn-vue | 135,301 | 10,794 | 高（可定制） | 难 | 要独特设计，需调 |
| ant-design-vue | 311,430 | 21,709 | 中上 | 中 | 国内团队熟悉 antd 时 |

**React 生态**

| 库 | 周下载 | 开箱好看 | 定位 |
| --- | --- | --- | --- |
| MUI | 13,836,129 | 中（Material） | 生态绝对第一 |
| antd | 5,359,099 | 中上 | 国内企业后台事实标准 |
| **astryx** | 661,968 | **最高** | Meta 出品，150+ 组件 + 预编译 CSS + **768 个页面/区块模板**，另有 agent CLI。要求 React ≥19 |

**关于 astryx 的成熟度，必须告知用户**：仓库 2026-01 建仓（约 10 个月），版本
0.7.11，README 自述 "Currently in Beta"。周下载量约为 MUI 的 1/21。它的好看很大
程度来自**附带的 768 个免费页面模板**，而非组件本身更美。用于长期维护的生产
项目有 API 变动与资料稀少的风险；做原型、内部工具、追求视觉质感时值得选。

**不要把"好看"当作唯一理由推荐 astryx**，必须同时说明 Beta 状态与生态差距。

**其他**

| 框架 | 首选 | 周下载 | 备注 |
| --- | --- | --- | --- |
| Svelte | shadcn-svelte | 300,511 | 也可用 `@skeletonlabs/skeleton`（93,565） |
| Angular | @angular/material | — | `ng add @angular/material` |
| uni-app / 小程序 | uview-plus | — | Web 组件库在端内跑不了 |
| 无框架 / 纯 HTML | 不装库 | — | 用 Tailwind + 设计 token |

**选型的默认判断顺序**（用户未指定偏好时）：

1. 项目已有 UI 库 → **复用，不新增**（`reuse_existing`）
2. 要开箱精致、非专业设计 → **Naive UI**（Vue）/ **astryx**（React）
3. 要生态成熟、出问题能搜到答案 → Vuetify 或 Element Plus（Vue）/ MUI 或 antd（React）
4. 要独特视觉、愿意调 → shadcn 系

**明说取舍**：astryx 在 React 里开箱最精致，但下载量只有 MUI 的 1/21，属"新贵"
而非"主流"。推荐它时必须同时告知这一点，让用户自己选，不许只用"好看"一个
理由搪塞。

### 第三步：先套页面模板，再写代码

**这是本 skill 的核心。** 组件库只给零件，页面长什么样取决于布局决策。不做这
一步，出来的就是"能跑但平庸"的页面 —— 这也是 AI 生成 UI 显丑的真正原因。

astryx 之所以开箱好看，不是因为组件更美，而是它附带 **57 个页面模板 + 711 个
区块模板**（免费，一条命令生成）。MUI、Naive UI、Element Plus 都**不带页面
模板**，只发组件。所以这里把 astryx 的模板骨架抽成了离线库，供任意框架使用。

**骨架是框架无关的**：只有布局结构与间距数值（`padding`、`gap`、嵌套层级），
不含任何 React 语法。

**按产品类型选模板：**

```bash
python "$SKILL_DIR/scripts/pick_template.py" "<产品描述>" --library <naive-ui|element-plus|mui|shadcn|html>
```

输出 `chosen`（选中模板）、`alternatives`（备选）、`skeleton`（原始骨架）、
`translated`（已按目标库翻译组件名的骨架）。中文查询可直接用，如
"后台管理系统"、"做个登录页"、"报表页"、"看板"。

**查看全部 57 个模板：**

```bash
python "$SKILL_DIR/scripts/pick_template.py" --list
```

**模板清单见** `templates/INDEX.md`；**组件映射表见**
`templates/component-map.json`（108 个原子组件 → 5 种目标库）。

映射表覆盖布局、排版、表单、数据、导航、浮层六类原子组件。剩余约 70 个是模板
自定义的复合件（`MetricCard`、`ActiveUsersChart`、`BoardCard` 等），按骨架里的
角色自行实现。

**落地顺序：**

1. 选模板 → 拿到骨架
2. 照骨架的**嵌套层级和 gap/padding 数值**搭结构，不要自己重新设计间距
3. 把骨架里的组件名换成目标库的对应组件（用 `component-map.json`）
4. 再套第四步选定风格的配色与 token
5. 最后填真实内容

**不许跳步**：直接从零手写页面，等于放弃模板带来的全部布局质量。

### 第四步：拿设计方向（风格与配色）

本 skill 内置**离线风格库**：143 种设计风格（来源
[luckymaomi/ui](https://github.com/luckymaomi/ui)，MIT），每种含中文说明、配色、
AI 实现规则、设计 token 和组件配方（Tailwind 实现）。运行时零网络。

**按产品气质选风格：**

```bash
python "$SKILL_DIR/scripts/search_style.py" "<气质或产品关键词>"
# 例：拟物 / 玻璃 / 极简 / dashboard / skeuomorphism / 温暖
```

返回命中风格列表。选定后取完整条目：

```bash
python "$SKILL_DIR/scripts/search_style.py" --slug <风格id>
```

完整条目包含：

| 字段 | 用途 |
| --- | --- |
| `aiRules` | **该风格的 AI 实现规则**（必读：绝对禁止/必须遵守/光影/动效） |
| `colors` | 主色、次色、强调色 hex |
| `tokens` | border / shadow / interaction / typography / spacing 令牌 |
| `recipe` | button / card / input 等组件的 Tailwind 类配方（骨架+变体+状态） |
| `doList` / `dontList` | 该风格该做与不该做 |
| `examplePrompts` | 示例提示词 |

**风格选择规则：**

1. 用户点名风格（"要拟物"、"要玻璃拟态"）→ 直接 `--slug` 取用。
2. 用户没点名 → 用产品关键词搜，**取第一名前先向用户确认气质方向**，
   报出 2-3 个候选（中文名 + 一句话）让用户挑。
3. 风格决定的是视觉语言，组件库决定的是实现手段，**两者叠加使用**：
   配色取 `colors`，间距圆角取 `tokens`，组件细节参考 `recipe` 的类名，
   再落到所选组件库上。

**可选补充**：`ui-ux-pro-max` 技能（若安装）可提供字体搭配与 UX 规则清单，
与本风格库互补。`route_stack.py` 输出的 `plan.design_search_available` 指示其
是否可用；未安装时跳过即可，风格库已够用。

```bash
python "$UIUX_SKILL/scripts/search.py" "<产品关键词>" --design-system -p "<项目名>"
```

### 第五步：用库写，不要手搓

让结果看起来像"设计过"而不是"生成出来"的规则：

- 用库的组件与布局原语组合。已有 `Card`、`NCard`、`VStack`、`Grid` 时，
  手写带 padding 的裸 `<div>` 属于缺陷。
- 间距、颜色、圆角、字号来自主题 token 或组件 props，不许自造 `#hex`
  和随意 `px`。
- 库有主题对象时（naive-ui 的 `themeOverrides`、astryx 的 theme），
  **改主题**，不要逐个组件覆写样式。
- 把第四步选定的风格（配色、token、组件配方）映射进库的主题，而不是绕开库另写一套。

## 模板快照与更新

模板骨架是**随包的离线快照**（`templates/pages/`），运行时零网络，断网可用。
来源与版本记录在 `templates/snapshot.json`。

**日常使用不需要更新**，快照已足够。仅在以下情况处理：

- 用户明确问"模板是不是最新"或要求更新；
- 用户报告某个模板缺失、或与 astryx 官网示例明显不符。

**检查是否有新版：**

```bash
python "$SKILL_DIR/scripts/update_templates.py" --check
```

输出含 `version_drift`（版本是否落后）、`local_matches_snapshot`（内容是否被
改动）、`template_count_local` 与 `template_count_upstream`。

**更新模板**（默认 dry-run，**必须得到用户同意后才加 `--write`**）：

```bash
python "$SKILL_DIR/scripts/update_templates.py"            # 干跑，不写盘
python "$SKILL_DIR/scripts/update_templates.py" --write    # 实际写入
```

**规则：**

1. 不要主动更新模板。它是用户仓库里的文件，改动会进入版本控制。
2. 更新需要 Node 与网络（会调用 astryx CLI）。缺任一条件时告知用户，不要自行安装。
3. 更新后 `INDEX.md` 与 `snapshot.json` 会一并重新生成，属预期行为。
4. 更新是幂等的：同版本重跑不产生差异。

## 向用户汇报

用中文说明：探测到的框架、选用的库、是否项目里已装。用户误以为某库能用
但实际不行时，直说原因是框架边界，不是配置失误，并给出该栈的等价库。

选型涉及取舍时（如 astryx 精致但小众），把取舍讲清楚。

## 适用范围

后端、数据库、API、基础设施、非可视化脚本不适用。只要交付物含用户界面
就适用。
