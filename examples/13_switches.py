"""
Example 13: Voltage-Controlled and Current-Controlled Switches

Demonstrates:
  S — Voltage-controlled switch (on/off based on control voltage)
  W — Current-controlled switch (on/off based on sense current)

Each switch uses a switch model with ON and OFF resistance.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm

circuit = Circuit("Switches Demo")

# ---- Voltage-controlled switch model ----
circuit.model(
    "SW_VCTL",
    "SW",
    VT=2.5,
    VH=0.5,
    RON=1.0,
    ROFF=1e6,
)

# ---- Current-controlled switch model ----
circuit.model(
    "SW_ICTL",
    "CSW",
    IT=1e-3,
    IH=0.1e-3,
    RON=1.0,
    ROFF=1e6,
)

# Supply for the switched circuits
circuit.V(
    name="dd",
    positive="vdd",
    negative=circuit.gnd,
    value=5 @ u_V,
)

# ==== Section 1: Voltage-controlled switch ====

# Control voltage for S switch (ramp from 0V to 5V)
circuit.PulseVoltageSource(
    name="ctrl_v",
    positive="vctrl",
    negative=circuit.gnd,
    initial_value=0.0,
    pulsed_value=5.0,
    pulse_width=5e-3,
    period=10e-3,
    rise_time=1e-3,
    fall_time=1e-3,
)

# Voltage-controlled switch S
circuit.S(
    name="1",
    positive="vdd",
    negative="sw_v_out",
    control_positive="vctrl",
    control_negative=circuit.gnd,
    model="SW_VCTL",
)

# Load for voltage-controlled switch
circuit.R(
    name="load_v",
    positive="sw_v_out",
    negative=circuit.gnd,
    value=1 @ u_kOhm,
)

# ==== Section 2: Current-controlled switch ====

# Current sense voltage source (zero-volt source to measure current)
circuit.V(
    name="sense_i",
    positive="i_ctrl_in",
    negative="i_ctrl_out",
    value=0.0,
)

# Resistor to set the control current (5V / 1kOhm = 5mA when on)
circuit.R(
    name="ctrl_i",
    positive="vdd",
    negative="i_ctrl_in",
    value=1 @ u_kOhm,
)

# Dummy load on sense path
circuit.R(
    name="sense_gnd",
    positive="i_ctrl_out",
    negative=circuit.gnd,
    value=0.001,
)

# Current-controlled switch W
circuit.W(
    name="1",
    positive="vdd",
    negative="sw_i_out",
    vcontrol="Vsense_i",
    model="SW_ICTL",
)

# Load for current-controlled switch
circuit.R(
    name="load_i",
    positive="sw_i_out",
    negative=circuit.gnd,
    value=1 @ u_kOhm,
)

# Print the SPICE netlist
print(circuit)

print("\nSwitch behavior:")
print("  S (voltage-controlled): ON when V(ctrl) > VT + VH = 3.0V")
print("  W (current-controlled): ON when I(sense) > IT + IH = 1.1mA")
