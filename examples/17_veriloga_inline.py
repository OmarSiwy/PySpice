"""
Example 17: Inline Verilog-A Resistor Model

Defines a simple resistor in Verilog-A source code and compiles it
inline using circuit.veriloga(). The compiled OSDI module is loaded
and the custom model is instantiated as a standard component.

Requires 'openvaf' on $PATH for Verilog-A compilation.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm

# Verilog-A source for a parameterized resistor
VERILOGA_RESISTOR = r"""
`include "disciplines.vams"
module myres(a, b);
    inout a, b;
    electrical a, b;
    parameter real r = 1000.0;
    analog V(a,b) <+ r * I(a,b);
endmodule
"""

circuit = Circuit("Verilog-A Inline Resistor")

# Try to compile and load the Verilog-A model
try:
    osdi_path = circuit.veriloga(VERILOGA_RESISTOR)
    print(f"Compiled Verilog-A to: {osdi_path}")

    # DC voltage source
    circuit.V(
        name="in",
        positive="input",
        negative=circuit.gnd,
        value=5 @ u_V,
    )

    # Standard resistor for comparison
    circuit.R(
        name="std",
        positive="input",
        negative="mid",
        value=1 @ u_kOhm,
    )

    # Use raw_spice to instantiate the Verilog-A resistor model
    # The OSDI module defines "myres" with parameter "r"
    circuit.raw_spice("Nmyres1 mid 0 myres r=1000")

    # Print the SPICE netlist
    print("\n=== Netlist ===")
    print(circuit)

    # Expected: two 1k resistors in series = 2k total
    # I = 5V / 2kOhm = 2.5mA, V(mid) = 2.5V
    print("\nExpected: V(mid) = 2.5V (two 1k resistors in series)")

except RuntimeError as e:
    print(f"Note: {e}")
    print("\nVerilog-A compilation requires 'openvaf' on $PATH.")
    print("Install OpenVAF from: https://openvaf.semimod.de/")
    print("\nShowing the circuit without the Verilog-A model:")

    # Build the circuit without Verilog-A for demonstration
    circuit2 = Circuit("Verilog-A Demo (fallback)")

    circuit2.V(
        name="in",
        positive="input",
        negative=circuit2.gnd,
        value=5 @ u_V,
    )

    circuit2.R(
        name="1",
        positive="input",
        negative="output",
        value=1 @ u_kOhm,
    )

    circuit2.R(
        name="2",
        positive="output",
        negative=circuit2.gnd,
        value=1 @ u_kOhm,
    )

    print(circuit2)
