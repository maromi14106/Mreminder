"""Test version module."""

from core.version import APP_NAME, APP_VERSION


def test_app_version():
    """Test app version information."""
    assert APP_NAME == "Mreminder"
    assert APP_VERSION == "1.0.0"


def test_windows_version_info():
    """Test that Windows version info matches APP_VERSION."""
    import re
    from pathlib import Path

    version_file = (
        Path(__file__).resolve().parents[1] / "resources" / "windows_version_info.txt"
    )
    assert version_file.exists(), "windows_version_info.txt not found"

    content = version_file.read_text(encoding="utf-8")

    # APP_VERSION is like "1.0.0", expected is "1.0.0.0"
    version_tuple_str = ", ".join(APP_VERSION.split(".") + ["0"])
    expected_version = f"{APP_VERSION}.0"

    # Check FixedFileInfo.filevers
    filevers_match = re.search(r"filevers=\(([^)]+)\)", content)
    assert filevers_match is not None, "FixedFileInfo.filevers not found"
    assert filevers_match.group(1).replace(" ", "") == version_tuple_str.replace(
        " ", ""
    )

    # Check FixedFileInfo.prodvers
    prodvers_match = re.search(r"prodvers=\(([^)]+)\)", content)
    assert prodvers_match is not None, "FixedFileInfo.prodvers not found"
    assert prodvers_match.group(1).replace(" ", "") == version_tuple_str.replace(
        " ", ""
    )

    # Check FileVersion
    file_version_match = re.search(
        r"StringStruct\('FileVersion',\s*'([^']+)'\)", content
    )
    assert (
        file_version_match is not None
    ), "FileVersion not found in resources/windows_version_info.txt"
    assert file_version_match.group(1) == expected_version

    # Check ProductVersion
    product_version_match = re.search(
        r"StringStruct\('ProductVersion',\s*'([^']+)'\)", content
    )
    assert (
        product_version_match is not None
    ), "ProductVersion not found in resources/windows_version_info.txt"
    assert product_version_match.group(1) == expected_version

    # Check ProductName
    product_name_match = re.search(
        r"StringStruct\('ProductName',\s*'([^']+)'\)", content
    )
    assert product_name_match is not None, "ProductName not found"
    assert product_name_match.group(1) == APP_NAME

    # Check OriginalFilename
    orig_filename_match = re.search(
        r"StringStruct\('OriginalFilename',\s*'([^']+)'\)", content
    )
    assert orig_filename_match is not None, "OriginalFilename not found"
    assert orig_filename_match.group(1) == f"{APP_NAME}.exe"
