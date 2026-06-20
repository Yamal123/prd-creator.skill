# prd-creator

用模板 HTML 生成产品需求页面。skill 负责：**扫描项目 → 收集信息 → 生成/索引章节内容 → 管理配置文件**，不修改 HTML 模板源码。

## 触发

"生成 PRD 页面""创建产品需求网页""prd-creator" "更新 PRD""删除 PRD"

## 操作模式

执行前先判断用户意图，选择对应模式：

### 模式 A：新建 PRD

项目中没有 `prd/` 目录或 `prd/config.json` 时触发。完整走 1→7 流程。

### 模式 B：更新 PRD

项目已有 PRD，用户要求更新内容。规范：

1. **不重新复制 HTML 模板**（除非用户明确说「重新部署模板」「更新模板」）
2. 读取现有 config.json 保留所有字段（meta/brand/cards/tabs/footer）
3. 扫描 `tabs/` 目录更新 files 索引（保持 `{file, label}` 对象格式）
4. 扫描项目新代码/文档，检查是否有新增模块可生成章节
5. 新增 Tab 追加到 tabs.files 和 tabs/，不覆盖已有 .md
6. 无新内容时仅做 config.json tabs.files 与 tabs/ 目录的一致性校验

### 模式 C：重新生成 PRD

用户要求完全重建。按新建流程走 1→7，但保留 HTML 模板不重复复制（除非用户明确要求）。config.json 和 tabs/ 全部重建。

### 模式 D：删除 PRD

用户要求删除。删除 `prd/` 整个目录，提醒用户确认后执行。不做多余操作。

## PRD 章节框架（22 章）

| 编号 | 章节 | 层 | 用途 | 数据来源 |
|---|---|---|---|---|
| 01 | 项目背景 | 叙事 | 为什么做 | README + 用户输入 + 已有 PRD |
| 02 | 技术路线 | 叙事 | 怎么做 | ARCHITECTURE + package.json + FLOWS + 配置文件 |
| 03 | 功能介绍 | 叙事 | 有什么能力 | 页面路由 + 组件树 + tRPC 路由 |
| 04 | 用户场景 | 叙事 | 谁怎么用 | 用户输入 + 已有用户故事 |
| 05-16 | 需求详述 | 执行 | 每个功能点细节 | 模块代码 + 已有文档 + 用户补充 |
| 17 | 非功能性需求 | 执行 | 性能/安全/可用性要求 | 技术栈推断 + 用户输入 |
| 18 | 数据设计 | 支撑 | 核心数据模型 | drizzle/schema 文件 + migration 文件 |
| 19 | 验收标准 | 支撑 | 上线依据 | 从 05-15 提取 + 用户确认 |
| 20 | 项目计划 | 支撑 | 进度与待办 | TODO.md + Git log + 用户输入 |
| 21 | 度量体系 | 支撑 | 产品指标 | 用户输入 + 埋点代码 |
| 22 | 附件 | 支撑 | 引用索引 | docs/grep 扫描 + 术语提取 |

## 流程

### 1. 部署模板（仅新建 / 重新生成且用户要求时）

```bash
git clone https://github.com/Yamal123/prd-creator.skill.git /tmp/prd-template
mkdir -p prd/tabs prd/manager
cp /tmp/prd-template/index.html prd/
cp /tmp/prd-template/manager/index.html prd/manager/
cp /tmp/prd-template/manager/server.py prd/manager/
cp /tmp/prd-template/manager/start.py prd/manager/
rm -rf /tmp/prd-template
```

### 2. 信息采集

**阶段一：自动扫描项目（无需用户参与）**

| 扫描目标 | 方法 | 用途 |
|---|---|---|
| 项目定位 | 读取 README.md h1 + 第一段 | 01 项目背景 |
| 技术栈 | 读取 package.json dependencies + tsconfig + vite.config | 02 技术路线 |
| 页面路由 | 扫描 client/src/pages/ 目录树 + wouter Route 定义 | 03 功能介绍 + pages.json |
| API 路由 | 扫描 server/routers.ts 或 tRPC router 定义 | 03 功能介绍 |
| 数据库 Schema | 扫描 drizzle/schema.ts 或 migrations/ | 17 数据设计 |
| 已有文档 | Glob: `docs/**/*.md`, `*.md`, `README*` | 全部章节 |
| 标签信息 | package.json version + git log -1 --format='%an' + git log -1 --format='%ci' | meta.tags（版本/作者/日期） |
| 流程图 | Glob: `**/*.mermaid`, `docs/FLOWS/**` | 02 技术路线 |
| 待办项 | 读取 TODO.md, todo.md | 19 项目计划 |
| Git 历史 | `git log --oneline -30` | 04 演化轨迹 |

**阶段二：收集业务信息（AskUserQuestion，2 轮）**

第一轮（4 问）— 产品基础：产品名称+定位、产品标签、品牌色、核心功能点

第二轮（4 问）— 业务深度：核心角色、用户场景、非功能需求、项目阶段

### 3. 生成 config.json

写入 `prd/config.json`。关键字段：

- `meta.tags`：`["版本号", "作者", "更新日期"]` — 从 package.json + git log 自动提取
- `tabs.files`：`{file, label}` 对象格式，按编号排序
- `tabs.groups`：多级菜单分组，将多个 Tab 折叠到下拉菜单
- `tabs.extra`：pages 类型的附加 Tab

```json
{
  "meta": { "title": "", "subtitle": "", "tags": ["v1.0", "作者", "2026-01-01"], "logo": {"type":"svg","value":"<svg...</svg>"} },
  "brand": { "primary": "#E31E24", "light": "#FDEBEC", "dark": "#B3151A" },
  "fonts": { "display": "Playfair Display", "body": "Inter", "mono": "JetBrains Mono" },
  "cards": [{ "icon": "document", "title": "", "description": "" }],
  "tabs": {
    "folder": "tabs",
    "groups": { "需求详述": ["05-模块A", "06-模块B"] },
    "files": [
      { "file": "tabs/01-项目背景.md", "label": "项目背景" }
    ],
    "extra": [
      { "id": "pages", "label": "页面地图", "type": "pages", "file": "pages.json" }
    ]
  },
  "footer": { "text": "" }
}
```

card icons: loop/sse/knowledge/memory/human/evolve/document/chart/cube/module/import/clock

### 4. 生成章节内容

**命名规则**：`01-项目背景.md` — 数字前缀控制顺序，中文 slug 自动派生 label。

**每章约束**：h1 标题 + 至少 2 个 h2 章节。

**生成策略**：
- 已有项目文档 → 在 tab .md 顶部标注 `> 关联文档: [标题](../路径)` 索引，不全量复制
- 代码扫描可推断的内容 → 自动填充表格和数据
- 需要用户输入的内容 → 标注 `> 待确认: 具体问题`
- 无法确认的内容 → 留空不编造

各章具体内容要求见 PRD 框架表。

### 5. 生成 pages.json

```json
{
  "sections": [
    { "title": "分组名", "cards": [
      { "title": "页面", "description": "", "tags": ["关键词"], "iconType": "chat", "link": "/admin/xxx" }
    ]}
  ]
}
```

- `link`：项目真实路由，不写 `#`；`tags`：核心关键词；`iconType`：chat/admin/kb/agent/ws

### 6. 完成

```bash
cd prd/ && python3 manager/start.py
```

访问 `/prd/`，后台 `/prd/manager/`。
