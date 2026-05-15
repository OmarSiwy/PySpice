"""
Example 07: Full-Bridge Diode Rectifier

A full-wave bridge rectifier with four diodes, sinusoidal AC input,
filter capacitor, and load resistor.
Demonstrates the D (diode) element with a diode model.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm, u_uF

circuit = Circuit("Full-Bridge Diode Rectifier")

# Diode model (1N4148)
circuit.model(
    "1N4148",
    "D",
    IS=2.52e-9,
    RS=0.568,
    N=1.752,
    BV=100,
    IBV=100e-6,
    CJO=4e-12,
    TT=20e-9,
)

# AC source: 10V peak at 60Hz
circuit.SinusoidalVoltageSource(
    name="ac",
    positive="ac_p",
    negative="ac_n",
    dc_offset=0.0,
    offset=0.0,
    amplitude=10.0,
    frequency=60.0,
)

# Bridge rectifier diodes:
# D1: ac_p -> out_p (positive half, forward path)
circuit.D(
    name="1",
    anode="ac_p",
    cathode="out_p",
    model="1N4148",
)

# D2: ac_n -> out_p (negative half, forward path)
circuit.D(
    name="2",
    anode="ac_n",
    cathode="out_p",
    model="1N4148",
)

# D3: gnd -> ac_p (positive half, return path)
circuit.D(
    name="3",
    anode=circuit.gnd,
    cathode="ac_p",
    model="1N4148",
)

# D4: gnd -> ac_n (negative half, return path)
circuit.D(
    name="4",
    anode=circuit.gnd,
    cathode="ac_n",
    model="1N4148",
)

# Filter capacitor: 100uF
circuit.C(
    name="filt",
    positive="out_p",
    negative=circuit.gnd,
    value=100 @ u_uF,
)

# Load resistor: 1kOhm
circuit.R(
    name="load",
    positive="out_p",
    negative=circuit.gnd,
    value=1 @ u_kOhm,
)

# Print the SPICE netlist
print(circuit)

# Expected DC output (approximate)
v_peak = 10.0
v_diode_drop = 0.7  # two diodes in series
v_dc = v_peak - 2 * v_diode_drop
print(f"\nFull-bridge rectifier:")
print(f"  V_peak(AC)   = {v_peak:.1f} V")
print(f"  Diode drops  = 2 x {v_diode_drop} V")
print(f"  V_dc(approx) = {v_dc:.1f} V")
