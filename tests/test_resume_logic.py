from dropraw_web.models import ConversionPreset, RemoteFile
from dropraw_web.pipeline.manifest import Manifest


def test_overwrite_disables_skip(tmp_path):
    preset = ConversionPreset(name="web", formats=["webp"])
    file = RemoteFile(provider="local", id="1", name="a.NEF", path="a.NEF")
    out = tmp_path / "a.webp"
    out.write_bytes(b"ok")
    with Manifest(tmp_path) as manifest:
        manifest.create_job("job1", _job_config(tmp_path), preset, "local")
        manifest.mark_done(
            "job1",
            file,
            "fp",
            "web",
            _asset(out),
        )
        assert manifest.should_skip("fp", preset, [(out, "webp", "full")], overwrite=True) is False


def test_changed_fingerprint_reprocesses(tmp_path):
    preset = ConversionPreset(name="web", formats=["webp"])
    out = tmp_path / "a.webp"
    out.write_bytes(b"ok")
    with Manifest(tmp_path) as manifest:
        manifest.create_job("job1", _job_config(tmp_path), preset, "local")
        assert manifest.should_skip("new-fp", preset, [(out, "webp", "full")]) is False


def _asset(out):
    from dropraw_web.models import AssetResult

    return AssetResult(source_path="a.NEF", output_path=str(out), format="webp", status="done")


def _job_config(tmp_path):
    from dropraw_web.models import JobConfig

    return JobConfig(source=str(tmp_path), output_dir=tmp_path)

