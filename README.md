# Lore

**项目经验框架** — 让 AI Agent 在项目中积累、检索和淘汰工程经验。

Lore 是一个目录约定（`.lore/`），为 AI Agent 提供一个结构化的地方来管理项目级工程经验。它不依赖任何特定平台——任何能读文件的 LLM 都能用（Claude Code、Codex、Gemini、Cursor 等）。

## 为什么需要 Lore

AI 编码 Agent 跨会话是无状态的。每次新对话，Agent 都会忘记：

- 你已经修过什么 bug、怎么修的
- 做过什么架构决策、为什么这样做
- 这个项目有什么特有的工程模式
- 哪些坑需要避免

现有方案各有局限：

| 方案 | 做了什么 | 缺什么 |
|------|---------|--------|
| CLAUDE.md / AGENTS.md | 全局行为规则 | 没有项目级经验，没有生命周期 |
| Agent 记忆（auto-memory） | 用户偏好 | 绑定 Agent 不绑定项目，平铺结构 |
| Trellis | 完整工作流管理 | 太重，控制整个开发过程 |
| Skills | 可复用操作流程 | 不积累知识，没有验证机制 |

**Lore 填补的空白**：项目级、经过验证、有生命周期管理的工程经验。

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

## 使用指南

### 日常工作流

```
1. Agent 启动 → 读 .lore/INDEX.md
2. 匹配当前任务关键词 → 决定加载哪些经验
3. 执行任务，应用已有经验
4. 任务完成后 →
   - 发现了新的可复用经验？写入 experiences/，更新索引
   - 只是一次性操作？不写入
   - 遇到了问题但没解决？记录到 runs/
```

### 写入经验的时机

**应该写入**（到 `experiences/`）：
- 修了一个非显而易见的 bug，下次可能再遇到
- 发现了项目特有的部署坑
- 找到了某个工具的正确使用姿势
- 解决了一个配置问题，有明确的验证方式

**不应该写入**：
- 一次性操作（改个文案、调个参数）
- 未验证的猜测
- 通用编程知识（Agent 已经知道）
- 用户个人偏好（那是 Agent 级记忆的事）

### 经验文件怎么写

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

### 人工维护

Agent 会自动写入和使用经验，但人工需要定期做几件事：

| 操作 | 频率 | 做什么 |
|------|------|--------|
| **审核** | 每周 | 看 `experiences/` 中 `reviewed: false` 的条目，确认准确性 |
| **晋升** | 有空时 | 将反复使用的经验提升到 `patterns/` |
| **清理** | 每月 | 删除 `runs/` 中 30 天以上的日志 |
| **归档** | 季度 | 将 `status: stale` 的经验归档或删除 |

---

## 目录结构

```
.lore/
├── INDEX.md              # 根索引——Agent 每次启动时唯一必读的文件
├── identity.md           # 项目身份：名称、技术栈、约束、阶段
├── glossary.md           # 领域术语表
├── domain/               # 领域知识
│   ├── INDEX.md          # 领域知识索引
│   └── <topic>.md        # 具体领域知识
├── experiences/          # 已验证的工程经验
│   ├── INDEX.md          # 经验索引（触发条件 + 一行摘要）
│   └── <experience>.md   # 单条经验
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

各目录职责：

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

## 跨平台兼容

Lore 只是文件。任何能读 Markdown 的 LLM 都能用。平台专属的注入片段在 `.lore/_adapters/` 中——复制对应的到你平台的配置文件即可。

---

## 文档

- [经验文件格式](docs/experience-format.md) — frontmatter 字段、正文结构、生命周期规则
- [架构决策记录格式](docs/decision-format.md) — 何时创建 ADR、模板和编号规则

## 许可证

MIT
