# Analysis Compatibility Matrix & Cross-Backend Mapping

## Full Matrix

Legend: **native** = built-in | *emulated* = achievable via workaround | — = not available

| Analysis | NGSpice | Xyce | LTspice | Vacask | Spectre |
|----------|---------|------|---------|--------|---------|
| **Operating Point** | `.op` | `.OP` | `.OP` | `op` | `dc` |
| **DC Sweep** | `.dc` | `.DC` | `.DC` | — | `dc` (sweep) |
| **AC Small-Signal** | `.ac` | `.AC` | `.AC` | `ac` | `ac` |
| **Transient** | `.tran` | `.TRAN` | `.TRAN` | `tran` | `tran` |
| **Noise** | `.noise` | `.NOISE` | `.NOISE` | `noise` | `noise` |
| **Transfer Function** | `.tf` | *(.DC sweep)* | `.TF` | `dcxf` | `xf` |
| **DC Sensitivity** | `.sens` | `.SENS` (enhanced) | — | — | `sens` |
| **AC Sensitivity** | `.sens ac` | `.SENS` (enhanced) | — | — | `sens` |
| **Transient Sensitivity** | — | `.SENS` (adjoint!) | — | — | — |
| **Pole-Zero** | `.pz` | — | — | — | — |
| **Distortion** | `.disto` | — | — | — | — |
| **Periodic Steady State** | `.pss` (exp.) | — | — | — | `pss` |
| **S-Parameters** | `.sp` | `.LIN` | `.NET` (limited) | `acsp` | `sp` |
| **Harmonic Balance** | — | `.HB` | — | `hb` | `hb` |
| **Stability (Loop Gain)** | *(.ac + post)* | — | — | `acstb` | `stb` |
| **AC Transfer Function** | *(.ac)* | — | — | `acxf` | `xf` |
| **Transient Noise** | — | — | — | `trannoise` | — |
| **Fourier** | `.four` | `.FOUR`/`.FFT` | `.FOUR` | — | — |
| **Measurement** | `.meas` | `.MEAS` | `.MEAS` | — | — |
| **Parameter Step** | *(.control loop)* | `.STEP` | `.STEP` | — | `sweep` |
| **Monte Carlo** | *(.control loop)* | `.SAMPLING` | *(.step list)* | — | `montecarlo` |
| **Embedded Sampling** | — | `.EMBEDDEDSAMPLING` | — | — | — |
| **PCE** | — | `.PCE` | — | — | — |
| **Periodic AC** | — | — | — | — | `pac` |
| **Periodic Noise** | — | — | — | — | `pnoise` |
| **DC Mismatch** | — | — | — | — | `dcmatch` |
| **FFT (ENOB/SFDR/SNR)** | — | `.FFT` | — | — | — |

## Emulation Strategies

When an analysis is not natively available on a backend, these workarounds
can produce equivalent results. PySpice applies these automatically when
the preferred backend lacks a native analysis.

### Transfer Function (.tf) on Xyce

Xyce has no `.TF`. Emulate with a DC sweep + computation:

```spice
* Compute transfer function V(out)/V(in)
V1 in 0 DC 0
R1 in mid 1k
R2 mid out 1k

.DC V1 -0.001 0.001 0.001
.PRINT DC V(out) I(V1)
```

Then: `gain = (V(out)@+1mV - V(out)@-1mV) / 0.002`
      `Rin = 0.002 / (I(V1)@+1mV - I(V1)@-1mV)`

### Pole-Zero on non-NGSpice backends

`.pz` is unique to NGSpice. Approximate via AC analysis + post-processing:

```
1. Run .ac over wide frequency range with fine resolution
2. Fit rational transfer function H(s) = N(s)/D(s) to AC data
3. Find roots of N(s) (zeros) and D(s) (poles)
```

Libraries like `scipy.signal` or vector fitting can extract poles/zeros
from frequency response data.

### Distortion on non-NGSpice backends

`.disto` is unique to NGSpice. Emulate via transient + FFT:

```spice
* Apply single-tone input
V1 in 0 SIN(0 1 1k)

.tran 1u 100m
```

Then FFT the output, measure HD2, HD3, THD from harmonic amplitudes.
Xyce's `.FFT` command can do this directly:
```spice
.FFT V(out) NP=8192 WINDOW=HANN
```

### Stability (Loop Gain) on NGSpice

NGSpice has no `stb`. Emulate with Middlebrook's method:

```spice
* Break the loop with an AC injection source
V_ac_inj feedback_in feedback_out AC 1
L_break feedback_in feedback_out 1T   ; DC short, AC open

.ac dec 100 1 10G

* Post-process:
* T(s) = -V(feedback_in) / V(feedback_out)  ; loop gain
* Gain margin = |T| at phase = -180deg
* Phase margin = 180 + angle(T) at |T| = 0dB
```

### Harmonic Balance on NGSpice

NGSpice has no `.HB`. For periodic steady state, use `.pss` (experimental)
or approximate with long transient + discard startup:

```spice
V1 in 0 SIN(0 1 1G)
.tran 0.01n 100n    ; 100 periods at 1GHz

* Post-process: discard first ~50ns, FFT the remaining
```

### Monte Carlo on NGSpice

Use `.control` block with statistical functions:

```spice
.control
set num_runs = 1000
let run = 0
while run < num_runs
  alter @R1[resistance] = 1k * (1 + sgauss(0) * 0.05)
  alter @C1[capacitance] = 10p * (1 + sgauss(0) * 0.10)
  run
  * collect results...
  let run = run + 1
end
.endc
```

Available distributions:
- `sgauss(seed)` — Gaussian (mean=0, sigma=1)
- `sunif(seed)` — Uniform [-1, +1]
- Custom via `define mygauss(nom, tol, sig) nom*(1+sgauss(seed)*tol/sig)`

### Monte Carlo on LTspice

Use `.step` with parameter randomization:

```spice
.param Rval=mc(1k, 0.05)    ; 5% tolerance
.step param run 1 100 1
```

Or use `.step` with explicit value lists for corner analysis.

### Parameter Step on NGSpice

No `.step` dot command. Use `.control` loops:

```spice
.control
foreach val 1k 2k 5k 10k
  alter R1 = $val
  run
end
.endc
```

Or nested DC sweep (limited to 2 variables):
```spice
.dc V1 0 5 0.1 temp -40 125 55
```

### S-Parameters on LTspice

`.NET` provides limited network parameters during AC:

```spice
.ac dec 100 1meg 10G
.NET I(R1) V1
```

For full S-parameter analysis, prefer NGSpice `.sp`, Xyce `.LIN`,
Vacask `acsp`, or Spectre `sp`.

### Sensitivity on LTspice

LTspice has no `.sens`. Emulate with parameter stepping:

```spice
.step param Rval list 990 1000 1010
.op
* Compute dV(out)/dR = (V(out)@1010 - V(out)@990) / 20
```

### Transient Noise on non-Vacask backends

Only Vacask has `trannoise`. Approximate on other backends:

```spice
* Add explicit noise sources
I_noise out 0 AC 0 trnoise(1n 0 0 0)    ; ngspice trnoise
.tran 1u 10m
```

NGSpice supports `trnoise` and `trrandom` on independent sources for
behavioral noise injection, but it's not the same as Vacask's device-level
noise propagation.

## Auto-Routing Rules

When `detect_and_select_with_features()` picks a backend, it applies two filters:

### 1. Analysis Preferences

Which backends support which analysis, in priority order:

```
pz, disto                       → must use ngspice
tf                              → ngspice > ltspice > vacask > spectre
hb                              → xyce > vacask > spectre
pss                             → spectre > ngspice (experimental)
s_param                         → xyce > vacask > spectre > ngspice
stability                       → vacask > spectre
sensitivity (transient/adjoint) → xyce only
sens_ac                         → ngspice > xyce > spectre
sampling, pce, embedded         → xyce only
periodic (pac, pnoise, pxf,     → spectre only
  pstb, psp, pdisto, hbac,
  hbnoise, hbsp)
transient_noise                 → vacask only
op, dc, ac, tran, noise         → any (prefer ngspice > xyce > ltspice > vacask > spectre)
```

### 2. Circuit Feature Constraints

Backends that don't support required circuit features are **skipped** during
selection. All features are AND-ed — a backend must pass every check:

| Circuit Feature | Supported Backends | Excluded Backends |
|----------------|-------------------|-------------------|
| **XSPICE A-elements** | ngspice | xyce, ltspice, vacask, spectre |
| **OSDI / Verilog-A** | ngspice, vacask, spectre | xyce, ltspice |
| **`.meas` directives** | ngspice, xyce, ltspice | vacask, spectre |
| **`.step` param sweeps** | xyce, ltspice, spectre | ngspice, vacask |
| **`.control` blocks** | ngspice | xyce, ltspice, vacask, spectre |
| **Laplace B-sources** | ngspice, ltspice | xyce, vacask, spectre |

Feature filtering happens **after** analysis preference ranking. Examples:

- OSDI + `.ac` → prefs `ngspice > xyce > ltspice > vacask > spectre` → xyce/ltspice filtered → picks **ngspice**
- XSPICE + `.tran` → only ngspice passes → picks **ngspice**
- XSPICE + `.hb` → hb prefs `xyce > vacask > spectre`, all filtered by XSPICE → **error**
- `.step` + `.meas` + `.ac` → prefs `ngspice > xyce > ...` → ngspice filtered (no .step), vacask/spectre filtered (no .meas) → picks **xyce** or **ltspice**
- `.control` + `.tran` → only ngspice → picks **ngspice**
- Laplace B-source + `.ac` → ngspice/ltspice pass → picks **ngspice** (higher priority)

### Feature Support Summary

```
                    XSPICE    OSDI    .meas    .step    .control    Laplace
ngspice              yes      yes      yes       no       yes        yes
xyce                  no       no      yes      yes        no         no
ltspice               no       no      yes      yes        no        yes
vacask                no      yes       no       no        no         no
spectre               no      yes       no      yes        no         no
```
