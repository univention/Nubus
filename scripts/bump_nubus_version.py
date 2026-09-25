#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only
"""Update publiccode.yml to the latest nubus-helm release."""

import argparse
import datetime
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import NamedTuple

DEFAULT_API_URL = "https://git.knut.univention.de/api/v4"
DEFAULT_PROJECT = "univention/dev/nubus-for-k8s/nubus-helm"
DEFAULT_FILE = Path(__file__).resolve().parent.parent / "publiccode.yml"

VERSION_PATTERN = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
SOFTWARE_VERSION_PATTERN = re.compile(r'^softwareVersion: "([^"]*)"(?=\r?$)', re.MULTILINE)
RELEASE_DATE_PATTERN = re.compile(r'^releaseDate: "([^"]*)"(?=\r?$)', re.MULTILINE)


class Release(NamedTuple):
    """A released Nubus version.

    Attributes:
        version: Version without the leading "v", for example "1.23.0".
        date: Release date in ISO format, for example "2026-09-15".
    """

    version: str
    date: str


def parse_version(text: str) -> tuple[int, int, int]:
    """Parse a semantic version string.

    Args:
        text: Version such as "1.23.0" or "v1.23.0".

    Returns:
        The major, minor and patch numbers.

    Raises:
        ValueError: If the text is not a plain X.Y.Z version.
    """
    match = VERSION_PATTERN.match(text.strip())
    if not match:
        raise ValueError(f"Not a valid version: {text!r}")
    major, minor, patch = (int(part) for part in match.groups())
    return major, minor, patch


def release_from_api(data: dict) -> Release:
    """Build a release from a GitLab release API response.

    Args:
        data: JSON object from the GitLab releases API.

    Returns:
        The release with a normalized version and date.
    """
    tag = data["tag_name"]
    parse_version(tag)
    date = datetime.datetime.fromisoformat(data["released_at"]).date().isoformat()
    return Release(version=tag.removeprefix("v"), date=date)


def fetch_latest_release(api_url: str, project: str) -> Release:
    """Fetch the latest release of a GitLab project.

    Args:
        api_url: Base URL of the GitLab API v4.
        project: Project path, for example "group/project".

    Returns:
        The latest release.
    """
    encoded = urllib.parse.quote(project, safe="")
    url = f"{api_url}/projects/{encoded}/releases/permalink/latest"
    with urllib.request.urlopen(url, timeout=30) as response:
        return release_from_api(json.load(response))


def read_current_version(content: str) -> str:
    """Read the software version from publiccode.yml content.

    Args:
        content: Text of publiccode.yml.

    Returns:
        The current software version.

    Raises:
        ValueError: If the softwareVersion line is missing.
    """
    match = SOFTWARE_VERSION_PATTERN.search(content)
    if not match:
        raise ValueError("softwareVersion not found")
    return match.group(1)


def update_content(content: str, release: Release) -> str:
    """Set the software version and release date in publiccode.yml content.

    Args:
        content: Text of publiccode.yml.
        release: Release to write.

    Returns:
        The updated text.

    Raises:
        ValueError: If a field is not found exactly once.
    """
    for pattern, key, value in (
        (SOFTWARE_VERSION_PATTERN, "softwareVersion", release.version),
        (RELEASE_DATE_PATTERN, "releaseDate", release.date),
    ):
        content, count = pattern.subn(f'{key}: "{value}"', content)
        if count != 1:
            raise ValueError(f"Expected one {key} line, found {count}")
    return content


def bump(path: Path, release: Release) -> bool:
    """Update the file if the release is newer than the current version.

    Args:
        path: Path to publiccode.yml.
        release: Latest release.

    Returns:
        True if the file was changed.
    """
    with path.open(encoding="utf-8", newline="") as file:
        content = file.read()
    current = read_current_version(content)
    if parse_version(release.version) <= parse_version(current):
        print(f"Nubus {current} is up to date (latest release: {release.version}).")
        return False
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write(update_content(content, release))
    print(f"Bumped Nubus from {current} to {release.version} ({release.date}).")
    return True


def main(argv: list[str] | None = None) -> int:
    """Run the command line interface.

    Args:
        argv: Command line arguments. Uses sys.argv if None.

    Returns:
        Exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    parser.add_argument("--api-url", default=os.environ.get("CI_API_V4_URL", DEFAULT_API_URL))
    parser.add_argument("--project", default=os.environ.get("NUBUS_HELM_PROJECT", DEFAULT_PROJECT))
    args = parser.parse_args(argv)

    bump(args.file, fetch_latest_release(args.api_url, args.project))
    return 0


if __name__ == "__main__":
    sys.exit(main())
