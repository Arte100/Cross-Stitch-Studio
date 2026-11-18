import json,re,collections,numpy as np
from skimage.color import rgb2lab, lab2rgb, deltaE_ciede2000
R='/home/claude/cross-stitch-studio/'; S=R+'_build/colours/swatches/'
s=open(R+'stitch/index.html',encoding='utf-8').read(); i=s.index('const DMC_RAW = `')+17; j=s.index('`',i)
DH={l.split(',')[0]:l.split(',')[2] for l in s[i:j].strip().split('\n')}
def norm(x):
    x=x.strip().upper(); m={'BLANC':'Blanc','WHITE':'Blanc','ECRU':'Ecru'}
    if x in m: return m[x]
    if x.isdigit() and len(x)<=2 and int(x)<36: return x.zfill(2)
    return x
def L(h): h=h.lstrip('#'); return rgb2lab(np.array([[[int(h[k:k+2],16)/255 for k in (0,2,4)]]]))[0,0]
def H(l): return '#%02X%02X%02X'%tuple(int(round(v*255)) for v in np.clip(lab2rgb(np.array([[l]]))[0,0],0,1))
def dE(a,b): return float(deltaE_ciede2000(a,b))
DL={a:L(h) for a,h in DH.items()}
def feats(X): return np.column_stack([np.ones(len(X)),X,X[:,0]**2])
def fit(pairs):  # pairs: (source lab, our dmc lab); robust least squares
    X=np.array([p[0] for p in pairs]); Y=np.array([p[1] for p in pairs]); w=np.ones(len(X))
    for _ in range(8):
        A=feats(X)*w[:,None]; M=np.linalg.lstsq(A,Y*w[:,None],rcond=None)[0]; r=np.linalg.norm(feats(X)@M-Y,axis=1); w=1/np.maximum(1,r/8)
    return lambda x: feats(np.array([x]))[0]@M
conv=json.loads(re.search(r'\nconst CONV=(.*?);\n',open(R+'colours/test/index.html',encoding='utf-8').read(),re.S).group(1))
def rep(b):  # code -> the DMC threads our table gives for it
    return {c:e['p'] or e.get('a',[]) for c,e in conv[b]['r'].items()}
