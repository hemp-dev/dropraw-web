from rawbridge.constants import is_raw_file


def test_is_raw_file_case_insensitive():
    assert is_raw_file("DSC_001.NEF")
    assert is_raw_file("photo.nef")
    assert is_raw_file("raw.CR3")
    assert not is_raw_file("image.JPG")
    assert not is_raw_file("file")

