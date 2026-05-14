from dropraw_web.providers.dropbox import ensure_leading_slash


def test_ensure_leading_slash_for_shared_download():
    assert ensure_leading_slash("DSC_4777.NEF") == "/DSC_4777.NEF"
    assert ensure_leading_slash("/nested/DSC_4777.NEF") == "/nested/DSC_4777.NEF"

