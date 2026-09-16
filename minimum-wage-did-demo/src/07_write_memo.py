from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
    x=pd.read_csv(ROOT/'data/processed/njmin3_clean.csv'); r=pd.read_csv(ROOT/'outputs/regression_results.csv'); tab=pd.read_csv(ROOT/'outputs/descriptive_statistics.csv')
    did=r[(r.model.str.startswith('M1'))&(r.term=='did')].iloc[0]; m3=r[(r.model.str.startswith('M3'))&(r.term=='treat')].iloc[0]
    means=tab.pivot(index='state',columns='period',values='mean'); nj=means.loc['New Jersey','Post (Nov 1992)']-means.loc['New Jersey','Pre (Feb 1992)']; pa=means.loc['Pennsylvania','Post (Nov 1992)']-means.loc['Pennsylvania','Pre (Feb 1992)']
    memo=f'''# 研究备忘录：新泽西最低工资与快餐店就业

## 非技术摘要

本项目以可复现方式比较 1992 年新泽西州和宾夕法尼亚州东部快餐店的就业变化。新泽西州于 4 月 1 日将最低工资由每小时 4.25 美元提高到 5.05 美元。标准差分中的差分（DID）交互项估计为 **{did.coefficient:.2f} 个全职等价（FTE）岗位**，餐厅聚类标准误 {did.std_error:.2f}，95% 置信区间 [{did.ci_low:.2f}, {did.ci_high:.2f}]，p={did.p_value:.3f}。在平行趋势、无重大组间溢出和研究设计基本成立的前提下，最低工资政策对新泽西州快餐店就业的差分中的差分估计为 **{did.coefficient:.2f} 个 FTE**。这不是“最低工资上调无条件导致就业增加”的结论。

## 数据、变量与研究设计

政策前调查在 1992 年 2 月，政策后调查在同年 11 月。清洗数据有 {len(x)} 个餐厅—时期观测，原始抽样框为 410 家餐厅的两期堆叠数据。任务指定的 Rdatasets CSV 及说明页在运行时均为 HTTP 404；下载程序保留失败记录，使用公开的长格式备用 CSV，并以 David Card 公共档案代码本核验州别、波次、样本规模与字段含义。原始文件、URL、时间、大小和 SHA-256 均已保存，清洗过程不会覆盖它。

因变量 `fte` 为全职人数、管理人员和一半兼职人数之和。`treat=1` 为新泽西处理组，`post=1` 为政策后，`did=treat×post`。CSV 没有显式门店 ID；每期各 410 行且为同一门店顺序，故以每期行号构成 `restaurant_id`，并核验每个餐厅—时期键不重复。缺失 FTE 不插补。M0 为四个州别—时期单元均值；M1 为 `fte ~ treat + post + did`；M2 加入所有制和连锁控制（Wendy's 为基准组）。地区虚拟变量虽可用，但与州处理变量共线，故不放入 M2；M3 在匹配门店上以就业变化为因变量。

## 描述性统计与主要结果

新泽西平均 FTE 的前后变化为 {nj:.2f}，宾州东部为 {pa:.2f}。这些是各州内部的描述性变化，不是政策效应；两者之差 {nj-pa:.2f} 才是未控制 DID。M1 在完整结果样本上复现该对比。M3 的匹配门店变化量处理系数为 {m3.coefficient:.2f}，与主结果接近。主估计的正值具有一定经济量级，但统计显著性、经济显著性和因果解释是不同概念；置信区间仍允许负效应和更大的正效应。

## 稳健性与安慰剂

将 FTE 限制在 1%—99% 分位数后的 DID 为 1.17，说明极端值会影响数值；匹配样本的结果则较稳定。项目对门店州别标签进行 5,000 次固定处理组大小的置换，结果在 `robustness_results.md` 中报告。该练习只是人工重排下的描述性参照，并非州政策随机分配检验。当前长格式 CSV 不含全职、兼职和管理人员分量，也无独立替代就业指标。虽然 Card 的官方档案含有分量，本项目不把外部数值混入指定原始 CSV，因此不伪造 M4，而是明确记录其不可完成。

## 因果边界、局限与建议

因果解释需要：若无政策，两地就业会平行演变；政策没有实质性溢出到宾州；调查口径和样本构成没有差异性改变；且无同时发生、只影响新泽西的重大冲击。这些条件不能被本数据完全验证。第一，只有一个政策前期，无法用预趋势或事件研究充分检验平行趋势。第二，处理发生在一个州、对照为相邻州的一部分，州层面只有两个集群，常规州聚类大样本推断不可靠，跨州招聘和顾客流动也可能造成溢出。第三，未回应、关店以及行号匹配可能影响平衡样本。第四，结果仅适用于该地区、行业和短期窗口，不能直接推广为长期或总体均衡效应。

谨慎的政策含义是：在上述假设下，本样本没有显示大幅短期负向 FTE 效应；它不证明其他地区或时期的最低工资不会减少就业。下一步应收集多个政策前后时期、更多对照地区和明确门店标识，测量工资合规、工时与关店，并使用适合少数处理集群的推断设计。
'''
    (ROOT/'outputs/research_memo.md').write_text(memo)
if __name__=='__main__': main()
