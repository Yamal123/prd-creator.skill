"""
tabs_panel.py — Tab 管理面板
自动扫描 tabs/ 文件夹 + 额外 Tab（如"产品介绍"）
"""
import customtkinter as ctk
from .. import data


class TabsPanel(ctk.CTkFrame):
    """Tab 管理面板"""

    def __init__(self, parent, config: dict, on_change=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_change = on_change
        self.extra_rows = []
        self._build()

    def _build(self):
        # ---- 自动发现区域 ----
        ctk.CTkLabel(self, text="自动发现（tabs/ 文件夹）", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(12, 4))

        info_row = ctk.CTkFrame(self, fg_color="transparent")
        info_row.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(info_row, text="文件夹:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.folder_entry = ctk.CTkEntry(info_row, width=120, height=28, font=ctk.CTkFont(size=12))
        self.folder_entry.pack(side="left", padx=8)
        self.folder_entry.insert(0, self.config.get("tabs", {}).get("folder", "tabs"))
        self.folder_entry.bind("<KeyRelease>", lambda e: self._update_folder())

        ctk.CTkButton(
            info_row, text="刷新扫描", width=80, height=28,
            font=ctk.CTkFont(size=11), command=self._refresh_scan
        ).pack(side="right", padx=(4, 0))

        ctk.CTkButton(
            info_row, text="打开文件夹", width=80, height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            command=self._open_folder
        ).pack(side="right")

        self.auto_list = ctk.CTkScrollableFrame(self, height=120, fg_color=("gray95", "gray17"))
        self.auto_list.pack(fill="x", pady=(4, 8))
        self._refresh_auto_display()

        # ---- 其它 Tab 区域 ----
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(8, 4))
        ctk.CTkLabel(header, text="其它 Tab", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

        ctk.CTkButton(
            header, text="+ 添加", width=70, height=28,
            font=ctk.CTkFont(size=11), command=self._add_extra
        ).pack(side="right")

        ctk.CTkButton(
            header, text="扫描", width=60, height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            command=self._scan_extra
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            header, text="打开文件夹", width=80, height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            command=self._open_project_folder
        ).pack(side="right", padx=4)

        self.extra_container = ctk.CTkScrollableFrame(self, height=200, fg_color="transparent")
        self.extra_container.pack(fill="both", expand=True)
        self._refresh_extra()

    def _refresh_scan(self):
        """重新扫描文件夹"""
        self._update_folder()
        data.sync_tabs_files(self.config)
        self._refresh_auto_display()
        self._notify()

    def _open_folder(self):
        """在 Finder 中打开 tabs 文件夹"""
        import subprocess, platform
        folder = data.get_tabs_folder(self.config)
        if not folder.exists():
            folder.mkdir(parents=True)
        try:
            system = platform.system()
            if system == "Darwin":
                subprocess.run(["open", str(folder)])
            elif system == "Windows":
                subprocess.run(["explorer", str(folder)])
            else:
                subprocess.run(["xdg-open", str(folder)])
        except Exception:
            pass

    def _open_project_folder(self):
        """打开项目根目录"""
        import subprocess, platform
        folder = data.get_project_root()
        try:
            system = platform.system()
            if system == "Darwin":
                subprocess.run(["open", str(folder)])
            elif system == "Windows":
                subprocess.run(["explorer", str(folder)])
            else:
                subprocess.run(["xdg-open", str(folder)])
        except Exception:
            pass

    def _scan_extra(self):
        """扫描项目根目录的 .md 和 .json 文件，自动添加到其它 Tab"""
        from pathlib import Path
        root = data.get_project_root()
        existing_files = set()
        for t in self.config.get("tabs", {}).get("extra", []):
            existing_files.add(t.get("file", ""))

        # 扫描根目录下非隐藏的 .md/.json 文件
        added = 0
        for f in sorted(root.glob("*.md")):
            rel = str(f.relative_to(root))
            if rel not in existing_files:
                tab_id = f.stem
                self.config.setdefault("tabs", {}).setdefault("extra", []).append({
                    "id": tab_id,
                    "label": tab_id[0].upper() + tab_id[1:] if tab_id else f.name,
                    "file": rel,
                    "type": "markdown"
                })
                existing_files.add(rel)
                added += 1

        for f in sorted(root.glob("*.json")):
            if f.name == "config.json":
                continue  # 跳过 config.json
            rel = str(f.relative_to(root))
            if rel not in existing_files:
                tab_id = f.stem
                self.config.setdefault("tabs", {}).setdefault("extra", []).append({
                    "id": tab_id,
                    "label": tab_id[0].upper() + tab_id[1:] if tab_id else f.name,
                    "file": rel,
                    "type": "pages" if f.stem == "pages" else "markdown"
                })
                existing_files.add(rel)
                added += 1

        self._refresh_extra()
        if added > 0:
            self._notify()

    def _update_folder(self):
        """更新文件夹路径"""
        self.config.setdefault("tabs", {})["folder"] = self.folder_entry.get()

    def _refresh_auto_display(self):
        """显示自动扫描的文件列表"""
        for w in self.auto_list.winfo_children():
            w.destroy()

        files = self.config.get("tabs", {}).get("files", [])
        if not files:
            ctk.CTkLabel(self.auto_list, text="（暂无文件，点击刷新扫描）",
                         font=ctk.CTkFont(size=12), text_color="gray").pack(pady=10)
            return

        for f in files:
            row = ctk.CTkFrame(self.auto_list, fg_color="transparent")
            row.pack(fill="x", pady=2)
            # 文件名
            parts = f.replace("\\", "/").split("/")
            fname = parts[-1] if parts else f
            tab_id = fname.rsplit(".", 1)[0]
            label = tab_id[0].upper() + tab_id[1:] if tab_id else fname

            ctk.CTkLabel(row, text=f"📄 {label}", font=ctk.CTkFont(size=12)).pack(side="left")
            ctk.CTkLabel(row, text=f, font=ctk.CTkFont(size=11), text_color="gray").pack(side="left", padx=8)

    def _refresh_extra(self):
        """刷新额外 Tab 列表"""
        for row in self.extra_rows:
            row[0].destroy()
        self.extra_rows.clear()

        extras = self.config.get("tabs", {}).get("extra", [])
        for i, tab in enumerate(extras):
            self._create_extra_row(i, tab)

    def _create_extra_row(self, index, tab):
        frame = ctk.CTkFrame(self.extra_container, fg_color=("gray95", "gray17"), corner_radius=8)
        frame.pack(fill="x", pady=3, padx=2)

        # 删除按钮
        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(top, text=f"Tab {index + 1}", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        ctk.CTkButton(
            top, text="✕ 删除", width=60, height=24,
            fg_color="#fee2e2", text_color="#dc2626",
            hover_color="#fecaca", font=ctk.CTkFont(size=11),
            command=lambda idx=index: self._remove_extra(idx)
        ).pack(side="right")

        # ID
        id_row = ctk.CTkFrame(frame, fg_color="transparent")
        id_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(id_row, text="ID", width=40, font=ctk.CTkFont(size=12)).pack(side="left")
        e_id = ctk.CTkEntry(id_row, height=28, font=ctk.CTkFont(size=13))
        e_id.pack(side="left", fill="x", expand=True)
        e_id.insert(0, tab.get("id", ""))
        e_id.bind("<KeyRelease>", lambda e, i=index: self._update_extra(i, "id", e.widget.get()))

        # 标签
        lbl_row = ctk.CTkFrame(frame, fg_color="transparent")
        lbl_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(lbl_row, text="名称", width=40, font=ctk.CTkFont(size=12)).pack(side="left")
        e_lbl = ctk.CTkEntry(lbl_row, height=28, font=ctk.CTkFont(size=13))
        e_lbl.pack(side="left", fill="x", expand=True)
        e_lbl.insert(0, tab.get("label", ""))
        e_lbl.bind("<KeyRelease>", lambda e, i=index: self._update_extra(i, "label", e.widget.get()))

        # 文件
        file_row = ctk.CTkFrame(frame, fg_color="transparent")
        file_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(file_row, text="文件", width=40, font=ctk.CTkFont(size=12)).pack(side="left")
        e_file = ctk.CTkEntry(file_row, height=28, font=ctk.CTkFont(size=13))
        e_file.pack(side="left", fill="x", expand=True)
        e_file.insert(0, tab.get("file", ""))
        e_file.bind("<KeyRelease>", lambda e, i=index: self._update_extra(i, "file", e.widget.get()))

        # 类型
        type_row = ctk.CTkFrame(frame, fg_color="transparent")
        type_row.pack(fill="x", padx=10, pady=(2, 8))
        ctk.CTkLabel(type_row, text="类型", width=40, font=ctk.CTkFont(size=12)).pack(side="left")
        m = ctk.CTkOptionMenu(
            type_row, values=data.TAB_TYPES, width=120, height=28,
            font=ctk.CTkFont(size=12),
            command=lambda v, i=index: self._update_extra(i, "type", v)
        )
        m.pack(side="left")
        ct = tab.get("type", "markdown")
        if ct in data.TAB_TYPES:
            m.set(ct)

        self.extra_rows.append((frame, e_id, e_lbl, e_file, m))

    def _update_extra(self, index, field, value):
        extras = self.config.get("tabs", {}).get("extra", [])
        if 0 <= index < len(extras):
            extras[index][field] = value
            self._notify()

    def _add_extra(self):
        self.config.setdefault("tabs", {}).setdefault("extra", [])
        extras = self.config["tabs"]["extra"]
        extras.append({"id": "new_tab", "label": "新页面", "file": "new.md", "type": "markdown"})
        self._refresh_extra()
        self._notify()

    def _remove_extra(self, index):
        extras = self.config.get("tabs", {}).get("extra", [])
        if 0 <= index < len(extras):
            extras.pop(index)
            self._refresh_extra()
            self._notify()

    def _notify(self):
        if self.on_change:
            self.on_change()
