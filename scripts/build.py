"""Bundle the exact Python engine and SimPy for the static dashboard."""
from pathlib import Path
import shutil
import zipfile
import simpy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
OUT.mkdir(exist_ok=True)
for path in (ROOT / "dashboard").iterdir():
    if path.is_file():
        shutil.copy2(path, OUT / path.name)
with zipfile.ZipFile(OUT / "engine.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for path in [ROOT / "simulation.py", *sorted((ROOT / "components").glob("*.py"))]:
        archive.write(path, str(path.relative_to(ROOT)))
    package = Path(simpy.__file__).parent
    for path in sorted(package.rglob("*.py")):
        archive.write(path, "simpy/" + str(path.relative_to(package)))
    license_file = package.parent / "simpy-4.1.1.dist-info" / "LICENSE.rst"
    if license_file.exists():
        archive.write(license_file, "SIMPY-LICENSE.rst")
print(f"Built dashboard in {OUT}")
