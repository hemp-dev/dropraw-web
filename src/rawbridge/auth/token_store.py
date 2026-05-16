from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def get_dropbox_token(cli_token: str | None = None, config_token: str | None = None) -> str | None:
    if cli_token:
        return cli_token
    load_dotenv()
    return os.getenv("DROPBOX_ACCESS_TOKEN") or config_token


def get_dropbox_link_password() -> str | None:
    load_dotenv()
    return os.getenv("DROPBOX_LINK_PASSWORD")


def token_presence_hint() -> str:
    return "Set DROPBOX_ACCESS_TOKEN in the environment or .env, or pass --dropbox-token."
