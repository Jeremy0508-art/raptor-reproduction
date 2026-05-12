# RAPTOR/RAG 项目复现实验报告

## 1. 实验目标

本实验目标是在 Windows 与 Python 3.12 环境下复现 RAPTOR
（Recursive Abstractive Processing for Tree-Organized Retrieval）的基本流程，
并验证其在 RAG 场景中的树状索引构建、检索和问答链路。

原仓库默认依赖 OpenAI API 完成 embedding、摘要和问答。由于当前 OpenAI API key
所属项目返回 `insufficient_quota`，无法继续执行 OpenAI 官方 API 的完整复现。
因此，本实验采用三条路径：

1. 使用仓库自带的 `demo/cinderella` tree 进行离线检索验证。
2. 使用本地确定性 embedding 与抽取式摘要模型完成无 API 的结构性复现。
3. 使用阿里云百炼 DashScope 的 OpenAI 兼容接口完成 API-backed 复现。

## 2. 实验环境

- 操作系统：Windows
- Python 版本：Python 3.12.7
- 项目目录：`D:\Research\raptor`
- 依赖文件：`requirements-py312.txt`
- 虚拟环境：`.venv`

原始 `requirements.txt` 中的部分依赖版本不适配 Python 3.12，例如
`tiktoken==0.5.1` 在 Windows/Python 3.12 下缺少合适 wheel。为此新增
`requirements-py312.txt` 作为兼容依赖约束。

另外，`umap-learn==0.5.5` 与较新的 `scikit-learn==1.8.0` 存在接口不兼容，
会触发：

```text
TypeError: check_array() got an unexpected keyword argument 'force_all_finite'
```

因此将 `scikit-learn` 固定为 `1.5.2`，并通过 `pip check` 验证依赖一致性。

## 3. 复现方法

### 3.1 环境安装

```powershell
cd D:\Research\raptor
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-py312.txt
```

验证依赖：

```powershell
.\.venv\Scripts\python.exe -m pip check
```

结果为：

```text
No broken requirements found.
```

### 3.2 离线 smoke test

运行：

```powershell
.\.venv\Scripts\python.exe examples\offline_smoke.py
```

该脚本加载仓库自带的 `demo/cinderella` tree，使用确定性 embedding 替代
OpenAI embedding，并执行检索。

运行结果显示：

```text
Loaded demo/cinderella and retrieved context successfully.
```

说明本地环境可以正确加载 RAPTOR tree，并完成检索流程。

### 3.3 离线结构性复现

运行：

```powershell
.\.venv\Scripts\python.exe examples\reproduce_cinderella_offline.py
```

该脚本从 `demo/sample.txt` 读取 Cinderella 文本，并使用：

- `DeterministicEmbeddingModel`：基于 SHA-256 的确定性本地 embedding；
- `ExtractiveSummarizationModel`：抽取前若干词作为本地摘要；
- `ContextPreviewQAModel`：返回检索到的上下文片段作为问答预览。

该流程不依赖 OpenAI API，主要用于验证 RAPTOR 的结构性流程：

1. 文档读取；
2. 文本分块；
3. leaf node 创建；
4. 聚类；
5. 上层摘要 node 构建；
6. tree 保存；
7. 检索与上下文返回。

输出产物为：

```text
demo/cinderella_offline_reproduced
```

### 3.5 国内 OpenAI 兼容 API 复现

由于 OpenAI 官方 API 无法充值，本实验改用阿里云百炼 DashScope 的
OpenAI-compatible 接口。配置方式如下：

```powershell
$env:COMPAT_API_KEY = "your-provider-api-key"
$env:COMPAT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
$env:COMPAT_CHAT_MODEL = "qwen-turbo"
$env:COMPAT_EMBEDDING_MODEL = "text-embedding-v4"
$env:COMPAT_EMBEDDING_DIMENSIONS = "1024"
```

先执行预检：

```powershell
.\.venv\Scripts\python.exe examples\reproduce_cinderella_compatible_api.py --check-api
```

预检成功后执行完整复现：

```powershell
.\.venv\Scripts\python.exe examples\reproduce_cinderella_compatible_api.py
```

最终生成：

```text
demo/cinderella_compatible_api_reproduced
```

该产物已经被反序列化检查，结构如下：

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

这说明国内兼容 API 路径已经完成从文本输入、embedding、摘要建树到 tree 保存的
完整流程。

### 3.4 保存产物加载验证

运行：

```powershell
.\.venv\Scripts\python.exe examples\reproduce_cinderella_offline.py --load-existing
```

该命令重新加载 `demo/cinderella_offline_reproduced`，并再次执行检索。结果显示
保存后的离线 tree 可以被正常读取和查询。

## 4. OpenAI-backed 路径受限说明

原始 OpenAI-backed 复现命令为：

```powershell
$env:OPENAI_API_KEY = "your-openai-api-key"
.\.venv\Scripts\python.exe examples\reproduce_cinderella_openai.py
```

为了减少不必要的 API 消耗，新增了预检命令：

```powershell
.\.venv\Scripts\python.exe examples\reproduce_cinderella_openai.py --check-openai
```

当前返回错误：

```text
Error code: 429
code: insufficient_quota
You exceeded your current quota
```

这说明 OpenAI-backed 复现失败原因是 API 项目额度不足，而不是本地代码、
依赖安装或 RAPTOR 流程错误。

## 5. 实验结果

本实验已完成以下内容：

- 成功配置 Windows/Python 3.12 下的 RAPTOR 运行环境；
- 修复 Python 3.12 依赖兼容问题；
- 成功加载并检索仓库自带 Cinderella tree；
- 成功从 `demo/sample.txt` 离线重建 Cinderella RAPTOR tree；
- 成功保存并重新加载 `demo/cinderella_offline_reproduced`；
- 明确记录 OpenAI 官方 API-backed 复现受限原因；
- 成功使用阿里云百炼 OpenAI 兼容接口重建 Cinderella RAPTOR tree；
- 成功生成 `demo/cinderella_compatible_api_reproduced`。

当前生成的关键文件包括：

- `requirements-py312.txt`
- `REPRODUCE.md`
- `RESULTS.md`
- `examples/offline_smoke.py`
- `examples/reproduce_cinderella_offline.py`
- `examples/reproduce_cinderella_openai.py`
- `examples/reproduce_cinderella_compatible_api.py`
- `demo/cinderella_offline_reproduced`
- `demo/cinderella_compatible_api_reproduced`

## 6. 局限性

离线结构性复现使用的是确定性 embedding 与抽取式摘要，并不等价于原论文中使用
OpenAI 模型得到的语义 embedding、抽象摘要和最终问答质量。因此，离线路径主要
验证 RAPTOR 的工程流程与数据结构。

兼容 API 路径已经使用真实在线 embedding 和 chat 模型完成复现，但模型供应商和
具体模型与原论文设置不同，因此结果不应视为完全等价于 OpenAI 原始设置。

若后续获得可用 OpenAI API 额度，可继续运行 OpenAI-backed 脚本以完成更接近原始
设置的复现。

另外，如果无法充值 OpenAI API，也可以尝试使用国内或其他提供 OpenAI 兼容接口的
模型平台。项目中新增了 `examples/reproduce_cinderella_compatible_api.py`，
该脚本通过环境变量配置 API key、base URL、聊天模型和 embedding 模型。只要目标
平台同时支持 chat completions 与 embeddings 接口，就可以用于 RAPTOR 的完整
API-backed 管线复现。

## 7. 结论

在没有可用 OpenAI 官方 API 额度的情况下，本实验先完成了 RAPTOR/RAG 项目的本地
结构性复现，随后通过阿里云百炼 OpenAI 兼容接口完成了 API-backed 复现。实验验证
了 RAPTOR 从文档输入到树状索引构建、检索、保存和产物检查的完整流程。OpenAI
官方版本目前受外部 API quota 限制，待额度恢复后可继续补充。
