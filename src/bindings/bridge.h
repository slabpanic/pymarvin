#pragma once
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <cstring>
#include <cmath>
#include <memory>
#include <type_traits>
#include <vector>
#include <string>
namespace nb = nanobind;

inline nb::object unwrap(nb::object value) {
    if (nb::hasattr(value, "_obj")) return value.attr("_obj");
    return value;
}
template <typename T> T scalar(nb::object value) {
    if (nb::hasattr(value, "value")) value = value.attr("value");
    if constexpr (std::is_same_v<T, char>) {
        if (nb::isinstance<nb::bytes>(value) || nb::isinstance<nb::str>(value)) {
            std::string text = nb::isinstance<nb::bytes>(value)
                ? std::string(PyBytes_AsString(value.ptr()), PyBytes_Size(value.ptr()))
                : nb::cast<std::string>(value);
            if (text.size() != 1) throw nb::value_error("expected one character");
            return text[0];
        }
    }
    return nb::cast<T>(value);
}
// Buffers are copied into aligned, bounded storage. Never accept Python integer
// addresses or dereference ctypes pointers. Copy output back only after a call.
template <typename T, size_t N = 1> struct Buffer {
    T data[N]{};
    nb::object owner;
    Py_buffer view{};
    explicit Buffer(nb::object obj) : owner(unwrap(obj)) {
        if (PyObject_GetBuffer(owner.ptr(), &view, PyBUF_WRITABLE | PyBUF_C_CONTIGUOUS) != 0)
            throw nb::python_error();
        if (view.len != static_cast<Py_ssize_t>(sizeof(data))) {
            PyBuffer_Release(&view); view.obj = nullptr;
            throw nb::value_error("buffer size does not match the C++ SDK argument");
        }
        std::memcpy(data, view.buf, sizeof(data));
    }
    ~Buffer() { if (view.obj) PyBuffer_Release(&view); }
    void commit() { std::memcpy(view.buf, data, sizeof(data)); }
};
template <typename T> struct Output {
    T data{};
    nb::object owner;
    explicit Output(nb::object obj) : owner(unwrap(obj)) {
        if (!nb::hasattr(owner, "value")) throw nb::type_error("expected a scalar output value");
        data = scalar<T>(owner);
    }
    void commit() { owner.attr("value") = nb::cast(data); }
};
struct Text {
    std::string data;
    explicit Text(nb::object obj) {
        if (nb::hasattr(obj, "value")) obj = obj.attr("value");
        if (nb::isinstance<nb::bytes>(obj))
            data.assign(PyBytes_AsString(obj.ptr()), PyBytes_Size(obj.ptr()));
        else data = nb::cast<std::string>(obj);
        if (data.find('\0') != std::string::npos) throw nb::value_error("embedded NUL in string");
    }
};
