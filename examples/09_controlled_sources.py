"""
Example 09: All Four Controlled Source Types

Demonstrates each linear controlled source in a single circuit:
  E — Voltage-Controlled Voltage Source (VCVS)
  G — Voltage-Controlled Current Source (VCCS)
  F — Current-Controlled Current Source (CCCS)
  H — Current-Controlled Voltage Source (CCVS)

Each controlled source is driven by the same input and produces
its output on a separate node for clarity.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm

circuit = Circuit("Controlled Sources Demo")

# Common input voltage source
circuit.V(
    name="in",
    positive="input",
    negative=circuit.gnd,
    value=1 @ u_V,
)

# Sense resistor for current-controlled sources
# Current through Vsense is used by F and H
circuit.V(
    name="sense",
    positive="input",
    negative="isense",
    value=0.0,
)

# Load on sense path so current flows
circuit.R(
    name="sense_load",
    positive="isense",
    negative=circuit.gnd,
    value=1 @ u_kOhm,
)

# ---- E: Voltage-Controlled Voltage Source (VCVS) ----
# Output voltage = voltage_gain * V(input, gnd)
circuit.E(
    name="1",
    positive="out_vcvs",
    negative=circuit.gnd,
    control_positive="input",
    control_negative=circuit.gnd,
    voltage_gain=5.0,
)

circuit.R(
    name="e_load",
    positive="out_vcvs",
    negative=circuit.gnd,
    value=10 @ u_kOhm,
)

# ---- G: Voltage-Controlled Current Source (VCCS) ----
# Output current = transconductance * V(input, gnd)
circuit.G(
    name="1",
    positive="out_vccs",
    negative=circuit.gnd,
    control_positive="input",
    control_negative=circuit.gnd,
    transconductance=1e-3,
)

circuit.R(
    name="g_load",
    positive="out_vccs",
    negative=circuit.gnd,
    value=10 @ u_kOhm,
)

# ---- F: Current-Controlled Current Source (CCCS) ----
# Output current = current_gain * I(Vsense)
circuit.F(
    name="1",
    positive="out_cccs",
    negative=circuit.gnd,
    vsense="Vsense",
    current_gain=3.0,
)

circuit.R(
    name="f_load",
    positive="out_cccs",
    negative=circuit.gnd,
    value=10 @ u_kOhm,
)

# ---- H: Current-Controlled Voltage Source (CCVS) ----
# Output voltage = transresistance * I(Vsense)
circuit.H(
    name="1",
    positive="out_ccvs",
    negative=circuit.gnd,
    vsense="Vsense",
    transresistance=2000.0,
)

circuit.R(
    name="h_load",
    positive="out_ccvs",
    negative=circuit.gnd,
    value=10 @ u_kOhm,
)

# Print the SPICE netlist
print(circuit)

# Expected outputs
vin = 1.0
i_sense = vin / 1000  # 1mA through 1kOhm sense load
print(f"\nControlled source outputs (Vin = {vin} V, I_sense = {i_sense*1000:.1f} mA):")
print(f"  E (VCVS): Vout = {5.0 * vin:.1f} V  (gain = 5)")
print(f"  G (VCCS): Iout = {1e-3 * vin * 1000:.1f} mA, Vout = {1e-3 * vin * 10e3:.1f} V")
print(f"  F (CCCS): Iout = {3.0 * i_sense * 1000:.1f} mA, Vout = {3.0 * i_sense * 10e3:.1f} V")
print(f"  H (CCVS): Vout = {2000.0 * i_sense:.1f} V  (transresistance = 2 kOhm)")
