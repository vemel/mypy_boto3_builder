import pytest
from packaging.version import Version

from mypy_boto3_builder.utils.version import (
    bump_postrelease,
    get_builder_version,
    get_max_build_version,
    get_min_build_version,
    get_release_version,
    is_valid_version,
    sort_versions,
    stringify_parts,
)


class TestStrings:
    def test_get_builder_version(self) -> None:
        assert Version(get_builder_version())

    def test_get_min_build_version(self) -> None:
        assert get_min_build_version("1.22.36") == "1.22.0"
        assert get_min_build_version("1.22.48.post13") == "1.22.0"
        assert get_min_build_version("1.13.3") == "1.13.0"
        assert get_min_build_version("1.13.2.post56") == "1.13.0"

    def test_get_max_build_version(self) -> None:
        assert get_max_build_version("1.22.36") == "1.23.0"
        assert get_max_build_version("1.22.48.post13") == "1.23.0"
        assert get_max_build_version("1.13.3") == "1.14.0"
        assert get_max_build_version("1.13.2.post56") == "1.14.0"

    def test_bump_postrelease(self) -> None:
        assert bump_postrelease("1.22.36") == "1.22.36.post1"
        assert bump_postrelease("1.22.36.post") == "1.22.36.post1"
        assert bump_postrelease("1.22.36.post0") == "1.22.36.post1"
        assert bump_postrelease("1.22.36.post5") == "1.22.36.post6"

    def test_get_release_version(self) -> None:
        assert get_release_version("1.22.36") == "1.22.36"
        assert get_release_version("1.22.36.post13") == "1.22.36"
        assert get_release_version("1.13.2.post56+dev123") == "1.13.2"

    def test_is_valid_version(self) -> None:
        assert is_valid_version("1.2.3")
        assert is_valid_version("1.2.3.post1")
        assert not is_valid_version("1.2.3dev3.4")

    def test_sort_versions(self) -> None:
        assert sort_versions(["1.2.3.post1", "1.2.3", "1.2.3dev3.4"]) == ["1.2.3", "1.2.3.post1"]

    def test_stringify_parts(self) -> None:
        assert stringify_parts((1, 2, 3)) == "1.2.3"
        assert stringify_parts((1, 3)) == "1.3"
        assert stringify_parts((3,)) == "3"
        with pytest.raises(ValueError, match="Empty version parts"):
            stringify_parts(())
