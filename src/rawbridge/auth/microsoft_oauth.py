from __future__ import annotations

from rawbridge.auth.oauth_common import OAuthStatus, todo_oauth_status


def status() -> OAuthStatus:
    return todo_oauth_status("onedrive")
