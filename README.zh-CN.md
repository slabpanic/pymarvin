# pymarvin

[![CI](https://github.com/slabpanic/pymarvin/actions/workflows/ci.yml/badge.svg)](https://github.com/slabpanic/pymarvin/actions/workflows/ci.yml)
[![文档](https://readthedocs.org/projects/pymarvin/badge/?version=latest)](https://pymarvin.readthedocs.io/zh-cn/latest/)
[![PyPI](https://img.shields.io/pypi/v/pymarvin.svg)](https://pypi.org/project/pymarvin/)
[![codecov](https://codecov.io/gh/slabpanic/pymarvin/graph/badge.svg)](https://codecov.io/gh/slabpanic/pymarvin)

[English](README.md)

通过 [nanobind](https://nanobind.readthedocs.io/)、CMake 和 scikit-build-core
构建的天机 Marvin 机器人 Python 绑定。发行包名和导入名均为 **pymarvin**。

控制、运动学和干涉检测 SDK 已集成到发行包并编译为原生扩展。支持的平台会直接
提供包含 SDK 的 wheel，安装时不需要额外安装厂商 SDK 或编译器。

## 功能

- 与官方接口兼容的控制器、离线运动学和干涉检测 API。
- 通过 nanobind 调用原生 C++，并验证 Python 数值和缓冲区参数。
- 控制器指令、遥测、运动规划、辨识和文件传输。
- 正逆运动学、雅可比矩阵、轨迹规划，以及支持上下文管理的托管 `PointSet`。
- 使用随包 CCSM6 模型定义文件进行碰撞距离和阈值检测。
- 可脱离控制器运行的离线示例，以及官方控制和规划示例。
- Linux 和 Windows wheel 由同一套经过测试的 CI 产物发布。

## 环境要求

| 项目 | 支持范围 |
| --- | --- |
| 平台 | Linux x86_64/aarch64 或 Windows x64 |
| Python | CPython 3.10–3.14 |
| 运行时 SDK | 已包含在支持的 wheel 中 |
| 源码构建 | C++17 编译器、CMake 及 nanobind 构建依赖 |

不发布 macOS、PyPy 和 32 位 Windows wheel。机器人运动及控制器相关功能需要兼容的
Marvin 控制器和对应机型配置文件。

## 安装

使用 uv 或 pip 安装已发布的 wheel：

```bash
uv add pymarvin
```

```bash
python -m pip install pymarvin
```

支持的平台安装后即可导入。源码包也可以使用 C++17 工具链和 CMake 构建；源码包中
包含所需的原生 SDK 源码。

## 快速开始

运动学和干涉检测可以在没有硬件的情况下运行：

```python
from pymarvin import Marvin_Kine, PointSet

kine = Marvin_Kine()
pose = kine.xyzabc_to_mat4x4([100, 200, 300, 0, 0, 0])
print(kine.mat4x4_to_xyzabc(pose))

with PointSet(dimension=7) as points:
    points.append([0, 0, 0, 0, 0, 0, 0])
    print(points.to_list())
```

控制器接口保留官方的清空、设置、发送流程：

```python
from pymarvin import DCSS, Marvin_Robot

robot = Marvin_Robot()
if not robot.connect("192.168.1.10"):
    raise RuntimeError("无法连接控制器")
try:
    print(robot.subscribe(DCSS())["states"])
finally:
    robot.release_robot()
```

导入包和创建接口对象都不会自动连接机器人。

## API 兼容性

| 模块 | 主要接口 |
| --- | --- |
| `pymarvin.fx_robot` | `Marvin_Robot`、`Concise_Marvin_Robot`、控制器数据结构和指令辅助函数 |
| `pymarvin.fx_kine` | `Marvin_Kine`、运动学数据结构、雅可比矩阵和规划辅助函数 |
| `pymarvin.fx_interference` | `Marvin_Interference` 和干涉检测状态常量 |

各接口保留官方的方法名、参数顺序和返回约定。规划方法仍返回 `(data, pset)`，其中
`pset` 是自动管理内存的 `PointSet`，而不是整数地址；支持 `close()` 和上下文管理。

## 示例

源码包包含官方 Marvin Python 示例。大多数控制器示例需要可连接的机器人，并可能发送
运动、力矩、拖动、刹车或文件传输指令；在真实机器人上运行前请先阅读对应示例。

以下示例无需硬件：

```bash
python examples/offline_kinematics.py
python examples/offline_interference.py
```

干涉检测示例使用随包模型定义文件，演示拖动模式下的实时碰撞检测：

```bash
python examples/showcase_drag_interference.py
```

## 文档

- [英文文档](https://pymarvin.readthedocs.io/en/latest/)
- [中文文档](https://pymarvin.readthedocs.io/zh-cn/latest/)
- [示例说明](examples/README.md)
- [兼容性说明](docs/compatibility.rst)
- [开发与发布](docs/development.rst)

## SDK 来源与许可证

随包官方 SDK 快照来自
[TJ_FX_ROBOT_CONTRL_SDK](https://github.com/cynthia-you/TJ_FX_ROBOT_CONTRL_SDK)
的 `master` 分支，提交号为
[`bc4f61104a66e82b4c750f3a0bc7a95c9ef44139`](https://github.com/cynthia-you/TJ_FX_ROBOT_CONTRL_SDK/commit/bc4f61104a66e82b4c750f3a0bc7a95c9ef44139)。
SDK 使用 Apache License 2.0。绑定修改和第三方依赖许可证见
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
