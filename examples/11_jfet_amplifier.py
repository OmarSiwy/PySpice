"""
Example 11: JFET Common-Source Amplifier

A common-source amplifier using a 2N5457 N-channel JFET.
Self-bias configuration with source resistor.
VDD = 15V, demonstrates the J (JFET) element.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm, u_uF

circuit = Circuit("JFET Common-Source Amplifier")

# 2N5457 JFET model
circuit.model(
    "2N5457",
    "NJF",
    VTO=-1.8,
    BETA=1.304e-3,
    LAMBDA=5.0e-3,
    IS=33.57e-15,
    RD=1.0,
    RS=1.0,
    CGS=2.0e-12,
    CGD=1.6e-12,
)

# Supply voltage: 15V
circuit.V(
    name="dd",
    positive="vdd",
    negative=circuit.gnd,
    value=15 @ u_V,
)

# AC input with coupling capacitor
circuit.SinusoidalVoltageSource(
    name="in",
    positive="sig_in",
    negative=circuit.gnd,
    dc_offset=0.0,
    offset=0.0,
    amplitude=0.05,
    frequency=10000.0,
)

# Input coupling capacitor
circuit.C(
    name="in",
    positive="sig_in",
    negative="gate",
    value=1 @ u_uF,
)

# Gate bias resistor to ground (gate current is ~zero for JFET)
circuit.R(
    name="g",
    positive="gate",
    negative=circuit.gnd,
    value=1000 @ u_kOhm,
)

# JFET: drain, gate, source
circuit.J(
    name="1",
    drain="drain",
    gate="gate",
    source="source",
    model="2N5457",
)

# Drain resistor
circuit.R(
    name="d",
    positive="vdd",
    negative="drain",
    value=3.3 @ u_kOhm,
)

# Source resistor (self-bias)
circuit.R(
    name="s",
    positive="source",
    negative=circuit.gnd,
    value=1 @ u_kOhm,
)

# Source bypass capacitor
circuit.C(
    name="s",
    positive="source",
    negative=circuit.gnd,
    value=100 @ u_uF,
)

# Output coupling capacitor
circuit.C(
    name="out",
    positive="drain",
    negative="output",
    value=1 @ u_uF,
)

# Load resistor
circuit.R(
    name="load",
    positive="output",
    negative=circuit.gnd,
    value=10 @ u_kOhm,
)

# Print the SPICE netlist
print(circuit)

# JFET self-bias operating point (approximate)
# With VGS ~ -1V (from source resistor), ID ~ BETA*(1 - VGS/VTO)^2
vgs = -1.0
vto = -1.8
beta = 1.304e-3
i_d = beta * (1 - vgs / vto) ** 2
v_drain = 15 - i_d * 3300
print(f"\nApproximate DC operating point:")
print(f"  VGS  ~ {vgs:.1f} V (self-bias)")
print(f"  ID   ~ {i_d * 1000:.2f} mA")
print(f"  Vd   ~ {v_drain:.2f} V")
print(f"  Av   ~ -gm * Rd (with bypass cap)")
