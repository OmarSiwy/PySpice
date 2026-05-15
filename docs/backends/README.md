# PySpice Backend Reference

PySpice supports multiple SPICE simulator backends. Each backend has different
analysis capabilities, output formats, and platform requirements.

## Supported Backends

| Backend | Binary | Netlist Format | Output Format | License |
|---------|--------|----------------|---------------|---------|
| [NGSpice](ngspice.md) | `ngspice` | SPICE | Raw (binary/ASCII) | BSD |
| [Xyce](xyce.md) | `Xyce` | SPICE (extended) | Raw/CSV/Tecplot | GPL-3.0 |
| [LTspice](ltspice.md) | `LTspice.exe` | SPICE | Raw (quirks) | Proprietary (free) |
| [Vacask](vacask.md) | `vacask` | Spectre-like | Raw (binary/ASCII) | AGPL-3.0 |
| [Spectre](spectre.md) | `spectre` | Spectre (has SPICE mode) | PSF/Nutmeg | Commercial |

## Not Supported

| Simulator | Reason |
|-----------|--------|
| Qucsator | Effectively abandoned (last release 2020), poor transient/HB engines, fixed timestep only |
| HSPICE | Commercial, no batch mode documentation publicly available |
| PSpice | Legacy, superseded by other tools |

## Analysis Compatibility Matrix

See [analysis-map.md](analysis-map.md) for a complete mapping of which analyses
are available on which backends, and how to emulate missing analyses using
`.control` blocks and post-processing.

## Backend Selection

PySpice auto-detects available backends by scanning `$PATH`. Selection uses
three layers of filtering, applied in order:

1. **User override** — `circuit.simulator(simulator="xyce")` bypasses auto-detection
2. **Analysis routing** — some analyses only work on certain backends (see [analysis-map.md](analysis-map.md))
3. **Circuit feature filtering** — backends that don't support required circuit features are skipped
4. **Default preference** — ngspice > xyce > ltspice > vacask > spectre

### Circuit Feature Detection

The auto-selector inspects the circuit and simulator config for features that
constrain backend choice. Each feature acts as a **hard filter** — backends
that don't support it are excluded:

| Feature | Detection | Supported Backends |
|---------|-----------|-------------------|
| **XSPICE A-elements** | Circuit contains `A` element instances | ngspice |
| **OSDI / Verilog-A** | Circuit has `.osdi` / `pre_osdi` / `load` directives | ngspice, vacask, spectre |
| **`.meas` directives** | Simulator config has measure statements | ngspice, xyce, ltspice |
| **`.step` param sweeps** | Simulator config has step parameters | xyce, ltspice, spectre |
| **`.control` blocks** | Circuit raw lines contain `.control` | ngspice |
| **Laplace B-sources** | B-source expression contains `Laplace(` | ngspice, ltspice |

All features are AND-ed: a backend must support **every** detected feature to
be eligible. Examples:

- XSPICE circuit → only ngspice
- OSDI + `.meas` → only ngspice (vacask/spectre don't support `.meas`)
- `.step` + `.meas` → xyce or ltspice (both support both)
- `.control` + anything → ngspice (only backend with `.control`)

If no backend supports all required features, auto-selection returns an error
explaining which features conflict.

## Output Format Strategy

All backends are configured to produce **SPICE raw files** where possible:

- **NGSpice/Xyce/LTspice**: native raw file output
- **LTspice quirks**: we inject `.options plotwinsize=0 numdgt=15` to normalize
  the raw file format (disable compression, force f64 precision)
- **Vacask**: native raw file output (SPICE-compatible format)
- **Spectre**: uses `-format nutbin` flag to produce ngspice-compatible Nutmeg
  binary output instead of proprietary PSF
