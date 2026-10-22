"""Tianji Marvin control, kinematics and interference bindings.

The distribution is named ``pymarvin``; import it as ``pymarvin``.
Importing the package never connects to a robot.
"""

from importlib.metadata import version

from . import fx_interference, fx_kine, fx_robot
from ._kinematics import PointSet
from .fx_kine import (
    ArmsSynchronousPlanningParams,
    FX_InvKineSolvePara,
    FX_Jacobi,
    Marvin_Kine,
    Matrix4,
    Matrix8,
    Vect7,
)
from .fx_robot import (
    DCSS,
    FTCmd,
    RT_IN,
    RT_OUT,
    StateCtr,
    Concise_Marvin_Robot,
    Marvin_Robot,
)
from .fx_interference import Marvin_Interference
from ._validation import verify_layouts

__version__ = version("pymarvin")
verify_layouts()

__all__ = [
    "Marvin_Robot",
    "Concise_Marvin_Robot",
    "Marvin_Kine",
    "Marvin_Interference",
    "PointSet",
    "DCSS",
    "RT_IN",
    "RT_OUT",
    "StateCtr",
    "FTCmd",
    "FX_InvKineSolvePara",
    "FX_Jacobi",
    "ArmsSynchronousPlanningParams",
    "Vect7",
    "Matrix4",
    "Matrix8",
    "fx_robot",
    "fx_kine",
    "fx_interference",
    "__version__",
]
