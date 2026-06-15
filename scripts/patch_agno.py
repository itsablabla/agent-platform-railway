"""Patch agno router to handle string status in _resume_stream_generator (agno 2.6.14 bug)."""

import glob
import sys

paths = glob.glob("/usr/local/lib/python*/site-packages/agno/os/routers/agents/router.py")
if not paths:
    print("agno router not found, skipping patch")
    sys.exit(0)

OLD = 'run_output.status.value if run_output.status else "unknown"'
NEW = '(run_output.status.value if hasattr(run_output.status, "value") else str(run_output.status)) if run_output.status else "unknown"'

for path in paths:
    with open(path) as f:
        content = f.read()
    count = content.count(OLD)
    if count == 0:
        print(f"Pattern not found in {path} — patch may already be applied or agno version changed")
        continue
    with open(path, "w") as f:
        f.write(content.replace(OLD, NEW))
    print(f"Patched {count} occurrence(s) in {path}")
