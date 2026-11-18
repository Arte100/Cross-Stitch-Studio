import sys; sys.path.insert(0,'/home/claude/photos')
from colour2 import *
import numpy as np, pickle, json
d=pickle.load(open(W+'obs.pkl','rb')); obs=d['obs']; names=d['names']; FL=0.011
def obs_lab(o):
    lin=(o['M']@(o['rel']*o['neutral']))/o['wh']; return lab((lin-FL)/(1-FL))
per={}
for o in obs: per.setdefault(o['name'],{}).setdefault(o['set'],[]).append(obs_lab(o))
col={o['name']:o['col'] for o in obs if not o['dup']}
N=np.array([np.mean(per[k]['n'],axis=0) for k in names]); Fh=[k for k in names if 'f' in per[k]]
F=np.array([np.mean(per[k]['f'],axis=0) if 'f' in per[k] else [np.nan]*3 for k in names]); has=~np.isnan(F[:,0])
# luminance: log-mean of Y across the two sets
Y=lambda L: np.where(L>8,((L+16)/116)**3,L/903.3)
Linv=lambda y: np.where(y>0.008856,116*np.cbrt(y)-16,903.3*y)
gF=np.exp(np.mean(np.log(Y(N[has,0]))-np.log(Y(F[has,0])))); print('F overall luminance factor vs N: %.3f'%(1/gF))
Yc=np.where(has,np.exp((np.log(Y(N[:,0]))+np.log(Y(np.nan_to_num(F[:,0],nan=50))))/2),Y(N[:,0])/np.sqrt(gF))
# chroma: F's a,b scale to N at same luminance is about equal; average a,b after scaling each to the combined lightness (a,b scale ~ with cube-root of Y)
sN=np.cbrt(Yc/Y(N[:,0])); sF=np.cbrt(Yc/Y(np.nan_to_num(F[:,0],nan=50)))
ab=np.where(has[:,None],(N[:,1:]*sN[:,None]+np.nan_to_num(F[:,1:])*sF[:,None])/2,N[:,1:]*sN[:,None])
C=np.column_stack([Linv(Yc),ab])
old,jpg,sm=refs(); smk={('Blanc' if k=='BLANC' else 'Ecru' if k=='ECRU' else k):v[2] for k,v in sm.items() if k!='DMC Code'}
J=np.array([lab_hex(jpg[k]) for k in names]); S=np.array([lab_hex(smk[k]) for k in names]); O=np.array([lab_hex(old[k]) for k in names])
cols=np.array([col[k] for k in names])
def colres(X,ref,deg=3):
    p=np.polyfit(X,ref,deg); r=ref-np.polyval(p,X); return np.array([r[cols==c].mean() for c in range(1,21)]),r.std()
print('per-column mean lightness residual (reference minus smooth function of ours), cols 1..20')
for nm,X in [('N',N[:,0]),('F',np.where(has,F[:,0],N[:,0])),('comb',C[:,0])]:
    for rn,R in [('JPG',J[:,0]),('SM',S[:,0]),('old',O[:,0])]:
        cr,sd=colres(X,R); print(' %-4s vs %-3s sd %.2f | '%(nm,rn,sd)+' '.join('%+5.1f'%v for v in cr)+' | rms of column means %.2f'%np.sqrt((cr**2).mean()))
cr,sd=colres(J[:,0],S[:,0]); print(' JPG  vs SM  sd %.2f | '%sd+' '.join('%+5.1f'%v for v in cr)+' | rms %.2f'%np.sqrt((cr**2).mean()))
pickle.dump(dict(names=names,C=C,N=N,F=F,has=has,cols=cols),open(W+'comb.pkl','wb'))
