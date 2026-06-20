"""
data.py — 配置与内容文件的读写层
管理 config.json 和 tabs/ 目录下的 .md / .json 内容文件
"""
import json
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_config_path() -> Path:
    return get_project_root() / "config.json"


def get_tabs_folder(config: dict) -> Path:
    """获取 Tab 文件夹路径"""
    folder = config.get("tabs", {}).get("folder", "tabs")
    return get_project_root() / folder


# ============================================================
# 默认配置
# ============================================================
DEFAULT_CONFIG = {
    "meta": {
        "title": "产品需求介绍",
        "subtitle": "",
        "tags": ["v1.0"],
        "logo": {"type": "svg", "value": ""}
    },
    "brand": {"primary": "#E31E24", "light": "#FDEBEC", "dark": "#B3151A"},
    "fonts": {"display": "Playfair Display", "body": "Inter", "mono": "JetBrains Mono"},
    "tabs": {
        "folder": "tabs",
        "files": [],
        "extra": []
    },
    "cards": [],
    "footer": {"text": "产品需求文档"}
}

AVAILABLE_ICONS = [
    "loop", "sse", "knowledge", "memory", "human", "evolve",
    "document", "chart", "cube", "module", "import", "clock"
]
TAB_TYPES = ["markdown", "pages"]


# ============================================================
# Config 读写
# ============================================================
def load_config() -> dict:
    path = get_config_path()
    if path.exists():
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
            return _deep_merge(DEFAULT_CONFIG, config)
        except (json.JSONDecodeError, IOError):
            pass
    return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config(config: dict) -> bool:
    try:
        get_config_path().write_text(
            json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return True
    except IOError as e:
        print(f"保存 config.json 失败: {e}")
        return False


# ============================================================
# Tab 文件夹扫描
# ============================================================
def scan_tabs_folder(config: dict) -> list[str]:
    """扫描 tabs/ 文件夹，返回相对路径列表"""
    folder = get_tabs_folder(config)
    if not folder.exists():
        return []

    project_root = get_project_root()
    files = []
    for f in sorted(folder.glob("*.md")):
        rel = str(f.relative_to(project_root))
        files.append(rel)
    for f in sorted(folder.glob("*.txt")):
        rel = str(f.relative_to(project_root))
        files.append(rel)
    return files


def sync_tabs_files(config: dict) -> dict:
    """扫描文件夹并更新 config.tabs.files"""
    config.setdefault("tabs", {})
    config["tabs"]["files"] = scan_tabs_folder(config)
    config["tabs"].setdefault("extra", [])
    return config


# ============================================================
# 内容文件读写
# ============================================================
def load_content(file_path: str, tab_id: str = None) -> str:
    project_root = get_project_root()
    if tab_id:
        backup = project_root / f".{tab_id}_backup.md"
        if backup.exists():
            return backup.read_text(encoding="utf-8")
    full = project_root / file_path
    if full.exists():
        return full.read_text(encoding="utf-8")
    return ""


def save_content(file_path: str, content: str, tab_id: str = None) -> bool:
    project_root = get_project_root()
    try:
        (project_root / file_path).write_text(content, encoding="utf-8")
        return True
    except IOError as e:
        print(f"保存 {file_path} 失败: {e}")
        if tab_id:
            (project_root / f".{tab_id}_backup.md").write_text(content, encoding="utf-8")
        return False


def list_content_files(config: dict) -> list[str]:
    """列出所有内容文件的相对路径"""
    files = list(config.get("tabs", {}).get("files", []))
    for t in config.get("tabs", {}).get("extra", []):
        files.append(t.get("file", ""))
    return [f for f in files if f]


# ============================================================
# 工具
# ============================================================
def _deep_merge(base: dict, override: dict) -> dict:
    result = json.loads(json.dumps(base))
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
