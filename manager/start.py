#!/usr/bin/env python3
"""PRD 页面 — 启动服务器
部署模式: python3 prd/manager/start.py → 访问 /prd/ 和 /prd/manager/
开发模式: python3 manager/start.py → 访问 / 和 /manager/
"""
import sys, os, webbrowser

# manager 目录
manager_dir = os.path.dirname(os.path.abspath(__file__))
# 项目根目录（向上两级：manager → prd → project）
project_root = os.path.dirname(os.path.dirname(manager_dir))
os.chdir(project_root)
sys.path.insert(0, manager_dir)

from server import start, PRD_ROOT

if __name__ == "__main__":
    s = start()
    in_prd = PRD_ROOT.name == "prd"
    prefix = "/prd" if in_prd else ""
    webbrowser.open(s.url + prefix + "/manager/")
    print(f"PRD: {s.url}{prefix}/")
    print(f"后台: {s.url}{prefix}/manager/")
    print("按 Ctrl+C 停止")
    try:
        import time
        while True: time.sleep(1)
    except KeyboardInterrupt:
        s.stop()
        print("已停止")
