"""Environment setup: installs what can be installed, reports exactly what is left to do by hand.

Needed to extract and track leads : Python >= 3.10, time zone data (tzdata on Windows), the local database.
Needed to send messages           : Node + npm, the agent-browser CLI and its Chrome download.
Optional                          : pnpm + portless (named dashboard URL).
"""
import os
import platform
import shutil
import subprocess
import sys

MIN_PYTHON = (3, 10)
TZ_PROBE = "America/Sao_Paulo"


def _os_key() -> str:
    return {"Darwin": "mac", "Windows": "windows"}.get(platform.system(), "linux")


NODE_HINT = {
    "mac": "brew install node",
    "windows": "winget install OpenJS.NodeJS.LTS",
    "linux": "sudo apt install nodejs npm  (ou use nvm: https://github.com/nvm-sh/nvm)",
}
PYTHON_HINT = {
    "mac": "brew install python",
    "windows": "winget install Python.Python.3.12",
    "linux": "sudo apt install python3 python3-pip",
}


def _run(cmd: list[str], timeout: int = 900) -> tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    tail = (proc.stdout + proc.stderr).strip().splitlines()[-3:]
    return proc.returncode == 0, " | ".join(tail)


def tz_ok() -> bool:
    try:
        from zoneinfo import ZoneInfo
        ZoneInfo(TZ_PROBE)
        return True
    except Exception:
        return False


def agent_browser_ok() -> tuple[bool, str]:
    path = shutil.which("agent-browser")
    if not path:
        return False, "não instalado"
    ok, detail = _run([path, "doctor"], timeout=120)
    return ok, detail or path


def run_setup(install: bool = True, with_portless: bool = False) -> dict:
    os_key = _os_key()
    steps: list[dict] = []
    manual: list[str] = []

    def step(name: str, status: str, detail: str = "") -> None:
        steps.append({"step": name, "status": status, "detail": detail})

    # 1. Python
    if sys.version_info >= MIN_PYTHON:
        step("python>=3.10", "ok", platform.python_version())
    else:
        step("python>=3.10", "manual", f"versão atual {platform.python_version()}")
        manual.append(f"Instale Python 3.10+ ({PYTHON_HINT[os_key]}) e rode o setup de novo.")

    # 2. Time zone data
    if tz_ok():
        step("tzdata", "ok")
    elif install:
        ok, detail = _run([sys.executable, "-m", "pip", "install", "--quiet", "tzdata"])
        if ok and tz_ok():
            step("tzdata", "installed", "pip install tzdata")
        else:
            step("tzdata", "failed", detail)
            manual.append(f"Instale os dados de fuso horário: {sys.executable} -m pip install --user tzdata")
    else:
        step("tzdata", "missing", "rode setup sem --check para instalar")

    # 3. Local database
    try:
        from . import db
        db.init()
        step("database", "ok", db.DB_PATH)
    except Exception as exc:  # pragma: no cover - defensive
        step("database", "failed", str(exc))

    # 4. Node + npm (needed only for sending)
    npm = shutil.which("npm")
    if shutil.which("node") and npm:
        step("node+npm", "ok")
    else:
        step("node+npm", "manual", "necessário para instalar o agent-browser (só para enviar)")
        manual.append(f"Para enviar mensagens, instale Node.js: {NODE_HINT[os_key]}")

    # 5. agent-browser CLI + Chrome download
    ab_path = shutil.which("agent-browser")
    if not ab_path and npm and install:
        ok, detail = _run([npm, "install", "-g", "agent-browser"])
        ab_path = shutil.which("agent-browser")
        step("agent-browser", "installed" if ok and ab_path else "failed", detail)
        if not ab_path:
            manual.append("Instale manualmente: npm install -g agent-browser (pode exigir permissão de administrador)")
    elif ab_path:
        step("agent-browser", "ok", ab_path)
    else:
        step("agent-browser", "missing" if npm else "manual", "")

    if ab_path:
        healthy, detail = agent_browser_ok()
        if not healthy and install:
            ok, detail = _run([ab_path, "install"])
            healthy, detail = agent_browser_ok() if ok else (False, detail)
            step("browser-binary", "installed" if healthy else "failed", detail)
        else:
            step("browser-binary", "ok" if healthy else "missing", detail)
        if not healthy:
            manual.append("Baixe o Chrome do agent-browser: agent-browser install")
        if os_key == "linux":
            manual.append("No Linux, se faltarem bibliotecas de sistema: sudo agent-browser install --with-deps")

    # 6. Optional: named dashboard URL
    if with_portless:
        pnpm = shutil.which("pnpm")
        if pnpm and os.path.exists("package.json"):
            ok, detail = _run([pnpm, "install", "--silent"])
            step("portless", "installed" if ok else "failed", detail)
        else:
            step("portless", "manual", "instale o pnpm (npm install -g pnpm) e rode pnpm install")

    by = {s["step"]: s["status"] for s in steps}
    ready_extract = by.get("python>=3.10") == "ok" and by.get("tzdata") in ("ok", "installed") and by.get("database") == "ok"
    ready_send = ready_extract and by.get("agent-browser") in ("ok", "installed") and by.get("browser-binary") in ("ok", "installed")
    return {"ok": ready_extract, "ready_to_extract": ready_extract, "ready_to_send": ready_send,
            "platform": f"{platform.system()} {platform.machine()}", "python": sys.executable,
            "steps": steps, "manual_steps": manual}
