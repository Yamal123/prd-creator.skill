# Template configuration

## `config.json`

Preserve these top-level objects: `meta`, `brand`, `fonts`, `cards`, `tabs`, and `footer`.

```json
{
  "meta": {"title": "", "subtitle": "", "tags": ["v1.0", "作者", "日期"], "logo": {"type": "svg", "value": ""}},
  "brand": {"primary": "#E31E24", "light": "#FDEBEC", "dark": "#B3151A"},
  "fonts": {"display": "Playfair Display", "body": "Inter", "mono": "JetBrains Mono"},
  "cards": [{"icon": "document", "title": "", "description": ""}],
  "tabs": {
    "folder": "tabs",
    "groups": {"需求详述": ["05-模块A", "06-模块B"]},
    "files": [{"file": "tabs/01-项目背景.md", "label": "项目背景"}],
    "extra": [{"id": "pages", "label": "页面地图", "type": "pages", "file": "pages.json"}]
  },
  "footer": {"text": ""}
}
```

Card icons: `loop`, `sse`, `knowledge`, `memory`, `human`, `evolve`, `document`, `chart`, `cube`, `module`, `import`, `clock`.

## `pages.json`

```json
{"sections":[{"title":"分组","cards":[{"title":"页面","description":"","tags":["关键词"],"iconType":"chat","link":"/route"}]}]}
```

Page `iconType`: `chat`, `admin`, `kb`, `agent`, `ws`. Use real routes, not `#` placeholders.

## Built-in behavior

The template supports grouped menus, H1–H3 table of contents, Mermaid, image/SVG lightbox zoom, per-tab comments, Chinese filenames, and the manager at `/prd/manager/`.
