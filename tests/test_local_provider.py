from pathlib import Path

from rawbridge.providers.local import LocalProvider


def test_local_provider_recursive_scan(tmp_path):
    (tmp_path / "day1").mkdir()
    (tmp_path / "day1" / "DSC_001.NEF").write_bytes(b"raw")
    (tmp_path / "day1" / "image.JPG").write_bytes(b"jpg")
    (tmp_path / "day2").mkdir()
    (tmp_path / "day2" / "raw.CR3").write_bytes(b"raw")

    files = list(LocalProvider().list_files(str(tmp_path)))

    assert [file.path for file in files] == ["day1/DSC_001.NEF", "day2/raw.CR3"]
    assert all(file.provider == "local" for file in files)


def test_local_provider_download_returns_original(tmp_path):
    raw = tmp_path / "photo.nef"
    raw.write_bytes(b"raw")
    file = next(LocalProvider().list_files(str(tmp_path)))

    assert LocalProvider().download_file(file, tmp_path / "tmp") == raw.resolve()

