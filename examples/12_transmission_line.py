"""
Example 12: Lossless Transmission Line

A 50-ohm lossless transmission line between a source and load.
Demonstrates the T (transmission line) element with Z0 and TD parameters.
Line delay TD = 1ns, source impedance = 50 ohm, load = 100 ohm (mismatched).

A pulse input shows reflections due to impedance mismatch.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_Ohm

circuit = Circuit("Transmission Line Example")

# Pulse source
circuit.PulseVoltageSource(
    name="src",
    positive="vs",
    negative=circuit.gnd,
    initial_value=0.0,
    pulsed_value=1.0,
    pulse_width=5e-9,
    period=20e-9,
    rise_time=0.1e-9,
    fall_time=0.1e-9,
)

# Source impedance: 50 ohm
circuit.R(
    name="src",
    positive="vs",
    negative="in_p",
    value=50 @ u_Ohm,
)

# Lossless transmission line: Z0 = 50 ohm, delay = 1ns
circuit.T(
    name="line",
    input_positive="in_p",
    input_negative=circuit.gnd,
    output_positive="out_p",
    output_negative=circuit.gnd,
    Z0=50.0,
    TD=1e-9,
)

# Load resistor: 100 ohm (mismatched for reflections)
circuit.R(
    name="load",
    positive="out_p",
    negative=circuit.gnd,
    value=100 @ u_Ohm,
)

# Print the SPICE netlist
print(circuit)

# Reflection coefficient
z0 = 50.0
zl = 100.0
gamma = (zl - z0) / (zl + z0)
print(f"\nTransmission line parameters:")
print(f"  Z0 = {z0:.0f} Ohm")
print(f"  TD = 1 ns")
print(f"  Z_load = {zl:.0f} Ohm")
print(f"  Reflection coefficient = {gamma:.3f}")
print(f"  Round-trip delay = {2 * 1:.0f} ns")
