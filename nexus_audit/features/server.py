#!/usr/bin/env python3
"""Local HTTP server for serving audit output and fix-queue updates."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Any
from urllib.parse import urlparse


TRACKED_STATUSES = {"open", "in_progress", "done", "snoozed"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_json(path: str, data: Dict[str, Any]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


class AuditHandler(BaseHTTPRequestHandler):
    html_path: str = ""
    json_path: str = ""
    queue_path: str = ""

    def _send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path: str, content_type: str) -> None:
        try:
            with open(path, "rb") as f:
                self._send_bytes(200, f.read(), content_type)
        except FileNotFoundError:
            self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"", "/"}:
            return self._serve_file(self.html_path, "text/html; charset=utf-8")
        if path == "/data.json":
            return self._serve_file(self.json_path, "application/json; charset=utf-8")
        if path == "/fix-queue":
            body = json.dumps(_read_json(self.queue_path), indent=2).encode("utf-8")
            return self._send_bytes(200, body, "application/json; charset=utf-8")
        self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")

    def do_PUT(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/fix-queue":
            self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        payload = json.loads(raw or "{}")
        rec_id = str(payload.get("rec_id", "")).strip()
        status = str(payload.get("status", "open")).strip()
        note = str(payload.get("note", "")).strip()
        if not rec_id:
            self._send_bytes(400, b"Missing rec_id", "text/plain; charset=utf-8")
            return
        if status not in TRACKED_STATUSES:
            self._send_bytes(400, b"Unsupported status", "text/plain; charset=utf-8")
            return
        queue = _read_json(self.queue_path)
        entry = queue.get(rec_id, {}) if isinstance(queue, dict) else {}
        if not isinstance(entry, dict):
            entry = {}
        entry.setdefault("created_at", _utc_now())
        entry.update({
            "status": status,
            "notes": note,
            "updated_at": _utc_now(),
        })
        queue[rec_id] = entry
        _write_json(self.queue_path, queue)
        body = json.dumps({"ok": True, "rec_id": rec_id, "status": status}).encode("utf-8")
        self._send_bytes(200, body, "application/json; charset=utf-8")

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def _python_files_mtime(root: Path) -> float:
    latest = 0.0
    for path in root.rglob("*.py"):
        try:
            latest = max(latest, path.stat().st_mtime)
        except FileNotFoundError:
            continue
    return latest


def _run_audit(repo_root: Path) -> None:
    subprocess.run([sys.executable, "pulse.py"], cwd=str(repo_root), check=False)


def _start_watch_loop(repo_root: Path, interval: int = 30) -> threading.Thread:
    last_mtime = _python_files_mtime(repo_root)
    lock = threading.Lock()

    def _loop() -> None:
        nonlocal last_mtime
        try:
            from watchdog.events import FileSystemEventHandler  # type: ignore
            from watchdog.observers import Observer  # type: ignore
        except Exception:
            while True:
                time.sleep(interval)
                current = _python_files_mtime(repo_root)
                if current > last_mtime:
                    with lock:
                        current_check = _python_files_mtime(repo_root)
                        if current_check > last_mtime:
                            last_mtime = current_check
                            _run_audit(repo_root)
            return

        class _Handler(FileSystemEventHandler):
            def on_any_event(self, event):  # noqa: ANN001
                nonlocal last_mtime
                if getattr(event, "is_directory", False):
                    return
                src = getattr(event, "src_path", "") or ""
                if not src.endswith(".py"):
                    return
                with lock:
                    current = _python_files_mtime(repo_root)
                    if current > last_mtime:
                        last_mtime = current
                        _run_audit(repo_root)

        observer = Observer()
        handler = _Handler()
        observer.schedule(handler, str(repo_root), recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(interval)
        finally:
            observer.stop()
            observer.join()

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
    return thread


def serve(
    audit_html_path: str,
    audit_json_path: str,
    queue_path: str,
    port: int = 8421,
    open_browser: bool = True,
    watch: bool = False,
) -> None:
    """Start the local dashboard server."""
    AuditHandler.html_path = audit_html_path
    AuditHandler.json_path = audit_json_path
    AuditHandler.queue_path = queue_path
    repo_root = Path(audit_html_path).resolve().parents[2]

    if watch:
        _start_watch_loop(repo_root)

    server = ThreadingHTTPServer(("127.0.0.1", port), AuditHandler)
    url = f"http://localhost:{port}"

    print()
    print("═" * 62)
    print(f"🌐  NEXUS AUDIT DASHBOARD SERVER")
    print(f"   URL  : {url}")
    try:
        # OSC 8 terminal hyperlink: \033]8;;URL\033\\TEXT\033]8;;\033\\
        print(f"   Open : \033]8;;{url}\033\\{url}\033]8;;\033\\ (clickable)")
    except Exception:
        pass
    print(f"   Watch: {'enabled' if watch else 'disabled'}")
    print(f"   Stop : Ctrl+C")
    print("═" * 62)
    print()

    if open_browser:
        # WSL-aware browser launch: try cmd.exe first (Windows host),
        # fall back to standard webbrowser module.
        opened = False
        try:
            result = subprocess.run(
                ["cmd.exe", "/c", "start", url],
                capture_output=True, timeout=5
            )
            opened = result.returncode == 0
        except Exception:
            pass
        if not opened:
            try:
                webbrowser.open(url)
                opened = True
            except Exception:
                pass
        
        if opened:
            print(f"✔ Browser opened automatically")
        else:
            print(f"📢 Could not open browser automatically — open: {url}")
        print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
    finally:
        server.server_close()
