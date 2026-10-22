"""Exercise the bundled interference SDK without connecting to a robot."""

from pathlib import Path

import pytest

from pymarvin import Marvin_Interference
from pymarvin.fx_interference import (
    FUNC_RET_ISInterference,
    FUNC_RET_NOInterference,
    FUNC_RET_OPERATION_FAILED,
    FUNC_RET_SUCCESS,
)

CONFIG_DIR = Path(__file__).parents[1] / "src/pymarvin/interference_configs"


def config_path(name):
    return str(CONFIG_DIR / name)


def test_interference_lifecycle_and_uninitialized_failures():
    checker = Marvin_Interference()
    assert (
        checker.init("missing", "missing", "missing", "missing", "missing")
        == FUNC_RET_OPERATION_FAILED
    )
    assert checker.update_cord(0, []) == FUNC_RET_OPERATION_FAILED
    assert checker.update_convex() == FUNC_RET_OPERATION_FAILED
    assert checker.calc_interf_distance() == FUNC_RET_OPERATION_FAILED
    assert checker.get_com() == (FUNC_RET_OPERATION_FAILED, [0.0, 0.0, 0.0])
    assert checker.get_cords_num() == (FUNC_RET_OPERATION_FAILED, 0)
    assert checker.get_mass(0) == (FUNC_RET_OPERATION_FAILED, [])
    assert checker.get_min_span() == (FUNC_RET_OPERATION_FAILED, 0.0)
    assert checker.get_interf_span(0) == (FUNC_RET_OPERATION_FAILED, 0.0)
    assert checker.on_is_interf([]) == FUNC_RET_OPERATION_FAILED
    checker.destroy()


def test_interference_configured_distance_queries():
    checker = Marvin_Interference()
    assert checker.create()
    assert (
        checker.init(
            config_path("CordDef_CCSM6Lite.Cord"),
            config_path("CalLinkDef.Links"),
            config_path("CalInputDef.Joints"),
            config_path("ConvexDef_CCSM6Lite.Convex"),
            config_path("InterfDef.Interf"),
        )
        == FUNC_RET_SUCCESS
    )
    assert checker.get_cords_num() == (FUNC_RET_SUCCESS, 17)
    status, masses = checker.get_mass(17)
    assert status == FUNC_RET_SUCCESS
    assert len(masses) == 17
    with pytest.raises(ValueError, match="coordinate count"):
        checker.get_mass(16)
    assert checker.update_cord(14, [0.0] * 14) == FUNC_RET_SUCCESS
    assert checker.update_convex() == FUNC_RET_SUCCESS
    assert checker.calc_interf_distance() == FUNC_RET_SUCCESS

    status, center = checker.get_com()
    assert status == FUNC_RET_SUCCESS
    assert len(center) == 3
    status, minimum = checker.get_min_span()
    assert status == FUNC_RET_SUCCESS
    assert minimum >= 0.0
    status, span = checker.get_interf_span(0)
    assert status == FUNC_RET_SUCCESS
    assert span >= 0.0
    assert checker.on_is_interf([10.0] * 15) in {
        FUNC_RET_ISInterference,
        FUNC_RET_NOInterference,
    }
    assert checker.update_cord(13, [0.0] * 13) == -2
    checker.destroy()
    checker.destroy()
