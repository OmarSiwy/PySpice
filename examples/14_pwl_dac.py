"""
Example 14: 3-bit DAC Staircase using PieceWiseLinearVoltageSource

Generates a staircase waveform with 8 voltage steps (0/8 to 7/8 of Vref)
using a PieceWiseLinearVoltageSource (PWL).
Each step lasts 1us, total period = 8us.
Vref = 3.3V.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_kOhm

circuit = Circuit("3-bit DAC Staircase")

# Generate PWL values: 8 steps, each 1us long
vref = 3.3
n_bits = 3
n_steps = 2 ** n_bits  # 8 steps
step_duration = 1e-6   # 1us per step

# Build time-voltage pairs
# Each step holds for step_duration, then transitions to next level
pwl_values = []
for i in range(n_steps):
    t_start = i * step_duration
    t_end = (i + 1) * step_duration - 1e-9  # hold until just before next step
    voltage = vref * i / n_steps
    pwl_values.append((t_start, voltage))
    pwl_values.append((t_end, voltage))

# Final point to close out the waveform
pwl_values.append((n_steps * step_duration, 0.0))

# PWL voltage source
circuit.PieceWiseLinearVoltageSource(
    name="dac",
    positive="dac_out",
    negative=circuit.gnd,
    values=pwl_values,
)

# Output buffer resistor
circuit.R(
    name="out",
    positive="dac_out",
    negative="buffered",
    value=0.1 @ u_kOhm,
)

# Load
circuit.R(
    name="load",
    positive="buffered",
    negative=circuit.gnd,
    value=10 @ u_kOhm,
)

# Print the SPICE netlist
print(circuit)

# Print the staircase levels
print(f"\n3-bit DAC staircase (Vref = {vref} V):")
print(f"  {'Code':>4}  {'Voltage':>8}")
for i in range(n_steps):
    v = vref * i / n_steps
    print(f"  {i:>4d}  {v:>8.4f} V")
print(f"\nLSB = {vref / n_steps:.4f} V")
