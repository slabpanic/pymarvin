import ctypes as ct
import math
from importlib.machinery import EXTENSION_SUFFIXES
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import pymarvin
from pymarvin import _control, _interference, _kinematics

ROOT = Path(__file__).resolve().parents[1]


def assert_matrix_close(actual, expected, abs=1e-9):
    assert len(actual) == len(expected)
    for a, b in zip(actual, expected):
        assert a == pytest.approx(b, abs=abs)


def test_distribution_and_native_modules():
    assert (
        pymarvin.__version__
        == re.search(
            r'(?m)^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text()
        )[1]
    )
    assert pymarvin.Marvin_Robot().robot is _control
    assert pymarvin.Concise_Marvin_Robot().robot is _control
    assert pymarvin.Marvin_Kine().kine is _kinematics
    assert pymarvin.Marvin_Interference
    assert any(_control.__file__.endswith(suffix) for suffix in EXTENSION_SUFFIXES)
    assert any(_interference.__file__.endswith(suffix) for suffix in EXTENSION_SUFFIXES)


@pytest.mark.parametrize(
    "sdk,header,module",
    [
        ("control", "MarvinSDK.h", _control),
        ("kinematics", "FxRobot.h", _kinematics),
    ],
)
def test_public_sdk_functions_are_bound(sdk, header, module):
    source = (ROOT / "src/sdk" / sdk / header).read_text(encoding="utf-8")
    source = re.sub(r"//[^\n]*|/\*.*?\*/", "", source, flags=re.S)
    names = set(
        re.findall(
            r"(?:FX_DLL_EXPORT\s+)?(?:FX_\w+|bool|int|long|void|double)\s+[*\s]*(\w+)\s*\([^;{}]*\)\s*;",
            source,
        )
    )
    if sdk == "control":
        # Control trajectories use the owning kinematics PointSet representation.
        names = {name for name in names if not name.startswith("FX_CPointSet_")}
    assert len(names) >= (100 if sdk == "control" else 30)
    for name in sorted(names):
        assert callable(getattr(module, name)), name


def test_records_match_cpp_layout():
    from pymarvin._validation import verify_layouts

    verify_layouts()
    assert ct.sizeof(pymarvin.DCSS) == _control._layouts["DCSS"]["__size__"]
    assert pymarvin.DCSS._pack_ == 4
    for cls in [
        pymarvin.FX_InvKineSolvePara,
        pymarvin.FX_Jacobi,
        pymarvin.ArmsSynchronousPlanningParams,
    ]:
        assert ct.sizeof(cls) == _kinematics._layouts[cls.__name__]["__size__"]


@pytest.mark.parametrize(
    "xyzabc",
    [[100, 200, 300, 0, 0, 0], [1, 2, 3, 10, 20, 30], [-3, 0, 7, -10, 35, -50]],
)
def test_pose_roundtrip(xyzabc):
    k = pymarvin.Marvin_Kine()
    pose = k.xyzabc_to_mat4x4(xyzabc)
    assert pose[3] == [0, 0, 0, 1]
    assert k.mat4x4_to_xyzabc(pose) == pytest.approx(xyzabc, abs=1e-9)


def test_known_rotation():
    k = pymarvin.Marvin_Kine()
    assert_matrix_close(
        k.xyzabc_to_mat4x4([0, 0, 0, 0, 0, 90]),
        [[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
    )
    assert k.calculate_end_xyzabc(
        [1, 2, 3, 0, 0, 0], [4, 5, 6], 11, [0, 0, 0]
    ) == pytest.approx([5, 7, 9, 0, 0, 0])


def test_fk_ik_roundtrip(kine):
    joints = [10, -20, 30, 40, 50, 60, 70]
    pose = kine.fk(joints)
    assert_matrix_close(kine.fk_nsp(joints)[0], pose)
    solve = pymarvin.FX_InvKineSolvePara()
    solve.set_input_ik_target_tcp(kine.mat4x4_to_mat1x16(pose))
    solve.set_input_ik_ref_joint(joints)
    assert kine.ik(solve) is solve
    assert solve.get_output_ret_joint() == pytest.approx(joints, abs=1e-6)
    assert_matrix_close(kine.fk(solve.get_output_ret_joint()), pose, abs=1e-5)


def test_jacobian_matches_fk_derivative(kine):
    joints = [10, -20, 30, 40, 50, 60, 70]
    jac = kine.joints2JacobMatrix(joints)
    pose = kine.fk(joints)
    delta = 1e-5
    for j in range(7):
        moved = joints[:]
        moved[j] += delta
        end = kine.fk(moved)
        for axis in range(3):
            derivative = (end[axis][3] - pose[axis][3]) / math.radians(delta) / 1000
            assert derivative == pytest.approx(jac[axis][j], abs=1e-6)


def test_tool_and_user_frame(kine):
    joints = [10, -20, 30, 40, 50, 60, 70]
    pose = kine.fk(joints)
    assert kine.set_tool_kine(kine.xyzabc_to_mat4x4([0, 0, 20, 0, 0, 0]))
    end = kine.fk(joints)
    for axis in range(3):
        assert end[axis][3] == pytest.approx(pose[axis][3] + pose[axis][2] * 20)
    assert kine.remove_tool_kine()
    assert_matrix_close(kine.fk(joints), pose)
    assert kine.set_user_frame_kine(kine.xyzabc_to_mat4x4([10, 0, 0, 0, 0, 0]))
    assert kine.remove_user_frame_kine()
    assert_matrix_close(kine.fk(joints), pose)


def test_pointset_ownership_and_bounds():
    k = pymarvin.Marvin_Kine()
    points = k.create_point_set(7)
    assert isinstance(points, pymarvin.PointSet)
    assert points.append([1, 2, 3, 4, 5, 6, 7])
    assert len(points) == 1
    assert k.get_point_set_data(points, 7) == [[1, 2, 3, 4, 5, 6, 7]]
    with pytest.raises(ValueError):
        k.get_point_set_data(points, 6)
    with pytest.raises(IndexError):
        _ = points[1]
    with pytest.raises(ValueError):
        points.append([1, 2])
    k.destroy_point_set(points)
    k.destroy_point_set(points)
    assert points.closed
    with pytest.raises(RuntimeError):
        points.to_list()
    with pymarvin.PointSet(7) as p:
        p.append([0] * 7)
    assert p.closed


def test_unsafe_buffers_and_addresses_rejected():
    with pytest.raises(ValueError):
        _kinematics.FX_XYZABC2Matrix4DEG((ct.c_double * 5)(), ((ct.c_double * 4) * 4)())
    with pytest.raises(TypeError):
        _control.OnSetPlnCart_A(1234)
    with pytest.raises(ValueError):
        _control.OnSetPlnCart_A(pymarvin.PointSet(6))
    p = pymarvin.PointSet(7)
    p.close()
    with pytest.raises(RuntimeError):
        _control.OnSetPlnCart_A(p)
    with pytest.raises(ValueError):
        pymarvin.PointSet(41)
    with pytest.raises(ValueError):
        _kinematics.FX_Robot_Init_Type(-1, 1007)
    with pytest.raises(RuntimeError):
        _kinematics.FX_Robot_Kine_FK(9, (ct.c_double * 7)(), ((ct.c_double * 4) * 4)())


def test_native_channel_and_gather_bounds():
    with pytest.raises(ValueError):
        _control.SetChData(b"A", (ct.c_ubyte * 256)(), 257, 1)
    with pytest.raises(ValueError):
        _control.OnStartGather(36, (ct.c_long * 35)(), 1000)
    with pytest.raises(ValueError):
        _control.OnSetJointCmdPos_A((ct.c_double * 6)())


UPGRADED_CONTROL_SYMBOLS = {
    "CheckSDKTypeCompat",
    "FTArmControl",
    "FX_OnSetVelEstStep",
    "OnGetRobotName",
    "OnReset6DofForceSensor",
    "OnSetReboot",
    "OnSetStopRunning",
    "OnSetSystemTime",
    "OnSetUserSpcfData",
    "OnSetUserSpcfData_A",
    "OnSetUserSpcfData_B",
}


def test_new_control_sdk_has_all_previously_missing_implementations():
    source = (ROOT / "src/sdk/control/MarvinSDK.cpp").read_text(encoding="utf-8")
    for name in UPGRADED_CONTROL_SYMBOLS:
        assert re.search(r"\b" + name + r"\s*\([^)]*\)\s*\{", source), name
        assert callable(getattr(_control, name))


def test_native_control_version_and_type_compatibility():
    assert pymarvin.Marvin_Robot().SDK_version() == 100343014
    assert pymarvin.Concise_Marvin_Robot().SDK_version() == 100343014
    order = 0 if sys.byteorder == "little" else 1
    assert pymarvin.Marvin_Robot().check_sdk_type_compat() == (
        1 if order == 0 else 2,
        order,
    )
    assert ct.sizeof(pymarvin.FTCmd) == _control._layouts["FTCmd"]["__size__"] == 112


@pytest.mark.parametrize("cls", [pymarvin.Marvin_Robot, pymarvin.Concise_Marvin_Robot])
@pytest.mark.parametrize("arm", ["A", "B"])
def test_restored_force_command_dispatch(cls, arm):
    robot = cls()
    command = pymarvin.FTCmd()
    command.fxDir[1], command.K, command.F = 1, 2000, 15
    seen = []

    def force(arm_arg, value):
        assert value is command
        assert (value.fxDir[1], value.K, value.F) == (1, 2000, 15)
        seen.append(arm_arg)
        return True

    robot.robot = SimpleNamespace(FTArmControl=force)
    assert robot.ft_arm_control(arm, command) == True
    assert seen == [arm.encode("ascii")]


@pytest.mark.parametrize("cls", [pymarvin.Marvin_Robot, pymarvin.Concise_Marvin_Robot])
@pytest.mark.parametrize("arm,suffix", [("A", "_A"), ("B", "_B"), ("AB", "")])
def test_restored_user_data_dispatch(cls, arm, suffix):
    robot = cls()
    seen = []
    robot.robot = SimpleNamespace(
        **{
            "OnSetUserSpcfData" + suffix: lambda category: seen.append(category.value)
            or True
        }
    )
    assert robot.set_user_specified_data(arm, 4) == True
    assert seen == [4]


@pytest.mark.parametrize("cls", [pymarvin.Marvin_Robot, pymarvin.Concise_Marvin_Robot])
def test_restored_name_output_and_system_command_dispatch(cls):
    robot = cls()
    seen = []

    def name_output(buffer):
        assert ct.sizeof(buffer) == 512
        buffer.value = "Marvin测试".encode("utf-8")
        return True

    def record(name):
        def call(*args):
            seen.append((name, [getattr(arg, "value", arg) for arg in args]))
            return True

        return call

    robot.robot = SimpleNamespace(
        OnGetRobotName=name_output,
        FX_OnSetVelEstStep=record("step"),
        OnReset6DofForceSensor=record("reset"),
        OnSetSystemTime=record("time"),
        OnSetReboot=record("reboot"),
        OnSetStopRunning=record("stop"),
    )
    assert robot.get_robot_name() == "Marvin测试"
    robot.robot.OnGetRobotName = lambda buffer: False
    assert robot.get_robot_name() is None
    if cls == pymarvin.Marvin_Robot:
        assert robot.set_PD_vel_est_step("A", 5) is True
    else:
        robot.set_vel_est_step("A", 5)
    assert robot.reset_6dof_force_sensor("B") is True
    assert robot.set_system_time(2026, 10, 22, 12, 30, 45) is True
    assert robot.reboot() is True
    assert robot.stop_running("AB") is None  # Official wrapper returns None.
    assert seen == [
        ("step", [b"A", 5]),
        ("reset", [b"B"]),
        ("time", [2026, 10, 22, 12, 30, 45]),
        ("reboot", []),
        ("stop", [b"AB"]),
    ]


def test_new_native_output_and_value_argument_bounds():
    # Rejected before entering any vendor function or touching a controller.
    with pytest.raises(ValueError):
        _control.OnGetRobotName(ct.create_string_buffer(8))
    with pytest.raises((TypeError, BufferError)):
        _control.OnGetRobotName(b"immutable")
    with pytest.raises(ValueError):
        _control.FTArmControl(b"A", (ct.c_ubyte * 1)())
    # Never enter the SDK with an uninitialized singleton (it dereferences NULL).
    for method, args in [
        (_control.FTArmControl, (b"A", pymarvin.FTCmd())),
        (_control.FX_OnSetVelEstStep, (b"A", 5)),
        (_control.OnGetRobotName, (ct.create_string_buffer(512),)),
        (_control.OnReset6DofForceSensor, (b"A",)),
        (_control.OnSetReboot, ()),
        (_control.OnSetStopRunning, (b"AB",)),
        (_control.OnSetSystemTime, (2026, 10, 22, 0, 0, 0)),
        (_control.OnSetUserSpcfData, (0,)),
        (_control.OnSetUserSpcfData_A, (0,)),
        (_control.OnSetUserSpcfData_B, (0,)),
    ]:
        with pytest.raises(RuntimeError, match="call connect"):
            method(*args)
    assert _control.OnRelease() is True
    assert _control.OnRelease() is True


def test_control_buffers_and_64bit_output():
    robot = pymarvin.Marvin_Robot()

    def get_int(name, out):
        assert len(name) == 30
        assert isinstance(out._obj, ct.c_long)
        out._obj.value = 2**34 if ct.sizeof(ct.c_long) == 8 else 2**30
        return 1

    robot.robot = SimpleNamespace(OnGetIntPara=get_int)
    assert robot.get_param("int", "R.A0.Type") == (
        1,
        (2**34 if ct.sizeof(ct.c_long) == 8 else 2**30),
    )
    for cls in [pymarvin.Marvin_Robot, pymarvin.Concise_Marvin_Robot]:
        r = cls()
        seen = []

        def gather(count, ids, records):
            assert len(ids) == 35
            seen.append(list(ids)[:2])
            return True

        r.robot = SimpleNamespace(OnStartGather=gather, StartCollectData=gather)
        method = (
            r.collect_data if cls == pymarvin.Marvin_Robot else r.start_collect_data
        )
        assert method(2, [10, 20], 1000)
        assert seen == [[10, 20]]


@pytest.mark.parametrize("arm", ["A", "B"])
def test_control_command_dispatch(arm):
    robot = pymarvin.Marvin_Robot()
    seen = []

    def command(joints):
        seen.append(list(joints))
        return True

    robot.robot = SimpleNamespace(**{f"OnSetJointCmdPos_{arm}": command})
    assert robot.set_joint_cmd_pose(arm, [1, 2, 3, 4, 5, 6, 7])
    assert seen == [[1, 2, 3, 4, 5, 6, 7]]


def test_strict_ipv4_validation():
    for cls in [pymarvin.Marvin_Robot, pymarvin.Concise_Marvin_Robot]:
        r = cls()
        assert r._convert_ip("192.168.1.10") == (192, 168, 1, 10)
        with pytest.raises(ValueError):
            r._convert_ip("256.1.2.3")


def test_subscription_record_conversion():
    record = pymarvin.DCSS()
    record.m_State[1].m_ERRCode = 13
    record.m_Out[0].m_FB_Joint_Pos[3] = 45.5
    record.m_Out[1].m_FB_Joint_PosE[4] = 21.0
    result = pymarvin.fx_robot.structure2dict(record)
    assert result["states"][1]["err_code"] == 13
    assert result["outputs"][0]["fb_joint_pos"][3] == 45.5
    assert result["outputs"][1]["fb_joint_posE"][4] == 21.0


def test_linear_velocity_matches_fk_difference(kine):
    joints = [10, -20, 30, 40, 50, 60, 70]
    rates = [1, -2, 3, -4, 5, -6, 7]
    assert kine.cal_ee_linear_vel(joints, [0] * 7) == 0.0
    dt = 1e-6
    before = kine.fk(joints)
    after = kine.fk([q + v * dt for q, v in zip(joints, rates)])
    expected = math.sqrt(
        sum(((after[r][3] - before[r][3]) / dt) ** 2 for r in range(3))
    )
    assert kine.cal_ee_linear_vel(joints, rates) == pytest.approx(expected, abs=1e-4)


def test_pointset_dimensions_and_exception_cleanup():
    k = pymarvin.Marvin_Kine()
    p = k.create_point_set()
    assert p.dimension == 6
    assert p.append([1, 2, 3, 4, 5, 6])
    assert k.get_point_set_data(p) == [[1, 2, 3, 4, 5, 6]]
    with pytest.raises(LookupError):
        with pymarvin.PointSet(7) as failing:
            raise LookupError("caller exception")
    assert failing.closed


def test_native_joint_planning_and_control_copy(kine):
    start = [10, -20, 30, 40, 50, 60, 70]
    end = [11, -21, 31, 41, 51, 61, 71]
    with pymarvin.PointSet(7) as points:
        assert _kinematics.FX_Robot_PLN_MOVJ(
            kine.robot_tag,
            (ct.c_double * 7)(*start),
            (ct.c_double * 7)(*end),
            0.1,
            0.1,
            100,
            points,
        )
        assert len(points) > 1
        assert points[0] == pytest.approx(start)
        assert points[len(points) - 1] == pytest.approx(end)
    # Copy to the control SDK representation, then reject the uninitialized SDK.
    with pymarvin.PointSet(7) as short:
        short.append(start)
        with pytest.raises(RuntimeError, match="call connect"):
            _control.OnSetPlnCart_A(short)
        assert short.to_list() == [start]


def test_load_config_native_output_buffers(tmp_path):
    lines = []
    for arm in range(2):
        lines.append(f"1007,0,0,-9.81,\n")
        for joint in range(7):
            values = [
                joint,
                0,
                100 + joint,
                0,
                -180,
                180,
                100,
                200,
                1 + arm,
                0,
                0,
                0,
                1,
                1,
                1,
                0,
                0,
                0,
            ]
            lines.append(",".join(str(x) for x in values) + ",\n")
        lines.append("0,0,50,0,\n")
        lines.extend(["0,0,0,\n"] * 4)
    path = tmp_path / "synthetic.MvKDCfg"
    path.write_text("".join(lines))
    k = pymarvin.Marvin_Kine()
    result = k.load_config(1, str(path))
    assert k.robot_tag == 1
    assert result["TYPE"] == [1007, 1007]
    assert result["GRV"][0] == [0, 0, -9.81]
    assert result["DH"][1][6] == [6, 0, 106, 0]
    assert result["PNVA"][0][0] == [180, -180, 100, 200]
    assert result["Mass"][1] == [2] * 7
    path.write_text("malformed config")
    assert k.load_config(0, str(path)) is None
