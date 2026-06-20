"""
intro_panel.py — 基础介绍面板
Logo上传 · 页面标题 · 副标题 · 标签（空格+#分隔） · 功能卡片管理
"""
import customtkinter as ctk
import base64
from pathlib import Path
from .. import data

# 图标中文名称映射
ICON_CN_MAP = {
    "路由/循环": "loop", "信号/实时": "sse", "知识/书本": "knowledge",
    "记忆/存储": "memory", "人工/用户": "human", "进化/成长": "evolve",
    "文档/文件": "document", "图表/数据": "chart", "模块/方块": "cube",
    "组件/插件": "module", "导入/下载": "import", "时钟/时间": "clock",
}


class IntroPanel(ctk.CTkFrame):
    """基础介绍编辑面板"""

    def __init__(self, parent, config: dict, on_change=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_change = on_change
        self.card_rows = []
        self._build()

    def _build(self):
        # ---- Logo ----
        ctk.CTkLabel(self, text="Logo", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(12, 6))

        logo_row = ctk.CTkFrame(self, fg_color="transparent")
        logo_row.pack(fill="x", pady=(0, 8))

        # 当前 Logo 预览
        self.logo_preview = ctk.CTkFrame(logo_row, width=56, height=56, corner_radius=12)
        self.logo_preview.pack(side="left", padx=(0, 10))
        try:
            self.logo_preview.configure(fg_color=self.config["brand"].get("primary", "#E31E24"))
        except Exception:
            self.logo_preview.configure(fg_color="#E31E24")
        self._update_logo_preview()

        btn_col = ctk.CTkFrame(logo_row, fg_color="transparent")
        btn_col.pack(side="left")
        ctk.CTkButton(btn_col, text="上传 PNG/JPG", width=110, height=28,
            font=ctk.CTkFont(size=11), command=self._upload_logo_image).pack(anchor="w", pady=2)
        ctk.CTkButton(btn_col, text="编辑 SVG", width=110, height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"), command=self._edit_logo_svg).pack(anchor="w")

        # SVG 编辑区（默认隐藏）
        self.svg_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.svg_box = ctk.CTkTextbox(self.svg_frame, height=80, font=ctk.CTkFont(size=11, family="monospace"), wrap="word")
        self.svg_box.pack(fill="x")
        self.svg_box.insert("1.0", self._get_logo_value())
        self.svg_box.bind("<KeyRelease>", lambda e: self._on_svg_change())

        ctk.CTkButton(self.svg_frame, text="应用 SVG", width=80, height=24,
            font=ctk.CTkFont(size=11), command=self._apply_svg).pack(anchor="e", pady=(4, 0))

        # ---- 页面标题 ----
        ctk.CTkLabel(self, text="页面标题", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(16, 6))
        self.title_entry = ctk.CTkEntry(self, height=34, font=ctk.CTkFont(size=14))
        self.title_entry.pack(fill="x", pady=(0, 12))
        self.title_entry.insert(0, self.config["meta"].get("title", ""))
        self.title_entry.bind("<KeyRelease>", lambda e: self._notify())

        # ---- 副标题 ----
        ctk.CTkLabel(self, text="副标题", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 6))
        self.subtitle_box = ctk.CTkTextbox(self, height=60, font=ctk.CTkFont(size=13), wrap="word")
        self.subtitle_box.pack(fill="x", pady=(0, 12))
        self.subtitle_box.insert("1.0", self.config["meta"].get("subtitle", ""))
        self.subtitle_box.bind("<KeyRelease>", lambda e: self._notify())

        # ---- 标签（空格+#分隔） ----
        ctk.CTkLabel(self, text="标签（用空格 + # 分隔，如: v2.0 #AI Agent #企业级）",
            font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 6))
        tags_display = " ".join(f"#{t}" for t in self.config["meta"].get("tags", []))
        self.tags_entry = ctk.CTkEntry(self, height=34, font=ctk.CTkFont(size=13))
        self.tags_entry.pack(fill="x", pady=(0, 12))
        self.tags_entry.insert(0, tags_display)
        self.tags_entry.bind("<KeyRelease>", lambda e: self._parse_tags())

        # ---- 功能卡片 ----
        card_header = ctk.CTkFrame(self, fg_color="transparent")
        card_header.pack(fill="x", pady=(4, 8))
        ctk.CTkLabel(card_header, text="首页功能卡片", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(card_header, text="+ 添加卡片", width=90, height=28,
            font=ctk.CTkFont(size=11), command=self._add_card).pack(side="right")

        self.cards_container = ctk.CTkScrollableFrame(self, height=320, fg_color="transparent")
        self.cards_container.pack(fill="both", expand=True)
        self._refresh_cards()

    # ================================================================
    # Logo
    # ================================================================
    def _get_logo_value(self):
        logo = self.config["meta"].get("logo", {})
        return logo.get("value", "") if logo else ""

    def _update_logo_preview(self):
        """更新 Logo 预览色块（简化显示）"""
        for w in self.logo_preview.winfo_children():
            w.destroy()
        logo_type = self.config["meta"].get("logo", {}).get("type", "svg")
        label_text = "SVG" if logo_type == "svg" else "IMG"
        ctk.CTkLabel(self.logo_preview, text=label_text, font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white").place(relx=0.5, rely=0.5, anchor="center")

    def _upload_logo_image(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="选择 Logo 图片",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")]
        )
        if not path:
            return
        try:
            with open(path, "rb") as f:
                img_data = f.read()
            ext = path.rsplit(".", 1)[-1].lower()
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif"}.get(ext, "image/png")
            data_uri = f"data:{mime};base64,{base64.b64encode(img_data).decode()}"
            self.config["meta"]["logo"] = {"type": "image", "value": data_uri}
            self._update_logo_preview()
            self._notify()
        except Exception as e:
            print(f"Logo upload failed: {e}")

    def _edit_logo_svg(self):
        if self.svg_frame.winfo_ismapped():
            self.svg_frame.pack_forget()
        else:
            self.svg_box.delete("1.0", "end")
            self.svg_box.insert("1.0", self._get_logo_value())
            self.svg_frame.pack(fill="x", pady=(0, 8), after=self.logo_preview.master)

    def _on_svg_change(self):
        pass  # 实时预览太麻烦，点击"应用 SVG"才生效

    def _apply_svg(self):
        svg_text = self.svg_box.get("1.0", "end-1c").strip()
        self.config["meta"]["logo"] = {"type": "svg", "value": svg_text if svg_text else ""}
        self._update_logo_preview()
        self.svg_frame.pack_forget()
        self._notify()

    # ================================================================
    # 标签
    # ================================================================
    def _parse_tags(self):
        raw = self.tags_entry.get()
        tags = [t.strip() for t in raw.split("#") if t.strip()]
        self.config["meta"]["tags"] = tags

    # ================================================================
    # 卡片
    # ================================================================
    def _refresh_cards(self):
        for row in self.card_rows:
            row[0].destroy()
        self.card_rows.clear()
        cards = self.config.get("cards", [])
        for i, card in enumerate(cards):
            self._create_card_row(i, card)

    def _create_card_row(self, index, card):
        frame = ctk.CTkFrame(self.cards_container, fg_color=("gray95", "gray17"), corner_radius=8)
        frame.pack(fill="x", pady=3, padx=2)

        # 标题栏
        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(top, text=f"卡片 {index + 1}", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

        # 图标（中文名称下拉）
        icon_names = list(ICON_CN_MAP.keys())
        current_icon = card.get("icon", "document")
        current_cn = next((cn for cn, en in ICON_CN_MAP.items() if en == current_icon), icon_names[0])
        icon_menu = ctk.CTkOptionMenu(top, values=icon_names, width=130, height=24,
            font=ctk.CTkFont(size=11),
            command=lambda v, i=index: self._update_card(i, "icon", ICON_CN_MAP.get(v, "document")))
        icon_menu.pack(side="right", padx=(0, 6))
        try: icon_menu.set(current_cn)
        except Exception: pass

        ctk.CTkButton(top, text="✕", width=28, height=24,
            fg_color="#fee2e2", text_color="#dc2626", hover_color="#fecaca",
            font=ctk.CTkFont(size=11),
            command=lambda i=index: self._remove_card(i)).pack(side="right")

        # 标题
        ctk.CTkLabel(frame, text="标题", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10)
        title_entry = ctk.CTkEntry(frame, height=28, font=ctk.CTkFont(size=13))
        title_entry.pack(fill="x", padx=10, pady=(0, 4))
        title_entry.insert(0, card.get("title", ""))
        title_entry.bind("<KeyRelease>", lambda e, i=index: self._update_card(i, "title", e.widget.get()))

        # 描述（markdown）
        ctk.CTkLabel(frame, text="描述（支持 Markdown）", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10)
        desc_box = ctk.CTkTextbox(frame, height=60, font=ctk.CTkFont(size=12), wrap="word")
        desc_box.pack(fill="x", padx=10, pady=(0, 8))
        desc_box.insert("1.0", card.get("description", ""))
        desc_box.bind("<KeyRelease>", lambda e, i=index: self._update_card(i, "description", e.widget.get("1.0", "end-1c")))

        self.card_rows.append((frame, icon_menu, title_entry, desc_box))

    def _update_card(self, index, field, value):
        cards = self.config.get("cards", [])
        if 0 <= index < len(cards):
            cards[index][field] = value
            self._notify()

    def _add_card(self):
        cards = self.config.get("cards", [])
        cards.append({"icon": "document", "title": "新功能", "description": "功能描述"})
        self.config["cards"] = cards
        self._refresh_cards()
        self._notify()

    def _remove_card(self, index):
        cards = self.config.get("cards", [])
        if 0 <= index < len(cards):
            cards.pop(index)
            self.config["cards"] = cards
            self._refresh_cards()
            self._notify()

    def collect(self):
        self.config["meta"]["title"] = self.title_entry.get()
        self.config["meta"]["subtitle"] = self.subtitle_box.get("1.0", "end-1c")
        self._parse_tags()

    def _notify(self):
        if self.on_change: self.on_change()
