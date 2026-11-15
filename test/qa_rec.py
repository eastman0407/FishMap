# 시·군·구 추천 장소 시험 (REQ-46). 가짜 응답은 출조 계획 시험과 같음. 조석 칩 시험의 가짜 응답을 3주로 늘리고 조차가 사리·조금으로 바뀌게 함
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
  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""")
# 기준 만조: 오늘 0시(KST)+11시41분
src=src.replace('BRIDGE=r"""','BRIDGE=r"""window.__HI0=(()=>{const d=new Date();d.setHours(0,0,0,0);return d.getTime()+(11*60+41)*60000;})();')
assert 'tideFcstHghLw' in src
exec(src+'''
    go(11,34.95,128.06,0)
    for _ in range(60):
        if E("!!__QA.TIDE.cur"): break
        pg.wait_for_timeout(500)
    E("localStorage.setItem('fishmap.favs.v1',JSON.stringify([{lat:34.9105,lng:128.0405,name:'실안 내 포인트'},{lat:35.10,lng:129.03,name:'부산 방파제'}]))")
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(200)
    for _ in range(200):
        pg.wait_for_timeout(300)
        if E("!__QA.REC.busy"): break
    E("document.querySelector('.ptabs [data-tab=rec]').click()"); pg.wait_for_timeout(1500)
    sd=E("[...document.querySelectorAll('#recSido option')].map(o=>o.textContent)")
    sg=E("[...document.querySelectorAll('#recSgg option')].map(o=>o.textContent)")
    cur=E("document.querySelector('#recSgg').selectedOptions[0].textContent")
    check('R1 시·도 → 시·군·구 고르기 (해안 있는 곳만, 지도 가까운 곳 먼저 선택)', len(sd)==11 and '경남' in sd and '서울' not in sd and any('사천시' in x for x in sg) and '사천시' in cur, [sd, cur, len(sg)])
    t=E("Date.now()"); E("document.querySelector('#recGo').click()")
    for _ in range(200):
        if E("!__QA.REC.busy&&!!__QA.REC.res"): break
        pg.wait_for_timeout(300)
    took=(E("Date.now()")-t)/1000
    R=E("(()=>{const R=__QA.REC.res;return R&&{n:R.n,cov:R.cov,str:R.str,b:R.sg.b,pick:R.pick.map(c=>({la:c.la,lo:c.lo,s:c.score,sp:c.best&&c.best.sp,rocks:c.rocks,kind:c.kind,fav:c.fav}))}})()")
    items=E("[...document.querySelectorAll('#recList>li')].map(l=>l.textContent)")
    check('R2 추천 5곳 (사천시 안, 서로 1.2km 이상 떨어짐) + 목록', R and len([p for p in R['pick'] if not p.get('fav')])==5 and len(items)==len(R['pick']) and all(R['b'][0]-0.01<=p['la']<=R['b'][2]+0.01 and R['b'][1]-0.01<=p['lo']<=R['b'][3]+0.01 for p in R['pick']), [took, R and R['cov'], R and R['n'], items[:2]])
    import math
    def dm(a,b): return math.hypot(a['la']-b['la'],(a['lo']-b['lo'])*math.cos(math.radians(a['la'])))*111320
    P=R['pick']
    check('R3 점수 높은 순 + 서로 떨어짐 + 유속 있음', all(P[i]['s']>=P[i+1]['s'] for i in range(4)) and min(dm(a,b) for i,a in enumerate([p for p in P if not p.get('fav')]) for b in [p for p in P if not p.get('fav')][i+1:])>=1200 and all(p['sp'] is not None for p in P), [(round(p['s'],2),p['sp'] and round(p['sp'],2),p['rocks'],p['kind']) for p in P])
    import json
    rocks=json.load(open('/tmp/qa/rocks.json'))
    py=[sum(1 for r in rocks if math.hypot(r[0]-p['la'],(r[1]-p['lo'])*math.cos(math.radians(p['la'])))*111320<=300) for p in P]
    check('R4 바위 개수(300m 안) 계산 확인', py==[p['rocks'] for p in P], [py,[p['rocks'] for p in P]])
    ld=E("__QA.mulddae(Date.now(),false).ld"); m=((ld-1)%15)+1
    want='strong' if (m<=4 or m>=13) else 'weak' if 7<=m<=10 else 'mid'
    check('R5 오늘 물 세기(음력)로 장소 성격 규칙 적용', R['str']==want and '오늘' in E("document.querySelector('#recSub').textContent"), [ld, R['str'], E("document.querySelector('#recSub').textContent")])
    m1=E("window.__markers||0")
    E("document.querySelector('#recList>li').click()"); pg.wait_for_timeout(400)
    check('R6 누르면 패널 닫고 그 지점 선택', not E("document.querySelector('#planPanel').classList.contains('show')") and (E("__QA.sel()&&__QA.sel().name") or '').startswith('추천 1'), E("__QA.sel()&&__QA.sel().name"))
    check('R7 지도에 ①~⑤ 핀', E("__QA.REC.layer.getLayers?__QA.REC.layer.getLayers().length:5")==5 or m1>=5, m1)
    # 11-16 수정 확인
    lines=E("[...document.querySelectorAll('#recList .l2')].map(x=>x.textContent)")
    names=E("__QA.REC.res.pick.filter(c=>!c.fav).map(c=>c.dong)")
    d0=E("(()=>{const d=new Date(__QA.REC.res.day0);return (d.getMonth()+1)+'/'+d.getDate()})()")
    check('R9 날짜·관측소가 줄마다 표시', all(d0+'(' in l and '(' in l.split('~')[1] for l in lines), lines[:2])
    check('R10 위치는 읍·면·동 이름 (사천시 안의 동네)', all(n and n in ['향촌동','동서금동','동서동','남양동','서포면','곤양면','선구동','용현면','사남면','축동면'] for n in names) and all(any(n in t for t in items) for n in names), names)
    kinds=E("__QA.REC.res.pick.map(c=>c.kind)"); st=E("__QA.REC.res.str")
    allk=E("(()=>{const R=__QA.REC.res;return R.pick.length})()")
    check('R11 센 곳·잔잔한 곳은 지역 안 비교 → 조금 날엔 센 곳이, 사리 날엔 잔잔한 곳이 위로', (st=='weak' and kinds.count('센 곳')>=kinds.count('잔잔한 곳')) or (st=='strong' and kinds.count('잔잔한 곳')>=kinds.count('센 곳')) or st=='mid', [st,kinds])
    E("document.querySelector('#planBtn').click()"); E("document.querySelector('.ptabs [data-tab=rec]').click()"); pg.wait_for_timeout(500)
    opts=E("[...document.querySelectorAll('#recDay option')].map(o=>o.textContent)")
    E("const s=document.querySelector('#recDay');s.value='2';"); E("document.querySelector('#recGo').click()")
    for _ in range(200):
        pg.wait_for_timeout(300)
        if E("!__QA.REC.busy"): break
    d2=E("(()=>{const d=new Date(__QA.tideDay()+2*86400000);return (d.getMonth()+1)+'/'+d.getDate()})()")
    l2=E("[...document.querySelectorAll('#recList .l2')].map(x=>x.textContent)")
    check('R12 날짜 고르기 (오늘부터 7일) → 고른 날 승부 시간으로 추천', len(opts)==7 and '오늘' in opts[0] and l2 and all(d2+'(' in x for x in l2), [opts[:2], l2[:1]])
    fv=E("__QA.REC.res.pick.filter(c=>c.fav).map(c=>c.fav)"); sc=E("__QA.REC.res.pick.map(c=>c.score)")
    li=E("[...document.querySelectorAll('#recList>li')].map(l=>[l.className,l.querySelector('.l1').textContent])")
    check('R14 이 지역 즐겨찾기도 같은 점수로 함께 (지역 밖 즐겨찾기는 빠짐), 점수 높은 순', fv==['실안 내 포인트'] and all(sc[i]>=sc[i+1] for i in range(len(sc)-1)) and len(sc)==6 and any('fav' in c and '⭐ 실안 내 포인트' in t for c,t in li), [fv, [round(x,2) for x in sc], li])
    check('R13 제목·탭이 스크롤해도 위에 고정', E("getComputedStyle(document.querySelector('#planPanel .pbox h3')).position")=='sticky' and E("getComputedStyle(document.querySelector('.ptabs')).position")=='sticky')
    check('R8 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
