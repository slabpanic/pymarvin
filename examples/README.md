# Official Marvin examples

The project includes the official Tianji Marvin Python showcases, adapted to
import the packaged `pymarvin` API. The original showcase filenames and
control-flow examples are preserved for compatibility with existing workflows.

Most scripts connect to a real controller and can enable motion, torque, force,
drag, brake, reboot, or file-transfer operations. Read the source and test the
sequence on a safe setup before running one. The examples use conservative
velocity and acceleration values where the upstream showcase provided them,
but they are demonstrations rather than production safety logic. The offline
kinematics and interference examples are safe to run without a controller:

```bash
uv run --no-sync python examples/offline_kinematics.py
uv run --no-sync python examples/offline_interference.py
```

The controller and planning showcases require a matching robot model
configuration and runtime data. Set the configuration values and controller
address in the selected script before connecting.

Run a selected showcase with the installed package:

```bash
uv run --no-sync python examples/showcase_kinematics_all_functions.py
uv run --no-sync python examples/showcase_position.py
```

`showcase_drag_interference.py` uses the bundled `pymarvin.fx_interference`
interface and the model definition files shipped in the package. Select a
matching model before running it; the example still requires a real controller
and enters drag mode.

The examples are included in source distributions, while supported wheels
contain the runtime package only.
