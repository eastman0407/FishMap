# 실데이터 모양(mock_roms_real.js) 기준 회귀 시험: 확대·축소해도 바다 전체에 흐름이 있는지, 호출 수가 적당한지
import re, io, math, json, sys, urllib.request
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
APP=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8094/index.html'
def proj(lat,lng,z):
    s=256*2**z; return ((lng+180)/360*s,(1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*s)
CX,CY=proj(34.92,128.07,15)
def tile(z,x,y):  # 위쪽 육지 띠 + 오른쪽 아래 섬, 나머지 바다
    k=2**(15-z); im=Image.new('RGB',(256,256),(170,211,223)); d=ImageDraw.Draw(im)
    P=lambda gx,gy:((gx/k)-x*256,(gy/k)-y*256)
    d.rectangle([P(CX-40000,CY-40000),P(CX+40000,CY-1500)],fill=(242,239,233))
    d.ellipse([P(CX+300,CY+400),P(CX+900,CY+900)],fill=(242,239,233))
    b=io.BytesIO(); im.save(b,'PNG'); return b.getvalue()
stub=open('/tmp/qa/stub.js').read()
BRIDGE=r"""window.AndroidBridge={_p:{dataKey:'K'},getPref(k){return this._p[k]||''},setPref(k,v){this._p[k]=v},dropCache(){},clearCache(){},shareText(t){window.__shared=t},
 httpGet(url,id,m){const reply=(c,b)=>setTimeout(()=>window.__nativeCb(id,c,b),3);
  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));
  fetch(url.replace('https://apis.data.go.kr/1192136/roms/GetRomsApiService','http://localhost:9098/roms')).then(r=>r.text().then(t=>reply(r.status,t)));}};"""
calls=lambda:int(urllib.request.urlopen('http://localhost:9098/calls').read())
urllib.request.urlopen('http://localhost:9098/reset')
res=[]
def check(n,c,d=''):
    res.append(c); print(('✅' if c else '❌'),n,('— '+str(d)) if d!='' else '')
COV="""(()=>{let w=0,h=0;const th=__QA.tMin()/60;for(let yy=0;yy<10;yy++)for(let xx=0;xx<6;xx++){const x=(xx+.5)*__QA.W()/6,y=(yy+.5)*__QA.H()/10;
  if(!__QA.isWater(x,y))continue;w++;const ll=_map.containerPointToLatLng([x,y]);if(__QA.baseAt(ll.lat,ll.lng,th))h++;}return [h,w];})()"""
with sync_playwright() as p:
    br=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=br.new_page(viewport={'width':411,'height':700}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(BRIDGE)
    pg.route('**/leaflet.min.js',lambda r:r.fulfill(body=stub,content_type='text/javascript'))
    pg.route('**/lib/leaflet.min.css',lambda r:r.fulfill(body='',content_type='text/css'))
    def ht(r):
        m=re.search(r'/(\d+)/(\d+)/(\d+)\.png',r.request.url)
        if not m: return r.abort()
        r.fulfill(body=tile(*map(int,m.groups())),content_type='image/png',headers={'Access-Control-Allow-Origin':'*'})
    pg.route('**/tile.openstreetmap.org/**',ht)
    pg.goto(APP); pg.wait_for_timeout(1500)
    E=lambda js:pg.evaluate(js)
    def go(z,lat,lng,wait=9000):
        E(f"_map._z={z};_map._c={{lat:{lat},lng:{lng}}};_map.fire('movestart');_map.fire('moveend')"); pg.wait_for_timeout(wait)
    c0=calls(); go(9,34.85,128.1,15000); h,w=E(COV); c1=calls()
    check('R1 넓은 화면(9단계) 바다 80% 이상에 흐름', w and h/w>=0.8, f'{h}/{w}곳, 호출 {c1-c0}회')
    check('R2 넓은 화면 호출 수 100회 이하', c1-c0<=100, c1-c0)
    go(15,34.86,128.15); h,w=E(COV); c2=calls()
    check('R3 넓게 본 뒤 15단계로 확대해도 바다 90% 이상에 흐름 (실기기 결함 재현)', w and h/w>=0.9, f'{h}/{w}곳, 추가 호출 {c2-c1}회')
    go(12,34.8,128.0); h,w=E(COV); c3=calls()
    check('R4 12단계 바다 90% 이상에 흐름 (띠 모양 잘림 없음)', w and h/w>=0.9, f'{h}/{w}곳, 추가 호출 {c3-c2}회')
    E("_map.panBy(40,30)"); pg.wait_for_timeout(4000); c4=calls()
    check('R5 조금 움직이면 다시 받지 않음(저장 재사용)', c4-c3<=4, f'추가 호출 {c4-c3}회')
    go(15,34.86,128.15,5000); c5=calls()
    check('R6 이미 본 곳 다시 가면 호출 거의 없음', c5-c4<=4, f'추가 호출 {c5-c4}회')
    # R8: 항내 추정 계산이 끝난 곳을 떠났다가 돌아오면 바로 보여야 함 (실기기 지연 보고 11-14)
    import time
    def wait_sim(limit):
        t=time.time()
        while time.time()-t<limit:
            if E("__QA.SIM.on&&__QA.SIM.ready&&__QA.SIM.done"): return time.time()-t
            pg.wait_for_timeout(100)
        return None
    go(16,34.898,128.096,500); t1=wait_sim(90)
    go(16,34.918,128.20,500); wait_sim(90)
    go(16,34.898,128.096,0); t0=time.time(); pg.wait_for_timeout(2500)  # 예보 다시 맞춘 뒤까지 포함
    while E("__QA.RD.loading") and time.time()-t0<30: pg.wait_for_timeout(100)
    r=wait_sim(30); t3=None if r is None else r  # 예보 맞춘 뒤 다시 계산하느라 기다린 시간
    check('R8 계산 끝난 곳에 돌아오면 3초 안에 표시 (다시 계산 안 함)', t3 is not None and t3<3, f'처음 {t1 and round(t1,1)}초 → 돌아왔을 때 {t3 and round(t3,1)}초')
    check('R7 스크립트 오류 없음', not errs, errs[:2])
    print(f'총 호출 {calls()}회 (하루 한도 10,000)')
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
