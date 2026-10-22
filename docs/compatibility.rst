Compatibility and implementation
================================

The public API follows the official Marvin ``fx_robot.py`` and ``fx_kine.py``
interfaces, preserving method names, argument order, defaults and return conventions.
The nanobind sources in ``src/bindings/`` and Python facades in ``src/pymarvin/``
are maintained directly. English API docstrings live alongside their implementations.

The bundled official SDK snapshot comes from the ``master`` branch of
`TJ_FX_ROBOT_CONTRL_SDK <https://github.com/cynthia-you/TJ_FX_ROBOT_CONTRL_SDK>`_
at commit ``bc4f61104a66e82b4c750f3a0bc7a95c9ef44139``. Project binding changes
and source corrections are recorded in ``THIRD_PARTY_NOTICES.md``.

ctypes is used only for compatible records and temporary buffers. All SDK calls go
through the compiled nanobind modules; no ``CDLL`` or ``WinDLL`` loading is used. Every
public record size and field offset is checked against the C++ compiler at import time.

The three SDKs contain common helper names but separate implementations. They are compiled
into separate extensions with hidden symbols. Point data is copied across the control and
kinematics boundary instead of casting their C++ object pointers.

SDK state is global: instances share a connection and model slots, including arm slots 0
and 1. Calls retain the GIL; concurrent SDK operations from multiple threads are not
promised.

Control SDK revision
--------------------

Control builds use ``src/sdk/control/``, reporting version ``100343014``. Kinematics
sources live in ``src/sdk/kinematics/`` and interference sources in
``src/sdk/interference/``. All three SDKs are Apache-2.0 and are compiled into
distributed wheels. Obsolete SDK revisions, Python reference copies and vendor binary
libraries have been removed. Tests compare the active SDK headers with the installed
native API.

Restored interfaces cover ABI checks, force/torque commands, velocity-estimation steps,
robot names, force-sensor reset, system time, reboot, motion stopping and user telemetry
selection. ``FTCmd`` is passed by value and robot names use a checked 512-byte writable
output buffer.

The binding checks that the native controller instance exists before commands that would
otherwise dereference a null singleton. The official facade still applies its existing
exception and failure-return conventions. Releasing an uninitialized instance repeatedly
is safe.

The official ``fx_interference`` interface and the interference-check implementation are
included under ``src/sdk/interference/``. The bundled model definition files are installed
under ``pymarvin/interference_configs/``. Robot-controller firmware compatibility must
still be established for the installed SDK version.

Platform support
----------------

Release wheels target Linux x86_64/aarch64 with glibc 2.28 or newer and Windows x64
on CPython 3.10–3.14. macOS is not included. The SDK uses its POSIX implementation
on Linux and Windows sockets, shared memory and multimedia timers on Windows.

C ``long`` is 64-bit on supported Linux targets and 32-bit on Windows x64.
The Python facade uses platform-native ctypes values for these arguments; telemetry
uses fixed-width fields whose sizes and offsets are checked against the compiled SDK.

Source corrections
------------------

The vendor linear-speed function multiplies the Jacobian by joint positions instead of
angular rates and mixes metres with millimetres. The binding uses ``norm(J_linear @
radians(angvel)) * 1000`` to return mm/s, verified against finite differences of FK.

Both ``FTArmControl`` branches now zero-initialize all seven force-control array
elements directly in the maintained SDK source. Windows builds explicitly include
the multimedia API and use narrow shared-memory path APIs. Original SDK authorship
notices are retained; modifications are recorded in ``THIRD_PARTY_NOTICES.md``.

Validation scope
----------------

Offline tests cover numeric kinematics, public facade marshaling with recording
backends, buffer validation, ownership and failure paths. GCC coverage measures binding
code under ``src/bindings/``; SDK source and nanobind internals are not counted. Python
coverage includes all package modules and branches. Each release wheel is installed
and tested on its matching platform before publication.

No physical robot motion, PVT execution, controller update, network file transfer or
sensor calibration has been validated. Offline coverage is not a hardware execution
certification.

See ``THIRD_PARTY_NOTICES.md`` for provenance, SDK modifications and licensing terms.
