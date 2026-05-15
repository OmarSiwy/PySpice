# Waveform Sources

Time-varying voltage and current sources let you drive circuits with realistic signals. PySpice-rs provides three waveform types: sinusoidal, pulse, and piecewise-linear (PWL).

## Sinusoidal Voltage Source

`SinusoidalVoltageSource(*, name, positive, negative, dc_offset=0.0, offset=0.0, amplitude=1.0, frequency=1000.0)`

Generates a sine wave: `V(t) = offset + amplitude * sin(2*pi*frequency*t)`

```python
# 1kHz sine wave, 1V amplitude, no DC offset
circuit.SinusoidalVoltageSource(
    name="in",
    positive="input",
    negative=circuit.gnd,
    dc_offset=0.0,
    offset=0.0,
    amplitude=1.0,
    frequency=1000.0,
)
```

Parameters:
- `name` -- the component name (becomes `Vin` in the netlist)
- `positive` -- positive terminal node
- `negative` -- negative terminal node
- `dc_offset` -- DC bias for operating point analysis (default: 0)
- `offset` -- DC offset added to the sine wave (default: 0)
- `amplitude` -- peak amplitude in Volts (default: 1.0)
- `frequency` -- frequency in Hertz (default: 1000.0)

Netlist output: `Vin input 0 0 SIN(0 1 1000 0 0 0)`

### Example: Audio signal generator

```python
# 440Hz "A" note, 100mV amplitude
circuit.SinusoidalVoltageSource(
    name="audio",
    positive="speaker_p",
    negative="speaker_m",
    dc_offset=0.0,
    offset=0.0,
    amplitude=0.1,
    frequency=440.0,
)
```

## Sinusoidal Current Source

`SinusoidalCurrentSource(*, name, positive, negative, dc_offset=0.0, offset=0.0, amplitude=1.0, frequency=1000.0)`

Same parameters as voltage, but produces current:

```python
circuit.SinusoidalCurrentSource(
    name="sig",
    positive=circuit.gnd,
    negative="input",
    dc_offset=0.0,
    offset=0.0,
    amplitude=1e-3,
    frequency=1e6,
)
```

## Pulse Voltage Source

`PulseVoltageSource(*, name, positive, negative, initial_value=0.0, pulsed_value=1.0, pulse_width=50e-9, period=100e-9, rise_time=1e-9, fall_time=1e-9)`

Generates a periodic rectangular pulse (clock, digital signal, etc.).

```
         pulsed_value
              ┌────────────┐
              │            │
              │  pw        │
   rise ──►  /              \  ◄── fall
            /                \
   ────────┘                  └────────
   initial_value
   |◄──────── period ────────────────►|
```

```python
# 100MHz clock: 0V to 1.8V, 50% duty cycle
circuit.PulseVoltageSource(
    name="clk",
    positive="clk",
    negative=circuit.gnd,
    initial_value=0.0,
    pulsed_value=1.8,
    pulse_width=5e-9,
    period=10e-9,
    rise_time=0.1e-9,
    fall_time=0.1e-9,
)
```

Parameters:
- `name` -- the component name
- `positive` -- positive terminal node
- `negative` -- negative terminal node
- `initial_value` -- voltage before the first pulse (default: 0)
- `pulsed_value` -- voltage during the pulse (default: 1.0)
- `pulse_width` -- duration of the high state (default: 50ns)
- `period` -- time between pulse starts (default: 100ns)
- `rise_time` -- transition time low-to-high (default: 1ns)
- `fall_time` -- transition time high-to-low (default: 1ns)

### Example: Reset signal

```python
# Active-low reset: starts at 0V, goes to 3.3V after 100ns
circuit.PulseVoltageSource(
    name="rst",
    positive="reset_n",
    negative=circuit.gnd,
    initial_value=0.0,
    pulsed_value=3.3,
    pulse_width=1.0,
    period=2.0,
    rise_time=1e-9,
    fall_time=1e-9,
)
```

## Pulse Current Source

`PulseCurrentSource(*, name, positive, negative, initial_value=0.0, pulsed_value=1.0, pulse_width=50e-9, period=100e-9, rise_time=1e-9, fall_time=1e-9)`

Same parameters as PulseVoltageSource, but produces current:

```python
circuit.PulseCurrentSource(
    name="stim",
    positive=circuit.gnd,
    negative="input",
    initial_value=0.0,
    pulsed_value=1e-3,
    pulse_width=1e-6,
    period=2e-6,
    rise_time=10e-9,
    fall_time=10e-9,
)
```

## Piecewise Linear (PWL) Voltage Source

`PieceWiseLinearVoltageSource(*, name, positive, negative, values)`

Define an arbitrary waveform as a list of `(time, voltage)` pairs. The simulator linearly interpolates between points.

```python
# Triangle wave: 0V at t=0, ramp to 5V at t=1ms, back to 0V at t=2ms
circuit.PieceWiseLinearVoltageSource(
    name="ramp",
    positive="ramp",
    negative=circuit.gnd,
    values=[
        (0.0,    0.0),
        (1e-3,   5.0),
        (2e-3,   0.0),
    ],
)
```

### Example: DAC staircase

```python
# 3-bit DAC output: 8 steps from 0 to 3.3V
steps = []
for code in range(8):
    t = code * 1e-6
    voltage = code * 3.3 / 7.0
    steps.append((t, voltage))
    steps.append((t + 0.999e-6, voltage))  # hold until next step

circuit.PieceWiseLinearVoltageSource(
    name="dac",
    positive="dac_out",
    negative=circuit.gnd,
    values=steps,
)
```

### Example: Custom stimulus from data

```python
# Load waveform from measurements
import csv

times = []
voltages = []
# ... read your data ...

circuit.PieceWiseLinearVoltageSource(
    name="meas",
    positive="stimulus",
    negative=circuit.gnd,
    values=list(zip(times, voltages)),
)
```

## Choosing the Right Source

| Use case | Source type |
|----------|-----------|
| AC analysis (Bode plot) | `SinusoidalVoltageSource` or plain `V` with AC magnitude |
| Clock signal | `PulseVoltageSource` |
| Digital stimulus | `PulseVoltageSource` |
| Arbitrary waveform | `PieceWiseLinearVoltageSource` |
| Ramp/triangle | `PieceWiseLinearVoltageSource` |
| Constant bias | `V` (DC source) |
| Current stimulus | `SinusoidalCurrentSource` or `PulseCurrentSource` |
