"""
app.py — 管理客户端主窗口 · 三面板布局
网站信息 · 基础介绍 · 需求详情
"""
import customtkinter as ctk
import subprocess
import platform

from . import data
from .server import get_server, PreviewServer
from .preview_window import PreviewWindow
from .ui.site_info_panel import SiteInfoPanel
from .ui.intro_panel import IntroPanel
from .ui.requirements_panel import RequirementsPanel


class ManagerApp(ctk.CTk):
    """产品需求页面管理客户端"""

    def __init__(self):
        super().__init__()
        self.title("产品需求页面管理器")
        self.geometry("820x920")
        self.minsize(700, 750)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.config = data.load_config()
        data.sync_tabs_files(self.config)

        self.server: PreviewServer | None = None
        self.preview: PreviewWindow | None = None

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=12, pady=(12, 4))

        self.tabview.add("网站信息")
        self.tabview.add("基础介绍")
        self.tabview.add("需求详情")

        self.site_panel = SiteInfoPanel(self.tabview.tab("网站信息"), self.config, on_change=self._on_change)
        self.site_panel.pack(fill="both", expand=True)

        self.intro_panel = IntroPanel(self.tabview.tab("基础介绍"), self.config, on_change=self._on_change)
        self.intro_panel.pack(fill="both", expand=True)

        self.req_panel = RequirementsPanel(self.tabview.tab("需求详情"), self.config, on_change=self._on_change)
        self.req_panel.pack(fill="both", expand=True)

        self._build_bottom_bar()
        self.status_label = ctk.CTkLabel(self, text="就绪", font=ctk.CTkFont(size=11), text_color="gray")
        self.status_label.pack(pady=(0, 8))

    def _build_bottom_bar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=12, pady=(4, 8))

        brand = self.config.get("brand", {})
        self.preview_btn = ctk.CTkButton(
            bar, text="启动预览", width=120, height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=brand.get("primary", "#E31E24"),
            hover_color=brand.get("dark", "#B3151A"),
            command=self._toggle_preview
        )
        self.preview_btn.pack(side="left", padx=(0, 8))

        ctk.CTkButton(bar, text="保存全部", width=100, height=36,
            font=ctk.CTkFont(size=13), command=self._save_all).pack(side="left", padx=4)

        self.refresh_btn = ctk.CTkButton(
            bar, text="刷新预览", width=100, height=36,
            font=ctk.CTkFont(size=13),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            command=self._refresh_preview, state="disabled"
        )
        self.refresh_btn.pack(side="left", padx=4)

        ctk.CTkButton(bar, text="打开目录", width=100, height=36,
            font=ctk.CTkFont(size=13),
            fg_color="transparent", border_width=1, border_color=("gray70", "gray40"),
            text_color=("gray40", "gray70"),
            command=self._open_folder).pack(side="right")

    # ================================================================
    def _on_change(self):
        self.status_label.configure(text="已修改（未保存）")

    def _collect_all(self):
        self.site_panel.collet()
        self.intro_panel.collect()

    def _save_all(self):
        self._collect_all()
        data.sync_tabs_files(self.config)
        ok = data.save_config(self.config)
        self.req_panel.save_current()
        self.status_label.configure(text="配置已保存到 config.json" if ok else "保存失败")

    def _start_server(self):
        if self.server is None or not self.server.is_running:
            self.server = get_server(port=18900)
            self.server.start()
            self.status_label.configure(text=f"服务器已启动: {self.server.url}")

    def _toggle_preview(self):
        self._start_server()
        if self.preview is None:
            self.preview = PreviewWindow(port=18900)
        self._save_all()
        import webbrowser
        url = f"http://127.0.0.1:{self.server.port if self.server else 18900}"
        webbrowser.open(url)
        self.preview_btn.configure(text="刷新预览")
        self.refresh_btn.configure(state="normal")
        self.status_label.configure(text=f"预览已打开: {url}")

    def _refresh_preview(self):
        self._save_all()
        import webbrowser
        url = f"http://127.0.0.1:{self.server.port if self.server else 18900}"
        webbrowser.open(url)
        self.status_label.configure(text="预览已刷新")

    def _open_folder(self):
        root = str(data.get_project_root())
        try:
            if platform.system() == "Darwin":
                subprocess.run(["open", root])
            elif platform.system() == "Windows":
                subprocess.run(["explorer", root])
            else:
                subprocess.run(["xdg-open", root])
        except Exception:
            pass

    def _on_close(self):
        if self.server: self.server.stop()
        self.destroy()


def run():
    app = ManagerApp()
    app.mainloop()
