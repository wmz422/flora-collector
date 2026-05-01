#!/usr/bin/env python3
"""
Flora Collector — 服务看门狗
每 5 分钟检查一次 API 健康状态，挂了自动重启
"""
import subprocess
import time
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python3"
SERVER_CMD = [
    str(VENV_PYTHON), "-m", "uvicorn",
    "src.flora_collector.main:app",
    "--host", "0.0.0.0",
    "--port", "8899",
    "--reload",
]

CHECK_INTERVAL = 180  # 3 分钟
HEALTH_URL = "http://localhost:8899/api/health"


def check_server() -> bool:
    import urllib.request
    try:
        resp = urllib.request.urlopen(HEALTH_URL, timeout=5)
        return resp.status == 200
    except Exception:
        return False


def restart_server():
    print(f"[{time.strftime('%H:%M:%S')}] Server down, restarting...")
    subprocess.Popen(
        SERVER_CMD,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Wait for it to start
    for i in range(30):
        if check_server():
            print(f"[{time.strftime('%H:%M:%S')}] Server restarted OK")
            return True
        time.sleep(1)
    print(f"[{time.strftime('%H:%M:%S')}] Server failed to restart!")
    return False


def main():
    print(f"Watchdog started (interval={CHECK_INTERVAL}s)")
    print(f"Project: {PROJECT_ROOT}")
    downs = 0
    while True:
        if not check_server():
            downs += 1
            print(f"[{time.strftime('%H:%M:%S')}] Down! (total: {downs})")
            restart_server()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
