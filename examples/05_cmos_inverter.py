"""
Example 05: CMOS Inverter

A complementary MOS inverter with NMOS and PMOS transistors.
VDD = 3.3V, pulse input for transient analysis.
Demonstrates MOSFET model definitions and PulseVoltageSource.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V

circuit = Circuit("CMOS Inverter")

# NMOS transistor model (simplified)
circuit.model(
    "NMOS_3V3",
    "NMOS",
    LEVEL=1,
    VTO=0.7,
    KP=110e-6,
    LAMBDA=0.04,
    TOX=9e-9,
    CGSO=0.06e-9,
    CGDO=0.06e-9,
)

# PMOS transistor model (simplified)
circuit.model(
    "PMOS_3V3",
    "PMOS",
    LEVEL=1,
    VTO=-0.7,
    KP=50e-6,
    LAMBDA=0.05,
    TOX=9e-9,
    CGSO=0.07e-9,
    CGDO=0.07e-9,
)

# Supply voltage: 3.3V
circuit.V(
    name="dd",
    positive="vdd",
    negative=circuit.gnd,
    value=3.3 @ u_V,
)

# Pulse input: 0V to 3.3V, 50ns period
circuit.PulseVoltageSource(
    name="in",
    positive="input",
    negative=circuit.gnd,
    initial_value=0.0,
    pulsed_value=3.3,
    pulse_width=25e-9,
    period=50e-9,
    rise_time=0.5e-9,
    fall_time=0.5e-9,
)

# PMOS: source=VDD, gate=input, drain=output, bulk=VDD
circuit.M(
    name="p1",
    drain="output",
    gate="input",
    source="vdd",
    bulk="vdd",
    model="PMOS_3V3",
)

# NMOS: drain=output, gate=input, source=GND, bulk=GND
circuit.M(
    name="n1",
    drain="output",
    gate="input",
    source=circuit.gnd,
    bulk=circuit.gnd,
    model="NMOS_3V3",
)

# Load capacitor (model interconnect/gate load)
circuit.C(
    name="load",
    positive="output",
    negative=circuit.gnd,
    value=50e-15,
)

# Print the SPICE netlist
print(circuit)

print("\nCMOS Inverter:")
print("  When Vin = 0V  -> PMOS ON,  NMOS OFF -> Vout = VDD = 3.3V")
print("  When Vin = VDD -> PMOS OFF, NMOS ON  -> Vout = GND = 0V")
print(f"  Switching threshold ~ VDD/2 = {3.3/2:.2f} V")
