#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data/raw data/processed docs outputs/figures src
for script in src/01_download_data.py src/02_clean_data.py src/03_audit_data.py src/04_descriptive_analysis.py src/05_did_regression.py src/06_robustness_checks.py src/07_write_memo.py; do
  echo "Running $script"; python3 "$script"
done
python3 - <<'PY'
from pathlib import Path
import platform, subprocess, datetime, hashlib, yaml
root=Path.cwd(); req=['data/raw/njmin3.csv','data/processed/njmin3_clean.csv','docs/data_source_log.md','docs/data_dictionary.md','outputs/data_audit.md','outputs/descriptive_statistics.csv','outputs/regression_results.csv','outputs/regression_table.md','outputs/model_diagnostics.md','outputs/robustness_results.md','outputs/research_memo.md']
missing=[p for p in req if not (root/p).is_file()]
if missing: raise SystemExit('缺少预期输出：'+', '.join(missing))
raw=root/'data/raw/njmin3.csv'; packages=[]
for line in (root/'requirements.txt').read_text().splitlines():
    name=line.split('>')[0].split('=')[0]
    try:
        import importlib.metadata as md; packages.append({'name':name,'version':md.version(name)})
    except Exception: packages.append({'name':name,'version':'not found'})
manifest={'数据':{'数据集':'njmin3','主_URL':'https://vincentarelbundock.github.io/Rdatasets/csv/wooldridge/njmin3.csv','备用_URL':['https://raw.githubusercontent.com/AnthonyPuggs/CardKrueger1994Replication/main/njmin3.csv','https://davidcard.berkeley.edu/data_sets/njmin.zip（代码本验证）'],'原始文件':'data/raw/njmin3.csv','格式':'csv','下载时间':__import__('json').loads((root/'docs/download_metadata.json').read_text())['downloaded_at'],'sha256':hashlib.sha256(raw.read_bytes()).hexdigest()},'软件':{'Python':platform.python_version(),'软件包':packages},'变量':{'结果变量':'fte','处理变量':'treat','政策后变量':'post','交互项':'did','个体标识':'restaurant_id'},'模型':{'类型':'difference_in_differences','公式':'fte ~ treat + post + treat:post','推断方法':'餐厅聚类协方差；未使用州聚类（仅两个州）'},'输出':req,'失败处理策略':{'重试次数':3,'使用缓存':True,'伪造数据':False}}
(root/'docs/analysis_manifest.yaml').write_text(yaml.safe_dump(manifest,sort_keys=False,allow_unicode=True))
n=len(__import__('pandas').read_csv(root/'data/processed/njmin3_clean.csv'))
report=f'''# 可复现性报告\n\n- 执行时间（UTC）：{datetime.datetime.now(datetime.timezone.utc).isoformat()}\n- Python：{platform.python_version()}\n- 最终清洗样本：{n} 个门店—波次观测\n- 脚本状态：全部七个分析脚本均已成功完成。\n- 原始数据 SHA-256：{manifest['数据']['sha256']}\n- 原始数据策略：保留现有非空原始文件；未伪造数据；未插补缺失结果变量。\n\n## 依赖项\n\n'''+ '\n'.join(f"- {p['name']}：{p['version']}" for p in packages)+'\n'
(root/'docs/reproducibility_report.md').write_text(report); (root/'outputs/reproducibility_report.md').write_text(report)
PY
