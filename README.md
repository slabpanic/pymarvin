# pymarvin

[![CI](https://github.com/slabpanic/pymarvin/actions/workflows/ci.yml/badge.svg)](https://github.com/slabpanic/pymarvin/actions/workflows/ci.yml)
[![Documentation](https://readthedocs.org/projects/pymarvin/badge/?version=latest)](https://pymarvin.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/pymarvin.svg)](https://pypi.org/project/pymarvin/)
[![codecov](https://codecov.io/gh/slabpanic/pymarvin/graph/badge.svg)](https://codecov.io/gh/slabpanic/pymarvin)

[简体中文](README.zh-CN.md)

High-performance Python bindings for Tianji Marvin robots, built with
[nanobind](https://nanobind.readthedocs.io/), CMake and scikit-build-core.
The distribution and import names are both **pymarvin**.

The control, kinematics and interference SDK implementations are bundled in the
package and compiled into its native extensions. Supported wheels include the
SDK, so installation does not require a separate vendor SDK or compiler.

## Features

- Official-compatible controller, offline kinematics and interference-check APIs.
- Native C++ execution through nanobind, with Python value and buffer validation.
- Controller commands, telemetry, motion planning, identification and file transfer.
- Forward/inverse kinematics, Jacobians, trajectory planning and owned `PointSet`
  objects with context-manager support.
- Collision distance and threshold checks with bundled CCSM6 model definitions.
- Offline examples that run without a controller, plus the official controller
  and planning showcases.
- Linux and Windows wheels published through the same tested CI artifacts.

## Requirements

| Requirement | Support |
| --- | --- |
| Platform | Linux x86_64/aarch64 or Windows x64 |
| Python | CPython 3.10–3.14 |
| Runtime SDK | Included in supported wheels |
| Source build | C++17 compiler, CMake and nanobind build dependencies |

macOS wheels, PyPy and 32-bit Windows are not published. Robot motion and
controller-dependent operations require a compatible Marvin controller and its
configuration files.

## Installation

Install a released wheel with uv or pip:

```bash
uv add pymarvin
```

```bash
python -m pip install pymarvin
```

Supported wheels are ready to import. A source distribution can also be built
with a C++17 toolchain and CMake; the native SDK sources are included in that
archive.

## Quick start

Kinematics and interference checks can run without hardware:

```python
from pymarvin import Marvin_Kine, PointSet

kine = Marvin_Kine()
pose = kine.xyzabc_to_mat4x4([100, 200, 300, 0, 0, 0])
print(kine.mat4x4_to_xyzabc(pose))

with PointSet(dimension=7) as points:
    points.append([0, 0, 0, 0, 0, 0, 0])
    print(points.to_list())
```

The controller facade keeps the official clear-set-send workflow:

```python
from pymarvin import DCSS, Marvin_Robot

robot = Marvin_Robot()
if not robot.connect("192.168.1.10"):
    raise RuntimeError("Cannot connect to the controller")
try:
    print(robot.subscribe(DCSS())["states"])
finally:
    robot.release_robot()
```

Importing the package and constructing a facade do not connect to a robot.

## API compatibility

| Module | Main interfaces |
| --- | --- |
| `pymarvin.fx_robot` | `Marvin_Robot`, `Concise_Marvin_Robot`, controller records and command helpers |
| `pymarvin.fx_kine` | `Marvin_Kine`, kinematics records, Jacobians and planning helpers |
| `pymarvin.fx_interference` | `Marvin_Interference` and interference status constants |

The facades preserve the official method names, argument order and return
conventions. Planning methods retain the `(data, pset)` convention, while
`pset` is an owned `PointSet` rather than an integer address. `close()` and
context-manager support are available for owned point sets.

## Examples

The source distribution includes the official Marvin Python showcases. Most
controller examples require a reachable robot and may issue motion, torque,
drag, brake or file-transfer commands. Read the selected example before running
it on a robot.

The following examples are hardware-independent:

```bash
python examples/offline_kinematics.py
python examples/offline_interference.py
```

The interference showcase uses the bundled model definitions and demonstrates
live collision checks during drag mode:

```bash
python examples/showcase_drag_interference.py
```

## Documentation

- [English documentation](https://pymarvin.readthedocs.io/en/latest/)
- [Chinese documentation](https://pymarvin.readthedocs.io/zh-cn/latest/)
- [Examples guide](examples/README.md)
- [Compatibility notes](docs/compatibility.rst)
- [Development and publishing](docs/development.rst)

## SDK source and license

The bundled official SDK snapshot comes from the `master` branch of
[TJ_FX_ROBOT_CONTRL_SDK](https://github.com/cynthia-you/TJ_FX_ROBOT_CONTRL_SDK),
commit [`bc4f61104a66e82b4c750f3a0bc7a95c9ef44139`](https://github.com/cynthia-you/TJ_FX_ROBOT_CONTRL_SDK/commit/bc4f61104a66e82b4c750f3a0bc7a95c9ef44139).
The SDK is distributed under Apache License 2.0. Project binding changes and
third-party license details are recorded in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
