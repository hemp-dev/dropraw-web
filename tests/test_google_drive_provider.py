from __future__ import annotations

import pytest

from rawbridge.providers.google_drive import GoogleDriveProvider, extract_folder_id, is_folder_metadata


def test_google_drive_folder_id_parser():
    assert extract_folder_id("https://drive.google.com/drive/folders/abc123") == "abc123"
    assert extract_folder_id("https://drive.google.com/drive/u/0/folders/abc123") == "abc123"
    assert extract_folder_id("https://drive.google.com/open?id=abc123") == "abc123"


def test_google_folder_detection():
    assert is_folder_metadata({"mimeType": "application/vnd.google-apps.folder"}) is True
    assert is_folder_metadata({"mimeType": "image/x-nikon-nef"}) is False


def test_google_pagination_and_raw_filtering():
    service = FakeDriveService(
        pages=[
            {
                "nextPageToken": "next",
                "files": [
                    {"id": "folder1", "name": "nested", "mimeType": "application/vnd.google-apps.folder"},
                    {"id": "skip", "name": "notes.gdoc", "mimeType": "application/vnd.google-apps.document"},
                ],
            },
            {"files": [{"id": "file1", "name": "a.NEF", "mimeType": "image/x-nikon-nef", "size": "3"}]},
            {"files": [{"id": "file2", "name": "b.jpg", "mimeType": "image/jpeg", "size": "3"}]},
        ]
    )
    provider = GoogleDriveProvider(service=service)

    files = list(provider.list_files("https://drive.google.com/drive/folders/root"))

    assert [file.path for file in files] == ["a.NEF"]
    assert files[0].size == 3


def test_google_listing_retry():
    service = FakeDriveService(pages=[{"files": [{"id": "file1", "name": "a.NEF", "size": "1"}]}], fail_lists=1)
    events = []
    provider = GoogleDriveProvider(service=service, sleeper=lambda _: None, list_retries=2, event_callback=lambda *args: events.append(args))

    assert [file.path for file in provider.list_files("https://drive.google.com/drive/folders/root")] == ["a.NEF"]
    assert events and events[0][2]["type"] == "listing_retry"


def test_google_part_cleanup_after_size_mismatch(tmp_path):
    service = FakeDriveService(download=b"abc")
    provider = GoogleDriveProvider(service=service, download_retries=1)
    file = next(provider.list_files("https://drive.google.com/drive/folders/root"))

    with pytest.raises(Exception, match="size mismatch"):
        provider.download_file(file, tmp_path)
    assert not list(tmp_path.glob("*.part"))


class FakeDriveService:
    def __init__(self, pages=None, fail_lists=0, download=b"abc"):
        self.pages = pages or [{"files": [{"id": "file1", "name": "a.NEF", "size": "9"}]}]
        self.fail_lists = fail_lists
        self.download = download
        self.calls = 0

    def files(self):
        return self

    def list(self, **kwargs):
        return FakeListRequest(self)

    def get_media(self, **kwargs):
        return FakeMediaRequest(self.download)


class FakeListRequest:
    def __init__(self, service):
        self.service = service

    def execute(self):
        self.service.calls += 1
        if self.service.fail_lists:
            self.service.fail_lists -= 1
            raise RuntimeError("temporary")
        index = min(self.service.calls - 1, len(self.service.pages) - 1)
        return self.service.pages[index]


class FakeMediaRequest:
    def __init__(self, content):
        self.content = content

    def execute(self):
        return self.content
