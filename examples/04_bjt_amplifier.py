"""
Example 04: Common-Emitter BJT Amplifier

A common-emitter amplifier with voltage divider biasing.
Uses a 2N2222 NPN transistor model.
Includes coupling capacitors for AC signal and bypass capacitor on emitter.
Vcc = 12V, designed for Ic ~ 1mA.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm, u_Ohm, u_uF

circuit = Circuit("Common-Emitter BJT Amplifier")

# 2N2222 NPN transistor model
circuit.model(
    "2N2222",
    "NPN",
    IS=14.34e-15,
    BF=255.9,
    VAF=74.03,
    RB=10.0,
    RC=1.0,
    CJE=22.01e-12,
    CJC=7.306e-12,
    TF=0.4111e-9,
)

# Supply voltage: 12V
circuit.V(
    name="cc",
    positive="vcc",
    negative=circuit.gnd,
    value=12 @ u_V,
)

# AC input signal via coupling capacitor
circuit.SinusoidalVoltageSource(
    name="in",
    positive="sig_in",
    negative=circuit.gnd,
    dc_offset=0.0,
    offset=0.0,
    amplitude=0.01,
    frequency=10000.0,
)

# Input coupling capacitor
circuit.C(
    name="in",
    positive="sig_in",
    negative="base",
    value=10 @ u_uF,
)

# Bias network: voltage divider
# R1 from Vcc to base
circuit.R(
    name="1",
    positive="vcc",
    negative="base",
    value=27 @ u_kOhm,
)

# R2 from base to ground
circuit.R(
    name="2",
    positive="base",
    negative=circuit.gnd,
    value=4.7 @ u_kOhm,
)

# BJT transistor Q1
circuit.Q(
    name="1",
    collector="collector",
    base="base",
    emitter="emitter",
    model="2N2222",
)

# Collector resistor
circuit.R(
    name="c",
    positive="vcc",
    negative="collector",
    value=4.7 @ u_kOhm,
)

# Emitter resistor
circuit.R(
    name="e",
    positive="emitter",
    negative=circuit.gnd,
    value=1 @ u_kOhm,
)

# Emitter bypass capacitor (AC ground for emitter)
circuit.C(
    name="e",
    positive="emitter",
    negative=circuit.gnd,
    value=100 @ u_uF,
)

# Output coupling capacitor
circuit.C(
    name="out",
    positive="collector",
    negative="output",
    value=10 @ u_uF,
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

# Approximate DC operating point
vb = 12 * 4700 / (27000 + 4700)
ve = vb - 0.7
ic = ve / 1000
vc = 12 - ic * 4700
print(f"\nApproximate DC operating point:")
print(f"  Vbase  = {vb:.2f} V")
print(f"  Ve     = {ve:.2f} V")
print(f"  Ic     = {ic * 1000:.2f} mA")
print(f"  Vc     = {vc:.2f} V")
print(f"  Av     ~ -{4700 / 1000:.1f} (with bypass cap)")
