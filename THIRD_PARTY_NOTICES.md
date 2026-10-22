# Third-party notices

The Tianji Marvin control SDK (version 100343014), kinematics SDK and
interference-check SDK are included under **Apache License 2.0**, as confirmed
by the project maintainer. Their required C++ headers and implementation files
live in `src/sdk/control/`, `src/sdk/kinematics/` and `src/sdk/interference/`.
All three SDKs are compiled into the Python extensions; installation of a
matching wheel requires no separate SDK or compiler.

The bundled official SDK snapshot was obtained from the ``master`` branch of
the [TJ_FX_ROBOT_CONTRL_SDK repository](https://github.com/cynthia-you/TJ_FX_ROBOT_CONTRL_SDK)
at commit [`bc4f61104a66e82b4c750f3a0bc7a95c9ef44139`](https://github.com/cynthia-you/TJ_FX_ROBOT_CONTRL_SDK/commit/bc4f61104a66e82b4c750f3a0bc7a95c9ef44139).
This provenance applies to the bundled control, kinematics, interference,
Python facade and model-definition files; project changes are listed below.

The SDK's Apache license and attribution notice are included in every source
distribution and wheel under `pymarvin/licenses/marvin-sdk/`. Original authorship
notices remain in the SDK source files. The obsolete control revision, SDK_PYTHON
facade copies, vendor build instructions and supplied binary libraries have been
removed. The upstream Python showcase scripts are retained under `examples/`
with their imports adapted to this package. Wheels contain the SDK compiled from
this project's sources, including the interference-check implementation and its
model definition files.

Changes to the supplied SDK include zero-initializing the seventh force-control
parameter in both `FTArmControl` branches, explicitly including the Windows
multimedia API, and selecting narrow Windows shared-memory path APIs. The
bindings isolate the three SDK implementations, validate buffers and ABI layouts,
and correct linear-speed calculation using the kinematics Jacobian.

`src/pymarvin/fx_robot.py` and `src/pymarvin/fx_kine.py` retain the official
Python interface with English docstrings. ctypes is used for compatible value
records and temporary buffers; SDK calls use the compiled nanobind extensions.

Project-authored bindings and Python code use the root MIT license. The bundled
nanobind code uses BSD 3-Clause and robin-map uses MIT. Their original notices
are shipped under `pymarvin/licenses/nanobind/` and `pymarvin/licenses/robin-map/`.
scikit-build-core is a build tool and is not compiled into the extensions.
Platform wheel repair bundles additional non-system runtime libraries when needed.
