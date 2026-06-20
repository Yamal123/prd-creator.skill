# prd-creator

用模板 HTML 生成产品需求页面，skill 只负责写内容文件和索引。

## 触发

"生成 PRD 页面""创建产品需求网页""prd-creator"

## 流程

### 1. 拉取模板

```bash
git clone https://github.com/Yamal123/prd-creator.skill.git /tmp/prd-template
```

### 2. 部署到项目

```bash
mkdir -p prd/tabs prd/manager
cp /tmp/prd-template/index.html prd/
cp /tmp/prd-template/manager/index.html prd/manager/
cp /tmp/prd-template/manager/server.py prd/manager/
cp /tmp/prd-template/manager/start.py prd/manager/
rm -rf /tmp/prd-template
```

### 3. 收集信息（AskUserQuestion）

1. 产品名称
2. 一句话描述
3. 产品标签（如 v1.0、AI）
4. 品牌色（默认 #E31E24）
5. 核心功能点（3-6 个，标题 + 描述，决定首页卡片）

### 4. 生成 config.json

写入 `prd/config.json`。关键字段：
- `tabs.files`：索引 tabs/ 目录下所有 .md 文件，支持两种格式：
  - 字符串：`"tabs/01-概述.md"` — 标题自动从文件名派生
  - 对象：`{"file":"tabs/01-概述.md","label":"产品概览"}` — 自定义 Tab 标题，顺序即显示顺序
- `tabs.extra`：附加 Tab（如 pages 类型的产品介绍卡片页）

```json
{
  "meta": { "title": "", "subtitle": "", "tags": [], "logo": {"type":"svg","value":"<svg...</svg>"} },
  "brand": { "primary": "#E31E24", "light": "#FDEBEC", "dark": "#B3151A" },
  "cards": [{ "icon": "document", "title": "", "description": "" }],
  "tabs": { "folder": "tabs", "files": ["tabs/01-xxx.md"], "extra": [{"id":"intro","label":"产品介绍","type":"pages","file":"pages.json"}] },
  "footer": { "text": "" }
}
```

card icon 可选：loop, sse, knowledge, memory, human, evolve, document, chart, cube, module, import, clock

### 5. 生成 Tab 文档

扫描用户项目已有文档（`*.md, README*, docs/**`），列出让用户选择哪些关联为 Tab。未被关联的也可根据产品描述新生成。

每个 Tab 对应 `prd/tabs/xxx.md`，文件必须有 h1/h2/h3 层级以供目录生成。

更新 `config.json` 的 `tabs.files` 数组。

### 6. 生成 pages.json（条件：2+ 页面）

如用户有前端页面需要展示。卡片规则：
- `link`：必须指向项目真实路由（如 `/admin/agents`、`/chat`），不是 `#` 锚点
- `tags`：核心关键词（如 "Agent", "RAG", "RBAC"），不是 P0/P1 优先级标签
- `iconType`：chat / admin / kb / agent / ws

```json
{
  "sections": [
    { "title": "分组名", "cards": [
      { "title": "页面", "description": "", "tags": ["关键词"], "iconType": "chat", "link": "/admin/xxx" }
    ]}
  ]
}
```

### 7. 完成

```bash
cd prd/ && python3 manager/start.py
```

访问 `/prd/`，后台 `/prd/manager/`。

## 更新已有 prd/

1. **不重新复制 HTML 模板**（除非用户明确要求）
2. 读取现有 config.json 保留用户修改
3. 扫描 tabs/ 目录更新 files 索引（保持 `{file, label}` 对象格式）
4. 新增 Tab 追加到 tabs.files 和 tabs/，不覆盖已有 .md
5. 如无新内容需要生成，仅做索引一致性校验
