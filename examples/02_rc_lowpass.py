"""
Example 02: RC Low-Pass Filter

First-order RC low-pass filter with sinusoidal input.
R = 1kOhm, C = 1uF
Break frequency f_c = 1 / (2 * pi * R * C) = 159.15 Hz
"""
import math
from pyspice_rs import Circuit
from pyspice_rs.unit import u_kOhm, u_uF, u_Hz

circuit = Circuit("RC Low-Pass Filter")

# Sinusoidal voltage source: 1V amplitude at 1kHz
circuit.SinusoidalVoltageSource(
    name="in",
    positive="input",
    negative=circuit.gnd,
    dc_offset=0.0,
    offset=0.0,
    amplitude=1.0,
    frequency=1000.0,
)

# Series resistor: 1kOhm
circuit.R(
    name="1",
    positive="input",
    negative="output",
    value=1 @ u_kOhm,
)

# Shunt capacitor: 1uF to ground
circuit.C(
    name="1",
    positive="output",
    negative=circuit.gnd,
    value=1 @ u_uF,
)

# Print the SPICE netlist
print(circuit)

# Expected -3dB break frequency
R = 1e3
C = 1e-6
f_c = 1.0 / (2.0 * math.pi * R * C)
print(f"\nExpected break frequency f_c = {f_c:.2f} Hz")
print(f"At f = 1 kHz, attenuation = {20 * math.log10(1 / math.sqrt(1 + (1000/f_c)**2)):.1f} dB")
