# Spectre Backend

Cadence's Spectre Circuit Simulator. Industry-standard for analog/RF IC design.
Requires a commercial license.

## Detection

Binary: `spectre` on `$PATH`.

## Analyses

### Core (base Spectre license)

| Analysis | Keyword | Description | PySpice Method |
|----------|---------|-------------|----------------|
| DC / Operating Point | `dc` | DC bias or DC sweep | `operating_point()` / `dc()` |
| AC Small-Signal | `ac` | Linearized frequency response | `ac()` |
| Transient | `tran` | Time-domain simulation | `transient()` |
| Noise | `noise` | Small-signal noise | `noise()` |
| Stability | `stb` | Loop gain, gain/phase margin | `stability()` |
| Transfer Function | `xf` | Transfer function from any source | `transfer_function()` |
| S-Parameters | `sp` | N-port S-parameter analysis | `s_param()` |
| Sensitivity | `sens` | Parameter sensitivity | `sensitivity()` |
| Sweep | `sweep` | Parametric sweep wrapper | `sweep()` |
| Monte Carlo | `montecarlo` | Statistical variation | `monte_carlo()` |
| DC Match | `dcmatch` | Device mismatch analysis | — |
| Info | `info` | Op-point/model/instance data | — |
| TDR | `tdr` | Time-domain reflectometry | — |

### SpectreRF (requires RF option license)

| Analysis | Keyword | Description | PySpice Method |
|----------|---------|-------------|----------------|
| Periodic Steady State | `pss` | Find periodic operating point | `pss()` |
| Periodic AC | `pac` | AC around periodic OP | `periodic_ac()` |
| Periodic Noise | `pnoise` | Noise around periodic OP | `periodic_noise()` |
| Periodic Transfer Func | `pxf` | XF around periodic OP | — |
| Periodic Stability | `pstb` | STB around periodic OP | — |
| Periodic S-Parameter | `psp` | SP around periodic OP | — |
| Periodic Distortion | `pdisto` | Distortion around periodic OP | — |
| Harmonic Balance | `hb` | Frequency-domain nonlinear SS | `harmonic_balance()` |
| HB AC | `hbac` | AC around HB OP | — |
| HB Noise | `hbnoise` | Noise around HB OP | — |
| HB S-Parameter | `hbsp` | S-param around HB OP | — |
| Envelope Following | `envlp` | Modulated signal analysis | — |
| Load Pull | `loadpull` | PA impedance sweep | — |

## Invocation

```bash
spectre input.scs                                          # basic
spectre -format nutbin -raw ./results input.scs            # ngspice-compatible output
spectre -format psfascii -raw ./results input.scs          # ASCII PSF
spectre +log spectre.log -raw ./results input.scs          # with log file
```

Key flags:
- `-format nutbin` — **Nutmeg binary** (ngspice-compatible raw file!)
- `-format psfascii` — ASCII PSF (Cadence format, human-readable)
- `-format psfbin` — Binary PSF (default)
- `-raw <dir>` — output directory
- `+log <file>` — log to file + stdout
- `+mt=<N>` — multi-threaded

## Netlist Format

Spectre has its own syntax but supports inline SPICE mode:

```spectre
// Spectre-native syntax
simulator lang=spectre

global 0

parameters vdd_val=1.2

include "/path/to/models.scs" section=tt

V0 (vdd 0) vsource dc=vdd_val type=dc
R0 (vout 0) resistor r=10k
C0 (vout 0) capacitor c=1p
M0 (vout vin 0 0) nmos4 w=1u l=100n

save vout vin M0:ids

dc1 dc dev=V0 param=dc start=0 stop=1.8 step=0.01
ac1 ac start=1 stop=10G dec=20
tran1 tran stop=10u errpreset=moderate
```

### SPICE Compatibility Mode

Spectre can read standard SPICE netlists via language switching:

```spectre
simulator lang=spice

.title My Circuit
V1 in 0 DC 1.0
R1 in out 1k
.ac dec 10 1 1G
.end

simulator lang=spectre
```

**PySpice uses this**: we wrap SPICE netlists in `simulator lang=spice` blocks,
allowing us to send standard SPICE netlists to Spectre without translation.

## Output Formats

### Nutmeg (recommended for PySpice)

Using `-format nutbin` or `-format nutascii`, Spectre produces output files
that are identical to ngspice raw files. Our existing parser handles them
directly.

### PSF (Parameter Storage Format)

Cadence's proprietary format. Four sections: HEADER, TYPE, SWEEP, TRACE, VALUE.

Libraries for parsing: `psf_utils` (Python, ASCII only), `psf-parser` (both).

The `logFile` in the output directory indexes all result files.

## Key Differences from SPICE

| Feature | SPICE | Spectre |
|---------|-------|---------|
| Instance | `R1 a b 1k` | `R1 (a b) resistor r=1k` |
| Case | insensitive | **sensitive** |
| Comments | `*` at line start | `//` C-style |
| Continuation | `+` at start | `\` at end |
| `m` suffix | milli (1e-3) | milli; `M` = Mega |
| Subcircuit | `.SUBCKT` / `.ENDS` | `subckt` / `ends` |
| Analysis | `.ac dec 10 1 1G` | `ac1 ac start=1 stop=10G dec=10` |

## Spectre-Unique Capabilities

### Stability Analysis (stb)
Direct loop-gain measurement via return-ratio method:
```spectre
IPROBE0 (mid out) iprobe
stb1 stb start=1 stop=10G dec=10 probe=IPROBE0
```

### Periodic Analyses (SpectreRF)
Full suite of analyses around a periodic operating point — essential for
mixer, oscillator, and PLL design:
```spectre
pss1 pss fund=2.4G harms=7 tstab=50n
pac1 pac start=1k stop=100M dec=10 maxsideband=5
pnoise1 pnoise (out 0) start=100 stop=10M dec=10 maxsideband=10
```

### Nested Sweep
```spectre
swp1 sweep param=Rval values=[1k 2k 5k 10k] {
    ac1 ac start=1 stop=10G dec=10
}
```

### errpreset
Convenient convergence presets:
```spectre
tran1 tran stop=10u errpreset=conservative  // liberal | moderate | conservative
```

## Circuit Feature Support

| Feature | Supported | Notes |
|---------|-----------|-------|
| **XSPICE A-elements** | No | Spectre has its own behavioral modeling (Verilog-A, ahdl) but not XSPICE `A` elements. |
| **OSDI / Verilog-A** | Yes | Native Verilog-A compilation and loading. Spectre's primary device model language. |

## What Spectre Cannot Do

- No pole-zero analysis
- No distortion analysis (use `pdisto` for periodic circuits)
- Requires commercial license
- No programmatic/shared library API
- No XSPICE code models
