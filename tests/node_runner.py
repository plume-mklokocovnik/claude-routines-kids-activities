"""Run a snippet of JavaScript against a script from app/static under Node.

The browser code has no test runner of its own, so its pure logic is loaded with
require() and driven from here. Tests that use this skip themselves when Node is
not installed.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

NODE = shutil.which("node")
STATIC = Path(__file__).resolve().parents[1] / "app" / "static"


def run(script, timezone=None):
    """Evaluate `script` (which may use await) and return what it resolves to."""
    program = ("(async () => {" + script + "})()"
               ".then((value) => console.log(JSON.stringify(value)))"
               ".catch((error) => { console.error(error.stack || String(error)); process.exit(1); });")
    env = dict(os.environ)
    if timezone:
        env["TZ"] = timezone
    result = subprocess.run([NODE, "-e", program], capture_output=True, text=True, env=env)
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def require(name):
    """A JavaScript statement that loads one of the static scripts."""
    return f"const {name.split('.')[0].capitalize()} = require({json.dumps(str(STATIC / name))});"
