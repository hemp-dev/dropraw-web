from rawbridge.models import FailedItem, RemoteFile
from rawbridge.pipeline.failed_log import filter_files_by_failed_log, read_failed_log, write_failed_log


def test_failed_log_roundtrip(tmp_path):
    path = write_failed_log(tmp_path, [FailedItem(rel_path="DSC_4777.NEF", error="boom\tbad\nline")])

    items = read_failed_log(path)

    assert items == [FailedItem(rel_path="DSC_4777.NEF", error="boom bad line")]


def test_only_failed_filters_files():
    files = [
        RemoteFile(provider="local", id="1", name="a.NEF", path="a.NEF"),
        RemoteFile(provider="local", id="2", name="b.NEF", path="nested/b.NEF"),
    ]

    filtered = filter_files_by_failed_log(files, ["nested/b.NEF"])

    assert [file.path for file in filtered] == ["nested/b.NEF"]

