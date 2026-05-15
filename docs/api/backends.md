# Backends

PySpice-rs supports five SPICE simulator backends. Each has different strengths, and PySpice-rs auto-detects which ones are installed on your system.

## Supported Backends

| Backend | Open Source | Best For |
|---------|-----------|----------|
| **ngspice** | Yes | General-purpose, most compatible, great default |
| **Xyce** | Yes | Large circuits, parallel simulation, Monte Carlo |
| **LTspice** | Free (proprietary) | Switching power supplies, fast transient |
| **Spectre** | No (Cadence) | Analog/RF, industry standard for IC design |
| **Vacask** | No | Advanced RF, periodic steady state |

## Auto-Detection

By default, PySpice-rs auto-detects which simulator to use:

```python
sim = circuit.simulator()  # picks the best available backend
```

The detection priority is: ngspice > Xyce > LTspice > Spectre > Vacask.

## Choosing a Backend

Force a specific backend:

```python
sim = circuit.simulator(simulator="ngspice")
sim = circuit.simulator(simulator="xyce")
sim = circuit.simulator(simulator="ltspice")
sim = circuit.simulator(simulator="spectre")
sim = circuit.simulator(simulator="vacask")
```

## Checking Available Backends

```python
from pyspice_rs import CircuitSimulator

backends = CircuitSimulator.available_backends()
print(backends)
# e.g. ["ngspice", "xyce"]
```

## Backend-Specific Features

### ngspice

The default open-source SPICE simulator. Supports all standard analyses.

```python
sim = circuit.simulator(simulator="ngspice")
op = sim.operating_point()
dc = sim.dc(Vin=slice(0, 5, 0.01))
ac = sim.ac("dec", 100, 1.0, 1e9)
tran = sim.transient(1e-9, 100e-9)
```

### Xyce (Sandia National Labs)

Designed for large-scale parallel simulation. Has unique uncertainty quantification features.

```python
sim = circuit.simulator(simulator="xyce")

# Standard analyses work the same
op = sim.operating_point()
tran = sim.transient(1e-9, 100e-9)

# Xyce-specific: Monte Carlo sampling
sampling = sim.xyce_sampling(
    num_samples=100,
    param_distributions=[
        ("R1:R", "normal(1000,50)"),      # R1 with 5% Gaussian variation
        ("C1:C", "uniform(0.9e-12,1.1e-12)")
    ]
)

# Xyce-specific: Embedded Monte Carlo (in time/freq domain)
embedded = sim.xyce_embedded_sampling(
    num_samples=50,
    param_distributions=[("R1:R", "normal(1000,50)")]
)

# Xyce-specific: Polynomial Chaos Expansion
pce = sim.xyce_pce(
    num_samples=100,
    param_distributions=[("R1:R", "normal(1000,50)")],
    expansion_order=3
)

# Xyce-specific: FFT with spectral metrics
fft = sim.xyce_fft("V(out)",
    np=1024,        # number of FFT points
    start=0.0,      # start time
    stop=1e-3,      # stop time
    window="HANN",  # window function
    format="UNORM"  # output format
)

print(f"ENOB: {fft.enob:.1f} bits")
print(f"SFDR: {fft.sfdr_db:.1f} dB")
print(f"SNR:  {fft.snr_db:.1f} dB")
print(f"THD:  {fft.thd_db:.1f} dB")
```

### LTspice

Very fast for switching power supply simulation.

```python
sim = circuit.simulator(simulator="ltspice")

# LTspice .NET for S-parameter analysis
sp = sim.network_params(
    output_current="I(R1)",
    input_source="Vin",
    z_in=50.0,
    z_out=50.0,
    variation="dec",
    points=100,
    start_freq=1e3,
    stop_freq=1e9
)
```

### Spectre (Cadence)

Industry-standard for analog IC design. Has unique RF analysis capabilities.

```python
sim = circuit.simulator(simulator="spectre")

# Standard analyses
ac = sim.ac("dec", 100, 1.0, 1e9)

# Spectre-specific: Parametric sweep
raw = sim.spectre_sweep(
    param="Rload",
    start=100,
    stop=10000,
    step=100,
    inner_analysis="ac1 ac start=1 stop=1G dec=100",
    inner_type="ac"
)

# Spectre-specific: Monte Carlo
raw = sim.spectre_montecarlo(
    num_iterations=100,
    inner_analysis="ac1 ac start=1 stop=1G dec=100",
    inner_type="ac",
    seed=42
)

# SpectreRF: Periodic AC (PAC) -- small-signal around periodic operating point
pac = sim.spectre_pac(
    pss_fundamental=1e9,     # LO frequency for PSS
    pss_stabilization=10e-9, # settling time
    pss_harmonics=10,
    variation="dec",
    points=100,
    start_freq=1.0,
    stop_freq=1e9,
    sweep_type="relative"
)

# SpectreRF: Periodic Noise (PNoise)
pnoise = sim.spectre_pnoise(
    pss_fundamental=1e9,
    pss_stabilization=10e-9,
    output_node="output",
    ref_node="0",
    pss_harmonics=10,
    variation="dec",
    points=100,
    start_freq=1.0,
    stop_freq=1e9
)

# SpectreRF: Periodic Transfer Function (PXF)
pxf = sim.spectre_pxf(
    pss_fundamental=1e9,
    pss_stabilization=10e-9,
    output_node="output",
    source="Vin",
    pss_harmonics=10,
    variation="dec",
    points=100,
    start_freq=1.0,
    stop_freq=1e9
)

# SpectreRF: Periodic Stability (PSTB)
pstb = sim.spectre_pstb(
    pss_fundamental=1e9,
    pss_stabilization=10e-9,
    probe="loop_break",
    pss_harmonics=10,
    variation="dec",
    points=100,
    start_freq=1.0,
    stop_freq=1e9
)
```

### Vacask

Advanced analog/RF simulator with periodic analyses.

```python
sim = circuit.simulator(simulator="vacask")

# Periodic Steady State
pss = sim.pss(1e9, 10e-9, "output", 128, 10)

# Stability analysis
stab = sim.stability("probe", "dec", 100, 1.0, 1e10)

# Transient noise
tnoise = sim.transient_noise(1e-9, 100e-9)
```

## Analysis Compatibility

Not all analyses are supported by all backends. Here's a quick compatibility matrix:

| Analysis | ngspice | Xyce | LTspice | Spectre | Vacask |
|----------|---------|------|---------|---------|--------|
| Operating Point | Yes | Yes | Yes | Yes | Yes |
| DC Sweep | Yes | Yes | Yes | Yes | Yes |
| AC | Yes | Yes | Yes | Yes | Yes |
| Transient | Yes | Yes | Yes | Yes | Yes |
| Noise | Yes | Yes | Yes | Yes | Yes |
| Transfer Function | Yes | Yes | -- | -- | -- |
| Sensitivity | Yes | -- | -- | -- | -- |
| Pole-Zero | Yes | -- | -- | -- | -- |
| Distortion | Yes | -- | -- | -- | -- |
| PSS | Experimental | -- | -- | Yes | Yes |
| S-Parameters | Yes | -- | Yes | Yes | -- |
| Harmonic Balance | -- | Yes | -- | Yes | Yes |
| Stability | -- | -- | -- | Yes | Yes |
| Monte Carlo | -- | Yes | -- | Yes | -- |
| FFT | -- | Yes | -- | -- | -- |

Use the [linter](linting.md) with a specific backend to catch unsupported features before simulating.
