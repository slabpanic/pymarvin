"""Require every supported CPython/platform wheel before publishing a release."""

import argparse
from pathlib import Path

from packaging.utils import parse_wheel_filename
from packaging.version import Version

PYTHONS = {f"cp3{minor}" for minor in range(10, 15)}
PLATFORMS = {"manylinux_2_28_x86_64", "manylinux_2_28_aarch64", "win_amd64"}


def validate_wheels(paths, version):
    """Reject missing, duplicate, incorrectly named or mismatched wheel artifacts."""
    expected = {(python, platform) for python in PYTHONS for platform in PLATFORMS}
    found = set()
    for path in paths:
        name, actual_version, build, tags = parse_wheel_filename(Path(path).name)
        if name != "pymarvin" or actual_version != Version(version) or build:
            raise ValueError(f"Unexpected wheel metadata: {path}")
        identities = {
            (tag.interpreter, tag.platform)
            for tag in tags
            if tag.abi == tag.interpreter
            and (tag.interpreter, tag.platform) in expected
        }
        if len(identities) != 1:
            raise ValueError(f"Unexpected interpreter, ABI or platform: {path}")
        identity = identities.pop()
        if identity in found:
            raise ValueError(f"Duplicate platform wheel: {path}")
        found.add(identity)
    if found != expected:
        raise ValueError(f"Missing platform wheels: {sorted(expected - found)}")
    return len(found)


if __name__ == "__main__":
    import tomllib

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    count = validate_wheels(args.directory.glob("*.whl"), project["version"])
    print(f'Validated {count} platform wheels for pymarvin {project["version"]}')
