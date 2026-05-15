# PySpice-rs API Documentation

Welcome to the PySpice-rs documentation. PySpice-rs is a Rust-powered Python library for building SPICE circuit netlists and running simulations. It gives you the power of a professional circuit simulator through a clean, Pythonic API.

## What is SPICE?

SPICE (Simulation Program with Integrated Circuit Emphasis) is the industry-standard tool for simulating electronic circuits. Engineers use it to verify that their circuit designs work correctly before building them physically. PySpice-rs lets you write SPICE simulations in Python instead of manually writing netlist text files.

## Quick Start

```python
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm

# Create a voltage divider circuit
circuit = Circuit("My First Circuit")
circuit.V(
    name="in",
    positive="input",
    negative=circuit.gnd,
    value=10 @ u_V,
)
circuit.R(
    name="1",
    positive="input",
    negative="output",
    value=2 @ u_kOhm,
)
circuit.R(
    name="2",
    positive="output",
    negative=circuit.gnd,
    value=1 @ u_kOhm,
)

# Print the SPICE netlist
print(circuit)

# Create a simulator and run an operating point analysis
sim = circuit.simulator()
result = sim.operating_point()
print(f"Output voltage: {result['output']:.3f} V")
```

Output:
```
.title My First Circuit
Vin input 0 10
R1 input output 2k
R2 output 0 1k
.end

Output voltage: 3.333 V
```

## Documentation Pages

| Page | What You'll Learn |
|------|-------------------|
| [Getting Started](getting-started.md) | Installation, first circuit, how netlists work |
| [Units](units.md) | The unit system (`u_V`, `u_kOhm`, `@` operator) |
| [Circuit Building](circuit.md) | All components: resistors, capacitors, transistors, sources |
| [Waveform Sources](waveforms.md) | Sinusoidal, pulse, and PWL signal sources |
| [Models and Subcircuits](models.md) | Device models, subcircuit definitions, `.include` |
| [Simulation](simulation.md) | Running analyses: DC, AC, transient, noise, and more |
| [Results](results.md) | Reading simulation output, accessing waveforms |
| [Linting](linting.md) | Checking netlists for errors before simulating |
| [Backends](backends.md) | Choosing between ngspice, Xyce, LTspice, Spectre, Vacask |

## Key Concepts

**Circuit** -- The main object. You create one, add components to it, then either print the netlist or run a simulation.

**Netlist** -- A text description of a circuit that SPICE simulators understand. PySpice-rs builds this for you.

**Simulator** -- Wraps a circuit with analysis configuration (what to simulate, what to save, temperature, etc.).

**Analysis** -- The type of simulation: DC operating point, AC frequency sweep, transient time-domain, etc.

**Backend** -- The actual SPICE engine that runs the simulation (ngspice, Xyce, LTspice, Spectre, or Vacask).
