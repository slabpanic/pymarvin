"""Check record setters, ABI failure diagnostics and public helpers."""

import inspect

import pytest
import pymarvin as mv
from pymarvin import fx_kine, fx_robot, _control
from pymarvin._validation import verify_layouts


@pytest.mark.parametrize(
    "record,size", [(mv.Vect7, 7), (mv.Matrix4, 16), (mv.Matrix8, 64)]
)
def test_numeric_record_roundtrip(record, size):
    values = list(range(size))
    r = record(values)
    assert r.to_list() == values
    assert str(r) == str([float(x) for x in values])
    assert record().to_list() == [0] * size
    with pytest.raises(ValueError):
        record(values[:-1])


def test_synchronous_record_validation():
    r = mv.ArmsSynchronousPlanningParams(
        Arm0_Ref_Joints=list(range(7)), Freq=100, World_Co_Flag=True
    )
    assert list(r.Arm0_Ref_Joints) == list(range(7))
    assert r.Freq == 100 and r.World_Co_Flag
    assert list(r.Arm1_Ref_Joints) == [0] * 7
    with pytest.raises(ValueError, match="unknown field"):
        mv.ArmsSynchronousPlanningParams(unknown=1)
    with pytest.raises(ValueError, match="exactly 7"):
        mv.ArmsSynchronousPlanningParams(Arm0_Ref_Joints=[])


def test_inverse_record_inputs_outputs():
    r = mv.FX_InvKineSolvePara()
    r.set_all_inputs(
        target_tcp=list(range(16)),
        ref_joint=list(range(7)),
        zsp_type=2,
        zsp_para=list(range(6)),
        zsp_angle=45.0,
        dgr1=1,
        dgr2=2,
        dgr3=3,
    )
    assert r.m_Input_IK_TargetTCP.to_list() == list(range(16))
    assert r.m_Input_IK_RefJoint.to_list() == list(range(7))
    assert r.get_input_ik_zsp_para() == list(range(6))
    assert (r.m_Input_ZSP_Angle, r.m_DGR1, r.m_DGR2, r.m_DGR3) == (45, 1, 2, 3)
    r.m_Output_RetJoint = mv.Vect7(list(range(7)))
    r.m_OutPut_AllJoint = mv.Matrix8(list(range(64)))
    r.m_OutPut_Result_Num = 4
    r.m_Output_IsOutRange = True
    r.m_Output_IsDeg[3] = True
    r.set_output_jnt_exd_tags([True] * 7)
    r.m_Output_JntExdABS = 12
    r.m_Output_IsJntExd = True
    r.m_Output_RunLmtP = mv.Vect7([100] * 7)
    r.m_Output_RunLmtN = mv.Vect7([-100] * 7)
    assert r.get_all_outputs() == dict(
        ret_joint=list(range(7)),
        all_joint=list(range(64)),
        result_num=4,
        is_out_range=True,
        is_deg=[False] * 3 + [True] + [False] * 3,
        jnt_exd_tags=[True] * 7,
        jnt_exd_abs=12,
        is_jnt_exd=True,
        run_lmt_positive=[100] * 7,
        run_lmt_negative=[-100] * 7,
    )
    assert "FX_InvKineSolvePara" in repr(r)
    for method in [
        "set_input_ik_target_tcp",
        "set_input_ik_ref_joint",
        "set_input_ik_zsp_para",
        "set_output_jnt_exd_tags",
    ]:
        with pytest.raises(ValueError):
            getattr(r, method)([])
    with pytest.raises(ValueError, match="Unknown input"):
        r.set_all_inputs(unknown=1)


def test_jacobian_record_and_solution_filter(capsys):
    jac = mv.FX_Jacobi()
    mat = [[float(i * 7 + j) for j in range(7)] for i in range(6)]
    jac.set_jcb(mat)
    assert jac.get_jcb() == mat
    assert "41.000000" in str(jac)
    for invalid in [[], [[0] * 6] * 6]:
        with pytest.raises(ValueError):
            jac.set_jcb(invalid)
    assert (
        fx_kine.convert_to_8x8_matrix([0] * 8 + list(range(8)) * 7)
        == [list(range(8))] * 7
    )
    with pytest.raises(ValueError):
        fx_kine.convert_to_8x8_matrix([])
    fx_kine.inv_main()
    assert "bytes" in capsys.readouterr().out


@pytest.mark.parametrize("field", ["__size__", "m_State"])
def test_abi_corruption_rejected(monkeypatch, field):
    layouts = {name: dict(values) for name, values in _control._layouts.items()}
    layouts["DCSS"][field] += 1
    monkeypatch.setattr(_control, "_layouts", layouts)
    with pytest.raises(ImportError, match="mismatch"):
        verify_layouts()


@pytest.mark.parametrize(
    "cls", [mv.Marvin_Kine, mv.Marvin_Robot, mv.Concise_Marvin_Robot]
)
def test_english_help(cls, capsys):
    r = cls()
    r.help()
    assert "Available methods" in capsys.readouterr().out
    method = "fk" if cls == mv.Marvin_Kine else "connect"
    r.help(method)
    assert inspect.getdoc(getattr(r, method)) in capsys.readouterr().out
    r.help("missing_method")
    assert "Unknown method" in capsys.readouterr().out


def test_comments_and_docstrings_are_english():
    import ast
    import io
    import tokenize
    from pathlib import Path

    for module in [fx_robot, fx_kine]:
        path = Path(__file__).parents[1] / "src/pymarvin" / Path(module.__file__).name
        source = path.read_text()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
                assert not any(
                    "\u4e00" <= c <= "\u9fff" for c in (ast.get_docstring(node) or "")
                )
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT:
                assert not any("\u4e00" <= c <= "\u9fff" for c in token.string)
