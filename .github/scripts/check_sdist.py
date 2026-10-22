"""Build and smoke-test an sdist without an external SDK."""

import os
from email.parser import BytesParser
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import zipfile

archive = Path(sys.argv[1]).resolve()
with tarfile.open(archive) as source:
    names = source.getnames()
    metadata = next(
        name for name in names if name.count("/") == 1 and name.endswith("/PKG-INFO")
    )
    expected_version = BytesParser().parsebytes(source.extractfile(metadata).read())[
        "Version"
    ]
    for suffix in [
        "CMakeLists.txt",
        "src/bindings/_control.cpp",
        "src/bindings/_kinematics.cpp",
        "src/bindings/_interference.cpp",
        "docs/_ext/generate_api.py",
        "docs/_ext/check_translations.py",
        "src/sdk/control/MarvinSDK.cpp",
        "src/sdk/kinematics/FxRobot.cpp",
        "src/sdk/interference/Interf/Interference.cpp",
        "src/pymarvin/interference_configs/InterfDef.Interf",
    ]:
        assert any(name.endswith("/" + suffix) for name in names), suffix
    assert not any(name.endswith((".so", ".pyd", ".dll")) for name in names)
    assert not any(
        name.split("/", 1)[-1].startswith(("tools/", "native/", "vendor/"))
        for name in names
    )
    assert not any("/docs/api/_generated/" in name for name in names)

with tempfile.TemporaryDirectory(prefix="pymarvin-sdist-") as temp:
    root = Path(temp)
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in {"PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"}
    }
    subprocess.run(
        [
            "uv",
            "build",
            str(archive),
            "--wheel",
            "--python",
            sys.executable,
            "--out-dir",
            str(root / "wheels"),
        ],
        cwd=root,
        env=env,
        check=True,
    )
    wheel = next((root / "wheels").glob("*.whl"))
    with zipfile.ZipFile(wheel) as binary:
        names = binary.namelist()
        assert any(
            name.startswith("pymarvin/_control.") and name.endswith((".so", ".pyd"))
            for name in names
        )
        assert any(
            name.startswith("pymarvin/_kinematics.") and name.endswith((".so", ".pyd"))
            for name in names
        )
        assert any(
            name.startswith("pymarvin/_interference.")
            and name.endswith((".so", ".pyd"))
            for name in names
        )
        assert "pymarvin/interference_configs/InterfDef.Interf" in names
        assert not any(
            name.startswith(("sdk/", "bindings/", "vendor/")) for name in names
        )
        for notice in [
            "nanobind/LICENSE",
            "robin-map/LICENSE",
            "marvin-sdk/LICENSE",
            "marvin-sdk/NOTICE",
        ]:
            assert any(name.endswith("licenses/" + notice) for name in names), notice
    subprocess.run(
        ["uv", "venv", "--python", sys.executable, str(root / "venv")],
        cwd=root,
        env=env,
        check=True,
    )
    python = root / (
        "venv/Scripts/python.exe" if os.name == "nt" else "venv/bin/python"
    )
    subprocess.run(
        ["uv", "pip", "install", "--python", str(python), "--no-deps", str(wheel)],
        cwd=root,
        env=env,
        check=True,
    )
    subprocess.run(
        [
            str(python),
            "-I",
            "-c",
            f"""
import pymarvin
assert pymarvin.__version__ == {expected_version!r}
k = pymarvin.Marvin_Kine()
assert k.mat4x4_to_xyzabc(k.xyzabc_to_mat4x4([1, 2, 3, 0, 0, 0])) == [1, 2, 3, 0, 0, 0]
with pymarvin.PointSet(7) as points:
    assert points.append([1, 2, 3, 4, 5, 6, 7])
    assert points.to_list() == [[1, 2, 3, 4, 5, 6, 7]]
assert points.closed
checker = pymarvin.Marvin_Interference()
assert checker.get_min_span() == (-2, 0.0)
checker.destroy()
print('Independent sdist -> wheel -> installation passed:', pymarvin.__file__)
""",
        ],
        cwd=root,
        env=env,
        check=True,
    )
