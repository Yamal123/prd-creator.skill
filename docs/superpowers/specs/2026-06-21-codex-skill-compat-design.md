# PRD Creator Codex Skill Compatibility Design

## Goal

Convert the existing `prd-creator.skill` repository into a self-contained Codex skill while preserving the current PRD webpage template and publishing the changes through a reviewable pull request.

## Current Problems

- `SKILL.md` lacks the required YAML frontmatter, so Codex does not discover the skill.
- The skill instructs the agent to clone the repository at runtime instead of using bundled assets.
- The repository mixes skill instructions, reusable template files, user documentation, and generated Python cache files at the root.
- The workflow uses tool terminology that is not native to Codex, such as `AskUserQuestion`.
- Installing the repository root through the current installer can produce a sparse working tree that omits `manager/` and `tabs/` even though those files exist in Git.
- The README and skill instructions contain outdated or conflicting template details.

## Chosen Approach

Create a conventional Codex skill package in the repository root:

```text
prd-creator.skill/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── template/
│       ├── index.html
│       ├── config.json
│       ├── pages.json
│       ├── manager/
│       └── tabs/
├── references/
│   ├── prd-chapters.md
│   └── template-configuration.md
├── README.md
└── .gitignore
```

The repository remains directly installable as a single skill. Template files become bundled assets, so creating a PRD does not require network access.

## Skill Metadata and Triggering

`SKILL.md` will contain only the required frontmatter fields:

- `name: prd-creator`
- A third-person `description` beginning with `Use when...` and covering creation, update, regeneration, deletion, PRD pages, product requirement pages, and Chinese trigger phrases.

`agents/openai.yaml` will define:

- `display_name`: PRD Creator
- A concise user-facing description
- A default prompt that explicitly invokes `$prd-creator`

No optional branding fields will be invented.

## Workflow Design

The skill will support four modes:

1. Create a new `prd/` site.
2. Update an existing site without overwriting user-authored content.
3. Regenerate configuration and content when explicitly requested.
4. Delete the generated `prd/` directory only after explicit confirmation.

For creation, Codex will:

1. Inspect the target project using `rg`, `rg --files`, project manifests, documentation, routes, schema files, and Git history.
2. Copy `assets/template/` into the target project's `prd/` directory.
3. Ask only for business information that cannot be inferred safely.
4. Generate `config.json`, `pages.json`, and Markdown chapters without inventing unknown facts.
5. Validate JSON, referenced files, and template integrity.
6. Explain how to launch the local preview.

The instructions will use tool-agnostic language where possible and Codex-native names only where they materially improve reliability.

## Progressive Disclosure

Keep `SKILL.md` focused on mode selection, safety rules, and the execution sequence. Move detailed content to references:

- `references/prd-chapters.md`: the 22-chapter framework, evidence sources, and content constraints.
- `references/template-configuration.md`: `config.json`, `pages.json`, icons, tabs, groups, and preview behavior.

The HTML, JSON examples, manager files, and starter tabs are assets and should not be loaded into context unless needed.

## Repository Hygiene

- Remove tracked `.DS_Store` and `__pycache__` files.
- Expand `.gitignore` to prevent OS metadata, Python caches, temporary files, and local environments.
- Preserve the GitHub README, but rewrite it as concise installation and usage documentation rather than duplicating the complete skill body.
- Do not add a plugin manifest; this repository remains a single skill, not a plugin bundle.

## Safety and Error Handling

- Never overwrite an existing `prd/` directory during creation without explicit approval.
- Preserve existing configuration fields and authored Markdown during update mode.
- Require explicit confirmation before deleting `prd/`.
- Treat missing project evidence as unknown and mark it for confirmation instead of fabricating content.
- Stop with an actionable error when bundled assets are missing or generated JSON is invalid.

## Validation

Validation will cover:

1. Codex skill schema: YAML frontmatter, folder/name agreement, and `agents/openai.yaml` structure.
2. Repository hygiene: no tracked cache or OS metadata files.
3. Asset completeness: required HTML, JSON, manager, and tab files exist.
4. Template smoke test: copy bundled assets to a temporary `prd/` directory and verify expected paths.
5. Data syntax: parse all bundled JSON files.
6. Python syntax: compile manager Python sources without writing cache files into the repository.
7. Reference integrity: verify every local path mentioned by `SKILL.md` exists.

The existing template behavior will not be redesigned in this compatibility pull request.

## Delivery

- Work on branch `codex/skill-compat`.
- Commit the compatibility changes with focused commit messages.
- Push the branch to `Yamal123/prd-creator.skill`.
- Open a pull request against `main` summarizing the structural migration and verification evidence.
