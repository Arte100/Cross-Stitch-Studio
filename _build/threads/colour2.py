import sys, pickle, json, csv, numpy as np
sys.path.insert(0,'/home/claude/photos')
from colour import lab_from_lin, lab_hex, lin_from_hex, tohex
from dev import cam2srgb_matrix
W='/home/claude/photos/o2/work/'
def key(n): return n.zfill(2) if n.isdigit() and int(n)<36 else n
def stat(px,lo,hi):
    g=px[:,1]; a,b=np.percentile(g,[lo,hi]); return px[(g>=a)&(g<=b)].mean(axis=0)
def col_paper(rows):
    t=np.arange(len(rows)); P=np.array([r['paper'] for r in rows]); keep=np.ones(len(rows),bool)
    for _ in range(3):
        co=[np.polyfit(t[keep],P[keep,ch],3) for ch in range(3)]; fit=np.stack([np.polyval(c,t) for c in co],1)
        res=np.abs(fit-P).max(axis=1)/fit[:,1]; keep=res<max(0.03,np.percentile(res,85))
    return fit,res
def load(setname,lo=10,hi=90,verbose=False):
    out={}
    for i in (1,2,3,4):
        k=f'{setname}{i}'; m=pickle.load(open(W+f'meas_{k}.pkl','rb')); meta=np.load(W+f'meta_{k}.npy')
        cm1,cm2=meta[:9].reshape(3,3),meta[9:18].reshape(3,3)
        g={}
        for r in m: g.setdefault(r['col'],[]).append(r)
        for col,rows in sorted(g.items()):
            fit,res=col_paper(rows)
            neutral=np.median(fit,axis=0); neutral=neutral/neutral[1]
            M,cct=cam2srgb_matrix(neutral,cm1,cm2); wh=M@neutral
            for r,s in zip(rows,fit):
                rel=stat(r['px'],lo,hi)/s
                lin=(M@(rel*neutral))/wh
                gg=r['px'][:,1]
                out[key(r['name'])]=dict(lin=lin,rel=rel,col=col,photo=k,paperG=float(s[1]),sd=float(gg.std()/gg.mean()),p=[float(np.percentile(gg,q)/s[1]) for q in (5,25,50,75,95)])
            if verbose: print(k,col,'paper G %.3f..%.3f'%(fit[:,1].min(),fit[:,1].max()),'R/G %.3f B/G %.3f'%(neutral[0],neutral[2]),'cct',round(cct),'resid max %.1f%%'%(res.max()*100))
    return out
def lab(lin): return lab_from_lin(np.clip(lin,1e-5,None))
def LCh(L):
    return L[0],float(np.hypot(L[1],L[2])),float(np.degrees(np.arctan2(L[2],L[1]))%360)
def refs():
    old={r[0]:r[2] for r in json.load(open('/tmp/dmc_rows.json'))}
    jpg=json.load(open('/home/claude/photos/day/final.json'))
    sm={}
    for row in csv.reader(open('/home/claude/threads/src/dmc.csv')):
        sm[row[0]]=row
    return old,jpg,sm
