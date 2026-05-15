"""
Example 01: Voltage Divider

A simple resistive voltage divider demonstrating basic circuit construction.
Vin = 10V, R1 = 2kOhm, R2 = 1kOhm
Vout = Vin * R2 / (R1 + R2) = 10 * 1k / (2k + 1k) = 3.333V
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm

circuit = Circuit("Voltage Divider")

# DC voltage source: 10V between input node and ground
circuit.V(
    name="in",
    positive="input",
    negative=circuit.gnd,
    value=10 @ u_V,
)

# Upper resistor: 2kOhm from input to output
circuit.R(
    name="1",
    positive="input",
    negative="output",
    value=2 @ u_kOhm,
)

# Lower resistor: 1kOhm from output to ground
circuit.R(
    name="2",
    positive="output",
    negative=circuit.gnd,
    value=1 @ u_kOhm,
)

# Print the SPICE netlist
print(circuit)

# Expected output voltage
r1 = 2000
r2 = 1000
vin = 10
vout = vin * r2 / (r1 + r2)
print(f"\nExpected Vout = {vout:.3f} V")
