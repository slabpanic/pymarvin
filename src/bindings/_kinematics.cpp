// Nanobind bindings maintained alongside the SDK headers and Python facade.
#include "FxRobot.h"
#include "bridge.h"
#include "pointset.h"
static unsigned stages[MAX_RUN_ROBOT_NUM]{};
static auto bind_LOADMvCfg(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6, nb::object a7, nb::object a8) {
    Text p0(a0);
    Buffer<FX_INT32L, 2> p1(a1);
    Buffer<FX_DOUBLE, 6> p2(a2);
    Buffer<FX_DOUBLE, 64> p3(a3);
    Buffer<FX_DOUBLE, 56> p4(a4);
    Buffer<FX_DOUBLE, 24> p5(a5);
    Buffer<FX_DOUBLE, 14> p6(a6);
    Buffer<FX_DOUBLE, 42> p7(a7);
    Buffer<FX_DOUBLE, 84> p8(a8);
    auto result = LOADMvCfg(p0.data.data(), p1.data, reinterpret_cast<FX_DOUBLE (*)[3]>(p2.data), reinterpret_cast<FX_DOUBLE (*)[8][4]>(p3.data), reinterpret_cast<FX_DOUBLE (*)[7][4]>(p4.data), reinterpret_cast<FX_DOUBLE (*)[4][3]>(p5.data), reinterpret_cast<FX_DOUBLE (*)[7]>(p6.data), reinterpret_cast<FX_DOUBLE (*)[7][3]>(p7.data), reinterpret_cast<FX_DOUBLE (*)[7][6]>(p8.data));
    p1.commit();
    p2.commit();
    p3.commit();
    p4.commit();
    p5.commit();
    p6.commit();
    p7.commit();
    p8.commit();
    return bool(result);
}
static auto bind_FX_LOG_SWITCH(nb::object a0) {
    auto p0 = scalar<FX_INT32L>(a0);
    FX_LOG_SWITCH(p0);
}
static auto bind_FX_Robot_Init_Type(nb::object a0, nb::object a1) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    auto p1 = scalar<FX_INT32L>(a1);
    stages[p0] = 0;
    auto result = FX_Robot_Init_Type(p0, p1);
    if (result) stages[p0] |= 1; else stages[p0] &= ~1u;
    return bool(result);
}
static auto bind_FX_Robot_Init_Kine(nb::object a0, nb::object a1) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    Buffer<FX_DOUBLE, 32> p1(a1);
    if (!(stages[p0] & 1)) throw std::runtime_error("initialize robot type first");
    auto result = FX_Robot_Init_Kine(p0, reinterpret_cast<FX_DOUBLE (*)[4]>(p1.data));
    p1.commit();
    if (result) stages[p0] |= 2; else stages[p0] &= ~2u;
    return bool(result);
}
static auto bind_FX_Robot_Init_Lmt(nb::object a0, nb::object a1, nb::object a2) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    Buffer<FX_DOUBLE, 28> p1(a1);
    Buffer<FX_DOUBLE, 12> p2(a2);
    if (!(stages[p0] & 1)) throw std::runtime_error("initialize robot type first");
    auto result = FX_Robot_Init_Lmt(p0, reinterpret_cast<FX_DOUBLE (*)[4]>(p1.data), reinterpret_cast<FX_DOUBLE (*)[3]>(p2.data));
    p1.commit();
    p2.commit();
    if (result) stages[p0] |= 4; else stages[p0] &= ~4u;
    return bool(result);
}
static auto bind_FX_Robot_Tool_Set(nb::object a0, nb::object a1) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 16> p1(a1);
    auto result = FX_Robot_Tool_Set(p0, reinterpret_cast<double (*)[4]>(p1.data));
    p1.commit();
    return bool(result);
}
static auto bind_FX_Robot_Tool_Rmv(nb::object a0) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    auto result = FX_Robot_Tool_Rmv(p0);
    return bool(result);
}
static auto bind_FX_Robot_UserFrame_Set(nb::object a0, nb::object a1) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 16> p1(a1);
    auto result = FX_Robot_UserFrame_Set(p0, reinterpret_cast<double (*)[4]>(p1.data));
    p1.commit();
    return bool(result);
}
static auto bind_FX_Robot_UserFrame_Rmv(nb::object a0) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    auto result = FX_Robot_UserFrame_Rmv(p0);
    return bool(result);
}
static auto bind_FX_Robot_Kine_FK(nb::object a0, nb::object a1, nb::object a2) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<FX_DOUBLE, 7> p1(a1);
    Buffer<double, 16> p2(a2);
    auto result = FX_Robot_Kine_FK(p0, p1.data, reinterpret_cast<double (*)[4]>(p2.data));
    p1.commit();
    p2.commit();
    return bool(result);
}
static auto bind_FX_Robot_Kine_FK_NSP(nb::object a0, nb::object a1, nb::object a2, nb::object a3) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<FX_DOUBLE, 7> p1(a1);
    Buffer<double, 16> p2(a2);
    Buffer<double, 9> p3(a3);
    auto result = FX_Robot_Kine_FK_NSP(p0, p1.data, reinterpret_cast<double (*)[4]>(p2.data), reinterpret_cast<double (*)[3]>(p3.data));
    p1.commit();
    p2.commit();
    p3.commit();
    return bool(result);
}
static auto bind_FX_Robot_Kine_Jacb(nb::object a0, nb::object a1, nb::object a2) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<FX_DOUBLE, 7> p1(a1);
    Buffer<FX_Jacobi> p2(a2);
    auto result = FX_Robot_Kine_Jacb(p0, p1.data, p2.data);
    p1.commit();
    p2.commit();
    return bool(result);
}
static auto bind_FX_Robot_Kine_IK(nb::object a0, nb::object a1) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<FX_InvKineSolvePara> p1(a1);
    auto result = FX_Robot_Kine_IK(p0, p1.data);
    p1.commit();
    return bool(result);
}
static auto bind_FX_Robot_Kine_IK_NSP(nb::object a0, nb::object a1) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<FX_InvKineSolvePara> p1(a1);
    auto result = FX_Robot_Kine_IK_NSP(p0, p1.data);
    p1.commit();
    return bool(result);
}
static auto bind_FX_Robot_CalEndXYZABC(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4) {
    Buffer<double, 6> p0(a0);
    Buffer<double, 3> p1(a1);
    auto p2 = scalar<FX_INT32L>(a2);
    Buffer<double, 3> p3(a3);
    Buffer<double, 6> p4(a4);
    auto result = FX_Robot_CalEndXYZABC(p0.data, p1.data, p2, p3.data, p4.data);
    p0.commit();
    p1.commit();
    p3.commit();
    p4.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_MOVL(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6, nb::object a7) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 6> p1(a1);
    Buffer<double, 6> p2(a2);
    Buffer<double, 7> p3(a3);
    auto p4 = scalar<FX_DOUBLE>(a4);
    auto p5 = scalar<FX_DOUBLE>(a5);
    auto p6 = scalar<FX_INT32L>(a6);
    Text p7(a7);
    if (p6 <= 0) throw nb::value_error("planning frequency must be positive");
    auto result = FX_Robot_PLN_MOVL(p0, p1.data, p2.data, p3.data, p4, p5, p6, p7.data.data());
    p1.commit();
    p2.commit();
    p3.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_MOVL_KeepJ(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 7> p1(a1);
    Buffer<double, 7> p2(a2);
    auto p3 = scalar<FX_DOUBLE>(a3);
    auto p4 = scalar<FX_DOUBLE>(a4);
    auto p5 = scalar<FX_INT32L>(a5);
    Text p6(a6);
    if (p5 <= 0) throw nb::value_error("planning frequency must be positive");
    auto result = FX_Robot_PLN_MOVL_KeepJ(p0, p1.data, p2.data, p3, p4, p5, p6.data.data());
    p1.commit();
    p2.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_Set_MOVL_Start(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6, nb::object a7, nb::object a8, nb::object a9) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 7> p1(a1);
    Buffer<double, 6> p2(a2);
    Buffer<double, 6> p3(a3);
    auto p4 = scalar<FX_DOUBLE>(a4);
    auto p5 = scalar<FX_INT32L>(a5);
    Buffer<double, 6> p6(a6);
    auto p7 = scalar<FX_DOUBLE>(a7);
    auto p8 = scalar<FX_DOUBLE>(a8);
    auto p9 = scalar<FX_INT32L>(a9);
    if (p9 <= 0) throw nb::value_error("planning frequency must be positive");
    auto result = FX_Robot_PLN_Set_MOVL_Start(p0, p1.data, p2.data, p3.data, p4, p5, p6.data, p7, p8, p9);
    p1.commit();
    p2.commit();
    p3.commit();
    p6.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_Set_MOVL_Next_Point(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 6> p1(a1);
    auto p2 = scalar<FX_DOUBLE>(a2);
    auto p3 = scalar<FX_INT32L>(a3);
    Buffer<double, 6> p4(a4);
    auto p5 = scalar<FX_DOUBLE>(a5);
    auto p6 = scalar<FX_DOUBLE>(a6);
    auto result = FX_Robot_PLN_Set_MOVL_Next_Point(p0, p1.data, p2, p3, p4.data, p5, p6);
    p1.commit();
    p4.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_Get_MOVL_Path(nb::object a0, nb::object a1) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    auto &p1 = nb::cast<OwnedPointSet&>(a1);
    if (p1.dimension() != 7) throw nb::value_error("planning output requires seven-dimensional points");
    auto result = FX_Robot_PLN_Get_MOVL_Path(p0, p1.get());
    return bool(result);
}
static auto bind_FX_Robot_PLN_MOVJ(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 7> p1(a1);
    Buffer<double, 7> p2(a2);
    auto p3 = scalar<FX_DOUBLE>(a3);
    auto p4 = scalar<FX_DOUBLE>(a4);
    auto p5 = scalar<FX_INT32L>(a5);
    auto &p6 = nb::cast<OwnedPointSet&>(a6);
    if (p5 <= 0) throw nb::value_error("planning frequency must be positive");
    if (p6.dimension() != 7) throw nb::value_error("planning output requires seven-dimensional points");
    auto result = FX_Robot_PLN_MOVJ(p0, p1.data, p2.data, p3, p4, p5, p6.get());
    p1.commit();
    p2.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_MOVL_Arms_Synchronous(nb::object a0, nb::object a1, nb::object a2) {
    Buffer<ArmsSynchronousPlanningParams> p0(a0);
    auto &p1 = nb::cast<OwnedPointSet&>(a1);
    auto &p2 = nb::cast<OwnedPointSet&>(a2);
    if (p0.data->Freq <= 0) throw nb::value_error("Freq must be positive");
    if (p1.dimension() != 7) throw nb::value_error("planning output requires seven-dimensional points");
    if (p2.dimension() != 7) throw nb::value_error("planning output requires seven-dimensional points");
    if (stages[0] != 7 || stages[1] != 7) throw std::runtime_error("initialize both arms before synchronous planning");
    auto result = FX_Robot_PLN_MOVL_Arms_Synchronous(p0.data, p1.get(), p2.get());
    p0.commit();
    return bool(result);
}
static auto bind_FX_Robot_JntTau2EETau(nb::object a0, nb::object a1, nb::object a2, nb::object a3) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 7> p1(a1);
    Buffer<double, 7> p2(a2);
    Buffer<double, 6> p3(a3);
    auto result = FX_Robot_JntTau2EETau(p0, p1.data, p2.data, p3.data);
    p1.commit();
    p2.commit();
    p3.commit();
    return bool(result);
}
static auto bind_FX_Robot_CalEELinerVel(nb::object a0, nb::object a1, nb::object a2) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 7> p1(a1);
    Buffer<double, 7> p2(a2);
    FX_Jacobi jac{};
    if (!FX_Robot_Kine_Jacb(p0, p1.data, &jac)) return -1.0;
    double speed2 = 0; for (int r = 0; r < 3; ++r) { double v = 0; for (int c = 0; c < 7; ++c) v += jac.m_Jcb[r][c] * p2.data[c] * FXARM_D2R * 1000.0; speed2 += v * v; }
    auto result = std::sqrt(speed2);
    p1.commit();
    p2.commit();
    return result;
}
static auto bind_FX_Robot_Iden_LoadDyn_M20(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5) {
    Text p0(a0);
    auto p1 = scalar<FX_INT32>(a1);
    Text p2(a2);
    Output<FX_DOUBLE> p3(a3);
    Buffer<double, 3> p4(a4);
    Buffer<double, 6> p5(a5);
    auto result = FX_Robot_Iden_LoadDyn_M20(p0.data.data(), p1, p2.data.data(), &p3.data, p4.data, p5.data);
    p3.commit();
    p4.commit();
    p5.commit();
    return result;
}
static auto bind_FX_Robot_Iden_LoadDyn(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4) {
    auto p0 = scalar<FX_INT32>(a0);
    Text p1(a1);
    Output<FX_DOUBLE> p2(a2);
    Buffer<double, 3> p3(a3);
    Buffer<double, 6> p4(a4);
    auto result = FX_Robot_Iden_LoadDyn(p0, p1.data.data(), &p2.data, p3.data, p4.data);
    p2.commit();
    p3.commit();
    p4.commit();
    return result;
}
static auto bind_FX_XYZABC2Matrix4DEG(nb::object a0, nb::object a1) {
    Buffer<FX_DOUBLE, 6> p0(a0);
    Buffer<FX_DOUBLE, 16> p1(a1);
    FX_XYZABC2Matrix4DEG(p0.data, reinterpret_cast<FX_DOUBLE (*)[4]>(p1.data));
    p0.commit();
    p1.commit();
}
static auto bind_FX_Matrix42XYZABCDEG(nb::object a0, nb::object a1) {
    Buffer<FX_DOUBLE, 16> p0(a0);
    Buffer<FX_DOUBLE, 6> p1(a1);
    auto result = FX_Matrix42XYZABCDEG(reinterpret_cast<FX_DOUBLE (*)[4]>(p0.data), p1.data);
    p0.commit();
    p1.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_MOVLA_C(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6, nb::object a7) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 6> p1(a1);
    Buffer<double, 6> p2(a2);
    Buffer<double, 7> p3(a3);
    auto p4 = scalar<FX_DOUBLE>(a4);
    auto p5 = scalar<FX_DOUBLE>(a5);
    auto p6 = scalar<FX_INT32L>(a6);
    auto &p7 = nb::cast<OwnedPointSet&>(a7);
    if (p6 <= 0) throw nb::value_error("planning frequency must be positive");
    if (p7.dimension() != 7) throw nb::value_error("planning output requires seven-dimensional points");
    auto result = FX_Robot_PLN_MOVLA_C(p0, p1.data, p2.data, p3.data, p4, p5, p6, p7.get());
    p1.commit();
    p2.commit();
    p3.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_MOVL_KeepJA_C(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 7> p1(a1);
    Buffer<double, 7> p2(a2);
    auto p3 = scalar<FX_DOUBLE>(a3);
    auto p4 = scalar<FX_DOUBLE>(a4);
    auto p5 = scalar<FX_INT32L>(a5);
    auto &p6 = nb::cast<OwnedPointSet&>(a6);
    if (p5 <= 0) throw nb::value_error("planning frequency must be positive");
    if (p6.dimension() != 7) throw nb::value_error("planning output requires seven-dimensional points");
    auto result = FX_Robot_PLN_MOVL_KeepJA_C(p0, p1.data, p2.data, p3, p4, p5, p6.get());
    p1.commit();
    p2.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_MOV_Target_C(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6, nb::object a7) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 6> p1(a1);
    Buffer<double, 6> p2(a2);
    Buffer<double, 7> p3(a3);
    auto p4 = scalar<FX_DOUBLE>(a4);
    auto p5 = scalar<FX_DOUBLE>(a5);
    auto p6 = scalar<FX_INT32L>(a6);
    auto &p7 = nb::cast<OwnedPointSet&>(a7);
    if (p6 <= 0) throw nb::value_error("planning frequency must be positive");
    if (p7.dimension() != 7) throw nb::value_error("planning output requires seven-dimensional points");
    auto result = FX_Robot_PLN_MOV_Target_C(p0, p1.data, p2.data, p3.data, p4, p5, p6, p7.get());
    p1.commit();
    p2.commit();
    p3.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_Get_MOVL_Path_C(nb::object a0, nb::object a1) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    auto &p1 = nb::cast<OwnedPointSet&>(a1);
    if (p1.dimension() != 7) throw nb::value_error("planning output requires seven-dimensional points");
    auto result = FX_Robot_PLN_Get_MOVL_Path_C(p0, p1.get());
    return bool(result);
}
static auto bind_FX_Robot_PLN_MOVLA(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6, nb::object a7) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 6> p1(a1);
    Buffer<double, 6> p2(a2);
    Buffer<double, 7> p3(a3);
    auto p4 = scalar<FX_DOUBLE>(a4);
    auto p5 = scalar<FX_DOUBLE>(a5);
    auto p6 = scalar<FX_INT32L>(a6);
    auto &p7 = nb::cast<OwnedPointSet&>(a7);
    if (p6 <= 0) throw nb::value_error("planning frequency must be positive");
    if (p7.dimension() != 7) throw nb::value_error("planning output requires seven-dimensional points");
    auto result = FX_Robot_PLN_MOVLA(p0, p1.data, p2.data, p3.data, p4, p5, p6, p7.get());
    p1.commit();
    p2.commit();
    p3.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_MOVL_KeepJA(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 7> p1(a1);
    Buffer<double, 7> p2(a2);
    auto p3 = scalar<FX_DOUBLE>(a3);
    auto p4 = scalar<FX_DOUBLE>(a4);
    auto p5 = scalar<FX_INT32L>(a5);
    auto &p6 = nb::cast<OwnedPointSet&>(a6);
    if (p5 <= 0) throw nb::value_error("planning frequency must be positive");
    if (p6.dimension() != 7) throw nb::value_error("planning output requires seven-dimensional points");
    auto result = FX_Robot_PLN_MOVL_KeepJA(p0, p1.data, p2.data, p3, p4, p5, p6.get());
    p1.commit();
    p2.commit();
    return bool(result);
}
static auto bind_FX_Robot_PLN_MOV_Target(nb::object a0, nb::object a1, nb::object a2, nb::object a3, nb::object a4, nb::object a5, nb::object a6, nb::object a7) {
    auto p0 = scalar<FX_INT32L>(a0);
    if (p0 < 0 || p0 >= MAX_RUN_ROBOT_NUM) throw nb::value_error("robot serial must be in 0..9");
    if (stages[p0] != 7) throw std::runtime_error("initialize robot type, kinematics and limits before calculation");
    Buffer<double, 6> p1(a1);
    Buffer<double, 6> p2(a2);
    Buffer<double, 7> p3(a3);
    auto p4 = scalar<FX_DOUBLE>(a4);
    auto p5 = scalar<FX_DOUBLE>(a5);
    auto p6 = scalar<FX_INT32L>(a6);
    auto &p7 = nb::cast<OwnedPointSet&>(a7);
    if (p6 <= 0) throw nb::value_error("planning frequency must be positive");
    if (p7.dimension() != 7) throw nb::value_error("planning output requires seven-dimensional points");
    auto result = FX_Robot_PLN_MOV_Target(p0, p1.data, p2.data, p3.data, p4, p5, p6, p7.get());
    p1.commit();
    p2.commit();
    p3.commit();
    return bool(result);
}
NB_MODULE(_kinematics, m) {
bind_pointset(m);
m.def("FX_CPointSet_Create", []() { return new OwnedPointSet(7); }, nb::rv_policy::take_ownership);
m.def("FX_CPointSet_Destroy", &OwnedPointSet::close);
m.def("FX_CPointSet_OnInit", &OwnedPointSet::init);
m.def("FX_CPointSet_OnGetPointNum", [](OwnedPointSet &p) { return p.get()->OnGetPointNum(); });
m.def("FX_CPointSet_OnGetPoint", &OwnedPointSet::point);
m.def("FX_CPointSet_OnSetPoint", &OwnedPointSet::append);
m.def("LOADMvCfg", &bind_LOADMvCfg, nb::arg("path"), nb::arg("TYPE"), nb::arg("GRV"), nb::arg("DH"), nb::arg("PNVA"), nb::arg("BD"), nb::arg("Mass"), nb::arg("MCP"), nb::arg("I"));
m.def("FX_LOG_SWITCH", &bind_FX_LOG_SWITCH, nb::arg("log_tag_input"));
m.def("FX_Robot_Init_Type", &bind_FX_Robot_Init_Type, nb::arg("RobotSerial"), nb::arg("RobotType"));
m.def("FX_Robot_Init_Kine", &bind_FX_Robot_Init_Kine, nb::arg("RobotSerial"), nb::arg("DH"));
m.def("FX_Robot_Init_Lmt", &bind_FX_Robot_Init_Lmt, nb::arg("RobotSerial"), nb::arg("PNVA"), nb::arg("J67"));
m.def("FX_Robot_Tool_Set", &bind_FX_Robot_Tool_Set, nb::arg("RobotSerial"), nb::arg("tool"));
m.def("FX_Robot_Tool_Rmv", &bind_FX_Robot_Tool_Rmv, nb::arg("RobotSerial"));
m.def("FX_Robot_UserFrame_Set", &bind_FX_Robot_UserFrame_Set, nb::arg("RobotSerial"), nb::arg("userframe"));
m.def("FX_Robot_UserFrame_Rmv", &bind_FX_Robot_UserFrame_Rmv, nb::arg("RobotSerial"));
m.def("FX_Robot_Kine_FK", &bind_FX_Robot_Kine_FK, nb::arg("RobotSerial"), nb::arg("joints"), nb::arg("pgos"));
m.def("FX_Robot_Kine_FK_NSP", &bind_FX_Robot_Kine_FK_NSP, nb::arg("RobotSerial"), nb::arg("joints"), nb::arg("pgos"), nb::arg("nspg"));
m.def("FX_Robot_Kine_Jacb", &bind_FX_Robot_Kine_Jacb, nb::arg("RobotSerial"), nb::arg("joints"), nb::arg("jcb"));
m.def("FX_Robot_Kine_IK", &bind_FX_Robot_Kine_IK, nb::arg("RobotSerial"), nb::arg("solve_para"));
m.def("FX_Robot_Kine_IK_NSP", &bind_FX_Robot_Kine_IK_NSP, nb::arg("RobotSerial"), nb::arg("solve_para"));
m.def("FX_Robot_CalEndXYZABC", &bind_FX_Robot_CalEndXYZABC, nb::arg("Start_XYZABC"), nb::arg("Pos_offset"), nb::arg("RotType"), nb::arg("Angle_Param"), nb::arg("End_XYZABC"));
m.def("FX_Robot_PLN_MOVL", &bind_FX_Robot_PLN_MOVL, nb::arg("RobotSerial"), nb::arg("Start_XYZABC"), nb::arg("End_XYZABC"), nb::arg("Ref_Joints"), nb::arg("Vel"), nb::arg("ACC"), nb::arg("Freq"), nb::arg("OutPutPath"));
m.def("FX_Robot_PLN_MOVL_KeepJ", &bind_FX_Robot_PLN_MOVL_KeepJ, nb::arg("RobotSerial"), nb::arg("startjoints"), nb::arg("stopjoints"), nb::arg("vel"), nb::arg("acc"), nb::arg("Freq"), nb::arg("OutPutPath"));
m.def("FX_Robot_PLN_Set_MOVL_Start", &bind_FX_Robot_PLN_Set_MOVL_Start, nb::arg("RobotSerial"), nb::arg("Ref_Joints"), nb::arg("Start_XYZABC"), nb::arg("End_XYZABC"), nb::arg("Allow_Range"), nb::arg("ZSP_Type"), nb::arg("ZSP_Para"), nb::arg("Vel"), nb::arg("Acc"), nb::arg("Freq"));
m.def("FX_Robot_PLN_Set_MOVL_Next_Point", &bind_FX_Robot_PLN_Set_MOVL_Next_Point, nb::arg("RobotSerial"), nb::arg("Next_XYZABC"), nb::arg("Allow_Range"), nb::arg("ZSP_Type"), nb::arg("ZSP_Para"), nb::arg("Vel"), nb::arg("Acc"));
m.def("FX_Robot_PLN_Get_MOVL_Path", &bind_FX_Robot_PLN_Get_MOVL_Path, nb::arg("RobotSerial"), nb::arg("ret_Pset"));
m.def("FX_Robot_PLN_MOVJ", &bind_FX_Robot_PLN_MOVJ, nb::arg("RobotSerial"), nb::arg("Start_Joints"), nb::arg("End_Joints"), nb::arg("Vel_ratio"), nb::arg("ACC_ratio"), nb::arg("Freq"), nb::arg("ret_pset"));
m.def("FX_Robot_PLN_MOVL_Arms_Synchronous", &bind_FX_Robot_PLN_MOVL_Arms_Synchronous, nb::arg("ASPP"), nb::arg("Arm0_Pln_Path"), nb::arg("Arm1_Pln_Path"));
m.def("FX_Robot_JntTau2EETau", &bind_FX_Robot_JntTau2EETau, nb::arg("RobotSerial"), nb::arg("q"), nb::arg("Joint_Torque"), nb::arg("EE_Torque"));
m.def("FX_Robot_CalEELinerVel", &bind_FX_Robot_CalEELinerVel, nb::arg("RobotSerial"), nb::arg("joint"), nb::arg("angvel"));
m.def("FX_Robot_Iden_LoadDyn_M20", &bind_FX_Robot_Iden_LoadDyn_M20, nb::arg("path_ini"), nb::arg("Type"), nb::arg("path"), nb::arg("mass"), nb::arg("mr"), nb::arg("I"));
m.def("FX_Robot_Iden_LoadDyn", &bind_FX_Robot_Iden_LoadDyn, nb::arg("Type"), nb::arg("path"), nb::arg("mass"), nb::arg("mr"), nb::arg("I"));
m.def("FX_XYZABC2Matrix4DEG", &bind_FX_XYZABC2Matrix4DEG, nb::arg("xyzabc"), nb::arg("m"));
m.def("FX_Matrix42XYZABCDEG", &bind_FX_Matrix42XYZABCDEG, nb::arg("m"), nb::arg("xyzabc"));
m.def("FX_Robot_PLN_MOVLA_C", &bind_FX_Robot_PLN_MOVLA_C, nb::arg("RobotSerial"), nb::arg("Start_XYZABC"), nb::arg("End_XYZABC"), nb::arg("Ref_Joints"), nb::arg("Vel"), nb::arg("ACC"), nb::arg("Freq"), nb::arg("ret_pset"));
m.def("FX_Robot_PLN_MOVL_KeepJA_C", &bind_FX_Robot_PLN_MOVL_KeepJA_C, nb::arg("RobotSerial"), nb::arg("startjoints"), nb::arg("stopjoints"), nb::arg("vel"), nb::arg("acc"), nb::arg("Freq"), nb::arg("ret_pset"));
m.def("FX_Robot_PLN_MOV_Target_C", &bind_FX_Robot_PLN_MOV_Target_C, nb::arg("RobotSerial"), nb::arg("Start_XYZABC"), nb::arg("End_XYZABC"), nb::arg("Ref_Joints"), nb::arg("Vel"), nb::arg("ACC"), nb::arg("Freq"), nb::arg("ret_pset"));
m.def("FX_Robot_PLN_Get_MOVL_Path_C", &bind_FX_Robot_PLN_Get_MOVL_Path_C, nb::arg("RobotSerial"), nb::arg("ret_Pset"));
m.def("FX_Robot_PLN_MOVLA", &bind_FX_Robot_PLN_MOVLA, nb::arg("RobotSerial"), nb::arg("Start_XYZABC"), nb::arg("End_XYZABC"), nb::arg("Ref_Joints"), nb::arg("Vel"), nb::arg("ACC"), nb::arg("Freq"), nb::arg("ret_pset"));
m.def("FX_Robot_PLN_MOVL_KeepJA", &bind_FX_Robot_PLN_MOVL_KeepJA, nb::arg("RobotSerial"), nb::arg("startjoints"), nb::arg("stopjoints"), nb::arg("vel"), nb::arg("acc"), nb::arg("Freq"), nb::arg("ret_pset"));
m.def("FX_Robot_PLN_MOV_Target", &bind_FX_Robot_PLN_MOV_Target, nb::arg("RobotSerial"), nb::arg("Start_XYZABC"), nb::arg("End_XYZABC"), nb::arg("Ref_Joints"), nb::arg("Vel"), nb::arg("ACC"), nb::arg("Freq"), nb::arg("ret_pset"));
nb::dict layouts;
{ nb::dict fields;
fields["__size__"] = sizeof(ArmsSynchronousPlanningParams);
fields["Skye_Body_Start_PRR"] = offsetof(ArmsSynchronousPlanningParams, Skye_Body_Start_PRR);
fields["Arm0_Start_XYZABC"] = offsetof(ArmsSynchronousPlanningParams, Arm0_Start_XYZABC);
fields["Arm0_End_XYZABC"] = offsetof(ArmsSynchronousPlanningParams, Arm0_End_XYZABC);
fields["Arm0_Ref_Joints"] = offsetof(ArmsSynchronousPlanningParams, Arm0_Ref_Joints);
fields["Arm0_ZSP_Type"] = offsetof(ArmsSynchronousPlanningParams, Arm0_ZSP_Type);
fields["Arm0_ZSP_Para"] = offsetof(ArmsSynchronousPlanningParams, Arm0_ZSP_Para);
fields["Arm1_Start_XYZABC"] = offsetof(ArmsSynchronousPlanningParams, Arm1_Start_XYZABC);
fields["Arm1_End_XYZABC"] = offsetof(ArmsSynchronousPlanningParams, Arm1_End_XYZABC);
fields["Arm1_Ref_Joints"] = offsetof(ArmsSynchronousPlanningParams, Arm1_Ref_Joints);
fields["Arm1_ZSP_Type"] = offsetof(ArmsSynchronousPlanningParams, Arm1_ZSP_Type);
fields["Arm1_ZSP_Para"] = offsetof(ArmsSynchronousPlanningParams, Arm1_ZSP_Para);
fields["Freq"] = offsetof(ArmsSynchronousPlanningParams, Freq);
fields["Vel"] = offsetof(ArmsSynchronousPlanningParams, Vel);
fields["Acc"] = offsetof(ArmsSynchronousPlanningParams, Acc);
fields["Sync_Type"] = offsetof(ArmsSynchronousPlanningParams, Sync_Type);
fields["World_Co_Flag"] = offsetof(ArmsSynchronousPlanningParams, World_Co_Flag);
layouts["ArmsSynchronousPlanningParams"] = fields; }
{ nb::dict fields;
fields["__size__"] = sizeof(FX_InvKineSolvePara);
fields["m_Input_IK_TargetTCP"] = offsetof(FX_InvKineSolvePara, m_Input_IK_TargetTCP);
fields["m_Input_IK_RefJoint"] = offsetof(FX_InvKineSolvePara, m_Input_IK_RefJoint);
fields["m_Input_IK_ZSPType"] = offsetof(FX_InvKineSolvePara, m_Input_IK_ZSPType);
fields["m_Input_IK_ZSPPara"] = offsetof(FX_InvKineSolvePara, m_Input_IK_ZSPPara);
fields["m_Input_ZSP_Angle"] = offsetof(FX_InvKineSolvePara, m_Input_ZSP_Angle);
fields["m_DGR1"] = offsetof(FX_InvKineSolvePara, m_DGR1);
fields["m_DGR2"] = offsetof(FX_InvKineSolvePara, m_DGR2);
fields["m_DGR3"] = offsetof(FX_InvKineSolvePara, m_DGR3);
fields["m_Output_RetJoint"] = offsetof(FX_InvKineSolvePara, m_Output_RetJoint);
fields["m_OutPut_AllJoint"] = offsetof(FX_InvKineSolvePara, m_OutPut_AllJoint);
fields["m_OutPut_Result_Num"] = offsetof(FX_InvKineSolvePara, m_OutPut_Result_Num);
fields["m_Output_IsOutRange"] = offsetof(FX_InvKineSolvePara, m_Output_IsOutRange);
fields["m_Output_IsDeg"] = offsetof(FX_InvKineSolvePara, m_Output_IsDeg);
fields["m_Output_JntExdTags"] = offsetof(FX_InvKineSolvePara, m_Output_JntExdTags);
fields["m_Output_JntExdABS"] = offsetof(FX_InvKineSolvePara, m_Output_JntExdABS);
fields["m_Output_IsJntExd"] = offsetof(FX_InvKineSolvePara, m_Output_IsJntExd);
fields["m_Output_RunLmtP"] = offsetof(FX_InvKineSolvePara, m_Output_RunLmtP);
fields["m_Output_RunLmtN"] = offsetof(FX_InvKineSolvePara, m_Output_RunLmtN);
layouts["FX_InvKineSolvePara"] = fields; }
{ nb::dict fields;
fields["__size__"] = sizeof(FX_Jacobi);
fields["m_AxisNum"] = offsetof(FX_Jacobi, m_AxisNum);
fields["m_Jcb"] = offsetof(FX_Jacobi, m_Jcb);
layouts["FX_Jacobi"] = fields; }
m.attr("_layouts") = layouts;
}
