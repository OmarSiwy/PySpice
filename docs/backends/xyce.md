# Xyce Backend

Sandia National Laboratories' parallel circuit simulator. Strongest for
statistical analysis (Monte Carlo, PCE), Harmonic Balance, and large circuits.

## Detection

Binary: `Xyce` on `$PATH`.

Two modes:
- **Serial** (`xyce-serial`): `Xyce -r output.raw input.cir`
- **Parallel** (`xyce-parallel`): `mpirun -np N Xyce -r output.raw input.cir`

## Analyses

### Core

| Analysis | Statement | PySpice Method |
|----------|-----------|----------------|
| Operating Point | `.OP` | `operating_point()` |
| DC Sweep | `.DC src start stop step` | `dc()` / `dc_multi()` |
| AC Small-Signal | `.AC DEC\|LIN\|OCT N fstart fstop` | `ac()` |
| Transient | `.TRAN tstep tstop [tstart]` | `transient()` |
| Noise | `.NOISE V(out) src DEC\|LIN\|OCT N fstart fstop` | `noise()` |

### Advanced (Xyce-unique or enhanced)

| Analysis | Statement | PySpice Method |
|----------|-----------|----------------|
| Harmonic Balance | `.HB freq1 [freq2 ...]` | `harmonic_balance()` |
| Sensitivity (DC) | `.SENS objfunc={expr} param=P1,P2` | `sensitivity()` |
| Sensitivity (Transient) | `.SENS objfunc={expr} param=P1,P2` + `.OPTIONS SENSITIVITY direct=1` | `sensitivity()` |
| Sensitivity (AC) | `.SENS objvars=N param=P1,P2` | `sensitivity()` |
| S-Parameters | `.LIN sparcalc=1 format=touchstone` (with `.AC`) | `s_param()` |
| Random Sampling | `.SAMPLING useExpr=true` | `sampling()` |
| Embedded Sampling | `.EMBEDDEDSAMPLING useExpr=true` | `embedded_sampling()` |
| Polynomial Chaos | `.PCE useExpr=true` | `pce()` |
| Parameter Step | `.STEP param start stop step` | `step()` |

### Post-Processing

| Command | Description | PySpice Method |
|---------|-------------|----------------|
| `.MEAS type name TYPE var ...` | Measurement | `measure()` |
| `.FOUR freq var` | Fourier (DC + 9 harmonics) | `fourier()` |
| `.FFT V(out)` | FFT with windowing + ENOB/SFDR/SNR/THD | `fft()` |

## Netlist Format

Extended SPICE. Case-insensitive. Key extensions:

```spice
.TITLE My Circuit
V1 in 0 DC 1.0
R1 in out 1k

* Xyce expression parameters
.PARAM rval={agauss(100,5,1)}

* Harmonic Balance
.HB 1e4
.OPTIONS HBINT numfreq=7

* Sensitivity with adjoint
.SENS objfunc={V(out)} param=R1:R,C1:C
.OPTIONS SENSITIVITY direct=1 adjoint=1

* S-parameters (requires port definitions)
P1 1 0 port=1
P2 2 0 port=2 z0=50
.AC DEC 10 1K 100MEG
.LIN sparcalc=1 format=touchstone

* Monte Carlo via sampling
.SAMPLING useExpr=true
.OPTIONS SAMPLES numsamples=100 sample_type=lhs
+ outputs={V(out)} stdoutput=true
.PARAM R1val={aunif(1k,100)}

.END
```

## Output Formats

Controlled via `.PRINT FORMAT=`:

| Format | Extension | Flag |
|--------|-----------|------|
| `STD` | `.prn` | (default) |
| `CSV` | `.csv` | |
| `RAW` | `.raw` | or `-r file` CLI |
| `TECPLOT` | `.dat` | |
| `GNUPLOT` | `.prn` | |
| `PROBE` | `.csd` | |

CLI flags: `-r file.raw` (binary raw), `-r file.raw -a` (ASCII raw).

## Xyce-Unique Capabilities

### Harmonic Balance (.HB)
Non-linear frequency-domain steady state. Single or multi-tone.
```
.HB 1e9              ; single tone at 1 GHz
.HB 1e9 1e3          ; two tones
.OPTIONS HBINT numfreq=7,3 tahb=1
```
Output: time-domain (`.HB.TD`) and frequency-domain (`.HB.FD`) files.
`tahb=1` enables Transient-Assisted HB for better convergence.

### Embedded Sampling
Propagates all Monte Carlo samples simultaneously through a block linear system.
Much faster than sequential sampling for linear-ish circuits.
```
.EMBEDDEDSAMPLING useExpr=true
.OPTIONS EMBEDDEDSAMPLES outputs={V(out)}
+ projection_pce=true
```

### PCE (Polynomial Chaos Expansion)
Fully intrusive spectral projection. Computes statistical moments without
repeated simulations.
```
.PCE useExpr=true
.OPTIONS PCES OUTPUTS=R4:R,D1:IS outputs={V(4)}
```

### FFT with Quality Metrics
```
.FFT V(out) NP=8192 WINDOW=HANN FORMAT=UNORM
.MEAS FFT myENOB ENOB V(out)
.MEAS FFT mySFDR SFDR V(out)
.MEAS FFT mySNR FIND SNR(V(out)) AT=1
```

## Circuit Feature Support

| Feature | Supported | Notes |
|---------|-----------|-------|
| **XSPICE A-elements** | No | Circuits with `A` elements cannot run on Xyce. |
| **OSDI / Verilog-A** | No | Xyce uses its own device plugin system, not OSDI. |

## What Xyce Cannot Do

- `.pz` (Pole-Zero) — use ngspice
- `.disto` (Distortion) — use ngspice
- `.tf` (Transfer Function) — use `.DC` with small-signal sweep
- No interactive mode / control language
- No `.control` blocks
- No XSPICE code models
- No OSDI/Verilog-A model loading

## Parallel Execution Notes

- Processors must be < number of devices + voltage nodes
- Linux/macOS only (no Windows parallel)
- Use `--bind-to none` with OpenMPI on multi-user systems
- Circuits need ~1000+ devices to benefit from parallelism
- `.SAMPLING` distributes sample points across processors (embarrassingly parallel)
