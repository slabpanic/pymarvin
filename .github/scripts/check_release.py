"""Reject a release unless the tag matches the normalized package version."""

import os
from pathlib import Path

from packaging.version import Version


def validate_release(project, tag):
    if project["name"] != "pymarvin":
        raise ValueError("The distribution name must be pymarvin")
    version = str(Version(project["version"]))
    if project["version"] != version:
        raise ValueError(f"Use the normalized project version: {version}")
    if tag != f"v{version}":
        raise ValueError(f"Release tag {tag!r} must match v{version}")
    return version


if __name__ == "__main__":
    import tomllib

    project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
    validate_release(project, os.environ["GITHUB_REF_NAME"])
