# Units

PySpice-rs has a built-in unit system that makes your circuit descriptions clear, correct, and self-documenting.

## The `@` Operator

The `@` operator attaches a unit to a number:

```python
from pyspice_rs.unit import u_V, u_kOhm, u_pF

voltage = 3.3 @ u_V      # 3.3 Volts
resistance = 10 @ u_kOhm  # 10 kilo-Ohms = 10,000 Ohms
capacitance = 5 @ u_pF    # 5 picofarads = 5e-12 Farads
```

Under the hood, `@` calls `__rmatmul__` on the unit object. The result is a `UnitValue` that stores the value in base SI units (so `10 @ u_kOhm` stores `10000.0` internally).

## All Available Units

### Voltage

| Constant | Meaning | Multiplier |
|----------|---------|------------|
| `u_V` | Volts | 1 |
| `u_mV` | Millivolts | 1e-3 |
| `u_uV` | Microvolts | 1e-6 |

```python
circuit.V(
    name="dd",
    positive="vdd",
    negative=circuit.gnd,
    value=3.3 @ u_V,
)
circuit.V(
    name="ref",
    positive="vref",
    negative=circuit.gnd,
    value=500 @ u_mV,
)
```

### Current

| Constant | Meaning | Multiplier |
|----------|---------|------------|
| `u_A` | Amperes | 1 |
| `u_mA` | Milliamperes | 1e-3 |
| `u_uA` | Microamperes | 1e-6 |
| `u_nA` | Nanoamperes | 1e-9 |

```python
circuit.I(
    name="bias",
    positive=circuit.gnd,
    negative="tail",
    value=100 @ u_uA,
)
```

### Resistance

| Constant | Meaning | Multiplier |
|----------|---------|------------|
| `u_Ohm` | Ohms | 1 |
| `u_kOhm` | kilo-Ohms | 1e3 |
| `u_MOhm` | Mega-Ohms | 1e6 |

```python
circuit.R(
    name="1",
    positive="a",
    negative="b",
    value=4.7 @ u_kOhm,
)
circuit.R(
    name="leak",
    positive="a",
    negative="b",
    value=10 @ u_MOhm,
)
```

### Capacitance

| Constant | Meaning | Multiplier |
|----------|---------|------------|
| `u_F` | Farads | 1 |
| `u_mF` | Millifarads | 1e-3 |
| `u_uF` | Microfarads | 1e-6 |
| `u_nF` | Nanofarads | 1e-9 |
| `u_pF` | Picofarads | 1e-12 |
| `u_fF` | Femtofarads | 1e-15 |

```python
circuit.C(
    name="bypass",
    positive="vdd",
    negative=circuit.gnd,
    value=100 @ u_nF,
)
circuit.C(
    name="gate",
    positive="g",
    negative=circuit.gnd,
    value=2 @ u_fF,
)
```

### Inductance

| Constant | Meaning | Multiplier |
|----------|---------|------------|
| `u_H` | Henrys | 1 |
| `u_mH` | Millihenrys | 1e-3 |
| `u_uH` | Microhenrys | 1e-6 |
| `u_nH` | Nanohenrys | 1e-9 |

```python
circuit.L(
    name="choke",
    positive="in",
    negative="out",
    value=10 @ u_uH,
)
```

### Frequency

| Constant | Meaning | Multiplier |
|----------|---------|------------|
| `u_Hz` | Hertz | 1 |
| `u_kHz` | Kilohertz | 1e3 |
| `u_MHz` | Megahertz | 1e6 |
| `u_GHz` | Gigahertz | 1e9 |

```python
# Used with waveform sources
circuit.SinusoidalVoltageSource(
    name="clk",
    positive="clk",
    negative=circuit.gnd,
    amplitude=1.0,
    frequency=100e6,
)
```

### Time

| Constant | Meaning | Multiplier |
|----------|---------|------------|
| `u_s` | Seconds | 1 |
| `u_ms` | Milliseconds | 1e-3 |
| `u_us` | Microseconds | 1e-6 |
| `u_ns` | Nanoseconds | 1e-9 |
| `u_ps` | Picoseconds | 1e-12 |

### Power

| Constant | Meaning | Multiplier |
|----------|---------|------------|
| `u_W` | Watts | 1 |
| `u_mW` | Milliwatts | 1e-3 |
| `u_uW` | Microwatts | 1e-6 |

### Temperature

| Constant | Meaning |
|----------|---------|
| `u_Degree` | Degrees Celsius |

## Working with UnitValues

A `UnitValue` object has useful methods:

```python
from pyspice_rs.unit import u_kOhm

val = 4.7 @ u_kOhm

# Get the raw float value (in base units)
print(val.value)        # 4700.0

# Convert to float
print(float(val))       # 4700.0

# Get the SPICE-format string
print(val.str_spice())  # "4.7k"

# Display representation
print(repr(val))        # "4.7kOhm"
print(str(val))         # "4.7kOhm"
```

## Importing Units

Import only what you need:

```python
from pyspice_rs.unit import u_V, u_kOhm, u_pF
```

Or import everything:

```python
from pyspice_rs.unit import *
```

## Plain Numbers

You can always use plain `float` values instead of units. PySpice-rs treats them as base SI units:

```python
circuit.R(name="1", positive="a", negative="b", value=1000.0)      # 1000 Ohms (same as 1 @ u_kOhm)
circuit.C(name="1", positive="a", negative="b", value=1e-12)       # 1e-12 Farads (same as 1 @ u_pF)
```

Units are optional but recommended for readability.
