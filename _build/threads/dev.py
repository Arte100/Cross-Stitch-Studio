import sys, numpy as np, tifffile, cv2
def develop(path, white_box=None):
    with tifffile.TiffFile(path) as t:
        p=t.pages[0]; raw=p.asarray().astype(np.float32)
        tags={k:p.tags[k].value for k in ['BlackLevel','WhiteLevel','ColorMatrix1','ColorMatrix2','AsShotNeutral','Orientation','CFAPattern'] if k in p.tags}
    bl=tags['BlackLevel']; bl=bl[0]/bl[1] if len(bl)>=2 and bl[1]==1 else float(bl[0]); wl=float(tags['WhiteLevel'])
    lin=np.clip((raw-bl)/(wl-bl),0,1)
    pat=bytes(tags['CFAPattern'])
    code={b'\x00\x01\x01\x02':cv2.COLOR_BayerBG2RGB, b'\x02\x01\x01\x00':cv2.COLOR_BayerRG2RGB, b'\x01\x00\x02\x01':cv2.COLOR_BayerGB2RGB, b'\x01\x02\x00\x01':cv2.COLOR_BayerGR2RGB}[pat]
    rgb=cv2.cvtColor((lin*65535).astype(np.uint16),code).astype(np.float32)/65535  # camera RGB, linear
    o=tags.get('Orientation',1)
    if o==6: rgb=np.rot90(rgb,3)
    elif o==8: rgb=np.rot90(rgb,1)
    elif o==3: rgb=np.rot90(rgb,2)
    rgb=np.ascontiguousarray(rgb)
    cm=lambda v: np.array([v[i]/v[i+1] for i in range(0,18,2)]).reshape(3,3)
    return rgb, cm(tags['ColorMatrix1']), cm(tags['ColorMatrix2']), np.array([tags['AsShotNeutral'][i]/tags['AsShotNeutral'][i+1] for i in (0,2,4)])
XYZ2SRGB=np.array([[3.2406,-1.5372,-0.4986],[-0.9689,1.8758,0.0415],[0.0557,-0.2040,1.0570]])
BRAD=np.array([[0.8951,0.2664,-0.1614],[-0.7502,1.7135,0.0367],[0.0389,-0.0685,1.0296]])
D65=np.array([0.95047,1.0,1.08883])
def cam2srgb_matrix(neutral, cm1, cm2):
    # cm1: illuminant D65, cm2: illuminant A. Interpolate by inverse colour temperature, iterating.
    w=0.5
    for _ in range(4):
        cm=w*cm1+(1-w)*cm2; xyzw=np.linalg.inv(cm)@neutral; x,y=xyzw[0]/xyzw.sum(),xyzw[1]/xyzw.sum()
        n=(x-0.3320)/(0.1858-y); cct=449*n**3+3525*n**2+6823.3*n+5520.33
        w=float(np.clip((1/2856-1/cct)/(1/2856-1/6504),0,1))
    cm=w*cm1+(1-w)*cm2; xyzw=np.linalg.inv(cm)@neutral; xyzw=xyzw/xyzw[1]
    s=BRAD@xyzw; d=BRAD@D65; adapt=np.linalg.inv(BRAD)@np.diag(d/s)@BRAD
    return XYZ2SRGB@adapt@np.linalg.inv(cm), cct
def encode(lin):
    lin=np.clip(lin,0,1); return np.where(lin<=0.0031308,12.92*lin,1.055*lin**(1/2.4)-0.055)
