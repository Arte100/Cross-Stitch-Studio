import sys, pickle, numpy as np, cv2
sys.path.insert(0,'/home/claude/photos')
from measure import rectify, refine
from cols import C
S=3
P={1:[(1,160,194,150,822),(2,271,196,262,883),(3,383,198,378,826),(4,493,204,490,852),(5,598,210,600,818)],
   2:[(6,115,121,121,823),(7,255,122,258,800),(8,393,115,398,962),(9,535,112,539,958),(10,673,113,675,955)],
   3:[(11,130,133,126,908),(12,272,131,261,944),(13,407,132,401,841),(14,541,137,543,838),(15,674,145,676,932)],
   4:[(16,130,122,117,945),(17,263,122,257,850),(18,404,121,398,918),(19,549,124,542,920),(20,690,124,690,958)]}
enc=lambda lin: np.where(lin<=0.0031308,12.92*lin,1.055*np.clip(lin,0,1)**(1/2.4)-0.055)
def measure_photo(k):
    rgb=np.load(f'/home/claude/photos/day/lin_{k}.npy'); out=[]
    ov=(enc(rgb)*255).astype(np.uint8)[:,:,::-1].copy()
    for (col,x0,y0,x1,y1) in P[k]:
        names=C[col]; n=len(names)
        strip,pitch,(start,u,v,W)=rectify(rgb,x0,y0,x1,y1,n,halfw=110)
        cx,hw,c0,p,score=refine(strip,pitch,n)
        for i,name in enumerate(names):
            cy=c0+i*p
            box=strip[int(cy-p*0.28):int(cy+p*0.28), int(cx-hw*0.62):int(cx+hw*0.62)].reshape(-1,3)
            lab=strip[int(cy-p*0.45):int(cy+p*0.45), max(0,int(cx-hw-56*S)):int(cx-hw-9*S)].reshape(-1,3)
            gl=lab[:,1]; paper=np.median(lab[gl>=np.percentile(gl,72)],axis=0)
            pos=start+u*cy+v*(cx-W/2)
            out.append(dict(photo=k,col=col,name=name,x=float(pos[0]),y=float(pos[1]),paper=paper.tolist(),px=box))
            pts=[start+u*(cy+sy*p*0.28)+v*(cx-W/2+sx*hw*0.62) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
            cv2.polylines(ov,[np.array(pts,np.int32)],True,(0,255,0),3)
            if i%4==0:
                q=start+u*cy+v*(cx-W/2+hw+6*S); cv2.putText(ov,name,(int(q[0]),int(q[1])+10),cv2.FONT_HERSHEY_SIMPLEX,1.1,(255,0,255),3)
        print(k,col,'centre',round(cx/S,1),'half-width',round(hw/S,1),'first',round(c0/S,1),'(expected',round(pitch*1.5/S,1),') pitch',round(p/S,2),'score',round(float(score),4))
    return out,ov
if __name__=='__main__':
    allm=[]; tiles=[]
    for k in (1,2,3,4):
        m,ov=measure_photo(k); allm+=m
        t=cv2.resize(ov,(ov.shape[1]*1000//ov.shape[0],1000),interpolation=cv2.INTER_AREA); tiles.append(t)
    pickle.dump(allm,open('/home/claude/photos/day/meas.pkl','wb')); print(len(allm))
    for i in (0,1):
        cv2.imwrite(f'/home/claude/photos/day/ov_{i}.jpg',np.hstack(tiles[2*i:2*i+2]),[cv2.IMWRITE_JPEG_QUALITY,80])
