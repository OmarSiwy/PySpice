# LTspice Backend

Analog Devices' free SPICE simulator. Extremely popular, especially for
power electronics and signal integrity. Windows/macOS native, Linux via Wine.

## Detection

Platform-specific executable paths:

| Platform | Binary | Typical Path |
|----------|--------|-------------|
| Windows | `LTspice.exe` | `%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe` |
| macOS | `LTspice` | `/Applications/LTspice.app/Contents/MacOS/LTspice` |
| Linux | via Wine | `wine ~/.wine/.../LTspice.exe` |
| Legacy | `XVIIx64.exe` | `C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe` |

Detection order: `LTspice.exe` > `XVIIx64.exe` on PATH, then platform-specific paths.

## Analyses

| Analysis | Statement | PySpice Method |
|----------|-----------|----------------|
| Operating Point | `.OP` | `operating_point()` |
| DC Sweep | `.DC src start stop step` | `dc()` |
| AC Small-Signal | `.AC dec\|oct\|lin N fstart fstop` | `ac()` |
| Transient | `.TRAN tstep tstop [tstart [tmaxstep]] [startup] [uic] [steady]` | `transient()` |
| Noise | `.NOISE V(out[,ref]) src dec\|oct\|lin N fstart fstop [Nper]` | `noise()` |
| Transfer Function | `.TF outvar insrc` | `transfer_function()` |

### Post-Processing / Modifiers

| Command | Description | PySpice Method |
|---------|-------------|----------------|
| `.STEP` | Parameter sweep | `step()` |
| `.MEAS` / `.MEASURE` | Measurement extraction | `measure()` |
| `.FOUR freq [Nharm] var` | Fourier analysis | `fourier()` |
| `.NET` | S/Z/Y/H network parameters during `.AC` | `network_params()` |

## Invocation

```
LTspice.exe -b circuit.cir                    # Windows
wine LTspice.exe -b circuit.cir               # Linux
/Applications/LTspice.app/.../LTspice -b circuit.cir  # macOS
```

Key flags:
- `-b` — batch mode (no GUI, essential)
- `-ascii` — force ASCII raw output
- `-Run` — open + simulate (keeps GUI)
- `-netlist` — convert `.asc` schematic to `.cir`

## Raw File Format Quirks

LTspice raw files differ from ngspice in several ways:

| Property | NGSpice | LTspice |
|----------|---------|---------|
| Header encoding | UTF-8 | **UTF-16-LE** (or UTF-8 if all ASCII) |
| Line endings | LF | **CRLF** |
| TRAN trace precision | f64 (8 bytes) | **f32 (4 bytes)** for traces, f64 for time |
| Compression | None | **Lossy compression** by default |

### Normalization

We inject these options into every netlist sent to LTspice:

```spice
.options plotwinsize=0    ; disable lossy compression
.options numdgt=15        ; force f64 precision for all traces
```

This makes the raw file format **identical to ngspice**, allowing our
existing parser to handle it without modification.

## LTspice-Unique Features

### .NET (Network Parameters)
Compute S/Z/Y/H-parameters during AC analysis:
```spice
.AC dec 10 1k 1G
.NET I(R1) V1
```
Not available in ngspice (use Xyce `.LIN` or Vacask `acsp` instead).

### .MACHINE (State Machines)
Define arbitrary state machines for mixed-signal modeling:
```spice
.MACHINE
.state idle running done
.rule idle->running if V(start)>2.5
.rule running->done if V(count)>10
.output V(out) idle=0 running=3.3 done=0
.ENDMACHINE
```

### .WAVE (Audio Export)
Write waveform data to `.wav` audio file:
```spice
.WAVE "output.wav" 16 44.1k V(out)
```

### B-Source Extensions
LTspice B-sources support Laplace transforms:
```spice
B1 out 0 V=Laplace(V(in), 1/(1+s/6.28e3))
```

## Circuit Feature Support

| Feature | Supported | Notes |
|---------|-----------|-------|
| **XSPICE A-elements** | No | LTspice has its own digital primitives but not XSPICE `A` elements. |
| **OSDI / Verilog-A** | No | No OSDI support. LTspice has built-in device models only. |

## What LTspice Cannot Do

- No Pole-Zero (`.pz`)
- No Distortion (`.disto`)
- No Sensitivity (`.sens`)
- No Harmonic Balance
- No Monte Carlo (use `.step` with parameter lists)
- No S-parameters (`.NET` is limited)
- No shared library / programmatic API
- No Linux native binary (requires Wine)
- No XSPICE code models
- No OSDI/Verilog-A model loading
