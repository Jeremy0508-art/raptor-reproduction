# RAPTOR Reproduction Notes

This workspace uses Python 3.12 on Windows, so install the compatibility
constraints instead of the original `requirements.txt`.

```powershell
cd D:\Research\raptor
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-py312.txt
```

Run an offline smoke test with the bundled Cinderella tree:

```powershell
.\.venv\Scripts\python.exe examples\offline_smoke.py
```

Run a fully offline structural reproduction that rebuilds a tree without OpenAI:

```powershell
.\.venv\Scripts\python.exe examples\reproduce_cinderella_offline.py
```

This uses deterministic local embeddings and extractive summaries, so it checks
the RAPTOR pipeline mechanics rather than matching paper-level answer quality.
It saves the rebuilt tree to `demo/cinderella_offline_reproduced`.

Verify that the saved offline tree can be loaded and queried:

```powershell
.\.venv\Scripts\python.exe examples\reproduce_cinderella_offline.py --load-existing
```

Run the OpenAI-backed reproduction path:

```powershell
$env:OPENAI_API_KEY = "your-openai-api-key"
.\.venv\Scripts\python.exe examples\reproduce_cinderella_openai.py
```

If the full reproduction fails, run the lightweight OpenAI access check first:

```powershell
.\.venv\Scripts\python.exe examples\reproduce_cinderella_openai.py --check-openai
```

If the output mentions `insufficient_quota` or quota/billing credit, the code is
working but the OpenAI project tied to that API key does not currently have
usable API credit.

The OpenAI-backed script reads `demo/sample.txt`, rebuilds a RAPTOR tree,
answers the Cinderella question, and saves the reproduced tree to
`demo/cinderella_reproduced`.

By default the script uses `gpt-4o-mini` for summarization and QA because the
original `gpt-3.5-turbo` default is now a legacy model. To force another chat
model:

```powershell
$env:OPENAI_CHAT_MODEL = "gpt-3.5-turbo"
```

Run the same reproduction against an OpenAI-compatible provider:

```powershell
$env:COMPAT_API_KEY = "your-provider-api-key"
$env:COMPAT_BASE_URL = "https://provider.example.com/v1"
$env:COMPAT_CHAT_MODEL = "provider-chat-model"
$env:COMPAT_EMBEDDING_MODEL = "provider-embedding-model"
.\.venv\Scripts\python.exe examples\reproduce_cinderella_compatible_api.py --check-api
.\.venv\Scripts\python.exe examples\reproduce_cinderella_compatible_api.py
```

If the embedding model supports custom output dimensions, set:

```powershell
$env:COMPAT_EMBEDDING_DIMENSIONS = "1024"
```

The compatible API script passes this value through the SDK's `extra_body`
argument because this workspace uses `openai==1.3.3`, whose embeddings helper
does not expose `dimensions` as a direct keyword argument.

Example provider configurations:

```powershell
# Alibaba Cloud Model Studio / DashScope OpenAI-compatible mode
$env:COMPAT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:COMPAT_CHAT_MODEL = "qwen-turbo"
$env:COMPAT_EMBEDDING_MODEL = "text-embedding-v4"

# SiliconFlow
$env:COMPAT_BASE_URL = "https://api.siliconflow.com/v1"
$env:COMPAT_CHAT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
$env:COMPAT_EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"
$env:COMPAT_EMBEDDING_DIMENSIONS = "1024"

# Zhipu AI
$env:COMPAT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
$env:COMPAT_CHAT_MODEL = "glm-4-flash"
$env:COMPAT_EMBEDDING_MODEL = "embedding-3"
$env:COMPAT_EMBEDDING_DIMENSIONS = "1024"
```

Current workspace status:

- Python 3.12 virtual environment exists at `.venv`.
- `pip check` reports no broken package requirements.
- `examples/offline_smoke.py` successfully loads `demo/cinderella` and retrieves
  context without calling OpenAI.
- `examples/reproduce_cinderella_offline.py` successfully rebuilds and saves
  `demo/cinderella_offline_reproduced`.
- `examples/reproduce_cinderella_compatible_api.py` successfully rebuilt and
  saved `demo/cinderella_compatible_api_reproduced` using an
  OpenAI-compatible provider.
- The OpenAI-backed rebuild is blocked by `insufficient_quota` for the current
  API project, not by a local code or dependency failure.

See `RESULTS.md` for the final reproduction summary and `REPORT_ZH.md` for a
Chinese experiment report draft.
