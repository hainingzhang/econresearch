# 新泽西州最低工资与快餐店就业：DID 可复现分析

本仓库包含一个可复现的研究项目：复现 Card 与 Krueger 所研究的 1992 年新泽西州最低工资上调情境，并以宾夕法尼亚州东部快餐店为比较组，使用差分中的差分（Difference-in-Differences, DID）估计短期就业变化。

项目不把估计结果表述为无条件因果结论。因果解释依赖平行趋势、有限溢出、测量与样本构成可比等假设；数据只有一个政策前时期、且只有两个地理集群，因此这些限制尤其重要。

## 主要结果

在完整结果样本中，标准 DID 模型估计的 `treat × post` 系数为 **2.75 个全职等价（FTE）岗位**（餐厅聚类标准误 1.31，95% CI [0.19, 5.31]，p = 0.035）。这表示：在研究设计假设成立时，样本中新泽西门店的就业变化相对于比较组高约 2.75 个 FTE；它不能推广为“提高最低工资必然增加就业”。完整讨论见[研究备忘录](minimum-wage-did-demo/outputs/research_memo.md)。

## 研究设计

- **处理组**：新泽西州快餐店；该州于 1992-04-01 将最低工资从每小时 4.25 美元提高至 5.05 美元。
- **比较组**：宾夕法尼亚州东部快餐店。
- **时期**：政策前（1992 年 2 月）与政策后（1992 年 11 月）。
- **结果变量**：FTE 就业，即全职员工与管理人员人数，加上兼职员工人数的一半。
- **主模型**：`fte ~ treat + post + treat:post`；交互项为 DID 估计量。

## 仓库结构

```text
.
├── minimum_wage_did_agent_task.md  # 项目任务说明
└── minimum-wage-did-demo/
    ├── data/                       # 原始和清洗后的数据
    ├── docs/                       # 数据来源、研究计划、分析规格与可复现性记录
    ├── outputs/                    # 回归表、图形、诊断、稳健性结果和研究备忘录
    ├── src/                        # 七个顺序执行的分析脚本
    ├── requirements.txt            # Python 依赖
    └── run_all.sh                  # 一键复现入口
```

## 快速开始

要求：Python 3.10+ 与 `pip`。

```bash
git clone git@github.com:hainingzhang/econresearch.git
cd econresearch/minimum-wage-did-demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash run_all.sh
```

脚本会依次下载或验证数据、清洗数据、审计数据、生成描述性统计、估计 DID 模型、运行稳健性检查，并写出研究备忘录与可复现性报告。它不会覆盖已有的非空 `data/raw/njmin3.csv`；如需有意刷新原始数据，请先删除该单个文件。

## 输出与复现

关键产物包括：

- [回归结果](minimum-wage-did-demo/outputs/regression_table.md)
- [稳健性结果](minimum-wage-did-demo/outputs/robustness_results.md)
- [数据审计](minimum-wage-did-demo/outputs/data_audit.md)
- [研究备忘录](minimum-wage-did-demo/outputs/research_memo.md)
- [可复现性报告](minimum-wage-did-demo/outputs/reproducibility_report.md)
- [描述性图片](minimum-wage-did-demo/outputs/figures)

数据下载策略、备用来源、文件哈希和获取记录见[数据来源日志](minimum-wage-did-demo/docs/data_source_log.md)。主 Rdatasets 端点曾返回 404，因此项目使用经代码本核验的备用长格式数据，并保留了这一记录。

## 局限

本项目只有一个政策前时期，无法充分检验平行趋势；处理发生在一个州，常规州聚类的大样本推断也不可靠。门店标签由每期行号构造，未回应、关店和样本构成变化可能影响匹配样本结果。结果仅适用于该地区、行业和短期政策窗口。

## 参考

Card, David, and Alan B. Krueger. 1994. “Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania.” *American Economic Review* 84 (4): 772–793.
