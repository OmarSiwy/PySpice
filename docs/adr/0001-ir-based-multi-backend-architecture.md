# ADR-0001: IR-based multi-backend architecture

**Status:** Accepted
**Date:** 2026-05-14

## Context

PySpice-rs supports five simulator backends (ngspice, xyce, ltspice, spectre, vacask) that speak three different netlist languages (SPICE3, Spectre syntax, SPICE-subset). The original design generates a single SPICE3 netlist and applies post-hoc string transforms for non-SPICE backends (notably Spectre). This approach:

- Cannot represent Spectre-native constructs (`altergroup`, `paramset`) that have no SPICE3 equivalent
- Makes the Spectre backend fragile — regex transforms on generated text
- Prevents build-time validation of backend compatibility (feature checking requires parsing text back)
- Blocks a serializable interchange format with Schemify's Zig-based schematic editor

## Decision

The circuit representation is a **backend-neutral IR** (intermediate representation). Each backend has a dedicated **code generator** that walks the IR and emits native syntax directly.

### IR structure

- **Subcircuit**: named, parameterized, composable circuit fragment with typed ports — the unit of reuse
- **Testbench**: wraps a Subcircuit (DUT) with stimulus, analysis directives, measurements, and simulation options
- **Circuit**: sugar over anonymous Subcircuit + implicit Testbench (backwards-compatible convenience class)
- Components, models, directives, and parameters are IR nodes — not strings

### Code generators

One per backend. Each implements `fn emit(&self, ir: &CircuitIR) -> String`. No shared "SPICE3 base + fixup" path. The IR is the single source of truth; text is a leaf output.

### Serialization

The IR is serializable to JSON. This is the contract between Schemify (produces JSON from schematics) and PySpice-rs (consumes JSON, emits backend-native netlists). Also serves as the file format for saving/sharing circuits.

### Analysis tiering

- **Tier 1 (universal):** op, dc, ac, tran, noise, tf, sens, pz, disto — methods on Testbench/Simulator
- **Tier 2 (portable):** pss, hb, s-param, stability — methods on Testbench/Simulator, library selects compatible backend or errors
- **Tier 3 (vendor-specific):** accessed via `sim.xyce.*`, `sim.spectre.*` namespaces

### Result normalization

All backends return results through a normalized API: lowercase node names, canonical current format, complex data always as complex, device operating points in a `.device` namespace.

### Options mapping

Curated portable vocabulary (`reltol`, `max_iterations`, `temperature`) mapped per code generator. Backend-specific options via `sim.<backend>.options(...)`.

## Alternatives considered

1. **SPICE3-canonical + string translation** (status quo). Simpler, but Spectre support remains fragile, no Spectre-native features, no serializable format, no build-time validation.

2. **Abstract syntax tree per dialect.** Each backend gets its own AST type, with conversion functions between them. Overly complex — N AST types instead of one IR.

## Consequences

- Every component type needs an IR node definition and an emit implementation in each code generator (5x)
- The JSON schema becomes a versioned public contract — changes require migration
- `check_backend()` becomes a pure function over the IR with zero I/O
- Schemify's `Netlist.zig` will emit JSON IR instead of SPICE text
- XSPICE A-elements are IR nodes with a `requires_xspice` feature flag, not raw strings
- `raw_spice()` remains as an escape hatch but is discouraged — it bypasses the IR and is injected verbatim by all code generators
