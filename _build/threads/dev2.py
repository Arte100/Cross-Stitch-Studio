import sys, numpy as np, cv2, tifffile
sys.path.insert(0,'/home/claude/photos')
from dev import *
W='/home/claude/photos/o2/'
for k in sys.argv[1:]:
    rgb,cm1,cm2,asn=develop(W+f'in/{k}.dng')
    with tifffile.TiffFile(W+f'in/{k}.dng') as t:
        p=t.pages[0]; ex={n:p.tags[n].value for n in ['ExposureTime','ISOSpeedRatings','Flash','Orientation','FNumber'] if n in p.tags}
        try:
            ei=p.tags['ExifTag'].value; ex.update({n:ei.get(n) for n in ['ExposureTime','ISOSpeedRatings','Flash','FNumber']})
        except Exception as e: pass
    np.save(W+f'work/cam_{k}.npy',rgb); np.save(W+f'work/meta_{k}.npy',np.concatenate([cm1.ravel(),cm2.ravel(),asn]))
    M,cct=cam2srgb_matrix(asn,cm1,cm2)
    sat=(rgb.max(axis=2)>=0.999).mean()
    print(k,rgb.shape,'asn',asn.round(3),'cct',round(cct),'clipped %.4f%%'%(sat*100),ex)
    s=cv2.resize(rgb,(rgb.shape[1]//3,rgb.shape[0]//3),interpolation=cv2.INTER_AREA)
    im=np.clip(encode((s.reshape(-1,3)@M.T).reshape(s.shape)*1.6)*255,0,255).astype(np.uint8)[:,:,::-1].copy()
    cv2.imwrite(W+f'work/prev_{k}.png',im)
    g=im.copy()
    for x in range(0,g.shape[1],50):
        cv2.line(g,(x,0),(x,g.shape[0]),(0,255,255) if x%100==0 else (120,120,120),1)
        if x%100==0:
            for y in (14,g.shape[0]//2,g.shape[0]-6): cv2.putText(g,str(x),(x+2,y),cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,0,255),1)
    for y in range(0,g.shape[0],50):
        cv2.line(g,(0,y),(g.shape[1],y),(0,255,255) if y%100==0 else (120,120,120),1)
        if y%100==0:
            for x in (2,g.shape[1]//2,g.shape[1]-40): cv2.putText(g,str(y),(x,y-2),cv2.FONT_HERSHEY_SIMPLEX,0.45,(0,0,255),1)
    cv2.imwrite(W+f'work/grid_{k}.jpg',g,[cv2.IMWRITE_JPEG_QUALITY,85])
