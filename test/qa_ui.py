# 화면 재배치 시험 (build-36, REQ-57): 지금 카드·레이어 시트·큰 입질 버튼·추천 거리. 바탕은 섬 나누기 시험. 가짜 Overpass: 사천 육지에서 가장 가까운 섬 하나에만 다리. 바탕은 시·군·구 추천 시험(REQ-46). 가짜 응답은 출조 계획 시험과 같음. 조석 칩 시험의 가짜 응답을 3주로 늘리고 조차가 사리·조금으로 바뀌게 함
# 원래: 조석 칩 시험: 다가오는 만조/간조, 들물·날물 단계, 물때 이름, 오늘 조석 목록 (build-24)
# 조석예보(고,저조) 가짜 응답: 삼천포(DT_0061) 한 곳, 만조 280cm·간조 20cm, 주기 12.42시간 (활용가이드 261106 응답 모양)
import sys, time, math, datetime
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
src=src.replace("""  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""",
"""  if(url.includes('tideFcstHghLw')){const q=new URL(url).searchParams; window.__tideCalls=(window.__tideCalls||0)+1;
    if(q.get('obsCode')!=='DT_0061')return reply(200,JSON.stringify({response:{header:{resultCode:'03',resultMsg:'NODATA_ERROR'}}}));
    const rd=q.get('reqDate'),y=+rd.slice(0,4),m=+rd.slice(4,6)-1,d=+rd.slice(6,8),day0=Date.UTC(y,m,d)-9*3600e3,P=12.42*3600e3,items=[],p2=v=>String(v).padStart(2,'0');
    for(let k=-6;k<=50;k++)for(const hi of [true,false]){const t=window.__HI0+k*P+(hi?0:P/2); if(t<day0||t>=day0+86400e3)continue;
      const dt=new Date(t+9*3600e3),pm=dt.getUTCHours()>=12;
      items.push({obsvtrNm:'삼천포',lot:'128.0700',lat:'34.9250',predcDt:`${dt.getUTCFullYear()}-${p2(dt.getUTCMonth()+1)}-${p2(dt.getUTCDate())} ${p2(dt.getUTCHours())}:${p2(dt.getUTCMinutes())}`,
        predcTdlvVl:(150+(hi?1:-1)*130*(0.6+0.4*Math.cos(2*Math.PI*(t-window.__HI0)/(14.77*86400e3)))).toFixed(1),extrSe:String(hi?(pm?3:1):(pm?4:2))});}
    items.sort((a,b)=>a.predcDt<b.predcDt?-1:1); const n=+q.get('numOfRows')||10;
    return reply(200,JSON.stringify({response:{header:{resultCode:'00',resultMsg:'NORMAL_SERVICE'},body:{items:{item:items.slice(0,n)},totalCount:items.length}}}));}
  if(url.includes('/api/interpreter')){window.__ovpCalls=(window.__ovpCalls||0)+1; if(window.__ovpFail)return reply(-1,'x');
    return reply(200,JSON.stringify({elements:window.__ovp||[]}));}
  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""")
# 기준 만조: 오늘 0시(KST)+11시41분
src=src.replace('BRIDGE=r"""','BRIDGE=r"""window.__HI0=(()=>{const d=new Date();d.setHours(0,0,0,0);return d.getTime()+(11*60+41)*60000;})();')
assert 'tideFcstHghLw' in src
exec(src+'''
    go(12,34.92,128.07,0)
    for _ in range(60):
        if E("!!__QA.TIDE.cur"): break
        pg.wait_for_timeout(500)
    side=E("[...document.querySelectorAll('.side .ibtn')].map(b=>b.id)")
    check('U1 오른쪽 버튼은 ◎·📅·☰ 3개 (+ 위 ★) — build-49 U-4', side==['locBtn','planBtn','layersBtn'] and E("!!document.querySelector('.top #favBtn')"), side)
    E("document.querySelector('#layersBtn').click()")
    ids=E("[...document.querySelectorAll('#layerPanel .ibtn')].map(b=>b.id)")
    check('U2 보기 시트에 도구 7개 (build-49: 출조 도우미는 M2로)', E("document.querySelector('#layerPanel').classList.contains('show')") and ids==['layerBtn','flowBtn','windBtn','simBtn','rockBtn','sstBtn','setBtn'], ids)
    pg.screenshot(path='/tmp/ui_layer.png')
    on0=E("document.querySelector('#flowBtn').classList.contains('on')"); E("document.querySelector('#flowBtn').click()"); on1=E("document.querySelector('#flowBtn').classList.contains('on')")
    E("document.querySelector('#flowBtn').click()")
    check('U3 시트 안 버튼도 예전처럼 켜고 끔', on0!=on1, [on0,on1])
    E("window.__onBack()")
    check('U4 뒤로가기로 레이어 시트 닫힘', not E("document.querySelector('#layerPanel').classList.contains('show')"))
    E("document.querySelector('#layersBtn').click(); document.querySelector('#planBtn').click()"); pg.wait_for_timeout(300)
    check('U5 시트에서 출조 도우미 열면 시트는 닫힘', E("document.querySelector('#planPanel').classList.contains('show')") and not E("document.querySelector('#layerPanel').classList.contains('show')"))
    E("window.__onBack()"); pg.wait_for_timeout(200)
    for _ in range(100):
        if E("!__QA.REC.busy"): break
        pg.wait_for_timeout(300)
    card=E("(()=>{const c=document.querySelector('#nowCard');return [c.classList.contains('topchips'),!!c.querySelector('#tideChip'),!!c.querySelector('#windChip'),!!c.querySelector('.samplebadge'),getComputedStyle(document.querySelector('#tideChip')).display]})()")
    check('U6 지금 카드 하나에 조석·물때·바람·상태', card[:4]==[True,True,True,True] and card[4]!='none', card)
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(300)
    check('U7 출조 도우미 열림 (build-42부터 머리 줄 대신 P1 📅·오늘 추천 자세히 ›)', E("document.querySelector('#planPanel').classList.contains('show')"))
    E("window.__onBack()"); pg.wait_for_timeout(200)
    for _ in range(100):
        if E("!__QA.REC.busy"): break
        pg.wait_for_timeout(300)
    E("__QA.renderLog&&0"); n0=E("JSON.parse(localStorage.getItem('fishmap.log.v1')||'[]').length")
    E("if(window.__onBack)while(window.__onBack()){}"); E("document.querySelector('#biteFab').click()")
    t=E("document.querySelector('#toast').textContent")
    check('U8 자리·위치 없으면 큰 입질 버튼이 안내', '현위치' in t and E("JSON.parse(localStorage.getItem('fishmap.log.v1')||'[]').length")==n0, t)
    E("__QA.placeMe(34.93,128.06,20)"); E("document.querySelector('#biteFab').click()")
    L1=E("JSON.parse(localStorage.getItem('fishmap.log.v1')||'[]')")
    check('U9 내 위치가 있으면 그 자리로 입질 기록', len(L1)==n0+1 and abs(L1[0]['lat']-34.93)<1e-3 and L1[0]['name']=='내 위치', L1[0] if L1 else None)
    # 박스 겹침 (폰 390x844)
    box=E("['#nowCard','.side','#biteFab','.legend','.top'].map(q=>{const r=document.querySelector(q).getBoundingClientRect();return [q,r.left,r.top,r.right,r.bottom]})")
    def ov(a,b): return not (a[3]<=b[1] or b[3]<=a[1] or a[4]<=b[2] or b[4]<=a[2])
    bad=[(a[0],b[0]) for i,a in enumerate(box) for b in box[i+1:] if ov(a,b)]
    check('U10 카드·버튼·범례·검색창이 서로 안 겹침 (390px 폰)', not bad, [bad, box])
    pg.screenshot(path='/tmp/ui_main.png')
    # 추천 거리 (build-41: 지점을 고를 때 시트에 가려지면 지도를 올리므로, 추천 지역이 바뀌지 않게 처음 화면으로 되돌림)
    E("while(window.__onBack&&window.__onBack()){}"); go(12,34.92,128.07,0)
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(200)
    for _ in range(200):
        pg.wait_for_timeout(300)
        if E("!__QA.REC.busy"): break
    E("AndroidBridge._p.recBasis='area'; document.querySelector('.ptabs [data-tab=rec]').click()"); pg.wait_for_timeout(800)
    E("__QA.REC.res=null; document.querySelector('#recGo').click()")
    for _ in range(300):
        if E("!__QA.REC.busy&&!!__QA.REC.res"): break
        pg.wait_for_timeout(300)
    l2=E("[...document.querySelectorAll('#recList li .l2')].map(x=>x.textContent.slice(0,14))")
    check('U11 추천에 내 위치에서 거리', l2 and all('km' in x for x in l2), l2[:3])
    E("const s=document.querySelector('#recSort'); s.value='near'; s.onchange()")
    km=E("document.querySelector('#recList')._P.map(c=>c.km)")
    pinsOk=E("[...document.querySelectorAll('#recList li')].every((li,i)=>+li.dataset.i===i)")
    check('U12 가까운 순으로 바꾸면 거리 오름차순 (저장)', km==sorted(km) and E("AndroidBridge.getPref('recSort')")=='near' and pinsOk, km)
    E("const s=document.querySelector('#recSort'); s.value='score'; s.onchange()")
    sc=E("document.querySelector('#recList')._P.map(c=>c.score)")
    check('U13 점수순으로 되돌림', sc==sorted(sc,reverse=True), sc)
    check('U14 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
