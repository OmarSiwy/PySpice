# Getting Started

This guide walks you through installing PySpice-rs and building your first circuit.

## Installation

PySpice-rs is built with [maturin](https://www.maturin.rs/), a tool that compiles Rust code into a Python package.

### Using the Nix development shell (recommended)

```bash
# Enter the development environment (includes Rust, Python, ngspice, etc.)
nix develop

# Create a virtual environment and install
python3 -m venv .venv
source .venv/bin/activate
pip install numpy pytest
maturin develop
```

### Manual setup

```bash
# Prerequisites: Rust toolchain, Python 3.10+, ngspice
pip install maturin numpy

# Build and install in development mode
maturin develop
```

### Verify the installation

```python
import pyspice_rs
print("PySpice-rs is ready!")
```

## Your First Circuit: A Voltage Divider

A voltage divider is one of the simplest circuits. Two resistors split a voltage proportionally.

```
       Vin = 10V
        +
        |
       [R1 = 2kOhm]
        |
        +--- Vout    <-- This is what we want to find
        |
       [R2 = 1kOhm]
        |
       GND
```

The output voltage is: `Vout = Vin * R2 / (R1 + R2) = 10 * 1000 / 3000 = 3.33V`

### Step 1: Import the library

```python
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm
```

- `Circuit` is the main class for building netlists
- `u_V` and `u_kOhm` are unit constants (Volts and kilo-Ohms)

### Step 2: Create a circuit

```python
circuit = Circuit("Voltage Divider")
```

Every circuit needs a title. This becomes the `.title` line in the SPICE netlist.

### Step 3: Add components

```python
# Voltage source: 10V between "input" node and ground
circuit.V(
    name="in",
    positive="input",
    negative=circuit.gnd,
    value=10 @ u_V,
)

# R1: 2kOhm between "input" and "output"
circuit.R(
    name="1",
    positive="input",
    negative="output",
    value=2 @ u_kOhm,
)

# R2: 1kOhm between "output" and ground
circuit.R(
    name="2",
    positive="output",
    negative=circuit.gnd,
    value=1 @ u_kOhm,
)
```

Let's break down the voltage source call:
- `name="in"` -- the component name (becomes `Vin` in the netlist)
- `positive="input"` -- the positive terminal node
- `negative=circuit.gnd` -- the negative terminal (ground, which is node `0`)
- `value=10 @ u_V` -- the value: 10 Volts

The `@` operator attaches a unit to a number. `10 @ u_V` means "10 Volts".

### Step 4: Print the netlist

```python
print(circuit)
```

Output:
```spice
.title Voltage Divider
Vin input 0 10
R1 input output 2k
R2 output 0 1k
.end
```

This is a valid SPICE netlist. You could paste it into any SPICE simulator and it would work.

### Step 5: Simulate

```python
sim = circuit.simulator()
result = sim.operating_point()
print(f"Output voltage: {result['output']:.3f} V")
```

Output:
```
Output voltage: 3.333 V
```

## Understanding Nodes

Nodes are the connection points between components. Think of them as the wires in your circuit.

- You name nodes with strings: `"input"`, `"output"`, `"vdd"`, etc.
- Ground is special: use `circuit.gnd` (which is node `"0"`)
- Two components sharing a node name are electrically connected

```python
# These two resistors are connected at "middle" node
circuit.R(
    name="1",
    positive="input",
    negative="middle",
    value=1e3,
)
circuit.R(
    name="2",
    positive="middle",
    negative=circuit.gnd,
    value=1e3,
)
```

## Understanding Component Names

Every component needs a unique name (the `name=` keyword argument). SPICE prepends a letter prefix:

| Method | Prefix | Example call | Netlist output |
|--------|--------|--------------|----------------|
| `R()` | R | `R(name="load", ...)` | `Rload` |
| `C()` | C | `C(name="1", ...)` | `C1` |
| `V()` | V | `V(name="dd", ...)` | `Vdd` |
| `M()` | M | `M(name="1", ...)` | `M1` |

Names must be unique within their type. You can have `R1` and `C1` in the same circuit, but not two `R1`s.

## Using Values Without Units

You don't have to use units. Plain numbers work too:

```python
circuit.R(name="1", positive="a", negative="b", value=1000.0)    # 1000 Ohms
circuit.C(name="1", positive="a", negative="b", value=1e-12)     # 1 picofarad
circuit.V(name="in", positive="a", negative="b", value=3.3)      # 3.3 Volts
```

PySpice-rs automatically formats these with SI prefixes in the netlist:
```
R1 a b 1k
C1 a b 1p
Vin a b 3.3
```

But units make your code more readable and self-documenting:

```python
circuit.R(name="1", positive="a", negative="b", value=1 @ u_kOhm)   # clearly 1 kilo-Ohm
circuit.C(name="1", positive="a", negative="b", value=1 @ u_pF)      # clearly 1 picofarad
circuit.V(name="in", positive="a", negative="b", value=3.3 @ u_V)    # clearly 3.3 Volts
```

## Next Steps

- Learn about all available [units](units.md)
- See every component type in [Circuit Building](circuit.md)
- Add time-varying signals with [Waveform Sources](waveforms.md)
- Run simulations in [Simulation](simulation.md)
