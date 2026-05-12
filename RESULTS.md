# RAPTOR Reproduction Results

Date: 2026-05-11

Chinese report draft: `REPORT_ZH.md`

## Summary

The RAPTOR repository was reproduced on Windows with Python 3.12. The original
OpenAI-backed rebuild path is blocked by the API project's quota:

```text
Error code: 429
code: insufficient_quota
```

To keep the experiment moving without paid OpenAI access, the workspace includes
a fully offline structural reproduction. The experiment was then completed with
an OpenAI-compatible domestic provider path using Alibaba Cloud Model Studio /
DashScope-compatible API settings.

## Completed

- Installed Python 3.12-compatible dependencies from `requirements-py312.txt`.
- Verified the Python environment with `pip check`.
- Loaded the bundled `demo/cinderella` tree and retrieved context offline.
- Rebuilt a Cinderella RAPTOR tree fully offline from `demo/sample.txt`.
- Saved the offline reproduced tree to `demo/cinderella_offline_reproduced`.
- Reloaded the saved offline tree and retrieved context from it.
- Rebuilt a Cinderella RAPTOR tree with an OpenAI-compatible API provider.
- Saved the compatible API tree to `demo/cinderella_compatible_api_reproduced`.
- Verified the compatible API tree can be deserialized and inspected locally.

## Artifacts

- `requirements-py312.txt`: Windows/Python 3.12 dependency constraints.
- `examples/offline_smoke.py`: Loads and queries the bundled tree without API
  access.
- `examples/reproduce_cinderella_offline.py`: Rebuilds and verifies a tree
  without OpenAI.
- `examples/reproduce_cinderella_openai.py`: OpenAI-backed path with a lightweight
  `--check-openai` quota/access check.
- `examples/reproduce_cinderella_compatible_api.py`: OpenAI-compatible provider
  path for domestic or alternative APIs that provide chat and embedding
  endpoints.
- `demo/cinderella_offline_reproduced`: Generated offline reproduction tree.
- `demo/cinderella_compatible_api_reproduced`: Generated compatible API
  reproduction tree.

## Verification Commands

```powershell
cd D:\Research\raptor
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe examples\offline_smoke.py
.\.venv\Scripts\python.exe examples\reproduce_cinderella_offline.py
.\.venv\Scripts\python.exe examples\reproduce_cinderella_offline.py --load-existing
Test-Path demo\cinderella_offline_reproduced
Test-Path demo\cinderella_compatible_api_reproduced
```

Compatible API artifact inspection:

```text
Tree type: Tree
num_layers: 1
all_nodes: 41
leaf_nodes: 35
root_nodes: 6
layers: {0: 35, 1: 6}
embedding_keys: ['EMB']
embedding_dim: 1024
```

## Limitation

The OpenAI-backed reproduction cannot complete until the API key's project has
usable quota or billing credit. Once quota is available, run:

```powershell
$env:OPENAI_API_KEY = "your-openai-api-key"
.\.venv\Scripts\python.exe examples\reproduce_cinderella_openai.py --check-openai
.\.venv\Scripts\python.exe examples\reproduce_cinderella_openai.py
```

The successful alternative path uses an OpenAI-compatible provider by setting
`COMPAT_API_KEY`, `COMPAT_BASE_URL`, `COMPAT_CHAT_MODEL`, and
`COMPAT_EMBEDDING_MODEL`, then run:

```powershell
.\.venv\Scripts\python.exe examples\reproduce_cinderella_compatible_api.py --check-api
.\.venv\Scripts\python.exe examples\reproduce_cinderella_compatible_api.py
```
