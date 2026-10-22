"""Run the bundled interference SDK with the included CCSM6 Lite model."""

from pathlib import Path

import pymarvin
from pymarvin.fx_interference import (
    FUNC_RET_NOInterference,
    FUNC_RET_SUCCESS,
    Marvin_Interference,
)

CONFIG_DIR = Path(pymarvin.__file__).with_name("interference_configs")


def main():
    """Load the model, calculate distances, and print the result."""
    checker = Marvin_Interference()
    checker.create()
    try:
        status = checker.init(
            str(CONFIG_DIR / "CordDef_CCSM6Lite.Cord"),
            str(CONFIG_DIR / "CalLinkDef.Links"),
            str(CONFIG_DIR / "CalInputDef.Joints"),
            str(CONFIG_DIR / "ConvexDef_CCSM6Lite.Convex"),
            str(CONFIG_DIR / "InterfDef.Interf"),
        )
        if status != FUNC_RET_SUCCESS:
            raise RuntimeError(f"interference initialization failed: {status}")

        # The CCSM6 Lite joint definition contains fourteen controllable values.
        for action in (
            lambda: checker.update_cord(14, [0.0] * 14),
            checker.update_convex,
            checker.calc_interf_distance,
        ):
            status = action()
            if status != FUNC_RET_SUCCESS:
                raise RuntimeError(f"interference calculation failed: {status}")

        _, minimum = checker.get_min_span()
        state = checker.on_is_interf([10.0] * 15)
        print(f"minimum separation: {minimum:.3f} mm")
        print(
            "interference detected"
            if state != FUNC_RET_NOInterference
            else "no interference"
        )
    finally:
        checker.destroy()


if __name__ == "__main__":
    main()
