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
from urllib.parse import urlparse, parse_qs

from ..report.markdown_report import generate_app_markdown, generate_category_markdown


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
        if path == "/api/status":
            running = getattr(AuditHandler, '_audit_running', False)
            try:
                mtime = Path(self.json_path).stat().st_mtime
            except Exception:
                mtime = 0
            body = json.dumps({"status": "running" if running else "idle", "mtime": mtime}).encode("utf-8")
            return self._send_bytes(200, body, "application/json; charset=utf-8")
            
        if path == "/api/settings":
            settings_path = Path(self.json_path).parent / "settings.json"
            if settings_path.exists():
                with open(settings_path, "rb") as f:
                    body = f.read()
            else:
                body = b"{}"
            return self._send_bytes(200, body, "application/json; charset=utf-8")
            
        if path == "/api/history":
            history_dir = Path(self.json_path).parent / "audit_history"
            history = []
            if history_dir.exists():
                for f in history_dir.glob("*.json"):
                    history.append(f.name)
            history.sort(reverse=True)
            body = json.dumps({"history": history}).encode("utf-8")
            return self._send_bytes(200, body, "application/json; charset=utf-8")
            
        if path == "/api/stream":
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()
            
            seen_idx = 0
            while True:
                try:
                    running = getattr(AuditHandler, '_audit_running', False)
                    logs = getattr(AuditHandler, '_audit_log', [])
                    
                    if len(logs) > seen_idx:
                        for line in logs[seen_idx:]:
                            if line == "__DONE__":
                                self.wfile.write(b'event: status\ndata: {"state": "completed"}\n\n')
                            else:
                                self.wfile.write(f'event: log\ndata: {json.dumps({"message": line})}\n\n'.encode('utf-8'))
                        seen_idx = len(logs)
                        self.wfile.flush()
                    
                    # Status ping every second
                    self.wfile.write(f'event: status\ndata: {{"state": "{ "running" if running else "idle" }"}}\n\n'.encode('utf-8'))
                    self.wfile.flush()
                    
                    time.sleep(1)
                except Exception:
                    # Broken pipe or connection closed
                    break
            return

        # ── Download endpoints ────────────────────────────────────────────
        if path == "/api/download/report/full":
            md_path = str(Path(self.json_path).parent / "AUDIT_REPORT_COMPREHENSIVE.md")
            if not Path(md_path).exists():
                return self._send_bytes(404, b"Full report not found. Run an audit first.", "text/plain")
            with open(md_path, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="AUDIT_REPORT_COMPREHENSIVE.md"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/download/report/app":
            qs = parse_qs(urlparse(self.path).query)
            app_name = (qs.get("name", [""])[0] or "").strip()
            if not app_name:
                return self._send_bytes(400, b"Missing ?name= parameter", "text/plain")
            if not Path(self.json_path).exists():
                return self._send_bytes(404, b"Audit data not found. Run an audit first.", "text/plain")
            with open(self.json_path, "r", encoding="utf-8") as f:
                audit_data = json.load(f)
            md_content = generate_app_markdown(audit_data, app_name)
            body = md_content.encode("utf-8")
            filename = f"{app_name}_audit_report.md"
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/download/report/category":
            qs = parse_qs(urlparse(self.path).query)
            category = (qs.get("name", [""])[0] or "").strip()
            if not category:
                return self._send_bytes(400, b"Missing ?name= parameter", "text/plain")
            if not Path(self.json_path).exists():
                return self._send_bytes(404, b"Audit data not found. Run an audit first.", "text/plain")
            with open(self.json_path, "r", encoding="utf-8") as f:
                audit_data = json.load(f)
            md_content = generate_category_markdown(audit_data, category)
            body = md_content.encode("utf-8")
            filename = f"{category}_audit_report.md"
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # ── Static CSS and JS files ────────────────────────────────────────
        if path.startswith("/css/") and path.endswith(".css"):
            safe_name = path[5:]
            if ".." in safe_name:
                return self._send_bytes(403, b"Forbidden", "text/plain")
            css_path = Path(self.html_path).parent / "css" / safe_name
            if css_path.exists():
                return self._serve_file(str(css_path), "text/css; charset=utf-8")

        if path.startswith("/js/") and path.endswith(".js"):
            safe_name = path[4:]
            if ".." in safe_name:
                return self._send_bytes(403, b"Forbidden", "text/plain")
            js_path = Path(self.html_path).parent / "js" / safe_name
            if js_path.exists():
                return self._serve_file(str(js_path), "application/javascript; charset=utf-8")

        if path == "/vis-network.min.js":
            vis_path = Path(self.html_path).parent / "vis-network.min.js"
            if vis_path.exists():
                return self._serve_file(str(vis_path), "application/javascript; charset=utf-8")

        self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path

        if path == "/api/settings":
            length = int(self.headers.get("Content-Length", "0") or 0)
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                payload = json.loads(raw)
                # Validation
                if "project_path" in payload and payload["project_path"]:
                    p = Path(payload["project_path"]).expanduser().resolve()
                    if not p.exists() or not p.is_dir():
                        return self._send_bytes(400, b'{"error": "Invalid project_path"}', "application/json; charset=utf-8")
                    payload["project_path"] = str(p)
                
                settings_path = Path(self.json_path).parent / "settings.json"
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2)
                return self._send_bytes(200, b'{"ok": true}', "application/json; charset=utf-8")
            except Exception as e:
                return self._send_bytes(400, json.dumps({"error": str(e)}).encode(), "application/json; charset=utf-8")

        if path == "/api/run":
            if getattr(AuditHandler, '_audit_running', False):
                body = json.dumps({"ok": False, "error": "Audit already running"}).encode("utf-8")
                return self._send_bytes(409, body, "application/json; charset=utf-8")

            # Load settings to get project path
            settings_path = Path(self.json_path).parent / "settings.json"
            repo_root = Path.cwd()
            if settings_path.exists():
                try:
                    with open(settings_path, "r", encoding="utf-8") as f:
                        settings = json.load(f)
                    if "project_path" in settings and settings["project_path"]:
                        repo_root = Path(settings["project_path"])
                except Exception:
                    pass

            # pulse.py path
            pulse_path = str(Path(__file__).resolve().parents[2] / "pulse.py")
            cmd = [sys.executable, pulse_path]

            def _run() -> None:
                AuditHandler._audit_running = True
                AuditHandler._audit_log = []
                try:
                    proc = subprocess.Popen(
                        cmd, cwd=str(repo_root),
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, bufsize=1,
                    )
                    AuditHandler._audit_pid = proc.pid
                    for line in proc.stdout:
                        AuditHandler._audit_log.append(line.rstrip())
                    proc.wait()
                    AuditHandler._audit_log.append("__DONE__")
                except Exception as exc:
                    AuditHandler._audit_log.append(f"ERROR: {exc}")
                    AuditHandler._audit_log.append("__DONE__")
                finally:
                    AuditHandler._audit_running = False
                    AuditHandler._audit_pid = None

            threading.Thread(target=_run, daemon=True).start()
            body = json.dumps({"ok": True}).encode("utf-8")
            return self._send_bytes(200, body, "application/json; charset=utf-8")

        if path == "/api/cancel":
            pid = getattr(AuditHandler, '_audit_pid', None)
            if pid:
                import signal
                try:
                    # Windows uses taskkill, UNIX uses os.kill
                    if sys.platform == "win32":
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
                    else:
                        os.kill(pid, signal.SIGTERM)
                    AuditHandler._audit_log.append("WARNING: Audit cancelled by user.")
                except Exception:
                    pass
            body = b'{"ok": true}'
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

    class ReusableThreadingHTTPServer(ThreadingHTTPServer):
        allow_reuse_address = True

    server = ReusableThreadingHTTPServer(("127.0.0.1", port), AuditHandler)
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
