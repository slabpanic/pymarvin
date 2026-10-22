"""Exercise SDK results, shape validation and owned planning buffers offline."""

from types import SimpleNamespace

import pytest
import pymarvin as mv
from pymarvin import _kinematics

Q = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
POSE = [0.0] * 6
MAT = [[float(i == j) for j in range(4)] for i in range(4)]
DH = [[0.0] * 4 for _ in range(8)]
PNVA = [[180.0, -180.0, 100.0, 100.0] for _ in range(7)]
BD = [[0.0] * 3 for _ in range(4)]


@pytest.fixture
def robot():
    k = mv.Marvin_Kine()
    k.robot_tag = 2
    return k


@pytest.mark.parametrize(
    "method,args",
    [
        ("load_config", (3, "missing")),
        ("load_config", (0, "missing")),
        ("initial_kine", ("1007", DH, PNVA, BD)),
        *[
            (
                "initial_kine",
                tuple([1007, DH, PNVA, BD][:i] + [bad] + [1007, DH, PNVA, BD][i + 1 :]),
            )
            for i, bad in [
                (1, []),
                (1, [[0]] * 8),
                (2, []),
                (2, [[0]] * 7),
                (3, []),
                (3, [[0]] * 4),
            ]
        ],
        *[
            (name, (bad,))
            for name in ["set_tool_kine", "set_user_frame_kine", "mat4x4_to_xyzabc"]
            for bad in [[], [[0]] * 4]
        ],
        *[
            (name, ([],))
            for name in ["fk", "fk_nsp", "joints2JacobMatrix", "xyzabc_to_mat4x4"]
        ],
        *[
            ("calculate_end_xyzabc", args)
            for args in [
                ([], [0] * 3, 11, [0] * 3),
                (POSE, [], 11, [0] * 3),
                (POSE, [0] * 3, 11, []),
                (POSE, [0] * 3, "11", [0] * 3),
            ]
        ],
        ("jnt_tau_to_ee_tau", ([], Q)),
        ("jnt_tau_to_ee_tau", (Q, [])),
        ("cal_ee_linear_vel", ([], Q)),
        ("cal_ee_linear_vel", (Q, [])),
        *[
            (method, args)
            for method in ["movLA", "mov_target"]
            for args in [
                ([], POSE, Q, 0.1, 0.1, 100),
                (POSE, [], Q, 0.1, 0.1, 100),
                (POSE, POSE, [], 0.1, 0.1, 100),
            ]
        ],
        *[
            (
                "multi_movL_set_start",
                tuple(
                    [Q, POSE, POSE, 1.0, 0, POSE, 0.1, 0.1, 100][:i]
                    + [[]]
                    + [Q, POSE, POSE, 1.0, 0, POSE, 0.1, 0.1, 100][i + 1 :]
                ),
            )
            for i in [0, 1, 2, 5]
        ],
    ],
)
def test_invalid_shapes(robot, method, args):
    robot.kine = SimpleNamespace()
    with pytest.raises(ValueError):
        getattr(robot, method)(*args)


@pytest.mark.parametrize("stage", range(3))
def test_initialization_failure(robot, stage):
    names = ["FX_Robot_Init_Type", "FX_Robot_Init_Kine", "FX_Robot_Init_Lmt"]
    calls = []

    def impl(index):
        def call(*args):
            calls.append(index)
            return index != stage

        return call

    robot.kine = SimpleNamespace(**{n: impl(i) for i, n in enumerate(names)})
    assert robot.initial_kine(1007, DH, PNVA, BD) is False
    assert calls == [0, 1, 2]


@pytest.mark.parametrize(
    "method,args,native",
    [
        ("set_tool_kine", (MAT,), "FX_Robot_Tool_Set"),
        ("set_user_frame_kine", (MAT,), "FX_Robot_UserFrame_Set"),
        ("remove_tool_kine", (), "FX_Robot_Tool_Rmv"),
        ("remove_user_frame_kine", (), "FX_Robot_UserFrame_Rmv"),
        ("fk", (Q,), "FX_Robot_Kine_FK"),
        ("fk_nsp", (Q,), "FX_Robot_Kine_FK_NSP"),
        ("ik", (mv.FX_InvKineSolvePara(),), "FX_Robot_Kine_IK"),
        ("ik_nsp", (mv.FX_InvKineSolvePara(),), "FX_Robot_Kine_IK_NSP"),
        ("joints2JacobMatrix", (Q,), "FX_Robot_Kine_Jacb"),
        ("mat4x4_to_xyzabc", (MAT,), "FX_Matrix42XYZABCDEG"),
        ("calculate_end_xyzabc", (POSE, [0] * 3, 11, [0] * 3), "FX_Robot_CalEndXYZABC"),
        ("jnt_tau_to_ee_tau", (Q, Q), "FX_Robot_JntTau2EETau"),
    ],
)
def test_native_failure(robot, method, args, native):
    for arg in args:
        if isinstance(arg, mv.FX_InvKineSolvePara):
            arg.m_Output_IsOutRange = True
            arg.m_Output_IsDeg[3] = True
    robot.kine = SimpleNamespace(**{native: lambda *a: False})
    assert getattr(robot, method)(*args) is False


PLANS = [
    ("movLA", (POSE, POSE, Q, 0.1, 0.1, 100), "FX_Robot_PLN_MOVLA_C"),
    ("movL_KeepJA", (Q, Q, 0.1, 0.1, 100), "FX_Robot_PLN_MOVL_KeepJA_C"),
    ("mov_target", (POSE, POSE, Q, 0.1, 0.1, 100), "FX_Robot_PLN_MOV_Target_C"),
    ("multi_movL_get_points", (), "FX_Robot_PLN_Get_MOVL_Path_C"),
    ("movL_synchronous", ({"Freq": 100},), "FX_Robot_PLN_MOVL_Arms_Synchronous"),
]


@pytest.mark.parametrize("method,args,native", PLANS)
@pytest.mark.parametrize("outcome", ["success", "failure", "exception", "allocation"])
def test_planning_ownership(robot, monkeypatch, method, args, native, outcome):
    created = []

    def create(dimension):
        if outcome == "allocation":
            return None
        p = mv.PointSet(dimension)
        created.append(p)
        return p

    monkeypatch.setattr(robot, "create_point_set", create)

    def plan(*arguments):
        if outcome == "exception":
            raise LookupError("planning failed")
        for a in arguments:
            if isinstance(a, mv.PointSet):
                a.append(Q)
        return outcome == "success"

    robot.kine = SimpleNamespace(
        **{native: plan, "FX_CPointSet_Destroy": _kinematics.FX_CPointSet_Destroy}
    )
    if outcome == "allocation":
        with pytest.raises(RuntimeError, match="create"):
            getattr(robot, method)(*args)
    elif outcome == "exception":
        with pytest.raises(LookupError):
            getattr(robot, method)(*args)
        # The official multipoint facade delegates cleanup to the owning handle.
        if method != "multi_movL_get_points":
            assert all(p.closed for p in created)
    else:
        result = getattr(robot, method)(*args)
        if outcome == "success":
            assert result[0] == [Q]
            assert not result[1].closed
            if method == "movL_synchronous":
                assert result[2] == [Q]
            for p in created:
                p.close()
        else:
            assert result[:2] == ([], None)
            assert all(p.closed for p in created)


@pytest.mark.parametrize(
    "method,native,args",
    [
        ("movL", "FX_Robot_PLN_MOVL", (POSE, POSE, Q, 0.1, 0.1, 100)),
        ("movL_KeepJ", "FX_Robot_PLN_MOVL_KeepJ", (Q, Q, 0.1, 0.1, 100)),
    ],
)
@pytest.mark.parametrize("outcome", ["success", "failure", "missing"])
def test_planning_file_results(robot, tmp_path, method, native, args, outcome):
    path = tmp_path / "path.pvt"

    def plan(*a):
        if outcome == "success":
            path.write_text("synthetic path")
        return outcome != "failure"

    robot.kine = SimpleNamespace(**{native: plan})
    assert (
        getattr(robot, method)(*args, str(path))
        is {"success": True, "failure": False, "missing": None}[outcome]
    )


@pytest.mark.parametrize("m20", [False, True])
@pytest.mark.parametrize("code", range(5))
@pytest.mark.parametrize("kind", [1, 2])
def test_identification_outputs(robot, tmp_path, m20, code, kind):
    path = tmp_path / "samples"
    path.write_text("offline")

    def identify(*a):
        mass, mcp, inertia = a[-3:]
        mass.value = 3
        mcp[:] = [4, 5, 6]
        inertia[:] = [1, 2, 3, 4, 5, 6]
        return code

    native = "FX_Robot_Iden_LoadDyn" + ("_M20" if m20 else "")
    robot.kine = SimpleNamespace(**{native: identify})
    result = (
        robot.identify_tool_dyn_m20(str(path), kind, str(path))
        if m20
        else robot.identify_tool_dyn(kind, str(path))
    )
    if code:
        assert result.startswith(f"ret={code},")
    else:
        assert result == [3, 4, 5, 6, 1, 4, 5, 2, 6, 3]


def test_optional_capabilities_and_streaming(robot):
    robot.kine = SimpleNamespace()
    assert robot.cal_ee_linear_vel(Q, Q) is None
    assert robot.jnt_tau_to_ee_tau(Q, Q) is False
    with pytest.raises(RuntimeError, match="not exported"):
        robot.movL_synchronous({})
    robot.kine.FX_Robot_PLN_MOVL_Arms_Synchronous = lambda *a: True
    with pytest.raises(TypeError):
        robot.movL_synchronous(42)
    assert robot.get_point_set_data(None) == []
    seen = []

    def streaming(*args):
        seen.append(
            [getattr(a, "value", list(a) if hasattr(a, "__len__") else a) for a in args]
        )
        return True

    robot.kine.FX_Robot_PLN_Set_MOVL_Start = streaming
    robot.kine.FX_Robot_PLN_Set_MOVL_Next_Point = streaming
    assert robot.multi_movL_set_start(Q, POSE, POSE, 2, 1, POSE, 0.1, 0.2, 100)
    assert robot.multi_movL_next_point(POSE, 2, 1, POSE, 0.1, 0.2)
    assert seen[0][1] == Q
    assert seen[1][1] == POSE

    def torque(*a):
        a[-1][:] = [1, 2, 3, 4, 5, 6]
        return True

    robot.kine.FX_Robot_JntTau2EETau = torque
    assert robot.jnt_tau_to_ee_tau(Q, Q) == [1, 2, 3, 4, 5, 6]


@pytest.mark.parametrize(
    "args,m20",
    [
        ((1, "missing"), False),
        (("1", "missing"), False),
        (("missing", 1, "missing"), True),
        (("missing", "1", "missing"), True),
    ],
)
def test_identification_input_errors(robot, args, m20):
    with pytest.raises(ValueError):
        (robot.identify_tool_dyn_m20 if m20 else robot.identify_tool_dyn)(*args)
