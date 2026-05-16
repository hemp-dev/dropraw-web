from rawbridge.pipeline.scanner import detect_provider


def test_detect_local_provider(tmp_path):
    provider = detect_provider(str(tmp_path), "auto")
    assert provider.name == "local"


def test_detect_dropbox_provider():
    provider = detect_provider("https://www.dropbox.com/scl/fo/example", "auto", token="token")
    assert provider.name == "dropbox"


def test_detect_new_cloud_providers():
    assert detect_provider("https://drive.google.com/drive/folders/example", "auto").name == "google-drive"
    assert detect_provider("s3://bucket/raw", "auto").name == "s3"
    assert detect_provider("r2://bucket/raw", "auto").name == "s3"
    assert detect_provider("minio://bucket/raw", "auto").name == "s3"
    assert detect_provider("https://1drv.ms/f/example", "auto").name == "onedrive"
    assert detect_provider("https://disk.yandex.ru/d/example", "auto").name == "yadisk"
    assert detect_provider("https://app.box.com/folder/example", "auto").name == "box"
