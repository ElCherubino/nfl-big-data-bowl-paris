#!/usr/bin/env python3
"""Generic, offline functional self-check for an installed developer environment."""
from __future__ import annotations
import argparse
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("grill-me", "grilling", "research", "implement", "tdd",
          "code-review", "diagnosing-bugs", "handoff", "pr",
          "explore-data", "validate-data", "data-visualization")
HOME = Path.home()
LOCATIONS = {
    "kiro-cli": (ROOT / ".kiro/skills", HOME / ".kiro/skills"),
    "claude-code": (ROOT / ".claude/skills", HOME / ".claude/skills"),
    "codex": (ROOT / ".agents/skills", ROOT / ".codex/skills",
              HOME / ".agents/skills", HOME / ".codex/skills"),
}

class Results:
    def __init__(self):
        self.items = []
    def add(self, level, title, detail):
        self.items.append({"status": level, "name": title, "details": str(detail)})
        print(f"[{level:<4}] {title}: {detail}", flush=True)
    def check(self, title, func, required=True):
        try:
            self.add("PASS", title, func())
        except Exception as exc:
            self.add("FAIL" if required else "WARN", title, f"{type(exc).__name__}: {exc}")
            if os.getenv("TEST_ENV_DEBUG") == "1":
                traceback.print_exc()
    def finish(self, json_file):
        count = {status: sum(x["status"] == status for x in self.items)
                 for status in ("PASS", "WARN", "FAIL")}
        good = count["FAIL"] == 0
        print("\n" + "=" * 62)
        print("  ".join(f"{n}: {count[n]}" for n in count))
        print("PYTHON READY" if good else "NOT READY — some required tests failed")
        if count["WARN"]:
            print("Check warnings: optional tools/skills may not be available.")
        print("=" * 62)
        if json_file:
            json_file.parent.mkdir(parents=True, exist_ok=True)
            json_file.write_text(json.dumps({"ready": good, "summary": count,
                                             "checks": self.items}, indent=2) + "\n",
                                 encoding="utf-8")
            print(f"Report: {json_file}")
        return 0 if good else 1

def verify(ok, message):
    if not ok:
        raise AssertionError(message)

def runtime():
    verify(sys.version_info >= (3, 11), "Python 3.11+ required")
    verify(sys.prefix != sys.base_prefix, "Not a virtual environment")
    verify(Path(sys.prefix).resolve() == (ROOT / ".venv").resolve(), "Not this project's .venv")
    return f"{sys.version.split()[0]} — {sys.executable}"

def numpy_check():
    import numpy as np
    arr = np.array([[0., 0.], [3., 4.]])
    verify(math.isclose(float(np.linalg.norm(arr[1] - arr[0])), 5), "Wrong distance")
    return f"numpy {np.__version__}: vector distance = 5"

def pandas_check():
    import pandas as pd
    df = pd.DataFrame({"key": [1, 1, 2], "value": [10, 20, 30]})
    verify(float(df.groupby("key").value.mean().loc[1]) == 15, "Groupby failed")
    verify(len(df.query("value > 15")) == 2, "Filter failed")
    return f"pandas {pd.__version__}: filter + groupby OK"

def scipy_check():
    import scipy
    from scipy.spatial.distance import cdist
    verify(math.isclose(float(cdist([[0,0]], [[3,4]])[0][0]), 5), "cdist incorrect")
    return f"scipy {scipy.__version__}: spatial distance OK"

def sklearn_check():
    import sklearn
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=1).fit([[0,0], [8,0]])
    dist, index = nn.kneighbors([[7,0]])
    verify(index[0][0] == 1 and math.isclose(float(dist[0][0]), 1), "Nearest neighbor failed")
    return f"scikit-learn {sklearn.__version__}: model fit + query OK"

def arrow_check():
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    table = pa.Table.from_pandas(pd.DataFrame({"value": [1,2]}), preserve_index=False)
    out = pa.BufferOutputStream()
    pq.write_table(table, out)
    got = pq.read_table(pa.BufferReader(out.getvalue())).to_pandas()
    verify(got["value"].tolist() == [1,2], "Parquet roundtrip failed")
    return f"pyarrow {pa.__version__}: in-memory Parquet roundtrip OK"

def duckdb_check():
    import pandas as pd
    import duckdb
    con = duckdb.connect(":memory:")
    try:
        con.register("data", pd.DataFrame({"value": [3,7]}))
        got = con.execute("SELECT SUM(value) FROM data").fetchone()[0]
        verify(got == 10, "SQL result wrong")
    finally:
        con.close()
    return f"duckdb {duckdb.__version__}: SQL on Pandas OK"

def plotly_check():
    import plotly
    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Scatter(x=[1,2], y=[3,4])])
    payload = json.loads(fig.to_json())
    verify(payload["data"][0]["type"] == "scatter", "Invalid Plotly output")
    return f"plotly {plotly.__version__}: chart serialized OK"

def matplotlib_check():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    try:
        ax.plot([1,2], [3,4])
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
        verify(buffer.getvalue().startswith(b"\x89PNG\r\n\x1a\n"), "PNG bytes invalid")
    finally:
        plt.close(fig)
    return f"matplotlib {matplotlib.__version__}: headless image rendered"

def streamlit_check():
    import streamlit as st
    from streamlit.testing.v1 import AppTest
    with tempfile.TemporaryDirectory(prefix="env-check-") as dirname:
        filename = Path(dirname) / "app.py"
        filename.write_text('import streamlit as st\nst.title("Local test")\nst.metric("Count", 3)\n',
                            encoding="utf-8")
        app = AppTest.from_file(str(filename)).run(timeout=20)
        verify(len(app.exception) == 0, "Streamlit raised an exception")
        verify(len(app.title) == 1 and app.title[0].value == "Local test", "No title")
        verify(len(app.metric) == 1, "No metric")
    return f"streamlit {st.__version__}: headless app executed OK"

def pytest_check():
    import pytest
    with tempfile.TemporaryDirectory(prefix="env-pytest-") as dirname:
        filename = Path(dirname) / "test_math.py"
        filename.write_text("import math\ndef test_distance():\n    assert math.hypot(3, 4) == 5\n")
        env = os.environ.copy()
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p",
                              "no:cacheprovider", str(filename)],
                             cwd=dirname, capture_output=True, text=True,
                             timeout=45, env=env)
        verify(run.returncode == 0 and "1 passed" in run.stdout,
               (run.stdout + run.stderr)[-600:])
    return f"pytest {pytest.__version__}: subprocess test passed"

def aws_check():
    import boto3
    client_names = boto3.session.Session().get_available_services()
    verify("bedrock-runtime" in client_names, "No Bedrock Runtime service definition")
    return f"boto3 {boto3.__version__}: offline Bedrock service definition OK"

def executable(name):
    path = shutil.which(name)
    verify(path is not None, "not on PATH")
    p = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
    verify(p.returncode == 0, f"unexpected status {p.returncode}")
    return f"{(p.stdout or p.stderr).strip().splitlines()[0]} ({path})"

def node_check():
    path = shutil.which("node")
    verify(path is not None, "Node.js absent")
    p = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
    verify(p.returncode == 0, "Cannot execute Node.js")
    version = int(p.stdout.strip().lstrip("v").split(".")[0])
    verify(version >= 20, f"Node.js >=20 required, found {p.stdout.strip()}")
    return p.stdout.strip()

def check_skills(report, agent, strict, aws):
    locations = LOCATIONS[agent]
    for name in SKILLS + (("amazon-bedrock",) if aws else ()):
        match = next((path / name / "SKILL.md" for path in locations
                      if (path / name / "SKILL.md").is_file()), None)
        if match:
            report.add("PASS", f"{agent}: {name}", f"Skill file found at {match}")
        else:
            shared = HOME / ".agents/skills" / name / "SKILL.md"
            if shared.is_file() and (HOME / ".agents/skills") not in locations:
                detail = f"Shared location {shared}; activation in {agent} NOT confirmed"
            else:
                detail = "Missing from agent-specific skill directories"
            report.add("FAIL" if strict else "WARN", f"{agent}: {name}", detail)
    report.add("WARN", f"{agent}: actual invocation",
               "Skill file presence does not verify assistant activation; manually invoke a harmless skill.")

def args_parse():
    p = argparse.ArgumentParser(description="Offline real-operation tests for an installed dev environment")
    p.add_argument("--no-skills", action="store_true", help="Skip AI skill file diagnostics")
    p.add_argument("--strict-skills", action="store_true", help="Make missing selected agent skills fatal")
    p.add_argument("--aws", action="store_true", help="Require boto3 / Bedrock service definition")
    p.add_argument("--agent", choices=tuple(LOCATIONS), action="append", help="Which coding agent to check")
    p.add_argument("--all-agents", action="store_true", help="Check all three coding agents")
    p.add_argument("--json", type=Path, metavar="FILE", help="Write an optional JSON results file")
    return p.parse_args()

def main():
    args = args_parse()
    if args.no_skills and args.strict_skills:
        print("Cannot use --no-skills and --strict-skills together", file=sys.stderr)
        return 2
    print("NFL x AWS — GENERIC ENVIRONMENT TEST (offline, no competition data)\n", flush=True)
    r = Results()
    r.check("Virtual environment / Python", runtime)
    operations = [
        ("NumPy distance", numpy_check),
        ("Pandas groupby + filter", pandas_check),
        ("SciPy spatial distance", scipy_check),
        ("scikit-learn nearest neighbors", sklearn_check),
        ("PyArrow Parquet roundtrip", arrow_check),
        ("DuckDB SQL query", duckdb_check),
        ("Plotly figure", plotly_check),
        ("Matplotlib PNG render", matplotlib_check),
        ("Streamlit AppTest", streamlit_check),
        ("pytest real execution", pytest_check),
    ]
    for label, operation in operations:
        r.check(label, operation)
    if args.aws:
        r.check("AWS SDK / Bedrock (offline)", aws_check)
    elif importlib.util.find_spec("boto3") is not None:
        r.check("Optional AWS SDK", aws_check, required=False)
    else:
        r.add("WARN", "Optional AWS SDK", "boto3 not installed (expected without --aws)")
    r.check("Git CLI", lambda: executable("git"), required=False)
    r.check("Node.js >=20", node_check, required=args.strict_skills and not args.no_skills)
    r.check("npx CLI", lambda: executable("npx"), required=args.strict_skills and not args.no_skills)
    for title, cmd in [("Kiro CLI", "kiro-cli"), ("Claude Code CLI", "claude"),
                       ("Codex CLI", "codex")]:
        if shutil.which(cmd):
            r.check(title, lambda cmd=cmd: executable(cmd), required=False)
        else:
            r.add("WARN", title, "CLI not found; desktop app may still be installed")
    if not args.no_skills:
        if args.all_agents:
            agents = list(LOCATIONS)
        elif args.agent:
            agents = list(dict.fromkeys(args.agent))
        else:
            agents = ["kiro-cli"]
            if shutil.which("claude"):
                agents.append("claude-code")
            if shutil.which("codex"):
                agents.append("codex")
        for agent in agents:
            check_skills(r, agent, strict=args.strict_skills, aws=args.aws)
    return r.finish(args.json)

if __name__ == "__main__":
    raise SystemExit(main())
