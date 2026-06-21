---
name: prd-creator
description: Use when creating, updating, regenerating, or deleting a product requirements webpage or PRD site, including requests for 产品需求页面、PRD 页面、需求介绍网页、更新 PRD、删除 PRD, or prd-creator.
---

# PRD Creator

Generate and maintain a project-local `prd/` website from bundled assets and evidence found in the project. Never invent product facts.

## Choose a mode

- **Create:** no `prd/config.json` exists. Inspect the project, then copy the bundled template and generate content.
- **Update:** preserve existing configuration fields and authored Markdown; add or revise only requested content.
- **Regenerate:** rebuild configuration and generated chapters only when explicitly requested. Preserve the HTML template unless replacement is requested.
- **Delete:** remove `prd/` only after explicit confirmation.

## Safety rules

1. Before copying, verify `assets/template/index.html`, `assets/template/config.json`, and `assets/template/manager/start.py` exist relative to this skill.
2. Never overwrite an existing `prd/` directory without approval.
3. Use project evidence for claims. Mark unresolved business facts as `> 待确认: ...`.
4. Preserve unknown keys in existing JSON during updates.
5. Use `rg` and `rg --files` for discovery when available; otherwise use equivalent read-only searches.

## Create workflow

1. Inspect README files, manifests, routes, API definitions, schemas, migrations, documentation, TODOs, and recent Git history.
2. Ask only for product positioning, users, brand choices, requirements, or milestones that cannot be inferred safely.
3. Copy the complete `assets/template/` directory to `<project>/prd/`.
4. Read `references/prd-chapters.md`, then create relevant numbered Markdown files under `prd/tabs/`.
5. Read `references/template-configuration.md`, then generate `prd/config.json` and `prd/pages.json`.
6. Validate JSON and every file referenced by `tabs.files` and `tabs.extra`.
7. Report generated paths and the preview command.

## Update workflow

1. Read the existing `prd/config.json`, `prd/pages.json`, and `prd/tabs/` files.
2. Inspect project changes relevant to the request.
3. Modify only requested content. Do not recopy `assets/template/` unless the user requests a template update.
4. Keep `tabs.files`, `tabs.groups`, `tabs.extra`, and files on disk consistent.
5. Re-run validation.

## Validation

```bash
python3 -m json.tool prd/config.json >/dev/null
python3 -m json.tool prd/pages.json >/dev/null
test -f prd/index.html
test -f prd/manager/start.py
```

Preview from the project root:

```bash
python3 prd/manager/start.py
```

Open `http://127.0.0.1:18900/prd/`; manager: `http://127.0.0.1:18900/prd/manager/`.
