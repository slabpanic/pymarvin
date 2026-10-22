# Integrated Marvin SDK sources

The official SDK snapshot bundled here was obtained from the `master` branch
of [TJ_FX_ROBOT_CONTRL_SDK](https://github.com/cynthia-you/TJ_FX_ROBOT_CONTRL_SDK)
at commit `bc4f61104a66e82b4c750f3a0bc7a95c9ef44139`. See
`THIRD_PARTY_NOTICES.md` for licensing and local binding changes.

- `control/`: active Tianji Marvin control SDK, version 100343014.
- `kinematics/`: offline kinematics, Jacobian, planning and identification SDK.
- `interference/`: collision-distance and interference-check SDK.

These Apache-2.0 sources are compiled directly into separate nanobind extensions.
The interference definition files are packaged under
`src/pymarvin/interference_configs/`.
Only the implementation files and headers required by the build are retained.
Licensing and modifications are documented in `THIRD_PARTY_NOTICES.md` and
`src/pymarvin/licenses/marvin-sdk/`.

Linux builds use the SDK's POSIX implementation. Windows builds use its Windows
implementation, Winsock and multimedia timers. Public C `long` arguments follow
the platform ABI; fixed-width telemetry fields retain the controller wire layout.
