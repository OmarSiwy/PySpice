# Circuit Building

The `Circuit` class is the heart of PySpice-rs. You create a circuit, add components to it, and then print the netlist or simulate.

```python
from pyspice_rs import Circuit
circuit = Circuit("My Circuit Title")
```

## Passive Components

### Resistor -- `R(*, name, positive, negative, value, raw_spice=None)`

A resistor connects two nodes with a resistance value.

```python
circuit.R(
    name="1",
    positive="input",
    negative="output",
    value=1e3,
)

circuit.R(
    name="load",
    positive="out",
    negative=circuit.gnd,
    value=10e3,
)

circuit.R(
    name="bias",
    positive="vdd",
    negative="gate",
    value=100 @ u_kOhm,
)
```

Netlist output: `R1 input output 1k`

You can also pass raw SPICE text for the value (useful for parameterized resistors):

```python
circuit.R(
    name="var",
    positive="a",
    negative="b",
    value=0,
    raw_spice="{Rval}",
)
```

Netlist output: `Rvar a b {Rval}`

### Capacitor -- `C(*, name, positive, negative, value)`

```python
circuit.C(
    name="1",
    positive="out",
    negative=circuit.gnd,
    value=100e-12,
)

circuit.C(
    name="bypass",
    positive="vdd",
    negative=circuit.gnd,
    value=100 @ u_nF,
)
```

Netlist output: `C1 out 0 100p`

### Inductor -- `L(*, name, positive, negative, value)`

```python
circuit.L(
    name="1",
    positive="in",
    negative="out",
    value=10e-6,
)

circuit.L(
    name="choke",
    positive="a",
    negative="b",
    value=1 @ u_mH,
)
```

Netlist output: `L1 in out 10u`

### Mutual Inductor (Transformer) -- `K(*, name, inductor1, inductor2, coupling)`

Couples two inductors magnetically. The coupling coefficient ranges from 0 (no coupling) to 1 (ideal transformer).

```python
# Two coupled inductors
circuit.L(
    name="primary",
    positive="p1",
    negative=circuit.gnd,
    value=1e-3,
)
circuit.L(
    name="secondary",
    positive="s1",
    negative=circuit.gnd,
    value=250e-6,
)

# Couple them (use inductor names WITHOUT the "L" prefix)
circuit.K(
    name="1",
    inductor1="primary",
    inductor2="secondary",
    coupling=1.0,
)
```

Netlist output: `K1 Lprimary Lsecondary 1`

The turns ratio is `N = sqrt(L1/L2)`. With L1=1mH and L2=250uH, N=2, so a 10V primary gives 5V secondary.

## Independent Sources

### DC Voltage Source -- `V(*, name, positive, negative, value)`

```python
circuit.V(
    name="dd",
    positive="vdd",
    negative=circuit.gnd,
    value=3.3,
)

circuit.V(
    name="in",
    positive="input",
    negative=circuit.gnd,
    value=1 @ u_V,
)
```

Current flows from positive to negative terminal inside the source.

### DC Current Source -- `I(*, name, positive, negative, value)`

```python
circuit.I(
    name="bias",
    positive=circuit.gnd,
    negative="tail",
    value=100e-6,
)
```

Current flows from positive to negative (external direction).

### Behavioral Voltage Source -- `BV(*, name, positive, negative, expression)`

Voltage defined by a mathematical expression:

```python
# Output = 1000 * (V(inp) - V(inm))  -- an ideal op-amp
circuit.BV(
    name="opamp",
    positive="out",
    negative=circuit.gnd,
    expression="1000*(V(inp)-V(inm))",
)
```

Netlist output: `Bopamp out 0 V=1000*(V(inp)-V(inm))`

### Behavioral Current Source -- `BI(*, name, positive, negative, expression)`

```python
circuit.BI(
    name="gm",
    positive="out",
    negative=circuit.gnd,
    expression="0.01*V(gate,source)",
)
```

## Controlled Sources

These are sources whose value depends on a voltage or current elsewhere in the circuit.

### VCVS (E) -- Voltage-Controlled Voltage Source

`E(*, name, positive, negative, control_positive, control_negative, voltage_gain)`

Output voltage = gain * V(control_positive, control_negative)

```python
# Buffer with gain 2: Vout = 2 * V(input, gnd)
circuit.E(
    name="1",
    positive="output",
    negative=circuit.gnd,
    control_positive="input",
    control_negative=circuit.gnd,
    voltage_gain=2.0,
)
```

Netlist output: `E1 output 0 input 0 2`

### VCCS (G) -- Voltage-Controlled Current Source

`G(*, name, positive, negative, control_positive, control_negative, transconductance)`

Output current = gm * V(control_positive, control_negative)

```python
# Transconductance amplifier: Iout = 0.001 * V(input, gnd)
circuit.G(
    name="1",
    positive="output",
    negative=circuit.gnd,
    control_positive="input",
    control_negative=circuit.gnd,
    transconductance=1e-3,
)
```

### CCCS (F) -- Current-Controlled Current Source

`F(*, name, positive, negative, vsense, current_gain)`

Output current = gain * I(Vsense). Requires a 0V voltage source to sense current:

```python
circuit.V(
    name="sense",
    positive="a",
    negative="a_sense",
    value=0.0,
)
circuit.F(
    name="1",
    positive="output",
    negative=circuit.gnd,
    vsense="Vsense",
    current_gain=5.0,
)
```

### CCVS (H) -- Current-Controlled Voltage Source

`H(*, name, positive, negative, vsense, transresistance)`

Output voltage = Rm * I(Vsense)

```python
circuit.V(
    name="sense",
    positive="a",
    negative=circuit.gnd,
    value=0.0,
)
circuit.H(
    name="1",
    positive="output",
    negative=circuit.gnd,
    vsense="Vsense",
    transresistance=1000.0,
)
```

## Semiconductor Devices

All semiconductor devices require a `.model` definition (see [Models](models.md)).

### Diode -- `D(*, name, anode, cathode, model)`

```python
circuit.model("1N4148", "D", IS=2.52e-9, RS=0.568, N=1.752, BV=100, IBV=100e-6)
circuit.D(
    name="1",
    anode="anode",
    cathode="cathode",
    model="1N4148",
)
```

Netlist output: `D1 anode cathode 1N4148`

### BJT -- `Q(*, name, collector, base, emitter, model)` or `BJT(...)`

```python
circuit.model("2N2222", "NPN", BF=200, IS=1e-14)
circuit.Q(
    name="1",
    collector="collector",
    base="base",
    emitter="emitter",
    model="2N2222",
)

# BJT() is an alias for Q()
circuit.BJT(
    name="2",
    collector="collector",
    base="base",
    emitter="emitter",
    model="2N2222",
)
```

Pin order: **Collector, Base, Emitter** (C, B, E).

### MOSFET -- `M(*, name, drain, gate, source, bulk, model)` or `MOSFET(...)`

```python
circuit.model("nch", "NMOS", LEVEL=1, VTO=0.4, KP=200e-6)
circuit.M(
    name="1",
    drain="drain",
    gate="gate",
    source="source",
    bulk="bulk",
    model="nch",
)

# MOSFET() is an alias for M()
circuit.MOSFET(
    name="2",
    drain="drain",
    gate="gate",
    source="source",
    bulk="bulk",
    model="nch",
)
```

Pin order: **Drain, Gate, Source, Bulk** (D, G, S, B).

For CMOS circuits, NMOS bulk typically connects to ground, PMOS bulk to VDD:

```python
circuit.model("nch", "NMOS", LEVEL=1, VTO=0.4, KP=200e-6)
circuit.model("pch", "PMOS", LEVEL=1, VTO=-0.4, KP=100e-6)

# CMOS inverter
circuit.MOSFET(
    name="n",
    drain="out",
    gate="in",
    source=circuit.gnd,
    bulk=circuit.gnd,
    model="nch",
)
circuit.MOSFET(
    name="p",
    drain="out",
    gate="in",
    source="vdd",
    bulk="vdd",
    model="pch",
)
```

### JFET -- `J(*, name, drain, gate, source, model)`

```python
circuit.model("2N5457", "NJF", VTO=-1.5, BETA=1.5e-3, LAMBDA=0.005)
circuit.J(
    name="1",
    drain="drain",
    gate="gate",
    source="source",
    model="2N5457",
)
```

Pin order: **Drain, Gate, Source** (D, G, S).

### MESFET -- `Z(*, name, drain, gate, source, model)`

```python
circuit.model("mesfet1", "NMF", VTO=-1.0)
circuit.Z(
    name="1",
    drain="drain",
    gate="gate",
    source="source",
    model="mesfet1",
)
```

## Switches

### Voltage-Controlled Switch -- `S(*, name, positive, negative, control_positive, control_negative, model)`

```python
circuit.model("sw1", "SW", VT=2.5, VH=0.5, RON=1, ROFF=1e6)
circuit.S(
    name="1",
    positive="out_p",
    negative="out_m",
    control_positive="ctrl_p",
    control_negative="ctrl_m",
    model="sw1",
)
```

### Current-Controlled Switch -- `W(*, name, positive, negative, vcontrol, model)`

```python
circuit.model("csw1", "CSW", IT=0.5, IH=0.1, RON=1, ROFF=1e6)
circuit.W(
    name="1",
    positive="out_p",
    negative="out_m",
    vcontrol="Vsense",
    model="csw1",
)
```

## Transmission Line -- `T(*, name, input_positive, input_negative, output_positive, output_negative, Z0, TD)`

Lossless transmission line with characteristic impedance and time delay:

```python
# 50-Ohm line with 1ns delay
circuit.T(
    name="1",
    input_positive="in_p",
    input_negative=circuit.gnd,
    output_positive="out_p",
    output_negative=circuit.gnd,
    Z0=50.0,
    TD=1e-9,
)
```

Netlist output: `T1 in_p 0 out_p 0 Z0=50 TD=0.000000001`

## Subcircuit Instance -- `X(name, subcircuit_name, *nodes)`

Instantiate a previously defined subcircuit (positional arguments):

```python
circuit.X("1", "opamp", "inp", "inm", "out", "vdd", "vss")
```

Netlist output: `X1 inp inm out vdd vss opamp`

See [Models and Subcircuits](models.md) for how to define subcircuits.

## XSPICE Digital Block -- `A(*, name, connections, model)`

```python
circuit.A(
    name="1",
    connections=["in1", "in2", "out"],
    model="and2",
)
```

## Verilog Integration -- `verilog(*, source, mode, instance_name, connections, ...)`

Embed digital Verilog modules into your circuit, either for co-simulation or gate-level synthesis.

### Simulation Mode (Co-simulation)

```python
circuit.verilog(
    source="""
        module counter(input clk, output reg [2:0] count);
            always @(posedge clk) count <= count + 1;
        endmodule
    """,
    mode="simulate",
    instance_name="cnt1",
    connections={"clk": "clk_net", "count": ["bit0", "bit1", "bit2"]},
)
```

Supported backends: ngspice (via iverilog), Spectre (via xrun/ncvlog).

### Synthesis Mode (Gate-level)

```python
circuit.verilog(
    source="""
        module counter(input clk, output reg [2:0] count);
            always @(posedge clk) count <= count + 1;
        endmodule
    """,
    mode="synthesize",
    instance_name="cnt1",
    connections={"clk": "clk_net", "count": ["bit0", "bit1", "bit2"]},
    pdk="sky130_fd_sc_hd",
)
```

Compiles Verilog to gate-level netlist via Yosys, maps to PDK standard cells. Works on all backends.

#### PDK Resolution

- `pdk="sky130_fd_sc_hd"` -- auto-resolves liberty and SPICE models via `$PDK_ROOT`
- `liberty="/explicit/path.lib"` -- explicit liberty file for Yosys
- `spice_models="/explicit/path.spice"` -- explicit cell SPICE models

#### From File

```python
circuit.verilog(
    source="counter.v",
    mode="simulate",
    instance_name="cnt1",
    connections={"clk": "clk_net", "count": ["bit0", "bit1", "bit2"]},
)
```

## Accessing Elements

You can look up elements by name:

```python
circuit.R(
    name="load",
    positive="out",
    negative=circuit.gnd,
    value=1e3,
)

# Access by name (returns the SPICE line as a string)
print(circuit["load"])    # "Rload out 0 1k"
print(circuit.element("load"))  # same thing
```

If the element doesn't exist, a `KeyError` is raised.

## Raw SPICE

For anything not covered by the API, inject raw SPICE lines:

```python
circuit.raw_spice(".options reltol=1e-6")
circuit.raw_spice(".global vdd")
```

These lines appear verbatim in the netlist before `.end`.

## Printing the Netlist

```python
# As a string
netlist_text = str(circuit)

# Print directly
print(circuit)

# Repr shows the title
repr(circuit)  # "Circuit('My Circuit Title')"
```
