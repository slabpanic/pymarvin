#pragma once
#include "bridge.h"
#include "PointSet.h"
struct OwnedPointSet {
    std::unique_ptr<CPointSet> ptr;
    explicit OwnedPointSet(int dimension = 7) : ptr(std::make_unique<CPointSet>()) { init(dimension); }
    CPointSet *get() const {
        if (!ptr) throw std::runtime_error("PointSet is closed");
        return ptr.get();
    }
    bool init(int dimension) {
        if (dimension < 1 || dimension > 40) throw nb::value_error("dimension must be in 1..40");
        auto current = get();
        if (current->OnGetType() != PotT_BEGIN && static_cast<int>(current->OnGetType()) != dimension) {
            auto fresh = std::make_unique<CPointSet>();
            if (!fresh->OnInit(static_cast<PoinType>(dimension))) throw std::runtime_error("cannot initialize PointSet");
            ptr = std::move(fresh);
            return true;
        }
        if (!current->OnInit(static_cast<PoinType>(dimension))) throw std::runtime_error("cannot initialize PointSet");
        return true;
    }
    int dimension() const { return static_cast<int>(get()->OnGetType()); }
    std::vector<double> point(long index) const {
        if (index < 0 || index >= get()->OnGetPointNum()) throw nb::index_error();
        auto p = get()->OnGetPoint(index);
        return std::vector<double>(p, p + dimension());
    }
    std::vector<std::vector<double>> points() const {
        std::vector<std::vector<double>> result;
        for (long i = 0; i < get()->OnGetPointNum(); ++i) result.push_back(point(i));
        return result;
    }
    bool append(std::vector<double> value) {
        if (value.size() != static_cast<size_t>(dimension())) throw nb::value_error("point dimension mismatch");
        return get()->OnSetPoint(value.data());
    }
    void close() { ptr.reset(); }
};
inline void bind_pointset(nb::module_ &m) {
    nb::class_<OwnedPointSet>(m, "PointSet", "Owned trajectory points with explicit close and context-manager support.")
        .def(nb::init<int>(), nb::arg("dimension") = 7)
        .def_prop_ro("dimension", &OwnedPointSet::dimension, "Number of coordinates in each point.")
        .def_prop_ro("closed", [](OwnedPointSet &p) { return !p.ptr; }, "Whether the underlying point set has been released.")
        .def("__bool__", [](OwnedPointSet &p) { return bool(p.ptr); })
        .def("__len__", [](OwnedPointSet &p) { return p.get()->OnGetPointNum(); })
        .def("__getitem__", &OwnedPointSet::point)
        .def("append", &OwnedPointSet::append)
        .def("to_list", &OwnedPointSet::points)
        .def("close", &OwnedPointSet::close)
        .def("__enter__", [](OwnedPointSet &p) -> OwnedPointSet& { p.get(); return p; }, nb::rv_policy::reference_internal)
        .def("__exit__", [](OwnedPointSet &p, nb::object, nb::object, nb::object) { p.close(); },
             nb::arg("exc_type").none(), nb::arg("exc_value").none(), nb::arg("traceback").none());
}
