# Codex 任务：用差分中的差分方法评估最低工资政策

## 0. 任务性质

你是一名经济学研究助理。请在当前目录创建一个完整、可复现、可审计的实证研究项目，而不是只回答一个回归系数。

本任务的目标是展示智能体如何自主完成：

1. 理解研究问题与因果识别策略；
2. 获取并保存原始数据；
3. 检查数据字典、数据格式和数据质量；
4. 构造差分中的差分变量；
5. 估计回归模型并进行可视化；
6. 进行稳健性和安慰剂检验；
7. 生成研究报告、数据说明和可复现性记录。

## 1. 研究问题

**1992 年新泽西州最低工资上调，是否改变了快餐店的就业规模？**

新泽西州将最低工资从每小时 4.25 美元提高到 5.05 美元。研究使用新泽西州作为处理组，使用宾夕法尼亚州东部快餐店作为对照组，比较政策前后两组快餐店就业变化的差异。

最终必须把结论表述为：

> 在平行趋势、无重大组间溢出和研究设计基本成立的前提下，最低工资政策对新泽西州快餐店就业的差分中的差分估计为……

不得无条件地写成“最低工资上调导致了就业增加/减少”。

## 2. 数据来源

### 2.1 主数据源

使用 Wooldridge 经济学教学数据集中的 `njmin3` 数据。该数据来自 Card and Krueger 的最低工资研究，包含新泽西州和宾夕法尼亚州快餐店在政策前后的调查信息。

优先使用 Rdatasets 的 CSV 镜像：

```text
https://vincentarelbundock.github.io/Rdatasets/csv/wooldridge/njmin3.csv
```

对应的数据说明页面：

```text
https://vincentarelbundock.github.io/Rdatasets/doc/wooldridge/njmin3.html
```

备用来源为 Wooldridge 官方 R 数据包：

```text
https://cran.r-project.org/package=wooldridge
https://github.com/JustinMShea/wooldridge
```

### 2.2 数据获取要求

1. 编写 `src/01_download_data.py`。
2. 优先从主 CSV 地址下载，并将原始文件保存为：

   ```text
   data/raw/njmin3.csv
   ```

3. 下载后记录：URL、下载时间、HTTP 状态、文件大小和 SHA-256 哈希值。
4. 如果主 URL 失败，按以下顺序处理：

   - 重试 3 次，每次间隔逐渐增加；
   - 检查本地是否已经存在非空缓存文件；
   - 尝试备用来源；
   - 验证备用文件是否包含 `njmin3` 数据和必要变量；
   - 如果所有来源失败，停止后续分析并将错误写入 `outputs/reproducibility_report.md`。

5. 严禁用编造数据、随机生成数据或自行填写缺失数据来替代下载失败的数据。

## 3. 变量与数据格式

### 3.1 数据结构

- 文件格式：CSV；
- 每一行：一家快餐店在一个调查时点的观测；
- 面板维度：餐厅 × 时间；
- 预期时间点：政策前和政策后两期；
- 研究对象：新泽西州和宾夕法尼亚州东部的快餐店。

Codex 必须先读取数据列名和数据说明，再决定具体变量映射，不得仅凭变量名猜测含义。

### 3.2 必须识别或构造的变量

| 变量 | 含义 | 类型 | 要求 |
|---|---|---|---|
| `fte` | 全职等价就业人数 | 数值型 | 作为主要因变量；若原始数据没有该列，依据数据说明构造 |
| `treat` | 是否属于新泽西州处理组 | 0/1 | 新泽西州为 1，宾夕法尼亚州为 0 |
| `post` | 是否为政策后调查 | 0/1 | 政策后为 1，政策前为 0 |
| `did` | DID 交互项 | 0/1 | `treat * post` |
| `restaurant_id` | 餐厅标识 | 标识变量 | 若原始数据没有明确 ID，构造稳定的行级餐厅标识并记录方法 |
| `state` | 州别 | 分类变量 | 必须说明编码规则 |
| `period` | 调查时期 | 分类变量 | 必须说明政策前后编码规则 |

如果原始数据中的变量名称与上表不同，必须在 `docs/data_dictionary.md` 中建立“原始变量名—分析变量名”映射表。

## 4. 研究设计与识别策略

### 4.1 核心 DID 模型

估计：

\[
fte_{it} = \alpha + \beta Treat_i + \gamma Post_t +
\delta(Treat_i \times Post_t) + \varepsilon_{it}
\]

其中：

- `fte` 是快餐店全职等价就业人数；
- `Treat` 表示新泽西州；
- `Post` 表示政策后；
- `Treat × Post` 是核心交互项；
- `δ` 是 DID 估计量。

### 4.2 必须估计的模型

- M0：直接比较两州政策前后的组均值；
- M1：标准 DID 回归；
- M2：DID + 餐厅层面的可用控制变量；
- M3：以就业变化量为因变量的等价变化量回归或组均值 DID；
- M4：稳健性模型，使用替代就业指标（如果数据提供，如总就业或兼职就业）。

标准误处理必须根据实际数据结构选择并说明。由于本案例只有两个州，不能机械地声称“按州聚类标准误具有可靠的大样本性质”。如果餐厅 ID 在两个时期可匹配，可以考虑餐厅层面的聚类或采用随机化推断/置换检验，并在报告中解释限制。

## 5. 工作流程

### 阶段一：研究计划

生成 `docs/research_plan.md`，包括：

- 研究问题；
- 处理组和对照组；
- 政策时间；
- 因变量和解释变量；
- DID 模型；
- 因果解释所依赖的假设；
- 预期局限。

### 阶段二：数据采集

生成 `src/01_download_data.py`，保存原始数据，不得覆盖原始文件。生成 `docs/data_source_log.md`，至少包括：

- 数据集名称；
- 数据来源；
- 具体下载地址；
- 下载时间；
- 数据格式；
- 原始文件大小；
- SHA-256 哈希值；
- 下载失败与备用来源记录。

### 阶段三：数据清洗与变量构造

生成 `src/02_clean_data.py`，完成：

- 读取原始 CSV；
- 清理多余索引列；
- 检查列名、类型和编码；
- 识别州别和调查时期；
- 构造 `treat`、`post`、`did`；
- 构造或核验 `fte`；
- 检查餐厅—时期键；
- 保存 `data/processed/njmin3_clean.csv`。

任何变量映射或异常处理都必须记录，不能只在代码中隐含处理。

### 阶段四：数据审计

生成 `src/03_audit_data.py`，输出 `outputs/data_audit.md`，包括：

- 原始和清洗后观测数；
- 州别和时期的样本分布；
- 重复餐厅—时期记录；
- 缺失值表；
- `fte` 的均值、标准差、最小值、最大值和分位数；
- 不合理值和极端值；
- 处理组与对照组的样本数量；
- 可否匹配同一家餐厅的前后两期数据；
- 可能影响识别的样本问题。

审计发现的问题必须在报告中明确写出，即使 Codex 认为它们“不影响结果”。

### 阶段五：描述性分析

生成 `src/04_descriptive_analysis.py`，输出：

- 政策前后两州平均就业表；
- 两州就业均值变化图；
- 处理组与对照组变化量对比图；
- 如果数据结构允许，餐厅层面的前后变化散点图。

图表保存到 `outputs/figures/`，并在图中标注单位、州别、时期和样本量。

### 阶段六：DID 回归

生成 `src/05_did_regression.py`，输出：

- `outputs/regression_results.csv`；
- `outputs/regression_table.md`；
- `outputs/model_diagnostics.md`。

回归结果至少包括：

- 系数；
- 标准误；
- t 值或 z 值；
- p 值；
- 95% 置信区间；
- 样本量；
- 处理组和对照组样本量；
- 核心交互项的解释。

### 阶段七：稳健性与安慰剂检验

生成 `src/06_robustness_checks.py`，至少完成：

1. 使用替代就业指标（若数据提供）；
2. 使用就业变化量直接计算 DID；
3. 对餐厅进行异常值敏感性分析；
4. 进行州别或处理标签的随机置换检验；
5. 讨论只有一个政策前期和一个政策后期时，平行趋势无法被充分检验的问题。

如果某项检验因数据结构无法完成，必须说明原因，不得伪造检验结果。

### 阶段八：研究报告

生成 `outputs/research_memo.md`，建议 1,200–1,800 字，包含：

1. 非技术摘要；
2. 政策背景与研究问题；
3. 数据来源和变量；
4. DID 识别策略；
5. 描述性统计；
6. 主要回归结果；
7. 稳健性分析；
8. 因果解释及其假设；
9. 至少三项局限；
10. 对政策含义的谨慎说明；
11. 下一步研究建议。

报告必须明确区分：

- 组均值差异；
- DID 估计结果；
- 统计显著性；
- 经济显著性；
- 因果解释所需的额外假设。

## 6. 项目目录结构

```text
minimum-wage-did-demo/
├── README.md
├── requirements.txt
├── run_all.sh
├── docs/
│   ├── research_plan.md
│   ├── data_source_log.md
│   ├── data_dictionary.md
│   ├── analysis_spec.md
│   └── reproducibility_report.md
├── data/
│   ├── raw/
│   │   └── njmin3.csv
│   └── processed/
│       └── njmin3_clean.csv
├── src/
│   ├── 01_download_data.py
│   ├── 02_clean_data.py
│   ├── 03_audit_data.py
│   ├── 04_descriptive_analysis.py
│   ├── 05_did_regression.py
│   └── 06_robustness_checks.py
└── outputs/
    ├── figures/
    ├── data_audit.md
    ├── descriptive_statistics.csv
    ├── regression_results.csv
    ├── regression_table.md
    ├── model_diagnostics.md
    ├── robustness_results.md
    ├── research_memo.md
    └── reproducibility_report.md
```

## 7. 必须生成的元数据

除分析结果外，必须生成 `docs/analysis_manifest.yaml`，内容至少包括：

```yaml
data:
  dataset: njmin3
  primary_url: https://vincentarelbundock.github.io/Rdatasets/csv/wooldridge/njmin3.csv
  fallback_urls: []
  raw_file: data/raw/njmin3.csv
  format: csv
  downloaded_at: ""
  sha256: ""

software:
  python: ""
  packages: []

variables:
  outcome: fte
  treatment: treat
  post: post
  interaction: did
  unit_id: restaurant_id

model:
  type: difference_in_differences
  formula: "fte ~ treat + post + treat:post"
  inference_method: ""

outputs: []

failure_policy:
  retries: 3
  use_cache: true
  fabricate_data: false
```

其中所有空字段都必须由 Codex 在执行后填充。`fabricate_data` 必须保持为 `false`。

## 8. 软件依赖

优先使用 Python，生成 `requirements.txt`，至少包含：

```text
pandas
numpy
requests
matplotlib
seaborn
statsmodels
scipy
pyyaml
```

如果实际使用了其他包，也必须写入 `requirements.txt`，并在 `README.md` 中说明版本和安装命令。

## 9. 一键运行与验收

生成 `run_all.sh`，依次执行所有脚本。脚本必须：

- 在任一阶段失败时停止；
- 对输入文件和输出文件做基本检查；
- 不覆盖 `data/raw/` 中已有的原始文件；
- 最后检查所有预期输出是否存在；
- 在 `docs/reproducibility_report.md` 中记录执行时间、Python 版本、依赖版本、脚本状态和最终样本量。

README 必须提供从空目录开始的命令，例如：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash run_all.sh
```

## 10. 给 Codex 的最终执行指令

请严格按照本文件创建并完成 `minimum-wage-did-demo/` 项目。

执行时遵守以下规则：

1. 先检查当前目录和网络状态，再创建项目文件；
2. 先读取数据说明，再决定原始变量到分析变量的映射；
3. 每完成一个阶段都检查输出，不要把错误留到最后；
4. 所有外部数据都要保存原始文件、来源 URL、下载时间和哈希值；
5. 不能使用编造数据替代下载失败；
6. 不能把 DID 估计自动解释为无条件的因果效应；
7. 如果某项识别假设无法检验，必须明确写出；
8. 如果数据结构与任务说明不一致，先记录差异，再采用有依据的适配方案；
9. 最终运行 `bash run_all.sh`，确认项目可复现；
10. 最终回复中报告：项目目录、数据来源、最终样本量、变量映射、使用的软件依赖、DID 核心估计值、稳健性结果、生成的主要文件和仍然存在的识别限制。

本任务的成功标准不是“得到一个显著的系数”，而是生成一个数据来源明确、过程可追溯、结果可复现、因果解释边界清晰的完整研究项目。
