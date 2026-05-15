"""
Example 18: Digital Verilog Co-simulation

Demonstrates how to set up a mixed-signal simulation with a digital
Verilog module using ngspice's d_cosim XSPICE bridge.

The digital side is a simple 4-bit counter in Verilog. The XSPICE
A-element connects the digital and analog domains.

NOTE: This requires ngspice compiled with XSPICE and Verilog
co-simulation support, plus 'iverilog' on $PATH.
Not all installations support this. If unavailable, the example
prints the netlist structure for reference.
"""
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V

# Inline Verilog source for a simple 4-bit counter
VERILOG_COUNTER = """\
module counter(clk, rst, count);
    input clk, rst;
    output [3:0] count;
    reg [3:0] count;

    always @(posedge clk or posedge rst) begin
        if (rst)
            count <= 4'b0000;
        else
            count <= count + 1;
    end
endmodule
"""

circuit = Circuit("Digital Verilog Co-simulation")

# Supply voltage
circuit.V(
    name="dd",
    positive="vdd",
    negative=circuit.gnd,
    value=3.3 @ u_V,
)

# Clock signal: 100 MHz square wave
circuit.PulseVoltageSource(
    name="clk",
    positive="clk",
    negative=circuit.gnd,
    initial_value=0.0,
    pulsed_value=3.3,
    pulse_width=5e-9,
    period=10e-9,
    rise_time=0.1e-9,
    fall_time=0.1e-9,
)

# Reset pulse: high for first 5ns, then low
circuit.PulseVoltageSource(
    name="rst",
    positive="rst",
    negative=circuit.gnd,
    initial_value=3.3,
    pulsed_value=0.0,
    pulse_width=1.0,
    period=2.0,
    rise_time=0.1e-9,
    fall_time=0.1e-9,
)

# XSPICE A-element for digital-to-analog bridge
# This connects the analog clock/reset signals to digital domain
# and the digital counter output back to analog nodes.
#
# In a real ngspice setup, you would use:
#   .model d_cosim_model d_cosim(delay=1n)
#   A_counter [clk rst] [count0 count1 count2 count3] d_cosim_model
#
# Here we demonstrate the XSPICE A-element syntax:
circuit.model(
    "adc_bridge_model",
    "adc_bridge",
    in_low=0.8,
    in_high=2.0,
)

circuit.model(
    "dac_bridge_model",
    "dac_bridge",
    out_low=0.0,
    out_high=3.3,
)

# ADC bridge: convert analog clock and reset to digital
circuit.A(
    name="adc1",
    connections=["[clk rst]", "[dclk drst]"],
    model="adc_bridge_model",
)

# The digital counter would be connected via d_cosim or d_process
# For demonstration, we show the raw SPICE for the cosim bridge:
circuit.raw_spice("* Digital counter module (requires iverilog + ngspice XSPICE)")
circuit.raw_spice("* .model counter_model d_cosim(delay=0.1n)")
circuit.raw_spice("* A_counter [dclk drst] [dcount0 dcount1 dcount2 dcount3] counter_model")

# DAC bridge: convert digital counter output back to analog
circuit.A(
    name="dac1",
    connections=["[dcount0 dcount1 dcount2 dcount3]", "[acount0 acount1 acount2 acount3]"],
    model="dac_bridge_model",
)

# Load resistors on analog outputs
for i in range(4):
    circuit.R(
        name=f"out{i}",
        positive=f"acount{i}",
        negative=circuit.gnd,
        value=10e3,
    )

# Print the SPICE netlist
print("=== Netlist ===")
print(circuit)

print("\n=== Verilog Module Source ===")
print(VERILOG_COUNTER)

print("NOTE: Full digital co-simulation requires:")
print("  1. ngspice compiled with XSPICE support")
print("  2. iverilog (Icarus Verilog) on $PATH")
print("  3. The d_cosim XSPICE model for Verilog interface")
print("\nThe netlist above shows the structure. To run:")
print("  - Compile the Verilog: iverilog -o counter.vvp counter.v")
print("  - Uncomment the d_cosim lines in the netlist")
print("  - Run with ngspice")
