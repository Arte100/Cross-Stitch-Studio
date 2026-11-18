import sys, pickle, json, csv, math, numpy as np
sys.path.insert(0,'/home/claude/photos')
from colour import lab_from_lin, lab_hex, de, tohex, stat
from cols import C
m=pickle.load(open('/home/claude/photos/day/meas.pkl','rb'))
def col_paper(rows):
    t=np.arange(len(rows)); P=np.array([r['paper'] for r in rows]); keep=np.ones(len(rows),bool)
    for _ in range(3):
        co=[np.polyfit(t[keep],P[keep,ch],3) for ch in range(3)]; fit=np.stack([np.polyval(c,t) for c in co],1)
        res=np.abs(fit-P).max(axis=1)/fit[:,1]; keep=res<max(0.03,np.percentile(res,85))
    return fit,res
groups={}
for r in m: groups.setdefault((r['photo'],r['col']),[]).append(r)
REL={}
for (k,col),rows in sorted(groups.items()):
    fit,res=col_paper(rows)
    for r,s in zip(rows,fit):
        key=r['name'].zfill(2) if r['name'].isdigit() and int(r['name'])<36 else r['name']
        REL[key]=dict(rel=stat(r['px'])/s, paper=s, col=col, photo=k, sd=float(np.std(r['px'][:,1])/np.mean(r['px'][:,1])))
    if __name__=='__main__': print(k,col,'paper level (green) %.3f..%.3f'%(fit[:,1].min(),fit[:,1].max()),'paper tint R/G %.3f B/G %.3f'%(np.median(fit[:,0]/fit[:,1]),np.median(fit[:,2]/fit[:,1])),'fit resid max %.1f%%'%(res.max()*100))
ours={r[0]:r for r in json.load(open('/tmp/dmc_rows.json'))} if __import__('os').path.exists('/tmp/dmc_rows.json') else None
