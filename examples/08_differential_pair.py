"""
Example 08: MOSFET Differential Pair

A MOSFET differential pair with:
- Two matched NMOS transistors
- Tail current source (ideal, 200uA)
- Resistive loads
- Differential input with small-signal offset

VDD = 3.3V, demonstrates the I (current source) element.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm, u_uA

circuit = Circuit("MOSFET Differential Pair")

# NMOS model
circuit.model(
    "NMOS_DIFF",
    "NMOS",
    LEVEL=1,
    VTO=0.7,
    KP=110e-6,
    LAMBDA=0.04,
    TOX=9e-9,
)

# Supply voltage: 3.3V
circuit.V(
    name="dd",
    positive="vdd",
    negative=circuit.gnd,
    value=3.3 @ u_V,
)

# Common-mode input bias
circuit.V(
    name="cm",
    positive="vcm",
    negative=circuit.gnd,
    value=1.65 @ u_V,
)

# Differential input: small positive offset on inp
circuit.V(
    name="diff",
    positive="inp",
    negative="vcm",
    value=0.01 @ u_V,
)

# Negative input: tied to common-mode
circuit.R(
    name="inn_tie",
    positive="inn",
    negative="vcm",
    value=0.001,
)

# Left MOSFET: M1
circuit.M(
    name="1",
    drain="out_p",
    gate="inp",
    source="tail",
    bulk=circuit.gnd,
    model="NMOS_DIFF",
)

# Right MOSFET: M2
circuit.M(
    name="2",
    drain="out_n",
    gate="inn",
    source="tail",
    bulk=circuit.gnd,
    model="NMOS_DIFF",
)

# Load resistors
circuit.R(
    name="d1",
    positive="vdd",
    negative="out_p",
    value=10 @ u_kOhm,
)

circuit.R(
    name="d2",
    positive="vdd",
    negative="out_n",
    value=10 @ u_kOhm,
)

# Tail current source: 200uA from tail node to ground
circuit.I(
    name="tail",
    positive="tail",
    negative=circuit.gnd,
    value=200 @ u_uA,
)

# Print the SPICE netlist
print(circuit)

# Expected behavior
i_tail = 200e-6
i_d = i_tail / 2  # each transistor carries half
rd = 10e3
v_out_cm = 3.3 - i_d * rd
print(f"\nDifferential pair operating point:")
print(f"  I_tail = {i_tail * 1e6:.0f} uA")
print(f"  I_D (each) = {i_d * 1e6:.0f} uA")
print(f"  V_out (common-mode) = {v_out_cm:.2f} V")
print(f"  Small-signal gain Av = gm * Rd")
