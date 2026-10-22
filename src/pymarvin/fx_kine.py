"""Official-compatible API; SDK calls use the nanobind extension.

Compatible with the official Marvin Python API; maintained with English docstrings.
"""

import ast
from ipaddress import IPv4Address
from . import _kinematics as _native
from ctypes import *
import ctypes
import inspect
from textwrap import dedent
import logging
import os
import sys
from typing import List

current_file_path = os.path.abspath(__file__)
current_path = os.path.dirname(current_file_path)
logger = logging.getLogger(__name__)


class Marvin_Kine:
    """Offline kinematics and planning interface. Load a model and initialize its type, DH table and limits before robot-specific calculations."""

    def __init__(self):
        """Create this interface or value record without opening a robot connection."""
        logger.info(f"user platform: {sys.platform}")
        self.kine = _native
        self.sp = FX_InvKineSolvePara()
        self.jacobi = FX_Jacobi()
        self.jacobi_dot = FX_Jacobi()
        self.robot_tag = None

    def create_point_set(self, point_type: int = 6) -> ctypes.c_void_p:
        """Create an owned PointSet with 1 through 40 values per point (default 6)."""
        pset = self.kine.FX_CPointSet_Create()
        if pset:
            self.kine.FX_CPointSet_OnInit(pset, point_type)
        return pset

    def destroy_point_set(self, pset: ctypes.c_void_p):
        """Close an owned PointSet. Repeated closing is safe; its storage is also reclaimed automatically."""
        if pset:
            self.kine.FX_CPointSet_Destroy(pset)

    def get_point_set_data(
        self, pset: ctypes.c_void_p, dimension: int = 6
    ) -> List[List[float]]:
        """Copy an owned PointSet to nested lists. dimension must match the stored point dimension."""
        if pset is None:
            return []
        if dimension != pset.dimension:
            raise ValueError("dimension does not match PointSet")
        return pset.to_list()

    def help(self, method_name: str = None) -> None:
        """Print public method signatures or the documentation for method_name."""
        methods = {
            name: method
            for name, method in inspect.getmembers(self, inspect.ismethod)
            if not name.startswith("_") and name != "help"
        }
        if method_name is None:
            print("Available methods:")
            for name, method in methods.items():
                print(f"  {name}{inspect.signature(method)}")
        elif method_name in methods:
            print(f"{method_name}{inspect.signature(methods[method_name])}")
            print(inspect.getdoc(methods[method_name]) or "No documentation available.")
        else:
            print(f"Unknown method: {method_name}")

    def _param_kind_to_str(kind):
        """Return a readable description of an inspect parameter kind."""
        mapping = {
            inspect.Parameter.POSITIONAL_ONLY: "位置参数",
            inspect.Parameter.POSITIONAL_OR_KEYWORD: "位置或关键字参数",
            inspect.Parameter.VAR_POSITIONAL: "可变位置参数(*args)",
            inspect.Parameter.KEYWORD_ONLY: "仅关键字参数",
            inspect.Parameter.VAR_KEYWORD: "可变关键字参数(**kwargs)",
        }
        return mapping.get(kind, "未知参数类型")

    def log_switch(self, switch: int):
        """Set kinematics SDK logging: 1 enables messages and 0 disables them."""
        switch_ = c_int32(switch)
        self.kine.FX_LOG_SWITCH(switch_)

    def load_config(self, arm_type: int, config_path: str):
        """Read a robot configuration file for arm_type 0 (left) or 1 (right). Return both arms' configuration arrays or None."""
        if arm_type != 0 and arm_type != 1:
            raise ValueError("arm_type must be 0 or 1")
        if not os.path.exists(config_path):
            raise ValueError("no config file")
        if arm_type == 0:
            self.robot_tag = 0
        if arm_type == 1:
            self.robot_tag = 1
        TYPE = (c_int32 * 2)()
        GRV = (c_double * 3 * 2)()
        DH = (c_double * 4 * 8 * 2)()
        PNVA = (c_double * 4 * 7 * 2)()
        BD = (c_double * 3 * 4 * 2)()
        Mass = (c_double * 7 * 2)()
        MCP = (c_double * 3 * 7 * 2)()
        I = (c_double * 6 * 7 * 2)()
        success = self.kine.LOADMvCfg(
            config_path.encode("utf-8"),
            ctypes.byref(TYPE),
            ctypes.byref(GRV),
            ctypes.byref(DH),
            ctypes.byref(PNVA),
            ctypes.byref(BD),
            ctypes.byref(Mass),
            ctypes.byref(MCP),
            ctypes.byref(I),
        )
        if success:
            result = {
                "TYPE": [TYPE[i] for i in range(2)],
                "GRV": [[GRV[i][j] for j in range(3)] for i in range(2)],
                "DH": [
                    [[DH[i][j][k] for k in range(4)] for j in range(8)]
                    for i in range(2)
                ],
                "PNVA": [
                    [[PNVA[i][j][k] for k in range(4)] for j in range(7)]
                    for i in range(2)
                ],
                "BD": [
                    [[BD[i][j][k] for k in range(3)] for j in range(4)]
                    for i in range(2)
                ],
                "Mass": [[Mass[i][j] for j in range(7)] for i in range(2)],
                "MCP": [
                    [[MCP[i][j][k] for k in range(3)] for j in range(7)]
                    for i in range(2)
                ],
                "I": [
                    [[I[i][j][k] for k in range(6)] for j in range(7)] for i in range(2)
                ],
            }
            logger.info("Load config successful")
            return result
        else:
            logger.error("Load config failed")
            return None

    def initial_kine(self, robot_type: int, dh: list, pnva: list, j67: list):
        """Initialize robot type, an 8x4 DH table, 7x4 joint limits and 4x3 joint-6/7 interference parameters, in that order."""
        if type(robot_type) != int:
            raise ValueError("robot_type  must be int type")
        if len(dh) != 8:
            raise ValueError("dh  must be 8 rows")
        else:
            for i in range(len(dh)):
                if len(dh[i]) != 4:
                    raise ValueError("dh  must be 4 columns")
        if len(pnva) != 7:
            raise ValueError("pnva  must be 7 rows")
        else:
            for i in range(len(pnva)):
                if len(pnva[i]) != 4:
                    raise ValueError("pnva  must be 4 columns")
        if len(j67) != 4:
            raise ValueError("j67  must be 4 rows")
        else:
            for i in range(len(j67)):
                if len(j67[i]) != 3:
                    raise ValueError("j67  must be 3 columns")
        Serial = ctypes.c_int32(self.robot_tag)
        robot_type_ = c_int32(robot_type)
        DH = (c_double * 4 * 8)()
        for i in range(8):
            for j in range(4):
                DH[i][j] = dh[i][j]
        PNVA = (c_double * 4 * 7)()
        for i in range(7):
            for j in range(4):
                PNVA[i][j] = pnva[i][j]
        J67 = (c_double * 3 * 4)()
        for i in range(4):
            for j in range(3):
                J67[i][j] = j67[i][j]
        success1 = self.kine.FX_Robot_Init_Type(Serial, robot_type_)
        success2 = self.kine.FX_Robot_Init_Kine(Serial, DH)
        success3 = self.kine.FX_Robot_Init_Lmt(Serial, PNVA, J67)
        if success1 and success2 and success3:
            logger.info("Initial kinematics successful")
            return True
        elif not success1:
            logger.error("Initial kinematics failed:FX_Robot_Init_Type")
            return False
        elif not success2:
            logger.error("Initial kinematics failed:FX_Robot_Init_Kine")
            return False
        elif not success3:
            logger.error("Initial kinematics failed:FX_Robot_Init_Lmt")
            return False

    def set_tool_kine(self, tool_mat: list):
        """Set a 4x4 homogeneous tool transform for forward and inverse kinematics."""
        if len(tool_mat) != 4:
            raise ValueError("tool_mat  must be 4 rows")
        else:
            for i in range(len(tool_mat)):
                if len(tool_mat[i]) != 4:
                    raise ValueError("tool_mat  must be 4 columns")
        Serial = ctypes.c_int32(self.robot_tag)
        TOOL = (c_double * 4 * 4)()
        for i in range(4):
            for j in range(4):
                TOOL[i][j] = tool_mat[i][j]
        success1 = self.kine.FX_Robot_Tool_Set(Serial, TOOL)
        if success1:
            logger.info("set tool kinematics info successful")
            return True
        else:
            logger.error("set tool kinematics info failed!")
            return False

    def remove_tool_kine(self):
        """Remove the tool transform from this robot's kinematics."""
        Serial = ctypes.c_int32(self.robot_tag)
        success1 = self.kine.FX_Robot_Tool_Rmv(Serial)
        if success1:
            logger.info("remove tool kinematics info successful")
            return True
        else:
            logger.error("remove tool kinematics info failed!")
            return False

    def set_user_frame_kine(self, user_mat: list):
        """Set a 4x4 homogeneous user-frame transform."""
        if len(user_mat) != 4:
            raise ValueError("user_mat  must be 4 rows")
        else:
            for i in range(len(user_mat)):
                if len(user_mat[i]) != 4:
                    raise ValueError("user_mat  must be 4 columns")
        Serial = ctypes.c_int32(self.robot_tag)
        TOOL = (c_double * 4 * 4)()
        for i in range(4):
            for j in range(4):
                TOOL[i][j] = user_mat[i][j]
        success1 = self.kine.FX_Robot_UserFrame_Set(Serial, TOOL)
        if success1:
            logger.info("set user frame info successful")
            return True
        else:
            logger.error("set user frame info failed!")
            return False

    def remove_user_frame_kine(self):
        """Remove the user-frame transform."""
        Serial = ctypes.c_int32(self.robot_tag)
        success1 = self.kine.FX_Robot_UserFrame_Rmv(Serial)
        if success1:
            logger.info("remove user frame  info successful")
            return True
        else:
            logger.error("remove user frame  info failed!")
            return False

    def fk(self, joints: list):
        """Compute a 4x4 TCP transform from seven joint angles in degrees. Return False when the SDK cannot solve it."""
        if len(joints) != 7:
            raise ValueError("shape error: fk input joints must be (7,)")
        Serial = ctypes.c_int32(self.robot_tag)
        joints_double = (ctypes.c_double * 7)(*joints)
        Matrix4x4 = ctypes.c_double * 4 * 4
        pg = Matrix4x4()
        for i in range(4):
            for j in range(4):
                pg[i][j] = 1.0 if i == j else 0.0
        success1 = self.kine.FX_Robot_Kine_FK(
            Serial, ctypes.byref(joints_double), ctypes.byref(pg)
        )
        if success1:
            fk_mat = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            for i in range(4):
                for j in range(4):
                    fk_mat[i][j] = pg[i][j]
            logger.info(f"fk result, matrix:{fk_mat}")
            return fk_mat
        else:
            return False

    def fk_nsp(self, joints: list):
        """Compute the TCP transform and 3x3 null-space reference matrix from seven joint angles in degrees."""
        if len(joints) != 7:
            raise ValueError("shape error: fk input joints must be (7,)")
        Serial = ctypes.c_int32(self.robot_tag)
        joints_double = (ctypes.c_double * 7)(*joints)
        Matrix4x4 = ctypes.c_double * 4 * 4
        pg = Matrix4x4()
        for i in range(4):
            for j in range(4):
                pg[i][j] = 1.0 if i == j else 0.0
        Matrix3x3 = ctypes.c_double * 3 * 3
        nspg = Matrix3x3()
        success1 = self.kine.FX_Robot_Kine_FK_NSP(
            Serial, ctypes.byref(joints_double), ctypes.byref(pg), ctypes.byref(nspg)
        )
        if success1:
            fk_mat = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            for i in range(4):
                for j in range(4):
                    fk_mat[i][j] = pg[i][j]
            nsp_mat = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            for i in range(3):
                for j in range(3):
                    nsp_mat[i][j] = nspg[i][j]
            logger.info(f"fk_nsp result, matrix:{fk_mat}")
            logger.info(f"nsp matrix:{nsp_mat}")
            return (fk_mat, nsp_mat)
        else:
            return False

    def ik(self, structure_data):
        """Solve inverse kinematics in place using FX_InvKineSolvePara. Return the same parameter object or False."""
        Serial = ctypes.c_int32(self.robot_tag)
        self.sp = structure_data
        success = self.kine.FX_Robot_Kine_IK(Serial, byref(self.sp))
        if not success:
            logger.error("Robot Inverse Kinematics Error")
            if self.sp.m_Output_IsOutRange == 1:
                logger.info(f"IK m_Output_IsOutRange:{self.sp.m_Output_IsOutRange}")
                logger.info("Robot Inverse Kinematics excess!")
            if self.sp.m_Output_IsDeg[3] == 1:
                logger.info(f"IK Joint4 m_Output_IsDeg:{self.sp.m_Output_IsDeg[3]}")
                logger.info("Robot Inverse Kinematics Degen!")
            return False
        else:
            logger.info("Robot Inverse Kinematics success")
            logger.info(f"ik result numbers :{self.sp.m_OutPut_Result_Num}")
            logger.info(
                f"ik joints(close to reference joints):{self.sp.m_Output_RetJoint.to_list()}"
            )
            all_joint_list = self.sp.m_OutPut_AllJoint.to_list()
            all_joint_8x8 = convert_to_8x8_matrix(all_joint_list)
            logger.info(f"all ik joints:{all_joint_8x8}")
            return self.sp

    def mat4x4_to_mat1x16(self, pose_mat):
        """Flatten a 4x4 transform in row-major order for an inverse-kinematics target."""
        matrix_data = []
        for i in range(4):
            for j in range(4):
                matrix_data.append(pose_mat[i][j])
        return matrix_data

    def ik_nsp(self, sturcture_data):
        """Refine an inverse-kinematics solution with null-space constraints. Return the parameter object or False."""
        Serial = ctypes.c_int32(self.robot_tag)
        self.sp = sturcture_data
        success = self.kine.FX_Robot_Kine_IK_NSP(Serial, byref(self.sp))
        if not success:
            logger.error("Robot Inverse Kinematics NSP Error")
            return False
        else:
            logger.info("Robot Inverse Kinematics NSP Success")
            logger.info(f"ik joints:{self.sp.m_Output_RetJoint.to_list()}")
            return self.sp

    def joints2JacobMatrix(self, joints: list):
        """Return the 6x7 geometric Jacobian for seven joint angles in degrees. Linear rows use metres per radian."""
        if len(joints) != 7:
            raise ValueError("joints must be (7,)")
        Serial = ctypes.c_int32(self.robot_tag)
        joints_value = (ctypes.c_double * 7)(*joints)
        example_matrix = [
            [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        ]
        self.jacobi.set_jcb(example_matrix)
        success = self.kine.FX_Robot_Kine_Jacb(Serial, joints_value, byref(self.jacobi))
        if not success:
            logger.error("Joints2Jacobi Error")
            return False
        else:
            logger.info("Joints2Jacobi Success")
            logger.info(f"Jacobi matrix:{self.jacobi.get_jcb()}")
            return self.jacobi.get_jcb()

    def mat4x4_to_xyzabc(self, pose_mat: list):
        """Convert a 4x4 homogeneous transform to XYZABC, using millimetres and degrees."""
        if len(pose_mat) != 4:
            raise ValueError("pose_mat  must be 4 rows")
        else:
            for i in range(len(pose_mat)):
                if len(pose_mat[i]) != 4:
                    raise ValueError("pose_mat  must be 4 columns")
        matrix_data = (c_double * 4 * 4)()
        for i in range(4):
            for j in range(4):
                matrix_data[i][j] = pose_mat[i][j]
        xyzabc = (c_double * 6)(0, 0, 0, 0, 0, 0)
        success = self.kine.FX_Matrix42XYZABCDEG(matrix_data, xyzabc)
        if not success:
            logger.error("Pose mat to xyzabc Error")
            return False
        else:
            logger.info("Pose mat to xyzabc Success")
            pose_6d = [xyzabc[i] for i in range(6)]
            logger.info(f"xyzabc:{pose_6d}")
            return pose_6d

    def xyzabc_to_mat4x4(self, xyzabc: list):
        """Convert six XYZABC values in millimetres/degrees to a 4x4 homogeneous transform."""
        if len(xyzabc) != 6:
            raise ValueError("length of xyzabc must be 6")
        joints_double = (ctypes.c_double * 6)(*xyzabc)
        Matrix4x4 = ctypes.c_double * 4 * 4
        pg = Matrix4x4()
        for i in range(4):
            for j in range(4):
                pg[i][j] = 1.0 if i == j else 0.0
        self.kine.FX_XYZABC2Matrix4DEG(ctypes.byref(joints_double), ctypes.byref(pg))
        fk_mat = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        for i in range(4):
            for j in range(4):
                fk_mat[i][j] = pg[i][j]
        if not fk_mat:
            logger.error("xyzabc to mat4x4 Error")
            return False
        else:
            logger.info("xyzabc to mat4x4 Success")
            return fk_mat

    def calculate_end_xyzabc(
        self, start_xyzabc: list, pose_offset: list, rot_type: int, angle_param: list
    ):
        """Apply a three-dimensional translation and the selected SDK rotation convention to a six-element XYZABC pose."""
        if len(start_xyzabc) != 6:
            raise ValueError("start_xyzabc must be (6,)")
        if len(pose_offset) != 3:
            raise ValueError("pose_offset must be (3,)")
        if len(angle_param) != 3:
            raise ValueError("angle_param must be (3,)")
        if type(rot_type) != int:
            raise ValueError("rot_type must be (3,)")
        start = (ctypes.c_double * 6)(*start_xyzabc)
        pose_off = (ctypes.c_double * 3)(*pose_offset)
        angle0, angle1, angle2 = angle_param
        angle = (ctypes.c_double * 3)(angle0, angle1, angle2)
        rot = ctypes.c_int32(rot_type)
        end_xyzabc = (c_double * 6)(0, 0, 0, 0, 0, 0)
        success = self.kine.FX_Robot_CalEndXYZABC(
            start, pose_off, rot, angle, end_xyzabc
        )
        if not success:
            logger.error("get end_xyzabc Error")
            return False
        else:
            logger.info("get end_xyzabc Success")
            pose_6d = [end_xyzabc[i] for i in range(6)]
            logger.info(f"end_xyzabc:{pose_6d}")
            return pose_6d

    def movL(
        self,
        start_xyzabc: list,
        end_xyzabc: list,
        ref_joints: list,
        vel: float,
        acc: float,
        freq_hz: int,
        save_path,
    ):
        """Plan a Cartesian straight line and save its PVT file. Poses use mm/degrees; velocity and acceleration use mm/s and mm/s squared."""
        Serial = ctypes.c_int32(self.robot_tag)
        freq = ctypes.c_int32(freq_hz)
        path = save_path.encode("utf-8")
        path_char = ctypes.c_char_p(path)
        start = (ctypes.c_double * 6)(*start_xyzabc)
        end = (ctypes.c_double * 6)(*end_xyzabc)
        vel_value = c_double(vel)
        acc_value = c_double(acc)
        joints_vel_value = (c_double * 7)(*ref_joints)
        success1 = self.kine.FX_Robot_PLN_MOVL(
            Serial, start, end, joints_vel_value, vel_value, acc_value, freq, path_char
        )
        if success1:
            if os.path.exists(save_path):
                logger.info(f"Plan MOVL successful, PATH saved as :{save_path}")
                return True
        else:
            logger.error(f"Plan MOVL failed!")
            return False

    def movLA(
        self,
        start_xyzabc: List[float],
        end_xyzabc: List[float],
        ref_joints: List[float],
        vel: float,
        acc: float,
        freq_hz: int,
        dimension: int = 7,
    ) -> tuple[List[List[float]], ctypes.c_void_p]:
        """Plan a Cartesian straight line and return (point_lists, owned_point_set). On failure return ([], None)."""
        Serial = ctypes.c_int32(self.robot_tag)
        freq = ctypes.c_int32(freq_hz)
        if len(start_xyzabc) != 6:
            raise ValueError("start_xyzabc must have 6 elements")
        start_array = (ctypes.c_double * 6)(*start_xyzabc)
        if len(end_xyzabc) != 6:
            raise ValueError("end_xyzabc must have 6 elements")
        end_array = (ctypes.c_double * 6)(*end_xyzabc)
        if len(ref_joints) != 7:
            raise ValueError("ref_joints must have 7 elements")
        joints_array = (ctypes.c_double * 7)(*ref_joints)
        vel_arr = ctypes.c_double(vel)
        acc_arr = ctypes.c_double(acc)
        pset = self.create_point_set(dimension)
        if not pset:
            raise RuntimeError("Failed to create CPointSet object")
        try:
            success = self.kine.FX_Robot_PLN_MOVLA_C(
                Serial,
                start_array,
                end_array,
                joints_array,
                vel_arr,
                acc_arr,
                freq,
                pset,
            )
            if not success:
                self.destroy_point_set(pset)
                return ([], None)
            data = self.get_point_set_data(pset, dimension)
            print(f"Plan MOVLA successful, got {len(data)} points")
            return (data, pset)
        except Exception as e:
            self.destroy_point_set(pset)
            raise e

    def movL_KeepJ(
        self,
        start_joints: list,
        end_joints: list,
        vel: float,
        acc: float,
        freq_hz: int,
        save_path,
    ) -> bool:
        """Plan a Cartesian straight line constrained by start/end joint configurations and save its PVT file."""
        Serial = ctypes.c_int32(self.robot_tag)
        freq = ctypes.c_int32(freq_hz)
        path = save_path.encode("utf-8")
        path_char = ctypes.c_char_p(path)
        start_array = (ctypes.c_double * 7)(*start_joints)
        end_array = (ctypes.c_double * 7)(*end_joints)
        vel_value = ctypes.c_double(vel)
        acc_value = ctypes.c_double(acc)
        success = self.kine.FX_Robot_PLN_MOVL_KeepJ(
            Serial, start_array, end_array, vel_value, acc_value, freq, path_char
        )
        if success:
            if os.path.exists(save_path):
                logger.info(f"Plan MOVL KeepJ successful, PATH saved as :{save_path}")
                return True
        else:
            logger.error(f"Plan MOVL KeepJ failed!")
            return False

    def movL_KeepJA(
        self,
        start_joints: List[float],
        end_joints: List[float],
        vel: float,
        acc: float,
        freq_hz: int,
        dimension: int = 7,
    ) -> tuple[List[List[float]], ctypes.c_void_p]:
        """Plan a joint-configuration-constrained Cartesian line and return (point_lists, owned_point_set)."""
        Serial = ctypes.c_int32(self.robot_tag)
        freq = ctypes.c_int32(freq_hz)
        start_array = (ctypes.c_double * 7)(*start_joints)
        end_array = (ctypes.c_double * 7)(*end_joints)
        vel_arr = c_double(vel)
        acc_arr = c_double(acc)
        pset = self.create_point_set(dimension)
        if not pset:
            raise RuntimeError("Failed to create CPointSet object")
        try:
            success = self.kine.FX_Robot_PLN_MOVL_KeepJA_C(
                Serial, start_array, end_array, vel_arr, acc_arr, freq, pset
            )
            if not success:
                self.destroy_point_set(pset)
                return ([], None)
            data = self.get_point_set_data(pset, dimension)
            print(f"Plan movL_KeepJA successful, got {len(data)} points")
            return (data, pset)
        except Exception as e:
            self.destroy_point_set(pset)
            raise e

    def mov_target(
        self,
        start_xyzabc: List[float],
        end_xyzabc: List[float],
        ref_joints: List[float],
        vel: float,
        acc: float,
        freq_hz: int,
        dimension: int = 7,
    ) -> tuple[List[List[float]], ctypes.c_void_p]:
        """Plan to a target Cartesian pose and return (point_lists, owned_point_set)."""
        if len(start_xyzabc) != 6 or len(end_xyzabc) != 6 or len(ref_joints) != 7:
            raise ValueError(
                "start_xyzabc and end_xyzabc must have 6 elements, ref_joints must have 7 elements"
            )
        serial = ctypes.c_int32(self.robot_tag)
        freq = ctypes.c_int32(freq_hz)
        start_arr = (ctypes.c_double * 6)(*start_xyzabc)
        end_arr = (ctypes.c_double * 6)(*end_xyzabc)
        ref_arr = (ctypes.c_double * 7)(*ref_joints)
        vel_val = ctypes.c_double(vel)
        acc_val = ctypes.c_double(acc)
        pset = self.create_point_set(dimension)
        if not pset:
            raise RuntimeError("Failed to create CPointSet object")
        try:
            success = self.kine.FX_Robot_PLN_MOV_Target_C(
                serial, start_arr, end_arr, ref_arr, vel_val, acc_val, freq, pset
            )
            if not success:
                self.destroy_point_set(pset)
                return ([], None)
            data = self.get_point_set_data(pset, dimension)
            print(f"Plan MOV_TargetA successful, got {len(data)} points")
            return (data, pset)
        except Exception as e:
            self.destroy_point_set(pset)
            raise e

    def movL_synchronous(
        self, aspp: "ArmsSynchronousPlanningParams", dimension: int = 7
    ) -> tuple[List[List[float]], ctypes.c_void_p, List[List[float]], ctypes.c_void_p]:
        """Plan synchronized dual-arm Cartesian motion. Return (left_data, left_points, right_data, right_points)."""
        if not hasattr(self.kine, "FX_Robot_PLN_MOVL_Arms_Synchronous"):
            raise RuntimeError(
                "FX_Robot_PLN_MOVL_Arms_Synchronous is not exported by current libKine"
            )
        if isinstance(aspp, dict):
            aspp = ArmsSynchronousPlanningParams(**aspp)
        if not isinstance(aspp, ArmsSynchronousPlanningParams):
            raise TypeError("aspp must be an ArmsSynchronousPlanningParams or dict")
        pset_arm0 = self.create_point_set(dimension)
        pset_arm1 = self.create_point_set(dimension)
        if not pset_arm0 or not pset_arm1:
            self.destroy_point_set(pset_arm0)
            self.destroy_point_set(pset_arm1)
            raise RuntimeError("Failed to create CPointSet object")
        try:
            success = self.kine.FX_Robot_PLN_MOVL_Arms_Synchronous(
                ctypes.byref(aspp), pset_arm0, pset_arm1
            )
            if not success:
                self.destroy_point_set(pset_arm0)
                self.destroy_point_set(pset_arm1)
                return ([], None, [], None)
            data_arm0 = self.get_point_set_data(pset_arm0, dimension)
            data_arm1 = self.get_point_set_data(pset_arm1, dimension)
            logger.info(
                f"Plan MOVL arms synchronous successful, got {len(data_arm0)} and {len(data_arm1)} points"
            )
            return (data_arm0, pset_arm0, data_arm1, pset_arm1)
        except Exception as e:
            self.destroy_point_set(pset_arm0)
            self.destroy_point_set(pset_arm1)
            raise e

    def multi_movL_set_start(
        self,
        ref_joints: List[float],
        start_xyzabc: List[float],
        end_xyzabc: List[float],
        allow_range: float,
        zsp_type: int,
        zsp_para: List[float],
        vel: float,
        acc: float,
        freq: int,
    ) -> bool:
        """Initialize a multipoint Cartesian plan with start/end poses, reference joints, tolerance and null-space parameters."""
        if len(ref_joints) != 7:
            raise ValueError(f"ref_joints must have 7 elements, got {len(ref_joints)}")
        if len(start_xyzabc) != 6:
            raise ValueError(
                f"start_xyzabc must have 6 elements, got {len(start_xyzabc)}"
            )
        if len(end_xyzabc) != 6:
            raise ValueError(f"end_xyzabc must have 6 elements, got {len(end_xyzabc)}")
        if len(zsp_para) != 6:
            raise ValueError(f"zsp_para must have 6 elements, got {len(zsp_para)}")
        serial = ctypes.c_int32(self.robot_tag)
        ref_arr = (ctypes.c_double * 7)(*ref_joints)
        start_arr = (ctypes.c_double * 6)(*start_xyzabc)
        end_arr = (ctypes.c_double * 6)(*end_xyzabc)
        allow_val = ctypes.c_double(allow_range)
        zsp_type_val = ctypes.c_int32(zsp_type)
        zsp_arr = (ctypes.c_double * 6)(*zsp_para)
        vel_val = ctypes.c_double(vel)
        acc_val = ctypes.c_double(acc)
        freq_val = ctypes.c_int32(freq)
        result = self.kine.FX_Robot_PLN_Set_MOVL_Start(
            serial,
            ref_arr,
            start_arr,
            end_arr,
            allow_val,
            zsp_type_val,
            zsp_arr,
            vel_val,
            acc_val,
            freq_val,
        )
        return result

    def multi_movL_next_point(
        self,
        next_xyzabc: List[float],
        allow_range: float,
        zsp_type: int,
        zsp_para: List[float],
        vel: float,
        acc: float,
    ) -> bool:
        """Append the next pose, tolerance, null-space constraints, velocity and acceleration to a multipoint plan."""
        serial = ctypes.c_int32(self.robot_tag)
        next_arr = (ctypes.c_double * 6)(*next_xyzabc)
        zsp_arr = (ctypes.c_double * 6)(*zsp_para)
        zsp_type_arr = ctypes.c_int32(zsp_type)
        allow_range_arr = ctypes.c_double(allow_range)
        vel_arr = ctypes.c_double(vel)
        acc_var = ctypes.c_double(acc)
        success = self.kine.FX_Robot_PLN_Set_MOVL_Next_Point(
            serial, next_arr, allow_range_arr, zsp_type_arr, zsp_arr, vel_arr, acc_var
        )
        return success

    def multi_movL_get_points(
        self, dimension: int = 7
    ) -> tuple[List[List[float]], ctypes.c_void_p]:
        """Fetch a multipoint Cartesian plan as (point_lists, owned_point_set)."""
        serial = ctypes.c_int32(self.robot_tag)
        pset = self.create_point_set(dimension)
        if not pset:
            raise RuntimeError("Failed to create point set object")
        success = self.kine.FX_Robot_PLN_Get_MOVL_Path_C(serial, pset)
        if success:
            data = self.get_point_set_data(pset, dimension)
            print(f"Get MOVL path successful, got {len(data)} points")
            return (data, pset)
        else:
            self.destroy_point_set(pset)
            print("Get MOVL path failed!")
            return ([], None)

    def identify_tool_dyn(self, robot_type: int, ipath: str):
        """Identify tool dynamics from recorded data for type 1 (CCS) or 2 (SRS). Return ten dynamic parameters or the official error text."""
        if type(robot_type) != int:
            raise ValueError("robot_type must be int type")
        if not os.path.exists(ipath):
            raise ValueError(f"no {ipath}, pls check!")
        if robot_type == 1:
            print(f"CCS tool identy")
        elif robot_type == 2:
            print(f"SRS tool identy")
        robot_type_ = c_int(robot_type)
        iden_path = ipath.encode("utf-8")
        path_char = ctypes.c_char_p(iden_path)
        mm_ptr = c_double(0)
        mcp_ptr = (c_double * 3)()
        ii_ptr = (c_double * 6)()
        ret_int = self.kine.FX_Robot_Iden_LoadDyn(
            robot_type_, path_char, mm_ptr, mcp_ptr, ii_ptr
        )
        if ret_int == 0:
            logger.info("Identify tool dynamics successful")
            dyn_para = []
            m_val = mm_ptr.value
            mcp_list = [mcp_ptr[i] for i in range(3)]
            ii_list = [ii_ptr[i] for i in range(6)]
            "ixx iyy izz ixy ixz iyz"
            dyn_para.append(m_val)
            for i in mcp_list:
                dyn_para.append(i)
            dyn_para.append(ii_list[0])
            dyn_para.append(ii_list[3])
            dyn_para.append(ii_list[4])
            dyn_para.append(ii_list[1])
            dyn_para.append(ii_list[5])
            dyn_para.append(ii_list[2])
            logger.info(
                f"tool dynamics[m,mx,my,mz,ixx,ixy,ixz,iyy,iyz,izz]: {dyn_para}"
            )
            return dyn_para
        else:
            logger.error("Identify tool dynamics failed!")
            logger.error(
                f"identify_tool_dyn 返回错误码:{ret_int}\n ret=1, 计算错误，需重新采集数据计算\n ret=2,打开采集数据文件错误，须检查采样文件\n ret=3,配置文件被修改\n ret=4, 采集时间不够，缺少有效数据"
            )
            if ret_int == 1:
                return "ret=1, 计算错误，需重新采集数据计算"
            elif ret_int == 2:
                return "ret=2,打开采集数据文件错误，须检查采样文件"
            elif ret_int == 3:
                return "ret=3,配置文件被修改"
            elif ret_int == 4:
                return "ret=4, 采集时间不够，缺少有效数据"

    def identify_tool_dyn_m20(self, ipath_ini: str, robot_type: int, ipath: str):
        """Identify M20 tool dynamics using an INI configuration and recorded data. Return ten parameters or the official error text."""
        if type(robot_type) != int:
            raise ValueError("robot_type must be int type")
        if not os.path.exists(ipath_ini):
            raise ValueError(f"no {ipath_ini}, pls check!")
        if not os.path.exists(ipath):
            raise ValueError(f"no {ipath}, pls check!")
        if robot_type == 1:
            print(f"CCS tool identy (M20)")
        elif robot_type == 2:
            print(f"SRS tool identy (M20)")
        ini_path_char = ctypes.c_char_p(ipath_ini.encode("utf-8"))
        robot_type_ = c_int(robot_type)
        iden_path = ipath.encode("utf-8")
        path_char = ctypes.c_char_p(iden_path)
        mm_ptr = c_double(0)
        mcp_ptr = (c_double * 3)()
        ii_ptr = (c_double * 6)()
        ret_int = self.kine.FX_Robot_Iden_LoadDyn_M20(
            ini_path_char, robot_type_, path_char, mm_ptr, mcp_ptr, ii_ptr
        )
        if ret_int == 0:
            logger.info("Identify tool dynamics successful (M20)")
            dyn_para = []
            m_val = mm_ptr.value
            mcp_list = [mcp_ptr[i] for i in range(3)]
            ii_list = [ii_ptr[i] for i in range(6)]
            "ixx iyy izz ixy ixz iyz"
            dyn_para.append(m_val)
            for i in mcp_list:
                dyn_para.append(i)
            dyn_para.append(ii_list[0])
            dyn_para.append(ii_list[3])
            dyn_para.append(ii_list[4])
            dyn_para.append(ii_list[1])
            dyn_para.append(ii_list[5])
            dyn_para.append(ii_list[2])
            logger.info(
                f"tool dynamics[m,mx,my,mz,ixx,ixy,ixz,iyy,iyz,izz]: {dyn_para}"
            )
            return dyn_para
        else:
            logger.error("Identify tool dynamics failed! (M20)")
            logger.error(
                f"identify_tool_dyn_m20 返回错误码:{ret_int}\n ret=1, 计算错误，需重新采集数据计算\n ret=2,打开采集数据文件错误，须检查采样文件\n ret=3,配置文件被修改\n ret=4, 采集时间不够，缺少有效数据"
            )
            if ret_int == 1:
                return "ret=1, 计算错误，需重新采集数据计算"
            elif ret_int == 2:
                return "ret=2,打开采集数据文件错误，须检查采样文件"
            elif ret_int == 3:
                return "ret=3,配置文件被修改"
            elif ret_int == 4:
                return "ret=4, 采集时间不够，缺少有效数据"

    def jnt_tau_to_ee_tau(self, q: list, joint_torque: list):
        """Map seven joint torques in N m to six end-effector force/torque components at the given joint angles."""
        if len(q) != 7:
            raise ValueError("q must be (7,)")
        if len(joint_torque) != 7:
            raise ValueError("joint_torque must be (7,)")
        Serial = ctypes.c_int32(self.robot_tag)
        q_arr = (ctypes.c_double * 7)(*q)
        tau_arr = (ctypes.c_double * 7)(*joint_torque)
        ee_tau_arr = (ctypes.c_double * 6)(0, 0, 0, 0, 0, 0)
        if not hasattr(self.kine, "FX_Robot_JntTau2EETau"):
            logger.error(
                "FX_Robot_JntTau2EETau not found in libKine, please update libKine.dll/.so"
            )
            return False
        success = self.kine.FX_Robot_JntTau2EETau(Serial, q_arr, tau_arr, ee_tau_arr)
        if not success:
            logger.error("JntTau to EETau Error")
            return False
        else:
            ee_tau = [ee_tau_arr[i] for i in range(6)]
            logger.info(f"JntTau to EETau Success, EE_Torque:{ee_tau}")
            return ee_tau

    def cal_ee_linear_vel(self, joints: list, angvel: list):
        """Return TCP linear speed in mm/s from seven joint angles and angular rates in degrees and degrees/s."""
        if len(joints) != 7:
            raise ValueError("joints must be (7,)")
        if len(angvel) != 7:
            raise ValueError("angvel must be (7,)")
        Serial = ctypes.c_int32(self.robot_tag)
        joints_arr = (ctypes.c_double * 7)(*joints)
        angvel_arr = (ctypes.c_double * 7)(*angvel)
        if not hasattr(self.kine, "FX_Robot_CalEELinerVel"):
            logger.error(
                "FX_Robot_CalEELinerVel not found in libKine, please update libKine.dll/.so"
            )
            return None
        ee_vel = self.kine.FX_Robot_CalEELinerVel(Serial, joints_arr, angvel_arr)
        logger.info(f"CalEE Linear Velocity: {ee_vel}")
        return ee_vel


def convert_to_8x8_matrix(flat_list):
    """Reshape a 64-value flat solution array into eight columns, omitting all-zero rows as in the official helper."""
    if len(flat_list) != 64:
        raise ValueError("列表必须有64个元素")
    matrix_8x8 = []
    for i in range(8):
        row_start = i * 8
        row_end = row_start + 8
        row = flat_list[row_start:row_end]
        if not all((abs(val) < 1e-10 for val in row)):
            matrix_8x8.append(row)
    return matrix_8x8


FX_INT32L = c_int32
FX_DOUBLE = c_double
FX_BOOL = c_bool


class Vect7(Structure):
    """Seven double-precision numeric values with a flat-list conversion helper."""

    _fields_ = [("data", FX_DOUBLE * 7)]

    def __init__(self, values=None):
        """Create this interface or value record without opening a robot connection."""
        super().__init__()
        if values is not None:
            if len(values) != 7:
                raise ValueError("Vect7 requires exactly 7 values")
            for i, val in enumerate(values):
                self.data[i] = val

    def to_list(self):
        """Return a copy of the record's flat numeric values as a Python list."""
        return [self.data[i] for i in range(7)]

    def __str__(self):
        """Return a readable text representation of this value record."""
        return str(self.to_list())


class Matrix4(Structure):
    """A 4x4 double-precision matrix stored as sixteen row-major values."""

    _fields_ = [("data", FX_DOUBLE * 16)]

    def __init__(self, values=None):
        """Create this interface or value record without opening a robot connection."""
        super().__init__()
        if values is not None:
            if len(values) != 16:
                raise ValueError("Matrix4 requires exactly 16 values")
            for i, val in enumerate(values):
                self.data[i] = val

    def to_list(self):
        """Return a copy of the record's flat numeric values as a Python list."""
        return [self.data[i] for i in range(16)]

    def __str__(self):
        """Return a readable text representation of this value record."""
        return str(self.to_list())


class Matrix8(Structure):
    """An 8x8 double-precision matrix stored as sixty-four row-major values."""

    _fields_ = [("data", FX_DOUBLE * 64)]

    def __init__(self, values=None):
        """Create this interface or value record without opening a robot connection."""
        super().__init__()
        if values is not None:
            if len(values) != 64:
                raise ValueError("Matrix8 requires exactly 64 values")
            for i, val in enumerate(values):
                self.data[i] = val

    def to_list(self):
        """Return a copy of the record's flat numeric values as a Python list."""
        return [self.data[i] for i in range(64)]

    def __str__(self):
        """Return a readable text representation of this value record."""
        return str(self.to_list())


class ArmsSynchronousPlanningParams(Structure):
    """Dual-arm synchronous planning parameters. Set both arm poses, reference joints, frequency, velocity, acceleration and coordinate-frame flag."""

    _fields_ = [
        ("Skye_Body_Start_PRR", FX_DOUBLE * 3),
        ("Arm0_Start_XYZABC", FX_DOUBLE * 6),
        ("Arm0_End_XYZABC", FX_DOUBLE * 6),
        ("Arm0_Ref_Joints", FX_DOUBLE * 7),
        ("Arm0_ZSP_Type", FX_INT32L),
        ("Arm0_ZSP_Para", FX_DOUBLE * 6),
        ("Arm1_Start_XYZABC", FX_DOUBLE * 6),
        ("Arm1_End_XYZABC", FX_DOUBLE * 6),
        ("Arm1_Ref_Joints", FX_DOUBLE * 7),
        ("Arm1_ZSP_Type", FX_INT32L),
        ("Arm1_ZSP_Para", FX_DOUBLE * 6),
        ("Freq", FX_INT32L),
        ("Vel", FX_DOUBLE),
        ("Acc", FX_DOUBLE),
        ("Sync_Type", FX_INT32L),
        ("World_Co_Flag", FX_BOOL),
    ]

    def __init__(self, **kwargs):
        """Create this interface or value record without opening a robot connection."""
        super().__init__()
        ctypes.memset(ctypes.byref(self), 0, ctypes.sizeof(self))
        field_types = dict(self._fields_)
        for key, value in kwargs.items():
            if key not in field_types:
                raise ValueError(
                    f"unknown field for ArmsSynchronousPlanningParams: {key}"
                )
            field_type = field_types[key]
            if isinstance(field_type, type) and issubclass(field_type, ctypes.Array):
                if len(value) != field_type._length_:
                    raise ValueError(
                        f"{key} requires exactly {field_type._length_} values"
                    )
                setattr(self, key, field_type(*value))
            else:
                setattr(self, key, value)


class FX_InvKineSolvePara(ctypes.Structure):
    """Inverse-kinematics inputs and outputs, including target transform, reference joints, null-space parameters and solution diagnostics."""

    _fields_ = [
        ("m_Input_IK_TargetTCP", Matrix4),
        ("m_Input_IK_RefJoint", Vect7),
        ("m_Input_IK_ZSPType", FX_INT32L),
        ("m_Input_IK_ZSPPara", FX_DOUBLE * 6),
        ("m_Input_ZSP_Angle", FX_DOUBLE),
        ("m_DGR1", FX_DOUBLE),
        ("m_DGR2", FX_DOUBLE),
        ("m_DGR3", FX_DOUBLE),
        ("m_Output_RetJoint", Vect7),
        ("m_OutPut_AllJoint", Matrix8),
        ("m_OutPut_Result_Num", FX_INT32L),
        ("m_Output_IsOutRange", FX_BOOL),
        ("m_Output_IsDeg", FX_BOOL * 7),
        ("m_Output_JntExdTags", FX_BOOL * 7),
        ("m_Output_JntExdABS", FX_DOUBLE),
        ("m_Output_IsJntExd", FX_BOOL),
        ("m_Output_RunLmtP", Vect7),
        ("m_Output_RunLmtN", Vect7),
    ]

    def __init__(self):
        """Create this interface or value record without opening a robot connection."""
        super().__init__()
        for i in range(6):
            self.m_Input_IK_ZSPPara[i] = 0.0
        for i in range(7):
            self.m_Output_IsDeg[i] = False
            self.m_Output_JntExdTags[i] = False
        self.m_OutPut_Result_Num = 0
        self.m_Output_JntExdABS = 0.0
        self.m_Output_IsJntExd = False
        self.m_Output_IsOutRange = False

    def set_input_ik_target_tcp(self, matrix):
        """Set the target TCP transform (16 row-major values)."""
        if len(matrix) != 16:
            raise ValueError(
                "m_Input_IK_TargetTCP requires exactly 16 values for 4x4 matrix"
            )
        for i, val in enumerate(matrix):
            self.m_Input_IK_TargetTCP.data[i] = val

    def set_input_ik_ref_joint(self, values):
        """Set the seven reference joint angles in degrees."""
        if len(values) != 7:
            raise ValueError("m_Input_IK_RefJoint requires exactly 7 values")
        for i, val in enumerate(values):
            self.m_Input_IK_RefJoint.data[i] = val

    def set_input_ik_zsp_type(self, value):
        """Set the null-space optimization type."""
        self.m_Input_IK_ZSPType = value

    def set_input_ik_zsp_para(self, values):
        """Set the six null-space optimization parameters."""
        if len(values) != 6:
            raise ValueError("m_Input_IK_ZSPPara requires exactly 6 values")
        for i, val in enumerate(values):
            self.m_Input_IK_ZSPPara[i] = val

    def set_input_zsp_angle(self, value):
        """Set the null-space arm angle in degrees."""
        self.m_Input_ZSP_Angle = value

    def set_dgr1(self, value):
        """Set the joint-2 singularity tolerance in degrees."""
        self.m_DGR1 = value

    def set_dgr2(self, value):
        """Set the joint-6 singularity tolerance in degrees."""
        self.m_DGR2 = value

    def set_dgr3(self, value):
        """Set the reserved singularity parameter."""
        self.m_DGR3 = value

    def set_all_inputs(self, **kwargs):
        """Set named inverse-kinematics inputs, rejecting unknown names."""
        setters = {
            "target_tcp": self.set_input_ik_target_tcp,
            "ref_joint": self.set_input_ik_ref_joint,
            "zsp_type": self.set_input_ik_zsp_type,
            "zsp_para": self.set_input_ik_zsp_para,
            "zsp_angle": self.set_input_zsp_angle,
            "dgr1": self.set_dgr1,
            "dgr2": self.set_dgr2,
            "dgr3": self.set_dgr3,
        }
        for key, value in kwargs.items():
            if key in setters:
                setters[key](value)
            else:
                raise ValueError(f"Unknown input parameter: {key}")

    def get_output_ret_joint(self):
        """Return the seven selected solution joint angles in degrees."""
        return [self.m_Output_RetJoint.data[i] for i in range(7)]

    def get_output_all_joint(self):
        """Return all candidate joint solutions as a flat 64-value list."""
        return [self.m_OutPut_AllJoint.data[i] for i in range(64)]

    def get_output_result_num(self):
        """Return the number of inverse-kinematics solutions."""
        return self.m_OutPut_Result_Num

    def get_output_is_out_range(self):
        """Return the target-out-of-reach flag."""
        return self.m_Output_IsOutRange

    def get_output_is_deg(self):
        """Return the seven joint-singularity flags."""
        return [self.m_Output_IsDeg[i] for i in range(7)]

    def get_output_jnt_exd_tags(self):
        """Return the seven joint-limit violation flags."""
        return [self.m_Output_JntExdTags[i] for i in range(7)]

    def get_output_jnt_exd_abs(self):
        """Return the maximum absolute joint-limit violation."""
        return self.m_Output_JntExdABS

    def get_output_is_jnt_exd(self):
        """Return the joint-limit violation flag."""
        return self.m_Output_IsJntExd

    def get_output_run_lmt_positive(self):
        """Return the seven positive running joint limits."""
        return [self.m_Output_RunLmtP.data[i] for i in range(7)]

    def get_output_run_lmt_negative(self):
        """Return the seven negative running joint limits."""
        return [self.m_Output_RunLmtN.data[i] for i in range(7)]

    def get_all_outputs(self):
        """Return all inverse-kinematics result fields as a dictionary."""
        return {
            "ret_joint": self.get_output_ret_joint(),
            "all_joint": self.get_output_all_joint(),
            "result_num": self.get_output_result_num(),
            "is_out_range": self.get_output_is_out_range(),
            "is_deg": self.get_output_is_deg(),
            "jnt_exd_tags": self.get_output_jnt_exd_tags(),
            "jnt_exd_abs": self.get_output_jnt_exd_abs(),
            "is_jnt_exd": self.get_output_is_jnt_exd(),
            "run_lmt_positive": self.get_output_run_lmt_positive(),
            "run_lmt_negative": self.get_output_run_lmt_negative(),
        }

    def set_output_jnt_exd_tags(self, values):
        """Set the seven joint-limit violation flags."""
        if len(values) != 7:
            raise ValueError("m_Output_JntExdTags requires exactly 7 values")
        for i, val in enumerate(values):
            self.m_Output_JntExdTags[i] = val

    def get_input_ik_zsp_para(self):
        """Return the six null-space optimization parameters."""
        return [self.m_Input_IK_ZSPPara[i] for i in range(6)]

    def __repr__(self):
        """Return a diagnostic text representation of the inverse-kinematics parameter record."""
        return f"FX_InvKineSolvePara:\n  输入: TCP={self.get_output_ret_joint()}, 参考关节={self.get_input_ik_zsp_para()}, ZSP类型={self.m_Input_IK_ZSPType}\n  输出: 结果数={self.m_OutPut_Result_Num}, 超限={self.m_Output_IsOutRange}"


class FX_Jacobi(Structure):
    """Six-by-seven geometric Jacobian record with an active-axis count."""

    _fields_ = [("m_AxisNum", FX_INT32L), ("m_Jcb", FX_DOUBLE * 7 * 6)]

    def __init__(self):
        """Create this interface or value record without opening a robot connection."""
        super().__init__()
        self.m_AxisNum = 0
        for i in range(6):
            row = self.m_Jcb[i]
            for j in range(7):
                row[j] = 0.0

    def set_jcb(self, matrix):
        """Set a 6x7 geometric Jacobian from nested numeric rows."""
        if len(matrix) != 6 or any((len(row) != 7 for row in matrix)):
            raise ValueError("雅可比矩阵必须是6x7的二维数组")
        for i in range(6):
            row = self.m_Jcb[i]
            for j in range(7):
                row[j] = matrix[i][j]

    def get_jcb(self):
        """Return the stored 6x7 geometric Jacobian as nested lists."""
        result = []
        for i in range(6):
            row = []
            for j in range(7):
                row.append(self.m_Jcb[i][j])
            result.append(row)
        return result

    def __str__(self):
        """Return a readable text representation of this value record."""
        result = f"AxisNum: {self.m_AxisNum}\nJacobian Matrix:\n"
        for i in range(6):
            row = [f"{self.m_Jcb[i][j]:.6f}" for j in range(7)]
            result += "  " + "  ".join(row) + "\n"
        return result


def inv_main():
    """Print an offline inverse-kinematics value-record construction example."""
    ik_params = FX_InvKineSolvePara()
    ik_params.m_Input_IK_ZSPType = 1
    ik_params.m_Input_ZSP_Angle = 45.0
    tcp_values = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    ik_params.m_Input_IK_TargetTCP = Matrix4(tcp_values)
    ref_joint = [0, 0.4, 0, 0, 0, 0, 0]
    ik_params.m_Input_IK_RefJoint = Vect7(ref_joint)
    ik_params.set_input_ik_zsp_para([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    print(f"FX_InvKineSolvePara size: {sizeof(ik_params)} bytes")
    print(f"Matrix8 size: {sizeof(Matrix8)} bytes")
