# prd-creator

根据用户项目自动生成产品需求介绍网页（首页 + Tab 内容区 + 目录导航 + 在线评论 + 后台管理），部署在项目的 `prd/` 目录下。

## 触发条件

"生成产品需求页面""创建 PRD""做一个需求介绍网页""prd-creator"。

## 目录结构

```
项目根目录/
├── prd/                  # 生成的所有内容
│   ├── index.html        # 主页面
│   ├── config.json       # 页面配置
│   ├── pages.json        # 前端页面卡片（可选）
│   ├── tabs/             # Markdown 内容文件
│   │   ├── 01-xxx.md
│   │   └── 02-xxx.md
│   └── manager/          # 后台管理器
│       ├── index.html
│       ├── server.py
│       └── start.py
```

访问地址：`<项目域名>/prd/`，后台：`<项目域名>/prd/manager/`

## 执行流程

### 步骤 1：扫描已有文档

用 Glob 扫描项目根目录：`*.md, README*, docs/**, CHANGELOG*, ARCHITECTURE*`

列出可关联的文档。

### 步骤 2：收集信息（AskUserQuestion）

1. 产品名称
2. 一句话描述
3. 产品标签
4. 品牌色（默认 #E31E24）
5. 核心功能点（3-6 个，标题 + 描述）

### 步骤 3：创建目录并复制模板

模板源：`/Users/yumeng/Knowledge/personal-knowledge-base/02_Projects/产品需求模板/`

```bash
mkdir -p prd/tabs prd/manager
cp <模板源>/index.html prd/
cp <模板源>/manager/index.html prd/manager/
cp <模板源>/manager/server.py prd/manager/
cp <模板源>/manager/start.py prd/manager/
```

### 步骤 4：生成 config.json

写入 `prd/config.json`。

### 步骤 5：生成 Tab 内容

每个章节一个 `prd/tabs/01-xxx.md`，Markdown 有清晰 h1/h2/h3 层级。更新 config.json 的 tabs.files。

### 步骤 6：生成 pages.json（可选）

iconType 可选：chat / admin / kb / agent / ws。

### 步骤 7：告知用户

```bash
cd prd/ && python3 manager/start.py
```

## 更新已有 prd/

1. 读取现有 config.json，保留已修改内容
2. 仅更新用户明确指定的部分
3. 新增 Tab 追加到 files 末尾
