from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rawbridge.constants import DEFAULT_MANIFEST
from rawbridge.models import AssetResult, ConversionPreset, JobConfig, RemoteFile


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Manifest:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.db_path = output_dir / DEFAULT_MANIFEST
        self.conn: sqlite3.Connection | None = None

    def __enter__(self) -> "Manifest":
        self.init_db()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def connect(self) -> sqlite3.Connection:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def init_db(self) -> None:
        conn = self.connect()
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
              id TEXT PRIMARY KEY,
              source TEXT,
              provider TEXT,
              output_dir TEXT,
              preset TEXT,
              status TEXT,
              total_files INTEGER,
              processed_files INTEGER,
              skipped_files INTEGER,
              failed_files INTEGER,
              started_at TEXT,
              finished_at TEXT,
              config_json TEXT
            );

            CREATE TABLE IF NOT EXISTS assets (
              id INTEGER PRIMARY KEY,
              job_id TEXT,
              source_provider TEXT,
              source_id TEXT,
              source_path TEXT,
              source_name TEXT,
              source_size INTEGER,
              source_revision TEXT,
              source_modified_at TEXT,
              fingerprint TEXT,
              preset TEXT,
              output_format TEXT,
              output_size_name TEXT,
              output_path TEXT,
              output_width INTEGER,
              output_height INTEGER,
              output_size_bytes INTEGER,
              status TEXT,
              error TEXT,
              created_at TEXT,
              updated_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_assets_lookup
              ON assets(fingerprint, preset, output_format, output_size_name);

            CREATE TABLE IF NOT EXISTS events (
              id INTEGER PRIMARY KEY,
              job_id TEXT,
              level TEXT,
              message TEXT,
              payload_json TEXT,
              created_at TEXT
            );
            """
        )
        conn.commit()

    def create_job(self, job_id: str, config: JobConfig, preset: ConversionPreset, provider: str) -> None:
        conn = self.connect()
        now = utc_now()
        conn.execute(
            """
            INSERT OR REPLACE INTO jobs
              (id, source, provider, output_dir, preset, status, total_files, processed_files,
               skipped_files, failed_files, started_at, finished_at, config_json)
            VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, 0, ?, NULL, ?)
            """,
            (
                job_id,
                config.source,
                provider,
                str(config.output_dir),
                preset.name,
                "running",
                now,
                json.dumps(_safe_config_dump(config), sort_keys=True),
            ),
        )
        conn.commit()

    def update_job(self, job_id: str, **fields: Any) -> None:
        if not fields:
            return
        conn = self.connect()
        columns = ", ".join(f"{name} = ?" for name in fields)
        conn.execute(f"UPDATE jobs SET {columns} WHERE id = ?", [*fields.values(), job_id])
        conn.commit()

    def record_event(self, job_id: str, level: str, message: str, payload: dict[str, Any] | None = None) -> None:
        conn = self.connect()
        conn.execute(
            "INSERT INTO events(job_id, level, message, payload_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (job_id, level, message, json.dumps(payload or {}), utc_now()),
        )
        conn.commit()

    def get_existing_asset(
        self,
        fingerprint: str,
        preset: str,
        output_format: str,
        output_size_name: str,
    ) -> sqlite3.Row | None:
        conn = self.connect()
        return conn.execute(
            """
            SELECT * FROM assets
            WHERE fingerprint = ? AND preset = ? AND output_format = ? AND output_size_name = ?
            ORDER BY id DESC LIMIT 1
            """,
            (fingerprint, preset, output_format, output_size_name),
        ).fetchone()

    def mark_done(
        self,
        job_id: str,
        file: RemoteFile,
        fingerprint: str,
        preset: str,
        result: AssetResult,
    ) -> None:
        self._insert_asset(job_id, file, fingerprint, preset, result)

    def mark_failed(
        self,
        job_id: str,
        file: RemoteFile,
        fingerprint: str,
        preset: str,
        error: str,
    ) -> None:
        result = AssetResult(
            source_path=file.path,
            output_path="",
            format="",
            status="failed",
            input_size=file.size,
            error=error,
        )
        self._insert_asset(job_id, file, fingerprint, preset, result)

    def _insert_asset(
        self,
        job_id: str,
        file: RemoteFile,
        fingerprint: str,
        preset: str,
        result: AssetResult,
    ) -> None:
        conn = self.connect()
        now = utc_now()
        conn.execute(
            """
            INSERT INTO assets (
              job_id, source_provider, source_id, source_path, source_name, source_size,
              source_revision, source_modified_at, fingerprint, preset, output_format,
              output_size_name, output_path, output_width, output_height, output_size_bytes,
              status, error, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                file.provider,
                file.id,
                file.path,
                file.name,
                file.size,
                file.revision,
                file.modified_at.isoformat() if file.modified_at else None,
                fingerprint,
                preset,
                result.format,
                result.output_size_name,
                result.output_path,
                result.width,
                result.height,
                result.output_size,
                result.status,
                result.error,
                now,
                now,
            ),
        )
        conn.commit()

    def should_skip(
        self,
        fingerprint: str,
        preset: ConversionPreset,
        outputs: list[tuple[Path, str, str]],
        overwrite: bool = False,
    ) -> bool:
        if overwrite:
            return False
        for output_path, fmt, size_name in outputs:
            row = self.get_existing_asset(fingerprint, preset.name, fmt, size_name)
            if row is None or row["status"] != "done" or not Path(row["output_path"]).exists():
                return False
            if not output_path.exists():
                return False
        return True

    def get_job(self, job_id: str) -> sqlite3.Row | None:
        return self.connect().execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()

    def list_jobs(self) -> list[sqlite3.Row]:
        return list(self.connect().execute("SELECT * FROM jobs ORDER BY started_at DESC"))

    def list_assets(self, job_id: str, status: str | None = None) -> list[sqlite3.Row]:
        conn = self.connect()
        if status:
            return list(
                conn.execute("SELECT * FROM assets WHERE job_id = ? AND status = ? ORDER BY id", (job_id, status))
            )
        return list(conn.execute("SELECT * FROM assets WHERE job_id = ? ORDER BY id", (job_id,)))

    def list_events(self, job_id: str, limit: int = 250) -> list[sqlite3.Row]:
        return list(
            self.connect().execute(
                "SELECT * FROM events WHERE job_id = ? ORDER BY id DESC LIMIT ?",
                (job_id, limit),
            )
        )[::-1]

    def get_pending_or_failed(self, job_id: str) -> list[sqlite3.Row]:
        return list(
            self.connect().execute(
                "SELECT * FROM assets WHERE job_id = ? AND status IN ('pending', 'failed') ORDER BY id",
                (job_id,),
            )
        )


def _safe_config_dump(config: JobConfig) -> dict[str, Any]:
    data = config.model_dump(mode="json")
    if data.get("dropbox_token"):
        data["dropbox_token"] = None
    return data


def init_db(output_dir: Path) -> Manifest:
    manifest = Manifest(output_dir)
    manifest.init_db()
    return manifest
