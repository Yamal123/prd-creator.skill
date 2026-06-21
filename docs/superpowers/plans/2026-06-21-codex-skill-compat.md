# PRD Creator Codex Skill Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `prd-creator.skill` into a discoverable, self-contained Codex skill and publish it through a pull request from `codex/skill-compat`.

**Architecture:** Keep the repository root as the installable skill. Store agent instructions in `SKILL.md`, UI discovery metadata in `agents/openai.yaml`, reusable website files in `assets/template/`, and detailed guidance in `references/`. A standard-library test suite validates discovery metadata, asset completeness, repository hygiene, JSON syntax, Python syntax, and local path references.

**Tech Stack:** Markdown, YAML, HTML/CSS/JavaScript, JSON, Python 3 standard library, Git, GitHub CLI.

---

## File Map

- Create `tests/test_skill_package.py`: automated contract tests for the Codex skill package.
- Rewrite `SKILL.md`: concise Codex-native workflow and safety rules.
- Create `agents/openai.yaml`: user-facing skill metadata.
- Create `references/prd-chapters.md`: detailed 22-chapter PRD framework.
- Create `references/template-configuration.md`: template schema and preview reference.
- Move `index.html`, `config.json`, `pages.json`, `manager/`, and `tabs/` into `assets/template/`.
- Rewrite `README.md`: GitHub installation and usage guide.
- Modify `.gitignore`: exclude generated caches, environments, and local output.
- Remove tracked `manager/.DS_Store` and `manager/__pycache__/` files.

### Task 1: Add a failing Codex package contract test

**Files:**
- Create: `tests/test_skill_package.py`

- [ ] **Step 1: Create the contract test**

Create a `unittest` suite with these checks:

```python
import json
import py_compile
import re
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
TEMPLATE = ROOT / "assets" / "template"


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    values = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip().strip('"')
    return values


class SkillPackageTests(unittest.TestCase):
    def test_skill_frontmatter_is_discoverable(self):
        metadata = frontmatter(SKILL.read_text(encoding="utf-8"))
        self.assertEqual(metadata.get("name"), "prd-creator")
        self.assertTrue(metadata.get("description", "").startswith("Use when"))
        self.assertEqual(set(metadata), {"name", "description"})

    def test_openai_interface_metadata_exists(self):
        text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "PRD Creator"', text)
        self.assertIn("$prd-creator", text)

    def test_template_assets_are_complete(self):
        required = [
            "index.html",
            "config.json",
            "pages.json",
            "manager/index.html",
            "manager/server.py",
            "manager/start.py",
            "tabs/flowchart.md",
            "tabs/architecture.md",
            "tabs/features.md",
        ]
        self.assertEqual([item for item in required if not (TEMPLATE / item).is_file()], [])

    def test_template_json_is_valid(self):
        for name in ("config.json", "pages.json"):
            with self.subTest(name=name):
                json.loads((TEMPLATE / name).read_text(encoding="utf-8"))

    def test_manager_python_has_valid_syntax(self):
        for path in (TEMPLATE / "manager").glob("*.py"):
            with self.subTest(path=path.name):
                py_compile.compile(str(path), doraise=True, cfile=str(Path(tempfile.gettempdir()) / f"{path.stem}.pyc"))

    def test_template_can_be_copied_as_prd_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "prd"
            shutil.copytree(TEMPLATE, target)
            self.assertTrue((target / "index.html").is_file())
            self.assertTrue((target / "manager" / "start.py").is_file())

    def test_skill_local_references_exist(self):
        text = SKILL.read_text(encoding="utf-8")
        paths = re.findall(r"`((?:assets|references)/[^`]+)`", text)
        missing = [path for path in paths if not (ROOT / path).exists()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify the expected failure**

Run:

```bash
python3 -m unittest tests/test_skill_package.py -v
```

Expected: failures for missing YAML frontmatter, `agents/openai.yaml`, and `assets/template/`. The failure must reflect absent Codex packaging, not a syntax error in the test.

- [ ] **Step 3: Commit the failing contract test**

```bash
git add tests/test_skill_package.py
git commit -m "test: define Codex skill package contract"
```

### Task 2: Move reusable template files into skill assets

**Files:**
- Create: `assets/template/`
- Move: `index.html` → `assets/template/index.html`
- Move: `config.json` → `assets/template/config.json`
- Move: `pages.json` → `assets/template/pages.json`
- Move: `manager/index.html` → `assets/template/manager/index.html`
- Move: `manager/server.py` → `assets/template/manager/server.py`
- Move: `manager/start.py` → `assets/template/manager/start.py`
- Move: `tabs/*.md` → `assets/template/tabs/*.md`
- Modify: `.gitignore`
- Delete: tracked cache and OS metadata files under `manager/`

- [ ] **Step 1: Move source-controlled template files**

```bash
mkdir -p assets/template
git mv index.html config.json pages.json assets/template/
git mv manager assets/template/manager
git mv tabs assets/template/tabs
```

- [ ] **Step 2: Remove tracked generated files**

Remove these paths from Git and the working tree:

```bash
find assets/template/manager -name .DS_Store -delete
find assets/template/manager -type d -name __pycache__ -prune -exec rm -rf {} +
```

- [ ] **Step 3: Replace `.gitignore` with repository hygiene rules**

```gitignore
.DS_Store
__pycache__/
*.py[cod]
.venv/
venv/
.env
.prd/
prd/
```

- [ ] **Step 4: Run the contract test**

Run:

```bash
python3 -m unittest tests/test_skill_package.py -v
```

Expected: asset, JSON, Python, and copy tests pass; metadata and reference tests still fail.

- [ ] **Step 5: Commit the asset migration**

```bash
git add .gitignore assets
git add -u
git commit -m "refactor: bundle PRD template as skill assets"
```

### Task 3: Create Codex discovery and UI metadata

**Files:**
- Rewrite: `SKILL.md`
- Create: `agents/openai.yaml`

- [ ] **Step 1: Rewrite `SKILL.md` with required frontmatter**

Use exactly two frontmatter fields:

```yaml
---
name: prd-creator
description: Use when creating, updating, regenerating, or deleting a product requirements webpage or PRD site, including requests for 产品需求页面、PRD 页面、需求介绍网页、更新 PRD、删除 PRD, or prd-creator.
---
```

The body must contain:

- Mode selection for create, update, regenerate, and delete.
- A required preflight check for `assets/template/`.
- Project inspection using `rg` and `rg --files` with fallbacks when unavailable.
- Copy instructions from `assets/template/` to the target `prd/` directory without runtime cloning.
- Preservation rules for existing `config.json` and authored Markdown.
- Explicit approval before overwrite or deletion.
- Links to `references/prd-chapters.md` and `references/template-configuration.md`.
- Validation commands for JSON, expected files, and preview startup.

Remove runtime `git clone`, `AskUserQuestion`, outdated step counts, and duplicated detailed schemas from the main body.

- [ ] **Step 2: Generate `agents/openai.yaml`**

Run the skill creator generator using these exact interface values:

```bash
python3 /Users/yumeng/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py . \
  --interface 'display_name=PRD Creator' \
  --interface 'short_description=Create and maintain project PRD websites' \
  --interface 'default_prompt=Use $prd-creator to create or update a PRD website for this project.'
```

Expected file:

```yaml
interface:
  display_name: "PRD Creator"
  short_description: "Create and maintain project PRD websites"
  default_prompt: "Use $prd-creator to create or update a PRD website for this project."
```

If the default Python runtime lacks `yaml`, use the bundled workspace Python reported by `codex_app__load_workspace_dependencies`; do not disable validation or vendor a YAML parser.

- [ ] **Step 3: Run the metadata-focused tests**

```bash
python3 -m unittest \
  tests.test_skill_package.SkillPackageTests.test_skill_frontmatter_is_discoverable \
  tests.test_skill_package.SkillPackageTests.test_openai_interface_metadata_exists -v
```

Expected: both tests pass. The reference test may still fail until Task 4.

- [ ] **Step 4: Commit discovery metadata**

```bash
git add SKILL.md agents/openai.yaml
git commit -m "feat: add Codex skill discovery metadata"
```

### Task 4: Extract detailed guidance into references

**Files:**
- Create: `references/prd-chapters.md`
- Create: `references/template-configuration.md`

- [ ] **Step 1: Create `references/prd-chapters.md`**

Move the existing 22-chapter table and generation constraints from `SKILL.md`. Preserve:

- Chapter numbers and Chinese labels.
- Evidence sources for each chapter.
- `01-标题.md` naming rule.
- Minimum heading structure.
- Linked-source, inferred-content, pending-confirmation, and no-fabrication rules.

Add a short table of contents because this reference is longer than 100 lines only if the final file crosses that threshold.

- [ ] **Step 2: Create `references/template-configuration.md`**

Document the exact `config.json` and `pages.json` schemas already supported by the template, including:

- `meta`, `brand`, `fonts`, `cards`, `tabs`, and `footer`.
- `{file, label}` entries in `tabs.files`.
- `tabs.groups` and `tabs.extra`.
- Supported card icons and page-card `iconType` values.
- Local preview command `python3 prd/manager/start.py` and URLs.
- Built-in multilevel menu, TOC, Mermaid, lightbox, comments, and manager behavior.

- [ ] **Step 3: Run reference and full contract tests**

```bash
python3 -m unittest tests/test_skill_package.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit references**

```bash
git add references SKILL.md
git commit -m "docs: add PRD generation references"
```

### Task 5: Rewrite GitHub documentation

**Files:**
- Rewrite: `README.md`

- [ ] **Step 1: Replace README content**

The README must include:

- What the skill creates.
- Codex installation command using the repository URL.
- Restart requirement after installation.
- Example prompts for create, update, regenerate, and delete.
- The new repository structure.
- A concise explanation that templates are bundled and do not require runtime GitHub access.
- Local preview command and URLs.
- Contributor validation command.

Do not duplicate the complete 22-chapter framework or configuration reference.

- [ ] **Step 2: Check documentation links and stale paths**

Run:

```bash
rg -n "git clone|AskUserQuestion|^index\.html|^config\.json|^pages\.json|manager/start\.py" SKILL.md README.md references
```

Expected: no runtime clone or foreign tool terminology. Template paths point to `assets/template/`; preview paths may correctly point to generated `prd/manager/start.py`.

- [ ] **Step 3: Run the full contract test**

```bash
python3 -m unittest tests/test_skill_package.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit README**

```bash
git add README.md
git commit -m "docs: document Codex installation and usage"
```

### Task 6: Perform final validation

**Files:**
- Verify all changed files.

- [ ] **Step 1: Run the official skill validator**

```bash
python3 /Users/yumeng/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

Expected: `Skill is valid!`. If the default runtime lacks `yaml`, rerun with the bundled workspace Python.

- [ ] **Step 2: Run the package contract suite**

```bash
python3 -m unittest tests/test_skill_package.py -v
```

Expected: seven tests pass with zero failures and zero errors.

- [ ] **Step 3: Verify repository hygiene and diffs**

```bash
git ls-files | rg '(^|/)(\.DS_Store|__pycache__/)|\.pyc$'
git diff --check main...HEAD
git status --short
```

Expected: the hygiene search returns no matches, `git diff --check` returns no errors, and the working tree is clean.

- [ ] **Step 4: Review the final branch diff**

```bash
git diff --stat main...HEAD
git diff --name-status main...HEAD
```

Expected: only the designed skill packaging, references, tests, README, and design/plan documents changed.

### Task 7: Publish the branch and open the pull request

**Files:**
- No new files.

- [ ] **Step 1: Push the feature branch**

```bash
git push -u origin codex/skill-compat
```

Expected: GitHub accepts the branch and reports it tracking `origin/codex/skill-compat`.

- [ ] **Step 2: Open the pull request**

```bash
gh pr create \
  --base main \
  --head codex/skill-compat \
  --title "feat: make prd-creator a Codex-compatible skill" \
  --body-file /private/tmp/prd-creator-skill-pr-body.md
```

The PR body must summarize:

- Required Codex frontmatter and UI metadata.
- Bundled template migration and removal of runtime cloning.
- Progressive disclosure via references.
- Repository cache cleanup.
- Exact validation commands and results.

Expected: `gh` returns the new pull request URL.
