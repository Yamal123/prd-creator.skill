#!/usr/bin/env python3
"""
产品需求页面管理器 — 入口

启动 CustomTkinter 管理客户端，支持：
- 可视化编辑 config.json（标题、卡片、Tab、品牌色）
- 编辑 Markdown 内容文件
- 一键启动本地预览服务器 + pywebview 浏览器窗口

依赖安装：
    pip install customtkinter pywebview pillow watchdog --break-system-packages

运行：
    python manager/main.py
    或
    cd manager && python main.py
"""
import sys
import os

# 确保 manager 的父目录在 sys.path 中
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent not in sys.path:
    sys.path.insert(0, parent)

# 切换到项目根目录
os.chdir(parent)

if __name__ == "__main__":
    from manager.app import run
    run()
