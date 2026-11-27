# 시험용 페이지 만들기: 앱 index.html에 시험용 창구(window.__QA)를 붙이고, 내장 자료·가짜 지도를 /tmp/qa에 복사
# (예전 /tmp/mkqa.py · /tmp/qa_extra.txt를 저장소로 옮김 — U-37, 11-21)
import os, shutil
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A=os.path.join(ROOT,'app/src/main/assets'); T=os.path.join(ROOT,'test'); OUT='/tmp/qa'
os.makedirs(OUT,exist_ok=True)
L=open(os.path.join(A,'index.html')).read().split('\n')
i=max(k for k,l in enumerate(L) if l=='})();' and L[k+1]=='</script>')
base="SIM,RD,VIEW,CONF,TIDE,WIND,FOLLOW,EV:()=>EV,sel:()=>sel,tMin:()=>tMin,flowAt,baseAt,isWater,W:()=>W,H:()=>H,mode:()=>mode,ROMS,parts:()=>parts,loadFavs,mulddae,tideNow,tH,runDiag,TIDAL,tidalLayer,setRealData,simTimeChanged,bucket,simCache,SIMDB,tideExtremes,tideDay,mulWord,updateTideChips,tideSt:()=>tideStMarker,PLAN,openPlan,sunTimes,select,"
extra=' '.join(open(os.path.join(T,'tools/qa_exports.txt')).read().split())
L.insert(i,"window.__QA={"+base+extra+"};")
open(os.path.join(OUT,'index.html'),'w').write('\n'.join(L))
for f in ('sgg.json','rocks.json','tidal.json','fishing-spots.json'):
    if os.path.exists(os.path.join(A,f)): shutil.copy(os.path.join(A,f),OUT)
if os.path.isdir(os.path.join(A,'depth')):  # 번들 수심 타일 (있으면)
    d=os.path.join(OUT,'depth'); shutil.rmtree(d,ignore_errors=True); shutil.copytree(os.path.join(A,'depth'),d)
shutil.copy(os.path.join(T,'leaflet_stub.js'),os.path.join(OUT,'stub.js'))
print('시험 페이지 준비:',OUT)
