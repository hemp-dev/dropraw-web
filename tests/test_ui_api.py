from __future__ import annotations

from fastapi.testclient import TestClient

from rawbridge.ui.api import create_app


def test_api_health_and_providers():
    client = TestClient(create_app())

    health = client.get("/api/health").json()
    providers = client.get("/api/providers").json()

    assert health["recommended_python"] == "3.11 or 3.12"
    assert any(provider["id"] == "google-drive" for provider in providers)
    assert any(provider["id"] == "s3" for provider in providers)


def test_api_scan_local(tmp_path, monkeypatch):
    (tmp_path / "a.NEF").write_bytes(b"raw")
    (tmp_path / "b.jpg").write_bytes(b"skip")
    monkeypatch.setenv("RAWBRIDGE_UI_ALLOWED_SOURCE_ROOTS", str(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/scan",
        json={"source": str(tmp_path), "provider": "auto", "list_retries": 1, "download_retries": 1, "retry_delay": 0, "cooldown": 0},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "local"
    assert data["files_count"] == 1


def test_api_job_schema_accepts_retry_settings(tmp_path, monkeypatch):
    from rawbridge.ui import job_runner

    def fake_create_job(request):
        assert request.list_retries == 2
        assert request.download_retries == 3
        assert request.overwrite is False
        return "job_test"

    monkeypatch.setattr(job_runner.runner, "create_job", fake_create_job)
    monkeypatch.setenv("RAWBRIDGE_UI_ALLOWED_SOURCE_ROOTS", str(tmp_path))
    monkeypatch.setenv("RAWBRIDGE_UI_ALLOWED_OUTPUT_ROOTS", str(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/jobs",
        json={
            "source": str(tmp_path),
            "provider": "local",
            "output_dir": str(tmp_path / "out"),
            "preset": "web",
            "list_retries": 2,
            "download_retries": 3,
            "retry_delay": 1,
            "cooldown": 0,
            "overwrite": False,
            "resume": True,
            "metadata_mode": "strip",
        },
    )

    assert response.status_code == 202
    assert response.json()["job_id"] == "job_test"


def test_failed_files_endpoint_for_unknown_job():
    client = TestClient(create_app())

    assert client.get("/api/jobs/missing/failed").json() == []


def test_api_requires_ui_token_when_configured(monkeypatch):
    monkeypatch.setenv("RAWBRIDGE_UI_TOKEN", "secret")
    client = TestClient(create_app())

    assert client.get("/api/health").status_code == 401
    assert client.get("/api/health", headers={"x-rawbridge-ui-token": "secret"}).status_code == 200

    response = client.get("/api/providers?ui_token=secret")
    assert response.status_code == 200
    assert "rawbridge_ui_token" in response.headers.get("set-cookie", "")
    assert client.get("/api/providers").status_code == 200


def test_api_rejects_local_paths_outside_allowed_roots(tmp_path, monkeypatch):
    monkeypatch.setenv("RAWBRIDGE_UI_ALLOWED_SOURCE_ROOTS", str(tmp_path))
    client = TestClient(create_app())

    response = client.post(
        "/api/scan",
        json={"source": "/", "provider": "local", "list_retries": 1, "download_retries": 1, "retry_delay": 0, "cooldown": 0},
    )

    assert response.status_code == 400
    assert "allowed UI root" in response.json()["detail"]
