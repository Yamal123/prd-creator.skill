# 产品需求介绍 — HTML 模板

## 概述

一个用于产品需求介绍的 HTML 网页模板。核心特性：页面打开后自动加载同目录下的 Markdown 文件或 JSON 配置文件，渲染为结构化的产品文档页面。

**适用场景**：产品需求文档、技术方案说明、项目导航页、PRD 演示。

## 文件结构

```
产品需求模板/
├── index.html          # 主页面
├── config.json         # 页面配置（标题/卡片/Tab/品牌色）
├── flowchart.md        # Tab1：流程图（示例）
├── architecture.md     # Tab2：架构图（示例）
├── pages.json          # Tab3：前端页面卡片配置（示例）
├── features.md         # Tab4：功能说明（示例）
├── README.md           # 本文件
└── manager/            # Python 可视化管理客户端
    ├── main.py         # 入口
    ├── app.py          # 主窗口
    ├── data.py         # 数据读写
    ├── server.py       # HTTP 服务器
    ├── preview_window.py  # pywebview 预览
    ├── requirements.txt
    └── ui/
        ├── metadata_panel.py   # 元数据面板
        ├── cards_panel.py      # 首页卡片面板
        ├── tabs_panel.py       # Tab 管理面板
        ├── brand_panel.py      # 品牌色面板
        └── content_editor.py   # 内容编辑器
```

## 快速开始

### 方式一：本地服务器（推荐）

由于浏览器安全策略限制，`fetch()` 不能从 `file://` 协议加载本地文件。需要启动一个本地静态服务器：

```bash
cd 产品需求模板/
python3 -m http.server 8000
```

然后打开 `http://localhost:8000`

### 方式二：导入文件

如果无法启动服务器，可以：
1. 打开 `index.html`
2. 页面会显示"暂无内容"
3. 点击"导入 .md"按钮手动选择文件
4. 内容会保存到 localStorage，刷新不丢失

## 核心机制

### 内容加载优先级

```
localStorage (浏览器本地存储)
  ↓ 未命中
fetch(同目录文件)
  ↓ 失败
显示空状态 + 手动导入提示
```

1. **首次访问**：页面自动 `fetch()` 同目录下的 `.md` / `.json` 文件
2. **编辑保存后**：内容写入 `localStorage`，后续访问优先读 localStorage
3. **文件未找到**：显示空状态，提供手动导入入口

### 四个 Tab 的数据来源

| Tab | 加载文件 | 类型 | 渲染方式 |
|:---|:---|:---|:---|
| 流程图 | `flowchart.md` | Markdown | marked.js 渲染 + mermaid 图表 |
| 架构图 | `architecture.md` | Markdown | 同上 |
| 前端页面 | `pages.json` | JSON | 项目卡片列表 |
| 功能说明 | `features.md` | Markdown | 同上 |

## 数据驱动（config.json）

页面不再是硬编码。所有可配置项集中在 `config.json`：

- `meta` — 标题、副标题、标签、Logo
- `brand` — 品牌三色
- `tabs` — Tab 导航配置（名称、文件、类型、顺序）
- `cards` — 首页功能卡片
- `footer` — 页脚文字

HTML 模板启动时自动 `fetch('config.json')` 加载配置。失败则使用内置默认值。

## Python 可视化管理客户端

无需手动编辑 JSON/HTML。用桌面 GUI 管理一切。

### 安装

```bash
cd 产品需求模板/
pip install -r manager/requirements.txt --break-system-packages
```

### 运行

```bash
python manager/main.py
```

### 功能

| 面板 | 功能 |
|:---|:---|
| 元数据 | 编辑页面标题、副标题、标签、Logo SVG |
| 首页卡片 | 增删改功能卡片，选择图标、标题、描述 |
| Tab 管理 | 增删 Tab、修改名称/文件/类型、拖拽排序 |
| 品牌色 | 颜色选择器 + 色板预览，一键恢复默认 |
| 内容编辑 | 编辑每个 Tab 的 Markdown 内容，支持导入/保存 |

### 预览

点击底部 **"启动预览"** 按钮：
1. 自动启动内置 HTTP 服务器（端口 18900）
2. 打开 pywebview 预览窗口（调用系统原生 WebView）
3. 编辑 → 保存 → 点击"刷新预览" → 即时看效果

### 架构

```
┌─ CustomTkinter 管理窗口 ─────────────────────┐
│  [元数据] [首页卡片] [Tab管理] [品牌色] [内容] │
│                                                │
│  表单编辑区（修改 config.json + .md 文件）       │
│                                                │
│  [启动预览] [保存全部] [刷新预览] [打开目录]     │
└────────────────────────────────────────────────┘
         │ 启动/管理
         ▼
┌─ HTTP 服务器 (127.0.0.1:18900) ─┐
│  静态文件服务（index.html + .md） │
└──────────────────────────────────┘
         │ 加载
         ▼
┌─ pywebview 预览窗口 ────────────┐
│  系统原生 WebView 渲染           │
│  完整支持 CSS/JS/Fonts/Mermaid   │
└──────────────────────────────────┘
```

## 替换成你自己的项目

### 方式一：Python 客户端（推荐）

运行 `python manager/main.py`，通过 GUI 修改所有内容，点击保存即可。

### 方式二：直接编辑 config.json

编辑 `index.html` 中的以下区域：

- **标题**：`<h1 id="page-title">产品需求介绍</h1>`
- **副标题**：`<p class="intro-sub" id="page-subtitle">...</p>`
- **元信息标签**：`<div class="meta" id="page-meta">` 内的 `<span>`
- **核心功能卡片**：`<div class="hl-grid">` 内的 6 张卡片

### 2. 修改 Tab 名称

在 HTML 中搜索 `tab-btn`，修改按钮文字：

```html
<button class="tab-btn active" data-tab="flowchart">流程图</button>
<button class="tab-btn" data-tab="architecture">架构图</button>
<button class="tab-btn" data-tab="pages">前端页面</button>
<button class="tab-btn" data-tab="features">功能说明</button>
```

同时修改对应的 `<section class="tab-content" id="tab-xxx">` 区域。

### 3. 修改文件映射

在 JavaScript 开头的 `TAB_CONFIG` 中修改：

```javascript
const TAB_CONFIG = {
  你的tabId: { file: '你的文件.md', type: 'markdown', storageKey: 'md_你的key' },
  // ...
};
```

- `type: 'markdown'` — 渲染为 Markdown
- `type: 'pages'` — 渲染为项目卡片（需对应 JSON 文件）

### 4. 自定义前端页面卡片

编辑 `pages.json`：

```json
{
  "sections": [
    {
      "title": "分组标题",
      "cards": [
        {
          "title": "卡片标题",
          "description": "卡片描述",
          "tags": ["标签1", "标签2"],
          "iconType": "chat",
          "link": "page.html"
        }
      ]
    }
  ]
}
```

`iconType` 可选值：`chat` / `admin` / `kb` / `agent` / `ws`

### 5. 修改品牌色

在 CSS 的 `:root` 块中修改变量：

```css
:root {
  --brand: #E31E24;        /* 主品牌色 */
  --brand-light: #FDEBEC;  /* 品牌浅底 */
  --brand-dark: #B3151A;   /* 品牌深色 */
}
```

## 交互功能

| 功能 | 操作 | 说明 |
|:---|:---|:---|
| Tab 切换 | 点击导航栏按钮 | 切换显示不同内容区 |
| 在线编辑 | 点击右下角红色 FAB 按钮 | 进入编辑模式，可修改 Markdown |
| 保存 | 编辑模式下点击"保存" | 保存到 localStorage，刷新不丢失 |
| 导入 | 编辑模式下点击"导入 .md" | 从本地选择 .md 文件 |
| 下载 | 编辑模式下点击"下载 .md" | 导出当前内容为 .md 文件 |
| 目录导航 | 左侧 TOC 目录 | 仅宽屏 (>1200px) 显示，点击跳转到对应标题 |
| 项目卡片 | 点击卡片 | 新标签页打开对应页面 |

## 依赖

| 库 | 版本 | 加载方式 |
|:---|:---|:---|
| marked.js | v12 | unpkg CDN |
| mermaid.js | v11 | unpkg CDN |
| Google Fonts | — | Google Fonts CDN |

所有依赖从 CDN 加载，无需本地安装。

## 设计规范

遵循设计说明书 v1.0，详见以下规范：

- 品牌色：`#E31E24`（红）
- 标题字体：Playfair Display
- 正文字体：Inter
- 代码字体：JetBrains Mono
- 响应式断点：768px / 1200px
- 减少动效：`prefers-reduced-motion` 支持

## 后续计划

本模板将封装为一个 Skill，实现：

- CLI 一键生成项目目录
- 根据问答自动填写配置
- 支持添加/删除 Tab
- 主题切换（亮色/暗色）
