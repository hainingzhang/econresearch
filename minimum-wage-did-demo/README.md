# 最低工资 DID 示例

这是对 Card--Krueger 新泽西最低工资研究设计的可复现实验，主要演示如何用AI来进行经济学研究。程序会先尝试指定的 Rdatasets URL。项目生成时该链接返回 HTTP 404，因此下载程序会记录失败，并使用带版本的长格式备用数据 `njmin3.csv`。变量含义及其 410 家门店、两个调查波次的结构均已根据 David Card 的公开档案和代码本核验；详见 `docs/data_source_log.md`。

请在本目录运行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash run_all.sh
```

`run_all.sh` 不会覆盖现有的非空 `data/raw/njmin3.csv`。如需有意刷新数据，请自行删除该单个文件后重新运行。结果是有条件的 DID 估计，而非无条件的因果主张。
