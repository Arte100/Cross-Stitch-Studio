import sys, pickle, numpy as np, cv2
sys.path.insert(0,'/home/claude/photos')
from measure import rectify, refine
from dev import cam2srgb_matrix, encode
from cols import C
S=3; W='/home/claude/photos/o2/work/'
P={'f1':[(1,310,352,312,983),(2,422,353,422,1038),(3,535,352,535,983),(4,645,355,645,1010),(5,755,358,755,982)],
   'f2':[(6,288,366,288,943),(7,403,367,403,915),(8,516,365,516,1050),(9,630,363,630,1050),(10,742,361,742,1051)],
   'f3':[(11,298,352,298,1007),(12,414,352,414,1035),(13,532,352,532,948),(14,648,352,648,947),(15,763,353,763,1033)],
   'f4':[(16,297,337,297,1010),(17,412,337,412,928),(18,528,337,528,985),(19,645,337,645,987),(20,762,336,762,1019)],
   'n1':[(1,303,390,298,1015),(2,415,390,410,1073),(3,525,390,522,1020),(4,637,391,637,1050),(5,748,392,750,1022)],
   'n2':[(6,295,364,295,950),(7,411,366,411,923),(8,526,365,526,1065),(9,641,364,641,1067),(10,757,363,757,1070)],
   'n3':[(11,297,337,297,980),(12,412,337,412,1010),(13,528,337,528,927),(14,644,337,644,930),(15,758,337,758,1013)],
   'n4':[(16,317,390,317,1052),(17,432,392,432,970),(18,543,393,543,1025),(19,656,394,656,1027),(20,767,395,767,1055)]}
def measure_photo(k):
    rgb=np.load(W+f'cam_{k}.npy'); meta=np.load(W+f'meta_{k}.npy'); M,_=cam2srgb_matrix(meta[18:],meta[:9].reshape(3,3),meta[9:18].reshape(3,3))
    out=[]; ov=np.clip(encode((rgb.reshape(-1,3)@M.T).reshape(rgb.shape)*1.6)*255,0,255).astype(np.uint8)[:,:,::-1].copy()
    for (col,x0,y0,x1,y1) in P[k]:
        names=C[col]; n=len(names)
        strip,pitch,(start,u,v,Wd)=rectify(rgb,x0,y0,x1,y1,n,halfw=110)
        cx,hw,c0,p,score=refine(strip,pitch,n)
        for i,name in enumerate(names):
            cy=c0+i*p
            box=strip[int(cy-p*0.28):int(cy+p*0.28), int(cx-hw*0.62):int(cx+hw*0.62)].reshape(-1,3)
            lab=strip[int(cy-p*0.45):int(cy+p*0.45), max(0,int(cx-hw-38*S)):int(cx-hw-9*S)].reshape(-1,3)
            gl=lab[:,1]; paper=np.median(lab[gl>=np.percentile(gl,72)],axis=0)
            pos=start+u*cy+v*(cx-Wd/2)
            out.append(dict(photo=k,col=col,name=name,x=float(pos[0]),y=float(pos[1]),paper=paper.tolist(),px=box.copy()))
            pts=[start+u*(cy+sy*p*0.28)+v*(cx-Wd/2+sx*hw*0.62) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
            cv2.polylines(ov,[np.array(pts,np.int32)],True,(0,255,0),3)
            pts=[start+u*(cy+sy*p*0.45)+v*(cx-Wd/2+sx) for sx,sy in [(-hw-38*S,-1),(-hw-9*S,-1),(-hw-9*S,1),(-hw-38*S,1)]]
            if i%6==0: cv2.polylines(ov,[np.array(pts,np.int32)],True,(255,128,0),2)
            if i%4==0:
                q=start+u*cy+v*(cx-Wd/2+hw+6*S); cv2.putText(ov,name,(int(q[0]),int(q[1])+10),cv2.FONT_HERSHEY_SIMPLEX,1.1,(255,0,255),3)
        print(k,col,'centre',round(cx/S,1),'half-width',round(hw/S,1),'first',round(c0/S,1),'(expected',round(pitch*1.5/S,1),') pitch',round(p/S,2),'vs',round(pitch/S,2),'score',round(float(score),4))
    return out,ov
if __name__=='__main__':
    for k in sys.argv[1:]:
        m,ov=measure_photo(k); pickle.dump(m,open(W+f'meas_{k}.pkl','wb'))
        cv2.imwrite(W+f'ov_{k}.jpg',cv2.resize(ov,(1024,1365),interpolation=cv2.INTER_AREA),[cv2.IMWRITE_JPEG_QUALITY,82])
