"""
Example 10: Subcircuit Definition and Instantiation

Defines a simple inverter subcircuit (using resistor + NMOS) and
instantiates it twice in a top-level circuit using X().
Demonstrates the Subcircuit class and subcircuit instantiation.
"""
from pyspice_rs import Circuit, Subcircuit
from pyspice_rs.unit import u_V, u_kOhm

# ---- Define the inverter subcircuit ----
inverter = Subcircuit(
    "inverter",
    ports=["vdd", "in", "out", "gnd"],
)

# NMOS model inside subcircuit
inverter.model(
    "NMOS_INV",
    "NMOS",
    LEVEL=1,
    VTO=0.7,
    KP=110e-6,
)

# Pull-up resistor from VDD to output
inverter.R(
    name="rup",
    positive="vdd",
    negative="out",
    value=10 @ u_kOhm,
)

# NMOS transistor: drain=out, gate=in, source=gnd, bulk=gnd
inverter.M(
    name="n1",
    drain="out",
    gate="in",
    source="gnd",
    bulk="gnd",
    model="NMOS_INV",
)

# ---- Top-level circuit ----
circuit = Circuit("Two Inverters in Series")

# Supply voltage
circuit.V(
    name="dd",
    positive="vdd",
    negative=circuit.gnd,
    value=3.3 @ u_V,
)

# Input signal
circuit.PulseVoltageSource(
    name="in",
    positive="a",
    negative=circuit.gnd,
    initial_value=0.0,
    pulsed_value=3.3,
    pulse_width=25e-9,
    period=50e-9,
    rise_time=1e-9,
    fall_time=1e-9,
)

# Add the subcircuit definition to the circuit via raw_spice
# (The subcircuit definition is emitted as part of the netlist)
circuit.raw_spice(str(inverter))

# First inverter instance: input -> mid
circuit.X(
    "inv1",
    "inverter",
    "vdd", "a", "mid", circuit.gnd,
)

# Second inverter instance: mid -> output (double inversion = buffer)
circuit.X(
    "inv2",
    "inverter",
    "vdd", "mid", "output", circuit.gnd,
)

# Load capacitor
circuit.C(
    name="load",
    positive="output",
    negative=circuit.gnd,
    value=10e-15,
)

# Print the SPICE netlist
print(circuit)

print("\nTwo inverters in series form a buffer:")
print("  Input A = 0V -> mid = VDD -> Output = 0V")
print("  Input A = VDD -> mid = 0V -> Output = VDD")
