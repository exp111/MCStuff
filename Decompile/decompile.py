from pathlib import Path
import os, sys
import subprocess

folder = "./"
pycdcPath = "pycdc.exe"
files = [p for p in Path(folder).rglob("*.pyc") if p.is_file()]
for file in files:
    print(file)
    out = subprocess.run([pycdcPath, str(file)], capture_output=True, text=True).stdout
    if not out:
        print(f"Couldn't read {file}")
        continue
    with open(f"{file.parent}/{file.stem}.py", "w") as f:
        f.write(out)