#!/usr/bin/env python3
"""
Spinel auto-setup script. Runs on SessionStart hook.

1. Creates a spinel venv if it doesn't exist
2. Installs core dependencies into the venv
3. Checks for required API keys
4. Reports status

Designed for scientists who may not be familiar with Python
environment management.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

VENV_DIR = Path.home() / ".spinel" / "venv"
REQUIREMENTS = [
    "pymatgen>=2024.0.0",
    "mp-api>=0.41.0",
    "emmet-core",
    "ase>=3.22",
    "hyperspy>=2.0",
    "kikuchipy",
    "pycalphad",
    "scheil",
    "phonopy",
    "matgl",
    "diffpy.structure",
    "Dans_Diffraction",
    "tifffile",
    "jcamp",
    "brukeropusreader",
    "spc-spectra",
    "cellpy",
    "galvani",
    "impedance.py",
    "PyBaMM",
]

OPTIONAL_PACKAGES = {
    "ml": ["megnet", "chgnet", "m3gnet"],
    "spectroscopy": ["renishawWiRE", "ramanspy"],
    "dft": ["custodian", "atomate2", "jobflow", "quacc"],
}


def run(cmd, **kwargs):
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300, **kwargs
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def get_pip():
    """Get path to pip in spinel venv."""
    if sys.platform == "win32":
        return str(VENV_DIR / "Scripts" / "pip")
    return str(VENV_DIR / "bin" / "pip")


def get_python():
    """Get path to python in spinel venv."""
    if sys.platform == "win32":
        return str(VENV_DIR / "Scripts" / "python")
    return str(VENV_DIR / "bin" / "python")


def ensure_venv():
    """Create spinel venv if it doesn't exist."""
    if (VENV_DIR / "bin" / "python").exists() or (VENV_DIR / "Scripts" / "python.exe").exists():
        return True, "venv exists"

    print("Creating Spinel virtual environment at ~/.spinel/venv ...")
    VENV_DIR.parent.mkdir(parents=True, exist_ok=True)

    # Try uv first (much faster), fall back to venv
    uv = shutil.which("uv")
    if uv:
        ok, out = run([uv, "venv", str(VENV_DIR)])
        if ok:
            return True, "created with uv"

    ok, out = run([sys.executable, "-m", "venv", str(VENV_DIR)])
    if ok:
        return True, "created with venv"

    return False, f"Failed to create venv: {out}"


def check_installed():
    """Check which required packages are already installed."""
    pip = get_pip()
    ok, out = run([pip, "list", "--format=columns"])
    if not ok:
        return set()

    installed = set()
    for line in out.strip().split("\n")[2:]:  # skip header
        parts = line.split()
        if parts:
            installed.add(parts[0].lower().replace("-", "_").replace(".", "_"))
    return installed


def install_missing(installed):
    """Install packages that aren't present yet."""
    pip = get_pip()

    # Normalize package names for comparison
    def normalize(name):
        return name.lower().split(">=")[0].split("<=")[0].split("==")[0].replace("-", "_").replace(".", "_")

    missing = [pkg for pkg in REQUIREMENTS if normalize(pkg) not in installed]

    if not missing:
        return True, "all packages installed"

    print(f"Installing {len(missing)} missing packages...")

    # Try uv pip first for speed
    uv = shutil.which("uv")
    if uv:
        ok, out = run([uv, "pip", "install", "--python", get_python()] + missing)
        if ok:
            return True, f"installed {len(missing)} packages with uv"

    # Fall back to pip
    ok, out = run([pip, "install"] + missing)
    if ok:
        return True, f"installed {len(missing)} packages with pip"

    return False, f"Installation failed: {out[-500:]}"


def check_api_keys():
    """Check for required API keys."""
    issues = []

    mp_key = os.environ.get("MP_API_KEY")
    if not mp_key:
        issues.append(
            "MP_API_KEY not set. Get a free key at https://next-gen.materialsproject.org "
            "(Dashboard → API Key), then: export MP_API_KEY=your_key"
        )

    # Optional keys — just note if missing
    notes = []
    if not os.environ.get("NOMAD_TOKEN"):
        notes.append("NOMAD_TOKEN not set (optional — needed only for private NOMAD data)")

    return issues, notes


def main():
    status = []

    # Step 1: venv
    ok, msg = ensure_venv()
    if not ok:
        print(f"✗ Venv setup failed: {msg}")
        print("  Try manually: python -m venv ~/.spinel/venv")
        return
    status.append(f"✓ Venv: {msg}")

    # Step 2: packages
    installed = check_installed()
    ok, msg = install_missing(installed)
    if not ok:
        print(f"⚠ Package installation issue: {msg}")
        print(f"  Try manually: {get_pip()} install pymatgen mp-api ase hyperspy")
    else:
        status.append(f"✓ Packages: {msg}")

    # Step 3: API keys
    issues, notes = check_api_keys()
    if issues:
        for issue in issues:
            status.append(f"⚠ {issue}")
    else:
        status.append("✓ API keys configured")

    for note in notes:
        status.append(f"  ℹ {note}")

    # Report
    print("\n".join(status))
    print(f"\nSpinel venv: {VENV_DIR}")
    print(f"Python: {get_python()}")
    print(f"To activate manually: source {VENV_DIR}/bin/activate")


if __name__ == "__main__":
    main()
