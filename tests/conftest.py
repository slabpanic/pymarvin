"""Shared synthetic robot geometry for offline numerical tests."""

import pytest
import pymarvin


@pytest.fixture
def kine():
    k = pymarvin.Marvin_Kine()
    k.log_switch(0)
    # Synthetic SRS geometry, for numerical tests only, not a robot calibration.
    k.robot_tag = 2
    dh = [
        [0, 0, 150, 0],
        [-90, 0, 0, 0],
        [90, 0, 250, 0],
        [-90, 0, 0, 0],
        [90, 0, 250, 0],
        [-90, 0, 0, 0],
        [90, 0, 100, 0],
        [0, 0, 50, 0],
    ]
    assert k.initial_kine(1007, dh, [[180, -180, 100, 100]] * 7, [[0, 0, 0]] * 4)
    return k
