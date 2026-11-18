# HTML 한 파일 버전 시험 (REQ-50): 안드로이드 연결 없이 파일(file://)로 열었을 때
# 공공데이터 받기·브라우저 저장소 캐시·인터넷 끊김·내장 자료·백업·달력 알림·CSV·뒤로가기
import re, io, math, json, sys, os, subprocess, datetime, urllib.request
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
ROOT='/home/claude/fishmap-gh'
OUT='/tmp/web/fishmap.html'
subprocess.run(['python3','tools/build_web.py','--leaflet-js','test/leaflet_stub.js','--leaflet-css','/nonexistent.css','--version','시험','--out',OUT],cwd=ROOT,check=True)
# 시험용 엿보기 창(__QA) 넣기
L=open(OUT,encoding='utf-8').read().split('\n')
i=max(k for k,l in enumerate(L) if l=='})();' and L[k+1]=='</script>')
L.insert(i,"window.__QA={SIM,RD,ROCK,TIDE,TIDAL,REC,CONF,sel:()=>sel,select,loadFavs,updateUI,WEBCACHE,tideDay,openPlan,bakMake,bakApply};")
open(OUT,'w',encoding='utf-8').write('\n'.join(L))
APP='file://'+OUT

def proj(lat,lng,z):
    s=256*2**z; return ((lng+180)/360*s,(1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*s)
CX,CY=proj(34.92,128.07,15)
def tile(z,x,y):
    k=2**(15-z); im=Image.new('RGB',(256,256),(170,211,223)); d=ImageDraw.Draw(im)
    P=lambda gx,gy:((gx/k)-x*256,(gy/k)-y*256)
    d.rectangle([P(CX-40000,CY-40000),P(CX+40000,CY-1500)],fill=(242,239,233))
    b=io.BytesIO(); im.save(b,'PNG'); return b.getvalue()
# 조석 가짜 응답 (조석 칩 시험과 같은 모양): 삼천포 DT_0061, 오늘 0시+11:41 만조, 주기 12.42시간
d0=datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
HI0=d0.timestamp()+(11*60+41)*60; P=12.42*3600
def tide(q):
    if q.get('obsCode')!='DT_0061': return {'response':{'header':{'resultCode':'03','resultMsg':'NODATA_ERROR'}}}
    rd=q['reqDate']; day=datetime.datetime(int(rd[:4]),int(rd[4:6]),int(rd[6:8])).timestamp(); items=[]
    for k in range(-6,51):
        for hi in (True,False):
            t=HI0+k*P+(0 if hi else P/2)
            if not (day<=t<day+86400): continue
            dt=datetime.datetime.fromtimestamp(t); pm=dt.hour>=12
            items.append({'obsvtrNm':'삼천포','lot':'128.0700','lat':'34.9250','predcDt':dt.strftime('%Y-%m-%d %H:%M'),
              'predcTdlvVl':'%.1f'%(150+(130 if hi else -130)),'extrSe':str((3 if pm else 1) if hi else (4 if pm else 2))})
    items.sort(key=lambda a:a['predcDt'])
    return {'response':{'header':{'resultCode':'00','resultMsg':'NORMAL_SERVICE'},'body':{'items':{'item':items[:int(q.get('numOfRows','10'))]},'totalCount':len(items)}}}
HITS={'roms':0,'tide':0,'json':0}; OFFLINE=[False]
from urllib.parse import urlparse, parse_qs
def api(route):
    u=route.request.url
    if OFFLINE[0]: return route.abort()
    q={k:v[0] for k,v in parse_qs(urlparse(u).query).items()}
    if '/roms/' in u:
        HITS['roms']+=1
        body=urllib.request.urlopen(u.replace('https://apis.data.go.kr/1192136/roms/GetRomsApiService','http://localhost:9098/roms')).read()
        return route.fulfill(body=body,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'})
    if 'tideFcstHghLw' in u:
        HITS['tide']+=1
        return route.fulfill(body=json.dumps(tide(q),ensure_ascii=False),content_type='application/json',headers={'Access-Control-Allow-Origin':'*'})
    return route.fulfill(body=json.dumps({'response':{'header':{'resultCode':'03'}}}),content_type='application/json',headers={'Access-Control-Allow-Origin':'*'})
res=[]
def check(n,c,d=''):
    res.append(bool(c)); print(('✅' if c else '❌'),n,('— '+str(d)) if d!='' else '')
with sync_playwright() as p:
    br=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    ctx=br.new_context(viewport={'width':411,'height':700},accept_downloads=True)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script("if(!localStorage.getItem('dataKey'))localStorage.setItem('dataKey','K');")
    pg.route('https://apis.data.go.kr/**',api)
    def ht(r):
        m=re.search(r'/(\d+)/(\d+)/(\d+)\.png',r.request.url)
        if not m: return r.abort()
        r.fulfill(body=tile(*map(int,m.groups())),content_type='image/png',headers={'Access-Control-Allow-Origin':'*'})
    pg.route('**/tile.openstreetmap.org/**',ht)
    pg.route('**/*.json',lambda r:(HITS.__setitem__('json',HITS['json']+1),r.abort()))
    pg.route('**/arcgisonline.com/**',lambda r:r.abort())
    pg.goto(APP); pg.wait_for_timeout(1500)
    E=lambda js:pg.evaluate(js)
    def go(z,lat,lng,wait=9000):
        E(f"_map._z={z};_map._c={{lat:{lat},lng:{lng}}};_map.fire('movestart');_map.fire('moveend')"); pg.wait_for_timeout(wait)
    size=os.path.getsize(OUT)//1024
    check('W1 파일 하나(file://)로 열림, 안드로이드 연결 없음, 자료 내장', E("!window.AndroidBridge&&!!window.__EMBED&&!!window.L&&location.protocol==='file:'"), f'{size}KB')
    go(13,34.92,128.07,12000)
    for _ in range(40):
        if E("!!__QA.TIDE.cur"): break
        pg.wait_for_timeout(500)
    st=E("__QA.TIDE.cur&&__QA.TIDE.cur.st.n"); npts=E("__QA.RD.pts.length")
    check('W2 브라우저가 직접 조석·조류 예보를 받음', st=='삼천포' and npts>0, [st,npts,dict(HITS)])
    t1=dict(HITS); n_cache=E("__QA.WEBCACHE.tx('readonly',s=>s.count())")
    pg.reload(); pg.wait_for_timeout(1500); go(13,34.92,128.07,9000)
    for _ in range(40):
        if E("!!__QA.TIDE.cur"): break
        pg.wait_for_timeout(500)
    t2=dict(HITS)
    check('W3 받은 자료를 브라우저 저장소에 저장 → 다시 열면 조석은 새로 안 받음', n_cache>0 and t2['tide']==t1['tide'] and E("!!__QA.TIDE.cur"), [n_cache, t1['tide'], t2['tide']])
    OFFLINE[0]=True
    r=E("(async()=>{const u=[...await new Promise(r=>{})]})") if False else None
    stale=E("""(async()=>{const db=await __QA.WEBCACHE.open();const keys=await new Promise(r=>{const q=db.transaction('h').objectStore('h').getAllKeys();q.onsuccess=()=>r(q.result);});
      const u=keys.find(k=>k.includes('/roms/'));if(!u)return 'no-roms-key';const x=await __QA.WEBCACHE.get(u);x.t-=3*3600e3;await __QA.WEBCACHE.put(u,x.b);
      const db2=await __QA.WEBCACHE.open();await new Promise(r=>{const t=db2.transaction('h','readwrite');t.objectStore('h').put({t:Date.now()-3*3600e3,b:x.b,c:'roms'},u);t.oncomplete=r;});
      const res=await (async()=>{try{const r=await fetch(u);return 'net'}catch(e){return 'off'}})();
      return [res]})()""")
    got=E("""(async()=>{const db=await __QA.WEBCACHE.open();const keys=await new Promise(r=>{const q=db.transaction('h').objectStore('h').getAllKeys();q.onsuccess=()=>r(q.result);});
      const u=keys.find(k=>k.includes('/roms/'));return u?u:''})()""")
    # nget 은 앱 안 함수라 직접 못 부르니, 저장본을 쓰는 지 확인: 인터넷 끊고 같은 화면 다시 그리기
    pg.reload(); pg.wait_for_timeout(1500); go(13,34.92,128.07,9000)
    npts2=E("__QA.RD.pts.length")
    check('W4 인터넷 끊겨도 저장해 둔 예보로 흐름 표시', stale==['off'] and npts2>0, [stale,npts2])
    OFFLINE[0]=False
    E("__QA.ROCK.data=null"); rk=E("(async()=>{const r=await fetch?1:0;return 1})()")
    E("document.querySelector('#rockBtn')&&document.querySelector('#rockBtn').click()"); pg.wait_for_timeout(500)
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(2500)
    check('W5 바위·행정구역 자료는 파일 안에서 읽음 (따로 받기 없음)', HITS['json']==0 and E("!!(__QA.REC.data&&__QA.REC.data.length>70)"), [HITS['json'], E("__QA.REC.data&&__QA.REC.data.length")])
    E("window.__onBack()")
    E("localStorage.setItem('fishmap.favs.v1',JSON.stringify([{lat:34.91,lng:128.04,name:'실안 포인트'}]));localStorage.setItem('fishmap.log.v1',JSON.stringify([{t:Date.now(),name:'실안',mul:'조금',fish:'갑오징어'}]));localStorage.setItem('redKn','2.4')")
    bak=E("__QA.bakMake()")
    E("localStorage.removeItem('fishmap.favs.v1');localStorage.removeItem('fishmap.log.v1');localStorage.setItem('redKn','2.0');localStorage.removeItem('dataKey')")
    r=E(f"__QA.bakApply({json.dumps(bak)})")
    ok=E("[JSON.parse(localStorage.getItem('fishmap.favs.v1')||'[]').length,JSON.parse(localStorage.getItem('fishmap.log.v1')||'[]').length,localStorage.getItem('redKn'),localStorage.getItem('dataKey')]")
    check('W6 백업 내보내기 → 가져오기 (키·설정·즐겨찾기·조과 기록)', bak.startswith('바다흐름지도-백업:') and ok==[1,1,'2.4','K'], [r,ok])
    E("document.querySelector('#setBtn').click()"); pg.wait_for_timeout(200)
    with pg.expect_download() as dl: E("document.querySelector('#bakOut').click()")
    bname=dl.value.suggested_filename; btxt=open(dl.value.path(),encoding='utf-8').read()
    check('W7 백업은 파일로 내려받음 (공유 창 없을 때)', bname.endswith('.json') and btxt.startswith('바다흐름지도-백업:'), bname)
    E("window.__onBack()")
    # 달력 알림
    E("__QA.select(34.92,128.07,'실안 바위')"); pg.wait_for_timeout(500)
    with pg.expect_download() as dl: E("document.querySelector('#alertBtn').click()")
    ics=open(dl.value.path(),encoding='utf-8').read(); nm=dl.value.suggested_filename
    trig=re.findall(r'TRIGGER:-PT(\d+)M',ics)
    check('W8 🔔 안전 알림 → 달력 일정 파일(.ics, 알림 1시간 전)', nm.endswith('.ics') and 'BEGIN:VALARM' in ics and '만조' in ics and trig and all(t in ('60','0') or int(t)<60 for t in trig), [nm, trig, ics.count('BEGIN:VEVENT')])
    check('W9 🔔 버튼이 켜짐으로', E("document.querySelector('#alertBtn').textContent")=='🔔 켜짐')
    # CSV
    E("document.querySelector('#biteBtn').click()"); pg.wait_for_timeout(200)
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(300); E("document.querySelector('.ptabs [data-tab=log]').click()")
    with pg.expect_download() as dl: E("document.querySelector('#logCsv').click()")
    csv=open(dl.value.path(),encoding='utf-8-sig').read()
    check('W10 조과 기록 CSV 내려받기', dl.value.suggested_filename.endswith('.csv') and '들물/날물' in csv.split('\n')[0] and '실안 바위' in csv, dl.value.suggested_filename)
    # 뒤로가기: 열린 창이 닫히고 페이지는 그대로
    pg.go_back(); pg.wait_for_timeout(400)
    check('W11 폰 뒤로가기 → 창 닫힘, 앱은 그대로', not E("document.querySelector('#planPanel').classList.contains('show')") and pg.url.startswith('file://'), pg.url[-30:])
    E("document.querySelector('#setBtn').click()"); pg.wait_for_timeout(200)
    d=E("(async()=>{document.querySelector('#diagBtn').click();await new Promise(r=>setTimeout(r,12000));return document.querySelector('#testOut').textContent})()")
    check('W12 진단에 "웹 시험" 버전 표시', '웹 시험' in d, d[:80])
    check('W13 스크립트 오류 없음', not errs, errs[:3])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
