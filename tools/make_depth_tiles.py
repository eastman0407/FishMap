#!/usr/bin/env python3
"""전국 수심 타일 생성 (앱 번들용).
DB/BADA2024_v1.1.txt.gz(국립해양조사원 BADA2024, 150m, 평균해수면)를 0.5°쯤 블록으로 쪼개
app/src/main/assets/depth/<bx>_<by>.json + index.json 으로 만든다.
전역 격자: 원점(glon0,glat0)에서 dlon/dlat 간격. 블록 = bc×br 칸. 셀=수심(m)·-9999(육지).
육지 판정: BADA 점이 near(150m) 안에 없으면 육지. 보간: rad(200m) 안 거리제곱역가중(IDW).
사용: python3 tools/make_depth_tiles.py [--src DB/..gz] [--out app/src/main/assets/depth]
      [--bbox W S E N]  (없으면 한국 연안 전체)
CI/로컬 공용. bridges.json과 같은 방식(저장소엔 원본만, 타일은 빌드 산출물).
"""
import argparse, gzip, json, math, os, time
import numpy as np

GLON0, GLAT0 = 124.0, 32.5          # 전역 격자 원점(한국 남서쪽)
DLON, DLAT   = 0.00164, 0.00135     # ~150m
BC, BR       = 320, 384             # 블록 칸수(약 0.52°)
LAND = -9999
NEAR, RAD = 150.0, 200.0

ap = argparse.ArgumentParser()
ap.add_argument('--src', default='DB/BADA2024_v1.1.txt.gz')
ap.add_argument('--out', default='app/src/main/assets/depth')
ap.add_argument('--bbox', nargs=4, type=float, default=[124.5, 33.0, 131.5, 38.7],
                metavar=('W','S','E','N'))
a = ap.parse_args()
W,S,E,N = a.bbox
t0 = time.time()
os.makedirs(a.out, exist_ok=True)

# 1) 범위 안 점 읽기
lon=[]; lat=[]; dep=[]
opn = gzip.open if a.src.endswith('.gz') else open
with opn(a.src, 'rt') as f:
    f.readline()
    for line in f:
        p=line.split()
        if len(p)!=3: continue
        try: x=float(p[0]); y=float(p[1]); d=float(p[2])
        except: continue
        if x<W-0.01 or x>E+0.01 or y<S-0.01 or y>N+0.01: continue
        lon.append(x); lat.append(y); dep.append(d)
lon=np.array(lon); lat=np.array(lat); dep=np.array(dep)
print(f"점 {len(lon)} ({time.time()-t0:.0f}s)", flush=True)
if not len(lon):
    json.dump({"glon0":GLON0,"glat0":GLAT0,"dlon":DLON,"dlat":DLAT,"bc":BC,"br":BR,
               "land":LAND,"datum":"MSL","tiles":[]}, open(os.path.join(a.out,'index.json'),'w'))
    print("점 없음 → 빈 index"); raise SystemExit

# 2) 공간 bin (약 150m)
mlat=(S+N)/2
BINLON=NEAR/(111320*math.cos(mlat*math.pi/180)); BINLAT=NEAR/111320
mperlon=111320*math.cos(mlat*math.pi/180); mperlat=111320
bins={}
bi=np.floor((lon-GLON0)/BINLON).astype(int); bj=np.floor((lat-GLAT0)/BINLAT).astype(int)
for k in range(len(lon)):
    bins.setdefault((bi[k],bj[k]),[]).append(k)

# 3) 어떤 블록이 점을 갖는지 → 그 블록만 생성
gJ=np.floor((lon-GLON0)/DLON).astype(int); gI=np.floor((lat-GLAT0)/DLAT).astype(int)
blocks=set(zip((gJ//BC).tolist(), (gI//BR).tolist()))
print(f"생성할 블록 {len(blocks)}개 ({time.time()-t0:.0f}s)", flush=True)

def cellval(cx, cy):
    cbx=int((cx-GLON0)/BINLON); cby=int((cy-GLAT0)/BINLAT)
    best=1e9; sw=0.0; sv=0.0
    for p in range(cbx-2,cbx+3):
        for q in range(cby-2,cby+3):
            arr=bins.get((p,q))
            if not arr: continue
            for k in arr:
                dx=(lon[k]-cx)*mperlon; dy=(lat[k]-cy)*mperlat; d=math.hypot(dx,dy)
                if d<best: best=d
                if d<=RAD: w=1.0/(d*d+1.0); sw+=w; sv+=dep[k]*w
    if best<=NEAR and sw>0: return round(sv/sw,2)
    return LAND

made=[]
for n,(bx,by) in enumerate(sorted(blocks)):
    data=[LAND]*(BC*BR); sea=0
    for li in range(BR):
        cy=GLAT0+(by*BR+li+0.5)*DLAT
        for lj in range(BC):
            cx=GLON0+(bx*BC+lj+0.5)*DLON
            v=cellval(cx,cy)
            if v!=LAND: data[li*BC+lj]=v; sea+=1
    if sea<20: continue   # 바다가 거의 없는 블록(섬 끄트머리)은 건너뜀
    key=f"{bx}_{by}"
    json.dump({"bx":bx,"by":by,"bc":BC,"br":BR,"land":LAND,"data":data},
              open(os.path.join(a.out,key+'.json'),'w'), separators=(',',':'))
    made.append(key)
    if n%20==0: print(f"  {n}/{len(blocks)} ({time.time()-t0:.0f}s)", flush=True)

idx={"glon0":GLON0,"glat0":GLAT0,"dlon":DLON,"dlat":DLAT,"bc":BC,"br":BR,
     "land":LAND,"datum":"MSL","depth_sign":"positive=m below MSL",
     "source":"KHOA BADA2024 v1.1","tiles":sorted(made)}
json.dump(idx, open(os.path.join(a.out,'index.json'),'w'))
tot=sum(os.path.getsize(os.path.join(a.out,k+'.json')) for k in made)
print(f"타일 {len(made)}개, 합계 {tot/1e6:.1f}MB ({time.time()-t0:.0f}s)")
