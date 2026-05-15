"""
Example 03: RLC Bandpass Filter with Mutual Inductor (Transformer)

Two coupled inductors forming a transformer with a tuning capacitor.
L1 = 10uH, L2 = 10uH, K = 0.9 coupling, C = 100pF
Demonstrates the K (mutual inductor) element.
Resonant frequency f_0 = 1 / (2 * pi * sqrt(L * C))
"""
import math
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm, u_uH, u_pF

circuit = Circuit("RLC Bandpass with Transformer")

# AC source
circuit.SinusoidalVoltageSource(
    name="in",
    positive="input",
    negative=circuit.gnd,
    dc_offset=0.0,
    offset=0.0,
    amplitude=1.0,
    frequency=5e6,
)

# Source impedance
circuit.R(
    name="src",
    positive="input",
    negative="n1",
    value=50.0,
)

# Primary inductor: 10uH
circuit.L(
    name="1",
    positive="n1",
    negative=circuit.gnd,
    value=10 @ u_uH,
)

# Secondary inductor: 10uH
circuit.L(
    name="2",
    positive="n2",
    negative=circuit.gnd,
    value=10 @ u_uH,
)

# Mutual coupling between L1 and L2, K = 0.9
circuit.K(
    name="12",
    inductor1="L1",
    inductor2="L2",
    coupling=0.9,
)

# Tuning capacitor on secondary: 100pF
circuit.C(
    name="tune",
    positive="n2",
    negative=circuit.gnd,
    value=100 @ u_pF,
)

# Load resistor
circuit.R(
    name="load",
    positive="n2",
    negative=circuit.gnd,
    value=1 @ u_kOhm,
)

# Print the SPICE netlist
print(circuit)

# Expected resonant frequency of secondary LC tank
L = 10e-6
C = 100e-12
f_0 = 1.0 / (2.0 * math.pi * math.sqrt(L * C))
print(f"\nExpected resonant frequency f_0 = {f_0 / 1e6:.2f} MHz")
