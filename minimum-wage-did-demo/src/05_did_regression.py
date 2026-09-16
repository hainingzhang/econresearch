from pathlib import Path
import pandas as pd
import statsmodels.formula.api as smf
ROOT=Path(__file__).resolve().parents[1]
def rows(name,res):
    ci=res.conf_int(); a=[]
    for v in res.params.index: a.append({'model':name,'term':v,'coefficient':res.params[v],'std_error':res.bse[v],'statistic':res.tvalues[v],'p_value':res.pvalues[v],'ci_low':ci.loc[v,0],'ci_high':ci.loc[v,1],'nobs':int(res.nobs)})
    return a
def main():
    x=pd.read_csv(ROOT/'data/processed/njmin3_clean.csv').dropna(subset=['fte']); f='fte ~ treat + post + did'; m1=smf.ols(f,x).fit(cov_type='cluster',cov_kwds={'groups':x.restaurant_id})
    # 省略 Wendy's。地理虚拟变量不纳入模型：在此数据中，它们与州处理变量共线。
    controls=[c for c in ['co_owned','bk','kfc','roys'] if c in x]
    m2=smf.ols(f+' + '+' + '.join(controls),x).fit(cov_type='cluster',cov_kwds={'groups':x.restaurant_id})
    wide=x.pivot(index='restaurant_id',columns='post',values='fte').dropna(); treat=x.drop_duplicates('restaurant_id').set_index('restaurant_id').loc[wide.index,'treat']; change=pd.DataFrame({'change':wide[1]-wide[0],'treat':treat}); m3=smf.ols('change ~ treat',change).fit(cov_type='HC1')
    allrows=rows('M1 standard DID (restaurant-clustered)',m1)+rows('M2 DID + controls (restaurant-clustered)',m2)+rows('M3 matched change (HC1)',m3); pd.DataFrame(allrows).to_csv(ROOT/'outputs/regression_results.csv',index=False)
    focus=pd.DataFrame(allrows); focus=focus[focus.term.isin(['did','treat'])][['model','term','coefficient','std_error','p_value','ci_low','ci_high','nobs']]
    focus=focus.rename(columns={'model':'模型','term':'项','coefficient':'系数','std_error':'标准误','p_value':'p 值','ci_low':'置信区间下限','ci_high':'置信区间上限','nobs':'观测数'}).replace({'M1 standard DID (restaurant-clustered)':'M1 标准 DID（餐厅聚类）','M2 DID + controls (restaurant-clustered)':'M2 DID + 控制变量（餐厅聚类）','M3 matched change (HC1)':'M3 匹配变化（HC1）'})
    (ROOT/'outputs/regression_table.md').write_text('# 回归结果\n\n'+focus.to_markdown(index=False,floatfmt='.3f')+f'\n\nM1 使用 {len(x)} 行结果变量完整的观测；NJ 和 PA 观测数分别为 {(x.treat==1).sum()} 和 {(x.treat==0).sum()}。`did` 系数是 NJ 与 PA 平均变化之差。M3 是等价的平衡面板变化回归。\n')
    did=m1.params['did']; (ROOT/'outputs/model_diagnostics.md').write_text(f'''# 模型诊断\n\nM1 公式：`{f}`。残差自由度：{m1.df_resid:.0f}；R 平方：{m1.rsquared:.3f}。餐厅聚类协方差考虑了门店内相关性，因为排序键可匹配两个波次。它**不能**解决核心的小集群问题：仅有两个州，因此州聚类的大样本推断不可靠，未予报告。交互项估计为 {did:.3f} 名 FTE 员工；应在研究计划所述的 DID 假设条件下解释。\n''')
if __name__=='__main__': main()
