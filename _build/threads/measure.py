import sys, json, numpy as np, cv2
sys.path.insert(0,'/home/claude/photos')
from dev import *
from cols import C,P
S=3
LUM=np.array([0.2126,0.7152,0.0722])
def rectify(rgb,x0,y0,x1,y1,n,halfw=60):
    """Straighten one column: returns strip image (length along axis, width 2*halfw*S) plus the mapping."""
    p0=np.array([x0,y0],float)*S; p1=np.array([x1,y1],float)*S
    axis=(p1-p0); L=np.linalg.norm(axis); u=axis/L; v=np.array([-u[1],u[0]])  # v points to the left of travel -> flip so +v = image right
    v=-v if v[0]<0 else v
    pitch=L/(n-1); start=p0-u*pitch*1.5; length=int(round(L+3*pitch)); W=2*halfw*S
    ys=np.arange(length)[:,None]; xs=(np.arange(W)-W/2)[None,:]
    mapx=(start[0]+u[0]*ys+v[0]*xs).astype(np.float32); mapy=(start[1]+u[1]*ys+v[1]*xs).astype(np.float32)
    return cv2.remap(rgb,mapx,mapy,cv2.INTER_LINEAR), pitch, (start,u,v,W)
def refine(strip,pitch,n):
    g=strip[:,:,1]; W=strip.shape[1]
    # across-width edges: thread strip is darker/more coloured than paper; use mean absolute horizontal gradient of all channels
    body=strip[int(pitch*1.5):int(pitch*1.5+pitch*(n-1))]
    prof=np.abs(np.diff(cv2.GaussianBlur(body,(0,0),2).mean(axis=2),axis=1)).mean(axis=0)
    mid=W//2; half=int(W*0.5)
    # expected strip half-width ~ 34 preview px
    exp=34*S
    lo=mid-exp; hi=mid+exp
    l=lo-25*S+int(np.argmax(prof[lo-25*S:lo+25*S])); r=hi-25*S+int(np.argmax(prof[hi-25*S:hi+25*S]))
    cx=(l+r)/2; hw=(r-l)/2
    # separators: thin bright lines across the strip
    core=strip[:, int(cx-hw*0.7):int(cx+hw*0.7)].min(axis=2).mean(axis=1)
    hp=core-cv2.GaussianBlur(core.reshape(-1,1),(0,0),pitch*0.35).ravel()
    best=(-1e9,0,pitch)
    for p in np.linspace(pitch*0.955,pitch*1.045,37):
        for off in np.arange(-0.6*pitch,0.6*pitch,1.0):
            centre0=pitch*1.5+off  # centre of first sample in strip coords
            ys=centre0-p/2+p*np.arange(1,n)  # internal boundaries
            ys=ys[(ys>2)&(ys<len(hp)-3)].astype(int)
            sc=hp[ys].sum()+0.5*(hp[ys-1].sum()+hp[ys+1].sum())
            if sc>best[0]: best=(sc,centre0,p)
    return cx,hw,best[1],best[2],best[0]/(n-1)
def measure_photo(k):
    rgb=np.load(f'/home/claude/photos/work/cam_{k}.npy'); _,cm1,cm2,asn=develop(f'/home/claude/photos/in/{k}.dng')
    out=[]; ov=None
    Mprev,_=cam2srgb_matrix(asn,cm1,cm2)
    for (col,x0,y0,x1,y1) in P[k]:
        names=C[col]; n=len(names)
        strip,pitch,(start,u,v,W)=rectify(rgb,x0,y0,x1,y1,n)
        cx,hw,c0,p,score=refine(strip,pitch,n)
        for i,name in enumerate(names):
            cy=c0+i*p
            box=strip[int(cy-p*0.28):int(cy+p*0.28), int(cx-hw*0.62):int(cx+hw*0.62)].reshape(-1,3)
            # paper beside the sample (label area on the left)
            lab=strip[int(cy-p*0.45):int(cy+p*0.45), max(0,int(cx-hw-58*S)):int(cx-hw-10*S)].reshape(-1,3)
            gl=lab[:,1]; paper=np.median(lab[gl>=np.percentile(gl,72)],axis=0)
            pos=start+u*cy+v*(cx-W/2)
            out.append(dict(photo=k,col=col,name=name,x=float(pos[0]),y=float(pos[1]),paper=paper.tolist(),px=box))
        out[-1]['_dbg']=(col,round(cx/S,1),round(hw/S,1),round(c0/S,1),round(p/S,2),round(float(score),4))
        # overlay
        if ov is None: ov=np.clip(encode((rgb.reshape(-1,3)@Mprev.T).reshape(rgb.shape)*2.2)*255,0,255).astype(np.uint8)[:,:,::-1].copy()
        for i in range(n):
            cy=c0+i*p
            for dx,dy,col_ in [(0.62,0.28,(0,255,0))]:
                pts=[start+u*(cy+sy*p*dy)+v*(cx-W/2+sx*hw*dx) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
                cv2.polylines(ov,[np.array(pts,np.int32)],True,col_,3)
            if i%4==0:
                q=start+u*cy+v*(cx-W/2+hw+6*S); cv2.putText(ov,names[i],(int(q[0]),int(q[1])+10),cv2.FONT_HERSHEY_SIMPLEX,1.1,(255,0,255),3)
    return out,ov
if __name__=='__main__':
    import pickle
    allm=[]
    for k in 'abcd':
        m,ov=measure_photo(k); allm+=m
        for r in m:
            if '_dbg' in r: print(k,r['_dbg'])
        cv2.imwrite(f'/home/claude/photos/work/ov_{k}.jpg',cv2.resize(ov,(1024,1365),interpolation=cv2.INTER_AREA),[cv2.IMWRITE_JPEG_QUALITY,80])
    pickle.dump(allm,open('/home/claude/photos/work/meas.pkl','wb')); print(len(allm))
