from pathlib import Path

import pytest

from rawbridge.models import RemoteFile
from rawbridge.pipeline.scanner import output_paths_for_file, safe_relative_path


def remote(path: str) -> RemoteFile:
    return RemoteFile(provider="local", id=path, name=Path(path).name, path=path)


def test_output_paths_preserve_structure(tmp_path):
    paths = output_paths_for_file(remote("day1/DSC_0012.NEF"), tmp_path, ["webp", "jpg"], [])
    assert [path.relative_to(tmp_path).as_posix() for path, _, _ in paths] == [
        "day1/DSC_0012.webp",
        "day1/DSC_0012.jpg",
    ]


def test_responsive_output_paths(tmp_path):
    paths = output_paths_for_file(remote("day1/DSC_0012.NEF"), tmp_path, ["webp"], [1200, 1800])
    assert [path.relative_to(tmp_path).as_posix() for path, _, _ in paths] == [
        "day1/DSC_0012@1200.webp",
        "day1/DSC_0012@1800.webp",
    ]


def test_safe_relative_path_blocks_traversal():
    assert safe_relative_path("../evil/DSC.NEF").as_posix() == "evil/DSC.NEF"
    assert safe_relative_path("/abs/DSC.NEF").as_posix() == "abs/DSC.NEF"
    with pytest.raises(ValueError):
        safe_relative_path("../..")

