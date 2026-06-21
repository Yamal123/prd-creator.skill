# PRD Creator for Codex

A self-contained Codex skill that creates and maintains project PRD websites under `prd/`.

## Install

Ask Codex to install:

```text
https://github.com/Yamal123/prd-creator.skill.git
```

Restart Codex after installation.

## Use

```text
Use $prd-creator to create a PRD website for this project.
Use $prd-creator to update the existing PRD with the new billing module.
Use $prd-creator to regenerate the PRD content.
Use $prd-creator to delete the generated PRD.
```

The template is bundled in `assets/template/`; generation does not clone GitHub at runtime.

## Structure

```text
SKILL.md
agents/openai.yaml
assets/template/
references/
tests/test_skill_package.py
```

## Preview generated output

```bash
python3 prd/manager/start.py
```

Open `http://127.0.0.1:18900/prd/` and `http://127.0.0.1:18900/prd/manager/`.

## Validate the skill

```bash
python3 -m unittest tests/test_skill_package.py -v
```
