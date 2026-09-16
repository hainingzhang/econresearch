from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
    raw=pd.read_csv(ROOT/'data/raw/njmin3.csv'); x=pd.read_csv(ROOT/'data/processed/njmin3_clean.csv')
    dist=x.groupby(['state','period']).size().to_frame('数量').rename(index={'New Jersey':'新泽西州','Pennsylvania':'宾夕法尼亚州'},level='state').rename(index={'Pre (Feb 1992)':'政策前（1992 年 2 月）','Post (Nov 1992)':'政策后（1992 年 11 月）'},level='period').to_markdown()
    missing=x.isna().sum().sort_values(ascending=False).to_frame('缺失数').to_markdown()
    desc=x.fte.describe(percentiles=[.01,.05,.25,.5,.75,.95,.99]).to_frame('fte').rename(index={'count':'计数','mean':'均值','std':'标准差','min':'最小值','max':'最大值'}).to_markdown()
    dup=x.duplicated(['restaurant_id','post']).sum(); matched=x.groupby('restaurant_id').post.nunique().eq(2).sum(); extreme=((x.fte<0)|(x.fte>100)).sum()
    report=f'''# 数据审计\n\n- 原始观测数：{len(raw)}；清洗后观测数：{len(x)}。\n- 处理组观测（NJ）：{(x.treat==1).sum()}；对照组观测（PA）：{(x.treat==0).sum()}。\n- 重复的门店—时期键：{dup}。两个时期均有观测的匹配门店：{matched} / {x.restaurant_id.nunique()}。\n- 小于 0 或大于 100 的 FTE 值：{extreme}。这些值仅作标记，不作修改。\n\n## 州别—时期分布\n\n{dist}\n\n## 缺失值\n\n{missing}\n\n## FTE 分布\n\n{desc}\n\n## 与识别相关的观察\n\n数据是基于行顺序推导标识符的两波次门店面板。任何未匹配或结果变量缺失的观测均按模型剔除，而不作插补。政策前仅有一个时期，因而无法诊断相对预趋势。对照地区是宾夕法尼亚州东部，而非整个宾夕法尼亚州；地理溢出以及样本/构成变化仍有可能。\n'''
    (ROOT/'outputs').mkdir(exist_ok=True); (ROOT/'outputs/data_audit.md').write_text(report)
if __name__=='__main__': main()
