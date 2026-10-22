"""Test compiled boundary validation without opening a network connection."""

import ctypes as ct

import pytest
from pymarvin import DCSS, FTCmd, PointSet, _control, _kinematics


def doubles(n):
    return (ct.c_double * n)(*[float(i) for i in range(n)])


def controller_cases():
    for name in [
        "OnEMG_A",
        "OnEMG_B",
        "OnEMG_AB",
        "OnLogOn",
        "OnLogOff",
        "OnSavePara",
        "OnClearSet",
        "OnClearErr_A",
        "OnClearErr_B",
        "OnStopGather",
        "OnSetSend",
        "OnStopPlnJoint_A",
        "OnStopPlnJoint_B",
        "CoStopPln",
        "OnClearChDataA",
        "OnClearChDataB",
        "CheckArmError",
        "CheckServoError",
        "ClearErr",
        "StopCollectData",
        "OnSetReboot",
    ]:
        yield name, []
    for name in [
        "OnUpdateSystem",
        "OnDownloadLog",
        "OnSaveGatherData",
        "OnSaveGatherDataCSV",
        "OnInitPlnLmt",
        "PlnInit",
    ]:
        yield name, [b"unused-local-path"]
    for name in ["OnSendFile", "OnRecvFile"]:
        yield name, [b"local", b"remote"]
    for arm in ["A", "B"]:
        for stem, args in [
            ("OnServoReset", [0]),
            ("OnGetServoErr", [(ct.c_long * 7)()]),
            ("OnSendPVT", [b"path", 0]),
            ("OnSetTool", [doubles(6), doubles(10)]),
            ("OnSetJointLmt", [10, 10]),
            ("OnSetJointKD", [doubles(7), doubles(7)]),
            ("OnSetCartKD", [doubles(7), doubles(7), 2]),
            ("OnSetEefRot", [1, doubles(7)]),
            ("OnSetForceCtrPara", [1, doubles(6), doubles(7), 1.0]),
            ("OnSetForceCmd", [1.0]),
            ("OnSetTargetState", [1]),
            ("OnSetImpType", [1]),
            ("OnSetDragSpace", [1]),
            ("OnSetJointCmdPos", [doubles(7)]),
            ("OnSetPVT", [0]),
            ("OnSetPlnJoint", [doubles(7), doubles(7), 0.1, 0.1]),
            ("OnSetUserSpcfData", [0]),
        ]:
            yield stem + "_" + arm, args
        yield "OnGetChData" + arm, [(ct.c_ubyte * 256)(), ct.c_long(1)]
        yield "OnSetChData" + arm, [(ct.c_ubyte * 256)(), 2, 1]
    para = (ct.c_char * 30)(*b"R.A0.Type")
    for name, second in [
        ("OnSetIntPara", 1),
        ("OnSetFloatPara", 1.0),
        ("OnGetIntPara", ct.c_long()),
        ("OnGetFloatPara", ct.c_double()),
    ]:
        yield name, [para, second]
    for name in ["OnStartGather", "StartCollectData"]:
        yield name, [1, (ct.c_long * 35)(), 1000]
    yield "OnSetSendWaitResponse", [1]
    yield "CoRunPlnJoint", [doubles(7), doubles(7), doubles(7), doubles(7), 0.1, 0.1]
    for name, tail in [
        ("EStop", []),
        ("ServoReset", [0]),
        ("SetTool", [doubles(6), doubles(10)]),
        ("SetJointMode", [10, 10]),
        ("SetImpJointMode", [10, 10, doubles(7), doubles(7)]),
        ("SetImpCartMode", [10, 10, doubles(7), doubles(7), 0, doubles(7)]),
        ("SetJointPostionCmd", [doubles(7)]),
        ("SetImpForceMode", [doubles(6), 1.0]),
        ("SetForceCmd", [1.0]),
        ("RunPlnJoint", [doubles(7), doubles(7), 0.1, 0.1]),
        ("StopPln", []),
        ("SendPVT", [b"path", 0]),
        ("RunPVT", [0]),
        ("SetJointDrag", []),
        ("SetCartDrag", [b"X"]),
        ("ExitDrag", []),
        ("ClearChData", []),
        ("GetChData", [(ct.c_ubyte * 256)(), ct.c_long(1)]),
        ("SetChData", [(ct.c_ubyte * 256)(), 1, 1]),
        ("Disable", []),
        ("FX_OnSetVelEstStep", [1]),
        ("FTArmControl", [FTCmd()]),
        ("OnReset6DofForceSensor", []),
    ]:
        yield name, [b"A", *tail]
    yield "LogSwitch", [0]
    yield "OnSetUserSpcfData", [1]
    yield "OnGetRobotName", [ct.create_string_buffer(512)]
    yield "OnSetSystemTime", [2026, 1, 1, 0, 0, 0]
    yield "OnSetStopRunning", [b"AB"]


@pytest.mark.parametrize("name,args", list(controller_cases()))
def test_every_uninitialized_control_command_is_guarded(name, args):
    with pytest.raises(RuntimeError, match="call connect"):
        getattr(_control, name)(*args)


def test_control_point_copies_and_uninitialized_calls():
    with PointSet(7) as left, PointSet(7) as right:
        left.append([1, 2, 3, 4, 5, 6, 7])
        right.append([7, 6, 5, 4, 3, 2, 1])
        for name, args in [
            ("OnSetPlnCart_A", [left]),
            ("OnSetPlnCart_B", [right]),
            ("RunPlnCart", [b"A", left]),
            ("CoRunPlnCart", [left, right]),
        ]:
            with pytest.raises(RuntimeError, match="call connect"):
                getattr(_control, name)(*args)
        assert left.to_list() == [[1, 2, 3, 4, 5, 6, 7]]
    assert _control.OnGetBuf(DCSS()) is False
    assert _control.ValidateArm(b"A") is True
    assert _control.ValidateArm(b"X") is False
    assert _control.OnLinkTo(127, 0, 0, 1) is False
    assert _control.Connect(127, 0, 0, 1) is False


def test_native_text_scalars_and_buffer_lifetimes():
    for text in ["hello", b"hello", ct.c_char_p(b"hello")]:
        with pytest.raises(RuntimeError, match="call connect"):
            _control.OnUpdateSystem(text)
    with pytest.raises(ValueError, match="NUL"):
        _control.OnUpdateSystem(b"bad\0path")
    with pytest.raises(ValueError, match="one character"):
        _control.ServoReset(b"AB", 0)
    with pytest.raises(TypeError):
        _control.CheckSDKTypeCompat(0)
    output = ct.c_int()
    assert _control.CheckSDKTypeCompat(ct.byref(output)) > 0
    matrix = ((ct.c_double * 4) * 4)()
    with pytest.raises((TypeError, BufferError)):
        _kinematics.FX_XYZABC2Matrix4DEG(bytes(48), matrix)
    for _ in range(10):
        pose = (ct.c_double * 6)(1, 2, 3, 0, 0, 0)
        _kinematics.FX_XYZABC2Matrix4DEG(pose, matrix)
        assert matrix[2][3] == 3


def test_pointset_c_wrappers_and_reinitialization():
    points = _kinematics.FX_CPointSet_Create()
    assert bool(points) and len(points) == 0
    assert _kinematics.FX_CPointSet_OnInit(points, 3)
    assert _kinematics.FX_CPointSet_OnSetPoint(points, [1.0, 2.0, 3.0])
    assert _kinematics.FX_CPointSet_OnGetPointNum(points) == 1
    assert _kinematics.FX_CPointSet_OnGetPoint(points, 0) == [1.0, 2.0, 3.0]
    assert _kinematics.FX_CPointSet_OnInit(points, 3)
    assert len(points) == 0
    _kinematics.FX_CPointSet_Destroy(points)
    assert not points
    with pytest.raises(RuntimeError):
        _kinematics.FX_CPointSet_OnInit(points, 3)


def planning_cases():
    for name in [
        "FX_Robot_PLN_MOVL",
        "FX_Robot_PLN_MOVLA",
        "FX_Robot_PLN_MOVLA_C",
        "FX_Robot_PLN_MOV_Target",
        "FX_Robot_PLN_MOV_Target_C",
    ]:
        output = b"unused.pvt" if name == "FX_Robot_PLN_MOVL" else PointSet(7)
        yield name, [doubles(6), doubles(6), doubles(7), 0.1, 0.1, 0, output]
    for name in [
        "FX_Robot_PLN_MOVL_KeepJ",
        "FX_Robot_PLN_MOVL_KeepJA",
        "FX_Robot_PLN_MOVL_KeepJA_C",
        "FX_Robot_PLN_MOVJ",
    ]:
        output = b"unused.pvt" if name == "FX_Robot_PLN_MOVL_KeepJ" else PointSet(7)
        yield name, [doubles(7), doubles(7), 0.1, 0.1, 0, output]
    yield "FX_Robot_PLN_Set_MOVL_Start", [
        doubles(7),
        doubles(6),
        doubles(6),
        1.0,
        0,
        doubles(6),
        0.1,
        0.1,
        0,
    ]


@pytest.mark.parametrize("name,args", list(planning_cases()))
def test_native_planning_frequency_and_initialization(kine, name, args):
    method = getattr(_kinematics, name)
    with pytest.raises(ValueError, match="serial"):
        method(10, *args)
    with pytest.raises(RuntimeError, match="initialize"):
        method(9, *args)
    with pytest.raises(ValueError, match="frequency"):
        method(kine.robot_tag, *args)


@pytest.mark.parametrize(
    "name", ["FX_Robot_PLN_Get_MOVL_Path", "FX_Robot_PLN_Get_MOVL_Path_C"]
)
def test_planning_output_dimension(kine, name):
    with PointSet(6) as output:
        with pytest.raises(ValueError, match="seven-dimensional"):
            getattr(_kinematics, name)(kine.robot_tag, output)


def test_native_synchronous_preconditions():
    from pymarvin import ArmsSynchronousPlanningParams

    params = ArmsSynchronousPlanningParams()
    with PointSet(7) as a, PointSet(7) as b, PointSet(6) as short:
        with pytest.raises(ValueError, match="Freq"):
            _kinematics.FX_Robot_PLN_MOVL_Arms_Synchronous(params, a, b)
        params.Freq = 100
        with pytest.raises(ValueError, match="seven-dimensional"):
            _kinematics.FX_Robot_PLN_MOVL_Arms_Synchronous(params, short, b)
        with pytest.raises(ValueError, match="seven-dimensional"):
            _kinematics.FX_Robot_PLN_MOVL_Arms_Synchronous(params, a, short)
        with pytest.raises(RuntimeError, match="both arms"):
            _kinematics.FX_Robot_PLN_MOVL_Arms_Synchronous(params, a, b)


def test_native_missing_identification_files(tmp_path):
    missing = str(tmp_path / "missing").encode()
    mass = ct.c_double(123.0)
    assert (
        _kinematics.FX_Robot_Iden_LoadDyn(99, missing, mass, doubles(3), doubles(6))
        != 0
    )
    assert mass.value == 123.0
    assert (
        _kinematics.FX_Robot_Iden_LoadDyn_M20(
            missing, 1, missing, mass, doubles(3), doubles(6)
        )
        != 0
    )
