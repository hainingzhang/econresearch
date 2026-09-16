# 数据来源日志

- **dataset**: `njmin3`
- **primary_url**: `https://vincentarelbundock.github.io/Rdatasets/csv/wooldridge/njmin3.csv`
- **fallback_url**: `https://raw.githubusercontent.com/AnthonyPuggs/CardKrueger1994Replication/main/njmin3.csv`
- **card_archive_validation_url**: `https://davidcard.berkeley.edu/data_sets/njmin.zip`
- **downloaded_at**: `2026-09-16T06:13:29.254112+00:00`
- **source_used**: `本地非空缓存（原始备用来源：https://raw.githubusercontent.com/AnthonyPuggs/CardKrueger1994Replication/main/njmin3.csv）`
- **status**: `已使用缓存；未覆盖`
- **size_bytes**: `25960`
- **sha256**: `5dd549a40790d58cd1705474297ba9cf069e3dbc7fd561e4f6e14a1cde98a4d2`

## 尝试日志

- 初次获取时，主 Rdatasets 端点在 3 次重试后返回 HTTP 404。
- 官方 Wooldridge 包/仓库未在当前包列表中提供 njmin3。
- 初始备用来源为 https://raw.githubusercontent.com/AnthonyPuggs/CardKrueger1994Replication/main/njmin3.csv；模式验证要求 ['centralj', 'co_owned', 'd', 'fte', 'nj', 'pa1', 'pa2', 'southj']。
- Card 公开档案代码本验证端点：https://davidcard.berkeley.edu/data_sets/njmin.zip（初次获取时 HTTP 200）。
- 本次运行按失败处理策略使用已验证缓存；未进行网络下载或覆盖原始文件。

后续脚本不会修改原始 CSV。备用数据的模式包含 `nj`、`d`、`fte`、所有制和地理字段，并与 Card 档案代码本一致：410 家门店和两个调查波次。
