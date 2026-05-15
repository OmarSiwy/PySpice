"""
Example 15: Netlist Linting

Builds a circuit with intentional issues:
  - A floating node (not connected to anything useful)
  - A missing .model reference

Calls the lint() function and prints warnings and errors.
"""
from pyspice_rs import Circuit, lint

# Build a circuit with deliberate issues
circuit = Circuit("Linting Example")

# Voltage source
circuit.V(
    name="in",
    positive="input",
    negative=circuit.gnd,
    value=5.0,
)

# Resistor connected to a floating node "orphan"
circuit.R(
    name="1",
    positive="input",
    negative="orphan",
    value=1000.0,
)

# Diode referencing a model that is NOT defined in this circuit
circuit.D(
    name="1",
    anode="input",
    cathode=circuit.gnd,
    model="MISSING_MODEL",
)

# Generate the netlist string
netlist = str(circuit)
print("=== Netlist ===")
print(netlist)

# Lint the netlist
print("\n=== Lint Results ===")
results = lint(netlist)

warnings = results.get("warnings", [])
errors = results.get("errors", [])

if warnings:
    print(f"\nWarnings ({len(warnings)}):")
    for w in warnings:
        line = w.get("line", "?")
        msg = w.get("message", "")
        suggestion = w.get("suggestion", "")
        backends = w.get("backends_affected", [])
        print(f"  Line {line}: {msg}")
        if suggestion:
            print(f"    Suggestion: {suggestion}")
        if backends:
            print(f"    Backends: {', '.join(str(b) for b in backends)}")
else:
    print("\nNo warnings.")

if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        line = e.get("line", "?")
        msg = e.get("message", "")
        print(f"  Line {line}: {msg}")
else:
    print("\nNo errors.")

# Also lint with a specific backend
print("\n=== Lint for ngspice backend ===")
results_ng = lint(netlist, backend="ngspice")
for category in ("warnings", "errors"):
    items = results_ng.get(category, [])
    if items:
        print(f"\n{category.title()} ({len(items)}):")
        for item in items:
            print(f"  Line {item.get('line', '?')}: {item.get('message', '')}")
