// Nanobind bindings maintained alongside the SDK headers and Python facade.
#include "MarvinSDK.h"
#include "bridge.h"
#include "control_pointset.h"

static auto bind_CheckSDKTypeCompat(nb::object a0) {
    Output<int> p0(a0);
    auto result = CheckSDKTypeCompat(&p0.data);
    p0.commit();
    return result;
}
static auto bind_OnLinkTo(nb::object a0, nb::object a1, nb::object a2, nb::object a3) {
    auto p0 = scalar<unsigned char>(a0);
    auto p1 = scalar<unsigned char>(a1);
    auto p2 = scalar<unsigned char>(a2);
    auto p3 = scalar<unsigned char>(a3);
    auto result = OnLinkTo(p0, p1, p2, p3);
    return result;
}
static auto bind_OnRelease() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) return true;
    auto result = OnRelease();
    return result;
}
static auto bind_OnGetSDKVersion() {
    auto result = OnGetSDKVersion();
    return result;
}
static auto bind_OnUpdateSystem(nb::object a0) {
    Text p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnUpdateSystem(p0.data.data());
    return result;
}
static auto bind_OnDownloadLog(nb::object a0) {
    Text p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnDownloadLog(p0.data.data());
    return result;
}
static auto bind_OnSendFile(nb::object a0, nb::object a1) {
    Text p0(a0);
    Text p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSendFile(p0.data.data(), p1.data.data());
    return result;
}
static auto bind_OnRecvFile(nb::object a0, nb::object a1) {
    Text p0(a0);
    Text p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnRecvFile(p0.data.data(), p1.data.data());
    return result;
}
static auto bind_OnGetBuf(nb::object a0) {
    Buffer<DCSS> p0(a0);
    auto result = OnGetBuf(p0.data);
    p0.commit();
    return result;
}
static auto bind_OnEMG_A() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    OnEMG_A();
}
static auto bind_OnEMG_B() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    OnEMG_B();
}
static auto bind_OnEMG_AB() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    OnEMG_AB();
}
static auto bind_OnServoReset_A(nb::object a0) {
    auto p0 = scalar<int>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    OnServoReset_A(p0);
}
static auto bind_OnServoReset_B(nb::object a0) {
    auto p0 = scalar<int>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    OnServoReset_B(p0);
}
static auto bind_OnGetServoErr_A(nb::object a0) {
    Buffer<long, 7> p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    OnGetServoErr_A(p0.data);
    p0.commit();
}
static auto bind_OnGetServoErr_B(nb::object a0) {
    Buffer<long, 7> p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    OnGetServoErr_B(p0.data);
    p0.commit();
}
static auto bind_OnLogOn() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    OnLogOn();
}
static auto bind_OnLogOff() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    OnLogOff();
}
static auto bind_OnLocalLogOn() {
    OnLocalLogOn();
}
static auto bind_OnLocalLogOff() {
    OnLocalLogOff();
}
static auto bind_OnSendPVT_A(nb::object a0, nb::object a1) {
    Text p0(a0);
    auto p1 = scalar<long>(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSendPVT_A(p0.data.data(), p1);
    return result;
}
static auto bind_OnSendPVT_B(nb::object a0, nb::object a1) {
    Text p0(a0);
    auto p1 = scalar<long>(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSendPVT_B(p0.data.data(), p1);
    return result;
}
static auto bind_OnSetIntPara(nb::object a0, nb::object a1) {
    Buffer<char, 30> p0(a0);
    auto p1 = scalar<long>(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetIntPara(p0.data, p1);
    p0.commit();
    return result;
}
static auto bind_OnSetFloatPara(nb::object a0, nb::object a1) {
    Buffer<char, 30> p0(a0);
    auto p1 = scalar<double>(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetFloatPara(p0.data, p1);
    p0.commit();
    return result;
}
static auto bind_OnGetIntPara(nb::object a0, nb::object a1) {
    Buffer<char, 30> p0(a0);
    Output<long> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnGetIntPara(p0.data, &p1.data);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnGetFloatPara(nb::object a0, nb::object a1) {
    Buffer<char, 30> p0(a0);
    Output<double> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnGetFloatPara(p0.data, &p1.data);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnSavePara() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSavePara();
    return result;
}
static auto bind_OnSaveGatherData(nb::object a0) {
    Text p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSaveGatherData(p0.data.data());
    return result;
}
static auto bind_OnSaveGatherDataCSV(nb::object a0) {
    Text p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSaveGatherDataCSV(p0.data.data());
    return result;
}
static auto bind_OnClearSet() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnClearSet();
    return result;
}
static auto bind_OnClearErr_A() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    OnClearErr_A();
}
static auto bind_OnClearErr_B() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    OnClearErr_B();
}
static auto bind_OnStartGather(nb::object a0, nb::object a1, nb::object a2) {
    auto p0 = scalar<long>(a0);
    Buffer<long, 35> p1(a1);
    auto p2 = scalar<long>(a2);
    if (p0 < 0 || p0 > 35) throw nb::value_error("target count must be in 0..35");
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnStartGather(p0, p1.data, p2);
    p1.commit();
    return result;
}
static auto bind_OnStopGather() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnStopGather();
    return result;
}
static auto bind_OnSetTool_A(nb::object a0, nb::object a1) {
    Buffer<double, 6> p0(a0);
    Buffer<double, 10> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetTool_A(p0.data, p1.data);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnSetTool_B(nb::object a0, nb::object a1) {
    Buffer<double, 6> p0(a0);
    Buffer<double, 10> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetTool_B(p0.data, p1.data);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnSetJointLmt_A(nb::object a0, nb::object a1) {
    auto p0 = scalar<int>(a0);
    auto p1 = scalar<int>(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetJointLmt_A(p0, p1);
    return result;
}
static auto bind_OnSetJointLmt_B(nb::object a0, nb::object a1) {
    auto p0 = scalar<int>(a0);
    auto p1 = scalar<int>(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetJointLmt_B(p0, p1);
    return result;
}
static auto bind_OnSetJointKD_A(nb::object a0, nb::object a1) {
    Buffer<double, 7> p0(a0);
    Buffer<double, 7> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetJointKD_A(p0.data, p1.data);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnSetJointKD_B(nb::object a0, nb::object a1) {
    Buffer<double, 7> p0(a0);
    Buffer<double, 7> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetJointKD_B(p0.data, p1.data);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnSetCartKD_A(nb::object a0, nb::object a1, nb::object a2) {
    Buffer<double, 7> p0(a0);
    Buffer<double, 7> p1(a1);
    auto p2 = scalar<int>(a2);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetCartKD_A(p0.data, p1.data, p2);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnSetCartKD_B(nb::object a0, nb::object a1, nb::object a2) {
    Buffer<double, 7> p0(a0);
    Buffer<double, 7> p1(a1);
    auto p2 = scalar<int>(a2);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetCartKD_B(p0.data, p1.data, p2);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnSetEefRot_A(nb::object a0, nb::object a1) {
    auto p0 = scalar<int>(a0);
    Buffer<double, 7> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetEefRot_A(p0, p1.data);
    p1.commit();
    return result;
}
static auto bind_OnSetEefRot_B(nb::object a0, nb::object a1) {
    auto p0 = scalar<int>(a0);
    Buffer<double, 7> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetEefRot_B(p0, p1.data);
    p1.commit();
    return result;
}
static auto bind_OnSetForceCtrPara_A(nb::object a0, nb::object a1, nb::object a2, nb::object a3) {
    auto p0 = scalar<int>(a0);
    Buffer<double, 6> p1(a1);
    Buffer<double, 7> p2(a2);
    auto p3 = scalar<double>(a3);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetForceCtrPara_A(p0, p1.data, p2.data, p3);
    p1.commit();
    p2.commit();
    return result;
}
static auto bind_OnSetForceCtrPara_B(nb::object a0, nb::object a1, nb::object a2, nb::object a3) {
    auto p0 = scalar<int>(a0);
    Buffer<double, 6> p1(a1);
    Buffer<double, 7> p2(a2);
    auto p3 = scalar<double>(a3);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetForceCtrPara_B(p0, p1.data, p2.data, p3);
    p1.commit();
    p2.commit();
    return result;
}
static auto bind_OnSetForceCmd_A(nb::object a0) {
    auto p0 = scalar<double>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetForceCmd_A(p0);
    return result;
}
static auto bind_OnSetForceCmd_B(nb::object a0) {
    auto p0 = scalar<double>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetForceCmd_B(p0);
    return result;
}
static auto bind_OnSetTargetState_A(nb::object a0) {
    auto p0 = scalar<int>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetTargetState_A(p0);
    return result;
}
static auto bind_OnSetTargetState_B(nb::object a0) {
    auto p0 = scalar<int>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetTargetState_B(p0);
    return result;
}
static auto bind_OnSetImpType_A(nb::object a0) {
    auto p0 = scalar<int>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetImpType_A(p0);
    return result;
}
static auto bind_OnSetImpType_B(nb::object a0) {
    auto p0 = scalar<int>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetImpType_B(p0);
    return result;
}
static auto bind_OnSetDragSpace_A(nb::object a0) {
    auto p0 = scalar<int>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetDragSpace_A(p0);
    return result;
}
static auto bind_OnSetDragSpace_B(nb::object a0) {
    auto p0 = scalar<int>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetDragSpace_B(p0);
    return result;
}
static auto bind_OnSetJointCmdPos_A(nb::object a0) {
    Buffer<double, 7> p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetJointCmdPos_A(p0.data);
    p0.commit();
    return result;
}
static auto bind_OnSetJointCmdPos_B(nb::object a0) {
    Buffer<double, 7> p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetJointCmdPos_B(p0.data);
    p0.commit();
    return result;
}
static auto bind_OnSetPVT_A(nb::object a0) {
    auto p0 = scalar<int>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetPVT_A(p0);
    return result;
}
static auto bind_OnSetPVT_B(nb::object a0) {
    auto p0 = scalar<int>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetPVT_B(p0);
    return result;
}
static auto bind_OnSetSend() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetSend();
    return result;
}
static auto bind_OnSetSendWaitResponse(nb::object a0) {
    auto p0 = scalar<long>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetSendWaitResponse(p0);
    return result;
}
static auto bind_OnInitPlnLmt(nb::object a0) {
    Text p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnInitPlnLmt(p0.data.data());
    return result;
}
static auto bind_OnSetPlnJoint_A(nb::object a0, nb::object a1, nb::object a2, nb::object a3) {
    Buffer<double, 7> p0(a0);
    Buffer<double, 7> p1(a1);
    auto p2 = scalar<double>(a2);
    auto p3 = scalar<double>(a3);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetPlnJoint_A(p0.data, p1.data, p2, p3);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnSetPlnJoint_B(nb::object a0, nb::object a1, nb::object a2, nb::object a3) {
    Buffer<double, 7> p0(a0);
    Buffer<double, 7> p1(a1);
    auto p2 = scalar<double>(a2);
    auto p3 = scalar<double>(a3);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetPlnJoint_B(p0.data, p1.data, p2, p3);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnSetPlnCart_A(nb::object a0) {
    ControlPoints p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetPlnCart_A(&p0.data);
    return result;
}
static auto bind_OnSetPlnCart_B(nb::object a0) {
    ControlPoints p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetPlnCart_B(&p0.data);
    return result;
}
static auto bind_OnStopPlnJoint_A() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnStopPlnJoint_A();
    return result;
}
static auto bind_OnStopPlnJoint_B() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnStopPlnJoint_B();
    return result;
}
static auto bind_CoRunPlnJoint(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5) {
    Buffer<double, 7> p0(a0);
    Buffer<double, 7> p1(a1);
    Buffer<double, 7> p2(a2);
    Buffer<double, 7> p3(a3);
    auto p4 = scalar<double>(a4);
    auto p5 = scalar<double>(a5);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = CoRunPlnJoint(p0.data, p1.data, p2.data, p3.data, p4, p5);
    p0.commit();
    p1.commit();
    p2.commit();
    p3.commit();
    return result;
}
static auto bind_CoRunPlnCart(nb::object a0, nb::object a1) {
    ControlPoints p0(a0);
    ControlPoints p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = CoRunPlnCart(&p0.data, &p1.data);
    return result;
}
static auto bind_CoStopPln() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = CoStopPln();
    return result;
}
static auto bind_OnClearChDataA() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnClearChDataA();
    return result;
}
static auto bind_OnClearChDataB() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnClearChDataB();
    return result;
}
static auto bind_OnGetChDataA(nb::object a0, nb::object a1) {
    Buffer<unsigned char, 256> p0(a0);
    Output<long> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnGetChDataA(p0.data, &p1.data);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnSetChDataA(nb::object a0, nb::object a1, nb::object a2) {
    Buffer<unsigned char, 256> p0(a0);
    auto p1 = scalar<long>(a1);
    auto p2 = scalar<long>(a2);
    if (p1 < 0 || p1 > 256) throw nb::value_error("channel payload must be in 0..256 bytes");
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetChDataA(p0.data, p1, p2);
    p0.commit();
    return result;
}
static auto bind_OnGetChDataB(nb::object a0, nb::object a1) {
    Buffer<unsigned char, 256> p0(a0);
    Output<long> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnGetChDataB(p0.data, &p1.data);
    p0.commit();
    p1.commit();
    return result;
}
static auto bind_OnSetChDataB(nb::object a0, nb::object a1, nb::object a2) {
    Buffer<unsigned char, 256> p0(a0);
    auto p1 = scalar<long>(a1);
    auto p2 = scalar<long>(a2);
    if (p1 < 0 || p1 > 256) throw nb::value_error("channel payload must be in 0..256 bytes");
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetChDataB(p0.data, p1, p2);
    p0.commit();
    return result;
}
static auto bind_FX_OnSetVelEstStep(nb::object a0, nb::object a1) {
    auto p0 = scalar<char>(a0);
    auto p1 = scalar<long>(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = FX_OnSetVelEstStep(p0, p1);
    return result;
}
static auto bind_FTArmControl(nb::object a0, nb::object a1) {
    auto p0 = scalar<char>(a0);
    Buffer<FTCmd> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = FTArmControl(p0, p1.data[0]);
    return result;
}
static auto bind_OnSetUserSpcfData_A(nb::object a0) {
    auto p0 = scalar<long>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetUserSpcfData_A(p0);
    return result;
}
static auto bind_OnSetUserSpcfData_B(nb::object a0) {
    auto p0 = scalar<long>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetUserSpcfData_B(p0);
    return result;
}
static auto bind_OnSetUserSpcfData(nb::object a0) {
    auto p0 = scalar<long>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetUserSpcfData(p0);
    return result;
}
static auto bind_OnGetRobotName(nb::object a0) {
    Buffer<char, 512> p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnGetRobotName(p0.data);
    p0.commit();
    return result;
}
static auto bind_OnReset6DofForceSensor(nb::object a0) {
    auto p0 = scalar<char>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnReset6DofForceSensor(p0);
    return result;
}
static auto bind_OnSetSystemTime(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5) {
    auto p0 = scalar<int>(a0);
    auto p1 = scalar<int>(a1);
    auto p2 = scalar<int>(a2);
    auto p3 = scalar<int>(a3);
    auto p4 = scalar<int>(a4);
    auto p5 = scalar<int>(a5);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetSystemTime(p0, p1, p2, p3, p4, p5);
    return result;
}
static auto bind_OnSetReboot() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetReboot();
    return result;
}
static auto bind_OnSetStopRunning(nb::object a0) {
    Text p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = OnSetStopRunning(p0.data.data());
    return result;
}
static auto bind_Connect(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4) {
    auto p0 = scalar<unsigned char>(a0);
    auto p1 = scalar<unsigned char>(a1);
    auto p2 = scalar<unsigned char>(a2);
    auto p3 = scalar<unsigned char>(a3);
    auto p4 = scalar<int>(a4);
    auto result = Connect(p0, p1, p2, p3, p4);
    return result;
}
static auto bind_LogSwitch(nb::object a0) {
    auto p0 = scalar<int>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    LogSwitch(p0);
}
static auto bind_EStop(nb::object a0) {
    Text p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    EStop(p0.data.data());
}
static auto bind_ServoReset(nb::object a0, nb::object a1) {
    auto p0 = scalar<char>(a0);
    auto p1 = scalar<int>(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    ServoReset(p0, p1);
}
static auto bind_CheckArmError() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = CheckArmError();
    return result;
}
static auto bind_CheckServoError() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = CheckServoError();
    return result;
}
static auto bind_ClearErr() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    ClearErr();
}
static auto bind_SetTool(nb::object a0, nb::object a1, nb::object a2) {
    auto p0 = scalar<char>(a0);
    Buffer<double, 6> p1(a1);
    Buffer<double, 10> p2(a2);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = SetTool(p0, p1.data, p2.data);
    p1.commit();
    p2.commit();
    return result;
}
static auto bind_SetJointMode(nb::object a0, nb::object a1, nb::object a2) {
    auto p0 = scalar<char>(a0);
    auto p1 = scalar<int>(a1);
    auto p2 = scalar<int>(a2);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = SetJointMode(p0, p1, p2);
    return result;
}
static auto bind_SetImpJointMode(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4) {
    auto p0 = scalar<char>(a0);
    auto p1 = scalar<int>(a1);
    auto p2 = scalar<int>(a2);
    Buffer<double, 7> p3(a3);
    Buffer<double, 7> p4(a4);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = SetImpJointMode(p0, p1, p2, p3.data, p4.data);
    p3.commit();
    p4.commit();
    return result;
}
static auto bind_SetImpCartMode(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6) {
    auto p0 = scalar<char>(a0);
    auto p1 = scalar<int>(a1);
    auto p2 = scalar<int>(a2);
    Buffer<double, 7> p3(a3);
    Buffer<double, 7> p4(a4);
    auto p5 = scalar<int>(a5);
    Buffer<double, 7> p6(a6);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = SetImpCartMode(p0, p1, p2, p3.data, p4.data, p5, p6.data);
    p3.commit();
    p4.commit();
    p6.commit();
    return result;
}
static auto bind_SetJointPostionCmd(nb::object a0, nb::object a1) {
    auto p0 = scalar<char>(a0);
    Buffer<double, 7> p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = SetJointPostionCmd(p0, p1.data);
    p1.commit();
    return result;
}
static auto bind_SetImpForceMode(nb::object a0, nb::object a1, nb::object a2) {
    auto p0 = scalar<char>(a0);
    Buffer<double, 6> p1(a1);
    auto p2 = scalar<double>(a2);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = SetImpForceMode(p0, p1.data, p2);
    p1.commit();
    return result;
}
static auto bind_SetForceCmd(nb::object a0, nb::object a1) {
    auto p0 = scalar<char>(a0);
    auto p1 = scalar<double>(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = SetForceCmd(p0, p1);
    return result;
}
static auto bind_PlnInit(nb::object a0) {
    Text p0(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = PlnInit(p0.data.data());
    return result;
}
static auto bind_RunPlnJoint(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4) {
    auto p0 = scalar<char>(a0);
    Buffer<double, 7> p1(a1);
    Buffer<double, 7> p2(a2);
    auto p3 = scalar<double>(a3);
    auto p4 = scalar<double>(a4);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = RunPlnJoint(p0, p1.data, p2.data, p3, p4);
    p1.commit();
    p2.commit();
    return result;
}
static auto bind_RunPlnCart(nb::object a0, nb::object a1) {
    auto p0 = scalar<char>(a0);
    ControlPoints p1(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = RunPlnCart(p0, &p1.data);
    return result;
}
static auto bind_StopPln(nb::object a0) {
    auto p0 = scalar<char>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = StopPln(p0);
    return result;
}
static auto bind_SendPVT(nb::object a0, nb::object a1, nb::object a2) {
    auto p0 = scalar<char>(a0);
    Text p1(a1);
    auto p2 = scalar<long>(a2);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = SendPVT(p0, p1.data.data(), p2);
    return result;
}
static auto bind_RunPVT(nb::object a0, nb::object a1) {
    auto p0 = scalar<char>(a0);
    auto p1 = scalar<int>(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = RunPVT(p0, p1);
    return result;
}
static auto bind_SetJointDrag(nb::object a0) {
    auto p0 = scalar<char>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = SetJointDrag(p0);
    return result;
}
static auto bind_SetCartDrag(nb::object a0, nb::object a1) {
    auto p0 = scalar<char>(a0);
    auto p1 = scalar<char>(a1);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = SetCartDrag(p0, p1);
    return result;
}
static auto bind_ExitDrag(nb::object a0) {
    auto p0 = scalar<char>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = ExitDrag(p0);
    return result;
}
static auto bind_ClearChData(nb::object a0) {
    auto p0 = scalar<char>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = ClearChData(p0);
    return result;
}
static auto bind_GetChData(nb::object a0, nb::object a1, nb::object a2) {
    auto p0 = scalar<char>(a0);
    Buffer<unsigned char, 256> p1(a1);
    Output<long> p2(a2);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = GetChData(p0, p1.data, &p2.data);
    p1.commit();
    p2.commit();
    return result;
}
static auto bind_SetChData(nb::object a0, nb::object a1, nb::object a2, nb::object a3) {
    auto p0 = scalar<char>(a0);
    Buffer<unsigned char, 256> p1(a1);
    auto p2 = scalar<long>(a2);
    auto p3 = scalar<long>(a3);
    if (p2 < 0 || p2 > 256) throw nb::value_error("channel payload must be in 0..256 bytes");
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = SetChData(p0, p1.data, p2, p3);
    p1.commit();
    return result;
}
static auto bind_StartCollectData(nb::object a0, nb::object a1, nb::object a2) {
    auto p0 = scalar<long>(a0);
    Buffer<long, 35> p1(a1);
    auto p2 = scalar<long>(a2);
    if (p0 < 0 || p0 > 35) throw nb::value_error("target count must be in 0..35");
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = StartCollectData(p0, p1.data, p2);
    p1.commit();
    return result;
}
static auto bind_StopCollectData() {
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = StopCollectData();
    return result;
}
static auto bind_Disable(nb::object a0) {
    auto p0 = scalar<char>(a0);
    DCSS instance_check{}; if (!CRobot::OnGetBuf(&instance_check)) throw std::runtime_error("call connect before using control commands");
    auto result = Disable(p0);
    return result;
}
static auto bind_ValidateArm(nb::object a0) {
    auto p0 = scalar<char>(a0);
    auto result = ValidateArm(p0);
    return result;
}
NB_MODULE(_control, m) {
m.def("CheckSDKTypeCompat", &bind_CheckSDKTypeCompat, nb::arg("pByteOrder"));
m.def("OnLinkTo", &bind_OnLinkTo, nb::arg("ip1"), nb::arg("ip2"), nb::arg("ip3"), nb::arg("ip4"));
m.def("OnRelease", &bind_OnRelease);
m.def("OnGetSDKVersion", &bind_OnGetSDKVersion);
m.def("OnUpdateSystem", &bind_OnUpdateSystem, nb::arg("local_path"));
m.def("OnDownloadLog", &bind_OnDownloadLog, nb::arg("local_path"));
m.def("OnSendFile", &bind_OnSendFile, nb::arg("local_file"), nb::arg("remote_file"));
m.def("OnRecvFile", &bind_OnRecvFile, nb::arg("local_file"), nb::arg("remote_file"));
m.def("OnGetBuf", &bind_OnGetBuf, nb::arg("ret"));
m.def("OnEMG_A", &bind_OnEMG_A);
m.def("OnEMG_B", &bind_OnEMG_B);
m.def("OnEMG_AB", &bind_OnEMG_AB);
m.def("OnServoReset_A", &bind_OnServoReset_A, nb::arg("axis"));
m.def("OnServoReset_B", &bind_OnServoReset_B, nb::arg("axis"));
m.def("OnGetServoErr_A", &bind_OnGetServoErr_A, nb::arg("ErrCode"));
m.def("OnGetServoErr_B", &bind_OnGetServoErr_B, nb::arg("ErrCode"));
m.def("OnLogOn", &bind_OnLogOn);
m.def("OnLogOff", &bind_OnLogOff);
m.def("OnLocalLogOn", &bind_OnLocalLogOn);
m.def("OnLocalLogOff", &bind_OnLocalLogOff);
m.def("OnSendPVT_A", &bind_OnSendPVT_A, nb::arg("local_file"), nb::arg("serial"));
m.def("OnSendPVT_B", &bind_OnSendPVT_B, nb::arg("local_file"), nb::arg("serial"));
m.def("OnSetIntPara", &bind_OnSetIntPara, nb::arg("paraName"), nb::arg("setValue"));
m.def("OnSetFloatPara", &bind_OnSetFloatPara, nb::arg("paraName"), nb::arg("setValue"));
m.def("OnGetIntPara", &bind_OnGetIntPara, nb::arg("paraName"), nb::arg("retValue"));
m.def("OnGetFloatPara", &bind_OnGetFloatPara, nb::arg("paraName"), nb::arg("retValue"));
m.def("OnSavePara", &bind_OnSavePara);
m.def("OnSaveGatherData", &bind_OnSaveGatherData, nb::arg("path"));
m.def("OnSaveGatherDataCSV", &bind_OnSaveGatherDataCSV, nb::arg("path"));
m.def("OnClearSet", &bind_OnClearSet);
m.def("OnClearErr_A", &bind_OnClearErr_A);
m.def("OnClearErr_B", &bind_OnClearErr_B);
m.def("OnStartGather", &bind_OnStartGather, nb::arg("targetNum"), nb::arg("targetID"), nb::arg("recordNum"));
m.def("OnStopGather", &bind_OnStopGather);
m.def("OnSetTool_A", &bind_OnSetTool_A, nb::arg("kinePara"), nb::arg("dynPara"));
m.def("OnSetTool_B", &bind_OnSetTool_B, nb::arg("kinePara"), nb::arg("dynPara"));
m.def("OnSetJointLmt_A", &bind_OnSetJointLmt_A, nb::arg("velRatio"), nb::arg("AccRatio"));
m.def("OnSetJointLmt_B", &bind_OnSetJointLmt_B, nb::arg("velRatio"), nb::arg("AccRatio"));
m.def("OnSetJointKD_A", &bind_OnSetJointKD_A, nb::arg("K"), nb::arg("D"));
m.def("OnSetJointKD_B", &bind_OnSetJointKD_B, nb::arg("K"), nb::arg("D"));
m.def("OnSetCartKD_A", &bind_OnSetCartKD_A, nb::arg("K"), nb::arg("D"), nb::arg("type") = 2);
m.def("OnSetCartKD_B", &bind_OnSetCartKD_B, nb::arg("K"), nb::arg("D"), nb::arg("type") = 2);
m.def("OnSetEefRot_A", &bind_OnSetEefRot_A, nb::arg("fcType"), nb::arg("CartCtrlPara"));
m.def("OnSetEefRot_B", &bind_OnSetEefRot_B, nb::arg("fcType"), nb::arg("CartCtrlPara"));
m.def("OnSetForceCtrPara_A", &bind_OnSetForceCtrPara_A, nb::arg("fcType"), nb::arg("fxDir"), nb::arg("fcCtrlPara"), nb::arg("fcAdjLmt"));
m.def("OnSetForceCtrPara_B", &bind_OnSetForceCtrPara_B, nb::arg("fcType"), nb::arg("fxDir"), nb::arg("fcCtrlPara"), nb::arg("fcAdjLmt"));
m.def("OnSetForceCmd_A", &bind_OnSetForceCmd_A, nb::arg("force"));
m.def("OnSetForceCmd_B", &bind_OnSetForceCmd_B, nb::arg("force"));
m.def("OnSetTargetState_A", &bind_OnSetTargetState_A, nb::arg("state"));
m.def("OnSetTargetState_B", &bind_OnSetTargetState_B, nb::arg("state"));
m.def("OnSetImpType_A", &bind_OnSetImpType_A, nb::arg("type"));
m.def("OnSetImpType_B", &bind_OnSetImpType_B, nb::arg("type"));
m.def("OnSetDragSpace_A", &bind_OnSetDragSpace_A, nb::arg("dgType"));
m.def("OnSetDragSpace_B", &bind_OnSetDragSpace_B, nb::arg("dgType"));
m.def("OnSetJointCmdPos_A", &bind_OnSetJointCmdPos_A, nb::arg("joint"));
m.def("OnSetJointCmdPos_B", &bind_OnSetJointCmdPos_B, nb::arg("joint"));
m.def("OnSetPVT_A", &bind_OnSetPVT_A, nb::arg("id"));
m.def("OnSetPVT_B", &bind_OnSetPVT_B, nb::arg("id"));
m.def("OnSetSend", &bind_OnSetSend);
m.def("OnSetSendWaitResponse", &bind_OnSetSendWaitResponse, nb::arg("time_out"));
m.def("OnInitPlnLmt", &bind_OnInitPlnLmt, nb::arg("path"));
m.def("OnSetPlnJoint_A", &bind_OnSetPlnJoint_A, nb::arg("start_joints"), nb::arg("stop_joints"), nb::arg("vel_ratio"), nb::arg("acc_ratio"));
m.def("OnSetPlnJoint_B", &bind_OnSetPlnJoint_B, nb::arg("start_joints"), nb::arg("stop_joints"), nb::arg("vel_ratio"), nb::arg("acc_ratio"));
m.def("OnSetPlnCart_A", &bind_OnSetPlnCart_A, nb::arg("pset"));
m.def("OnSetPlnCart_B", &bind_OnSetPlnCart_B, nb::arg("pset"));
m.def("OnStopPlnJoint_A", &bind_OnStopPlnJoint_A);
m.def("OnStopPlnJoint_B", &bind_OnStopPlnJoint_B);
m.def("CoRunPlnJoint", &bind_CoRunPlnJoint, nb::arg("start_joints_A"), nb::arg("stop_joints_A"), nb::arg("start_joints_B"), nb::arg("stop_joints_B"), nb::arg("vel_ratio"), nb::arg("acc_ratio"));
m.def("CoRunPlnCart", &bind_CoRunPlnCart, nb::arg("pset0"), nb::arg("pset1"));
m.def("CoStopPln", &bind_CoStopPln);
m.def("OnClearChDataA", &bind_OnClearChDataA);
m.def("OnClearChDataB", &bind_OnClearChDataB);
m.def("OnGetChDataA", &bind_OnGetChDataA, nb::arg("data_ptr"), nb::arg("ret_ch"));
m.def("OnSetChDataA", &bind_OnSetChDataA, nb::arg("data_ptr"), nb::arg("size_int"), nb::arg("set_ch"));
m.def("OnGetChDataB", &bind_OnGetChDataB, nb::arg("data_ptr"), nb::arg("ret_ch"));
m.def("OnSetChDataB", &bind_OnSetChDataB, nb::arg("data_ptr"), nb::arg("size_int"), nb::arg("set_ch"));
m.def("FX_OnSetVelEstStep", &bind_FX_OnSetVelEstStep, nb::arg("arm"), nb::arg("step"));
m.def("FTArmControl", &bind_FTArmControl, nb::arg("arm"), nb::arg("FTCmds"));
m.def("OnSetUserSpcfData_A", &bind_OnSetUserSpcfData_A, nb::arg("data_category"));
m.def("OnSetUserSpcfData_B", &bind_OnSetUserSpcfData_B, nb::arg("data_category"));
m.def("OnSetUserSpcfData", &bind_OnSetUserSpcfData, nb::arg("data_category"));
m.def("OnGetRobotName", &bind_OnGetRobotName, nb::arg("robotName"));
m.def("OnReset6DofForceSensor", &bind_OnReset6DofForceSensor, nb::arg("arm"));
m.def("OnSetSystemTime", &bind_OnSetSystemTime, nb::arg("year"), nb::arg("month"), nb::arg("day"), nb::arg("hour"), nb::arg("minute"), nb::arg("second"));
m.def("OnSetReboot", &bind_OnSetReboot);
m.def("OnSetStopRunning", &bind_OnSetStopRunning, nb::arg("arm"));
m.def("Connect", &bind_Connect, nb::arg("ip1"), nb::arg("ip2"), nb::arg("ip3"), nb::arg("ip4"), nb::arg("log_switch") = 0);
m.def("LogSwitch", &bind_LogSwitch, nb::arg("signal"));
m.def("EStop", &bind_EStop, nb::arg("arm"));
m.def("ServoReset", &bind_ServoReset, nb::arg("arm"), nb::arg("axis"));
m.def("CheckArmError", &bind_CheckArmError);
m.def("CheckServoError", &bind_CheckServoError);
m.def("ClearErr", &bind_ClearErr);
m.def("SetTool", &bind_SetTool, nb::arg("arm"), nb::arg("kinePara"), nb::arg("dynPara"));
m.def("SetJointMode", &bind_SetJointMode, nb::arg("arm"), nb::arg("velRatio"), nb::arg("AccRatio"));
m.def("SetImpJointMode", &bind_SetImpJointMode, nb::arg("arm"), nb::arg("velRatio"), nb::arg("AccRatio"), nb::arg("K"), nb::arg("D"));
m.def("SetImpCartMode", &bind_SetImpCartMode, nb::arg("arm"), nb::arg("velRatio"), nb::arg("AccRatio"), nb::arg("K"), nb::arg("D"), nb::arg("RotType"), nb::arg("CartCtrlPara"));
m.def("SetJointPostionCmd", &bind_SetJointPostionCmd, nb::arg("arm"), nb::arg("joint"));
m.def("SetImpForceMode", &bind_SetImpForceMode, nb::arg("arm"), nb::arg("fxDir"), nb::arg("fcAdjLmt"));
m.def("SetForceCmd", &bind_SetForceCmd, nb::arg("arm"), nb::arg("force"));
m.def("PlnInit", &bind_PlnInit, nb::arg("path"));
m.def("RunPlnJoint", &bind_RunPlnJoint, nb::arg("arm"), nb::arg("start_joints"), nb::arg("stop_joints"), nb::arg("vel_ratio"), nb::arg("acc_ratio"));
m.def("RunPlnCart", &bind_RunPlnCart, nb::arg("arm"), nb::arg("pset"));
m.def("StopPln", &bind_StopPln, nb::arg("arm"));
m.def("SendPVT", &bind_SendPVT, nb::arg("arm"), nb::arg("local_file"), nb::arg("serial"));
m.def("RunPVT", &bind_RunPVT, nb::arg("arm"), nb::arg("id"));
m.def("SetJointDrag", &bind_SetJointDrag, nb::arg("arm"));
m.def("SetCartDrag", &bind_SetCartDrag, nb::arg("arm"), nb::arg("type"));
m.def("ExitDrag", &bind_ExitDrag, nb::arg("arm"));
m.def("ClearChData", &bind_ClearChData, nb::arg("arm"));
m.def("GetChData", &bind_GetChData, nb::arg("arm"), nb::arg("data_ptr"), nb::arg("ret_ch"));
m.def("SetChData", &bind_SetChData, nb::arg("arm"), nb::arg("data_ptr"), nb::arg("size_int"), nb::arg("set_ch"));
m.def("StartCollectData", &bind_StartCollectData, nb::arg("targetNum"), nb::arg("targetID"), nb::arg("recordNum"));
m.def("StopCollectData", &bind_StopCollectData);
m.def("Disable", &bind_Disable, nb::arg("arm"));
m.def("ValidateArm", &bind_ValidateArm, nb::arg("arm"));
nb::dict layouts;
{ nb::dict fields;
fields["__size__"] = sizeof(StateCtr);
fields["m_CurState"] = offsetof(StateCtr, m_CurState);
fields["m_CmdState"] = offsetof(StateCtr, m_CmdState);
fields["m_ERRCode"] = offsetof(StateCtr, m_ERRCode);
layouts["StateCtr"] = fields; }
{ nb::dict fields;
fields["__size__"] = sizeof(RT_IN);
fields["m_RtInSwitch"] = offsetof(RT_IN, m_RtInSwitch);
fields["m_ImpType"] = offsetof(RT_IN, m_ImpType);
fields["m_InFrameSerial"] = offsetof(RT_IN, m_InFrameSerial);
fields["m_FrameMissCnt"] = offsetof(RT_IN, m_FrameMissCnt);
fields["m_MaxFrameMissCnt"] = offsetof(RT_IN, m_MaxFrameMissCnt);
fields["m_SysCyc"] = offsetof(RT_IN, m_SysCyc);
fields["m_SysCycMissCnt"] = offsetof(RT_IN, m_SysCycMissCnt);
fields["m_MaxSysCycMissCnt"] = offsetof(RT_IN, m_MaxSysCycMissCnt);
fields["m_ToolKine"] = offsetof(RT_IN, m_ToolKine);
fields["m_ToolDyn"] = offsetof(RT_IN, m_ToolDyn);
fields["m_Joint_CMD_Pos"] = offsetof(RT_IN, m_Joint_CMD_Pos);
fields["m_Joint_Vel_Ratio"] = offsetof(RT_IN, m_Joint_Vel_Ratio);
fields["m_Joint_Acc_Ratio"] = offsetof(RT_IN, m_Joint_Acc_Ratio);
fields["m_Joint_K"] = offsetof(RT_IN, m_Joint_K);
fields["m_Joint_D"] = offsetof(RT_IN, m_Joint_D);
fields["m_DragSpType"] = offsetof(RT_IN, m_DragSpType);
fields["m_DragSpPara"] = offsetof(RT_IN, m_DragSpPara);
fields["m_Cart_KD_Type"] = offsetof(RT_IN, m_Cart_KD_Type);
fields["m_Cart_K"] = offsetof(RT_IN, m_Cart_K);
fields["m_Cart_D"] = offsetof(RT_IN, m_Cart_D);
fields["m_Cart_KN"] = offsetof(RT_IN, m_Cart_KN);
fields["m_Cart_DN"] = offsetof(RT_IN, m_Cart_DN);
fields["m_Force_FB_Type"] = offsetof(RT_IN, m_Force_FB_Type);
fields["m_Force_Type"] = offsetof(RT_IN, m_Force_Type);
fields["m_Force_Dir"] = offsetof(RT_IN, m_Force_Dir);
fields["m_Force_PIDUL"] = offsetof(RT_IN, m_Force_PIDUL);
fields["m_Force_AdjLmt"] = offsetof(RT_IN, m_Force_AdjLmt);
fields["m_Force_Cmd"] = offsetof(RT_IN, m_Force_Cmd);
fields["m_SET_Tags"] = offsetof(RT_IN, m_SET_Tags);
fields["m_Update_Tags"] = offsetof(RT_IN, m_Update_Tags);
fields["m_PvtID"] = offsetof(RT_IN, m_PvtID);
fields["m_PvtID_Update"] = offsetof(RT_IN, m_PvtID_Update);
fields["m_Pvt_RunID"] = offsetof(RT_IN, m_Pvt_RunID);
fields["m_Pvt_RunState"] = offsetof(RT_IN, m_Pvt_RunState);
layouts["RT_IN"] = fields; }
{ nb::dict fields;
fields["__size__"] = sizeof(RT_OUT);
fields["m_OutFrameSerial"] = offsetof(RT_OUT, m_OutFrameSerial);
fields["m_FB_Joint_Pos"] = offsetof(RT_OUT, m_FB_Joint_Pos);
fields["m_FB_Joint_Vel"] = offsetof(RT_OUT, m_FB_Joint_Vel);
fields["m_FB_Joint_PosE"] = offsetof(RT_OUT, m_FB_Joint_PosE);
fields["m_FB_Joint_Cmd"] = offsetof(RT_OUT, m_FB_Joint_Cmd);
fields["m_FB_Joint_CToq"] = offsetof(RT_OUT, m_FB_Joint_CToq);
fields["m_FB_Joint_SToq"] = offsetof(RT_OUT, m_FB_Joint_SToq);
fields["m_FB_Joint_Them"] = offsetof(RT_OUT, m_FB_Joint_Them);
fields["m_EST_Joint_Firc"] = offsetof(RT_OUT, m_EST_Joint_Firc);
fields["m_EST_Joint_Firc_Dot"] = offsetof(RT_OUT, m_EST_Joint_Firc_Dot);
fields["m_EST_Joint_Force"] = offsetof(RT_OUT, m_EST_Joint_Force);
fields["m_EST_Cart_FN"] = offsetof(RT_OUT, m_EST_Cart_FN);
fields["m_TipDI"] = offsetof(RT_OUT, m_TipDI);
fields["m_LowSpdFlag"] = offsetof(RT_OUT, m_LowSpdFlag);
fields["m_pad"] = offsetof(RT_OUT, m_pad);
fields["m_TrajState"] = offsetof(RT_OUT, m_TrajState);
layouts["RT_OUT"] = fields; }
{ nb::dict fields;
fields["__size__"] = sizeof(DCSS);
fields["m_State"] = offsetof(DCSS, m_State);
fields["m_In"] = offsetof(DCSS, m_In);
fields["m_Out"] = offsetof(DCSS, m_Out);
fields["m_ParaName"] = offsetof(DCSS, m_ParaName);
fields["m_ParaType"] = offsetof(DCSS, m_ParaType);
fields["m_ParaIns"] = offsetof(DCSS, m_ParaIns);
fields["m_ParaValueI"] = offsetof(DCSS, m_ParaValueI);
fields["m_ParaValueF"] = offsetof(DCSS, m_ParaValueF);
fields["m_ParaCmdSerial"] = offsetof(DCSS, m_ParaCmdSerial);
fields["m_ParaRetSerial"] = offsetof(DCSS, m_ParaRetSerial);
layouts["DCSS"] = fields; }
{ nb::dict fields;
fields["__size__"] = sizeof(FTCmd);
fields["fxDir"] = offsetof(FTCmd, fxDir);
fields["K"] = offsetof(FTCmd, K);
fields["F"] = offsetof(FTCmd, F);
fields["FreeDis"] = offsetof(FTCmd, FreeDis);
fields["Dis"] = offsetof(FTCmd, Dis);
fields["Kn"] = offsetof(FTCmd, Kn);
fields["Tn"] = offsetof(FTCmd, Tn);
fields["NFreeDis"] = offsetof(FTCmd, NFreeDis);
fields["Ndis"] = offsetof(FTCmd, Ndis);
layouts["FTCmd"] = fields; }
m.attr("_layouts") = layouts;
}
