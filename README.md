# Spinel

A materials science toolkit for Claude Code. Install once, get access to materials databases, analysis tools, and domain expertise.

## Quick Start

```bash
/plugin marketplace add renaissance-philanthropy/spinel
/plugin install spinel
```

That's it. Spinel auto-creates a virtual environment at `~/.spinel/venv`, installs dependencies, and checks your API keys on first session. You just need a Materials Project API key:

1. Create free account at https://next-gen.materialsproject.org
2. Dashboard → API Key
3. `export MP_API_KEY=your_key_here`

## What's Included

### MCP Servers
- **Materials Project** — 150,000+ computed inorganic materials
- **AFLOW** — Crystal prototypes, thermodynamic properties (stub)
- **NOMAD** — DFT calculations, experimental datasets (stub)

### Skills
| Skill | What it does |
|---|---|
| `crystal-structure-analysis` | Load, inspect, compare crystal structures (pymatgen) |
| `phase-diagrams` | Convex hulls, stability, Pourbaix diagrams, CALPHAD (pymatgen, pycalphad) |
| `electronic-structure` | Band structures, DOS, band gap analysis (pymatgen) |
| `xrd-analysis` | Simulate/match XRD patterns, peak indexing (pymatgen) |
| `instrument-data` | Parse vendor files — Bruker, Gatan, Thermo Fisher, Rigaku (hyperspy, tifffile, jcamp) |
| `materials-screening` | High-throughput property search across databases (mp-api) |
| `battery-analysis` | Cycling data, EIS fitting, electrode voltage prediction, PyBaMM modeling (cellpy, galvani, impedance.py, PyBaMM) |

Each skill includes reference documentation that loads into Claude's context on demand — ensuring Claude uses current APIs, not stale training data.

### Auto-Setup

Spinel uses a `SessionStart` hook to automatically:
- Create `~/.spinel/venv` if it doesn't exist (uses `uv` if available, falls back to `venv`)
- Install missing Python packages
- Check for `MP_API_KEY` and warn if missing

No manual environment management needed.

## Core Packages

| Package | Domain |
|---|---|
| `pymatgen` + `mp-api` | Crystal structures, phase diagrams, electronic structure, diffraction |
| `ase` | DFT workflows, structure building, calculator interfaces (VASP, QE, GPAW) |
| `hyperspy` + `kikuchipy` | Electron microscopy (EELS, EDS, EBSD) |
| `pycalphad` + `scheil` | CALPHAD thermodynamics, solidification |
| `phonopy` | Phonon band structures, thermal properties |
| `matgl` | ML interatomic potentials (M3GNet, CHGNet) |
| `diffpy.structure` | Pair distribution function analysis |
| `Dans_Diffraction` | Multi-radiation diffraction simulation |
| `cellpy` + `galvani` | Potentiostat data (Biologic .mpr, Arbin .res, Maccor) |
| `impedance.py` | EIS equivalent circuit fitting |
| `PyBaMM` | Physics-based battery modeling (SPM, DFN) |

## Usage

Just ask Claude naturally:

- "Find stable perovskite oxides with band gaps between 1.5 and 3 eV"
- "Parse this .mpr file and plot the voltage profiles and coulombic efficiency"
- "What's the theoretical capacity and average voltage of LiMnO2 as a cathode?"
- "Fit this EIS data to a Randles circuit and extract the charge transfer resistance"
- "Simulate a 1C discharge of an NMC cell using PyBaMM"
- "Parse this .dm4 file from our TEM and extract the EELS spectrum"
- "Build a CALPHAD phase diagram for the Al-Cu-Mg system"

## Architecture

```
spinel/
├── .claude-plugin/plugin.json
├── .mcp.json                            # Materials Project + AFLOW + NOMAD
├── pyproject.toml
├── skills/
│   ├── crystal-structure-analysis/
│   │   ├── SKILL.md
│   │   └── references/pymatgen-api.md
│   ├── phase-diagrams/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── electronic-structure/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── xrd-analysis/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── instrument-data/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── materials-screening/
│   │   ├── SKILL.md
│   │   └── references/mp-api-guide.md
│   └── battery-analysis/
│       ├── SKILL.md
│       └── references/
├── scripts/
│   ├── setup.py                         # Auto-setup (SessionStart hook)
│   └── validate_structure.py            # Structure validation
├── servers/
│   ├── materials_project_server.py      # Implemented
│   ├── aflow_server.py                  # Stub
│   └── nomad_server.py                  # Stub
└── hooks/
    └── hooks.json                       # SessionStart auto-setup
```

## Contributing

We need domain experts to review and improve skill files — especially the "Critical Rules" and "Common Pitfalls" sections, which encode the tribal knowledge that makes the difference between useful and broken AI-assisted analysis.

## License

MIT
