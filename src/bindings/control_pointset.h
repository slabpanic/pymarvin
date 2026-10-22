#pragma once
#include "bridge.h"
#include "PointSet.h"
// The SDK consumes the points synchronously. Copy across the extension boundary
// instead of casting between independently compiled vendor C++ classes.
struct ControlPoints {
    CPointSet data;
    explicit ControlPoints(nb::object obj) {
        auto type = nb::module_::import_("pymarvin._kinematics").attr("PointSet");
        if (!nb::isinstance(obj, type)) throw nb::type_error("expected pymarvin.PointSet");
        int dim = nb::cast<int>(obj.attr("dimension"));
        if (dim != 7) throw nb::value_error("robot trajectories require seven-dimensional points");
        data.OnInit(PotT_7d);
        for (auto row : nb::cast<std::vector<std::vector<double>>>(obj.attr("to_list")())) {
            if (row.size() != 7) throw nb::value_error("invalid trajectory row");
            if (!data.OnSetPoint(row.data())) throw std::runtime_error("cannot copy trajectory");
        }
    }
};
