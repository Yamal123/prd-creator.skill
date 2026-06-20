"""
preview_window.py — 系统浏览器预览
使用系统默认浏览器打开页面，通过 AppleScript / subprocess 实现刷新
"""
import webbrowser
import subprocess
import platform
from .server import get_server


class PreviewWindow:
    """预览窗口管理器（系统浏览器）"""

    def __init__(self, port: int = 18900):
        self.port = port
        self._open = False

    @property
    def is_open(self) -> bool:
        return self._open

    def open(self, server=None):
        """打开系统浏览器预览"""
        if server is None:
            server = get_server(self.port)
        if not server.is_running:
            server.start()

        url = f"http://127.0.0.1:{self.port}"
        webbrowser.open(url)
        self._open = True

    def reload(self):
        """刷新浏览器页面（macOS 用 AppleScript）"""
        system = platform.system()
        try:
            if system == "Darwin":
                # macOS: 用 AppleScript 刷新 Safari/Chrome 当前标签页
                subprocess.run([
                    "osascript", "-e",
                    'tell application "Safari" to do JavaScript "location.reload()" in current tab of front window'
                ], timeout=5)
            # 其他系统：无法远程刷新，用户手动刷新即可
        except Exception:
            pass  # 静默失败，用户手动刷新

    def close(self):
        """关闭预览（浏览器窗口不强制关闭，由用户管理）"""
        self._open = False
