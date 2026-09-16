from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
ROOT=Path(__file__).resolve().parents[1]
def main():
    x=pd.read_csv(ROOT/'data/processed/njmin3_clean.csv'); out=ROOT/'outputs'; fig=out/'figures'; fig.mkdir(parents=True,exist_ok=True)
    tab=x.groupby(['state','period'],observed=True).fte.agg(['count','mean','std']).reset_index(); tab.to_csv(out/'descriptive_statistics.csv',index=False)
    order=['Pre (Feb 1992)','Post (Nov 1992)']; sns.set_theme(style='whitegrid'); plt.rcParams['font.sans-serif']=['Noto Sans CJK SC']; plt.rcParams['axes.unicode_minus']=False
    display_tab=tab.assign(period_cn=pd.Categorical(tab.period.map({'Pre (Feb 1992)':'政策前（1992 年 2 月）','Post (Nov 1992)':'政策后（1992 年 11 月）'}),categories=['政策前（1992 年 2 月）','政策后（1992 年 11 月）'],ordered=True),state_cn=tab.state.map({'New Jersey':'新泽西州','Pennsylvania':'宾夕法尼亚州'}))
    ax=sns.lineplot(data=display_tab,x='period_cn',y='mean',hue='state_cn',marker='o',sort=False); ax.set(xlabel='调查时期',ylabel='平均 FTE 就业（人）',title='各州和时期的快餐店平均就业'); ax.legend(title='州别'); plt.tight_layout(); plt.savefig(fig/'mean_fte_by_state_period.png',dpi=180); plt.close()
    changes=tab.pivot(index='state',columns='period',values='mean'); changes['change']=changes[order[1]]-changes[order[0]]; changes.index=changes.index.map({'New Jersey':'新泽西州','Pennsylvania':'宾夕法尼亚州'}); ax=changes['change'].sort_values().plot.bar(color=['#4c78a8','#f58518']); ax.set(xlabel='州别',ylabel='平均 FTE 就业变化（人）',title='平均就业从政策前到政策后的变化'); plt.tight_layout(); plt.savefig(fig/'mean_fte_change_by_state.png',dpi=180); plt.close()
    wide=x.pivot(index='restaurant_id',columns='post',values='fte').dropna(); groups=x.drop_duplicates('restaurant_id').set_index('restaurant_id').treat; p=pd.DataFrame({'pre':wide[0],'post':wide[1],'state':groups.loc[wide.index].map({1:'新泽西州',0:'宾夕法尼亚州'})}); ax=sns.scatterplot(data=p,x='pre',y='post',hue='state',alpha=.65); lim=[min(p.pre.min(),p.post.min()),max(p.pre.max(),p.post.max())]; ax.plot(lim,lim,'k--',lw=1); ax.set(xlabel='政策前 FTE',ylabel='政策后 FTE',title=f'匹配门店的 FTE（n={len(p)}）'); ax.legend(title='州别'); plt.tight_layout(); plt.savefig(fig/'matched_store_fte_scatter.png',dpi=180); plt.close()
if __name__=='__main__': main()
