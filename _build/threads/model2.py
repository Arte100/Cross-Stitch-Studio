import sys; sys.path.insert(0,'/home/claude/photos')
import measure2 as m2, numpy as np, pickle, os
from colour2 import *
XD={'n2x':[(5,110,358,110,1008),(11,915,360,915,1015)],'n3x':[(10,147,338,147,1035)],'f2x':[(5,105,368,105,998),(11,893,358,893,995)],'f3x':[(10,143,355,143,1068)]}
if not os.path.exists(W+'meas_n2x.pkl'):
    for k,lst in XD.items():
        import shutil
        for nm in ('cam','meta'): 
            if not os.path.exists(W+f'{nm}_{k}.npy'): os.symlink(W+f'{nm}_{k[:2]}.npy',W+f'{nm}_{k}.npy')
        m2.P[k]=lst; m,ov=m2.measure_photo(k); pickle.dump(m,open(W+f'meas_{k}.pkl','wb'))
FL=0.011; XC,YC=512*3,683*3
obs=[]
for k in ['n1','n2','n3','n4','f1','f2','f3','f4','n2x','n3x','f2x','f3x']:
    m=pickle.load(open(W+f'meas_{k}.pkl','rb')); meta=np.load(W+f'meta_{k[:2]}.npy'); cm1,cm2=meta[:9].reshape(3,3),meta[9:18].reshape(3,3)
    g={}
    for r in m: g.setdefault(r['col'],[]).append(r)
    for col,rows in g.items():
        fit,res=col_paper(rows); neutral=np.median(fit,axis=0); neutral/=neutral[1]; M,_=cam2srgb_matrix(neutral,cm1,cm2); wh=M@neutral
        for r,s in zip(rows,fit):
            rel=stat(r['px'],10,90)/s
            obs.append(dict(photo=k[:2],dup=len(k)>2,set=k[0],col=col,name=key(r['name']),x=(r['x']-XC)/1000,y=(r['y']-YC)/1000,rel=rel,M=M,neutral=neutral,wh=wh,clip=float((r['px'].max(axis=1)>0.97).mean())))
obs=[o for o in obs if o['clip']<=0.002]
names=sorted({o['name'] for o in obs}); ni={n:i for i,n in enumerate(names)}; photos=['n1','n2','n3','n4','f1','f2','f3','f4']; pi={p:i for i,p in enumerate(photos)}
def fit(order=1,ygrad=False,lam=0.0):
    nt=len(names); npar=order+(1 if ygrad else 0); A=np.zeros((len(obs)+ (8*npar if lam else 0),nt+8*npar)); b=np.zeros(A.shape[0])
    for j,o in enumerate(obs):
        A[j,ni[o['name']]]=1; base=nt+pi[o['photo']]*npar
        for q in range(order): A[j,base+q]=o['x']**(q+1)
        if ygrad: A[j,base+order]=o['y']
        b[j]=np.log(o['rel'][1])
    sol=np.linalg.lstsq(A,b,rcond=None)[0]; r=A[:len(obs)]@sol-b[:len(obs)]
    return sol,r,npar
for order,yg in [(0,False),(1,False),(2,False),(1,True)]:
    if order==0:
        # no correction: residual around per-thread mean
        T={}; 
        for o in obs: T.setdefault(o['name'],[]).append(np.log(o['rel'][1]))
        r=np.concatenate([np.array(v)-np.mean(v) for v in T.values()]); print('no correction: rms residual %.4f'%np.sqrt((r**2).mean())); continue
    sol,r,npar=fit(order,yg); nt=len(names)
    print('order',order,'ygrad',yg,'rms residual %.4f'%np.sqrt((r**2).mean()),'| params per photo:',{p:sol[nt+pi[p]*npar:nt+(pi[p]+1)*npar].round(3).tolist() for p in photos})
    d=np.array([o['dup'] for o in obs]); print('   dup obs rms %.4f, main rms %.4f'%(np.sqrt((r[d]**2).mean()),np.sqrt((r[~d]**2).mean())))
    for s in 'nf':
        print('   ',s,' '.join('c%d %+.3f'%(c,np.mean([rr for rr,o in zip(r,obs) if o['set']==s and o['col']==c and not o['dup']])) for c in range(1,21)))
pickle.dump(dict(obs=obs,names=names),open(W+'obs.pkl','wb'))
