# Vacask Backend

Verilog-A Circuit Analysis Kernel. Modern C++20 simulator from the EDA Laboratory,
University of Ljubljana. Builds device models from Verilog-A via OpenVAF/OSDI.

Project: https://codeberg.org/arpadbuermen/VACASK

## Detection

Binary: `vacask` on `$PATH`.

## Analyses

| Analysis | Keyword | Description | PySpice Method |
|----------|---------|-------------|----------------|
| Operating Point | `op` | DC bias (Newton-Raphson + homotopy) | `operating_point()` |
| DC Small-Signal | `dcinc` | Linearization at OP | — |
| DC Transfer Function | `dcxf` | DC transfer functions and impedances | `transfer_function()` |
| AC Small-Signal | `ac` | Frequency sweep | `ac()` |
| AC Transfer Function | `acxf` | AC transfer functions vs frequency | `ac_transfer_function()` |
| AC Stability | `acstb` | Open-loop gain of feedback circuits | `stability()` |
| AC S-Parameters | `acsp` | Multi-port S-parameters | `s_param()` |
| Noise | `noise` | Small-signal noise spectral densities | `noise()` |
| Transient | `tran` | Time-domain integration | `transient()` |
| Transient Noise | `trannoise` | Time-domain with device noise injection | `transient_noise()` |
| Harmonic Balance | `hb` | Periodic steady-state (multi-tone) | `harmonic_balance()` |

## Netlist Format

Vacask uses a **Spectre-like syntax**, NOT standard SPICE.

```
* Title: My Amplifier

load "bsim4.osdi"

global 0

v1 (in 0) vsource dc=0.6 type="sine" ampl=10m freq=1k
v2 (vdd 0) vsource dc=1.2

r1 (vdd out) resistor r=10k
c1 (out 0) capacitor c=1p

m1 (out in 0 0) nmos4 w=1u l=100n

op1 op

ac1 ac start=1 stop=10G dec=10

tran1 tran stop=10u
```

### Key syntax differences from SPICE

| Feature | SPICE | Vacask |
|---------|-------|--------|
| Instance | `R1 a b 1k` | `r1 (a b) resistor r=1k` |
| Source | `V1 a b DC 1.2` | `v1 (a b) vsource dc=1.2` |
| MOSFET | `M1 d g s b model` | `m1 (d g s b) model w=1u l=100n` |
| Analysis | `.ac dec 10 1 1G` | `ac1 ac start=1 stop=1G dec=10` |
| Comment | `* comment` | `// comment` (also `*`) |
| Terminals | space-separated | parenthesized: `(a b)` |
| Parameters | positional | named: `r=1k` |

### SPICE-to-Vacask Translation

PySpice automatically translates SPICE netlists to Vacask format.
The translation handles:
- Component syntax: `R1 a b 1k` -> `r1 (a b) resistor r=1k`
- Source syntax: `V1 a b DC 3.3` -> `v1 (a b) vsource dc=3.3`
- Analysis statements: `.ac dec 10 1 1G` -> `ac1 ac start=1 stop=1G dec=10`
- `.model` -> `model`
- `.include` -> `include`
- `.param` -> `parameters`

An upstream `ng2vc.py` converter also exists (under development).

## Output Format

SPICE raw file format (binary or ASCII), controlled by the `rawfile` option.
**Fully compatible with our existing raw file parser.**

Output files are named `<analysis>.*` (e.g., `op1.raw`, `ac1.raw`).

### Variable naming conventions
- Node voltages: node name (e.g., `out`)
- Branch currents: `instance:flow(br)`
- Device output variables: `instance.varname`

## Vacask-Unique Capabilities

### AC Stability Analysis (acstb)
Built-in loop-gain analysis for feedback circuits. Computes gain margin
and phase margin directly.
```
acstb1 acstb start=1 stop=10G dec=10 probe=iprobe0
```

### Transient Noise (trannoise)
Time-domain simulation with device noise injection. Shows noise effects
in time domain rather than frequency domain.
```
trannoise1 trannoise stop=1m
```

### Harmonic Balance
Periodic steady-state in frequency domain. Multi-tone capable.
```
hb1 hb fund=1G nharms=7
```

## Circuit Feature Support

| Feature | Supported | Notes |
|---------|-----------|-------|
| **XSPICE A-elements** | No | Vacask does not support XSPICE code models. |
| **OSDI / Verilog-A** | Yes | Core strength — Vacask is built around OSDI. All device models are Verilog-A compiled via OpenVAF. |

### Native Verilog-A Support
Any Verilog-A model can be compiled and loaded at runtime via OSDI:
```
load "mymodel.osdi"
m1 (d g s b) mymodel w=1u l=100n
```

## Device Library

Built-in: vsource, isource, vcvs, vccs, ccvs, cccs, mutual
Precompiled OSDI: resistor, capacitor, inductor, diode, opamp
Third-party: BSIM3v3, BSIM4v8, PSP103.4, BSIMBULK, VBIC (3/4/5 terminal)

## Performance

Benchmarks (C6288 multiplier, 2016 devices):
- Vacask: 57.98s, 138.5 MB
- NGSpice: 71.81s, 200.5 MB
- Xyce: 151.57s, 775.7 MB

## What Vacask Cannot Do

- No DC sweep (only operating point)
- No `.meas` / `.four` post-processing
- No Monte Carlo / parameter stepping built-in
- No pole-zero analysis
- No distortion analysis
- No sensitivity analysis
- No XSPICE code models
