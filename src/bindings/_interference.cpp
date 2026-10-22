// Nanobind bindings for the official Marvin interference-check SDK.
#include "Interference.h"
#include "bridge.h"

#include <nanobind/stl/vector.h>

#include <memory>
#include <vector>

struct InterferenceHandle {
    FX_InterfHandle value = nullptr;

    InterferenceHandle() : value(FX_Interf_Create()) {}
    ~InterferenceHandle() { reset(); }

    InterferenceHandle(const InterferenceHandle &) = delete;
    InterferenceHandle &operator=(const InterferenceHandle &) = delete;

    void reset() {
        if (value) {
            FX_Interf_Destroy(value);
            value = nullptr;
        }
    }
};

static int bind_init(InterferenceHandle &handle, nb::object cord_def,
                     nb::object cal_link_def, nb::object input_def,
                     nb::object convex_def, nb::object ic_def) {
    Text cord(cord_def);
    Text cal_link(cal_link_def);
    Text input(input_def);
    Text convex(convex_def);
    Text ic(ic_def);
    return FX_Interf_Init(handle.value, cord.data.data(), cal_link.data.data(),
                          input.data.data(), convex.data.data(), ic.data.data());
}

static int bind_update_cord(InterferenceHandle &handle, long cord_num,
                            const std::vector<double> &input) {
    return FX_Interf_UpdateCord(handle.value, cord_num,
                                const_cast<double *>(input.data()));
}

static nb::tuple bind_get_com(InterferenceHandle &handle) {
    double value[3]{};
    int result = FX_Interf_GetCoM(handle.value, value);
    return nb::make_tuple(result, std::vector<double>(value, value + 3));
}

static nb::tuple bind_get_cords_num(InterferenceHandle &handle) {
    long value = 0;
    int result = FX_Interf_GetCordsNum(handle.value, &value);
    return nb::make_tuple(result, value);
}

static nb::tuple bind_get_mass(InterferenceHandle &handle, long count) {
    if (count < 0 || count > 1000000)
        throw nb::value_error("count must be between 0 and 1000000");
    long expected = 0;
    int count_status = FX_Interf_GetCordsNum(handle.value, &expected);
    if (count_status == FUNC_RET_SUCCESS && count != expected)
        throw nb::value_error("count must match the configured coordinate count");
    std::vector<double> values(static_cast<size_t>(count), 0.0);
    int result = FX_Interf_GetMass(handle.value, values.data());
    return nb::make_tuple(result, values);
}

static nb::tuple bind_get_min_span(InterferenceHandle &handle) {
    double value = 0.0;
    int result = FX_Interf_GetMinSpan(handle.value, &value);
    return nb::make_tuple(result, value);
}

static nb::tuple bind_get_interf_span(InterferenceHandle &handle, long serial) {
    double value = 0.0;
    int result = FX_Interf_GetInterfSpan(handle.value, serial, &value);
    return nb::make_tuple(result, value);
}

NB_MODULE(_interference, m) {
    m.doc() = "Nanobind bindings for the Marvin interference-check SDK.";

    nb::class_<InterferenceHandle>(m, "InterferenceHandle")
        .def(nb::init<>())
        .def("close", &InterferenceHandle::reset)
        .def_prop_ro("closed", [](const InterferenceHandle &handle) {
            return handle.value == nullptr;
        })
        .def("__bool__", [](const InterferenceHandle &handle) {
            return handle.value != nullptr;
        });

    m.def("FX_Interf_Create", []() { return new InterferenceHandle(); },
          nb::rv_policy::take_ownership);
    m.def("FX_Interf_Destroy", [](InterferenceHandle &handle) { handle.reset(); });
    m.def("FX_Interf_Init", &bind_init, nb::arg("handle"), nb::arg("cord_def"),
          nb::arg("cal_link_def"), nb::arg("input_def"), nb::arg("convex_def"),
          nb::arg("ic_def"));
    m.def("FX_Interf_UpdateCord", &bind_update_cord, nb::arg("handle"),
          nb::arg("cord_num"), nb::arg("input"));
    m.def("FX_Interf_UpdateConvex",
          [](InterferenceHandle &handle) { return FX_Interf_UpdateConvex(handle.value); });
    m.def("FX_Interf_CalcInterfDistance", [](InterferenceHandle &handle) {
        return FX_Interf_CalcInterfDistance(handle.value);
    });
    m.def("FX_Interf_GetCoM", &bind_get_com, nb::arg("handle"));
    m.def("FX_Interf_GetCordsNum", &bind_get_cords_num, nb::arg("handle"));
    m.def("FX_Interf_GetMass", &bind_get_mass, nb::arg("handle"), nb::arg("count"));
    m.def("FX_Interf_GetMinSpan", &bind_get_min_span, nb::arg("handle"));
    m.def("FX_Interf_GetInterfSpan", &bind_get_interf_span, nb::arg("handle"),
          nb::arg("serial"));
    m.def("FX_Interf_OnIsInterf", [](InterferenceHandle &handle,
                                      const std::vector<double> &thresholds) {
        return FX_Interf_OnIsInterf(handle.value,
                                    const_cast<double *>(thresholds.data()));
    }, nb::arg("handle"), nb::arg("thresholds"));

    m.attr("FUNC_RET_SUCCESS") = 0;
    m.attr("FUNC_RET_INVALID_INPUT_ARG") = -1;
    m.attr("FUNC_RET_OPERATION_FAILED") = -2;
    m.attr("FUNC_RET_ISInterference") = -3;
    m.attr("FUNC_RET_NOInterference") = -4;
}
