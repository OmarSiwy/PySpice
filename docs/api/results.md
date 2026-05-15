# Results

Every simulation analysis returns a result object. This page explains how to read data from each type.

## Common Pattern

All result objects support two ways to access data:

```python
# Dictionary-style (subscript)
value = result["node_name"]

# Attribute-style (dot notation)
value = result.node_name
```

If the node doesn't exist, `KeyError` or `AttributeError` is raised.

## Operating Point Results

`operating_point()` returns a single voltage for each node.

```python
op = sim.operating_point()

# Each access returns a single float
vout = op["output"]          # e.g. 3.333
vdd = op["vdd"]              # e.g. 5.0
```

## DC Analysis Results

`dc()` returns arrays -- one value per sweep point.

```python
dc = sim.dc(Vinput=slice(0, 5, 0.1))

# The sweep variable values
sweep = dc.sweep                  # [0.0, 0.1, 0.2, ..., 5.0]

# Node voltages at each sweep point
vout = dc["output"]               # [0.0, 0.033, 0.066, ..., 1.666]

# Same length as sweep
assert len(vout) == len(sweep)
```

## AC Analysis Results

`ac()` returns complex data at each frequency point.

```python
ac = sim.ac("dec", 100, 1.0, 1e9)

# Frequency points
freqs = ac.frequency              # [1.0, 1.23, 1.51, ..., 1e9]

# Node data (magnitude values)
vout = ac["output"]               # array of values at each frequency
```

## Transient Analysis Results

`transient()` returns time-domain waveforms.

```python
tran = sim.transient(1e-9, 100e-9)

# Time points
t = tran.time                     # [0.0, 1e-9, 2e-9, ..., 100e-9]

# Node voltages vs. time
vout = tran["output"]             # array of voltages
vin = tran["input"]

# Same length
assert len(vout) == len(t)
```

## Noise Analysis Results

```python
noise = sim.noise("output", "0", "Vin", "dec", 10, 1e3, 1e8)

# Access noise spectral density data
data = noise["onoise_spectrum"]   # output-referred noise
data = noise["inoise_spectrum"]   # input-referred noise
```

## Transfer Function Results

```python
tf = sim.tf("V(output)", "Vin")

# Access transfer function data
data = tf["output"]
```

## Other Analysis Results

All other analysis types follow the same pattern:

| Analysis | Time/Frequency Axis | Data Access |
|----------|---------------------|-------------|
| `pss()` | `.time` | `result["node"]` |
| `s_param()` | `.frequency` | `result["S11"]` etc. |
| `harmonic_balance()` | `.frequency` | `result["node"]` |
| `stability()` | `.frequency` | `result["loopgain"]` etc. |
| `distortion()` | `.frequency` | `result["node"]` |

## Measurement Results

If you added `.meas` directives before simulation, the results are available as a dictionary:

```python
sim.measure("tran", "vpeak", "MAX", "V(out)")
sim.measure("tran", "trise", "TRIG", "V(out)", "VAL=0.5", "RISE=1",
            "TARG", "V(out)", "VAL=4.5", "RISE=1")

tran = sim.transient(1e-9, 1e-3)

# Access measured values
print(tran.measures)
# {"vpeak": 4.95, "trise": 2.3e-7}

print(tran.measures["vpeak"])    # 4.95
print(tran.measures["trise"])    # 2.3e-7
```

## RawData Results

The `spectre_sweep()` and `spectre_montecarlo()` methods return a generic `RawData` object:

```python
raw = sim.spectre_sweep("Rload", 100, 10000, 100,
                         "ac1 ac start=1 stop=1G dec=100", "ac")

# Metadata
print(raw.title)
print(raw.plot_name)
print(raw.is_complex)
print(raw.variable_names)        # list of all variable names

# Data access (same as other results)
data = raw["frequency"]
data = raw["V(output)"]
```

## Xyce FFT Results

The `xyce_fft()` method returns spectral metrics alongside the data:

```python
fft = sim.xyce_fft("V(out)", np=1024, start=0.0, stop=1e-3)

# Spectral data
freqs = fft.frequency
mags = fft.magnitude
phases = fft.phase

# Pre-computed metrics
print(f"ENOB:  {fft.enob:.1f} bits")
print(f"SFDR:  {fft.sfdr_db:.1f} dB")
print(f"SNR:   {fft.snr_db:.1f} dB")
print(f"THD:   {fft.thd_db:.1f} dB")
```

## Tips

- All array data is returned as Python `list[float]`. Use `numpy.array()` if you need NumPy operations.
- Node names are case-insensitive in most backends.
- Current through a voltage source `Vin` is typically accessed as `i(vin)` or `vin#branch` depending on the backend.
