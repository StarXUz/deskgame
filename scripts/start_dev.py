import os
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173


def local_ip() -> str:
    for interface in ("en0", "en1"):
        try:
            value = subprocess.check_output(
                ["ipconfig", "getifaddr", interface],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if value:
                return value
        except Exception:
            pass
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def stream_output(name: str, process: subprocess.Popen[str]) -> None:
    assert process.stdout is not None
    for line in process.stdout:
        print(f"[{name}] {line}", end="", flush=True)


def start_processes() -> list[subprocess.Popen[str]]:
    npm = shutil.which("npm")
    if not npm:
        raise RuntimeError("Cannot find npm. Please install Node.js first.")
    if not (FRONTEND / "node_modules").exists():
        raise RuntimeError("frontend/node_modules is missing. Run: cd frontend && npm install")

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    backend = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(BACKEND_PORT),
            "--reload",
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    frontend = subprocess.Popen(
        [
            npm,
            "run",
            "dev",
            "--",
            "--host",
            "0.0.0.0",
            "--port",
            str(FRONTEND_PORT),
        ],
        cwd=FRONTEND,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    for name, process in (("backend", backend), ("frontend", frontend)):
        threading.Thread(target=stream_output, args=(name, process), daemon=True).start()
    return [backend, frontend]


def stop_processes(processes: list[subprocess.Popen[str]]) -> None:
    for process in processes:
        if process.poll() is None:
            process.send_signal(signal.SIGINT)
    deadline = time.time() + 6
    for process in processes:
        while process.poll() is None and time.time() < deadline:
            time.sleep(0.1)
        if process.poll() is None:
            process.terminate()


def main() -> int:
    lan_ip = local_ip()
    print("")
    print("桌游比赛管理系统 - 开发启动项")
    print("=" * 42)
    print(f"前端页面: http://127.0.0.1:{FRONTEND_PORT}/admin")
    print(f"前端局域网: http://{lan_ip}:{FRONTEND_PORT}/admin")
    print(f"后端接口: http://127.0.0.1:{BACKEND_PORT}/docs")
    print(f"后端健康检查: http://127.0.0.1:{BACKEND_PORT}/api/health")
    print("=" * 42)
    print("停止服务: 在这个窗口按 Ctrl+C")
    print("")

    processes: list[subprocess.Popen[str]] = []
    try:
        processes = start_processes()
        while True:
            for process in processes:
                if process.poll() is not None:
                    stop_processes(processes)
                    return process.returncode or 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n正在停止前端和后端...")
        stop_processes(processes)
        return 0
    except Exception as exc:
        print(f"启动失败: {exc}")
        stop_processes(processes)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
