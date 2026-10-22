"""Official-compatible API; SDK calls use the nanobind extension.

Compatible with the official Marvin Python API; maintained with English docstrings.
"""

import ast
from ipaddress import IPv4Address
from . import _control as _native
import csv
import ctypes
import inspect
import os
import re
import time
from ctypes import *
from textwrap import dedent
from typing import Union, List

current_file_path = os.path.abspath(__file__)
current_path = os.path.dirname(current_file_path)


class Marvin_Robot:
    """Basic controller interface. Clear the command batch, set parameters, then send it. Instances share SDK state."""

    def __init__(self):
        """Create this interface or value record without opening a robot connection."""
        import sys

        self.robot = _native
        self.ErrorCode = None
        self.a_pvt_path = None
        self.b_pvt_path = None
        self.local_file_path = None
        self.remote_file_path = None
        self.save_csv_path = None
        self.save_data_path = None

    def _convert_ip(self, ip_str):
        """Validate an IPv4 address and return its four integer octets."""
        return tuple((int(part) for part in IPv4Address(ip_str).exploded.split(".")))

    def connect(self, robot_ip: str):
        """Connect to the controller at an IPv4 address. The concise interface also configures controller logging."""
        ip1, ip2, ip3, ip4 = self._convert_ip(robot_ip)
        return self.robot.OnLinkTo(ip1, ip2, ip3, ip4)

    def subscribe(self, dcss):
        """Fill a DCSS record and return its nested state dictionary. The concise interface returns None on failure."""
        self.robot.OnGetBuf(ctypes.byref(dcss))
        result = structure2dict(dcss)
        return result

    def check_error_and_clear(self, dcss):
        """Inspect arm and servo errors and request error clearing when necessary."""
        sub_data = self.subscribe(dcss)
        a_state = sub_data["states"][0]["cur_state"]
        b_state = sub_data["states"][1]["cur_state"]
        a_arm_err = sub_data["states"][0]["err_code"]
        b_arm_err = sub_data["states"][1]["err_code"]
        err_code_value_a = (ctypes.c_long * 7)()
        self.robot.OnGetServoErr_A(ctypes.byref(err_code_value_a))
        a_servo_err = [0] * 7
        err_code_value_b = (ctypes.c_long * 7)()
        self.robot.OnGetServoErr_B(ctypes.byref(err_code_value_b))
        b_servo_err = [0] * 7
        for i in range(7):
            a_servo_err[i] = err_code_value_a[i]
            b_servo_err[i] = err_code_value_b[i]
        if a_state == 100 or a_arm_err != 0:
            self.clear_error("A")
            print(f"Arm A exits error, clear error")
        elif b_state == 100 or b_arm_err != 0:
            self.clear_error("B")
            print(f"Arm B exits error, clear error")
        elif set(a_servo_err) != {0}:
            self.clear_error("A")
            print(f"Arm A exits servo error, clear error")
        elif set(b_servo_err) != {0}:
            self.clear_error("B")
            print(f"Arm B exits servo error, clear error")
        else:
            print(f"Arms A&B exist no error")

    def release_robot(self):
        """Release the shared controller connection. Repeated release before initialization is safe."""
        return self.robot.OnRelease()

    def SDK_version(self):
        """Return the version reported by the compiled control SDK."""
        return self.robot.OnGetSDKVersion()

    def check_sdk_type_compat(self):
        """Check C type sizes, pack(4) layout and byte order. Return the SDK status and byte-order indicator."""
        byte_order = ctypes.c_int(0)
        ret = self.robot.CheckSDKTypeCompat(ctypes.byref(byte_order))
        return (ret, byte_order.value)

    def update_SDK(self, sdk_path: str):
        """Upload a local controller system update package. Check the returned SDK status."""
        sdk_char = ctypes.c_char_p(sdk_path.encode("utf-8"))
        return self.robot.OnUpdateSystem(sdk_char)

    def download_sdk_log(self, log_path: str):
        """Download controller logs to the requested local path."""
        log_char = ctypes.c_char_p(log_path.encode("utf-8"))
        return self.robot.OnDownloadLog(log_char)

    def get_param(self, type: str, paraName: str):
        """Read an integer or floating-point parameter by its ASCII controller parameter name. Return (status, value)."""
        try:
            param_buf = (ctypes.c_char * 30)(*paraName.encode("ascii"), 0)
            if type == "float":
                result = ctypes.c_double(0)
                re_flag = self.robot.OnGetFloatPara(param_buf, ctypes.byref(result))
                return (re_flag, result.value)
            elif type == "int":
                result = ctypes.c_long(0)
                re_flag = self.robot.OnGetIntPara(param_buf, ctypes.byref(result))
                return (re_flag, result.value)
        except Exception as e:
            print("ERROR:", e)

    def save_para_file(self):
        """Save the current controller configuration parameters."""
        return self.robot.OnSavePara()

    def set_param(self, type: str, paraName: str, value: float):
        """Write an integer or floating-point controller parameter and return the SDK status."""
        try:
            param_buf = (ctypes.c_char * 30)(*paraName.encode("ascii"), 0)
            if type == "float":
                result = ctypes.c_double(value)
                return self.robot.OnSetFloatPara(param_buf, result)
            elif type == "int":
                result = ctypes.c_int(int(value))
                return self.robot.OnSetIntPara(param_buf, result)
        except Exception as e:
            print("ERROR:", e)

    def clear_set(self):
        """Clear the pending command batch before appending basic-interface commands."""
        return self.robot.OnClearSet()

    def send_cmd(self):
        """Send the pending basic-interface command batch to the controller."""
        return self.robot.OnSetSend()

    def send_cmd_wait_response(self, timeout: int):
        """Send the pending command batch and wait for a response using the SDK timeout in milliseconds."""
        timeout_long = ctypes.c_long(timeout)
        return self.robot.OnSetSendWaitResponse(timeout_long)

    def collect_data(self, targetNum: int, targetID: list[int], recordNum: int):
        """Start recording up to 35 telemetry fields identified by targetID. The identifier buffer is padded to 35 entries."""
        targetNum_int = ctypes.c_int(targetNum)
        targetID_int = (ctypes.c_long * 35)(*targetID)
        recordNum_int = ctypes.c_int(recordNum)
        return self.robot.OnStartGather(targetNum_int, targetID_int, recordNum_int)

    def stop_collect_data(self):
        """Stop recording controller telemetry."""
        return self.robot.OnStopGather()

    def save_collected_data_to_path(self, path: str):
        """Save recorded telemetry to a local data file."""
        self.save_data_path = path.encode("utf-8")
        path_char = ctypes.c_char_p(self.save_data_path)
        return self.robot.OnSaveGatherData(path_char)

    def save_collected_data_as_csv_to_path(self, path: str):
        """Save recorded telemetry to a local CSV file using the official conversion format."""
        path1 = "tmp.txt"
        self.save_data_path = path1.encode("utf-8")
        path_char = ctypes.c_char_p(self.save_data_path)
        self.robot.OnSaveGatherData(path_char)
        time.sleep(0.2)
        with open(path1, "r") as file:
            lines = file.readlines()
        processed_data = []
        lines = lines[1:]
        for i, line in enumerate(lines):
            parts = line.strip().split("$")
            numbers = []
            for part in parts:
                if part:
                    num_str = part.split()[-1]
                    numbers.append(num_str)
            if len(numbers) >= 2:
                numbers = numbers[2:]
            processed_data.append(numbers)
        try:
            with open(path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(processed_data)
            print(f"数据已成功保存到: {path}")
            if os.path.exists(path1):
                os.remove(path1)
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            if os.path.exists(path1):
                os.remove(path1)
            return False

    def soft_stop(self, arm: str):
        """Request a software emergency stop for arm A, B or both arms (AB)."""
        try:
            if arm == "A":
                return self.robot.OnEMG_A()
            elif arm == "B":
                return self.robot.OnEMG_B()
            elif arm == "AB":
                return self.robot.OnEMG_AB()
        except Exception as e:
            print("ERROR:", e)

    def servo_reset(self, arm: str, axis: int):
        """Reset the specified servo axis, numbered 0 through 6, on arm A or B."""
        try:
            axis_int = ctypes.c_int(axis)
            if arm == "A":
                return self.robot.OnServoReset_A(axis_int)
            elif arm == "B":
                return self.robot.OnServoReset_B(axis_int)
        except Exception as e:
            print("ERROR:", e)

    def get_servo_error_code(self, arm: str, lang="CN"):
        """Read servo fault codes and return their descriptions in the selected CN or EN language."""
        try:
            err_code_value = (ctypes.c_long * 7)()
            if arm == "A":
                self.robot.OnGetServoErr_A(ctypes.byref(err_code_value))
                err_code = [0] * 7
                for i in range(7):
                    err_code[i] = decimal_to_hex(err_code_value[i], prefix=True)
                err_code = get_fault_descriptions(err_code, lang)
                return err_code
            elif arm == "B":
                self.robot.OnGetServoErr_B(ctypes.byref(err_code_value))
                err_code = [0] * 7
                for i in range(7):
                    err_code[i] = decimal_to_hex(err_code_value[i], prefix=True)
                err_code = get_fault_descriptions(err_code, lang)
                return err_code
        except Exception as e:
            print("ERROR:", e)

    def clear_error(self, arm: str):
        """Append an error-clear command for arm A or B to the pending batch."""
        try:
            if arm == "A":
                return self.robot.OnClearErr_A()
            elif arm == "B":
                return self.robot.OnClearErr_B()
        except Exception as e:
            print(f"ERROR:{e}")

    def set_state(self, arm: str, state: int):
        """Set the target arm state: 0 disabled, 1 position, 2 PVT, 3 torque, or 4 cooperative release."""
        try:
            state_int = ctypes.c_int(state)
            if arm == "A":
                return self.robot.OnSetTargetState_A(state_int)
            elif arm == "B":
                return self.robot.OnSetTargetState_B(state_int)
        except Exception as e:
            print(f"ERROR:{e}")

    def set_impedance_type(self, arm: str, type: int):
        """Select joint (1), Cartesian (2) or force (3) impedance for arm A or B."""
        try:
            type_int = ctypes.c_int(type)
            if arm == "A":
                return self.robot.OnSetImpType_A(type_int)
            elif arm == "B":
                return self.robot.OnSetImpType_B(type_int)
        except Exception as e:
            print(f"ERROR:{e}")

    def set_vel_acc(self, arm: str, velRatio: int, AccRatio: int):
        """Set arm velocity and acceleration percentages. These limits do not constrain PVT playback or dragging."""
        try:
            velRatio_int = ctypes.c_int(velRatio)
            AccRatio_int = ctypes.c_int(AccRatio)
            if arm == "A":
                return self.robot.OnSetJointLmt_A(velRatio_int, AccRatio_int)
            elif arm == "B":
                return self.robot.OnSetJointLmt_B(velRatio_int, AccRatio_int)
        except Exception as e:
            print(f"ERROR:{e}")

    def set_tool(self, arm: str, kineParams: list, dynamicParams: list):
        """Set six tool kinematic parameters and ten tool dynamic parameters for the selected arm."""
        try:
            k0, k1, k2, k3, k4, k5 = kineParams
            d0, d1, d2, d3, d4, d5, d6, d7, d8, d9 = dynamicParams
            kp_double = ctypes.c_double * 6
            kineParams_value = kp_double(k0, k1, k2, k3, k4, k5)
            dp_double = ctypes.c_double * 10
            dynamicParams_value = dp_double(d0, d1, d2, d3, d4, d5, d6, d7, d8, d9)
            if arm == "A":
                return self.robot.OnSetTool_A(kineParams_value, dynamicParams_value)
            if arm == "B":
                return self.robot.OnSetTool_B(kineParams_value, dynamicParams_value)
        except Exception as e:
            print(f"ERROR:{e}")

    def set_joint_kd_params(self, arm: str, K: list, D: list):
        """Set seven joint stiffness values K and seven damping values D for arm A or B."""
        try:
            k0, k1, k2, k3, k4, k5, k6 = K
            d0, d1, d2, d3, d4, d5, d6 = D
            k_double = ctypes.c_double * 7
            k_value = k_double(k0, k1, k2, k3, k4, k5, k6)
            d_double = ctypes.c_double * 7
            d_value = d_double(d0, d1, d2, d3, d4, d5, d6)
            if arm == "A":
                return self.robot.OnSetJointKD_A(k_value, d_value)
            elif arm == "B":
                return self.robot.OnSetJointKD_B(k_value, d_value)
        except Exception as e:
            print(f"ERROR:{e}")

    def set_cart_kd_params(self, arm: str, K: list, D: list, type=2):
        """Set seven Cartesian/null-space stiffness and damping values and the Cartesian impedance type (default 2)."""
        try:
            k0, k1, k2, k3, k4, k5, k6 = K
            d0, d1, d2, d3, d4, d5, d6 = D
            k_double = ctypes.c_double * 7
            k_value = k_double(k0, k1, k2, k3, k4, k5, k6)
            d_double = ctypes.c_double * 7
            d_value = d_double(d0, d1, d2, d3, d4, d5, d6)
            type_int = ctypes.c_int(type)
            if arm == "A":
                return self.robot.OnSetCartKD_A(k_value, d_value, type_int)
            if arm == "B":
                return self.robot.OnSetCartKD_B(k_value, d_value, type_int)
        except Exception as e:
            print(f"ERROR:{e}")

    def set_force_control_params(
        self,
        arm: str,
        fcType: int,
        fxDirection: list,
        fcCtrlpara: list,
        fcAdjLmt: float,
    ):
        """Set the force-control mode, six-dimensional force direction, seven control parameters and adjustment limit."""
        try:
            fc_int = ctypes.c_int(fcType)
            k0, k1, k2, k3, k4, k5 = fxDirection
            d0, d1, d2, d3, d4, d5, d6 = fcCtrlpara
            fxDir_arr = (ctypes.c_double * 6)(k0, k1, k2, k3, k4, k5)
            fcCtrlPara_arr = (ctypes.c_double * 7)(d0, d1, d2, d3, d4, d5, d6)
            adj_double = ctypes.c_double(fcAdjLmt)
            if arm == "A":
                return self.robot.OnSetForceCtrPara_A(
                    fc_int, fxDir_arr, fcCtrlPara_arr, adj_double
                )
            elif arm == "B":
                return self.robot.OnSetForceCtrPara_B(
                    fc_int, fxDir_arr, fcCtrlPara_arr, adj_double
                )
        except Exception as e:
            print(f"ERROR:{e}")

    def set_EefCart_control_params(self, arm: str, fcType: int, CartCtrlPara: list):
        """Set the end-effector Cartesian rotation mode and its seven control parameters."""
        try:
            fc_int = ctypes.c_int(fcType)
            d0, d1, d2, d3, d4, d5, d6 = CartCtrlPara
            CartCtrlPara_arr = (ctypes.c_double * 7)(d0, d1, d2, d3, d4, d5, d6)
            if arm == "A":
                return self.robot.OnSetEefRot_A(fc_int, CartCtrlPara_arr)
            elif arm == "B":
                return self.robot.OnSetEefRot_B(fc_int, CartCtrlPara_arr)
        except Exception as e:
            print(f"ERROR:{e}")

    def set_joint_cmd_pose(self, arm: str, joints: list):
        """Append a seven-joint position command in degrees for arm A or B."""
        try:
            j0, j1, j2, j3, j4, j5, j6 = joints
            joints_double = ctypes.c_double * 7
            joints_value = joints_double(j0, j1, j2, j3, j4, j5, j6)
            if arm == "A":
                return self.robot.OnSetJointCmdPos_A(joints_value)
            elif arm == "B":
                return self.robot.OnSetJointCmdPos_B(joints_value)
        except Exception as e:
            print(f"ERROR:{e}")

    def set_force_cmd(self, arm: str, f: float):
        """Set the target force for the selected arm in newtons (or torque in newton-metres as defined by the mode)."""
        try:
            f_double = ctypes.c_double(f)
            if arm == "A":
                return self.robot.OnSetForceCmd_A(f_double)
            elif arm == "B":
                return self.robot.OnSetForceCmd_B(f_double)
        except Exception as e:
            print(f"ERROR:{e}")

    def ft_arm_control(self, arm: str, ft_cmd: "FTCmd"):
        """Apply an FTCmd force/torque command by value. Distances use millimetres and angles use degrees."""
        try:
            arm_byte = arm.encode("ascii")
            result = self.robot.FTArmControl(arm_byte, ft_cmd)
            return int(result)
        except Exception as e:
            print(f"ERROR:{e}")
            return 0

    def set_user_specified_data(self, arm: str, data_category: int):
        """Select user telemetry category data for arm A, B or both arms (AB)."""
        try:
            if arm == "A":
                result = self.robot.OnSetUserSpcfData_A(ctypes.c_long(data_category))
            elif arm == "B":
                result = self.robot.OnSetUserSpcfData_B(ctypes.c_long(data_category))
            elif arm == "AB":
                result = self.robot.OnSetUserSpcfData(ctypes.c_long(data_category))
            else:
                print(f'ERROR: arm must be "A", "B" or "AB", got "{arm}"')
                return 0
            return int(result)
        except Exception as e:
            print(f"ERROR:{e}")
            return 0

    def set_pvt_id(self, arm: str, id: int):
        """Select and run the uploaded PVT trajectory identifier for the selected arm."""
        try:
            if arm == "B":
                id_int = ctypes.c_int(id)
                return self.robot.OnSetPVT_B(id_int)
            elif arm == "A":
                id_int = ctypes.c_int(id)
                return self.robot.OnSetPVT_A(id_int)
        except Exception as e:
            print(f"ERROR:{e}")

    def send_pvt_file(self, arm: str, pvt_path: str, id: int):
        """Upload a local PVT trajectory file for the selected arm and identifier."""
        try:
            if arm == "A":
                self.a_pvt_path = pvt_path.encode("utf-8")
                pvt_char = ctypes.c_char_p(self.a_pvt_path)
                id_int = ctypes.c_int(id)
                return self.robot.OnSendPVT_A(pvt_char, id_int)
            elif arm == "B":
                self.b_pvt_path = pvt_path.encode("utf-8")
                pvt_char = ctypes.c_char_p(self.b_pvt_path)
                id_int = ctypes.c_int(id)
                return self.robot.OnSendPVT_B(pvt_char, id_int)
        except Exception as e:
            print(f"ERROR:{e}")

    def set_drag_space(self, arm: str, dgType: int):
        """Set the SDK dragging-space mode for the selected arm; zero exits dragging."""
        try:
            type_int = ctypes.c_int(dgType)
            if arm == "A":
                return self.robot.OnSetDragSpace_A(type_int)
            elif arm == "B":
                return self.robot.OnSetDragSpace_B(type_int)
        except Exception as e:
            print(f"ERROR:{e}")

    def receive_file(self, local_path: str, remote_path: str):
        """Download a controller file from remote_path to local_path."""
        self.local_file_path = local_path.encode("utf-8")
        local_char = ctypes.c_char_p(self.local_file_path)
        self.remote_file_path = remote_path.encode("utf-8")
        remote_char = ctypes.c_char_p(self.remote_file_path)
        return self.robot.OnRecvFile(local_char, remote_char)

    def send_file(self, local_path: str, remote_path: str):
        """Upload local_path to the controller file path remote_path."""
        self.local_file_path = local_path.encode("utf-8")
        local_char = ctypes.c_char_p(self.local_file_path)
        self.remote_file_path = remote_path.encode("utf-8")
        remote_char = ctypes.c_char_p(self.remote_file_path)
        return self.robot.OnSendFile(local_char, remote_char)

    def log_switch(self, flag: str):
        """Set controller logging using the official on/off flag convention."""
        try:
            if flag == "1":
                return self.robot.OnLogOn()
            elif flag == "0":
                return self.robot.OnLogOff()
        except Exception as e:
            print(f"ERROR:{e}")

    def local_log_switch(self, flag: str):
        """Set local SDK logging using the official on/off flag convention."""
        try:
            if flag == "1":
                return self.robot.OnLocalLogOn()
            elif flag == "0":
                return self.robot.OnLocalLogOff()
        except Exception as e:
            print(f"ERROR:{e}")

    def pln_init(self, config_path):
        """Initialize controller joint-planning limits from a local configuration file."""
        if not os.path.exists(config_path):
            raise ValueError("no config file")
        return self.robot.OnInitPlnLmt(config_path.encode("utf-8"))

    def stopRunPln_joint(self, arm: str):
        """Stop the active joint or Cartesian plan for arm A or B."""
        try:
            if arm not in ["A", "B"]:
                raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
            if arm == "A":
                return self.robot.OnStopPlnJoint_A()
            if arm == "B":
                return self.robot.OnStopPlnJoint_B()
        except Exception as e:
            print(f"ERROR:{e}")

    def setPln_joint_AB(
        self,
        start_joints_A: List[float],
        stop_joints_A: List[float],
        start_joints_B: List[float],
        stop_joints_B: List[float],
        vel_ratio: float,
        acc_ratio: float,
    ) -> bool:
        """Start both arms' joint-space plans together using seven-element start/end vectors and velocity/acceleration ratios."""
        if (
            len(start_joints_A) != 7
            or len(stop_joints_A) != 7
            or len(start_joints_B) != 7
            or (len(stop_joints_B) != 7)
        ):
            raise ValueError("All joint arrays must have exactly 7 elements")
        start_A = (ctypes.c_double * 7)(*start_joints_A)
        stop_A = (ctypes.c_double * 7)(*stop_joints_A)
        start_B = (ctypes.c_double * 7)(*start_joints_B)
        stop_B = (ctypes.c_double * 7)(*stop_joints_B)
        ret = self.robot.CoRunPlnJoint(
            start_A,
            stop_A,
            start_B,
            stop_B,
            ctypes.c_double(vel_ratio),
            ctypes.c_double(acc_ratio),
        )
        return ret

    def setPln_Cart_AB(self, pset0: ctypes.c_void_p, pset1: ctypes.c_void_p) -> bool:
        """Run two seven-dimensional PointSet trajectories together. Raw integer pointers are not accepted."""
        return self.robot.CoRunPlnCart(pset0, pset1)

    def stopPln_AB(self) -> bool:
        """Stop planning on both arms."""
        return self.robot.CoStopPln()

    def setPln_joint(
        self,
        arm: str,
        start_joints: list,
        target_joints: list,
        velRatio: float,
        accRatio: float,
    ):
        """Plan joint-space movement between two seven-joint vectors using velocity and acceleration ratios in (0, 1]."""
        try:
            if arm not in ["A", "B"]:
                raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
            if len(start_joints) != 7:
                raise ValueError("shape error: start joints must be (7,)")
            if len(target_joints) != 7:
                raise ValueError("shape error: target joints must be (7,)")
            if type(velRatio) != float:
                raise ValueError("value error: velRatio must be float, range:0~1 ")
            if type(accRatio) != float:
                raise ValueError("value error: accRatio must be float, range:0~1 ")
            if velRatio > 1 or velRatio <= 0:
                raise ValueError("value error: velRatio range:0~1 ")
            if accRatio > 1 or accRatio <= 0:
                raise ValueError("value error: accRatio range:0~1 ")
            sj0, sj1, sj2, sj3, sj4, sj5, sj6 = start_joints
            tj0, tj1, tj2, tj3, tj4, tj5, tj6 = target_joints
            k_double = ctypes.c_double * 7
            start_value = k_double(sj0, sj1, sj2, sj3, sj4, sj5, sj6)
            d_double = ctypes.c_double * 7
            target_value = d_double(tj0, tj1, tj2, tj3, tj4, tj5, tj6)
            vel = ctypes.c_double(velRatio)
            acc = ctypes.c_double(accRatio)
            if arm == "A":
                return self.robot.OnSetPlnJoint_A(start_value, target_value, vel, acc)
            if arm == "B":
                return self.robot.OnSetPlnJoint_B(start_value, target_value, vel, acc)
        except Exception as e:
            print(f"ERROR:{e}")

    def setPln_Cart(self, arm: str, pset: ctypes.c_void_p) -> bool:
        """Run a seven-dimensional PointSet trajectory on arm A or B without transferring C++ object ownership."""
        if arm not in ["A", "B"]:
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        success = False
        if arm == "A":
            success = self.robot.OnSetPlnCart_A(pset)
        elif arm == "B":
            success = self.robot.OnSetPlnCart_B(pset)
        if not success:
            raise RuntimeError("setPln_Cart failed")
        return success

    def clear_485_cache(self, arm: str):
        """Clear the selected arm's end-effector communication buffer."""
        try:
            if arm == "A":
                return self.robot.OnClearChDataA()
            elif arm == "B":
                return self.robot.OnClearChDataB()
        except Exception as e:
            print(f"ERROR:{e}")

    def set_485_data(self, arm: str, data: bytes, size_int: int, com: int):
        """Send at most 256 bytes to the selected end-effector channel: 1 CAN/CANFD, 2 COM1, or 3 COM2."""
        try:
            if len(data) >= 257:
                raise ValueError(f"data length({len(data)}) exceed 256")
            if size_int >= 257:
                print(f"size_int({size_int}) will be 256")
                size_int = 256
            result = identify_and_calculate_length(data)
            if (
                result["type"] == "hex string"
                or result["type"] == "bytes"
                or result["type"] == "bytes representation string"
            ):
                print("-" * 50)
                print(f"input: {data}")
                print(f"type: {result['type']}")
                print(f"byte length: {result['length_bytes']}")
                print(f"byte: {result['bytes_representation']}")
                print("-" * 50)
            else:
                print(f"ERROR: set_485_data input must be hex string of bytes string")
                return (False, False)
            size_int_long = ctypes.c_long(result["length_bytes"])
            com_long = ctypes.c_long(com)
            data_buffer = (ctypes.c_ubyte * 256)()
            data_length = min(len(result["bytes_representation"]), size_int)
            for i in range(data_length):
                data_buffer[i] = result["bytes_representation"][i]
            if arm == "A":
                return (
                    True,
                    self.robot.OnSetChDataA(data_buffer, size_int_long, com_long),
                )
            elif arm == "B":
                return (
                    True,
                    self.robot.OnSetChDataB(data_buffer, size_int_long, com_long),
                )
        except Exception as e:
            print(f"ERROR:{e}")

    def get_485_data(self, arm: str, com: int):
        """Read end-effector communication data and return the SDK status plus its hexadecimal byte string."""
        try:
            data_buffer = (ctypes.c_ubyte * 256)()
            ret_ch = ctypes.c_long(com)
            if arm == "A":
                result = self.robot.OnGetChDataA(data_buffer, ctypes.byref(ret_ch))
                byte_data = bytes(data_buffer)
                hex_list = []
                for byte in byte_data:
                    hex_value = hex(byte)[2:].upper().zfill(2)
                    hex_list.append(hex_value)
                return (result, " ".join(hex_list))
            elif arm == "B":
                result = self.robot.OnGetChDataB(data_buffer, ctypes.byref(ret_ch))
                byte_data = bytes(data_buffer)
                hex_list = []
                for byte in byte_data:
                    hex_value = hex(byte)[2:].upper().zfill(2)
                    hex_list.append(hex_value)
                return (result, " ".join(hex_list))
        except Exception as e:
            print(f"ERROR:{e}")

    def set_PD_vel_est_step(self, arm: str, step: int):
        """Set the velocity-estimation step for the selected arm in milliseconds."""
        step_long = c_long(step)
        arm_byte = arm.encode("ascii")
        try:
            result = self.robot.FX_OnSetVelEstStep(arm_byte, step_long)
            return bool(result)
        except Exception as e:
            print(f"set_PD_vel_est_step failed: {e}")
            return False

    def get_robot_name(self):
        """Download and read the controller robot name as UTF-8 text, returning None on failure."""
        try:
            name_buf = ctypes.create_string_buffer(512)
            ret = self.robot.OnGetRobotName(name_buf)
            if ret:
                return name_buf.value.decode("utf-8")
            return None
        except Exception as e:
            print(f"ERROR:{e}")
            return None

    def reset_6dof_force_sensor(self, arm: str):
        """Request zeroing of the selected arm's six-axis force sensor."""
        arm_byte = arm.encode("ascii")
        try:
            result = self.robot.OnReset6DofForceSensor(arm_byte)
            return bool(result)
        except Exception as e:
            print(f"reset_6dof_force_sensor failed: {e}")
            return False

    def set_system_time(self, year, month, day, hour, minute, scenod):
        """Set controller calendar time using year, month, day, hour, minute and scenod (the official seconds argument name)."""
        year_int = ctypes.c_int(year)
        month_int = ctypes.c_int(month)
        day_int = ctypes.c_int(day)
        hour_int = ctypes.c_int(hour)
        minute_int = ctypes.c_int(minute)
        secnod_int = ctypes.c_int(scenod)
        try:
            result = self.robot.OnSetSystemTime(
                year_int, month_int, day_int, hour_int, minute_int, secnod_int
            )
            return bool(result)
        except Exception as e:
            print(f"set_system_time failed: {e}")
            return False

    def reboot(self):
        """Request a controller reboot and return the SDK status."""
        try:
            result = self.robot.OnSetReboot()
            return bool(result)
        except Exception as e:
            print(f"reboot failed: {e}")
            return False

    def stop_running(self, arm: str):
        """Request a motion stop for A, B or AB. The official Python wrapper returns None."""
        try:
            arm_bytes = arm.encode("utf-8")
            self.robot.OnSetStopRunning(arm_bytes)
        except Exception as e:
            print("stop_running failed: ", e)

    def get_tool_info(self):
        """Download tool kinematic/dynamic data and decode the official two-line, 16-column file."""
        local_path = "tool_dyn_kine.txt"
        remote_path = "/home/fusion/tool_dyn_kine.txt"
        self.local_file_path = local_path.encode("utf-8")
        local_char = ctypes.c_char_p(self.local_file_path)
        self.remote_file_path = remote_path.encode("utf-8")
        remote_char = ctypes.c_char_p(self.remote_file_path)
        self.robot.OnRecvFile(local_char, remote_char)
        time.sleep(1)
        tool_result = read_csv_file_to_float_strict(local_path, expected_columns=16)
        return tool_result

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


"######################################## Concise SDK ########################################################"


class Concise_Marvin_Robot:
    """Controller interface that batches commands and checks errors inside the SDK. Instances share SDK state."""

    def __init__(self):
        """Create this interface or value record without opening a robot connection."""
        import sys

        self.robot = _native
        self.ErrorCode = None
        self.a_pvt_path = None
        self.b_pvt_path = None
        self.local_file_path = None
        self.remote_file_path = None
        self.save_csv_path = None
        self.save_data_path = None

    def _convert_ip(self, ip_str: str):
        """Validate an IPv4 address and return its four integer octets."""
        return tuple((int(part) for part in IPv4Address(ip_str).exploded.split(".")))

    def connect(self, robot_ip: str, log_switch: int = 0) -> bool:
        """Connect to the controller at an IPv4 address. The concise interface also configures controller logging."""
        try:
            ip1, ip2, ip3, ip4 = self._convert_ip(robot_ip)
            result = self.robot.Connect(ip1, ip2, ip3, ip4, log_switch)
            return bool(result)
        except Exception as e:
            print(f"ConnectAndCkeck failed: {e}")
            return False

    def subscribe(self, dcss) -> dict | None:
        """Fill a DCSS record and return its nested state dictionary. The concise interface returns None on failure."""
        if dcss is None:
            print("[ERROR] subscribe: dcss is None")
            return None
        try:
            success = self.robot.OnGetBuf(ctypes.byref(dcss))
            if not success:
                print("[ERROR] subscribe: OnGetBuf returned False")
                return None
            result = structure2dict(dcss)
            return result
        except Exception as e:
            print(f"[ERROR] subscribe failed: {e}")
            return None

    def check_arms_error(self) -> bool:
        """Check and clear arm-state errors using the concise SDK interface."""
        return self.robot.CheckArmError()

    def check_servo_error(self) -> bool:
        """Check and clear servo errors using the concise SDK interface."""
        return self.robot.CheckServoError()

    def check_error_and_clear(self):
        """Inspect arm and servo errors and request error clearing when necessary."""
        if not self.check_arms_error() and (not self.check_servo_error()):
            return False
        else:
            return False

    def release_robot(self):
        """Release the shared controller connection. Repeated release before initialization is safe."""
        return self.robot.OnRelease()

    def SDK_version(self):
        """Return the version reported by the compiled control SDK."""
        return self.robot.OnGetSDKVersion()

    def update_SDK(self, sdk_path: str):
        """Upload a local controller system update package. Check the returned SDK status."""
        sdk_char = ctypes.c_char_p(sdk_path.encode("utf-8"))
        return self.robot.OnUpdateSystem(sdk_char)

    def download_sdk_log(self, log_path: str):
        """Download controller logs to the requested local path."""
        log_char = ctypes.c_char_p(log_path.encode("utf-8"))
        return self.robot.OnDownloadLog(log_char)

    def get_param(self, type: str, paraName: str):
        """Read an integer or floating-point parameter by its ASCII controller parameter name. Return (status, value)."""
        try:
            param_buf = (ctypes.c_char * 30)(*paraName.encode("ascii"), 0)
            if type == "float":
                result = ctypes.c_double(0)
                re_flag = self.robot.OnGetFloatPara(param_buf, ctypes.byref(result))
                return (re_flag, result.value)
            elif type == "int":
                result = ctypes.c_long(0)
                re_flag = self.robot.OnGetIntPara(param_buf, ctypes.byref(result))
                return (re_flag, result.value)
        except Exception as e:
            print("ERROR:", e)

    def save_para_file(self):
        """Save the current controller configuration parameters."""
        return self.robot.OnSavePara()

    def set_param(self, type: str, paraName: str, value: float):
        """Write an integer or floating-point controller parameter and return the SDK status."""
        try:
            param_buf = (ctypes.c_char * 30)(*paraName.encode("ascii"), 0)
            if type == "float":
                result = ctypes.c_double(value)
                return self.robot.OnSetFloatPara(param_buf, result)
            elif type == "int":
                result = ctypes.c_int(int(value))
                return self.robot.OnSetIntPara(param_buf, result)
        except Exception as e:
            print("ERROR:", e)

    def start_collect_data(
        self, target_num: int, target_id: list, record_num: int
    ) -> bool:
        """Start recording up to 35 telemetry fields, clamping record count to 1,000 through 1,000,000."""
        if target_num < 0:
            target_num = 1
        if target_num > 35:
            target_num = 35
        if record_num < 1000:
            record_num = 1000
        if record_num > 1000000:
            record_num = 1000000
        id_array = (ctypes.c_long * 35)(*target_id)
        try:
            result = self.robot.StartCollectData(target_num, id_array, record_num)
            return bool(result)
        except Exception as e:
            print(f"StartCollectData failed: {e}")
            return False

    def stop_collect_data(self) -> bool:
        """Stop recording controller telemetry."""
        try:
            result = self.robot.StopCollectData()
            return bool(result)
        except Exception as e:
            print(f"StopCollectData failed: {e}")
            return False

    def save_gather_data(self, path: str) -> bool:
        """Save recorded telemetry in the SDK data-file format."""
        if not path:
            raise ValueError("path cannot be empty")
        try:
            path_bytes = path.encode("utf-8")
            result = self.robot.OnSaveGatherData(path_bytes)
            return bool(result)
        except Exception as e:
            print(f"OnSaveGatherData failed: {e}")
            return False

    def save_gather_data_as_csv_to_path(self, path: str) -> bool:
        """Save recorded telemetry as CSV using the concise interface's conversion format."""
        path1 = "tmp.txt"
        self.save_data_path = path1.encode("utf-8")
        path_char = ctypes.c_char_p(self.save_data_path)
        self.robot.OnSaveGatherData(path_char)
        time.sleep(0.2)
        with open(path1, "r") as file:
            lines = file.readlines()
        processed_data = []
        lines = lines[1:]
        for i, line in enumerate(lines):
            parts = line.strip().split("$")
            numbers = []
            for part in parts:
                if part:
                    num_str = part.split()[-1]
                    numbers.append(num_str)
            if len(numbers) >= 2:
                numbers = numbers[2:]
            processed_data.append(numbers)
        try:
            with open(path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(processed_data)
            print(f"数据已成功保存到: {path}")
            if os.path.exists(path1):
                os.remove(path1)
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            if os.path.exists(path1):
                os.remove(path1)
            return False

    def soft_stop(self, arm: str):
        """Request a software emergency stop for arm A, B or both arms (AB)."""
        try:
            arm_bytes = arm.encode("utf-8")
            self.robot.EStop(arm_bytes)
        except Exception as e:
            print("ERROR:", e)

    def servo_reset(self, arm: str, axis: int):
        """Reset the specified servo axis, numbered 0 through 6, on arm A or B."""
        if len(arm) != 1:
            raise ValueError("arm must be a single character, got '{}'".format(arm))
        if not isinstance(axis, int) or axis < 0 or axis > 6:
            raise ValueError("axis must be an integer between 0 and 6")
        arm_byte = arm.encode("ascii")
        try:
            self.robot.ServoReset(arm_byte, axis)
        except Exception as e:
            print("ServoReset failed:", e)

    def get_servo_error_code(self, arm: str, lang="CN"):
        """Read servo fault codes and return their descriptions in the selected CN or EN language."""
        try:
            err_code_value = (ctypes.c_long * 7)()
            if arm == "A":
                self.robot.OnGetServoErr_A(ctypes.byref(err_code_value))
                err_code = [0] * 7
                for i in range(7):
                    err_code[i] = decimal_to_hex(err_code_value[i], prefix=True)
                err_code = get_fault_descriptions(err_code, lang)
                return err_code
            elif arm == "B":
                self.robot.OnGetServoErr_B(ctypes.byref(err_code_value))
                err_code = [0] * 7
                for i in range(7):
                    err_code[i] = decimal_to_hex(err_code_value[i], prefix=True)
                err_code = get_fault_descriptions(err_code, lang)
                return err_code
        except Exception as e:
            print("ERROR:", e)

    def set_position_state(self, arm: str, velRatio: int, AccRatio: int) -> bool:
        """Enter position mode with velocity and acceleration percentages for arm A or B."""
        if len(arm) != 1:
            raise ValueError(f"arm must be a single character, got '{arm}'")
        if velRatio < 0:
            velRatio = 10
        elif velRatio > 100:
            velRatio = 100
        if AccRatio < 0:
            AccRatio = 10
        elif AccRatio > 100:
            AccRatio = 100
        arm_byte = arm.encode("ascii")
        try:
            result = self.robot.SetJointMode(arm_byte, velRatio, AccRatio)
            return bool(result)
        except Exception as e:
            print(f"SetJointMode failed: {e}")
            return False

    def set_imp_joint_state(self, arm: str, velRatio: int, AccRatio: int, K, D) -> bool:
        """Enter joint impedance mode with seven stiffness and damping values."""
        if velRatio < 0:
            velRatio = 10
        elif velRatio > 100:
            velRatio = 100
        if AccRatio < 0:
            AccRatio = 10
        elif AccRatio > 100:
            AccRatio = 100
        if len(K) != 7 or len(D) != 7:
            raise ValueError("K and D must have exactly 7 elements")
        K_clamped = []
        for val in K:
            if val < 0:
                val = 0.0
            K_clamped.append(float(val))
        D_clamped = []
        for val in D:
            if val < 0:
                val = 0.0
            elif val > 1:
                val = 1.0
            D_clamped.append(float(val))
        arm_byte = arm.encode("ascii")
        k_array = (ctypes.c_double * 7)(*K_clamped)
        d_array = (ctypes.c_double * 7)(*D_clamped)
        try:
            result = self.robot.SetImpJointMode(
                arm_byte, velRatio, AccRatio, k_array, d_array
            )
            return bool(result)
        except Exception as e:
            print(f"SetImpJointMode failed: {e}")
            return False

    def set_imp_cart_state(
        self,
        arm: str,
        velRatio: int,
        AccRatio: int,
        K,
        D,
        rot_type: int,
        cart_ctrl_para,
    ) -> bool:
        """Enter Cartesian impedance mode with stiffness, damping and end-effector rotation parameters."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        velRatio = max(0, min(velRatio, 100))
        AccRatio = max(0, min(AccRatio, 100))
        if len(K) != 7 or len(D) != 7:
            raise ValueError("K and D must have exactly 7 elements")
        if rot_type not in (0, 1, 2):
            raise ValueError(f"rot_type must be 1 or 2, got {rot_type}")
        if len(cart_ctrl_para) != 7:
            raise ValueError("cart_ctrl_para must have exactly 7 elements")
        K_clamped = [max(0.0, float(v)) for v in K]
        D_clamped = [max(0.0, min(1.0, float(v))) for v in D]
        arm_byte = arm.encode("ascii")
        k_array = (ctypes.c_double * 7)(*K_clamped)
        d_array = (ctypes.c_double * 7)(*D_clamped)
        para_array = (ctypes.c_double * 7)(*cart_ctrl_para)
        try:
            result = self.robot.SetImpCartMode(
                arm_byte, velRatio, AccRatio, k_array, d_array, rot_type, para_array
            )
            return bool(result)
        except Exception as e:
            print(f"SetImpCartMode failed: {e}")
            return False

    def set_imp_force_state(self, arm: str, fx_dir, fc_adj_lmt: float) -> bool:
        """Enter force impedance mode using a six-element force direction and adjustment limit."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        if len(fx_dir) != 6:
            raise ValueError("fx_dir must have exactly 6 elements")
        if fc_adj_lmt < 0:
            raise ValueError(f"fc_adj_lmt must be >= 0, got {fc_adj_lmt}")
        arm_byte = arm.encode("ascii")
        fx_array = (ctypes.c_double * 6)(*fx_dir)
        try:
            result = self.robot.SetImpForceMode(
                arm_byte, fx_array, ctypes.c_double(fc_adj_lmt)
            )
            return bool(result)
        except Exception as e:
            print(f"SetImpForceMode failed: {e}")
            return False

    def set_force_cmd(self, arm: str, force: float) -> bool:
        """Set the target force for the selected arm in newtons (or torque in newton-metres as defined by the mode)."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        arm_byte = arm.encode("ascii")
        try:
            result = self.robot.SetForceCmd(arm_byte, ctypes.c_double(force))
            return bool(result)
        except Exception as e:
            print(f"SetForceCmd failed: {e}")
            return False

    def ft_arm_control(self, arm: str, ft_cmd: "FTCmd") -> bool:
        """Apply an FTCmd force/torque command by value. Distances use millimetres and angles use degrees."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        arm_byte = arm.encode("ascii")
        try:
            result = self.robot.FTArmControl(arm_byte, ft_cmd)
            return bool(result)
        except Exception as e:
            print(f"FTArmControl failed: {e}")
            return False

    def set_user_specified_data(self, arm: str, data_category: int) -> bool:
        """Select user telemetry category data for arm A, B or both arms (AB)."""
        if arm not in ("A", "B", "AB"):
            raise ValueError(f"arm must be 'A', 'B' or 'AB', got '{arm}'")
        try:
            if arm == "A":
                return bool(
                    self.robot.OnSetUserSpcfData_A(ctypes.c_long(data_category))
                )
            elif arm == "B":
                return bool(
                    self.robot.OnSetUserSpcfData_B(ctypes.c_long(data_category))
                )
            else:
                return bool(self.robot.OnSetUserSpcfData(ctypes.c_long(data_category)))
        except Exception as e:
            print(f"OnSetUserSpcfData failed: {e}")
            return False

    def set_joint_position_cmd(self, arm: str, joint) -> bool:
        """Send a seven-joint position command in degrees through the concise interface."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        if len(joint) != 7:
            raise ValueError("joint must have exactly 7 elements")
        arm_byte = arm.encode("ascii")
        joint_array = (ctypes.c_double * 7)(*joint)
        try:
            result = self.robot.SetJointPostionCmd(arm_byte, joint_array)
            return bool(result)
        except Exception as e:
            print(f"SetJointPostionCmd failed: {e}")
            return False

    def pln_init(self, path: str) -> bool:
        """Initialize controller joint-planning limits from a local configuration file."""
        if not path:
            raise ValueError("path cannot be empty")
        try:
            result = self.robot.PlnInit(path.encode("utf-8"))
            return bool(result)
        except Exception as e:
            print(f"PlnInit failed: {e}")
            return False

    def run_pln_joint(
        self, arm: str, start_joints, stop_joints, vel_ratio: float, acc_ratio: float
    ) -> bool:
        """Run a joint-space plan between seven-joint start/end vectors using ratios in (0, 1]."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        if len(start_joints) != 7 or len(stop_joints) != 7:
            raise ValueError(
                "start_joints and stop_joints must have exactly 7 elements"
            )
        vel_ratio = max(0.0, min(1.0, vel_ratio))
        acc_ratio = max(0.0, min(1.0, acc_ratio))
        arm_byte = arm.encode("ascii")
        start_array = (ctypes.c_double * 7)(*start_joints)
        stop_array = (ctypes.c_double * 7)(*stop_joints)
        try:
            result = self.robot.RunPlnJoint(
                arm_byte, start_array, stop_array, vel_ratio, acc_ratio
            )
            return bool(result)
        except Exception as e:
            print(f"RunPlnJoint failed: {e}")
            return False

    def run_pln_cart(self, arm: str, pset) -> bool:
        """Run a seven-dimensional PointSet trajectory through the concise interface."""
        return bool(self.robot.RunPlnCart(arm.encode("ascii"), pset))

    def stop_pln(self, arm: str) -> bool:
        """Stop the selected arm's active plan."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        try:
            result = self.robot.StopPln(arm.encode("ascii"))
            return bool(result)
        except Exception as e:
            print(f"StopPln failed: {e}")
            return False

    def setPln_joint_AB(
        self,
        start_joints_A: List[float],
        stop_joints_A: List[float],
        start_joints_B: List[float],
        stop_joints_B: List[float],
        vel_ratio: float,
        acc_ratio: float,
    ) -> bool:
        """Start both arms' joint-space plans together using seven-element start/end vectors and velocity/acceleration ratios."""
        if (
            len(start_joints_A) != 7
            or len(stop_joints_A) != 7
            or len(start_joints_B) != 7
            or (len(stop_joints_B) != 7)
        ):
            raise ValueError("All joint arrays must have exactly 7 elements")
        start_A = (ctypes.c_double * 7)(*start_joints_A)
        stop_A = (ctypes.c_double * 7)(*stop_joints_A)
        start_B = (ctypes.c_double * 7)(*start_joints_B)
        stop_B = (ctypes.c_double * 7)(*stop_joints_B)
        ret = self.robot.CoRunPlnJoint(
            start_A,
            stop_A,
            start_B,
            stop_B,
            ctypes.c_double(vel_ratio),
            ctypes.c_double(acc_ratio),
        )
        return ret

    def setPln_Cart_AB(self, pset0: ctypes.c_void_p, pset1: ctypes.c_void_p) -> bool:
        """Run two seven-dimensional PointSet trajectories together. Raw integer pointers are not accepted."""
        return self.robot.CoRunPlnCart(pset0, pset1)

    def stopPln_AB(self) -> bool:
        """Stop planning on both arms."""
        return self.robot.CoStopPln()

    def send_pvt(self, arm: str, local_file: str, serial: int) -> bool:
        """Upload a local PVT file to the selected arm's trajectory identifier."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        if not 0 <= serial <= 99:
            raise ValueError(f"serial must be between 0 and 99, got {serial}")
        if not local_file:
            raise ValueError("local_file cannot be empty")
        try:
            result = self.robot.SendPVT(
                arm.encode("ascii"), local_file.encode("utf-8"), serial
            )
            return bool(result)
        except Exception as e:
            print(f"SendPVT failed: {e}")
            return False

    def run_pvt(self, arm: str, id_: int) -> bool:
        """Run a previously uploaded PVT trajectory identifier."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        if not 0 <= id_ <= 99:
            raise ValueError(f"id must be between 0 and 99, got {id_}")
        try:
            result = self.robot.RunPVT(arm.encode("ascii"), id_)
            return bool(result)
        except Exception as e:
            print(f"RunPVT failed: {e}")
            return False

    def set_joint_drag(self, arm: str) -> bool:
        """Enter joint dragging after configuring the required joint impedance mode."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        try:
            result = self.robot.SetJointDrag(arm.encode("ascii"))
            return bool(result)
        except Exception as e:
            print(f"SetJointDrag failed: {e}")
            return False

    def set_cart_drag(self, arm: str, type_: str) -> bool:
        """Enter Cartesian dragging for X, Y, Z or R (rotation). Exit dragging before selecting another mode."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        if type_ not in ("X", "Y", "Z", "R"):
            raise ValueError(f"type must be 'X', 'Y', 'Z' or 'R', got '{type_}'")
        try:
            result = self.robot.SetCartDrag(arm.encode("ascii"), type_.encode("ascii"))
            return bool(result)
        except Exception as e:
            print(f"SetCartDrag failed: {e}")
            return False

    def exit_drag(self, arm: str) -> bool:
        """Exit dragging on the selected arm."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        try:
            result = self.robot.ExitDrag(arm.encode("ascii"))
            return bool(result)
        except Exception as e:
            print(f"ExitDrag failed: {e}")
            return False

    def set_tool(self, arm: str, kine_para, dyn_para) -> bool:
        """Set six tool kinematic parameters and ten tool dynamic parameters for the selected arm."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        if len(kine_para) != 6:
            raise ValueError("kine_para must have exactly 6 elements")
        if len(dyn_para) != 10:
            raise ValueError("dyn_para must have exactly 10 elements")
        arm_byte = arm.encode("ascii")
        kine_array = (ctypes.c_double * 6)(*kine_para)
        dyn_array = (ctypes.c_double * 10)(*dyn_para)
        try:
            result = self.robot.SetTool(arm_byte, kine_array, dyn_array)
            return bool(result)
        except Exception as e:
            print(f"SetTool failed: {e}")
            return False

    def disable(self, arm: str) -> bool:
        """Disable or reset the selected arm."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        try:
            result = self.robot.Disable(arm.encode("ascii"))
            return bool(result)
        except Exception as e:
            print(f"Disable failed: {e}")
            return False

    def clear_ch_data(self, arm: str) -> bool:
        """Clear the selected end-effector communication channel buffer."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        try:
            result = self.robot.ClearChData(arm.encode("ascii"))
            return bool(result)
        except Exception as e:
            print(f"ClearChData failed: {e}")
            return False

    def get_ch_data(self, arm: str, channel: int) -> tuple[int, bytes, int]:
        """Read end-effector channel data and return (length, hexadecimal_text), or (0, empty_bytes) on failure."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        data_buffer = (ctypes.c_ubyte * 256)()
        ret_ch = ctypes.c_long(channel)
        try:
            read_len = self.robot.GetChData(
                arm.encode("ascii"), data_buffer, ctypes.byref(ret_ch)
            )
            if read_len <= 0:
                return (0, b"")
            byte_data = bytes(data_buffer)[:read_len]
            hex_list = []
            for byte in byte_data:
                hex_value = hex(byte)[2:].upper().zfill(2)
                hex_list.append(hex_value)
            return (read_len, " ".join(hex_list))
        except Exception as e:
            print(f"GetChData failed: {e}")
            return (0, b"")

    def set_ch_data(self, arm: str, data: bytes, size_int: int, set_ch: int) -> int:
        """Send up to 256 bytes to end-effector channel 1, 2 or 3 and return the SDK result."""
        if len(arm) != 1 or arm not in ("A", "B"):
            raise ValueError(f"arm must be 'A' or 'B', got '{arm}'")
        if size_int > 256 or size_int < 0:
            raise ValueError(f"size_int must be between 0 and 256, got {size_int}")
        if set_ch not in (1, 2, 3):
            raise ValueError(f"set_ch must be 1, 2 or 3, got {set_ch}")
        data_buffer = (ctypes.c_ubyte * 256)()
        for i in range(min(size_int, len(data))):
            data_buffer[i] = data[i]
        try:
            sent_len = self.robot.SetChData(
                arm.encode("ascii"), data_buffer, size_int, set_ch
            )
            return sent_len
        except Exception as e:
            print(f"SetChData failed: {e}")
            return -1

    def get_tool_info(self):
        """Download tool kinematic/dynamic data and decode the official two-line, 16-column file."""
        local_path = "tool_dyn_kine.txt"
        remote_path = "/home/fusion/tool_dyn_kine.txt"
        self.local_file_path = local_path.encode("utf-8")
        local_char = ctypes.c_char_p(self.local_file_path)
        self.remote_file_path = remote_path.encode("utf-8")
        remote_char = ctypes.c_char_p(self.remote_file_path)
        self.robot.OnRecvFile(local_char, remote_char)
        time.sleep(1)
        tool_result = read_csv_file_to_float_strict(local_path, expected_columns=16)
        return tool_result

    def set_vel_est_step(self, arm: str, time: int):
        """Set the selected arm's velocity-estimation step in milliseconds."""
        time_long = ctypes.c_long(time)
        return self.robot.FX_OnSetVelEstStep(arm.encode("ascii"), time_long)

    def get_robot_name(self) -> str | None:
        """Download and read the controller robot name as UTF-8 text, returning None on failure."""
        name_buf = ctypes.create_string_buffer(512)
        try:
            result = self.robot.OnGetRobotName(name_buf)
            print(f"===={name_buf.value.decode('utf-8')}")
            if result:
                return name_buf.value.decode("utf-8")
            return None
        except Exception as e:
            print(f"OnGetRobotName failed: {e}")
            return None

    def reset_6dof_force_sensor(self, arm: str):
        """Request zeroing of the selected arm's six-axis force sensor."""
        arm_byte = arm.encode("ascii")
        try:
            result = self.robot.OnReset6DofForceSensor(arm_byte)
            return bool(result)
        except Exception as e:
            print(f"reset_6dof_force_sensor failed: {e}")
            return False

    def set_system_time(self, year, month, day, hour, minute, scenod):
        """Set controller calendar time using year, month, day, hour, minute and scenod (the official seconds argument name)."""
        year_int = ctypes.c_int(year)
        month_int = ctypes.c_int(month)
        day_int = ctypes.c_int(day)
        hour_int = ctypes.c_int(hour)
        minute_int = ctypes.c_int(minute)
        secnod_int = ctypes.c_int(scenod)
        try:
            result = self.robot.OnSetSystemTime(
                year_int, month_int, day_int, hour_int, minute_int, secnod_int
            )
            return bool(result)
        except Exception as e:
            print(f"set_system_time failed: {e}")
            return False

    def reboot(self):
        """Request a controller reboot and return the SDK status."""
        try:
            result = self.robot.OnSetReboot()
            return bool(result)
        except Exception as e:
            print(f"reboot failed: {e}")
            return False

    def stop_running(self, arm: str):
        """Request a motion stop for A, B or AB. The official Python wrapper returns None."""
        try:
            arm_bytes = arm.encode("utf-8")
            self.robot.OnSetStopRunning(arm_bytes)
        except Exception as e:
            print("stop_running failed: ", e)

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


"######################################## Assistive Funcs ####################################################"


def check_joints_accuracy_with_tolerance(joint1, joint2, tolerance=0.01):
    """Compare two seven-joint vectors using the requested absolute per-joint tolerance."""
    if not (joint1 and joint2 and (len(joint1) == 7) and (len(joint2) == 7)):
        return False
    return all((abs(j1 - j2) < tolerance for j1, j2 in zip(joint1, joint2)))


class StateCtr(Structure):
    """Packed controller state, commanded state and error code."""

    _pack_ = 4
    _layout_ = "ms"
    _fields_ = [("m_CurState", c_int), ("m_CmdState", c_int), ("m_ERRCode", c_int)]


class RT_IN(Structure):
    """Packed per-arm input commands and controller settings."""

    _pack_ = 4
    _layout_ = "ms"
    _fields_ = [
        ("m_RtInSwitch", c_int),
        ("m_ImpType", c_int),
        ("m_InFrameSerial", c_int),
        ("m_FrameMissCnt", c_short),
        ("m_MaxFrameMissCnt", c_short),
        ("m_SysCyc", c_int),
        ("m_SysCycMissCnt", c_short),
        ("m_MaxSysCycMissCnt", c_short),
        ("m_ToolKine", c_float * 6),
        ("m_ToolDyn", c_float * 10),
        ("m_Joint_CMD_Pos", c_float * 7),
        ("m_Joint_Vel_Ratio", c_short),
        ("m_Joint_Acc_Ratio", c_short),
        ("m_Joint_K", c_float * 7),
        ("m_Joint_D", c_float * 7),
        ("m_DragSpType", c_int),
        ("m_DragSpPara", c_float * 6),
        ("m_Cart_KD_Type", c_int),
        ("m_Cart_K", c_float * 6),
        ("m_Cart_D", c_float * 6),
        ("m_Cart_KN", c_float),
        ("m_Cart_DN", c_float),
        ("m_Force_FB_Type", c_int),
        ("m_Force_Type", c_int),
        ("m_Force_Dir", c_float * 6),
        ("m_Force_PIDUL", c_float * 7),
        ("m_Force_AdjLmt", c_float),
        ("m_Force_Cmd", c_float),
        ("m_SET_Tags", c_ubyte * 16),
        ("m_Update_Tags", c_ubyte * 16),
        ("m_PvtID", c_ubyte),
        ("m_PvtID_Update", c_ubyte),
        ("m_Pvt_RunID", c_ubyte),
        ("m_Pvt_RunState", c_ubyte),
    ]


class RT_OUT(Structure):
    """Packed per-arm feedback and trajectory status."""

    _pack_ = 4
    _layout_ = "ms"
    _fields_ = [
        ("m_OutFrameSerial", c_int),
        ("m_FB_Joint_Pos", c_float * 7),
        ("m_FB_Joint_Vel", c_float * 7),
        ("m_FB_Joint_PosE", c_float * 7),
        ("m_FB_Joint_Cmd", c_float * 7),
        ("m_FB_Joint_CToq", c_float * 7),
        ("m_FB_Joint_SToq", c_float * 7),
        ("m_FB_Joint_Them", c_float * 7),
        ("m_EST_Joint_Firc", c_float * 7),
        ("m_EST_Joint_Firc_Dot", c_float * 7),
        ("m_EST_Joint_Force", c_float * 7),
        ("m_EST_Cart_FN", c_float * 6),
        ("m_TipDI", c_char),
        ("m_LowSpdFlag", c_char),
        ("m_pad", c_char),
        ("m_TrajState", c_char),
    ]


class DCSS(Structure):
    """Packed dual-arm telemetry and configuration exchange record."""

    _pack_ = 4
    _layout_ = "ms"
    _fields_ = [
        ("m_State", StateCtr * 2),
        ("m_In", RT_IN * 2),
        ("m_Out", RT_OUT * 2),
        ("m_ParaName", c_char * 30),
        ("m_ParaType", c_ubyte),
        ("m_ParaIns", c_ubyte),
        ("m_ParaValueI", c_int),
        ("m_ParaValueF", c_float),
        ("m_ParaCmdSerial", c_short),
        ("m_ParaRetSerial", c_short),
    ]


class FTCmd(Structure):
    """Force/torque control record passed by value to the native SDK. fxDir has six elements; distances use mm and angles use degrees."""

    _pack_ = 4
    _layout_ = "ms"
    _fields_ = [
        ("fxDir", c_double * 6),
        ("K", c_double),
        ("F", c_double),
        ("FreeDis", c_double),
        ("Dis", c_double),
        ("Kn", c_double),
        ("Tn", c_double),
        ("NFreeDis", c_double),
        ("Ndis", c_double),
    ]


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


def update_text_file_simple(mode, data_list, filename):
    """Replace the selected A/B row of an existing two-row tool file with sixteen values."""
    if mode not in ["A", "B"] or len(data_list) != 16:
        return False
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                lines = file.readlines()
        line_index = 0 if mode == "A" else 1
        lines[line_index] = ",".join((str(x) for x in data_list)) + "\n"
        with open(filename, "w", encoding="utf-8") as file:
            file.writelines(lines)
        return True
    except Exception as e:
        print(f"更新文件时出错: {e}")
        return False


def read_csv_file_to_float_strict(filename, expected_columns=16):
    """Parse the official two-row tool CSV format, preserving its zero-row, one-active-row and error return conventions."""
    if not os.path.isfile(filename):
        print(f"文件不存在: {filename}")
        return -1
    if os.path.getsize(filename) == 0:
        return 0
    try:
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        if len(non_empty_lines) == 0:
            return 0
        all_float_data = []
        for line_num, line in enumerate(non_empty_lines, 1):
            values = line.split(",")
            cleaned_values = [v.strip() for v in values if v.strip()]
            if len(cleaned_values) != expected_columns:
                print(
                    f"第{line_num}行: 期望{expected_columns}列，实际找到{len(cleaned_values)}列"
                )
                return -1
            float_values = []
            for value in cleaned_values:
                try:
                    float_value = float(value)
                    float_values.append(float_value)
                except ValueError:
                    print(f"第{line_num}行: 无法将内容 '{value}' 转换为float")
                    return -1
            all_float_data.append(float_values)
        if len(all_float_data) == 1:
            return 0
        elif len(all_float_data) == 2:
            line1_all_zero = all((x == 0.0 for x in all_float_data[0]))
            line2_all_zero = all((x == 0.0 for x in all_float_data[1]))
            if line1_all_zero and line2_all_zero:
                return 0
            elif line1_all_zero and (not line2_all_zero):
                return ("line2", all_float_data[1])
            elif not line1_all_zero and line2_all_zero:
                return ("line1", all_float_data[0])
            else:
                return all_float_data
        else:
            print(f"文件包含{len(all_float_data)}行，只支持1-2行")
            return -1
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return -1


def decimal_to_hex(number, prefix=False, upper=True, float_precision=8):
    """Format an integer or floating-point value as hexadecimal using the requested prefix, case and precision."""
    if not isinstance(number, (int, float)):
        raise TypeError("输入必须是整数或浮点数")
    if isinstance(number, int):
        hex_str = hex(number)
    else:
        hex_str = float(number).hex()
        if float_precision is not None:
            parts = hex_str.split(".")
            if len(parts) > 1:
                exponent_part = parts[1].split("p")
                if len(exponent_part) > 1:
                    hex_str = f"{parts[0]}.{exponent_part[0][:float_precision]}p{exponent_part[1]}"
    if not prefix and hex_str.startswith("0x"):
        hex_str = hex_str[2:]
    elif prefix and (not hex_str.startswith("0x")):
        hex_str = "0x" + hex_str
    if upper:
        hex_str = hex_str.upper()
    else:
        hex_str = hex_str.lower()
    return hex_str


def identify_and_calculate_length(input_data: Union[str, bytes]) -> dict:
    """Classify bytes, hexadecimal text or ordinary text and report its byte representation and length."""
    result = {
        "input": input_data,
        "type": None,
        "length_bytes": None,
        "bytes_representation": None,
    }
    if isinstance(input_data, bytes):
        result["type"] = "bytes"
        result["length_bytes"] = len(input_data)
        result["bytes_representation"] = input_data
        return result
    if isinstance(input_data, str):
        clean_input = re.sub("\\s+", "", input_data.lower())
        if clean_input.startswith("0x"):
            clean_input = clean_input[2:]
        hex_pattern = re.compile("^[0-9a-f]+$")
        if hex_pattern.match(clean_input):
            if len(clean_input) % 2 != 0:
                clean_input = "0" + clean_input
            try:
                bytes_rep = bytes.fromhex(clean_input)
                result["type"] = "hex string"
                result["length_bytes"] = len(bytes_rep)
                result["bytes_representation"] = bytes_rep
                return result
            except ValueError:
                pass
        if input_data.startswith('b"') and input_data.endswith('"'):
            try:
                bytes_rep = ast.literal_eval(input_data)
                if isinstance(bytes_rep, bytes):
                    result["type"] = "bytes representation string"
                    result["length_bytes"] = len(bytes_rep)
                    result["bytes_representation"] = bytes_rep
                    return result
            except:
                pass
        try:
            bytes_rep = input_data.encode("utf-8")
            result["type"] = "regular string"
            result["length_bytes"] = len(bytes_rep)
            result["bytes_representation"] = bytes_rep
            return result
        except UnicodeEncodeError:
            raise ValueError("输入不是有效的十六进制字符串，也无法编码为UTF-8字节串")
    raise TypeError("输入必须是字符串或字节串")


def structure2dict(dcss):
    """Convert a DCSS telemetry record to the official nested dictionary representation."""
    result = {
        "para_name": ["Marvin_sub_data"],
        "states": [
            {
                "cur_state": dcss.m_State[0].m_CurState,
                "cmd_state": dcss.m_State[0].m_CmdState,
                "err_code": dcss.m_State[0].m_ERRCode,
            },
            {
                "cur_state": dcss.m_State[1].m_CurState,
                "cmd_state": dcss.m_State[1].m_CmdState,
                "err_code": dcss.m_State[1].m_ERRCode,
            },
        ],
    }
    result["outputs"] = [
        {
            "frame_serial": rt_out.m_OutFrameSerial,
            "pad": rt_out.m_pad,
            "traj_state": rt_out.m_TrajState,
            "tip_di": rt_out.m_TipDI,
            "low_speed_flag": rt_out.m_LowSpdFlag,
            "fb_joint_pos": [round(rt_out.m_FB_Joint_Pos[j], 4) for j in range(7)],
            "fb_joint_vel": [round(rt_out.m_FB_Joint_Vel[j], 4) for j in range(7)],
            "fb_joint_posE": [round(rt_out.m_FB_Joint_PosE[j], 4) for j in range(7)],
            "fb_joint_cmd": [round(rt_out.m_FB_Joint_Cmd[j], 4) for j in range(7)],
            "fb_joint_cToq": [round(rt_out.m_FB_Joint_CToq[j], 4) for j in range(7)],
            "fb_joint_sToq": [round(rt_out.m_FB_Joint_SToq[j], 4) for j in range(7)],
            "fb_joint_them": [round(rt_out.m_FB_Joint_Them[j], 4) for j in range(7)],
            "est_joint_firc": [round(rt_out.m_EST_Joint_Firc[j], 4) for j in range(7)],
            "est_joint_firc_dot": [
                round(rt_out.m_EST_Joint_Firc_Dot[j], 4) for j in range(7)
            ],
            "est_joint_force": [
                round(rt_out.m_EST_Joint_Force[j], 4) for j in range(7)
            ],
            "est_cart_fn": [round(rt_out.m_EST_Cart_FN[j], 4) for j in range(6)],
        }
        for rt_out in dcss.m_Out
    ]
    result["inputs"] = [
        {
            "rt_in_switch": rt_in.m_RtInSwitch,
            "imp_type": rt_in.m_ImpType,
            "in_frame_serial": rt_in.m_InFrameSerial,
            "frame_miss_cnt": rt_in.m_FrameMissCnt,
            "max_frame_miss_cnt": rt_in.m_MaxFrameMissCnt,
            "sys_cyc": rt_in.m_SysCyc,
            "sys_cyc_miss_cnt": rt_in.m_SysCycMissCnt,
            "max_sys_cyc_miss_cnt": rt_in.m_MaxSysCycMissCnt,
            "tool_kine": [round(rt_in.m_ToolKine[j], 4) for j in range(6)],
            "tool_dyn": [round(rt_in.m_ToolDyn[j], 4) for j in range(10)],
            "joint_cmd_pos": [round(rt_in.m_Joint_CMD_Pos[j], 4) for j in range(7)],
            "joint_vel_ratio": rt_in.m_Joint_Vel_Ratio,
            "joint_acc_ratio": rt_in.m_Joint_Acc_Ratio,
            "joint_k": [round(rt_in.m_Joint_K[j], 4) for j in range(7)],
            "joint_d": [round(rt_in.m_Joint_D[j], 4) for j in range(7)],
            "drag_sp_type": rt_in.m_DragSpType,
            "drag_sp_para": [round(rt_in.m_DragSpPara[j], 4) for j in range(6)],
            "cart_kd_type": rt_in.m_Cart_KD_Type,
            "cart_k": [round(rt_in.m_Cart_K[j], 4) for j in range(6)],
            "cart_d": [round(rt_in.m_Cart_D[j], 4) for j in range(6)],
            "cart_kn": round(rt_in.m_Cart_KN, 4),
            "cart_dn": round(rt_in.m_Cart_DN, 4),
            "force_fb_type": rt_in.m_Force_FB_Type,
            "force_type": rt_in.m_Force_Type,
            "force_dir": [round(rt_in.m_Force_Dir[j], 4) for j in range(6)],
            "force_pidul": [round(rt_in.m_Force_PIDUL[j], 4) for j in range(7)],
            "force_adj_lmt": round(rt_in.m_Force_AdjLmt, 4),
            "force_cmd": round(rt_in.m_Force_Cmd, 4),
            "set_tags": list(rt_in.m_SET_Tags),
            "update_tags": list(rt_in.m_Update_Tags),
            "pvt_id": rt_in.m_PvtID,
            "pvt_id_update": rt_in.m_PvtID_Update,
            "pvt_run_id": rt_in.m_Pvt_RunID,
            "pvt_run_state": rt_in.m_Pvt_RunState,
        }
        for rt_in in dcss.m_In
    ]
    result["ParaName"] = [list(dcss.m_ParaName)]
    result["ParaType"] = [dcss.m_ParaType]
    result["ParaIns"] = [dcss.m_ParaIns]
    result["ParaValueI"] = [dcss.m_ParaValueI]
    result["ParaValueF"] = [dcss.m_ParaValueF]
    result["ParaCmdSerial"] = [dcss.m_ParaCmdSerial]
    result["ParaRetSerial"] = [dcss.m_ParaRetSerial]
    return result


arm_err_code = {
    "1": "总线拓扑异常",
    "2": "伺服故障",
    "3": "PVT异常",
    "4": "请求进位置失败",
    "5": "进位置失败",
    "6": "请求进扭矩失败",
    "7": "进扭矩失败",
    "8": "请求上伺服失败",
    "9": "上伺服失败",
    "10": "请求下伺服失败",
    "11": "下伺服失败",
    "12": "内部错",
    "13": "急停",
    "14": "配置文件选择了浮动基座选项，但是UMI设置在配置文件未开",
    "15": "PDO数据异常",
    "16": "手臂为虚拟轴",
}
arm_err_code_EN = {
    "1": "Bus topology error",
    "2": "Servo failure",
    "3": "PVT error",
    "4": "Failed to request position advance",
    "5": "Failed to advance position",
    "6": "Failed to request torque advance",
    "7": "Failed to advance torque",
    "8": "Failed to request servo up",
    "9": "Failed to request servo up",
    "10": "Failed to request servo down",
    "11": "Failed to request servo down",
    "12": "Internal error",
    "13": "Emergency stop",
    "14": "Floating base option selected in configuration file, but UMI setting not enabled in configuration file",
    "15": "PDO abnormal",
    "16": "Arm is virtual",
}
fault_code_dict_CN = {
    "0x2280": "驱动器短路",
    "0x2310": "U相输出电流过大",
    "0x2311": "V相输出电流过大",
    "0x2320": "驱动器硬件过流",
    "0x2330": "驱动器输出对地短路",
    "0x3130": "主电源输入异常",
    "0x3210": "直流母线过压",
    "0x3220": "直流母线欠压",
    "0x4210": "功率模块过热",
    "0x6010": "CPU1 看门狗溢出",
    "0x6011": "CPU2 看门狗溢出",
    "0x7112": "能耗制动电阻过载",
    "0x8311": "电机持续过载",
    "0x8611": "位置跟随误差过大",
    "0x8612": "正向软限位",
    "0x8613": "负向软限位",
    "0x8800": "编码器数据溢出",
    "0x8801": "保留",
    "0xFF00": "CPU1 工作异常",
    "0xFF01": "CPU2 工作异常",
    "0xFF02": "CPU1 内存异常",
    "0xFF03": "CPU2 内存异常",
    "0xFF04": "CPU 内存冲突",
    "0xFF05": "磁极定位错误",
    "0xFF06": "编码器数据异常",
    "0xFF07": "编码器通信异常",
    "0xFF08": "编码器通信超时",
    "0xFF09": "编码器内部异常1",
    "0xFF10": "驱动器其它轴异常",
    "0xFF11": "电机抱闸断线",
    "0xFF12": "保留",
    "0xFF13": "保留",
    "0xFF14": "控制编码器超速",
    "0xFF15": "驱动器持续过载",
    "0xFF16": "保留",
    "0xFF17": "驱动器输出缺相",
    "0xFF18": "电机失速",
    "0xFF19": "协处理器通讯异常",
    "0xFF20": "编码器AB信号变化异常",
    "0xFF21": "电流跟随误差过大",
    "0xFF22": "位置目标值异常",
    "0xFF23": "编码器上电位置异常",
    "0xFF24": "位置目标值溢出",
    "0xFF25": "电机抱闸异常",
    "0xFF26": "控制电源欠压",
    "0xFF27": "STO1 触发",
    "0xFF28": "STO2 触发",
    "0xFF29": "正向硬限位开关触发",
    "0xFF30": "负向硬限位开关触发",
    "0xFF31": "电机超速",
    "0xFF32": "急停输入开关触发",
    "0xFF33": "转矩饱和检测故障",
    "0xFF34": "速度跟随误差过大",
    "0xFF35": "驱动器过流2",
    "0xFF36": "寻原点失效",
    "0xFF37": "EtherCAT过程数据错误",
    "0xFF38": "EtherCAT总线指令非法",
    "0xFF39": "EtherCAT通讯周期错误",
    "0xFF40": "位置规划运行错误",
    "0xFF41": "EtherCAT非法同步模式",
    "0xFF42": "位置目标值超出设定范围",
    "0xFF43": "整流模块过热",
    "0xFF44": "散热器过热",
    "0xFF45": "电机U相持续过载",
    "0xFF46": "电机V相持续过载",
    "0xFF48": "保留",
    "0xFF49": "驱动器内部异常",
    "0xFF50": "限位开关异常",
    "0xFF51": "EtherCAT总线通讯异常",
    "0xFF52": "接口编码器分辨率变更",
    "0xFF53": "编码器过热",
    "0xFF54": "编码器电池欠电压故障",
    "0xFF55": "保留",
    "0xFF56": "保留",
    "0xFF57": "控制模式设定错误",
    "0xFF58": "上电位置偏差过大",
    "0xFF59": "编码器加速度异常故障",
    "0xFF60": "电机堵转",
    "0xFF61": "电机过热",
    "0xFF62": "增量式编码器Z信号异常",
    "0xFF63": "写EPROM数据异常",
    "0xFF64": "读EPROM数据异常",
    "0xFF65": "控制机功率异常",
    "0xFF66": "拖曳使能异常",
    "0xFF67": "CPU过热",
    "0xFF68": "CPU1过载",
    "0xFF69": "CPU2过载",
    "0xFF70": "CPU1握手失效",
    "0xFF71": "DriveMaster通讯超时",
    "0xFF72": "保留",
    "0xFF73": "力矩传感器异常",
    "0xFF74": "保留",
    "0xFF75": "ESC配置EEPROM异常",
    "0xFF76": "ESC内部访问错误",
    "0xFF77": "伺服使能未准备好",
    "0xFF78": "CPU2握手失败",
    "0xFF79": "CPU1主任务超时",
    "0xFF80": "主电源掉电",
    "0xFF81": "直流母线充电继电器异常",
    "0xFF82": "CPU内部错误",
    "0xFF83": "位置实际值溢出",
    "0xFF84": "保留",
    "0xFF85": "编码器内部异常2",
    "0xFF86": "保留",
    "0xFF87": "编码器内部异常3",
    "0xFF88": "保留",
    "0xFF89": "保留",
    "0xFF8A": "STO1电路诊断异常",
    "0xFF8B": "STO2电路诊断异常",
    "0xFF8C": "霍尔信号异常",
    "0xFF8D": "编码器霍尔-AB信号欠相异常",
    "0xFF8E": "第2位置跟随误差过大",
    "0xFF8F": "STO接线异常",
    "0xFF90": "第2速度跟随误差过大",
    "0xFF91": "驱动器内部异常2",
}
fault_code_dict_EN = {
    "0x2280": "Drive short circuit",
    "0x2310": "U-phase output overcurrent",
    "0x2311": "V-phase output overcurrent",
    "0x2320": "Drive hardware overcurrent",
    "0x2330": "Drive output short to ground",
    "0x3130": "Main power input abnormal",
    "0x3210": "DC bus overvoltage",
    "0x3220": "DC bus undervoltage",
    "0x4210": "Power module overtemperature",
    "0x6010": "CPU1 watchdog timeout",
    "0x6011": "CPU2 watchdog timeout",
    "0x7112": "Dynamic braking resistor overload",
    "0x8311": "Motor continuous overload",
    "0x8611": "Position following error too large",
    "0x8612": "Positive software limit",
    "0x8613": "Negative software limit",
    "0x8800": "Encoder data overflow",
    "0x8801": "Reserved",
    "0xFF00": "CPU1 operation abnormal",
    "0xFF01": "CPU2 operation abnormal",
    "0xFF02": "CPU1 memory abnormal",
    "0xFF03": "CPU2 memory abnormal",
    "0xFF04": "CPU memory conflict",
    "0xFF05": "Magnetic pole positioning error",
    "0xFF06": "Encoder data abnormal",
    "0xFF07": "Encoder communication abnormal",
    "0xFF08": "Encoder communication timeout",
    "0xFF09": "Encoder internal error 1",
    "0xFF10": "Other drive axis abnormal",
    "0xFF11": "Motor brake disconnection",
    "0xFF12": "Reserved",
    "0xFF13": "Reserved",
    "0xFF14": "Control encoder overspeed",
    "0xFF15": "Drive continuous overload",
    "0xFF16": "Reserved",
    "0xFF17": "Drive output missing phase",
    "0xFF18": "Motor stall",
    "0xFF19": "Coprocessor communication abnormal",
    "0xFF20": "Encoder AB signal change abnormal",
    "0xFF21": "Current following error too large",
    "0xFF22": "Position target value abnormal",
    "0xFF23": "Encoder power-on position abnormal",
    "0xFF24": "Position target value overflow",
    "0xFF25": "Motor brake abnormal",
    "0xFF26": "Control power undervoltage",
    "0xFF27": "STO1 triggered",
    "0xFF28": "STO2 triggered",
    "0xFF29": "Positive hardware limit switch triggered",
    "0xFF30": "Negative hardware limit switch triggered",
    "0xFF31": "Motor overspeed",
    "0xFF32": "Emergency stop input switch triggered",
    "0xFF33": "Torque saturation detection fault",
    "0xFF34": "Speed following error too large",
    "0xFF35": "Drive overcurrent 2",
    "0xFF36": "Homing failed",
    "0xFF37": "EtherCAT process data error",
    "0xFF38": "EtherCAT bus command illegal",
    "0xFF39": "EtherCAT communication cycle error",
    "0xFF40": "Position planning operation error",
    "0xFF41": "EtherCAT illegal sync mode",
    "0xFF42": "Position target value out of range",
    "0xFF43": "Rectifier module overtemperature",
    "0xFF44": "Heatsink overtemperature",
    "0xFF45": "Motor U-phase continuous overload",
    "0xFF46": "Motor V-phase continuous overload",
    "0xFF48": "Reserved",
    "0xFF49": "Drive internal error",
    "0xFF50": "Limit switch abnormal",
    "0xFF51": "EtherCAT bus communication abnormal",
    "0xFF52": "Interface encoder resolution changed",
    "0xFF53": "Encoder overtemperature",
    "0xFF54": "Encoder battery undervoltage fault",
    "0xFF55": "Reserved",
    "0xFF56": "Reserved",
    "0xFF57": "Control mode setting error",
    "0xFF58": "Power-on position deviation too large",
    "0xFF59": "Encoder acceleration abnormal fault",
    "0xFF60": "Motor locked rotor",
    "0xFF61": "Motor overtemperature",
    "0xFF62": "Incremental encoder Z signal abnormal",
    "0xFF63": "Write EPROM data abnormal",
    "0xFF64": "Read EPROM data abnormal",
    "0xFF65": "Control/power module mismatch",
    "0xFF66": "Drag enable abnormal",
    "0xFF67": "CPU overtemperature",
    "0xFF68": "CPU1 overload",
    "0xFF69": "CPU2 overload",
    "0xFF70": "CPU1 handshake failure",
    "0xFF71": "DriveMaster communication timeout",
    "0xFF72": "Reserved",
    "0xFF73": "Torque sensor abnormal",
    "0xFF74": "Reserved",
    "0xFF75": "ESC configuration EEPROM abnormal",
    "0xFF76": "ESC internal access error",
    "0xFF77": "Servo enable not ready",
    "0xFF78": "CPU2 handshake failure",
    "0xFF79": "CPU1 main task timeout",
    "0xFF80": "Main power loss",
    "0xFF81": "DC bus charging relay abnormal",
    "0xFF82": "CPU internal error",
    "0xFF83": "Actual position value overflow",
    "0xFF84": "Reserved",
    "0xFF85": "Encoder internal error 2",
    "0xFF86": "Reserved",
    "0xFF87": "Encoder internal error 3",
    "0xFF88": "Reserved",
    "0xFF89": "Reserved",
    "0xFF8A": "STO1 circuit diagnosis abnormal",
    "0xFF8B": "STO2 circuit diagnosis abnormal",
    "0xFF8C": "Hall signal abnormal",
    "0xFF8D": "Encoder Hall-AB signal missing phase abnormal",
    "0xFF8E": "2nd position following error too large",
    "0xFF8F": "STO wiring abnormal",
    "0xFF90": "2nd speed following error too large",
    "0xFF91": "Drive internal error 2",
}


def get_fault_descriptions(fault_codes_list, lang="CN"):
    """Format known servo fault codes using the selected CN or EN dictionary, preserving unknown codes."""
    fault_dict = fault_code_dict_CN
    if lang == "EN":
        fault_dict = fault_code_dict_EN
    if not fault_codes_list:
        return "None fault codes list"
    all_descriptions = []
    for joint_idx, code in enumerate(fault_codes_list, 1):
        code_str = str(code)
        if isinstance(code, int):
            code_str = hex(code)
        code_str_lower = code_str.lower()
        if code_str in ["0x0000", "0000", "0", "0x0", "0X0", ""]:
            continue
        fault_name = None
        if code_str in fault_dict:
            fault_name = fault_dict[code_str]
        elif code_str_lower in fault_dict:
            fault_name = fault_dict[code_str_lower]
        else:
            fault_name = f"unknown error({code_str})"
        if fault_name:
            all_descriptions.append(f"joint {joint_idx}: {code_str} - {fault_name}")
    if not all_descriptions:
        return "None"
    elif len(all_descriptions) == 1:
        return all_descriptions[0]
    else:
        result = "Fault information for each joint:\n"
        for i, desc in enumerate(all_descriptions, 1):
            result += f"{i}. {desc}\n"
        return result.strip()


tools_cfg = {
    "arm0": {
        "tool-1": {"dyn": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "kine": [0, 0, 0, 0, 0, 0]},
        "tool-2": {"dyn": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "kine": [0, 0, 0, 0, 0, 0]},
        "tool-3": {"dyn": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "kine": [0, 0, 0, 0, 0, 0]},
        "tool-4": {"dyn": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "kine": [0, 0, 0, 0, 0, 0]},
        "tool-5": {"dyn": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "kine": [0, 0, 0, 0, 0, 0]},
    },
    "arm1": {
        "tool-1": {"dyn": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "kine": [0, 0, 0, 0, 0, 0]},
        "tool-2": {"dyn": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "kine": [0, 0, 0, 0, 0, 0]},
        "tool-3": {"dyn": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "kine": [0, 0, 0, 0, 0, 0]},
        "tool-4": {"dyn": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "kine": [0, 0, 0, 0, 0, 0]},
        "tool-5": {"dyn": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "kine": [0, 0, 0, 0, 0, 0]},
    },
    "current_tool": {"arm0": None, "arm1": None},
}
