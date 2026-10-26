import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = []

def run(name, cmd, cwd):
    print(f"\n=== {name} ===")
    p = subprocess.run(cmd, cwd=cwd, shell=True)
    results.append((name, p.returncode == 0))
    print(f"{name}: {'PASS' if p.returncode == 0 else 'FAIL'}")

run("Backend tests", "python -m pytest -q", os.path.join(ROOT, "backend"))
run("Frontend build", "npm run build", os.path.join(ROOT, "frontend"))

print("\n=== SUMMARY ===")
for name, ok in results:
    print(f"{name}: {'PASS' if ok else 'FAIL'}")
sys.exit(0 if all(ok for _, ok in results) else 1)
