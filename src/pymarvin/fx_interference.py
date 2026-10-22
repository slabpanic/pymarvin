"""Official-compatible collision and interference checking API."""

from __future__ import annotations

from . import _interference as _native

FUNC_RET_SUCCESS = 0
FUNC_RET_INVALID_INPUT_ARG = -1
FUNC_RET_OPERATION_FAILED = -2
FUNC_RET_ISInterference = -3
FUNC_RET_NOInterference = -4


class Marvin_Interference:
    """Check distances and collisions using the bundled interference SDK.

    The normal call order is ``create()``, ``init()``, ``update_cord()``,
    ``update_convex()``, ``calc_interf_distance()``, and ``on_is_interf()``.
    Configuration arguments may be paths or the corresponding definition text.
    """

    def __init__(self):
        """Create an interface without allocating the native context."""
        self._handle = None

    def __del__(self):
        try:
            self.destroy()
        except Exception:
            # Destructors must not mask interpreter shutdown or an earlier error.
            pass

    def create(self):
        """Allocate and return the owned native interference context."""
        self.destroy()
        self._handle = _native.FX_Interf_Create()
        return self._handle

    def destroy(self):
        """Release the native context. Repeated calls are safe."""
        if self._handle is not None:
            _native.FX_Interf_Destroy(self._handle)
            self._handle = None

    def init(self, cord_def, cal_link_def, input_def, convex_def, ic_def):
        """Load coordinate, link, input, convex, and interference definitions."""
        if self._handle is None:
            return FUNC_RET_OPERATION_FAILED
        return _native.FX_Interf_Init(
            self._handle, cord_def, cal_link_def, input_def, convex_def, ic_def
        )

    def update_cord(self, cord_num, input_data):
        """Update one coordinate group with its current double values."""
        if self._handle is None:
            return FUNC_RET_OPERATION_FAILED
        return _native.FX_Interf_UpdateCord(
            self._handle, int(cord_num), [float(value) for value in input_data]
        )

    def update_convex(self):
        """Rebuild convex collision geometry after coordinate updates."""
        if self._handle is None:
            return FUNC_RET_OPERATION_FAILED
        return _native.FX_Interf_UpdateConvex(self._handle)

    def calc_interf_distance(self):
        """Calculate minimum distances for every configured collision pair."""
        if self._handle is None:
            return FUNC_RET_OPERATION_FAILED
        return _native.FX_Interf_CalcInterfDistance(self._handle)

    def get_com(self):
        """Return ``(status, [x, y, z])`` for the weighted center of mass."""
        if self._handle is None:
            return FUNC_RET_OPERATION_FAILED, [0.0, 0.0, 0.0]
        return _native.FX_Interf_GetCoM(self._handle)

    def get_cords_num(self):
        """Return ``(status, count)`` for the loaded coordinate groups."""
        if self._handle is None:
            return FUNC_RET_OPERATION_FAILED, 0
        return _native.FX_Interf_GetCordsNum(self._handle)

    def get_mass(self, count):
        """Return ``(status, masses)`` for all configured rigid bodies.

        ``count`` must equal the coordinate count reported by
        :meth:`get_cords_num`; a mismatch raises ``ValueError`` before entering
        the native SDK.
        """
        if self._handle is None:
            return FUNC_RET_OPERATION_FAILED, []
        return _native.FX_Interf_GetMass(self._handle, int(count))

    def get_min_span(self):
        """Return ``(status, distance)`` for the global minimum separation."""
        if self._handle is None:
            return FUNC_RET_OPERATION_FAILED, 0.0
        return _native.FX_Interf_GetMinSpan(self._handle)

    def get_interf_span(self, serial):
        """Return ``(status, distance)`` for one collision pair."""
        if self._handle is None:
            return FUNC_RET_OPERATION_FAILED, 0.0
        return _native.FX_Interf_GetInterfSpan(self._handle, int(serial))

    def on_is_interf(self, thresholds):
        """Return the official interference status for the configured thresholds."""
        if self._handle is None:
            return FUNC_RET_OPERATION_FAILED
        return _native.FX_Interf_OnIsInterf(
            self._handle, [float(value) for value in thresholds]
        )


__all__ = [
    "Marvin_Interference",
    "FUNC_RET_SUCCESS",
    "FUNC_RET_INVALID_INPUT_ARG",
    "FUNC_RET_OPERATION_FAILED",
    "FUNC_RET_ISInterference",
    "FUNC_RET_NOInterference",
]
