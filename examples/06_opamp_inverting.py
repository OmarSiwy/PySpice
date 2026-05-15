"""
Example 06: Inverting Amplifier using Behavioral Voltage Source

An ideal opamp modeled as a behavioral voltage source (BV).
The BV implements: Vout = A * (V(inp) - V(inn)) with very high gain.
Configured as an inverting amplifier: Gain = -Rf / Rin = -10k / 1k = -10.

The BV expression references node voltages using V(node) syntax.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm

circuit = Circuit("Inverting Amplifier with Behavioral Opamp")

# DC input signal
circuit.V(
    name="in",
    positive="sig_in",
    negative=circuit.gnd,
    value=0.5 @ u_V,
)

# Input resistor: Rin = 1kOhm
circuit.R(
    name="in",
    positive="sig_in",
    negative="inn",
    value=1 @ u_kOhm,
)

# Feedback resistor: Rf = 10kOhm
circuit.R(
    name="f",
    positive="inn",
    negative="output",
    value=10 @ u_kOhm,
)

# Non-inverting input tied to ground (reference)
# Using a resistor to ground to establish the node
circuit.R(
    name="ref",
    positive="inp",
    negative=circuit.gnd,
    value=1 @ u_kOhm,
)

# Ideal opamp as behavioral voltage source:
# Vout = 1e6 * (V(inp) - V(inn))  [open-loop gain = 1e6]
# With feedback, closed-loop gain converges to -Rf/Rin = -10
circuit.BV(
    name="opamp",
    positive="output",
    negative=circuit.gnd,
    expression="1e6 * (V(inp) - V(inn))",
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

# Expected output
vin = 0.5
gain = -10.0  # -Rf/Rin
vout = vin * gain
print(f"\nInverting amplifier:")
print(f"  Vin  = {vin} V")
print(f"  Gain = -Rf/Rin = -{10000}/{1000} = {gain}")
print(f"  Expected Vout = {vout:.1f} V")
