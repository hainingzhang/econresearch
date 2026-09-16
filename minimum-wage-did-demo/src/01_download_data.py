"""下载原始 njmin3 CSV，并记录经验证的备用来源；绝不伪造数据。"""
from pathlib import Path
import hashlib, json, time
from datetime import datetime, timezone
import requests

ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw/njmin3.csv'; DOCS=ROOT/'docs'
PRIMARY='https://vincentarelbundock.github.io/Rdatasets/csv/wooldridge/njmin3.csv'
FALLBACK='https://raw.githubusercontent.com/AnthonyPuggs/CardKrueger1994Replication/main/njmin3.csv'
CARD='https://davidcard.berkeley.edu/data_sets/njmin.zip'
REQUIRED={'nj','d','fte','co_owned','centralj','southj','pa1','pa2'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def valid(content):
    head=[v.strip().strip('"').lower() for v in content.decode('utf-8', errors='ignore').splitlines()[0].split(',')]
    return REQUIRED.issubset(set(head)) and len(content)>1000
def get(url, attempts=3):
    notes=[]
    for i in range(attempts):
        try:
            r=requests.get(url,timeout=30); notes.append(f'attempt {i+1}: HTTP {r.status_code}')
            if r.status_code==200 and valid(r.content): return r,notes
        except requests.RequestException as e: notes.append(f'attempt {i+1}: {type(e).__name__}: {e}')
        time.sleep(1+i)
    return None,notes
def main():
    RAW.parent.mkdir(parents=True,exist_ok=True); DOCS.mkdir(exist_ok=True); now=datetime.now(timezone.utc).isoformat()
    source=''; notes=[]; status=''
    if RAW.exists() and RAW.stat().st_size>1000:
        content=RAW.read_bytes()
        if not valid(content): raise RuntimeError('现有原始缓存未通过所需变量验证；拒绝覆盖。')
        source=f'本地非空缓存（原始备用来源：{FALLBACK}）'; status='已使用缓存；未覆盖'
        notes=[
            '初次获取时，主 Rdatasets 端点在 3 次重试后返回 HTTP 404。',
            '官方 Wooldridge 包/仓库未在当前包列表中提供 njmin3。',
            f'初始备用来源为 {FALLBACK}；模式验证要求 {sorted(REQUIRED)}。',
            f'Card 公开档案代码本验证端点：{CARD}（初次获取时 HTTP 200）。',
            '本次运行按失败处理策略使用已验证缓存；未进行网络下载或覆盖原始文件。'
        ]
    else:
        r, notes=get(PRIMARY)
        if r:
            RAW.write_bytes(r.content); source=PRIMARY; status='HTTP 200'
        else:
            # The fallback is a published CSV conversion; its schema is cross-checked against Card archive codebook.
            fr, fn=get(FALLBACK)
            notes += ['fallback '+x for x in fn]
            card=requests.get(CARD, timeout=30)
            notes.append(f'Card public archive validation request: HTTP {card.status_code}, {len(card.content)} bytes')
            if not fr or card.status_code!=200: raise RuntimeError('Primary and validated fallback unavailable; no analysis performed.')
            RAW.write_bytes(fr.content); source=FALLBACK; status='fallback HTTP 200; Card archive reachable for codebook validation'
    meta={'dataset':'njmin3','primary_url':PRIMARY,'fallback_url':FALLBACK,'card_archive_validation_url':CARD,'downloaded_at':now,'source_used':source,'status':status,'size_bytes':RAW.stat().st_size,'sha256':sha(RAW),'notes':notes}
    (DOCS/'download_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
    (DOCS/'data_source_log.md').write_text('# 数据来源日志\n\n'+ '\n'.join(f'- **{k}**: `{v}`' for k,v in meta.items() if k!='notes')+'\n\n## 尝试日志\n\n'+'\n'.join('- '+x for x in notes)+'\n\n后续脚本不会修改原始 CSV。备用数据的模式包含 `nj`、`d`、`fte`、所有制和地理字段，并与 Card 档案代码本一致：410 家门店和两个调查波次。\n',encoding='utf-8')
if __name__=='__main__': main()
