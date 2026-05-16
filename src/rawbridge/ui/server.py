from __future__ import annotations

import os
import secrets
import socket
import webbrowser
from pathlib import Path

from rawbridge.ui.api import create_app


def build_app():
    try:
        from fastapi.responses import HTMLResponse
        from fastapi.staticfiles import StaticFiles
    except ImportError as exc:
        raise RuntimeError("RawBridge UI requires fastapi and uvicorn. Install with: pip install 'rawbridge[ui]'") from exc

    app = create_app()
    dist = _ui_dist_path()
    if dist.exists():
        app.mount("/", StaticFiles(directory=dist, html=True), name="ui")
    else:
        @app.get("/", response_class=HTMLResponse)
        def fallback() -> str:
            return """
            <!doctype html><html><head><title>RawBridge</title></head>
            <body style="font-family: system-ui; margin: 40px;">
              <h1>RawBridge</h1>
              <p>Frontend build is not present yet. Run <code>npm install && npm run build</code> in the ui directory.</p>
              <p>API is available at <a href="/api/health">/api/health</a>.</p>
            </body></html>
            """
    return app


def run_ui(host: str = "127.0.0.1", port: int = 8787, open_browser: bool = True) -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("RawBridge UI requires uvicorn. Install with: pip install 'rawbridge[ui]'") from exc
    token = os.getenv("RAWBRIDGE_UI_TOKEN") or os.getenv("DROPRAW_UI_TOKEN")
    if host not in {"127.0.0.1", "localhost", "::1"} and not token:
        os.environ["RAWBRIDGE_UI_TOKEN"] = secrets.token_urlsafe(32)
        token = os.environ["RAWBRIDGE_UI_TOKEN"]
    url = f"http://{host}:{port}"
    print(f"RawBridge UI: {url}")
    if token:
        print("RawBridge UI token is enabled. API clients must send x-rawbridge-ui-token or a secure cookie.")
    if open_browser and _port_available(host, port):
        try:
            webbrowser.open(url)
        except Exception:
            pass
    uvicorn.run("rawbridge.ui.server:build_app", factory=True, host=host, port=port, log_level="info")


def _ui_dist_path() -> Path:
    candidates = [
        Path(__file__).resolve().parents[3] / "ui" / "dist",
        Path.cwd() / "ui" / "dist",
        Path(__file__).resolve().parent / "dist",
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def _port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) != 0
