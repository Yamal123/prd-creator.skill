"""
content_editor.py — 内容编辑面板
编辑每个 Tab 对应的 Markdown 内容文件
"""
import customtkinter as ctk
from .. import data


class ContentEditor(ctk.CTkFrame):
    """Markdown 内容编辑器"""

    def __init__(self, parent, config: dict, on_change=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_change = on_change
        self.current_tab_id = None
        self._build()

    def _build(self):
        selector_row = ctk.CTkFrame(self, fg_color="transparent")
        selector_row.pack(fill="x", pady=(12, 8))
        ctk.CTkLabel(selector_row, text="内容编辑", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

        self.tab_list = self._collect_markdown_tabs()
        labels = [t["label"] for t in self.tab_list] if self.tab_list else ["无 Markdown Tab"]

        self.tab_selector = ctk.CTkOptionMenu(
            selector_row, values=labels,
            width=160, height=30, font=ctk.CTkFont(size=12),
            command=self._on_tab_selected
        )
        self.tab_selector.pack(side="left", padx=(12, 8))

        # ---- 新建下拉 ----
        self.btn_new = ctk.CTkButton(selector_row, text="新建 ▼", width=70, height=28,
            font=ctk.CTkFont(size=11), command=lambda: self._show_menu(self.btn_new, [
                ("新建文件", self._new_file),
                ("导入文件", self._import_file),
            ]))
        self.btn_new.pack(side="right", padx=2)

        # ---- 打开下拉 ----
        self.btn_open = ctk.CTkButton(selector_row, text="打开 ▼", width=70, height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            command=lambda: self._show_menu(self.btn_open, [
                ("打开文件", self._open_file),
                ("打开目录", self._open_dir),
            ]))
        self.btn_open.pack(side="right", padx=2)

        # ---- 其它下拉 ----
        self.btn_other = ctk.CTkButton(selector_row, text="其它 ▼", width=70, height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            command=lambda: self._show_menu(self.btn_other, [
                ("重命名", self._rename_file),
                ("删除", self._delete_file),
            ]))
        self.btn_other.pack(side="right", padx=2)

        self.editor = ctk.CTkTextbox(self, height=400, font=ctk.CTkFont(size=13, family="monospace"), wrap="word")
        self.editor.pack(fill="both", expand=True, pady=(4, 8))
        self.editor.bind("<KeyRelease>", lambda e: self._on_edit())

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.status_label.pack(anchor="w")

        if self.tab_list:
            self._load_current_content()

    # ================================================================
    # 下拉菜单
    # ================================================================
    def _show_menu(self, trigger_btn, actions: list):
        """在按钮下方显示弹出菜单（CTkToplevel）"""
        menu = ctk.CTkToplevel(self)
        menu.overrideredirect(True)  # 无标题栏
        menu.configure(fg_color=("gray95", "gray17"))

        # 计算位置
        x = trigger_btn.winfo_rootx()
        y = trigger_btn.winfo_rooty() + trigger_btn.winfo_height() + 2
        menu.geometry(f"+{x}+{y}")

        # 按钮列表
        w = 0
        for label, cmd in actions:
            def make_cmd(c=cmd, m=menu):
                return lambda: [c(), m.destroy()]
            btn = ctk.CTkButton(menu, text=label, width=130, height=30,
                font=ctk.CTkFont(size=12), anchor="w",
                fg_color="transparent", text_color=("gray30", "gray80"),
                hover_color=("gray85", "gray25"),
                command=make_cmd()
            )
            btn.pack(fill="x", padx=4, pady=(4 if label == actions[0][0] else 0, 4 if label == actions[-1][0] else 0))
            w = max(w, 138)

        menu.update_idletasks()
        menu.geometry(f"{w}x{menu.winfo_reqheight()}+{x}+{y}")

        # 点击外部关闭
        menu.bind("<FocusOut>", lambda e: menu.destroy())
        menu.focus_set()

    # ================================================================
    # Tab 列表
    # ================================================================
    def _collect_markdown_tabs(self):
        result = []
        tc = self.config.get("tabs", {})
        for file_path in tc.get("files", []):
            parts = file_path.replace("\\", "/").split("/")
            fname = parts[-1] if parts else file_path
            tab_id = fname.rsplit(".", 1)[0]
            label = tab_id[0].upper() + tab_id[1:] if tab_id else fname
            result.append({"id": tab_id, "label": label, "file": file_path})
        for t in tc.get("extra", []):
            if t.get("type") == "markdown":
                result.append({"id": t["id"], "label": t.get("label", t["id"]), "file": t["file"]})
        return result

    def _on_tab_selected(self, label):
        self._load_current_content()

    def _get_selected_tab(self):
        selected_label = self.tab_selector.get()
        for t in self.tab_list:
            if t["label"] == selected_label:
                return t
        return None

    def _refresh_selector(self):
        self.tab_list = self._collect_markdown_tabs()
        labels = [t["label"] for t in self.tab_list] if self.tab_list else ["无 Markdown Tab"]
        self.tab_selector.configure(values=labels)
        if self.tab_list:
            self.tab_selector.set(self.tab_list[0]["label"])

    # ================================================================
    # 内容读写
    # ================================================================
    def _load_current_content(self):
        tab = self._get_selected_tab()
        if not tab:
            return
        self.current_tab_id = tab["id"]
        content = data.load_content(tab["file"], tab.get("id"))
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", content)
        self.status_label.configure(text=f"文件: {tab['file']} | 已加载 {len(content)} 字符")

    def _on_edit(self):
        content = self.editor.get("1.0", "end-1c")
        self.status_label.configure(text=f"已编辑 | {len(content)} 字符 | 未保存")

    def save_current(self):
        tab = self._get_selected_tab()
        if not tab:
            return False
        content = self.editor.get("1.0", "end-1c")
        ok = data.save_content(tab["file"], content, tab.get("id"))
        self.status_label.configure(text=f"已保存: {tab['file']} | {len(content)} 字符" if ok else f"保存失败: {tab['file']}")
        return ok

    # ================================================================
    # 新建 ──────────────────────────────────────────────────────────
    # ================================================================
    def _new_file(self):
        """创建新的 Markdown 文件"""
        from tkinter import simpledialog
        name = simpledialog.askstring("新建文件", "输入文件名（不含 .md 后缀）:", initialvalue="new")
        if not name:
            return

        fname = name + ".md" if not name.endswith(".md") else name
        folder = data.get_tabs_folder(self.config)
        if not folder.exists():
            folder.mkdir(parents=True)

        new_path = folder / fname
        if new_path.exists():
            self.status_label.configure(text=f"文件已存在: {fname}")
            return

        new_path.write_text(f"# {name}\n\n", encoding="utf-8")
        rel = str(new_path.relative_to(data.get_project_root()))

        # 加入 tabs.files
        tc = self.config.setdefault("tabs", {})
        tc.setdefault("files", []).append(rel)

        # 刷新选择器并选中新文件
        self._refresh_selector()
        self.tab_selector.set(name if name[0].isupper() else name[0].upper() + name[1:])
        self._load_current_content()
        self.status_label.configure(text=f"已创建: {rel}")
        if self.on_change:
            self.on_change()

    def _import_file(self):
        from tkinter import filedialog
        import shutil
        file_path = filedialog.askopenfilename(
            title="导入 Markdown 文件",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return

        # 复制到 tabs/ 目录
        folder = data.get_tabs_folder(self.config)
        if not folder.exists():
            folder.mkdir(parents=True)

        dest = folder / file_path.split("/")[-1]
        try:
            shutil.copy2(file_path, dest)
            rel = str(dest.relative_to(data.get_project_root()))
        except Exception as e:
            self.status_label.configure(text=f"导入失败: {e}")
            return

        # 加入 tabs.files
        tc = self.config.setdefault("tabs", {})
        files = tc.setdefault("files", [])
        if rel not in files:
            files.append(rel)

        self._refresh_selector()
        tab_id = dest.stem
        label = tab_id[0].upper() + tab_id[1:] if tab_id else dest.name
        # 尝试选中
        try:
            self.tab_selector.set(label)
        except Exception:
            pass
        self._load_current_content()
        self.status_label.configure(text=f"已导入: {rel}")
        if self.on_change:
            self.on_change()

    # ================================================================
    # 打开 ──────────────────────────────────────────────────────────
    # ================================================================
    def _open_file(self):
        import subprocess, platform
        tab = self._get_selected_tab()
        if not tab:
            return
        file_path = data.get_project_root() / tab["file"]
        if not file_path.exists():
            self.status_label.configure(text=f"文件不存在: {tab['file']}")
            return
        try:
            system = platform.system()
            if system == "Darwin":
                subprocess.run(["open", str(file_path)])
            elif system == "Windows":
                subprocess.run(["start", str(file_path)], shell=True)
            else:
                subprocess.run(["xdg-open", str(file_path)])
            self.status_label.configure(text=f"已打开: {tab['file']}")
        except Exception as e:
            self.status_label.configure(text=f"打开失败: {e}")

    def _open_dir(self):
        """打开 tabs 文件夹"""
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

    # ================================================================
    # 其它 ──────────────────────────────────────────────────────────
    # ================================================================
    def _rename_file(self):
        from tkinter import simpledialog
        tab = self._get_selected_tab()
        if not tab:
            return

        old_path = data.get_project_root() / tab["file"]
        current_name = old_path.name if old_path.exists() else tab["file"].split("/")[-1]

        new_name = simpledialog.askstring(
            "重命名文件", f"当前文件名: {current_name}\n输入新文件名（含 .md 后缀）:",
            initialvalue=current_name
        )
        if not new_name or new_name == current_name:
            return
        if not new_name.endswith(".md"):
            new_name += ".md"

        new_file = old_path.parent / new_name
        try:
            if old_path.exists():
                old_path.rename(new_file)
            self.status_label.configure(text=f"已重命名: {current_name} → {new_name}")
        except Exception as e:
            self.status_label.configure(text=f"重命名失败: {e}")
            return

        new_rel = str(new_file.relative_to(data.get_project_root()))
        tc = self.config.setdefault("tabs", {})

        # 更新 files 列表
        files = tc.get("files", [])
        for i, f in enumerate(files):
            if f == tab["file"]:
                files[i] = new_rel
                break
        # 更新 extra 列表
        for t in tc.get("extra", []):
            if t.get("file") == tab["file"]:
                t["file"] = new_rel
                break

        tab["file"] = new_rel
        tab["id"] = new_name.rsplit(".", 1)[0]
        self.current_tab_id = tab["id"]
        self._refresh_selector()
        self.tab_selector.set(tab["label"])
        if self.on_change:
            self.on_change()

    def _delete_file(self):
        """删除当前文件（带确认弹窗）"""
        tab = self._get_selected_tab()
        if not tab:
            return

        file_path = data.get_project_root() / tab["file"]
        fname = tab["file"].split("/")[-1]

        # 确认弹窗
        confirm = ctk.CTkToplevel(self)
        confirm.title("确认删除")
        confirm.geometry("340x180")
        confirm.resizable(False, False)
        confirm.transient(self)

        # 居中
        confirm.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 340) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 180) // 2
        confirm.geometry(f"+{x}+{y}")

        ctk.CTkLabel(confirm, text="确认删除文件",
            font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 4))
        ctk.CTkLabel(confirm, text=f"将删除: {fname}\n此操作不可撤销。",
            font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 16))

        btn_row = ctk.CTkFrame(confirm, fg_color="transparent")
        btn_row.pack()

        def do_delete():
            try:
                if file_path.exists():
                    file_path.unlink()
                # 从 config 中移除
                tc = self.config.setdefault("tabs", {})
                files = tc.get("files", [])
                if tab["file"] in files:
                    files.remove(tab["file"])
                extras = tc.get("extra", [])
                for i, t in enumerate(extras):
                    if t.get("file") == tab["file"]:
                        extras.pop(i)
                        break
                self.status_label.configure(text=f"已删除: {fname}")
                self._refresh_selector()
                self._load_current_content()
                if self.on_change:
                    self.on_change()
            except Exception as e:
                self.status_label.configure(text=f"删除失败: {e}")
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
