#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-cve126916}"
export PYTHONUNBUFFERED=1
chmod +x poc.py start.sh run.sh

exec python3 -u - <<'PY'
import fcntl
import subprocess
import sys
import time
from pathlib import Path

LABEL = "CVE-2026-126916"
WITNESS = "CVE-2026-126916-INTOF-WITNESS"
PROJECT = "cve126916"
SLOTS = (Path("/tmp/chrome-lab-slot-1.lock"), Path("/tmp/chrome-lab-slot-2.lock"))
ROOT = Path(".").resolve()
LAST = ROOT / "poc-last-run.txt"


def compose(*args: str) -> int:
    cmd = ["docker", "compose", "-p", PROJECT, *args]
    return subprocess.call(cmd)


def down() -> None:
    print("== docker compose down -v ==", flush=True)
    compose("down", "-v", "--remove-orphans")


def finished() -> bool:
    if not LAST.is_file():
        return False
    lines = LAST.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return False
    head = lines[-1]
    return head.startswith("SUCCESS ") or head.startswith("FAIL ")


def fail_setup(reason: str) -> None:
    if not finished():
        line = f"FAIL {LABEL} {reason} {WITNESS}\n"
        LAST.write_text(line, encoding="utf-8")
        print(line, end="", flush=True)
    down()


def acquire() -> object:
    deadline = time.monotonic() + 40 * 60
    while True:
        for path in SLOTS:
            handle = path.open("a+")
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                handle.close()
                continue
            print(f"locked {path}", flush=True)
            return handle
        if time.monotonic() >= deadline:
            fail_setup("lock-timeout")
            raise SystemExit(1)
        print("lock-busy sleep 20s", flush=True)
        time.sleep(20)


def main() -> int:
    held = acquire()
    try:
        down()
        if LAST.is_file():
            LAST.unlink()
        up_ok = False
        rc = 1
        for attempt in range(1, 4):
            rc = compose(
                "up",
                "--build",
                "--abort-on-container-exit",
                "--exit-code-from",
                "lab",
            )
            if finished():
                up_ok = True
                print(f"lab-finished attempt={attempt} compose_rc={rc}", flush=True)
                break
            print(f"compose-up-retry attempt={attempt} compose_rc={rc}", flush=True)
            time.sleep(8)
            down()
        if not up_ok:
            print("== compose logs (no oracle line) ==", flush=True)
            compose("logs", "--no-color", "--tail=120")
            fail_setup("compose-up-failed")
            return 1
        print("== oracle ==", flush=True)
        lines = LAST.read_text(encoding="utf-8", errors="replace").splitlines()
        print(lines[-1], flush=True)
        down()
        return 0
    finally:
        fcntl.flock(held.fileno(), fcntl.LOCK_UN)
        held.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        line = f"FAIL {LABEL} run-exception {WITNESS}"
        print(line, flush=True)
        print(f"{type(exc).__name__}: {exc}", flush=True)
        if not finished():
            LAST.write_text(line + "\n", encoding="utf-8")
        down()
        raise SystemExit(1)
PY
