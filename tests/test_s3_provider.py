from __future__ import annotations

import pytest

from rawbridge.models import RemoteFile
from rawbridge.providers.s3 import S3Provider, parse_s3_url


def test_parse_s3_urls():
    assert parse_s3_url("s3://bucket/prefix").bucket == "bucket"
    assert parse_s3_url("r2://bucket/prefix").scheme == "r2"
    assert parse_s3_url("minio://bucket/prefix").prefix == "prefix"
    assert parse_s3_url("https://example.com") is None


def test_s3_list_filters_raw():
    provider = S3Provider(client=FakeS3Client(contents=[
        {"Key": "raw/a.NEF", "Size": 3, "ETag": "e1"},
        {"Key": "raw/b.jpg", "Size": 3, "ETag": "e2"},
    ]))

    files = list(provider.list_files("s3://bucket/raw"))

    assert [file.path for file in files] == ["a.NEF"]
    assert files[0].raw["bucket"] == "bucket"


def test_s3_listing_retry():
    events = []
    provider = S3Provider(
        client=FakeS3Client(contents=[{"Key": "a.NEF", "Size": 1}], fail_paginate=1),
        list_retries=2,
        sleeper=lambda _: None,
        event_callback=lambda *args: events.append(args),
    )

    assert [file.path for file in provider.list_files("s3://bucket/")] == ["a.NEF"]
    assert events and events[0][2]["type"] == "listing_retry"


def test_s3_download_retry_and_part_cleanup(tmp_path):
    client = FakeS3Client(download_failures=1, download_content=b"abc")
    provider = S3Provider(client=client, download_retries=2, sleeper=lambda _: None)
    file = RemoteFile(provider="s3", id="s3://bucket/a.NEF", name="a.NEF", path="a.NEF", size=3, raw={"bucket": "bucket", "key": "a.NEF"})

    path = provider.download_file(file, tmp_path)

    assert path.read_bytes() == b"abc"
    assert not list(tmp_path.glob("*.part"))


def test_s3_fingerprint_changes_with_etag():
    provider = S3Provider(client=FakeS3Client())
    a = RemoteFile(provider="s3", id="1", name="a.NEF", path="a.NEF", size=1, revision="e1", raw={"bucket": "b", "key": "a.NEF"})
    b = RemoteFile(provider="s3", id="1", name="a.NEF", path="a.NEF", size=1, revision="e2", raw={"bucket": "b", "key": "a.NEF"})

    assert provider.fingerprint(a) != provider.fingerprint(b)


class FakeS3Client:
    def __init__(self, contents=None, fail_paginate=0, download_failures=0, download_content=b""):
        self.contents = contents or []
        self.fail_paginate = fail_paginate
        self.download_failures = download_failures
        self.download_content = download_content

    def get_paginator(self, name):
        return self

    def paginate(self, **kwargs):
        if self.fail_paginate:
            self.fail_paginate -= 1
            raise RuntimeError("temporary")
        return [{"Contents": self.contents}]

    def download_file(self, **kwargs):
        filename = kwargs["Filename"]
        if self.download_failures:
            self.download_failures -= 1
            with open(filename, "wb") as handle:
                handle.write(b"part")
            raise RuntimeError("temporary")
        with open(filename, "wb") as handle:
            handle.write(self.download_content)
