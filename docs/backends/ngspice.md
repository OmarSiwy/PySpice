# NGSpice Backend

NGSpice is the default and most widely supported backend. Open-source (BSD),
available on all platforms.

## Detection

Binary: `ngspice` on `$PATH`.

Two modes:
- **Subprocess** (`ngspice-subprocess`): `ngspice -b -r output.raw input.cir`
- **Shared library** (`ngspice-shared`): `libngspice.so` / `libngspice.dylib` via dlopen

## Analyses

### Core (produce raw file output)

| Analysis | Statement | PySpice Method |
|----------|-----------|----------------|
| Operating Point | `.op` | `operating_point()` |
| DC Sweep | `.dc Vsrc start stop step` | `dc()` / `dc_multi()` |
| AC Small-Signal | `.ac dec\|oct\|lin N fstart fstop` | `ac()` |
| Transient | `.tran tstep tstop [tstart [tmax]] [uic]` | `transient()` |
| Noise | `.noise V(out,ref) src dec\|oct\|lin N fstart fstop [pps]` | `noise()` |
| Transfer Function | `.tf outvar insrc` | `transfer_function()` / `tf()` |
| DC Sensitivity | `.sens outvar` | `dc_sensitivity()` |
| AC Sensitivity | `.sens outvar ac dec\|lin\|oct N fstart fstop` | `ac_sensitivity()` |
| Pole-Zero | `.pz node1 node2 node3 node4 vol\|cur pol\|zer\|pz` | `polezero()` |
| Distortion | `.disto dec\|oct\|lin N fstart fstop [f2overf1]` | `distortion()` |
| Periodic Steady State | `.pss gfreq tstab oscnob psspoints harms [sciter [steadycoeff]] [uic]` | `pss()` |
| S-Parameters | `.sp dec\|oct\|lin N fstart fstop [donoise]` | `s_param()` |

### Post-Processing (stdout only in batch mode)

| Command | Description | PySpice Method |
|---------|-------------|----------------|
| `.four freq [Nharm] [Nperiods] var...` | Fourier analysis of transient | `fourier()` |
| `.meas tran\|dc\|ac name TYPE ...` | Measurement extraction | `measure()` |

### Shared Library API

The shared library mode (`libngspice.so`) provides:

```
ngSpice_Init()         — register callbacks
ngSpice_Circ()         — load circuit as string array
ngSpice_Command()      — send command ("run", "op", etc.)
ngGet_Vec_Info()       — retrieve result vectors directly
ngSpice_CurPlot()      — get current plot name ("tran1", "ac1")
ngSpice_AllVecs()      — list all vectors in a plot
```

Advantages over subprocess:
- No temp files
- Real-time data streaming via `SendData` callback
- Direct vector access (no raw file parsing)
- `.meas` results accessible as vectors
- `.four` results via `fourier` command create named vectors

## Netlist Format

Standard SPICE3f5. Case-insensitive. First line is title.

```spice
.title My Circuit
V1 in 0 DC 1.0
R1 in out 1k
C1 out 0 10p
.ac dec 10 1 1G
.end
```

## Output

Raw file format: binary (default) or ASCII.
- All values are f64 (8 bytes)
- Complex data: two f64 per value (re, im)
- Header: UTF-8
- Standard interleaved layout

## Circuit Feature Support

| Feature | Supported | Notes |
|---------|-----------|-------|
| **XSPICE A-elements** | Yes | Only backend with XSPICE support. Circuits using `A` elements (digital bridges, code models) are auto-routed here. |
| **OSDI / Verilog-A** | Yes | Load compiled `.osdi` modules via `pre_osdi` or `.osdi` directive. |

If a circuit uses XSPICE, ngspice is the **only** valid backend — auto-selection
will always pick it regardless of analysis preferences.

## NGSpice-Only Features

These analyses are **not available** on other backends:
- `.pz` (Pole-Zero)
- `.disto` (Distortion)

## Emulating Missing Analyses

NGSpice lacks built-in Harmonic Balance and Monte Carlo. Workarounds:

### Monte Carlo via .control
```spice
.control
let runs = 100
let i = 0
while i < runs
  alter @R1[resistance] = 1k * (1 + sgauss(0) * 0.05)
  op
  let i = i + 1
end
.endc
```

### Parameter Sweep via .control
```spice
.control
foreach rval 1k 2k 5k 10k
  alter R1 = $rval
  run
end
.endc
```

### Fourier (THD) via .control
```spice
.control
tran 1u 10m
fourier 1k v(out)
print fourier1[0] fourier1[1]  $ freq, magnitude
.endc
```
