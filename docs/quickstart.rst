Installation and usage
======================

Install from PyPI with uv or pip. Tagged releases provide prebuilt wheels for
CPython 3.10–3.14 on Linux x86_64/aarch64 (glibc 2.28+) and Windows x64. A supported
wheel includes the compiled SDK and needs no compiler or separate SDK installation.
Building from the source archive requires a C++17 compiler and CMake.

.. code-block:: bash

   uv add pymarvin
   # Alternatively:
   python -m pip install pymarvin

Importing the package or constructing a facade does not connect to a robot.

Offline pose conversion
-----------------------

.. code-block:: python

   from pymarvin import Marvin_Kine

   kine = Marvin_Kine()
   pose = kine.xyzabc_to_mat4x4([100, 200, 300, 0, 0, 0])
   print(kine.mat4x4_to_xyzabc(pose))

Initialize a robot model
------------------------

Robot-specific calculations require a matching vendor configuration. Load the chosen
arm, then initialize robot type, DH parameters and joint limits before FK, IK or
planning. Poses use millimetres/degrees; joint angles use degrees.

.. code-block:: python

   config = kine.load_config(arm_type=0, config_path="robot.MvKDCfg")
   if config is None:
       raise RuntimeError("Cannot read configuration")
   if not kine.initial_kine(
       robot_type=config["TYPE"][0], dh=config["DH"][0],
       pnva=config["PNVA"][0], j67=config["BD"][0],
   ):
       raise RuntimeError("Cannot initialize kinematics")
   pose = kine.fk([0, -20, 0, 40, 0, 20, 0])

Controller connection
---------------------

The basic interface retains the official clear-set-send transaction order. Always
release an acquired connection. These examples do not issue motion commands.

.. code-block:: python

   from pymarvin import DCSS, Marvin_Robot

   robot = Marvin_Robot()
   if not robot.connect("192.168.1.10"):
       raise RuntimeError("Cannot connect")
   try:
       print(robot.subscribe(DCSS())["states"])
       # Batch commands: clear_set() -> setters -> send_cmd().
   finally:
       robot.release_robot()

Official showcases
------------------

The source distribution includes the official Marvin Python showcases in
``examples/``. They use the packaged ``pymarvin`` modules and cover controller
commands, planning, telemetry, offline kinematics and interference checks. Most connect to a real
robot and some issue motion or configuration commands; read
``examples/README.md`` and the selected script before running one. The
``offline_kinematics.py`` and ``offline_interference.py`` examples do not require hardware.

Offline interference check
--------------------------

The bundled interference model can be exercised without a controller. The model
definition files are installed with the package and the same interface is used by
``showcase_drag_interference.py`` when live joint values are available.

.. code-block:: python

   from pathlib import Path

   import pymarvin
   from pymarvin.fx_interference import Marvin_Interference

   config_dir = Path(pymarvin.__file__).with_name("interference_configs")
   checker = Marvin_Interference()
   checker.create()
   try:
       checker.init(
           str(config_dir / "CordDef_CCSM6Lite.Cord"),
           str(config_dir / "CalLinkDef.Links"),
           str(config_dir / "CalInputDef.Joints"),
           str(config_dir / "ConvexDef_CCSM6Lite.Convex"),
           str(config_dir / "InterfDef.Interf"),
       )
       checker.update_cord(14, [0.0] * 14)
       checker.update_convex()
       checker.calc_interf_distance()
       print(checker.get_min_span())
   finally:
       checker.destroy()

Owned trajectory points
-----------------------

Planning methods preserve tuples such as ``(data, pset)``. The handle is an owned
``PointSet`` rather than an integer address. A control call copies seven-dimensional
points into its own SDK representation.

.. code-block:: python

   from pymarvin import PointSet

   with PointSet(dimension=7) as points:
       points.append([0, 0, 0, 0, 0, 0, 0])
       print(points.to_list())

``destroy_point_set(pset)`` and ``pset.close()`` are both supported. Closing repeatedly
is safe; access after closing raises an exception. Raw addresses and ctypes pointer
handles are rejected.

