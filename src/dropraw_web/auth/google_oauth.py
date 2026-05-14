from __future__ import annotations

from dropraw_web.auth.oauth_common import OAuthStatus, todo_oauth_status


def status() -> OAuthStatus:
    return todo_oauth_status("google-drive")
