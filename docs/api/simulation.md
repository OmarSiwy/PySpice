# Simulation

Once you've built a circuit, create a simulator to run analyses. The simulator generates a complete netlist with analysis commands and sends it to a SPICE backend.

## Creating a Simulator

```python
sim = circuit.simulator()                    # auto-detect backend
sim = circuit.simulator(simulator="ngspice") # force specific backend
```

## Configuring the Simulator

Before running an analysis, you can configure various simulation options.

### Temperature

```python
sim.temperature = 27.0           # simulation temperature in Celsius
sim.nominal_temperature = 27.0   # model reference temperature
```

### Options

SPICE solver options control accuracy and convergence:

```python
sim.options(RELTOL="1e-4", ABSTOL="1e-12")
sim.options(METHOD="gear")       # integration method
```

### Saving Signals

By default, all node voltages are saved. You can restrict this:

```python
sim.save("V(out)", "V(in)")      # save only these signals
sim.save_currents = True         # also save all branch currents
```

### Initial Conditions

Set initial node voltages (used with `use_initial_condition=True` in transient):

```python
sim.initial_condition(out=2.5, cap_top=0.0)
```

### Node Sets

Provide convergence hints (the simulator uses these as starting guesses, not hard constraints):

```python
sim.node_set(out=1.65, bias=0.7)
```

### Measurements

Add `.meas` directives to automatically extract values:

```python
sim.measure("tran", "trise",
            "TRIG", "V(out)", "VAL=0.5", "RISE=1",
            "TARG", "V(out)", "VAL=4.5", "RISE=1")
```

After simulation, access results via the `.measures` property on the analysis result.

### Parameter Stepping

Sweep a parameter across multiple values:

```python
# Sweep R1 from 500 to 2000 in steps of 500
sim.step("R1", 500, 2000, 500)

# With explicit sweep type
sim.step_sweep("C1", 0.1e-6, 10e-6, 1e-6, "lin")
```

## Analysis Types

### Operating Point -- `.operating_point()`

Finds the DC steady-state of the circuit. All capacitors are open, all inductors are shorted.

```python
op = sim.operating_point()

# Access node voltages by name
print(op["output"])       # voltage at node "output"
print(op["vdd"])          # voltage at node "vdd"
```

**When to use:** Find DC bias points, verify power supply voltages, check transistor operating regions.

### DC Sweep -- `.dc(**kwargs)`

Sweep one or more source values and record the DC solution at each point.

```python
# Sweep Vinput from -2V to 5V in 0.01V steps
dc = sim.dc(Vinput=slice(-2, 5, 0.01))

# Access results
sweep_values = dc.sweep         # the swept variable values
output_data = dc["output"]      # output node voltage at each sweep point
```

The `slice(start, stop, step)` syntax defines the sweep range. The key name must match a voltage or current source in your circuit.

**Nested sweeps** (two variables):

```python
dc = sim.dc(Vgs=slice(0, 1.8, 0.01), Vds=slice(0, 1.8, 0.1))
```

**When to use:** I-V curves, transfer characteristics, finding threshold voltages.

### AC Analysis -- `.ac(variation, number_of_points, start_frequency, stop_frequency)`

Small-signal frequency-domain analysis. Produces magnitude and phase vs. frequency (Bode plot data).

```python
ac = sim.ac(
    variation="dec",            # logarithmic spacing ("dec", "oct", or "lin")
    number_of_points=100,       # points per decade
    start_frequency=1.0,        # 1 Hz
    stop_frequency=1e9          # 1 GHz
)

frequencies = ac.frequency      # frequency points
gain = ac["output"]             # complex gain at output node
```

**When to use:** Frequency response, filter design, amplifier bandwidth, stability analysis.

### Transient Analysis -- `.transient(step_time, end_time, ...)`

Time-domain simulation. This is the most intuitive analysis -- it shows how voltages and currents evolve over time.

```python
tran = sim.transient(
    step_time=1e-9,             # maximum time step (1ns)
    end_time=100e-9,            # stop time (100ns)
    start_time=None,            # start recording from t=0 (default)
    max_time=None,              # no maximum internal step constraint
    use_initial_condition=False # don't use .ic values
)

time = tran.time                # time points
vout = tran["output"]           # output voltage vs time
```

**With initial conditions:**

```python
sim.initial_condition(cap=2.5)
tran = sim.transient(1e-9, 100e-9, use_initial_condition=True)
```

**When to use:** Oscillators, digital circuits, switching power supplies, anything time-dependent.

### Noise Analysis -- `.noise(output_node, ref_node, src, ...)`

Calculates noise spectral density referred to an output node.

```python
noise = sim.noise(
    output_node="output",
    ref_node="0",               # reference (usually ground)
    src="Vin",                  # input source name
    variation="dec",
    points=10,
    start_frequency=1e3,
    stop_frequency=1e8,
    points_per_summary=None     # optional summary interval
)
```

**When to use:** Amplifier noise figure, noise-sensitive analog design.

### Transfer Function -- `.transfer_function(outvar, insrc)` or `.tf(...)`

Finds the DC small-signal transfer function, input resistance, and output resistance.

```python
tf = sim.transfer_function("V(output)", "Vin")
# or equivalently:
tf = sim.tf("V(output)", "Vin")
```

**When to use:** Quick gain and impedance calculation without a full AC sweep.

### DC Sensitivity -- `.dc_sensitivity(output_variable)`

Calculates the sensitivity of a DC output to each component value.

```python
sens = sim.dc_sensitivity("V(output)")
```

**When to use:** Identifying which components most affect your output -- useful for tolerance analysis.

### AC Sensitivity -- `.ac_sensitivity(output_variable, variation, ...)`

Frequency-dependent sensitivity analysis:

```python
sens = sim.ac_sensitivity("V(output)", "dec", 10, 100.0, 1e5)
```

### Pole-Zero Analysis -- `.polezero(node1, node2, node3, node4, tf_type, pz_type)`

Finds poles and zeros of a transfer function:

```python
pz = sim.polezero("input", "0", "output", "0", "vol", "pz")
```

- `tf_type`: `"vol"` (voltage) or `"cur"` (current)
- `pz_type`: `"pol"` (poles only), `"zer"` (zeros only), or `"pz"` (both)

**When to use:** Stability analysis, understanding frequency behavior from a control theory perspective.

### Distortion Analysis -- `.distortion(variation, points, start_frequency, stop_frequency, ...)`

Harmonic and intermodulation distortion:

```python
disto = sim.distortion("dec", 10, 100.0, 1e8)
```

### Fourier Analysis -- `.fourier(fundamental_frequency, output_variables, ...)`

Internally runs a transient simulation, then performs FFT to extract harmonic content:

```python
tran = sim.fourier(1e3, ["V(output)"], num_harmonics=10)
```

## Advanced Analysis Types

These are available depending on your backend.

### Periodic Steady State (PSS) -- `.pss(...)`

For circuits with periodic behavior (oscillators, mixers):

```python
pss = sim.pss(
    fundamental_frequency=1e9,
    stabilization_time=10e-9,
    observe_node="output",
    points_per_period=128,
    harmonics=10
)
```

### S-Parameters -- `.s_param(...)` and `.network_params(...)`

For RF/microwave network analysis:

```python
sp = sim.s_param("dec", 100, 1e6, 10e9)

# Or using LTspice .NET syntax:
sp = sim.network_params("I(R1)", "Vin", z_in=50.0, z_out=50.0,
                         variation="dec", points=100,
                         start_freq=1e3, stop_freq=1e9)
```

### Harmonic Balance -- `.harmonic_balance(...)`

For nonlinear RF circuits (Xyce, Vacask, Spectre):

```python
hb = sim.harmonic_balance(
    fundamental_frequencies=[1e9],
    num_harmonics=[7]
)
```

### Stability Analysis -- `.stability(...)`

Loop gain analysis:

```python
stab = sim.stability("probe_net", "dec", 100, 1.0, 1e10)
```

## Accessing Results

All analysis results support dictionary-style access:

```python
result = sim.operating_point()
voltage = result["node_name"]       # by subscript
voltage = result.node_name          # by attribute (same thing)
```

For swept analyses (DC, AC, transient), results are arrays:

```python
tran = sim.transient(1e-9, 100e-9)
time_array = tran.time              # list of time points
voltage_array = tran["output"]      # list of voltages at each time point
```

### Measurement Results

If you defined `.meas` directives, access them via `.measures`:

```python
sim.measure("tran", "vmax", "MAX", "V(out)")
tran = sim.transient(1e-9, 100e-9)
print(tran.measures)    # {"vmax": 4.95}
```

## Available Backends

Check which simulators are installed on your system:

```python
from pyspice_rs import CircuitSimulator
print(CircuitSimulator.available_backends())
# e.g. ["ngspice", "xyce", "ltspice"]
```

## Complete Example: RC Filter Analysis

```python
from pyspice_rs import Circuit
from pyspice_rs.unit import u_V, u_kOhm, u_uF
import math

# Build circuit
circuit = Circuit("RC Low-Pass Filter")
circuit.SinusoidalVoltageSource(
    name="in",
    positive="in",
    negative=circuit.gnd,
    amplitude=1.0,
    frequency=1000.0,
)
circuit.R(
    name="1",
    positive="in",
    negative="out",
    value=1e3,
)
circuit.C(
    name="1",
    positive="out",
    negative=circuit.gnd,
    value=1e-6,
)

# Calculate expected break frequency
fc = 1 / (2 * math.pi * 1e3 * 1e-6)
print(f"Expected -3dB frequency: {fc:.1f} Hz")

# Run AC analysis
sim = circuit.simulator()
ac = sim.ac("dec", 100, 1.0, 1e6)
print(f"Number of frequency points: {len(ac.frequency)}")

# Run transient analysis
tran = sim.transient(1e-6, 5e-3)
print(f"Number of time points: {len(tran.time)}")
```
