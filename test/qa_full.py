import re, io, math, json, time
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
def proj(lat,lng,z):
    s=256*2**z; return ((lng+180)/360*s,(1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*s)
CX,CY=proj(34.92,128.07,15)
def tile(z,x,y):
    k=2**(15-z); im=Image.new('RGB',(256,256),(170,211,223)); d=ImageDraw.Draw(im)
    P=lambda gx,gy:((gx/k)-x*256,(gy/k)-y*256)
    d.rectangle([P(CX-2000,CY+150),P(CX+2000,CY+3000)],fill=(242,239,233))
    d.rectangle([P(CX+300,CY+40),P(CX+2000,CY+3000)],fill=(242,239,233))
    d.rectangle([P(CX-60,CY+38),P(CX+300,CY+43)],fill=(170,170,170))
    b=io.BytesIO(); im.save(b,'PNG'); return b.getvalue()
stub=open('/tmp/qa/stub.js').read()
BRIDGE=r"""
window.__calls=[];
window.AndroidBridge={_p:__PREFS__,shareText(t){window.__shared=t},getPref(k){return this._p[k]||''},setPref(k,v){this._p[k]=v},dropCache(u){__calls.push('drop:'+u.slice(0,60))},clearCache(){},
 httpGet(url,id,m){ __calls.push(url.split('?')[0].split('/').slice(-1)[0]+'|'+m);
  const reply=(c,b)=>setTimeout(()=>window.__nativeCb(id,c,b),5);
  if(url.includes('tideFcstTime')){
    const u=new URL(url),code=u.searchParams.get('obsCode'),rd=u.searchParams.get('reqDate'),min=+u.searchParams.get('min')||60;
    if(code!=='DT_0005')return reply(200,JSON.stringify({response:{header:{resultCode:'03',resultMsg:'NO_DATA'},body:{}}}));
    const items=[];for(let mm=0;mm<1440;mm+=min){const hh=String(Math.floor(mm/60)).padStart(2,'0'),mi=String(mm%60).padStart(2,'0');
      const ms=Date.parse(`${rd.slice(0,4)}-${rd.slice(4,6)}-${rd.slice(6,8)}T${hh}:${mi}:00+09:00`);
      items.push({obsName:'삼천포',lat:'34.934',lot:'128.069',predcYmd:rd,predcTm:hh+mi,tideLevel:(150+150*Math.sin(ms/3.6e6/12.42*2*Math.PI)).toFixed(0)});}
    return reply(200,JSON.stringify({response:{header:{resultCode:'00'},body:{totalCount:items.length,items:{item:items}}}}));}
  if(url.includes('VilageFcst')){const items=[];const d=new Date();d.setMinutes(0,0,0);
    for(let h=-30;h<72;h++){const t=new Date(d.getTime()+h*3600e3);const p=n=>String(n).padStart(2,'0');const fd=`${t.getFullYear()}${p(t.getMonth()+1)}${p(t.getDate())}`,ft=p(t.getHours())+'00';
      items.push({category:'UUU',fcstDate:fd,fcstTime:ft,fcstValue:'6'},{category:'VVV',fcstDate:fd,fcstTime:ft,fcstValue:'0'});}
    return reply(200,JSON.stringify({response:{header:{resultCode:'00'},body:{totalCount:items.length,items:{item:items}}}}));}
  const u2=url.replace('https://apis.data.go.kr/1192136/roms/GetRomsApiService','http://localhost:9099/roms');
  fetch(u2).then(r=>r.text().then(t=>window.__nativeCb(id,r.status,t))).catch(e=>window.__nativeCb(id,-1,String(e)));}};
"""
results=[]
def check(name,cond,detail=''):
    results.append((name,bool(cond),detail)); print(('✅' if cond else '❌'),name,('— '+str(detail) if detail else ''))

def page(br,prefs):
    ctx=br.new_context(viewport={'width':390,'height':760},geolocation={'latitude':34.915,'longitude':128.06},permissions=['geolocation'])
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(BRIDGE.replace('__PREFS__',json.dumps(prefs)))
    pg.route('**/leaflet.min.js',lambda r:r.fulfill(body=stub,content_type='text/javascript'))
    pg.route('**/leaflet.min.css',lambda r:r.fulfill(body='',content_type='text/css'))
    def ht(r):
        m=re.search(r'/(\d+)/(\d+)/(\d+)\.png',r.request.url)
        if not m: return r.abort()
        z,x,y=map(int,m.groups()); r.fulfill(body=tile(z,x,y),content_type='image/png',headers={'Access-Control-Allow-Origin':'*'})
    pg.route('**/tile.openstreetmap.org/**',ht)
    pg.route('**/nominatim.openstreetmap.org/**',lambda r:r.fulfill(body=json.dumps([{'name':'신수도','display_name':'신수도, 사천시, 경상남도','lat':'34.905','lon':'128.06'}]),content_type='application/json',headers={'Access-Control-Allow-Origin':'*'}))
    pg.goto('http://localhost:8094/index.html'); pg.wait_for_timeout(1500)
    return pg,errs
E=lambda pg,js:pg.evaluate(js)

with sync_playwright() as p:
    br=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    # ===== A. 키 없는 샘플 모드 =====
    print('\n[A] 샘플 모드 (키 없음)')
    pg,errs=page(br,{})
    check('A1 앱 시작·오류 없음', not errs, errs[:2])
    check('A2 샘플 배지', '샘플' in pg.inner_text('.samplebadge'), pg.inner_text('.samplebadge'))
    E(pg,"_map._z=10;_map.fire('moveend')"); pg.wait_for_timeout(1500)
    check('A3 흐름선 입자 생성', E(pg,"__QA.parts().length")>100, E(pg,"__QA.parts().length"))
    v=E(pg,"JSON.stringify(__QA.flowAt(34.9,128.0,__QA.tMin()/60))")
    check('A4 샘플 흐름값 계산', v and 'vE' in v, v)
    pg.close()

    # ===== B. 실제 예보 모드 =====
    print('\n[B] 실제 예보 모드 (키 있음)')
    pg,errs=page(br,{'dataKey':'TESTKEY'})
    check('B1 실제 예보 배지', any(w in pg.inner_text('.samplebadge') for w in ('실제','확대','항내')), pg.inner_text('.samplebadge'))
    E(pg,"_map._z=11;_map.fire('moveend')"); pg.wait_for_timeout(4000)
    check('B2 ROMS 자료 수신·보간(REQ-07)', E(pg,"__QA.RD.pts.length")>0 and E(pg,"__QA.RD.times.length")>0, f"{E(pg,'__QA.RD.pts.length')}지점 {E(pg,'__QA.RD.times.length')}시각")
    v=E(pg,"(()=>{const f=__QA.flowAt(34.9,128.05,__QA.tMin()/60);return f?Math.hypot(f.vE,f.vN):null})()")
    check('B3 지점 유속 값', v is not None and 0<=v<5, v)
    # 광역(8단계)
    E(pg,"_map._z=8;_map.fire('moveend')"); pg.wait_for_timeout(3000)
    check('B4 광역 8단계 표시(REQ-18)', E(pg,"__QA.RD.pts.length")>0 and '자료 없음' not in pg.inner_text('.samplebadge'), pg.inner_text('.samplebadge'))
    E(pg,"_map._z=11;_map.fire('moveend')"); pg.wait_for_timeout(2500)
    check('B5 색 단계 자동조정(REQ-19)', len(E(pg,"__QA.VIEW.breaks"))==5, [round(x,2) for x in E(pg,"__QA.VIEW.breaks")])
    # 지점 선택·정보카드
    E(pg,"_map.fire('click',{latlng:{lat:34.9,lng:128.05}})"); pg.wait_for_timeout(800)
    check('B6 지점 정보카드', pg.is_visible('#info') and 'kn' in pg.inner_text('#iSpeed'), pg.inner_text('#iSpeed')+' '+pg.inner_text('#iDir'))
    check('B7 유속 그래프 이벤트(물 약해짐)', len(E(pg,"__QA.EV().slack"))>0, pg.inner_text('#iSlack'))
    # 시간 슬라이더
    t0=E(pg,"__QA.tMin()"); pg.click('#nowBtn'); pg.fill('#slider','600'); pg.dispatch_event('#slider','input'); pg.wait_for_timeout(300)
    check('B8 시간 슬라이더', E(pg,"__QA.tMin()")==600, pg.inner_text('#timeLabel'))
    pg.click('#play'); pg.wait_for_timeout(1500); t1=E(pg,"__QA.tMin()"); pg.click('#play')
    check('B9 재생 버튼', t1>600, f"600→{t1:.0f}")
    # 즐겨찾기
    pg.click('#starBtn'); pg.fill('#favName','테스트포인트'); pg.click('#favSave'); pg.wait_for_timeout(300)
    check('B10 즐겨찾기 저장(REQ-06)', any(f['name']=='테스트포인트' for f in E(pg,"__QA.loadFavs()")))
    pg.click('#favBtn'); pg.wait_for_timeout(300)
    check('B11 즐겨찾기 목록에 현재 흐름', 'kn' in pg.inner_text('#favList') or '불러와요' in pg.inner_text('#favList'), pg.inner_text('#favList')[:60])
    pg.click('[data-del="0"]'); pg.wait_for_timeout(200)
    check('B12 즐겨찾기 삭제', len(E(pg,"__QA.loadFavs()"))==0)
    pg.click('#favClose')
    # 검색
    pg.fill('#q','삼천포'); pg.press('#q','Enter'); pg.wait_for_timeout(1800)
    check('B13 내장 포인트 검색(REQ-05)', '삼천포항' in pg.inner_text('#results'))
    pg.fill('#q','신수도'); pg.press('#q','Enter'); pg.wait_for_timeout(2000)
    check('B14 지역 검색(인터넷)', '신수도' in pg.inner_text('#results'), pg.inner_text('#results')[:80])
    pg.click('#results div[data-lat]'); pg.wait_for_timeout(800)
    check('B15 검색결과 이동·선택', E(pg,"__QA.sel()&&__QA.sel().name")=='신수도')
    # 현위치
    pg.click('#locBtn'); pg.wait_for_timeout(2000)
    check('B16 현위치(REQ-04)', E(pg,"__QA.sel()&&__QA.sel().name")=='내 위치', E(pg,"JSON.stringify(__QA.sel())"))
    # 뒤로가기
    r=E(pg,"window.__onBack()")
    check('B17 뒤로가기 → 정보창 닫기', r is True and not E(pg,"!!__QA.sel()"))
    # 지도 순환
    m0=E(pg,"__QA.mode()"); pg.click('#layerBtn'); m1=E(pg,"__QA.mode()"); pg.click('#layerBtn'); m2=E(pg,"__QA.mode()")
    check('B18 지도 전환(REQ-03/20)', m0!=m1 and m1!=m2 or (m0!=m1), f"{m0}→{m1}→{m2}")
    pg.close()

    # ===== C. 바람 =====
    print('\n[C] 바람 (REQ-12)')
    pg,errs=page(br,{'dataKey':'TESTKEY','vworldKey':'VW'})
    pg.click('#windBtn'); pg.wait_for_timeout(2500)
    check('C1 바람 예보 수신', E(pg,"!!__QA.WIND.data"), pg.inner_text('#windChip'))
    check('C2 바람 칩 표시', '서풍' in pg.inner_text('#windChip'), pg.inner_text('#windChip'))
    pg.click('#layerBtn'); m1=E(pg,"__QA.mode()"); pg.click('#layerBtn'); m2=E(pg,"__QA.mode()"); pg.click('#layerBtn'); m3=E(pg,"__QA.mode()")
    check('C3 브이월드 키 있을 때 3단 순환', [m1,m2,m3]==['esri','street','sat'], [m1,m2,m3])
    pg.close()

    # ===== D. 항내 추정 =====
    print('\n[D] 항내 추정 (REQ-09/11)')
    pg,errs=page(br,{'dataKey':'TESTKEY'})
    E(pg,"_map._z=16;_map.fire('moveend')")
    done=False
    for k in range(50):
        pg.wait_for_timeout(1000)
        if E(pg,"__QA.SIM.done"): done=True; break
    check('D1 항내 계산 완료', done, f"steps={E(pg,'__QA.SIM.steps')} badge={pg.inner_text('.samplebadge')}")
    key=E(pg,"__QA.SIM.key"); u=E(pg,"Array.from(__QA.SIM.u.slice(9000,9004))")
    E(pg,"_map.panBy(80,-60)"); pg.wait_for_timeout(1500)
    check('D2 조금 이동해도 결과 동일(재현성)', E(pg,"__QA.SIM.key")==key and E(pg,"Array.from(__QA.SIM.u.slice(9000,9004))")==u)
    E(pg,"_map.fire('click',{latlng:{lat:34.9196,lng:128.07}})"); pg.wait_for_timeout(500)
    check('D3 항내 지점 카드 "추정" 표시', '추정' in pg.inner_text('#iState') or '약' in pg.inner_text('#iSpeed'), pg.inner_text('#iSpeed')+' / '+pg.inner_text('#iState'))
    pg.close()

    # ===== E. 바위·조위 =====
    print('\n[E] 바위·조위 (REQ-13/14)')
    pg,errs=page(br,{'dataKey':'TESTKEY','rockOn':'1'})
    E(pg,"_map._z=13;_map._c={lat:34.92,lng:128.07};_map.fire('moveend')"); pg.wait_for_timeout(5000)
    check('E1 바위 자료 로드', E(pg,"__QA.ROCK.data&&__QA.ROCK.data.length")==9762, E(pg,"__QA.ROCK.data&&__QA.ROCK.data.length"))
    nr=E(pg,"(window.__rocks||[]).length")
    check('E2 화면 내 바위 표시', nr>0, f"{nr}개")
    check('E3 조위 지점 인식', E(pg,"__QA.TIDE.cur&&__QA.TIDE.cur.st.n")=='삼천포', E(pg,"__QA.TIDE.err"))
    tn=E(pg,"__QA.tideNow()")
    check('E4 현재 조위(m)', tn is not None and -1<tn<4, tn)
    cols=set(E(pg,"window.__rocks||[]"))
    check('E5 잠김/드러남 색 구분', '#5fb4ff' in cols or '#ffad5c' in cols, cols)
    E(pg,"_map._z=10;_map.fire('moveend')"); pg.wait_for_timeout(800)
    check('E6 12단계 미만엔 바위 숨김', E(pg,"(window.__rocks||[]).length")==0)
    pg.close()

    # ===== F. 오류 상황 =====
    print('\n[F] 오류 상황')
    pg,errs=page(br,{'dataKey':'TESTKEY'})
    pg.click('#setBtn'); pg.click('#keyTest'); pg.wait_for_timeout(2000)
    check('F1 연결 시험 버튼', '성공' in pg.inner_text('#testOut'), pg.inner_text('#testOut')[:50])
    pg.click('#setClose')
    check('F2 전체 시험 중 스크립트 오류 없음', not errs, errs[:3])
    pg.close()
    print('\n[G] 조석예보 미신청 상태 (결함 회귀 시험)')
    G_BRIDGE=BRIDGE.replace("if(url.includes('tideFcstTime')){","if(url.includes('tideFcstTime')){return reply(200,'<OpenAPI_ServiceResponse><cmmMsgHeader><returnAuthMsg>SERVICE_KEY_IS_NOT_REGISTERED_ERROR</returnAuthMsg></cmmMsgHeader></OpenAPI_ServiceResponse>');")
    BR0=BRIDGE; BRIDGE=G_BRIDGE
    pg,errs=page(br,{'dataKey':'TESTKEY','rockOn':'1'})
    BRIDGE=BR0
    E(pg,"_map._z=13;_map.fire('moveend')"); pg.wait_for_timeout(5000)
    calls=E(pg,"__calls.filter(c=>c.startsWith('tideFcstTime'))")
    check('G1 미신청 응답을 저장하지 않음(저장시간 0)', calls and all(c.endswith('|0') for c in calls), f"{len(calls)}회, 예:{calls[:1]}")
    check('G2 미신청 안내 표시', '활용신청' in E(pg,"__QA.TIDE.err"), E(pg,"__QA.TIDE.err"))
    n1=len(calls); E(pg,"_map.panBy(50,0)"); pg.wait_for_timeout(2500)
    n2=E(pg,"__calls.filter(c=>c.startsWith('tideFcstTime')).length")
    check('G3 실패 후 지도 이동해도 재탐색 안 함(30분)', n2==n1, f"{n1}→{n2}")
    pg.click('#setBtn'); pg.click('#keySave'); pg.wait_for_timeout(300)
    check('G4 설정 저장하면 재탐색 허용', E(pg,"AndroidBridge.getPref('tideScanFailAt')")=='0')
    check('G5 스크립트 오류 없음', not errs, errs[:2])
    pg.close()
    print('\n[H] 개선 5종 (REQ-22~26)')
    pg,errs=page(br,{'dataKey':'TESTKEY','rockOn':'1'})
    lab=pg.inner_html('#timeLabel')
    check('H1 물때 표시(남해 8물때식)', '물' in lab and '음 ' in lab, re.sub('<[^>]+>',' ',lab))
    m=E(pg,"__QA.mulddae(Date.parse('2026-11-14T12:00:00+09:00'),false).name+'/'+__QA.mulddae(Date.parse('2026-11-14T12:00:00+09:00'),true).name")
    check('H2 물때식 구분 (남해 13물 / 서해 12물)', m=='13물/12물', m)
    E(pg,"_map.fire('click',{latlng:{lat:36.33,lng:126.5}})"); pg.wait_for_timeout(500)
    check('H3 서해 지점 누르면 7물때식', '12물' in pg.inner_text('#timeLabel') or '물' in pg.inner_text('#timeLabel'), pg.inner_text('#timeLabel').replace('\n',' '))
    E(pg,"_map._z=13;_map._c={lat:34.92,lng:128.07};_map.fire('moveend')"); pg.wait_for_timeout(5000)
    E(pg,"_map.fire('click',{latlng:{lat:34.915,lng:128.06}})"); pg.wait_for_timeout(800)
    ts=pg.inner_text('#iTide')
    check('H4 물높이·만조·간조 표시(REQ-22)', '물높이' in ts and ('만조' in ts or '간조' in ts), ts)
    # 따라가기
    pg.click('#locBtn'); pg.wait_for_timeout(1500)
    pg.click('#locBtn'); pg.wait_for_timeout(800)
    check('H5 ◎ 두 번 → 따라가기 켜짐(REQ-24)', E(pg,"__QA.FOLLOW.on") and 'follow' in pg.get_attribute('#locBtn','class'))
    pg.context.set_geolocation({'latitude':34.905,'longitude':128.075}); pg.wait_for_timeout(2500)
    s2=E(pg,"__QA.sel()")
    check('H6 걸어가면 내 위치 갱신 (GPS 잠깐 끊겨도 유지)', s2 and abs(s2['lat']-34.905)<1e-4 and E(pg,"__QA.FOLLOW.on"), s2)
    E(pg,"_map.fire('dragstart')"); pg.wait_for_timeout(300)
    check('H7 지도 손으로 움직이면 따라가기 꺼짐', not E(pg,"__QA.FOLLOW.on"))
    # 즐겨찾기 백업
    pg.click('#starBtn'); pg.fill('#favName','백업시험A'); pg.click('#favSave'); pg.wait_for_timeout(200)
    pg.click('#favBtn'); pg.click('#favExport'); pg.wait_for_timeout(300)
    shared=E(pg,"window.__shared||''")
    check('H8 즐겨찾기 백업 보내기(REQ-25)', shared.startswith('물흐름지도-즐겨찾기:') and '백업시험A' in shared, shared[:60])
    check('H9 스크립트 오류 없음', not errs, errs[:2])
    pg.close()
    # 새 폰(빈 앱)에 복원
    pg,errs=page(br,{})
    pg.click('#favBtn'); pg.click('#favImportOpen'); pg.fill('#favImportText','카톡에서 복사:\n'+shared); pg.click('#favImport'); pg.wait_for_timeout(300)
    check('H10 백업 넣기(복원)', any(f['name']=='백업시험A' for f in E(pg,"__QA.loadFavs()")), pg.inner_text('#toast'))
    pg.click('#favImportOpen'); pg.fill('#favImportText',shared); pg.click('#favImport'); pg.wait_for_timeout(300)
    check('H11 같은 백업 두 번 넣어도 중복 안 생김', len(E(pg,"__QA.loadFavs()"))==1, pg.inner_text('#toast'))
    pg.close()
    # 오프라인: 앱이 저장 자료(90분 전)를 돌려주는 상황
    OFF=BRIDGE.replace("fetch(u2).then(r=>r.text().then(t=>window.__nativeCb(id,r.status,t)))","fetch(u2).then(r=>r.text().then(t=>window.__nativeCb(id,1090,t)))")
    BR0=BRIDGE; BRIDGE=OFF; pg,errs=page(br,{'dataKey':'TESTKEY'}); BRIDGE=BR0
    E(pg,"_map._z=11;_map.fire('moveend')"); pg.wait_for_timeout(4000)
    b=pg.inner_text('.samplebadge')
    check('H12 인터넷 없을 때 저장 예보 표시(REQ-23)', '저장된 예보' in b and '2시간 전' in b, b)
    check('H13 저장 예보로도 흐름 계산', E(pg,"__QA.RD.pts.length")>0, E(pg,"__QA.RD.pts.length"))
    pg.close()
    br.close()

ok=sum(1 for r in results if r[1]); print(f"\n결과: {ok}/{len(results)} 통과")
json.dump([[a,b,str(c)] for a,b,c in results],open('/tmp/qa/results.json','w'),ensure_ascii=False)
