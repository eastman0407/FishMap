# 오늘의 추천 시험 (REQ-48). 가짜 응답은 출조 계획 시험과 같음. 조석 칩 시험의 가짜 응답을 3주로 늘리고 조차가 사리·조금으로 바뀌게 함
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
    E("localStorage.setItem('fishmap.favs.v1',JSON.stringify([{lat:34.9105,lng:128.0405,name:'실안 내 포인트'},{lat:35.0905,lng:129.0405,name:'부산 방파제'}]))")
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(1500)
    for _ in range(200):
        if E("!__QA.REC.busy&&!!__QA.REC.today"): break
        pg.wait_for_timeout(300)
    tab=E("[document.querySelector('.ptabs button.on').dataset.tab,getComputedStyle(document.querySelector('#tabToday')).display]")
    sgn=E("document.querySelector('#todaySgg').selectedOptions[0].textContent")
    check('T1 📅 누르면 ⭐ 오늘 탭이 먼저, 지역은 지금 보는 곳(사천시) 자동', tab[0]=='today' and tab[1]!='none' and '사천시' in sgn, [tab,sgn])
    pg.screenshot(path='/tmp/shot_today.png')
    sm=E("document.querySelector('#todaySum').innerText")
    check('T2 오늘 요약: 날짜·물때·조차·해·관측소', '오늘' in sm and '조차' in sm and '해 ' in sm and '관측소' in sm, sm[:120])
    g=E("""(()=>{const t=document.querySelector('#todaySum').innerText;const m=/황금 시간\\D*(\\d\\d):(\\d\\d)~(\\d\\d):(\\d\\d)/.exec(t);return [(t.includes('도착 권장')||t.includes('지금 승부 시간')||t.includes('지금 출발')),m&&m.slice(1).join(':')]})()""")
    now=E("new Date().getHours()*60+new Date().getMinutes()")
    gt=[int(x) for x in g[1].split(':')] if g[1] else None
    check('T3 🔥 오늘의 황금 시간 (아직 안 끝난 승부 시간) + 도착 권장', g[0] and gt and (gt[2]*60+gt[3]>now or gt[2]<gt[0]), g)
    st=E("__QA.tideStrength?__QA.tideStrength(Date.now()):''")
    want={'weak':'조금 물때','strong':'사리 물때','mid':'중간 물때'}.get(st,'')
    check('T4 💡 한마디가 오늘 물때에 맞음', want and want in sm, [st, [l for l in sm.split(chr(10)) if '💡' in l]])
    L1=E("[...document.querySelectorAll('#todayList>li')].map(l=>[l.className,l.querySelector('.l1').textContent])")
    sc=E("__QA.REC.today.pick.map(c=>c.score)")
    check('T5 갈 만한 곳: 해안 5곳 + 이 지역 즐겨찾기(⭐), 점수 높은 순', len(L1)==6 and sum(1 for c,_ in L1 if 'fav' in c)==1 and any('⭐ 실안 내 포인트' in t for _,t in L1) and all(sc[i]>=sc[i+1] for i in range(5)), L1)
    code=E("(()=>{const g=__QA.sggOf(35.0905,129.0405);return g&&[g.c,g.s,g.n]})()")
    E(f"const a=document.querySelector('#todaySido');a.value='{code[1]}';a.dispatchEvent(new Event('change'))"); pg.wait_for_timeout(300)
    E(f"const b=document.querySelector('#todaySgg');b.value='{code[0]}';b.dispatchEvent(new Event('change'))")
    pg.wait_for_timeout(1000)
    for _ in range(300):
        if E("!__QA.REC.busy&&!__QA.REC.todayQ&&__QA.REC.todayKey.startsWith('"+code[0]+"')"): break
        pg.wait_for_timeout(300)
    L2=E("[...document.querySelectorAll('#todayList>li .l1')].map(l=>l.textContent)")
    check('T6 다른 지역(부산) 고르면 그 지역 즐겨찾기가 들어감', any('부산 방파제' in t for t in L2) and not any('실안' in t for t in L2), [code, L2[:3]])
    k1=E("__QA.REC.todayKey"); E("window.__onBack()"); E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(500)
    check('T7 다시 열면 같은 날·같은 지역은 다시 계산 안 함', not E("__QA.REC.busy") and E("__QA.REC.todayKey")==k1)
    E("[...document.querySelectorAll('#todayList>li')].find(l=>l.classList.contains('fav')).click()"); pg.wait_for_timeout(300)
    check('T8 즐겨찾기 줄 누르면 그 포인트 선택', E("__QA.sel()&&__QA.sel().name")=='부산 방파제', E("__QA.sel()&&__QA.sel().name"))
    check('T9 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
