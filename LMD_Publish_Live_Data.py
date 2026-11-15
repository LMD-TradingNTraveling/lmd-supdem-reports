"""Prepare privacy-reduced LMD dashboard live.json from Tradovate master CSVs.
No network access or GitHub credentials required. Optional --repo copies into local clone.
"""
import argparse,csv,json,os,re,tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f);return list(r),r.fieldnames or []
def num(v):return float(str(v or '0').replace(',','').replace('$','').strip())
def stamp(v):return datetime.strptime(v.strip(),'%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
def build(pos,cash):
    ps,ph=read_csv(pos);cs,ch=read_csv(cash)
    if not {'Pair ID','Paired Qty','P/L','Bought Timestamp','Sold Timestamp','Buy Price','Sell Price','Account'}.issubset(ph):raise ValueError('Invalid Position History headers')
    if not {'Transaction ID','Timestamp','Cash Change Type','Delta','Amount','Account'}.issubset(ch):raise ValueError('Invalid Cash History headers')
    if not ps or not cs:raise ValueError('Empty full-history input; publication stopped')
    accounts={x['Account'].strip() for x in ps+cs}
    if len(accounts)!=1:raise ValueError('Multiple or mismatched accounts; publication stopped')
    trades={}
    for r in ps:
        key=r['Pair ID'].strip()
        if not key:raise ValueError('Missing Pair ID')
        buy=stamp(r['Bought Timestamp']);sell=stamp(r['Sold Timestamp'])
        # Short: sold first, bought later. Long: bought first, sold later.
        side='Long' if buy<=sell else 'Short'
        t={'id':key,'account':'LMDTrading','contract':r.get('Contract',''),
           'product':r.get('Product',''),'entry':min(buy,sell),'exit':max(buy,sell),
           'side':side,'qty':num(r['Paired Qty']),'pnl':num(r['P/L']),
           'buy':num(r['Buy Price']),'sell':num(r['Sell Price'])}
        if key in trades and trades[key]!=t:raise ValueError('Conflicting trade Pair ID')
        trades[key]=t
    ledger={}
    for r in cs:
        key=r['Transaction ID'].strip()
        if not key:raise ValueError('Missing Transaction ID')
        c={'id':key,'type':r['Cash Change Type'].strip(),'date':r.get('Date','').strip(),
           'timestamp':r['Timestamp'].strip(),'delta':num(r['Delta']),
           'amount':num(r['Amount']),'account':'LMDTrading'}
        if key in ledger and ledger[key]!=c:raise ValueError('Conflicting Transaction ID')
        ledger[key]=c
    return {'schema':1,'updated_at_et':datetime.now(ZoneInfo('America/New_York')).strftime('%b %d, %Y · %I:%M %p'),
            'trades':sorted(trades.values(),key=lambda x:(x['entry'],x['id'])),
            'cash':sorted(ledger.values(),key=lambda x:(stamp(x['timestamp']),int(x['id']) if x['id'].isdigit() else x['id']))}

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--position',required=True,type=Path)
    a.add_argument('--cash',required=True,type=Path)
    a.add_argument('--repo',type=Path,help='Existing local Git clone, optional')
    a.add_argument('--output',type=Path,default=Path('data/live.json'))
    a.add_argument('--minimum-trades',type=int,default=425)
    args=a.parse_args()
    payload=build(args.position,args.cash)
    if len(payload['trades'])<args.minimum_trades:
        raise SystemExit(f'SAFETY STOP: {len(payload["trades"])} trades < {args.minimum_trades} minimum; full YTD not available')
    target=(args.repo/'data'/'live.json') if args.repo else args.output
    target.parent.mkdir(parents=True,exist_ok=True)
    # Never overwrite with a smaller historical snapshot.
    if target.exists():
        old=json.loads(target.read_text(encoding='utf-8'))
        if len(payload['trades'])<len(old.get('trades',[])) or len(payload['cash'])<len(old.get('cash',[])):
            raise SystemExit('SAFETY STOP: new dataset has fewer records than currently published')
    fd,temp=tempfile.mkstemp(prefix='.live_',suffix='.json',dir=target.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(payload,f,separators=(',',':'),ensure_ascii=False)
        os.replace(temp,target)
    finally:
        if os.path.exists(temp):os.unlink(temp)
    print(f'Validated: {len(payload["trades"])} trades; {len(payload["cash"])} cash records -> {target}')
    print('No GitHub push performed. Review published data and commit/push from your local Git clone.')
if __name__=='__main__':main()
