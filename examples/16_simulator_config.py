"""
Example 16: Simulator Configuration

Demonstrates all simulator configuration options:
  - temperature
  - options (abstol, reltol, etc.)
  - save (specific nodes/currents)
  - measure (measurement expressions)
  - step (parameter sweeps)
  - initial_condition (node voltages at t=0)
  - node_set (initial guess for DC operating point)

This example builds the circuit and simulator but does NOT run
a simulation -- it shows how to configure the simulator object.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm, u_uF

# Build a simple RC circuit
circuit = Circuit("Simulator Configuration Demo")

circuit.V(
    name="in",
    positive="input",
    negative=circuit.gnd,
    value=5 @ u_V,
)

circuit.R(
    name="1",
    positive="input",
    negative="output",
    value=1 @ u_kOhm,
)

circuit.C(
    name="1",
    positive="output",
    negative=circuit.gnd,
    value=1 @ u_uF,
)

circuit.R(
    name="load",
    positive="output",
    negative=circuit.gnd,
    value=10 @ u_kOhm,
)

print("=== Netlist ===")
print(circuit)

# Create a simulator instance
sim = circuit.simulator()

# 1. Set temperature
sim.temperature = 27.0
print("\n1. Temperature set to 27 C")

# 2. Set nominal temperature
sim.nominal_temperature = 25.0
print("2. Nominal temperature set to 25 C")

# 3. Simulator options
sim.options(
    RELTOL="1e-4",
    ABSTOL="1e-12",
    VNTOL="1e-6",
    GMIN="1e-12",
    ITL1="200",
)
print("3. Simulator options configured (RELTOL, ABSTOL, VNTOL, GMIN, ITL1)")

# 4. Save specific signals
sim.save("V(output)", "I(Vin)")
print("4. Save: V(output), I(Vin)")

# 5. Save all currents
sim.save_currents = True
print("5. Save all currents enabled")

# 6. Measure statements
sim.measure(
    "TRAN", "v_peak", "MAX", "V(output)"
)
print("6. Measure: peak voltage of V(output)")

# 7. Parameter step sweep
sim.step("R1", 500, 2000, 500)
print("7. Step: R1 from 500 to 2000 Ohm, step 500")

# 8. Initial conditions (for transient analysis)
sim.initial_condition(output=0.0)
print("8. Initial condition: V(output) = 0V")

# 9. Node set (DC operating point hint)
sim.node_set(output=2.5)
print("9. Node set: V(output) initial guess = 2.5V")

print("\nSimulator configured successfully.")
print("Call sim.transient(), sim.ac(), sim.dc(), or sim.operating_point() to run.")
