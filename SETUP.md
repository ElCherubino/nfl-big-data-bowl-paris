# Python environment

The dependency lists, installer and offline checks were copied from the sibling
NFLxAWS_Hackathon preparation repository. This project creates its own `.venv`;
it does not reuse or modify that repository's virtual environment.

Requires Python 3.11+ and Git. Run from this repository:

```bash
./run
```

This creates the virtual environment, installs the Python stack and starts the
dashboard. The first run requires internet access. Later runs reuse the installed
environment; changing `requirements.txt` triggers installation again. The script
does not install system Python or Git. On Windows, use Git Bash or WSL.
Downloading or cloning files does not execute setup automatically.

For setup and verification without launching the dashboard:

```bash
./prepare_environnement --dry-run --no-skills
./prepare_environnement --no-skills
./prepare_environnement --check --no-skills
./test_env --no-skills
```

The installer uses pip inside `.venv`. It includes pandas, NumPy, SciPy,
scikit-learn, PyArrow, DuckDB, Plotly, Streamlit, Matplotlib, seaborn,
ipykernel and pytest. Requirements use version ranges, rather than an exact lock.
Rerunning setup reuses the local environment and satisfies those ranges.

Start the dashboard:

```bash
source .venv/bin/activate
python -m streamlit run app.py
```

On Windows Git Bash, activate with `source .venv/Scripts/activate`.
In Kiro or VS Code, select the Python interpreter inside `.venv`; select the
same environment as the notebook kernel. Activation is optional if commands use
`.venv/bin/python` explicitly.

The starter dashboard only confirms that Streamlit runs. No NFL metric or
analysis is implemented. The supplied data remains under `nfl-data/data/`.
Use `outputs/` for generated local artifacts; it is ignored by Git.

For optional AWS support, run `./prepare_environnement --no-skills --aws` and
`./test_env --no-skills --aws`. The AWS check only verifies offline SDK metadata;
it does not authenticate or call AWS. Keep credentials outside source control.

Use `--no-skills` for Python-only setup. Without it, the inherited installer
also offers global AI skill installation, which is separate from this project.

`./test_env --no-skills --json environment_report.json` saves diagnostic results.
It exercises numerical operations, Parquet, SQL, plotting, a headless Streamlit
app and pytest. Optional tool warnings do not mean the Python stack failed.
