import sys, json, pickle, math, csv, numpy as np
sys.path.insert(0,'/home/claude/photos')
from dev import *
LUMc=None
def lab_from_lin(rgb):
    r,g,b=rgb; x=(0.4124*r+0.3576*g+0.1805*b)/0.95047; y=0.2126*r+0.7152*g+0.0722*b; z=(0.0193*r+0.1192*g+0.9505*b)/1.08883
    t=lambda v: v**(1/3) if v>0.008856 else 7.787*v+16/116
    return np.array([116*t(y)-16,500*(t(x)-t(y)),200*(t(y)-t(z))])
def lin_from_hex(h):
    h=h.lstrip('#'); c=np.array([int(h[i:i+2],16)/255 for i in (0,2,4)]); return np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
def lab_hex(h): return lab_from_lin(lin_from_hex(h))
def de(a,b): return float(np.linalg.norm(a-b))
def tohex(lin): return '#%02X%02X%02X'%tuple(int(round(v*255)) for v in encode(np.asarray(lin)))
def load():
    return pickle.load(open('/home/claude/photos/work/meas.pkl','rb'))
def paper_surface(rows):
    X=np.array([[1,r['x']/1000,r['y']/1000,(r['x']/1000)**2,(r['y']/1000)**2,r['x']*r['y']/1e6] for r in rows]); P=np.array([r['paper'] for r in rows])
    keep=np.ones(len(rows),bool)
    for _ in range(3):
        coef=np.linalg.lstsq(X[keep],P[keep],rcond=None)[0]; res=np.abs((X@coef-P)/P).max(axis=1); keep=res<max(0.04,np.percentile(res,90))
    return X@coef, res
def stat(px, lo=10, hi=90):
    g=px[:,1]; a,b=np.percentile(g,[lo,hi]); return px[(g>=a)&(g<=b)].mean(axis=0)
def relative(rows_by_photo, lo=10, hi=90):
    """camera-space reflectance relative to the paper beside each sample"""
    out={}
    for k,rows in rows_by_photo.items():
        surf,res=paper_surface(rows)
        for r,s in zip(rows,surf): out[(k,r['col'],r['name'])]=dict(rel=stat(r['px'],lo,hi)/s, paper=s, x=r['x'], y=r['y'])
    return out
