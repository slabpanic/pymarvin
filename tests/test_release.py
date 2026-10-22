"""Prevent mismatched or non-normalized release metadata reaching PyPI."""

from pathlib import Path
import runpy

import pytest

validate = runpy.run_path(
    str(Path(__file__).parents[1] / ".github/scripts/check_release.py")
)["validate_release"]


@pytest.mark.parametrize("version", ["0.1.0", "1.2.3", "1.2.3rc1", "1.2.3.post1"])
def test_release_tag_matches_version(version):
    assert validate({"name": "pymarvin", "version": version}, "v" + version) == version


@pytest.mark.parametrize(
    "name,version,tag",
    [
        ("marvin", "1.0.0", "v1.0.0"),
        ("pymarvin", "1.0.0", "1.0.0"),
        ("pymarvin", "1.0.0", "v1.0.1"),
        ("pymarvin", "1.0.0-rc1", "v1.0.0rc1"),
        ("pymarvin", "invalid", "vinvalid"),
    ],
)
def test_release_rejects_inconsistent_metadata(name, version, tag):
    with pytest.raises(ValueError):
        validate({"name": name, "version": version}, tag)


wheel_namespace = runpy.run_path(
    str(Path(__file__).parents[1] / ".github/scripts/check_wheels.py")
)


def wheel_names():
    return [
        f"pymarvin-0.1.0-{python}-{python}-{platform}.whl"
        for python in sorted(wheel_namespace["PYTHONS"])
        for platform in sorted(wheel_namespace["PLATFORMS"])
    ]


def test_all_platform_wheels_required():
    assert wheel_namespace["validate_wheels"](wheel_names(), "0.1.0") == 15


@pytest.mark.parametrize(
    "problem", ["missing", "duplicate", "version", "abi", "platform", "name"]
)
def test_incomplete_or_mismatched_wheels_rejected(problem):
    wheels = wheel_names()
    if problem == "missing":
        wheels.pop()
    elif problem == "duplicate":
        wheels.append(wheels[0])
    elif problem == "version":
        wheels[0] = wheels[0].replace("0.1.0", "0.1.1")
    elif problem == "abi":
        wheels[0] = wheels[0].replace("-cp310-cp310-", "-cp310-abi3-")
    elif problem == "platform":
        wheels[0] = wheels[0].replace("manylinux_2_28_aarch64", "macosx_11_0_arm64")
    elif problem == "name":
        wheels[0] = wheels[0].replace("pymarvin-", "marvin-")
    with pytest.raises(ValueError):
        wheel_namespace["validate_wheels"](wheels, "0.1.0")
