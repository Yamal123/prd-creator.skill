"""
brand_panel.py — 品牌色配置面板
颜色选择器，实时预览色板
"""
import customtkinter as ctk
from tkinter import colorchooser


class BrandPanel(ctk.CTkFrame):
    """品牌色编辑面板"""

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
        # 颜色设置
        ctk.CTkLabel(self, text="品牌色配置", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(12, 8))

        brand = self.config.get("brand", {})

        for key, label, hint in self.COLOR_KEYS:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", pady=4)

            # 色块
            color = brand.get(key, "#E31E24")
            swatch = ctk.CTkFrame(row, width=36, height=36, corner_radius=6)
            swatch.pack(side="left", padx=(0, 10))
            try:
                # CustomTkinter doesn't support hex directly on CTkFrame, use configure
                swatch.configure(fg_color=color)
            except Exception:
                swatch.configure(fg_color="#E31E24")

            # 信息
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info, text=label, font=ctk.CTkFont(size=13)).pack(anchor="w")
            ctk.CTkLabel(info, text=hint, font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")

            # 颜色值 + 选择按钮
            entry = ctk.CTkEntry(row, width=90, height=28, font=ctk.CTkFont(size=12))
            entry.insert(0, color)
            entry.pack(side="right", padx=(0, 6))
            entry.bind("<KeyRelease>", lambda e, k=key, s=swatch: self._on_color_input(k, e.widget.get(), s))

            picker_btn = ctk.CTkButton(
                row, text="选色", width=50, height=28,
                font=ctk.CTkFont(size=11),
                command=lambda k=key, e=entry, s=swatch: self._open_color_picker(k, e, s)
            )
            picker_btn.pack(side="right")

            self.swatches.append((key, swatch, entry))

        # 预览色板
        ctk.CTkLabel(self, text="预览色板", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(16, 8))

        self.preview_frame = ctk.CTkFrame(self, height=80, corner_radius=10)
        self.preview_frame.pack(fill="x", pady=(0, 8))
        self._update_preview()

        # 恢复默认
        ctk.CTkButton(
            self, text="恢复默认品牌色", width=140, height=30,
            font=ctk.CTkFont(size=12),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            command=self._reset_defaults
        ).pack(pady=(4, 12))

    def _on_color_input(self, key, value, swatch):
        """手动输入颜色值"""
        value = value.strip()
        if value.startswith("#") and len(value) in [4, 7]:
            self.config.setdefault("brand", {})[key] = value
            try:
                swatch.configure(fg_color=value)
            except Exception:
                pass
            self._update_preview()
            self._notify()

    def _open_color_picker(self, key, entry, swatch):
        """打开系统颜色选择器"""
        current = self.config.get("brand", {}).get(key, "#E31E24")
        color = colorchooser.askcolor(color=current, title=f"选择{key}")
        if color and color[1]:
            hex_color = color[1]
            self.config.setdefault("brand", {})[key] = hex_color
            entry.delete(0, "end")
            entry.insert(0, hex_color)
            try:
                swatch.configure(fg_color=hex_color)
            except Exception:
                pass
            self._update_preview()
            self._notify()

    def _update_preview(self):
        """更新色板预览"""
        brand = self.config.get("brand", {})
        primary = brand.get("primary", "#E31E24")
        light = brand.get("light", "#FDEBEC")
        dark = brand.get("dark", "#B3151A")

        for w in self.preview_frame.winfo_children():
            w.destroy()

        # 三个色块
        for i, (color, label) in enumerate([
            (primary, "主色"), (light, "浅色"), (dark, "深色")
        ]):
            block = ctk.CTkFrame(self.preview_frame, width=80, height=50, corner_radius=6)
            block.pack(side="left", padx=10, pady=15)
            try:
                block.configure(fg_color=color)
            except Exception:
                block.configure(fg_color="#ccc")
            ctk.CTkLabel(block, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="white" if i != 1 else "black").place(relx=0.5, rely=0.5, anchor="center")

    def _reset_defaults(self):
        """恢复默认品牌色"""
        self.config["brand"] = {
            "primary": "#E31E24",
            "light": "#FDEBEC",
            "dark": "#B3151A"
        }
        for key, swatch, entry in self.swatches:
            val = self.config["brand"][key]
            entry.delete(0, "end")
            entry.insert(0, val)
            try:
                swatch.configure(fg_color=val)
            except Exception:
                pass
        self._update_preview()
        self._notify()

    def _notify(self):
        if self.on_change:
            self.on_change()
