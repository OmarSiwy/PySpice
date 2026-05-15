# Linting

PySpice-rs includes a built-in SPICE netlist linter that catches common mistakes before you send your circuit to a simulator. This saves time by catching issues that would otherwise result in cryptic simulator errors.

## Basic Usage

```python
from pyspice_rs import Circuit, lint

# Build a circuit
circuit = Circuit("My Circuit")
circuit.R(
    name="1",
    positive="in",
    negative="out",
    value=1e3,
)
circuit.R(
    name="2",
    positive="out",
    negative=circuit.gnd,
    value=1e3,
)

# Lint the netlist
result = lint(str(circuit))

print(f"Warnings: {len(result['warnings'])}")
print(f"Errors:   {len(result['errors'])}")
```

## The `lint()` Function

```python
lint(netlist, backend=None)
```

**Parameters:**
- `netlist` (str) -- the SPICE netlist text (e.g., `str(circuit)`)
- `backend` (str, optional) -- target backend for backend-specific checks. One of `"ngspice"`, `"xyce"`, `"ltspice"`, `"spectre"`.

**Returns:** A dictionary with two keys:
- `"warnings"` -- list of warning dicts
- `"errors"` -- list of error dicts

## Warning Format

Each warning is a dictionary:

```python
{
    "line": 3,                                  # line number in the netlist
    "message": "Resistor 'R2' has zero resistance",
    "suggestion": "Use a small value (e.g., 1m) or a voltage source instead",
    "backends_affected": ["ngspice", "xyce", "ltspice", "spectre"]
}
```

## Error Format

Each error is a dictionary:

```python
{
    "line": 0,
    "message": "Netlist is missing .end directive"
}
```

## What the Linter Checks

### Universal Checks (all backends)

| Check | Severity | Description |
|-------|----------|-------------|
| Missing `.end` | Error | Every netlist must end with `.end` |
| Missing ground | Error | Circuit must have a ground node (`0` or `gnd`) |
| Duplicate elements | Warning | Two elements with the same name (e.g., two `R1`) |
| Floating nodes | Warning | A node connected to only one element |
| Zero-value components | Warning | `R=0` (short circuit) or `C=0` (open circuit) |
| Missing model | Warning | Element references a model not defined in the netlist |
| Undefined parameters | Warning | Parameter used but never defined with `.param` |

### Backend-Specific Checks

When you pass a `backend` argument, additional checks are performed:

**ngspice:**
- Warns about `.meas` syntax differences

**Xyce:**
- Error: `.control`/`.endc` blocks (not supported)
- Warning: `.pz` analysis (not supported)

**LTspice:**
- Warning: `.sens` analysis (not supported)
- Error: `.control`/`.endc` blocks (not supported)

**Spectre:**
- Warning: `.disto` analysis (not supported)
- Error: `.control`/`.endc` blocks (not supported)

## Example: Catching Issues

```python
from pyspice_rs import Circuit, lint

circuit = Circuit("Problem Circuit")
circuit.R(
    name="1",
    positive="in",
    negative="mid",
    value=1e3,
)
circuit.R(
    name="2",
    positive="mid",
    negative=circuit.gnd,
    value=0.0,
)
circuit.D(
    name="1",
    anode="mid",
    cathode="dangling",
    model="BAD",
)

result = lint(str(circuit))

for w in result["warnings"]:
    print(f"Line {w['line']}: {w['message']}")
    if w.get("suggestion"):
        print(f"  Fix: {w['suggestion']}")
```

Output:
```
Line 4: Node 'dangling' is connected to only one element (floating node)
  Fix: Add another connection or remove the node
Line 2: Node 'in' is connected to only one element (floating node)
  Fix: Add another connection or remove the node
Line 3: Resistor 'R2' has zero resistance
  Fix: Use a small value (e.g., 1m) or a voltage source instead
Line 4: Element 'D1' references model 'BAD' which is not defined in this netlist
  Fix: Add a .model definition or .include the model file
```

## Example: Backend-Specific Lint

```python
netlist = """.title Test
R1 in out 1k
R2 out 0 1k
.control
run
.endc
.end
"""

# General lint
result = lint(netlist)
print(f"General: {len(result['warnings'])} warnings, {len(result['errors'])} errors")

# Xyce-specific lint
result_xyce = lint(netlist, backend="xyce")
print(f"Xyce: {len(result_xyce['warnings'])} warnings, {len(result_xyce['errors'])} errors")
# Xyce will flag .control/.endc as an error
```

## Example: Validating Generated Netlists

A good workflow is to lint before simulating:

```python
from pyspice_rs import Circuit, lint

def build_and_validate(circuit):
    """Build netlist and check for issues before simulating."""
    netlist = str(circuit)
    result = lint(netlist)

    if result["errors"]:
        for e in result["errors"]:
            print(f"ERROR: {e['message']}")
        raise ValueError("Netlist has errors -- fix before simulating")

    if result["warnings"]:
        for w in result["warnings"]:
            print(f"WARNING: {w['message']}")

    return circuit.simulator()

# Use it
circuit = Circuit("Safe Circuit")
circuit.V(
    name="in",
    positive="in",
    negative=circuit.gnd,
    value=5.0,
)
circuit.R(
    name="1",
    positive="in",
    negative="out",
    value=1e3,
)
circuit.R(
    name="2",
    positive="out",
    negative=circuit.gnd,
    value=2e3,
)

sim = build_and_validate(circuit)
# No warnings, no errors -- safe to simulate
```
