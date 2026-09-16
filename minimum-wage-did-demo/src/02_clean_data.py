from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
    raw=pd.read_csv(ROOT/'data/raw/njmin3.csv')
    raw=raw.loc[:,~raw.columns.str.lower().str.startswith('unnamed')].copy(); raw.columns=raw.columns.str.lower().str.strip()
    required={'nj','d','fte'}
    if not required.issubset(raw): raise ValueError(f'缺少必需列：{required-set(raw)}')
    for c in raw.columns: raw[c]=pd.to_numeric(raw[c],errors='coerce')
    if not set(raw.nj.dropna().unique()).issubset({0,1}) or not set(raw.d.dropna().unique()).issubset({0,1}): raise ValueError('nj/d 编码不符合预期')
    # 数据按调查波次堆叠；每个 d 内的位置是稳定的 1..410 门店键。
    raw['restaurant_id']=raw.groupby('d').cumcount()+1
    if raw.groupby('restaurant_id').size().eq(2).sum()!=raw.restaurant_id.nunique(): raise ValueError('无法建立两波次门店键')
    raw['treat']=raw['nj'].astype('Int64'); raw['post']=raw['d'].astype('Int64'); raw['did']=raw['treat']*raw['post']
    raw['state']=raw['treat'].map({1:'New Jersey',0:'Pennsylvania'}); raw['period']=raw['post'].map({0:'Pre (Feb 1992)',1:'Post (Nov 1992)'})
    raw['fte']=pd.to_numeric(raw['fte'],errors='coerce')
    # FTE 由数据来源提供：全职员工 + 管理人员 + 0.5*兼职员工；不填补任何值。
    ROOT.joinpath('data/processed').mkdir(parents=True,exist_ok=True); raw.to_csv(ROOT/'data/processed/njmin3_clean.csv',index=False)
    text='''# 数据字典\n\n备用数据 `njmin3` 为长格式（820 行 = 410 家门店 × 2 个波次）。原始 Card 公开数据代码本将 `STATE` 定义为 1=NJ、0=PA，并报告就业构成；备用数据提供了其公布的 FTE 构造方法。\n\n| 原始字段 | 分析字段 | 含义 / 规则 |\n|---|---|---|\n| `nj` | `treat`, `state` | 1 = New Jersey / 处理组；0 = Pennsylvania / 对照组 |\n| `d` | `post`, `period` | 0 = 1992 年 2 月（政策前）；1 = 1992 年 11 月（政策后） |\n| `fte` | `fte` | FTE 就业：全职员工 + 管理人员 + 0.5 × 兼职员工 |\n| `nj` × `d` | `did` | DID 交互项 |\n| `d` 内的行顺序 | `restaurant_id` | 每个堆叠波次中稳定的 1--410 位置；已核验每个门店—时期仅一个观测 |\n| `bk`, `kfc`, `roys`, `wendys` | controls | 快餐连锁品牌指示变量 |\n| `co_owned`, `centralj`, `southj`, `pa1`, `pa2` | controls | 所有制和地理指示变量 |\n\n不对缺失值进行插补。原始数据没有明确的门店标识符；仅在确认每个波次均有 410 行后，才使用有文档说明的基于行顺序的键。\n'''
    (ROOT/'docs/data_dictionary.md').write_text(text,encoding='utf-8')
if __name__=='__main__': main()
