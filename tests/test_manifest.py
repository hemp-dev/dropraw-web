from pathlib import Path

from rawbridge.models import AssetResult, ConversionPreset, RemoteFile
from rawbridge.pipeline.manifest import Manifest


def test_manifest_mark_done_and_skip(tmp_path):
    preset = ConversionPreset(name="web", formats=["webp"])
    file = RemoteFile(provider="local", id="1", name="a.NEF", path="a.NEF", size=10, revision="r1")
    out = tmp_path / "a.webp"
    out.write_bytes(b"webp")

    with Manifest(tmp_path) as manifest:
        manifest.create_job("job1", _job_config(tmp_path), preset, "local")
        manifest.mark_done(
            "job1",
            file,
            "fingerprint",
            "web",
            AssetResult(
                source_path="a.NEF",
                output_path=str(out),
                format="webp",
                width=1,
                height=1,
                output_size=4,
                status="done",
            ),
        )

        assert manifest.should_skip("fingerprint", preset, [(out, "webp", "full")]) is True
        out.unlink()
        assert manifest.should_skip("fingerprint", preset, [(out, "webp", "full")]) is False


def test_manifest_records_failed(tmp_path):
    preset = ConversionPreset(name="web")
    file = RemoteFile(provider="local", id="1", name="a.NEF", path="a.NEF")
    with Manifest(tmp_path) as manifest:
        manifest.create_job("job1", _job_config(tmp_path), preset, "local")
        manifest.mark_failed("job1", file, "fingerprint", "web", "bad")
        rows = manifest.get_pending_or_failed("job1")
    assert rows[0]["status"] == "failed"
    assert rows[0]["error"] == "bad"


def _job_config(tmp_path: Path):
    from rawbridge.models import JobConfig

    return JobConfig(source=str(tmp_path), output_dir=tmp_path)

