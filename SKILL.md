---
name: battery-analysis
description: >
  Use for battery materials research and electrochemistry: analyzing cycling
  data from potentiostats (Biologic, Arbin, Maccor), predicting electrode
  voltages and capacities, electrochemical stability windows, impedance
  spectroscopy (EIS) fitting, battery modeling, cathode/anode screening,
  solid electrolyte analysis, or any lithium/sodium-ion battery workflow.
license: MIT
---

# Battery Analysis

## Critical Rules

1. **Always specify the battery chemistry** — Li-ion, Na-ion, solid-state, etc. Voltage windows, stability criteria, and analysis methods differ significantly.
2. **Cycling data must be parsed from the native potentiostat format** — CSV exports lose metadata (mass loading, cell area, protocol details). Use `galvani` for Biologic .mpr, `cellpy` for Arbin/Maccor.
3. **Report capacities normalized correctly** — mAh/g (gravimetric) requires accurate active mass. mAh/cm² (areal) requires electrode area. Always state which.
4. **Voltage profiles shift with C-rate** — don't compare 0.1C and 1C profiles directly without noting the rate.
5. **Coulombic efficiency is the most important cycling metric** — CE > 99.9% is typically needed for practical cells. Plot CE on a separate y-axis with expanded scale.
6. **For computational screening**, always check electrochemical stability window (voltage vs Li/Li+) using the Materials Project phase diagram, not just thermodynamic stability.

## Potentiostat Data Parsing

### Biologic (.mpr files)
```python
from galvani import BioLogic

mpr = BioLogic.MPRfile("cycling_data.mpr")
df = mpr.data

# Common columns: time/s, Ewe/V, I/mA, capacity/mA.h, cycle number
print(df.columns.tolist())

# Basic cycling plot
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(df["capacity/mA.h"], df["Ewe/V"])
ax1.set_xlabel("Capacity (mAh)")
ax1.set_ylabel("Voltage (V)")
plt.savefig("voltage_profile.png", dpi=150)
```

### Arbin / Maccor (via cellpy)
```python
from cellpy import cellreader

# Load raw data — cellpy handles Arbin .res and Maccor formats
cell = cellreader.CellpyCell()
cell.from_raw("arbin_data.res")

# Get summary per cycle
summary = cell.cell.summary
print(f"Cycles: {len(summary)}")
print(f"First discharge capacity: {summary.iloc[0]['discharge_capacity']:.1f} mAh/g")

# Get step data for voltage profiles
steps = cell.cell.steps

# Capacity vs cycle number
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
ax1.plot(summary.index, summary["discharge_capacity"], 'o-')
ax1.set_xlabel("Cycle")
ax1.set_ylabel("Discharge Capacity (mAh/g)")

ax2.plot(summary.index, summary["coulombic_efficiency"] * 100, 'o-')
ax2.set_xlabel("Cycle")
ax2.set_ylabel("Coulombic Efficiency (%)")
ax2.set_ylim([99, 101])
plt.tight_layout()
plt.savefig("cycling_summary.png", dpi=150)
```

## Electrochemical Impedance Spectroscopy (EIS)

```python
from impedance import preprocessing
from impedance.models.circuits import CustomCircuit

# Load EIS data (frequency, Z_real, Z_imag)
f, Z = preprocessing.readCSV("eis_data.csv")

# Ignore points below 0 (instrument artifacts)
f, Z = preprocessing.ignoreBelowX(f, Z)

# Define equivalent circuit
# R0 = ohmic resistance, R1-CPE1 = charge transfer, W1 = Warburg diffusion
circuit = "R0-p(R1,CPE1)-W1"
initial_guess = [10, 100, 1e-4, 0.8, 500]

circuit_model = CustomCircuit(circuit, initial_guess=initial_guess)
circuit_model.fit(f, Z)

print(f"Ohmic resistance: {circuit_model.parameters_[0]:.2f} Ω")
print(f"Charge transfer resistance: {circuit_model.parameters_[1]:.2f} Ω")

# Nyquist plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.plot(Z.real, -Z.imag, 'o', label="Data")
Z_fit = circuit_model.predict(f)
ax.plot(Z_fit.real, -Z_fit.imag, '-', label="Fit")
ax.set_xlabel("Z' (Ω)")
ax.set_ylabel("-Z'' (Ω)")
ax.set_aspect("equal")
ax.legend()
plt.savefig("nyquist.png", dpi=150)
```

## Computational Battery Screening

### Electrode voltage and capacity prediction
```python
from mp_api.client import MPRester
from pymatgen.apps.battery.insertion_battery import InsertionElectrode
from pymatgen.analysis.phase_diagram import PhaseDiagram
from pymatgen.entries.compatibility import MaterialsProjectCompatibility

with MPRester() as mpr:
    # Get all entries in the Li-Mn-O system
    entries = mpr.get_entries_in_chemsys(["Li", "Mn", "O"])

# Apply compatibility corrections
compat = MaterialsProjectCompatibility()
entries = compat.process_entries(entries)

# Build insertion electrode (Li into MnO2 framework)
# This calculates voltage profile and theoretical capacity
ie = InsertionElectrode.from_entries(entries, working_ion="Li")

print(f"Average voltage: {ie.get_average_voltage():.2f} V vs Li/Li+")
print(f"Theoretical capacity: {ie.get_capacity_grav():.0f} mAh/g")
print(f"Energy density: {ie.get_energy_grav():.0f} Wh/kg")
```

### Electrochemical stability window
```python
from mp_api.client import MPRester
from pymatgen.analysis.phase_diagram import PhaseDiagram

with MPRester() as mpr:
    # Check stability of a solid electrolyte against Li metal
    entries = mpr.get_entries_in_chemsys(["Li", "P", "S"])

pd = PhaseDiagram(entries)

# Get stability window — voltage range where electrolyte doesn't decompose
# This is critical for solid-state battery electrolyte selection
from pymatgen.analysis.phase_diagram import GrandPotentialPhaseDiagram

# Sweep Li chemical potential to find stability window
for voltage in [0, 1, 2, 3, 4, 5]:
    mu_li = -voltage  # μ_Li = -eV vs Li/Li+
    # Check if the material is stable at this potential
    # ... (use GrandPotentialPhaseDiagram)
```

## Physics-Based Modeling (PyBaMM)

```python
import pybamm

# Single Particle Model — fast, good for initial analysis
model = pybamm.lithium_ion.SPM()

# Or full Doyle-Fuller-Newman model — more accurate
# model = pybamm.lithium_ion.DFN()

# Use built-in parameter set
param = pybamm.ParameterValues("Chen2020")

# Simulate 1C discharge
sim = pybamm.Simulation(model, parameter_values=param)
sim.solve([0, 3600])  # 1 hour = 1C

# Plot
sim.plot(["Terminal voltage [V]", "Current [A]",
          "Negative particle concentration [mol.m-3]",
          "Positive particle concentration [mol.m-3]"])
```

## Common Battery Metrics

| Metric | Good Target | How to Calculate |
|---|---|---|
| Gravimetric capacity | >150 mAh/g (cathode) | Discharge capacity / active mass |
| Coulombic efficiency | >99.9% | Discharge capacity / charge capacity × 100 |
| Rate capability | >80% at 2C vs 0.1C | Capacity at high rate / capacity at low rate |
| Cycle retention | >80% after 500 cycles | Capacity at cycle N / capacity at cycle 1 |
| ICE (1st cycle) | >85% | 1st discharge / 1st charge × 100 |
| Voltage hysteresis | <0.2 V | Average charge V - average discharge V |
| ASR (impedance) | <20 Ω·cm² | From EIS fitting |

## Common Pitfalls
- **Mass loading errors** propagate directly to capacity — verify active mass carefully.
- **Formation cycles** (first 1-3 cycles) should be analyzed separately — SEI formation causes irreversible capacity loss.
- **Temperature matters** — always report cell temperature. Capacity increases ~1%/°C.
- **Calendar aging** — cells degrade even when not cycling. Note rest periods.
- **Two-electrode vs three-electrode** — coin cell data mixes cathode and anode contributions. Use reference electrode for single-electrode analysis.

## Reference
See `references/cellpy-guide.md` for detailed potentiostat data handling.
See `references/battery-screening.md` for computational screening workflows.
