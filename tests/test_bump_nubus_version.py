# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

import io
import json
from pathlib import Path

import pytest

import bump_nubus_version as bnv

CONTENT = """\
publiccodeYmlVersion: "0.4"
name: "Nubus"
softwareVersion: "1.22.0"
releaseDate: "2026-08-28"
logo: logos/logo.svg
"""


@pytest.fixture
def publiccode(tmp_path: Path) -> Path:
    path = tmp_path / "publiccode.yml"
    path.write_text(CONTENT)
    return path


@pytest.mark.parametrize(
    ("text", "expected"),
    [("1.23.0", (1, 23, 0)), ("v1.23.0", (1, 23, 0)), (" 2.0.10\n", (2, 0, 10))],
)
def test_parse_version(text: str, expected: tuple[int, int, int]) -> None:
    assert bnv.parse_version(text) == expected


@pytest.mark.parametrize("text", ["1.23", "v1.23.0-rc.1", "latest", ""])
def test_parse_version_rejects_invalid(text: str) -> None:
    with pytest.raises(ValueError):
        bnv.parse_version(text)


def test_release_from_api_uses_local_release_date() -> None:
    data = {"tag_name": "v1.23.0", "released_at": "2026-09-15T00:30:00.000+02:00"}
    assert bnv.release_from_api(data) == bnv.Release("1.23.0", "2026-09-15")


def test_release_from_api_rejects_prerelease() -> None:
    with pytest.raises(ValueError):
        bnv.release_from_api({"tag_name": "v1.24.0-rc.1", "released_at": "2026-09-15T00:00:00Z"})


def test_fetch_latest_release(monkeypatch: pytest.MonkeyPatch) -> None:
    requested = []

    def fake_urlopen(url: str, timeout: int) -> io.BytesIO:
        requested.append(url)
        return io.BytesIO(json.dumps({"tag_name": "v1.23.0", "released_at": "2026-09-15T16:05:59+02:00"}).encode())

    monkeypatch.setattr(bnv.urllib.request, "urlopen", fake_urlopen)

    release = bnv.fetch_latest_release("https://example.com/api/v4", "group/sub/project")

    assert release == bnv.Release("1.23.0", "2026-09-15")
    assert requested == ["https://example.com/api/v4/projects/group%2Fsub%2Fproject/releases/permalink/latest"]


def test_read_current_version() -> None:
    assert bnv.read_current_version(CONTENT) == "1.22.0"


def test_read_current_version_missing() -> None:
    with pytest.raises(ValueError):
        bnv.read_current_version('name: "Nubus"\n')


def test_update_content_changes_only_version_and_date() -> None:
    updated = bnv.update_content(CONTENT, bnv.Release("1.23.0", "2026-09-15"))
    assert updated == CONTENT.replace('"1.22.0"', '"1.23.0"').replace('"2026-08-28"', '"2026-09-15"')


def test_update_content_requires_release_date() -> None:
    with pytest.raises(ValueError):
        bnv.update_content('softwareVersion: "1.22.0"\n', bnv.Release("1.23.0", "2026-09-15"))


def test_bump_newer_release(publiccode: Path) -> None:
    assert bnv.bump(publiccode, bnv.Release("1.23.0", "2026-09-15"))
    assert 'softwareVersion: "1.23.0"' in publiccode.read_text()
    assert 'releaseDate: "2026-09-15"' in publiccode.read_text()


def test_bump_keeps_crlf_line_endings(tmp_path: Path) -> None:
    path = tmp_path / "publiccode.yml"
    path.write_bytes(CONTENT.replace("\n", "\r\n").encode())

    assert bnv.bump(path, bnv.Release("1.23.0", "2026-09-15"))

    expected = CONTENT.replace('"1.22.0"', '"1.23.0"').replace('"2026-08-28"', '"2026-09-15"')
    assert path.read_bytes() == expected.replace("\n", "\r\n").encode()


@pytest.mark.parametrize("version", ["1.22.0", "1.21.5"])
def test_bump_same_or_older_release(publiccode: Path, version: str) -> None:
    assert not bnv.bump(publiccode, bnv.Release(version, "2026-09-15"))
    assert publiccode.read_text() == CONTENT


def test_main(monkeypatch: pytest.MonkeyPatch, publiccode: Path) -> None:
    calls = []

    def fake_fetch(api_url: str, project: str) -> bnv.Release:
        calls.append((api_url, project))
        return bnv.Release("1.23.0", "2026-09-15")

    monkeypatch.setattr(bnv, "fetch_latest_release", fake_fetch)

    assert bnv.main(["--file", str(publiccode), "--api-url", "https://example.com/api/v4", "--project", "a/b"]) == 0
    assert calls == [("https://example.com/api/v4", "a/b")]
    assert 'softwareVersion: "1.23.0"' in publiccode.read_text()
