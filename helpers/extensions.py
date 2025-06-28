import os

from pathlib import Path

extensions = []

for name in os.listdir("commands"):
    if name.startswith("_") or name.startswith("."):
        continue

    file = Path("commands/" + name)
    extensions.append("commands." + file.stem)

for name in os.listdir("tasks"):
    if name.startswith("_") or name.startswith("."):
        continue

    file = Path("tasks/" + name)
    extensions.append("tasks." + file.stem)

for name in os.listdir("events"):
    if name.startswith("_") or name.startswith("."):
        continue

    file = Path("events/" + name)
    extensions.append("events." + file.stem)