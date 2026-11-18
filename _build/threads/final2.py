import sys; sys.path.insert(0,'/home/claude/photos')
from colour2 import *
import numpy as np, pickle, json
d=pickle.load(open(W+'comb.pkl','rb')); names=d['names']; C=d['C']
old,jpg,sm=refs(); smk={('Blanc' if k=='BLANC' else 'Ecru' if k=='ECRU' else k):v[2] for k,v in sm.items() if k!='DMC Code'}
J=np.array([lab_hex(jpg[k]) for k in names]); S=np.array([lab_hex(smk[k]) for k in names]); O=np.array([lab_hex(old[k]) for k in names])
def rob(x,y):
    keep=np.ones(len(x),bool)
    for _ in range(4):
        p=np.polyfit(x[keep],y[keep],1); r=y-np.polyval(p,x); keep=np.abs(r)<2*r[keep].std()
    return p
mid=(C[:,0]>35)&(C[:,0]<92)
for nm,R in [('JPG',J),('old',O),('SM',S)]:
    p=rob(C[mid,0],R[mid,0]); print(nm,'L = %.3f*Lc %+.1f  -> at Lc 30: %.1f, 50: %.1f, 70: %.1f, 90: %.1f'%(p[0],p[1],*[np.polyval(p,v) for v in (30,50,70,90)]))
print('comb L range',C[:,0].min().round(1),C[:,0].max().round(1),'310',C[names.index('310')].round(1),'B5200',C[names.index('B5200')].round(1),'Blanc',C[names.index('Blanc')].round(1))
SL,OFF,CH=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3])
AX=[20,28,29.5,40,50,70,90,95,101]; AY=[2,10,12,29.5,41.5,65.5,89.5,95,99.5]
def tone(L): return np.interp(L,AX,AY)
def lab2lin(L,a,b):
    fy=(L+16)/116; fx=fy+a/500; fz=fy-b/200; f=lambda t: t**3 if t>0.206893 else (t-16/116)/7.787
    X,Y,Z=0.95047*f(fx),f(fy),1.08883*f(fz)
    return np.array([3.2406*X-1.5372*Y-0.4986*Z,-0.9689*X+1.8758*Y+0.0415*Z,0.0557*X-0.2040*Y+1.0570*Z])
iw=names.index('Blanc'); aw,bw,Lw=C[iw,1]*0.5,C[iw,2]*0.5,C[iw,0]
out={}; sq=0
for k,(L,a,b) in zip(names,C):
    a,b=a-aw*L/Lw,b-bw*L/Lw
    L2=float(tone(L)); ch=CH*(0.5 if k=='B5200' else 1.0); a2,b2=a*ch,b*ch; s=1.0
    while True:
        lin=lab2lin(L2,a2*s,b2*s)
        if lin.min()>=-1e-4 and lin.max()<=1+1e-4 or s<0.05: break
        s-=0.01
    sq+=s<0.995; out[k]=tohex(np.clip(lin,0,1)).lstrip('#')
print('gamut-squeezed:',sq)
repl={'504':'3813','731':'732','776':'3326','781':'782','806':'3760','971':'740','3773':'407'}
for o_,n_ in repl.items(): out[o_]=out[n_]
rows=json.load(open('/tmp/dmc_rows.json')); miss=[r[0] for r in rows if r[0] not in out]; print('rows',len(rows),'missing',miss)
json.dump(out,open(W+'final.json','w'))
N2=np.array([lab_hex(out[k]) for k in names])
print('new vs JPG dE median %.1f | new vs old median %.1f | new vs SM median %.1f'%tuple(np.median(np.linalg.norm(N2-R,axis=1)) for R in (J,O,S)))
for k in ['798','3849','3848','3847','505','561','500','319','890','734','733','732','730','3013','3012','3011','372','371','370','B5200','Blanc','310','666','444','820','939']:
    i=names.index(k); print(k.ljust(6),'new #%s L%5.1f C%5.1f h%5.1f | yesterday #%s L%5.1f C%5.1f h%5.1f | old #%s L%5.1f C%5.1f h%5.1f'%(out[k],*LCh(N2[i]),jpg[k],*LCh(J[i]),old[k],*LCh(O[i])))
