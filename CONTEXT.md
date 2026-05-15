# PySpice-rs — Bounded Context

Universal SPICE circuit description and simulation library. Rust core, Python bindings via PyO3. Part of Schemify.

## Ubiquitous Language

| Term | Definition |
|------|-----------|
| **Subcircuit** | Named, parameterized, composable circuit fragment with typed ports. The unit of reuse. Can be nested, shared across projects, and serialized. |
| **Circuit** | Sugar over an anonymous top-level Subcircuit + Testbench. The "quick start" API — backwards-compatible with existing code. |
| **Testbench** | Wraps a Subcircuit (the DUT) with stimulus sources, loads, analysis commands, and measurements. Owns simulation configuration. Subcircuit is topology; Testbench is experiment. |
| **IR** | Backend-neutral intermediate representation. A graph of components, nodes, parameters, models, and directives. All validation, linting, and feature-detection operate on the IR, never on text. |
| **Code Generator** | A backend-specific module that walks the IR and emits native netlist syntax. ngspice emits SPICE3, Spectre emits Spectre syntax, etc. Replaces post-hoc string transforms. |
| **Backend** | A simulator that can execute a netlist: ngspice, xyce, ltspice, spectre, vacask. Selected at simulate-time, not circuit-build-time. |
| **ModelLibrary** | Opaque reference to a PDK or model collection. Knows which files to `.include`/`.lib` per backend and per corner. Does not parse model contents. |
| **Portable Option** | A simulation option with a curated canonical name (`reltol`, `max_iterations`, `temperature`) that the library maps to each backend's native syntax. |
| **Backend-Specific Option** | An option accessed through a backend namespace (`sim.spectre.options(errpreset="moderate")`). Explicitly non-portable. |
| **Analysis Tier** | Classification of analysis types: **Tier 1** (universal — op, dc, ac, tran, noise, tf, sens, pz, disto), **Tier 2** (portable across 2+ backends — pss, hb, s-param, stability), **Tier 3** (vendor-specific — accessed via `sim.xyce.*`, `sim.spectre.*`). |
| **Normalized Result** | Analysis output with backend-agnostic naming: nodes as lowercase (`result["out"]`), currents in canonical format (`result["I(Vdd)"]`), complex data always as complex, device operating points in a separate `.device` namespace. |
| **Feature Flag** | Property of a circuit IR (has_xspice, has_osdi, etc.) used for backend compatibility checking. `check_backend()` walks the IR and reports issues without spawning a process. |
| **Serialized IR** | JSON representation of the IR. The contract between Schemify's Zig schematic editor and PySpice-rs. Also the file format for saving/loading/sharing circuits. |

## Key Relationships

- A **Subcircuit** contains components, nested subcircuit instances, models, and parameters. It does *not* contain analysis directives.
- A **Testbench** references one Subcircuit as DUT, adds stimulus and measurement, and owns the simulation lifecycle.
- **Circuit** = anonymous Subcircuit + implicit Testbench. Calling `circuit.R(...)` adds to the subcircuit; calling `circuit.simulator()` creates the testbench.
- **Code Generators** are the *only* path from IR to text. No module builds netlist strings directly.
- **ModelLibrary** attaches to a Testbench (or Circuit). The code generator emits the right `.include`/`.lib` for the active backend.
- **Schemify** produces Serialized IR (JSON); PySpice-rs consumes it. Neither depends on the other's internal types.

## Invariants

- The IR is always backend-neutral. Backend-specific information lives in code generators and backend option namespaces, never in the IR graph.
- Every component in the IR has enough information for any supported code generator to emit it, or a feature flag marking it as backend-restricted (e.g., XSPICE).
- Results are normalized before reaching user code. Backend-specific naming conventions are stripped by the result parser, not by the user.
- `check_backend(name)` is a pure function of the IR — no I/O, no process spawning.
