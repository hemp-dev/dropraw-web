from dataclasses import dataclass

import pytest
from requests import ConnectionError

from rawbridge.models import RemoteFile
from rawbridge.providers.dropbox import DropboxProviderError, DropboxSharedProvider


class FolderMetadata:
    def __init__(self, name, path_display):
        self.name = name
        self.path_display = path_display


class FileMetadata:
    def __init__(self, name, path_display, size=3, rev="r1", id="id:1"):
        self.name = name
        self.path_display = path_display
        self.size = size
        self.rev = rev
        self.id = id


@dataclass
class Result:
    entries: list
    has_more: bool = False
    cursor: str = ""


class Response:
    def __init__(self, content):
        self.content = content


def test_listing_connection_error_then_succeeds():
    calls = {"count": 0}

    class Client:
        def files_list_folder(self, **kwargs):
            calls["count"] += 1
            if calls["count"] == 1:
                raise ConnectionError("connection aborted")
            return Result([FileMetadata("a.NEF", "/a.NEF")])

    provider = DropboxSharedProvider(api_factory=lambda: Client(), sleeper=lambda _: None, list_retries=2)
    files = list(provider.list_files("https://www.dropbox.com/scl/fo/example"))

    assert [file.path for file in files] == ["a.NEF"]
    assert calls["count"] == 2


def test_listing_continue_connection_error_then_succeeds():
    calls = {"continue": 0}

    class Client:
        def files_list_folder(self, **kwargs):
            return Result([], has_more=True, cursor="cursor")

        def files_list_folder_continue(self, cursor):
            calls["continue"] += 1
            if calls["continue"] == 1:
                raise ConnectionError("connection aborted")
            return Result([FileMetadata("b.NEF", "/b.NEF")])

    provider = DropboxSharedProvider(api_factory=lambda: Client(), sleeper=lambda _: None, list_retries=2)
    files = list(provider.list_files("https://www.dropbox.com/scl/fo/example"))

    assert [file.path for file in files] == ["b.NEF"]


def test_queue_recursion_and_filtering():
    seen_paths = []

    class Client:
        def files_list_folder(self, **kwargs):
            seen_paths.append(kwargs["path"])
            if kwargs["path"] == "":
                return Result([FolderMetadata("nested", "/nested"), FileMetadata("skip.JPG", "/skip.JPG")])
            return Result([FileMetadata("c.NEF", "/nested/c.NEF")])

    provider = DropboxSharedProvider(api_factory=lambda: Client())
    files = list(provider.list_files("https://www.dropbox.com/scl/fo/example"))

    assert seen_paths == ["", "/nested"]
    assert [file.path for file in files] == ["nested/c.NEF"]


def test_download_connection_error_then_succeeds(tmp_path):
    calls = {"download": 0, "paths": []}

    class Client:
        def files_download(self, **kwargs):
            calls["download"] += 1
            calls["paths"].append(kwargs["path"])
            if calls["download"] == 1:
                raise ConnectionError("connection aborted")
            return None, Response(b"abc")

    provider = DropboxSharedProvider(api_factory=lambda: Client(), sleeper=lambda _: None, download_retries=2)
    file = RemoteFile(provider="dropbox", id="1", name="a.NEF", path="a.NEF", size=3)
    path = provider.download_file(file, tmp_path)

    assert path.read_bytes() == b"abc"
    assert calls["paths"] == ["/a.NEF", "/a.NEF"]


def test_partial_download_removed_after_failure(tmp_path):
    class Client:
        def files_download(self, **kwargs):
            return None, Response(b"abc")

    provider = DropboxSharedProvider(api_factory=lambda: Client(), download_retries=1)
    file = RemoteFile(provider="dropbox", id="1", name="a.NEF", path="a.NEF", size=9)

    with pytest.raises(DropboxProviderError, match="Downloaded size mismatch"):
        provider.download_file(file, tmp_path)

    assert not list(tmp_path.glob("*.part"))


def test_leading_slash_path_is_used_first(tmp_path):
    class Client:
        def files_download(self, **kwargs):
            if not kwargs["path"].startswith("/"):
                raise ValueError("path did not match pattern")
            return None, Response(b"abc")

    provider = DropboxSharedProvider(api_factory=lambda: Client())
    file = RemoteFile(provider="dropbox", id="1", name="a.NEF", path="a.NEF", size=3)

    assert provider.download_file(file, tmp_path).exists()


def test_fingerprint_uses_dropbox_identity():
    provider = DropboxSharedProvider(api_factory=lambda: object())
    a = RemoteFile(provider="dropbox", id="id:1", name="a.NEF", path="a.NEF", size=3, revision="r1")
    b = RemoteFile(provider="dropbox", id="id:1", name="a.NEF", path="a.NEF", size=4, revision="r1")

    assert provider.fingerprint(a) != provider.fingerprint(b)
