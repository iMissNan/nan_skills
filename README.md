# nan_skills

一组给 AI 编码助手用的技能（skills）。每个技能独立成目录，可单独使用，也可整个仓库克隆后按需取用。

## 技能列表

| 技能 | 用途 | 状态 |
|---|---|---|
| [`ui-stack-router`](skills/ui-stack-router/) | 做前端界面时选对 UI 组件库与页面模板，再写代码 | ✅ 可用 |

> 新技能会陆续加入 `skills/` 目录。

## 安装

本仓库采用**标准 skill 目录结构**，每个子目录都是一个独立的技能。

### 方式一：整个仓库安装（推荐）

```bash
git clone <本仓库地址> nan_skills
mkdir -p ~/.zcode/skills
cp -r nan_skills/skills/* ~/.zcode/skills/
```

### 方式二：只装某个技能

```bash
mkdir -p ~/.zcode/skills
cp -r nan_skills/skills/ui-stack-router ~/.zcode/skills/
```

安装后**重启客户端**，技能列表里会出现。

### 其他客户端

技能是标准 `SKILL.md` 目录，放在你所用工具的 skills 根目录即可：

| 客户端 | 技能根目录 |
|---|---|
| ZCode | `~/.zcode/skills/` |
| Claude Code | `~/.claude/skills/` |
| 通用约定 | `~/.agents/skills/` |

## 仓库结构

```
nan_skills/
├── README.md
├── LICENSE
├── .gitignore
└── skills/
    └── ui-stack-router/
        ├── SKILL.md
        ├── LICENSE
        ├── README.md
        ├── scripts/
        └── templates/
```

新增技能时，在 `skills/` 下新建一个目录，放入 `SKILL.md` 即可，其余技能不受影响。

## 技能设计约定

本仓库的技能遵循几条共同原则：

1. **离线可用** — 运行时零网络请求，需要的资料随包分发。
2. **无重依赖** — 优先纯标准库 / 零外部依赖。
3. **不改用户仓库** — 需要写文件的动作默认 dry-run，且需用户明确同意。
4. **如实标注限制** — 数据快照的时间、已知不足都写清楚，不夸大能力。

## 许可证

MIT。各技能目录内若含第三方内容，其归因见该技能下的 `LICENSE`。

## English

A collection of agent skills. Each directory under `skills/` is a standalone skill with a standard `SKILL.md`. Clone and copy into your client's skills directory.

First skill: **ui-stack-router** — picks the right UI library and page template for a frontend task before writing code. Supports new projects with no stack yet.
