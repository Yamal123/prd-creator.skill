"""
site_info_panel.py — 网站信息面板
品牌色 · 网页名称 · Logo
"""
import customtkinter as ctk
from tkinter import colorchooser
from .. import data


class SiteInfoPanel(ctk.CTkFrame):

    COLOR_KEYS = [
        ("primary", "主品牌色", "按钮、链接、激活态"),
        ("light", "品牌浅色", "标签背景、浅底"),
        ("dark", "品牌深色", "按压态、深色背景"),
    ]

    def __init__(self, parent, config: dict, on_change=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_change = on_change
        self.swatches = []
        self._build()

    def _build(self):
        # ---- 品牌色 ----
        ctk.CTkLabel(self, text="品牌色", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(12, 8))
        brand = self.config.get("brand", {})

        for key, label, hint in self.COLOR_KEYS:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", pady=3)
            color = brand.get(key, "#E31E24")
            swatch = ctk.CTkFrame(row, width=32, height=32, corner_radius=6)
            swatch.pack(side="left", padx=(0, 10))
            try:
                swatch.configure(fg_color=color)
            except Exception:
                swatch.configure(fg_color="#E31E24")

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info, text=label, font=ctk.CTkFont(size=13)).pack(anchor="w")
            ctk.CTkLabel(info, text=hint, font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")

            entry = ctk.CTkEntry(row, width=90, height=28, font=ctk.CTkFont(size=12))
            entry.insert(0, color)
            entry.pack(side="right", padx=(0, 6))
            entry.bind("<KeyRelease>", lambda e, k=key, s=swatch: self._on_color_input(k, e.widget.get(), s))

            ctk.CTkButton(row, text="选色", width=50, height=28,
                font=ctk.CTkFont(size=11),
                command=lambda k=key, e=entry, s=swatch: self._open_picker(k, e, s)
            ).pack(side="right")
            self.swatches.append((key, swatch, entry))

        # 色板预览
        self.preview = ctk.CTkFrame(self, height=60, corner_radius=10)
        self.preview.pack(fill="x", pady=(8, 12))
        self._update_preview()

        ctk.CTkButton(self, text="恢复默认品牌色", width=140, height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"), command=self._reset
        ).pack(anchor="w")

        # ---- 网页名称 ----
        ctk.CTkLabel(self, text="网页名称（页面标题）", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(20, 6))
        self.title_entry = ctk.CTkEntry(self, height=34, font=ctk.CTkFont(size=14))
        self.title_entry.pack(fill="x")
        self.title_entry.insert(0, self.config["meta"].get("title", ""))
        self.title_entry.bind("<KeyRelease>", lambda e: self._update_title())

        # ---- 底部文案 ----
        ctk.CTkLabel(self, text="页面底部文案", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(20, 6))
        self.footer_entry = ctk.CTkEntry(self, height=34, font=ctk.CTkFont(size=14))
        self.footer_entry.pack(fill="x")
        self.footer_entry.insert(0, self.config.get("footer", {}).get("text", ""))
        self.footer_entry.bind("<KeyRelease>", lambda e: self._update_footer())

    def _on_color_input(self, key, value, swatch):
        value = value.strip()
        if value.startswith("#") and len(value) in [4, 7]:
            self.config.setdefault("brand", {})[key] = value
            try: swatch.configure(fg_color=value)
            except Exception: pass
            self._update_preview()
            self._notify()

    def _open_picker(self, key, entry, swatch):
        current = self.config.get("brand", {}).get(key, "#E31E24")
        color = colorchooser.askcolor(color=current, title=f"选择{key}")
        if color and color[1]:
            self.config.setdefault("brand", {})[key] = color[1]
            entry.delete(0, "end"); entry.insert(0, color[1])
            try: swatch.configure(fg_color=color[1])
            except Exception: pass
            self._update_preview()
            self._notify()

    def _update_preview(self):
        for w in self.preview.winfo_children():
            w.destroy()
        brand = self.config.get("brand", {})
        for color, label in [
            (brand.get("primary", "#E31E24"), "主色"),
            (brand.get("light", "#FDEBEC"), "浅色"),
            (brand.get("dark", "#B3151A"), "深色")
        ]:
            block = ctk.CTkFrame(self.preview, width=90, height=42, corner_radius=6)
            block.pack(side="left", padx=8, pady=9)
            try: block.configure(fg_color=color)
            except Exception: block.configure(fg_color="#ccc")
            ctk.CTkLabel(block, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white" if label == "主色" or label == "深色" else "black"
            ).place(relx=0.5, rely=0.5, anchor="center")

    def _reset(self):
        self.config["brand"] = {"primary": "#E31E24", "light": "#FDEBEC", "dark": "#B3151A"}
        for key, swatch, entry in self.swatches:
            val = self.config["brand"][key]
            entry.delete(0, "end"); entry.insert(0, val)
            try: swatch.configure(fg_color=val)
            except Exception: pass
        self._update_preview()
        self._notify()

    def _update_title(self):
        self.config["meta"]["title"] = self.title_entry.get()

    def _update_footer(self):
        self.config.setdefault("footer", {})["text"] = self.footer_entry.get()

    def collet(self):
        self.config["meta"]["title"] = self.title_entry.get()
        self.config.setdefault("footer", {})["text"] = self.footer_entry.get()

    def _notify(self):
        if self.on_change: self.on_change()
