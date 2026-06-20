"""
requirements_panel.py — 需求详情面板
Tab 管理（简化列表） + 选择 Tab 编辑内容（Markdown / JSON）
"""
import customtkinter as ctk
import shutil
from pathlib import Path
from .. import data


class RequirementsPanel(ctk.CTkFrame):

    def __init__(self, parent, config: dict, on_change=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_change = on_change
        self._build()

    def _build(self):
        # ---- Tab 管理（简化：数量 + 刷新扫描 + 打开文件夹） ----
        ctk.CTkLabel(self, text="Tab 管理", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(12, 6))

        tab_header = ctk.CTkFrame(self, fg_color="transparent")
        tab_header.pack(fill="x", pady=(0, 6))

        tc = self.config.get("tabs", {})
        auto_count = len(tc.get("files", []))
        extra_count = len(tc.get("extra", []))
        self.tab_count_label = ctk.CTkLabel(tab_header,
            text=f"共 {auto_count + extra_count} 个 Tab（自动: {auto_count}，其它: {extra_count}）",
            font=ctk.CTkFont(size=13))
        self.tab_count_label.pack(side="left")

        ctk.CTkButton(tab_header, text="打开文件夹", width=90, height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            command=self._open_tabs_folder).pack(side="right", padx=2)

        ctk.CTkButton(tab_header, text="刷新扫描", width=80, height=28,
            font=ctk.CTkFont(size=11), command=self._refresh).pack(side="right", padx=2)

        # ---- 分隔线 ----
        sep = ctk.CTkFrame(self, height=1, fg_color=("gray85", "gray25"))
        sep.pack(fill="x", pady=8)

        # ---- 内容编辑 ----
        edit_header = ctk.CTkFrame(self, fg_color="transparent")
        edit_header.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(edit_header, text="内容编辑", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        # Tab 选择器
        self.tab_list = self._collect_all_tabs()
        labels = [t["label"] for t in self.tab_list] if self.tab_list else ["无可用 Tab"]
        self.tab_selector = ctk.CTkOptionMenu(edit_header, values=labels,
            width=180, height=28, font=ctk.CTkFont(size=12), command=self._on_tab_selected)
        self.tab_selector.pack(side="left", padx=(12, 4))

        # 操作按钮行
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", pady=(4, 4))

        # 新建 ▼
        ctk.CTkButton(btn_row, text="新建 ▼", width=70, height=28, font=ctk.CTkFont(size=11),
            command=lambda: self._popup_menu(self._new_menu_widget, [
                ("新建 Markdown", lambda: self._new_tab("markdown")),
                ("新建 JSON 配置", lambda: self._new_tab("pages")),
                ("上传文件", self._upload_file),
            ])).pack(side="left", padx=2)

        # 打开 ▼
        ctk.CTkButton(btn_row, text="打开 ▼", width=70, height=28, font=ctk.CTkFont(size=11),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            command=lambda: self._popup_menu(self._open_menu_widget, [
                ("打开文件", self._open_file),
                ("打开目录", self._open_dir),
            ])).pack(side="left", padx=2)

        # 其它 ▼
        ctk.CTkButton(btn_row, text="其它 ▼", width=70, height=28, font=ctk.CTkFont(size=11),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            command=lambda: self._popup_menu(self._other_menu_widget, [
                ("重命名", self._rename_tab),
                ("删除", self._delete_tab),
            ])).pack(side="left", padx=2)

        ctk.CTkButton(btn_row, text="保存", width=60, height=28,
            font=ctk.CTkFont(size=11),
            fg_color=self.config["brand"].get("primary", "#E31E24"),
            command=self.save_current).pack(side="right", padx=2)

        # 编辑器
        self.editor = ctk.CTkTextbox(self, height=340, font=ctk.CTkFont(size=13, family="monospace"), wrap="word")
        self.editor.pack(fill="both", expand=True, pady=(4, 4))
        self.editor.bind("<KeyRelease>", lambda e: self._on_edit())

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.status_label.pack(anchor="w")

        if self.tab_list:
            self._load_current()

    # ================================================================
    # 下拉菜单
    # ================================================================
    def _popup_menu(self, ref_btn, actions: list):
        menu = ctk.CTkToplevel(self)
        menu.overrideredirect(True)
        menu.configure(fg_color=("gray95", "gray17"))

        x = ref_btn.winfo_rootx()
        y = ref_btn.winfo_rooty() + ref_btn.winfo_height() + 2
        menu.geometry(f"+{x}+{y}")

        for i, (label, cmd) in enumerate(actions):
            is_first = (i == 0)
            is_last = (i == len(actions) - 1)
            def make_cmd(c=cmd, m=menu): return lambda: [c(), m.destroy()]
            ctk.CTkButton(menu, text=label, width=140, height=30,
                font=ctk.CTkFont(size=12), anchor="w",
                fg_color="transparent", text_color=("gray30", "gray80"),
                hover_color=("gray85", "gray25"),
                command=make_cmd()
            ).pack(fill="x", padx=4, pady=(4 if is_first else 0, 4 if is_last else 0))

        menu.update_idletasks()
        menu.geometry(f"{menu.winfo_reqwidth()}x{menu.winfo_reqheight()}+{x}+{y}")
        menu.bind("<FocusOut>", lambda e: menu.destroy())
        menu.focus_set()

    # ================================================================
    # Tab 列表
    # ================================================================
    def _collect_all_tabs(self):
        result = []
        tc = self.config.get("tabs", {})
        for fp in tc.get("files", []):
            parts = fp.replace("\\", "/").split("/")
            fname = parts[-1] if parts else fp
            tid = fname.rsplit(".", 1)[0]
            result.append({"id": tid, "label": fname, "file": fp, "type": "markdown"})
        for t in tc.get("extra", []):
            result.append({"id": t["id"], "label": t.get("label", t["id"]), "file": t["file"], "type": t.get("type", "markdown")})
        return result

    def _refresh_selector(self):
        self.tab_list = self._collect_all_tabs()
        labels = [t["label"] for t in self.tab_list] if self.tab_list else ["无可用 Tab"]
        self.tab_selector.configure(values=labels)
        if self.tab_list:
            self.tab_selector.set(self.tab_list[0]["label"])

    def _refresh_counts(self):
        tc = self.config.get("tabs", {})
        auto = len(tc.get("files", []))
        extra = len(tc.get("extra", []))
        self.tab_count_label.configure(text=f"共 {auto + extra} 个 Tab（自动: {auto}，其它: {extra}）")

    def _on_tab_selected(self, label):
        self._load_current()

    def _get_selected(self):
        sel = self.tab_selector.get()
        for t in self.tab_list:
            if t["label"] == sel:
                return t
        return None

    def _load_current(self):
        tab = self._get_selected()
        if not tab:
            return
        content = data.load_content(tab["file"], tab.get("id"))
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", content)
        self.status_label.configure(text=f"文件: {tab['file']} | {len(content)} 字符")

    def _on_edit(self):
        content = self.editor.get("1.0", "end-1c")
        self.status_label.configure(text=f"已编辑 | {len(content)} 字符 | 未保存")

    def save_current(self):
        tab = self._get_selected()
        if not tab:
            return False
        content = self.editor.get("1.0", "end-1c")
        ok = data.save_content(tab["file"], content, tab.get("id"))
        self.status_label.configure(text=f"已保存: {tab['file']} | {len(content)} 字符" if ok else f"保存失败")
        return ok

    # ================================================================
    # 新建 & 上传
    # ================================================================
    def _new_tab(self, tab_type="markdown"):
        from tkinter import simpledialog
        ext = ".json" if tab_type == "pages" else ".md"
        name = simpledialog.askstring("新建 Tab", f"输入文件名（不含{ext}后缀）:", initialvalue="new")
        if not name:
            return
        if not name.endswith(ext):
            name += ext

        folder = data.get_tabs_folder(self.config)
        if not folder.exists():
            folder.mkdir(parents=True)

        new_path = folder / name
        if new_path.exists():
            self.status_label.configure(text=f"文件已存在: {name}")
            return

        if tab_type == "pages":
            new_path.write_text('{"sections":[]}', encoding="utf-8")
        else:
            new_path.write_text(f"# {name.rsplit('.', 1)[0]}\n\n", encoding="utf-8")

        rel = str(new_path.relative_to(data.get_project_root()))
        tc = self.config.setdefault("tabs", {})
        tc.setdefault("files", []).append(rel)

        self._refresh_selector()
        self._refresh_counts()
        self.tab_selector.set(name)
        self._load_current()
        self.status_label.configure(text=f"已创建: {rel}")
        if self.on_change: self.on_change()

    def _upload_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="上传文件",
            filetypes=[("Markdown", "*.md"), ("JSON", "*.json"), ("Text", "*.txt"), ("All", "*.*")]
        )
        if not path:
            return
        folder = data.get_tabs_folder(self.config)
        if not folder.exists():
            folder.mkdir(parents=True)

        dest = folder / path.split("/")[-1]
        try:
            shutil.copy2(path, dest)
            rel = str(dest.relative_to(data.get_project_root()))
        except Exception as e:
            self.status_label.configure(text=f"上传失败: {e}")
            return

        tc = self.config.setdefault("tabs", {})
        files = tc.setdefault("files", [])
        if rel not in files:
            files.append(rel)

        self._refresh_selector()
        self._refresh_counts()
        self.tab_selector.set(dest.name)
        self._load_current()
        self.status_label.configure(text=f"已上传: {rel}")
        if self.on_change: self.on_change()

    # ================================================================
    # 打开
    # ================================================================
    def _open_file(self):
        import subprocess, platform
        tab = self._get_selected()
        if not tab: return
        fp = data.get_project_root() / tab["file"]
        if not fp.exists():
            self.status_label.configure(text=f"文件不存在: {tab['file']}")
            return
        try:
            system = platform.system()
            if system == "Darwin": subprocess.run(["open", str(fp)])
            elif system == "Windows": subprocess.run(["start", str(fp)], shell=True)
            else: subprocess.run(["xdg-open", str(fp)])
            self.status_label.configure(text=f"已打开: {tab['file']}")
        except Exception as e:
            self.status_label.configure(text=f"打开失败: {e}")

    def _open_dir(self):
        import subprocess, platform
        folder = data.get_tabs_folder(self.config)
        if not folder.exists(): folder.mkdir(parents=True)
        try:
            system = platform.system()
            if system == "Darwin": subprocess.run(["open", str(folder)])
            elif system == "Windows": subprocess.run(["explorer", str(folder)])
            else: subprocess.run(["xdg-open", str(folder)])
        except Exception: pass

    def _open_tabs_folder(self):
        self._open_dir()

    # ================================================================
    # 重命名 & 删除
    # ================================================================
    def _rename_tab(self):
        from tkinter import simpledialog
        tab = self._get_selected()
        if not tab: return

        old_path = data.get_project_root() / tab["file"]
        current_name = old_path.name if old_path.exists() else tab["file"].split("/")[-1]

        new_name = simpledialog.askstring("重命名", f"当前: {current_name}\n新文件名:", initialvalue=current_name)
        if not new_name or new_name == current_name:
            return

        new_file = old_path.parent / new_name
        try:
            if old_path.exists(): old_path.rename(new_file)
        except Exception as e:
            self.status_label.configure(text=f"重命名失败: {e}")
            return

        new_rel = str(new_file.relative_to(data.get_project_root()))
        tc = self.config.setdefault("tabs", {})

        files = tc.get("files", [])
        for i, f in enumerate(files):
            if f == tab["file"]:
                files[i] = new_rel
                break
        for t in tc.get("extra", []):
            if t.get("file") == tab["file"]:
                t["file"] = new_rel
                break

        tab["file"] = new_rel
        self._refresh_selector()
        self._refresh_counts()
        self.tab_selector.set(new_name)
        self._load_current()
        self.status_label.configure(text=f"已重命名: {current_name} → {new_name}")
        if self.on_change: self.on_change()

    def _delete_tab(self):
        tab = self._get_selected()
        if not tab: return

        file_path = data.get_project_root() / tab["file"]
        fname = tab["file"].split("/")[-1]

        confirm = ctk.CTkToplevel(self)
        confirm.title("确认删除")
        confirm.geometry("340x180")
        confirm.resizable(False, False)
        confirm.transient(self)
        confirm.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 340) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 180) // 2
        confirm.geometry(f"+{x}+{y}")

        ctk.CTkLabel(confirm, text="确认删除 Tab", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 4))
        ctk.CTkLabel(confirm, text=f"将删除: {fname}\n此操作不可撤销。",
            font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 16))

        btn_row = ctk.CTkFrame(confirm, fg_color="transparent")
        btn_row.pack()

        def do_delete():
            try:
                if file_path.exists(): file_path.unlink()
            except Exception: pass
            tc = self.config.setdefault("tabs", {})
            files = tc.get("files", [])
            if tab["file"] in files:
                files.remove(tab["file"])
            extras = tc.get("extra", [])
            for i, t in enumerate(extras):
                if t.get("file") == tab["file"]:
                    extras.pop(i)
                    break
            self._refresh_selector()
            self._refresh_counts()
            self._load_current()
            self.status_label.configure(text=f"已删除: {fname}")
            if self.on_change: self.on_change()
            confirm.destroy()

        ctk.CTkButton(btn_row, text="确认删除", width=100, height=32,
            fg_color="#dc2626", hover_color="#b91c1c",
            font=ctk.CTkFont(size=13), command=do_delete).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="取消", width=80, height=32,
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            font=ctk.CTkFont(size=13), command=confirm.destroy).pack(side="left", padx=6)
        confirm.focus_set()
        confirm.grab_set()

    # ================================================================
    # 刷新
    # ================================================================
    def _refresh(self):
        data.sync_tabs_files(self.config)
        self._refresh_selector()
        self._refresh_counts()
        self.status_label.configure(text="已刷新扫描")
        if self.on_change: self.on_change()
