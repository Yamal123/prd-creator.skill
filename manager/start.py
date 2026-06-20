#!/usr/bin/env python3
"""PRD 页面 — 启动服务器"""
import sys, os, webbrowser
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
manager_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
sys.path.insert(0, manager_dir)
from server import start

if __name__ == "__main__":
    s = start()
    webbrowser.open(s.url + "/prd/manager/")
    print("按 Ctrl+C 停止")
    try:
        import time
        while True: time.sleep(1)
    except KeyboardInterrupt:
        s.stop()
        print("已停止")
