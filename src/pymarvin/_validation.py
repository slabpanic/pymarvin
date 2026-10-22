"""Check value record ABI against the compiler, including every field offset."""

import ctypes

from . import _control, _kinematics, fx_kine, fx_robot


def verify_layouts():
    for native, facade in [(_control, fx_robot), (_kinematics, fx_kine)]:
        for name, fields in native._layouts.items():
            record = getattr(facade, name)
            if ctypes.sizeof(record) != fields["__size__"]:
                raise ImportError(f"{name}: Python/C++ SDK structure size mismatch")
            for field, offset in fields.items():
                if field != "__size__" and getattr(record, field).offset != offset:
                    raise ImportError(
                        f"{name}.{field}: Python/C++ field offset mismatch"
                    )
