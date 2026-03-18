from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parents[1]

pairs = [
    (BASE_DIR / ".env.example", BASE_DIR / ".env"),
    (BASE_DIR / ".env.test.example", BASE_DIR / ".env.test"),
]

for src, dst in pairs:
    if src.exists() and not dst.exists():
        shutil.copyfile(src, dst)
        print(f"created: {dst.name}")
    else:
        print(f"skip: {dst.name}")