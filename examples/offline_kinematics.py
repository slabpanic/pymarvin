"""Run with uv run examples/offline_kinematics.py; no robot connection required."""

from pymarvin import Marvin_Kine, PointSet

kine = Marvin_Kine()
pose = kine.xyzabc_to_mat4x4([100, 200, 300, 10, 20, 30])
print("Matrix:", pose)
print("XYZABC:", kine.mat4x4_to_xyzabc(pose))

with PointSet(7) as points:
    points.append([0, 0, 0, 0, 0, 0, 0])
    print("Points:", points.to_list())
