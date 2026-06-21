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
                bytecode = Path(tempfile.gettempdir()) / f"prd-creator-{path.stem}.pyc"
                py_compile.compile(str(path), doraise=True, cfile=str(bytecode))

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
