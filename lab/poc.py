#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: CVE-2026-126916 (High)
#  Vendor: Google Chrome / ICU
#  Versions: Chrome < 157.0.8103.78
#  Impact: ICU usearch int32 CE-index overflow via window.find; renderer SIGSEGV
#  Requires: Docker linux-arm64, Chrome for Testing 157.0.8103.50 and 157.0.8103.78, several GB RAM for the corpus
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "CVE-2026-126916"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _PRINT(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _PRINT(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_PRINT = _builtins.print
_builtins.print = _cprint

"""CVE-2026-126916 usearch CE-index overflow oracle.

Bug 574025697 is the ICU usearch CEIBuffer int32 index overflow
(ICU-23568), reached from Blink window.find. The page runs the in-tree
TestCEIndexOverflow corpus. Patched Chrome reports the match. Vulnerable
Chrome crashes or does not. No exploit payload. CFT is not ASan.
"""


import json
import os
import signal
import struct
import subprocess
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

LABEL = "CVE-2026-126916"
WITNESS = "CVE-2026-126916-INTOF-WITNESS"
HOST = "127.0.0.1"
PORT = 18650
ORIGIN = f"http://{HOST}:{PORT}/poc.html"
VULN = "157.0.8103.50"
FIXED = "157.0.8103.78"
OUT = Path("/out")
LAB = Path("/lab")
CHROME_TIMEOUT_S = 1800
CRASH_ROOT = Path("/root/.config/google-chrome-for-testing/Crash Reports")
REPS = 119304647

LINES: list[str] = []
CRASH_MARKERS = (
    "sigsegv",
    "sigabrt",
    "segmentation fault",
    "check failed",
    "aw, snap",
    "sad_tab",
    "target crashed",
    "renderer process crashed",
)


def log(msg: str) -> None:
    print(msg, flush=True)
    LINES.append(msg)


class BeaconState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.events: list[dict[str, object]] = []

    def add(self, event: dict[str, object]) -> None:
        with self._lock:
            self.events.append(event)

    def snapshot(self) -> list[dict[str, object]]:
        with self._lock:
            return list(self.events)

    def clear(self) -> None:
        with self._lock:
            self.events.clear()


class LabHandler(BaseHTTPRequestHandler):
    state: BeaconState
    pages: dict[str, bytes]

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/":
            path = "/poc.html"
        body = self.pages.get(path)
        if body is None:
            self.send_error(404)
            return
        kind = "text/html; charset=utf-8" if path.endswith(".html") else "text/javascript"
        self._send(200, body, kind)

    def do_POST(self) -> None:
        if self.path.split("?", 1)[0] != "/beacon":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400)
            return
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_error(400)
            return
        if not isinstance(payload, dict):
            self.send_error(400)
            return
        self.state.add(payload)
        self._send(204, b"", "text/plain")


@dataclass
class VersionResult:
    version: str
    smoke_ok: bool
    offset_ok: bool
    crashed: bool
    timed_out: bool
    detail: str


def chrome_bin(version: str) -> Path:
    return Path("/opt/chrome") / version / "chrome-linux-arm64" / "chrome"


def load_pages() -> dict[str, bytes]:
    pages: dict[str, bytes] = {}
    for name in ("poc.html", "poc.js"):
        pages["/" + name] = (LAB / name).read_bytes()
    return pages


def event_phase(events: list[dict[str, object]], phase: str) -> dict[str, object] | None:
    for event in reversed(events):
        if event.get("phase") == phase:
            return event
    return None


def looks_crashed(text: str, code: int | None) -> bool:
    if code in {139, 134, -11, -6}:
        return True
    low = text.lower()
    return any(marker in low for marker in CRASH_MARKERS)


def chrome_rss_kb() -> int:
    total = 0
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            comm = (entry / "comm").read_text(encoding="utf-8").strip()
            status = (entry / "status").read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if comm != "chrome":
            continue
        for line in status.splitlines():
            if line.startswith("VmRSS:"):
                total += int(line.split()[1])
                break
    return total


def crash_dumps() -> dict[Path, bytes]:
    found: dict[Path, bytes] = {}
    for sub in ("pending", "completed", "new"):
        folder = CRASH_ROOT / sub
        if not folder.is_dir():
            continue
        for path in folder.glob("*.dmp"):
            try:
                found[path] = path.read_bytes()
            except OSError:
                continue
    return found


def exception_code(data: bytes) -> int | None:
    if len(data) < 32 or data[:4] != b"MDMP":
        return None
    nstreams, dir_rva = struct.unpack_from("<II", data, 8)
    for index in range(nstreams):
        off = dir_rva + index * 12
        if off + 12 > len(data):
            return None
        typ, _size, rva = struct.unpack_from("<III", data, off)
        if typ == 6 and rva + 12 <= len(data):
            return struct.unpack_from("<I", data, rva + 8)[0]
    return None


def renderer_notes(dumps: dict[Path, bytes]) -> list[str]:
    notes: list[str] = []
    for path, data in sorted(dumps.items(), key=lambda item: item[0].name):
        if b"--type=renderer" not in data:
            continue
        code = exception_code(data)
        notes.append(f"{path.name}:{code:#x}" if code is not None else path.name)
    return notes


def run_chrome(state: BeaconState, version: str) -> VersionResult:
    state.clear()
    binary = chrome_bin(version)
    debug = OUT / "debug" / version
    debug.mkdir(parents=True, exist_ok=True)
    log_path = debug / "chrome.log"
    profile = Path("/tmp") / f"profile-{version}"
    if profile.exists():
        subprocess.run(["rm", "-rf", str(profile)], check=False)
    profile.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(binary),
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-hang-monitor",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--disable-sync",
        "--lang=en-US",
        "--window-size=800,600",
        f"--user-data-dir={profile}",
        "--js-flags=--max-old-space-size=8192 --expose-gc",
        ORIGIN,
    ]
    log(f"chrome-start {version}")
    before_dumps = set(crash_dumps())
    with log_path.open("w", encoding="utf-8") as log_file:
        proc = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        deadline = time.monotonic() + CHROME_TIMEOUT_S
        timed_out = False
        seen = 0
        last_hb = time.monotonic()
        last_dump = 0.0
        notes: list[str] = []
        while time.monotonic() < deadline:
            events = state.snapshot()
            if len(events) > seen:
                for event in events[seen:]:
                    log(f"beacon {version} {json.dumps(event, sort_keys=True)}")
                seen = len(events)
            if event_phase(events, "done") is not None:
                break
            if proc.poll() is not None:
                break
            now = time.monotonic()
            if now - last_hb >= 30:
                log(f"wait {version} rss_kb={chrome_rss_kb()} events={len(events)}")
                last_hb = now
            if now - last_dump >= 2:
                fresh = {
                    path: data
                    for path, data in crash_dumps().items()
                    if path not in before_dumps
                }
                notes = renderer_notes(fresh)
                last_dump = now
                if notes:
                    break
            time.sleep(0.4)
        else:
            timed_out = True
        fresh = {
            path: data
            for path, data in crash_dumps().items()
            if path not in before_dumps
        }
        notes = renderer_notes(fresh) or notes
        if notes:
            log(f"crash-dump {version} {','.join(notes)}")
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill()
        code = proc.poll()
    text = log_path.read_text(encoding="utf-8", errors="replace")
    tail = "\n".join(text.splitlines()[-40:])
    (debug / "chrome.tail").write_text(tail, encoding="utf-8")
    events = state.snapshot()
    smoke = event_phase(events, "smoke")
    full = event_phase(events, "full")
    smoke_ok = bool(smoke and smoke.get("offsetOk") is True)
    offset_ok = bool(full and full.get("offsetOk") is True)
    crashed = (looks_crashed(text, code) or bool(notes)) and not offset_ok
    detail = (
        f"code={code} timeout={timed_out} smoke={smoke_ok} "
        f"offset_ok={offset_ok} crashed={crashed} events={len(events)}"
    )
    log(f"chrome-end {version} {detail}")
    subprocess.run(["rm", "-rf", str(profile)], check=False)
    return VersionResult(version, smoke_ok, offset_ok, crashed, timed_out, detail)


def verdict(vuln: VersionResult, fixed: VersionResult) -> tuple[bool, str]:
    if not fixed.smoke_ok or not vuln.smoke_ok:
        return False, "smoke-failed"
    if fixed.offset_ok and (vuln.crashed or not vuln.offset_ok):
        why = "vuln-crash" if vuln.crashed else "vuln-no-match"
        return True, why
    if fixed.offset_ok and vuln.offset_ok:
        return False, "neither-crashed"
    if not fixed.offset_ok and vuln.crashed and not fixed.crashed:
        return False, "fixed-no-witness"
    if vuln.timed_out and fixed.timed_out:
        return False, "both-timeout"
    if vuln.crashed and fixed.crashed:
        return False, "both-crashed"
    return False, "fixed-no-witness"


def finish(ok: bool, reason: str) -> int:
    status = "SUCCESS" if ok else "FAIL"
    log(f"{status} {LABEL} {reason} {WITNESS}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "poc-last-run.txt").write_text("\n".join(LINES) + "\n", encoding="utf-8")
    return 0 if ok else 1


def main() -> int:
    pages = load_pages()
    state = BeaconState()
    LabHandler.state = state
    LabHandler.pages = pages
    server = ThreadingHTTPServer((HOST, PORT), LabHandler)
    thread = threading.Thread(target=server.serve_forever, name="http", daemon=True)
    thread.start()
    log(f"listen {HOST}:{PORT}")
    try:
        for version in (VULN, FIXED):
            binary = chrome_bin(version)
            if not binary.is_file():
                return finish(False, f"missing-chrome-{version}")
        vuln = run_chrome(state, VULN)
        fixed = run_chrome(state, FIXED)
        ok, reason = verdict(vuln, fixed)
        log(f"vuln {vuln.detail}")
        log(f"fixed {fixed.detail}")
        return finish(ok, reason)
    except Exception as exc:
        log(f"exception {type(exc).__name__}: {exc}")
        return finish(False, "exception")
    finally:
        server.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())

