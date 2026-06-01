"""Local development diagnostics for the backend service."""
from __future__ import annotations

import json
import socket
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def _print(title: str, value: str) -> None:
    print(f"{title}: {value}")


def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex((host, port)) == 0


def _get_json(url: str) -> dict | None:
    try:
        with urlopen(url, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


def main() -> int:
    _print("Project root", str(ROOT))
    _print("Python executable", sys.executable)
    _print("Python version", sys.version.split()[0])
    expected_venv = ROOT / ".venv"
    if expected_venv.exists() and expected_venv not in Path(sys.executable).resolve().parents:
        print("Warning: current Python is not the project .venv. PyCharm may be using the wrong interpreter.")
    _print(".env exists", str((ROOT / ".env").exists()))
    _print("requirements.txt exists", str((ROOT / "requirements.txt").exists()))

    port_open = _port_open("127.0.0.1", 8000)
    _print("Backend port 8000", "listening" if port_open else "not listening")
    if not port_open:
        print("Start backend with: uvicorn app.main:app --reload")
        return 1

    health = _get_json("http://127.0.0.1:8000/healthz")
    ready = _get_json("http://127.0.0.1:8000/readyz")
    _print("/healthz", json.dumps(health, ensure_ascii=False) if health else "failed")
    _print("/readyz", json.dumps(ready, ensure_ascii=False) if ready else "failed")

    if not health or health.get("code") != 200:
        return 1
    if not ready or ready.get("code") != 200:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
