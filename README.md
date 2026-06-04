<p align="center">
  <img src="assets/lore-icon.png" width="180" alt="Lore Logo" />
</p>

<h1 align="center">Lore</h1>

<p align="center">
  <b>项目经验框架</b> — 让 AI Agent 在项目中积累、检索和淘汰工程经验。
</p>

<p align="center">
  <b>简体中文</b> | <a href="README.en.md">English</a>
</p>

---

## 为什么需要 Lore

AI 编码 Agent 跨会话是无状态的。每次新对话，Agent 都会忘记：

- 你已经修过什么 bug、怎么修的
- 做过什么架构决策、为什么这样做
- 这个项目有什么特有的工程模式
- 哪些坑需要避免

| 方案 | 做了什么 | 缺什么 |
|------|---------|--------|
| CLAUDE.md / AGENTS.md | 全局行为规则 | 没有项目级经验，没有生命周期 |
| Agent 记忆（auto-memory） | 用户偏好 | 绑定 Agent 不绑定项目，平铺结构 |
| Trellis | 完整工作流管理 | 太重，控制整个开发过程 |
| Skills | 可复用操作流程 | 不积累知识，没有验证机制 |

**Lore 填补的空白**：项目级、经过验证、有生命周期管理的工程经验。

Lore 是一个目录约定（`.lore/`），为 AI Agent 提供一个结构化的地方来管理项目级工程经验。它不依赖任何特定平台——任何能读文件的 LLM 都能用（Claude Code、Codex、Gemini、Cursor 等）。

---

## 快速开始

### 第一步：初始化

进入你的项目根目录，运行：

```bash
# Bash / Zsh / Git Bash
curl -fsSL https://raw.githubusercontent.com/LS-plan/lore/main/scripts/init.sh | bash
```

```powershell
# PowerShell
irm https://raw.githubusercontent.com/LS-plan/lore/main/scripts/init.ps1 | iex
```

或者手动复制：

```bash
git clone https://github.com/LS-plan/lore.git /tmp/lore
cp -r /tmp/lore/template/.lore .lore
rm -rf /tmp/lore
```

### 第二步：填写项目信息

编辑 `.lore/identity.md`，写入你的项目名称、技术栈和当前阶段：

```markdown
## Basics
- **Project**: my-awesome-app
- **Tech stack**: Python / FastAPI / Docker / PostgreSQL

## Phase
- **Current phase**: exploration
```

### 第三步：注入到你的 Agent 平台

从 `.lore/_adapters/` 中复制对应平台的片段到你的配置文件：

| 平台 | 配置文件 | 适配器 |
|------|---------|--------|
| Claude Code | `CLAUDE.md` | `.lore/_adapters/claude-code.md` |
| Codex | `AGENTS.md` | `.lore/_adapters/codex.md` |
| Cursor | `.cursor/rules` | `.lore/_adapters/cursor.md` |
| Gemini | `.gemini/` | `.lore/_adapters/gemini.md` |

也可以直接在项目的 `CLAUDE.md`（或对应文件）中加一段：

```markdown
## 项目经验框架 (Lore)

本项目使用 Lore 管理工程经验。
启动时读 `.lore/INDEX.md`，按任务关键词决定是否加载深层内容。
任务后如有已验证经验，写入 `.lore/experiences/` 并更新索引。
循环保护：同一经验加载 2 次仍未解决问题时，停止并报告用户。
```

### 第四步：开始使用

正常工作就行。Agent 会在每次会话开始时读 `.lore/INDEX.md`，按需加载相关经验。

---

## 安装后 LLM 的预期行为

安装 Lore 后，AI Agent 在会话中应当表现出以下行为模式：

### 首次接触项目

- **自动形成项目理解**：Agent 首次接触包含 `.lore/` 的项目时，默认先读取 `identity.md`、`INDEX.md`、`glossary.md` 等文件，主动建立对项目的全局理解——不需要用户额外授权或确认这一步
- **自动识别项目信息**：项目名称、技术栈等应从 `.lore/identity.md` 和项目目录结构中主动识别，而非反复询问用户

### 执行任务

- **计划先行**：用户提出一个诉求后，Agent 先给出完整的计划（包括涉及的文件、步骤、可能命中的工程经验），然后针对需要用户确认的具体细节（比如是否初始化 git、是否创建新目录等）逐一确认
- **经验命中提示**：当任务命中了某条已有工程经验时，在计划中引用该经验并简要说明
- **渐进式确认**：对于细节问题，逐步确认直到形成完整理解，而不是一次性抛出大量问题

### 防止停滞

- **主动推进**：如果连续几轮对话进展不明显（比如反复确认同一个问题、或用户没有给出明确指示），Agent 应主动询问："要不要先按当前理解开始做？后续可以再调整。"
- **不过度设计**：不在细节上纠缠，不预设过多假想需求。先做出来能用的版本，后续迭代优化

### 经验写入

- **任务完成后自省**：任务做完后，Agent 应判断是否产生了值得记录的工程经验
- **不记录琐碎操作**：一次性操作（改文案、调参数）不写入 `experiences/`
- **必须有验证依据**：development 阶段新经验必须附带验证方式

---

## 经验文件怎么写

每个经验是 `.lore/experiences/` 下的一个 Markdown 文件：

```markdown
---
id: docker-volume-vs-bake
triggers:
  - "修改了宿主机文件但容器没变化"
  - "docker restart 后改动丢失"
scope: [Docker, 部署]
verified: 2026-06-03
status: active
impact: medium
author: generated
reviewed: false
---

# Docker 容器：volume mount vs baked image

## 症状
修改了宿主机上的代码文件，但 Docker 容器内没有任何变化。

## 根因
代码在 docker build 时被 COPY 进了镜像。宿主机文件和容器内文件是独立副本。

## 解决
在 docker-compose.yml 中添加 volume mount。

## 验证方式
修改宿主机文件 → docker compose up -d → 进入容器确认文件已更新。
```

关键字段说明：
- `triggers`：触发条件——Agent 靠这些关键词判断是否需要加载
- `status`：`active`（活跃）/ `stale`（过期）/ `archived`（归档）
- `impact`：`low` / `medium` / `high` / `critical`
- `author`：`authored`（人工编写）/ `generated`（Agent 生成）
- `reviewed`：是否经过人工审核

完整格式说明见 [docs/experience-format.md](docs/experience-format.md)。

---

## 目录结构

```
.lore/
├── INDEX.md              # 根索引——Agent 每次启动时唯一必读的文件
├── identity.md           # 项目身份：名称、技术栈、约束、阶段
├── glossary.md           # 领域术语表
├── domain/               # 领域知识
│   ├── INDEX.md
│   └── <topic>.md
├── experiences/          # 已验证的工程经验
│   ├── INDEX.md
│   └── <experience>.md
├── decisions/            # 架构决策记录（ADR）
│   └── <NNNN>-<slug>.md
├── patterns/             # 稳定工程模式（从经验晋升）
│   ├── INDEX.md
│   └── <pattern>.md
├── runs/                 # 任务运行日志（临时证据）
│   └── <date>-<task>.yaml
└── _adapters/            # 各平台的注入配置片段
    ├── claude-code.md
    ├── codex.md
    ├── cursor.md
    └── gemini.md
```

| 目录 | 存什么 | 生命周期 |
|------|--------|---------|
| `identity.md` | 项目技术栈、约束、当前阶段 | 长期，偶尔更新 |
| `glossary.md` | 领域术语定义 | 长期，持续积累 |
| `domain/` | 领域知识（业务逻辑、协议细节） | 长期 |
| `experiences/` | 已验证的工程经验 | 中期，可能过期 |
| `decisions/` | 架构决策记录 | 长期 |
| `patterns/` | 稳定工程模式 | 长期 |
| `runs/` | 任务运行日志 | 短期（30 天清理） |

---

## 两个阶段

### Exploration（探索阶段）

项目早期，或 Agent 首次接触项目时。在 `identity.md` 中设置 `phase: exploration`。

- Agent 主动写入 `domain/`、`glossary.md`、`experiences/`
- 写入门槛低——有价值的观察先记录，后续人工审核
- 生成的条目标记 `reviewed: false`

### Development（开发阶段）

项目成熟，经验库已有积累。在 `identity.md` 中设置 `phase: development`。

- Agent 主要读取，选择性写入
- 未验证的观察只进 `runs/`，不直接进 `experiences/`
- 新经验必须有验证证据
- 生命周期规则（过期 / 归档）主动执行

通常在项目有 5 条以上 verified experience 且 `domain/` 覆盖了核心领域后，可以切换到 development。

---

## 经验生命周期（PDCA）

```
观察 / 猜测
    ↓
runs/ (临时运行日志，30 天清理)
    ↓  [验证通过 + 可复用]
experiences/ (已验证经验，status: active)
    ↓  [3+ 次使用，成功率 > 80%，人工审核通过]
patterns/ (稳定工程模式)
    ↓  [进一步固化为可执行流程]
成为独立 Skill

反向淘汰：
  90 天未使用 → status: stale
  再 90 天仍未使用 → status: archived
  有替代方案 → 直接 archived
  impact: critical → 豁免自动过期
```

---

## 内置保护机制

| 机制 | 规则 |
|------|------|
| **循环保护** | 同一经验加载 2 次仍未解决问题 → 停止，向用户报告 |
| **写入门控** | development 阶段：未验证条目不能进 `experiences/` |
| **加载上限** | 每次任务最多加载 5 条经验（按 impact 排序） |
| **索引一致性** | 每次增删经验后必须更新索引 |
| **自审禁止** | Agent 不能对自己生成的条目设置 `reviewed: true` |

---

## 人工维护

| 操作 | 频率 | 做什么 |
|------|------|--------|
| **审核** | 每周 | 看 `experiences/` 中 `reviewed: false` 的条目，确认准确性 |
| **晋升** | 有空时 | 将反复使用的经验提升到 `patterns/` |
| **清理** | 每月 | 删除 `runs/` 中 30 天以上的日志 |
| **归档** | 季度 | 将 `status: stale` 的经验归档或删除 |

---

## 文档

- [经验文件格式](docs/experience-format.md) — frontmatter 字段、正文结构、生命周期规则
- [架构决策记录格式](docs/decision-format.md) — 何时创建 ADR、模板和编号规则

## 许可证

MIT
