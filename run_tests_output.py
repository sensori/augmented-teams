import subprocess
import sys
import os

os.chdir(r"c:\dev\augmented-teams")

result = subprocess.run(
    [sys.executable, "-m", "pytest", "agile_bot/bots/base_bot/test", "-v", "--tb=short"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)

sys.stdout.write(result.stdout)
if result.stderr:
    sys.stderr.write(result.stderr)

sys.exit(result.returncode)
