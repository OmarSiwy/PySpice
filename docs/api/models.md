# Models and Subcircuits

Device models define the electrical behavior of semiconductor components. Subcircuits let you package a group of components into a reusable block.

## Device Models

### Defining a Model -- `model(name, kind, **params)`

Every semiconductor device (diode, transistor, etc.) needs a model that describes its physical characteristics.

```python
circuit.model("1N4148", "D",
    IS=2.52e-9,    # saturation current
    RS=0.568,      # series resistance
    N=1.752,       # emission coefficient
    BV=100,        # breakdown voltage
    IBV=100e-6     # breakdown current
)
```

Netlist output: `.model 1N4148 D(IS=2.52e-09 RS=0.568 N=1.752 BV=100 IBV=0.0001)`

### Common Model Types

| `kind` string | Description | Used with |
|---------------|-------------|-----------|
| `"D"` | Diode | `D()` |
| `"NPN"` | NPN bipolar transistor | `Q()`, `BJT()` |
| `"PNP"` | PNP bipolar transistor | `Q()`, `BJT()` |
| `"NMOS"` | N-channel MOSFET | `M()`, `MOSFET()` |
| `"PMOS"` | P-channel MOSFET | `M()`, `MOSFET()` |
| `"NJF"` | N-channel JFET | `J()` |
| `"PJF"` | P-channel JFET | `J()` |
| `"NMF"` | N-channel MESFET | `Z()` |
| `"SW"` | Voltage-controlled switch | `S()` |
| `"CSW"` | Current-controlled switch | `W()` |

### Example: CMOS Models

```python
# Level 1 MOSFET models (simple, good for learning)
circuit.model("nch", "NMOS",
    LEVEL=1,
    VTO=0.4,       # threshold voltage
    KP=200e-6      # transconductance parameter
)

circuit.model("pch", "PMOS",
    LEVEL=1,
    VTO=-0.4,      # threshold (negative for PMOS)
    KP=100e-6
)
```

### Example: BJT Model

```python
circuit.model("npn_amp", "NPN",
    BF=200,        # forward current gain (beta)
    IS=1e-14,      # saturation current
    CJC=5e-12,     # collector-base capacitance
    RB=100         # base resistance
)
```

### Model Without Parameters

You can define a model with no parameters (uses simulator defaults):

```python
circuit.model("mydiode", "D")
```

## Including External Model Files

Real-world models are often provided as separate files (from PDK vendors, component manufacturers, etc.).

### `.include` -- Include a SPICE file

```python
circuit.include("/path/to/sky130_fd_pr/nfet_01v8.spice")
```

Netlist output: `.include /path/to/sky130_fd_pr/nfet_01v8.spice`

The included file is read by the SPICE simulator at runtime. It can contain model definitions, subcircuit definitions, or any valid SPICE statements.

### `.lib` -- Include a library section

Library files can contain multiple sections. Use `.lib` to include a specific one:

```python
circuit.lib("/path/to/models.lib", "tt")   # typical-typical corner
circuit.lib("/path/to/models.lib", "ff")   # fast-fast corner
```

Netlist output: `.lib /path/to/models.lib tt`

## Parameters

Define global parameters that can be used in expressions:

```python
circuit.parameter("Rval", "1k")
circuit.parameter("Cval", "10p")
circuit.parameter("gain", "100")

# Use parameters in component values
circuit.R(
    name="1",
    positive="a",
    negative="b",
    value=0,
    raw_spice="{Rval}",
)
```

Netlist output:
```
.param Rval=1k
.param Cval=10p
.param gain=100
R1 a b {Rval}
```

## Subcircuits

Subcircuits let you define a reusable block of components and instantiate it multiple times.

### Defining a Subcircuit with `raw_spice`

```python
circuit = Circuit("Ring Oscillator with Subcircuits")

circuit.V(
    name="dd",
    positive="vdd",
    negative=circuit.gnd,
    value=1.8,
)
circuit.model("nch", "NMOS", LEVEL=1, VTO=0.4, KP=200e-6)
circuit.model("pch", "PMOS", LEVEL=1, VTO=-0.4, KP=100e-6)

# Define the subcircuit
circuit.raw_spice(".subckt inverter in out vdd vss")
circuit.raw_spice("Mn out in vss vss nch")
circuit.raw_spice("Mp out in vdd vdd pch")
circuit.raw_spice(".ends inverter")

# Instantiate it three times
circuit.X("1", "inverter", "n1", "n2", "vdd", "0")
circuit.X("2", "inverter", "n2", "n3", "vdd", "0")
circuit.X("3", "inverter", "n3", "n1", "vdd", "0")
```

### Understanding Subcircuit Pins

The `.subckt` line declares the interface:

```
.subckt inverter in out vdd vss
```

This says the subcircuit "inverter" has 4 pins: `in`, `out`, `vdd`, `vss`.

When you instantiate it:

```python
circuit.X("1", "inverter", "n1", "n2", "vdd", "0")
```

The pins are mapped positionally:
- `in` -> `n1`
- `out` -> `n2`
- `vdd` -> `vdd`
- `vss` -> `0` (ground)

### Netlist Output

```spice
.title Ring Oscillator with Subcircuits
Vdd vdd 0 1.8
.model nch NMOS(LEVEL=1 VTO=0.4 KP=0.0002)
.model pch PMOS(LEVEL=1 VTO=-0.4 KP=0.0001)
X1 n1 n2 vdd 0 inverter
X2 n2 n3 vdd 0 inverter
X3 n3 n1 vdd 0 inverter
.subckt inverter in out vdd vss
Mn out in vss vss nch
Mp out in vdd vdd pch
.ends inverter
.end
```

## Complete Example: Op-Amp with Models

```python
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm, u_uF

circuit = Circuit("Inverting Amplifier")

# Power supply
circuit.V(
    name="cc",
    positive="vcc",
    negative=circuit.gnd,
    value=15.0,
)
circuit.V(
    name="ee",
    positive="vee",
    negative=circuit.gnd,
    value=-15.0,
)

# Include op-amp model from file
circuit.include("/path/to/ua741.spice")

# Input signal
circuit.SinusoidalVoltageSource(
    name="in",
    positive="input",
    negative=circuit.gnd,
    amplitude=0.1,
    frequency=1000.0,
)

# Inverting amplifier: gain = -Rf/Rin = -10k/1k = -10
circuit.R(
    name="in",
    positive="input",
    negative="inv_input",
    value=1 @ u_kOhm,
)
circuit.R(
    name="f",
    positive="inv_input",
    negative="output",
    value=10 @ u_kOhm,
)

# Op-amp subcircuit instance
circuit.X("1", "ua741", "inv_input", circuit.gnd, "vcc", "vee", "output")

print(circuit)
```
