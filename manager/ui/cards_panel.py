"""
cards_panel.py — 首页功能卡片编辑面板
管理 6 张核心功能卡片的图标、标题、描述
"""
import customtkinter as ctk
from .. import data


class CardsPanel(ctk.CTkFrame):
    """首页卡片编辑面板"""

    def __init__(self, parent, config: dict, on_change=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_change = on_change
        self.card_rows = []

        self._build()

    def _build(self):
        # 标题行
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(12, 8))
        ctk.CTkLabel(header, text="首页功能卡片", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        ctk.CTkButton(
            header, text="+ 添加", width=70, height=28,
            font=ctk.CTkFont(size=11), command=self._add_card
        ).pack(side="right")

        # 卡片列表
        self.cards_container = ctk.CTkScrollableFrame(self, height=400, fg_color="transparent")
        self.cards_container.pack(fill="both", expand=True)
        self._refresh_cards()

    def _refresh_cards(self):
        for row in self.card_rows:
            row[0].destroy()
        self.card_rows.clear()

        cards = self.config.get("cards", [])
        for i, card in enumerate(cards):
            self._create_card_row(i, card)

    def _create_card_row(self, index, card):
        frame = ctk.CTkFrame(self.cards_container, fg_color=("gray95", "gray17"), corner_radius=8)
        frame.pack(fill="x", pady=4, padx=2)

        # 第一行：序号 + 删除按钮
        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(top, text=f"卡片 {index + 1}", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        ctk.CTkButton(
            top, text="✕ 删除", width=60, height=24,
            fg_color="#fee2e2", text_color="#dc2626",
            hover_color="#fecaca", font=ctk.CTkFont(size=11),
            command=lambda idx=index: self._remove_card(idx)
        ).pack(side="right")

        # 图标选择
        icon_row = ctk.CTkFrame(frame, fg_color="transparent")
        icon_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(icon_row, text="图标", width=40, font=ctk.CTkFont(size=12)).pack(side="left")
        icon_menu = ctk.CTkOptionMenu(
            icon_row, values=data.AVAILABLE_ICONS,
            width=140, height=28, font=ctk.CTkFont(size=12),
            command=lambda v, idx=index: self._update_card_field(idx, "icon", v)
        )
        icon_menu.pack(side="left")
        current_icon = card.get("icon", "document")
        if current_icon in data.AVAILABLE_ICONS:
            icon_menu.set(current_icon)

        # 标题
        title_row = ctk.CTkFrame(frame, fg_color="transparent")
        title_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(title_row, text="标题", width=40, font=ctk.CTkFont(size=12)).pack(side="left")
        title_entry = ctk.CTkEntry(title_row, height=28, font=ctk.CTkFont(size=13))
        title_entry.pack(side="left", fill="x", expand=True)
        title_entry.insert(0, card.get("title", ""))
        title_entry.bind("<KeyRelease>", lambda e, idx=index: self._update_card_field(idx, "title", e.widget.get()))

        # 描述
        desc_row = ctk.CTkFrame(frame, fg_color="transparent")
        desc_row.pack(fill="x", padx=10, pady=(2, 8))
        ctk.CTkLabel(desc_row, text="描述", width=40, font=ctk.CTkFont(size=12)).pack(side="left")
        desc_entry = ctk.CTkEntry(desc_row, height=28, font=ctk.CTkFont(size=12))
        desc_entry.pack(side="left", fill="x", expand=True)
        desc_entry.insert(0, card.get("description", ""))
        desc_entry.bind("<KeyRelease>", lambda e, idx=index: self._update_card_field(idx, "description", e.widget.get()))

        self.card_rows.append((frame, icon_menu, title_entry, desc_entry))

    def _update_card_field(self, index, field, value):
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

    def _notify(self):
        if self.on_change:
            self.on_change()
