from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthStatus:
    provider: str
    configured: bool
    authenticated: bool
    message: str


def todo_oauth_status(provider: str) -> OAuthStatus:
    return OAuthStatus(provider=provider, configured=False, authenticated=False, message="OAuth flow is not configured yet.")
