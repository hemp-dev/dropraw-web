from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def new_job_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"job_{stamp}_{uuid4().hex[:8]}"
