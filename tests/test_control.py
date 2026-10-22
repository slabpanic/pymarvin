"""Exercise controller marshaling with an isolated recording backend, never hardware."""

import ctypes as ct
from pathlib import Path

import pytest

from pymarvin import Concise_Marvin_Robot, DCSS, Marvin_Robot, PointSet
from pymarvin import fx_robot

V7 = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
V6 = V7[:6]
V10 = list(range(10))
P = object()


def value(arg):
    if hasattr(arg, "_obj"):
        return value(arg._obj)
    if hasattr(arg, "value"):
        return arg.value
    if isinstance(arg, ct.Array):
        return [value(item) for item in arg]
    return arg


class Backend:
    """Record wire-boundary values and provide bounded output buffers."""

    def __init__(self, result=True, error=False):
        self.result, self.error, self.calls = result, error, []
        self.state = DCSS()
        self.servo = {"A": [0] * 7, "B": [0] * 7}

    def __getattr__(self, name):
        def call(*args):
            self.calls.append((name, [value(arg) for arg in args]))
            if self.error:
                raise RuntimeError("simulated controller failure")
            if name == "OnGetBuf":
                ct.memmove(
                    ct.addressof(args[0]._obj),
                    ct.addressof(self.state),
                    ct.sizeof(DCSS),
                )
            if name.startswith("OnGetServoErr_"):
                args[0]._obj[:] = self.servo[name[-1]]
            if name in ("OnGetIntPara", "OnGetFloatPara"):
                args[-1]._obj.value = (
                    (2**34 if ct.sizeof(ct.c_long) == 8 else 2**30)
                    if name == "OnGetIntPara"
                    else 1.25
                )
                return 7
            if name in ("OnGetChDataA", "OnGetChDataB", "GetChData"):
                args[-2][0], args[-2][1] = 0xAB, 0xCD
                args[-1]._obj.value = 3
                return 2
            if name == "OnSaveGatherData":
                Path(value(args[0]).decode()).write_text("header\na 1$b 2$c 3$d 4$\n")
            if name == "OnRecvFile":
                Path(value(args[0]).decode()).write_text(
                    ",".join(["1"] * 16) + "\n" + ",".join(["0"] * 16) + "\n"
                )
            return self.result

        return call


# Each case states the expected native API and its serialized arguments. Test
# data is independent of the generator and checks official facade conventions.
BASIC = [
    ("soft_stop", [], "OnEMG_{arm}", []),
    ("servo_reset", [2], "OnServoReset_{arm}", [2]),
    ("clear_error", [], "OnClearErr_{arm}", []),
    ("set_state", [1], "OnSetTargetState_{arm}", [1]),
    ("set_impedance_type", [2], "OnSetImpType_{arm}", [2]),
    ("set_vel_acc", [10, 20], "OnSetJointLmt_{arm}", [10, 20]),
    ("set_tool", [V6, V10], "OnSetTool_{arm}", [V6, V10]),
    ("set_joint_kd_params", [V7, V7], "OnSetJointKD_{arm}", [V7, V7]),
    ("set_cart_kd_params", [V7, V7], "OnSetCartKD_{arm}", [V7, V7, 2]),
    (
        "set_force_control_params",
        [0, V6, V7, 10.0],
        "OnSetForceCtrPara_{arm}",
        [0, V6, V7, 10.0],
    ),
    ("set_EefCart_control_params", [1, V7], "OnSetEefRot_{arm}", [1, V7]),
    ("set_joint_cmd_pose", [V7], "OnSetJointCmdPos_{arm}", [V7]),
    ("set_force_cmd", [12.5], "OnSetForceCmd_{arm}", [12.5]),
    ("set_pvt_id", [9], "OnSetPVT_{arm}", [9]),
    ("send_pvt_file", ["test.pvt", 9], "OnSendPVT_{arm}", [b"test.pvt", 9]),
    ("set_drag_space", [1], "OnSetDragSpace_{arm}", [1]),
    ("stopRunPln_joint", [], "OnStopPlnJoint_{arm}", []),
    ("setPln_joint", [V7, V7, 0.2, 0.3], "OnSetPlnJoint_{arm}", [V7, V7, 0.2, 0.3]),
    ("setPln_Cart", [P], "OnSetPlnCart_{arm}", [P]),
    ("clear_485_cache", [], "OnClearChData{arm}", []),
]
CONCISE = [
    ("soft_stop", [], "EStop", []),
    ("servo_reset", [2], "ServoReset", [2]),
    ("set_position_state", [10, 20], "SetJointMode", [10, 20]),
    (
        "set_imp_joint_state",
        [10, 20, V7, [0.2] * 7],
        "SetImpJointMode",
        [10, 20, V7, [0.2] * 7],
    ),
    (
        "set_imp_cart_state",
        [10, 20, V7, [0.2] * 7, 1, V7],
        "SetImpCartMode",
        [10, 20, V7, [0.2] * 7, 1, V7],
    ),
    ("set_imp_force_state", [V6, 10.0], "SetImpForceMode", [V6, 10.0]),
    ("set_force_cmd", [12.5], "SetForceCmd", [12.5]),
    ("set_joint_position_cmd", [V7], "SetJointPostionCmd", [V7]),
    ("run_pln_joint", [V7, V7, 0.2, 0.3], "RunPlnJoint", [V7, V7, 0.2, 0.3]),
    ("run_pln_cart", [P], "RunPlnCart", [P]),
    ("stop_pln", [], "StopPln", []),
    ("send_pvt", ["test.pvt", 9], "SendPVT", [b"test.pvt", 9]),
    ("run_pvt", [9], "RunPVT", [9]),
    ("set_joint_drag", [], "SetJointDrag", []),
    ("set_cart_drag", ["R"], "SetCartDrag", [b"R"]),
    ("exit_drag", [], "ExitDrag", []),
    ("set_tool", [V6, V10], "SetTool", [V6, V10]),
    ("disable", [], "Disable", []),
    ("clear_ch_data", [], "ClearChData", []),
]
CASES = [(Marvin_Robot, *case) for case in BASIC] + [
    (Concise_Marvin_Robot, *case) for case in CONCISE
]


@pytest.mark.parametrize("cls,method,args,native,expected", CASES)
@pytest.mark.parametrize("arm", ["A", "B"])
def test_arm_command_marshaling(cls, method, args, native, expected, arm):
    robot, backend = cls(), Backend()
    robot.robot = backend
    with PointSet(7) as points:
        actual_args = [points if x is P else x for x in args]
        actual_expected = [points if x is P else x for x in expected]
        result = getattr(robot, method)(arm, *actual_args)
        if cls is Concise_Marvin_Robot:
            actual_expected.insert(0, arm.encode())
        assert backend.calls == [(native.format(arm=arm), actual_expected)]
        assert result is None or result == True


@pytest.mark.parametrize("cls,method,args,native,expected", CASES)
def test_controller_failures_do_not_report_success(cls, method, args, native, expected):
    robot, backend = cls(), Backend(error=True)
    robot.robot = backend
    with PointSet(7) as points:
        try:
            result = getattr(robot, method)(
                "A", *[points if x is P else x for x in args]
            )
        except RuntimeError as exc:
            assert "simulated controller failure" in str(
                exc
            ) or "setPln_Cart failed" in str(exc)
        else:
            assert not result
        assert backend.calls[0][0] == native.format(arm="A")


@pytest.mark.parametrize("cls", [Marvin_Robot, Concise_Marvin_Robot])
def test_non_arm_commands_and_parameter_outputs(cls, tmp_path, monkeypatch):
    robot, backend = cls(), Backend()
    robot.robot = backend
    assert robot.connect("192.168.1.10")
    assert backend.calls[-1] == (
        ("OnLinkTo", [192, 168, 1, 10])
        if cls is Marvin_Robot
        else ("Connect", [192, 168, 1, 10, 0])
    )
    assert robot.update_SDK("update.bin")
    assert backend.calls[-1] == ("OnUpdateSystem", [b"update.bin"])
    assert robot.download_sdk_log("logs")
    assert backend.calls[-1] == ("OnDownloadLog", [b"logs"])
    for kind, expected in [
        ("int", (2**34 if ct.sizeof(ct.c_long) == 8 else 2**30)),
        ("float", 1.25),
    ]:
        assert robot.get_param(kind, "R.A0.Type") == (7, expected)
        assert robot.set_param(kind, "R.A0.Type", 3.5)
    assert robot.get_param("invalid", "x") is None
    assert robot.set_param("invalid", "x", 0) is None
    assert robot.get_param("int", "x" * 31) is None
    assert robot.set_param("int", "x" * 31, 1) is None
    assert robot.save_para_file()
    assert robot.release_robot()
    assert robot.setPln_joint_AB(V7, V7, V7, V7, 0.1, 0.2)
    assert backend.calls[-1] == ("CoRunPlnJoint", [V7, V7, V7, V7, 0.1, 0.2])
    assert robot.stopPln_AB()
    with PointSet(7) as a, PointSet(7) as b:
        assert robot.setPln_Cart_AB(a, b)
        assert backend.calls[-1] == ("CoRunPlnCart", [a, b])
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(fx_robot.time, "sleep", lambda _: None)
    assert robot.get_tool_info() == ("line1", [1.0] * 16)
    csv_method = (
        robot.save_collected_data_as_csv_to_path
        if cls is Marvin_Robot
        else robot.save_gather_data_as_csv_to_path
    )
    assert csv_method("result.csv")
    assert Path("result.csv").read_text().strip() == "3,4"
    assert not Path("tmp.txt").exists()
    assert csv_method(str(tmp_path)) is False
    if cls is Marvin_Robot:
        assert (
            robot.clear_set() and robot.send_cmd() and robot.send_cmd_wait_response(20)
        )
        assert robot.stop_collect_data()
        assert robot.save_collected_data_to_path("data.txt")
        for flag in ["0", "1", "invalid"]:
            robot.log_switch(flag)
            robot.local_log_switch(flag)
        Path("config").touch()
        assert robot.pln_init("config")
        with pytest.raises(ValueError):
            robot.pln_init("missing")
        robot.soft_stop("AB")
        assert backend.calls[-1][0] == "OnEMG_AB"
    else:
        assert robot.start_collect_data(-1, [1], 1)
        assert backend.calls[-1][1][0] == 1
        assert backend.calls[-1][1][-1] == 1000
        assert robot.start_collect_data(99, [1], 9999999)
        assert backend.calls[-1][1][0] == 35
        assert backend.calls[-1][1][-1] == 1000000
        assert robot.stop_collect_data() and robot.save_gather_data("data.txt")
        assert robot.pln_init("config")
        assert robot.check_arms_error() and robot.check_servo_error()
        assert robot.check_error_and_clear() is False
        backend.result = False
        assert robot.check_error_and_clear() is False


@pytest.mark.parametrize("cls", [Marvin_Robot, Concise_Marvin_Robot])
@pytest.mark.parametrize("arm", ["A", "B"])
def test_telemetry_and_communication_outputs(cls, arm):
    robot, backend = cls(), Backend()
    robot.robot = backend
    backend.state.m_State[1].m_ERRCode = 13
    assert robot.subscribe(DCSS())["states"][1]["err_code"] == 13
    backend.servo[arm][2] = 0x2310
    assert "joint 3" in robot.get_servo_error_code(arm, "EN")
    if cls is Marvin_Robot:
        assert robot.set_485_data(arm, b"\xab\xcd", 2, 1) == (True, True)
        sent = backend.calls[-1][1]
        assert sent[0][:2] == [0xAB, 0xCD] and sent[1:] == [2, 1]
        length, text = robot.get_485_data(arm, 1)
        assert length == 2 and text.startswith("AB CD ")
    else:
        assert robot.set_ch_data(arm, b"\xab\xcd", 2, 1)
        assert robot.get_ch_data(arm, 1) == (2, "AB CD")
        backend.result = False
        assert robot.subscribe(DCSS()) is None
        assert robot.subscribe(None) is None
        backend.error = True
        assert robot.subscribe(DCSS()) is None
        assert robot.get_ch_data(arm, 1) == (0, b"")
        assert robot.set_ch_data(arm, b"a", 1, 1) == -1


@pytest.mark.parametrize(
    "state,servo,expected",
    [
        ((100, 0), (0, 0), "A"),
        ((0, 100), (0, 0), "B"),
        ((0, 0), (1, 0), "A"),
        ((0, 0), (0, 1), "B"),
        ((0, 0), (0, 0), None),
    ],
)
def test_basic_error_clear_priority(state, servo, expected):
    robot, backend = Marvin_Robot(), Backend()
    robot.robot = backend
    for i, arm in enumerate(["A", "B"]):
        backend.state.m_State[i].m_CurState = state[i]
        backend.servo[arm][0] = servo[i]
    robot.check_error_and_clear(DCSS())
    cleared = [name for name, args in backend.calls if name.startswith("OnClearErr_")]
    assert cleared == ([] if expected is None else ["OnClearErr_" + expected])


@pytest.mark.parametrize(
    "method,args",
    [
        ("servo_reset", ["AB", 0]),
        ("servo_reset", ["A", 7]),
        ("set_position_state", ["AB", 1, 1]),
        ("set_imp_joint_state", ["A", 1, 1, [], []]),
        ("set_imp_cart_state", ["X", 1, 1, V7, V7, 0, V7]),
        ("set_imp_cart_state", ["A", 1, 1, [], V7, 0, V7]),
        ("set_imp_cart_state", ["A", 1, 1, V7, V7, 4, V7]),
        ("set_imp_cart_state", ["A", 1, 1, V7, V7, 0, []]),
        ("set_imp_force_state", ["X", V6, 1.0]),
        ("set_imp_force_state", ["A", [], 1.0]),
        ("set_imp_force_state", ["A", V6, -1.0]),
        ("set_force_cmd", ["X", 1.0]),
        ("set_joint_position_cmd", ["X", V7]),
        ("set_joint_position_cmd", ["A", []]),
        ("pln_init", [""]),
        ("save_gather_data", [""]),
        ("run_pln_joint", ["X", V7, V7, 0.1, 0.2]),
        ("run_pln_joint", ["A", [], V7, 0.1, 0.2]),
        ("stop_pln", ["X"]),
        ("send_pvt", ["X", "a", 0]),
        ("send_pvt", ["A", "a", 100]),
        ("send_pvt", ["A", "", 0]),
        ("run_pvt", ["X", 0]),
        ("run_pvt", ["A", 100]),
        ("set_joint_drag", ["X"]),
        ("set_cart_drag", ["X", "X"]),
        ("set_cart_drag", ["A", "bad"]),
        ("exit_drag", ["X"]),
        ("set_tool", ["X", V6, V10]),
        ("set_tool", ["A", [], V10]),
        ("set_tool", ["A", V6, []]),
        ("disable", ["X"]),
        ("clear_ch_data", ["X"]),
        ("get_ch_data", ["X", 1]),
        ("set_ch_data", ["X", b"a", 1, 1]),
        ("set_ch_data", ["A", b"a", 257, 1]),
        ("set_ch_data", ["A", b"a", 1, 4]),
    ],
)
def test_concise_invalid_inputs_never_reach_backend(method, args):
    robot, backend = Concise_Marvin_Robot(), Backend()
    robot.robot = backend
    with pytest.raises(ValueError):
        getattr(robot, method)(*args)
    assert backend.calls == []


def test_percentage_and_impedance_clamping():
    robot, backend = Concise_Marvin_Robot(), Backend()
    robot.robot = backend
    robot.set_position_state("A", -1, 101)
    assert backend.calls[-1][1] == [b"A", 10, 100]
    robot.set_position_state("B", 101, -1)
    assert backend.calls[-1][1] == [b"B", 100, 10]
    robot.set_imp_joint_state("A", -1, 101, [-1] * 7, [-1, 2, 0.2, 0.2, 0.2, 0.2, 0.2])
    assert backend.calls[-1][1] == [
        b"A",
        10,
        100,
        [0.0] * 7,
        [0.0, 1.0, 0.2, 0.2, 0.2, 0.2, 0.2],
    ]
    robot.set_imp_joint_state("B", 101, -1, V7, [0.2] * 7)
    assert backend.calls[-1][1][1:3] == [100, 10]
    robot.set_imp_cart_state("A", -1, 101, V7, [0.2] * 7, 0, V7)
    assert backend.calls[-1][1][1:3] == [0, 100]
    robot.run_pln_joint("A", V7, V7, -1.0, 2.0)
    assert backend.calls[-1][1][-2:] == [0.0, 1.0]


@pytest.mark.parametrize("cls", [Marvin_Robot, Concise_Marvin_Robot])
@pytest.mark.parametrize(
    "method,args,expected",
    [
        ("ft_arm_control", ["A", None], 0),
        ("set_user_specified_data", ["A", 1], 0),
        ("get_robot_name", [], None),
        ("reset_6dof_force_sensor", ["A"], False),
        ("set_system_time", [2026, 10, 22, 12, 0, 0], False),
        ("reboot", [], False),
        ("stop_running", ["AB"], None),
    ],
)
def test_system_command_failures(cls, method, args, expected):
    r = cls()
    r.robot = Backend(error=True)
    assert getattr(r, method)(*args) == expected


@pytest.mark.parametrize(
    "method,args,expected",
    [
        ("log_switch", ["1"], None),
        ("local_log_switch", ["0"], None),
        ("get_servo_error_code", ["A"], None),
        ("get_485_data", ["B", 1], None),
        ("set_PD_vel_est_step", ["A", 1], False),
        ("set_user_specified_data", ["X", 1], 0),
        ("set_485_data", ["A", b"x" * 257, 257, 1], None),
        ("set_485_data", ["A", "ordinary text", 10, 1], (False, False)),
        *[
            ("setPln_joint", args, None)
            for args in [
                ["X", V7, V7, 0.1, 0.1],
                ["A", [], V7, 0.1, 0.1],
                ["A", V7, [], 0.1, 0.1],
                ["A", V7, V7, 1, 0.1],
                ["A", V7, V7, 0.1, 1],
                ["A", V7, V7, 0.0, 0.1],
                ["A", V7, V7, 0.1, 0.0],
                ["A", V7, V7, 1.1, 0.1],
                ["A", V7, V7, 0.1, 1.1],
            ]
        ],
        *[
            (method, ["X", *args], None)
            for method, args, native, expected in BASIC
            if method not in ["setPln_joint", "setPln_Cart"]
        ],
    ],
)
def test_basic_error_conventions(method, args, expected):
    r = Marvin_Robot()
    r.robot = Backend(error=True)
    assert getattr(r, method)(*args) == expected


@pytest.mark.parametrize(
    "method,args,expected",
    [
        ("pln_init", ["config"], False),
        ("start_collect_data", [1, [1], 1000], False),
        ("stop_collect_data", [], False),
        ("save_gather_data", ["data.csv"], False),
        ("disable", ["A"], False),
        ("clear_ch_data", ["A"], False),
        ("set_ch_data", ["A", b"\x01", 1, 1], -1),
    ],
)
def test_concise_io_failures(method, args, expected):
    r = Concise_Marvin_Robot()
    r.robot = Backend(error=True)
    assert getattr(r, method)(*args) == expected
