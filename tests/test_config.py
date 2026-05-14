import pytest

from dropraw_web.config import load_presets, parse_csv_list, parse_int_csv, validate_formats, validate_quality


def test_load_presets_contains_web():
    presets = load_presets()
    assert presets["web"].formats == ["webp", "jpg"]
    assert presets["preview"].half_size is True


def test_parse_cli_lists():
    assert parse_csv_list("webp,jpg") == ["webp", "jpg"]
    assert parse_int_csv("1200, 1800") == [1200, 1800]


def test_validate_formats_and_quality():
    assert validate_formats(["jpeg", "webp"]) == ["jpg", "webp"]
    with pytest.raises(ValueError):
        validate_formats(["gif"])
    with pytest.raises(ValueError):
        validate_quality(0)

