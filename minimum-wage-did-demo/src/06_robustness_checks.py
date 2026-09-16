from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
ROOT=Path(__file__).resolve().parents[1]
def main():
    x=pd.read_csv(ROOT/'data/processed/njmin3_clean.csv').dropna(subset=['fte']); base=smf.ols('fte ~ treat + post + did',x).fit().params.did
    q=x.fte.quantile([.01,.99]); trim=x[x.fte.between(q.iloc[0],q.iloc[1])]; trimmed=smf.ols('fte ~ treat + post + did',trim).fit().params.did
    wide=x.pivot(index='restaurant_id',columns='post',values='fte').dropna(); tr=x.drop_duplicates('restaurant_id').set_index('restaurant_id').loc[wide.index,'treat'].to_numpy(); change=wide[1].to_numpy()-wide[0].to_numpy(); observed=change[tr==1].mean()-change[tr==0].mean()
    rng=np.random.default_rng(20260916); perms=[]
    for _ in range(5000):
        z=rng.permutation(tr); perms.append(change[z==1].mean()-change[z==0].mean())
    p=(np.sum(np.abs(perms)>=abs(observed))+1)/(len(perms)+1)
    text=f'''# 稳健性与安慰剂检验\n\n| 检验 | DID / 处理组变化估计 | 细节 |\n|---|---:|---|\n| 主回归的未调整 DID | {base:.3f} | 结果变量完整的观测行 |\n| 剔除 FTE 在第 1--99 百分位数之外的观测 | {trimmed:.3f} | n={len(trim)}；敏感性检验，不是首选估计量 |\n| 匹配门店变化 DID | {observed:.3f} | n={len(wide)} 家匹配门店 |\n| 门店标签置换 | 双侧 p={p:.4f} | 5,000 次固定数量的随机分配；随机种子 20260916 |\n\n所提供的长格式 CSV 未提供就业构成（全职、兼职、管理人员）或替代的总就业结果，因此无法基于该文件诚实地估计使用替代结果变量的 M4。Card 官方档案包含这些构成，但本工作流不会将外部数值合并或重建到指定下载的原始 CSV 中。不会对缺失 FTE 作插补。\n\n置换练习评估在任意重新分配 NJ 标签时，匹配门店变化对比是否异常；由于各州并非随机接受处理，这不是基于研究设计的政策随机分配检验。仅有一个政策前时期和一个政策后时期，平行趋势仍无法检验。\n'''
    (ROOT/'outputs/robustness_results.md').write_text(text)
if __name__=='__main__': main()
