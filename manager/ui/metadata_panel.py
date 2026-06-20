"""
metadata_panel.py — 元数据配置面板
编辑页面标题、副标题、标签、Logo
"""
import customtkinter as ctk
from .. import data


class MetadataPanel(ctk.CTkFrame):
    """元数据编辑面板"""

    def __init__(self, parent, config: dict, on_change=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_change = on_change
        self.tag_frames = []  # 标签行控件引用

        self._build()

    def _build(self):
        # 标题
        ctk.CTkLabel(self, text="页面标题", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(12, 4))
        self.title_entry = ctk.CTkEntry(self, height=36, font=ctk.CTkFont(size=14))
        self.title_entry.pack(fill="x", pady=(0, 12))
        self.title_entry.insert(0, self.config["meta"].get("title", ""))
        self.title_entry.bind("<KeyRelease>", lambda e: self._notify())

        # 副标题
        ctk.CTkLabel(self, text="副标题", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 4))
        self.subtitle_box = ctk.CTkTextbox(self, height=72, font=ctk.CTkFont(size=13), wrap="word")
        self.subtitle_box.pack(fill="x", pady=(0, 12))
        self.subtitle_box.insert("1.0", self.config["meta"].get("subtitle", ""))
        self.subtitle_box.bind("<KeyRelease>", lambda e: self._notify())

        # 标签
        tag_header = ctk.CTkFrame(self, fg_color="transparent")
        tag_header.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(tag_header, text="元信息标签", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        ctk.CTkButton(
            tag_header, text="+ 添加", width=70, height=28,
            font=ctk.CTkFont(size=11),
            command=self._add_tag
        ).pack(side="right")

        self.tags_container = ctk.CTkScrollableFrame(self, height=80, fg_color="transparent")
        self.tags_container.pack(fill="x", pady=(0, 12))
        self._refresh_tags()

        # Logo
        ctk.CTkLabel(self, text="Logo SVG（留空使用默认）", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 4))
        self.logo_box = ctk.CTkTextbox(self, height=80, font=ctk.CTkFont(size=11, family="monospace"), wrap="word")
        self.logo_box.pack(fill="x")
        logo_val = ""
        if self.config["meta"].get("logo"):
            logo_val = self.config["meta"]["logo"].get("value", "")
        self.logo_box.insert("1.0", logo_val)
        self.logo_box.bind("<KeyRelease>", lambda e: self._notify())

    def _refresh_tags(self):
        """重建标签行"""
        for f in self.tag_frames:
            f.destroy()
        self.tag_frames.clear()

        tags = self.config["meta"].get("tags", [])
        for i, tag in enumerate(tags):
            row = ctk.CTkFrame(self.tags_container, fg_color="transparent")
            row.pack(fill="x", pady=2)

            entry = ctk.CTkEntry(row, height=30, font=ctk.CTkFont(size=13))
            entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
            entry.insert(0, tag)
            entry.bind("<KeyRelease>", lambda e, idx=i: self._update_tag(idx, e.widget.get()))

            btn = ctk.CTkButton(
                row, text="✕", width=30, height=30,
                fg_color="#fee2e2", text_color="#dc2626",
                hover_color="#fecaca", font=ctk.CTkFont(size=12),
                command=lambda idx=i: self._remove_tag(idx)
            )
            btn.pack(side="right")

            self.tag_frames.append(row)

    def _add_tag(self):
        tags = self.config["meta"].get("tags", [])
        tags.append("新标签")
        self.config["meta"]["tags"] = tags
        self._refresh_tags()
        self._notify()

    def _remove_tag(self, index):
        tags = self.config["meta"].get("tags", [])
        if 0 <= index < len(tags):
            tags.pop(index)
            self.config["meta"]["tags"] = tags
            self._refresh_tags()
            self._notify()

    def _update_tag(self, index, value):
        tags = self.config["meta"].get("tags", [])
        if 0 <= index < len(tags):
            tags[index] = value
            self._notify()

    def _notify(self):
        """通知外部数据变更"""
        if self.on_change:
            self.on_change()

    def collect(self):
        """收集当前表单数据到 config"""
        self.config["meta"]["title"] = self.title_entry.get()
        self.config["meta"]["subtitle"] = self.subtitle_box.get("1.0", "end-1c")
        self.config["meta"]["logo"] = {
            "type": "svg",
            "value": self.logo_box.get("1.0", "end-1c")
        }
        # tags 已在编辑时实时更新
