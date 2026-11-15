# 안전 알림 시험 (REQ-45). 가짜 응답은 출조 계획 시험과 같음. 앱 밖(브라우저)에서는 예약을 window.__alarms에 기록 조석 칩 시험의 가짜 응답을 3주로 늘리고 조차가 사리·조금으로 바뀌게 함
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
    go(13,34.92,128.07,0)
    for _ in range(60):
        if E("!!__QA.TIDE.cur"): break
        pg.wait_for_timeout(500)
    rk=E("""(async()=>{await __QA.rockEnsure();return __QA.ROCK.data.filter(r=>r[2]===1&&r[3]!=null&&r[3]<-0.6&&r[3]>-2.2&&Math.abs(r[0]-34.9)<0.15&&Math.abs(r[1]-128.05)<0.25)[0]})()""")
    lat,lng=rk[0]+0.0007,rk[1]   # 약 78m 북쪽
    E(f"__QA.select({lat},{lng},'바위 옆 포인트')"); pg.wait_for_timeout(300)
    E("document.querySelector('#alertBtn').click()"); pg.wait_for_timeout(1500)
    pg.screenshot(path='/tmp/shot_card.png')
    A=E("Object.values(window.__alarms||{})")
    S=E("JSON.parse(AndroidBridge.getPref('alertSet')||'null')")
    kinds=sorted(x['kind'] for x in S['items']) if S else []
    check('A1 🔔 누르면 다음 만조 + 300m 안 간출암 잠김, 2개 알림 예약', len(A)==2 and kinds==['hi','rock'], [kinds, [a['title'] for a in A]])
    lead=[round((x['ms']-x['at'])/60000) for x in S['items']] if S else []
    now=E("Date.now()")
    check('A2 알림 시각 = 1시간 전 (기본), 이미 지났으면 바로', all(l==60 or abs(x['at']-now)<15000 for l,x in zip(lead,S['items'])), lead)
    rs=[x for x in S['items'] if x['kind']=='rock'][0]
    ok=E(f"(()=>{{const s=__QA.TIDE.cur.ser,d={rk[3]};const a=__QA.tideAtMs(s,{rs['ms']}),b=__QA.tideAtMs(s,{rs['ms']}-600000);return [b,a,-d,b<-d&&a>=-d]}})()")
    check('A3 바위 잠김 시각이 맞음 (그 10분 전엔 드러남, 그때 잠김)', ok[3], ok)
    hi=[x for x in S['items'] if x['kind']=='hi'][0]
    nx=E("__QA.tideExtremes(__QA.TIDE.cur.ser,Date.now(),Date.now()+86400e3).find(e=>e.hi).ms")
    check('A4 만조 시각 = 다가오는 만조', abs(hi['ms']-nx)<60000, [hi['title']])
    dbg=E("(()=>{try{__QA.updateUI();return [document.querySelector('#alertBtn').textContent,!!__QA.alertHere(__QA.sel().lat,__QA.sel().lng)]}catch(e){return String(e.stack)}})()")
    check('A5 버튼이 🔔 켜짐으로 바뀜', E("document.querySelector('#alertBtn').textContent")=='🔔 켜짐', dbg)
    E("document.querySelector('#alertBtn').click()"); pg.wait_for_timeout(300)
    check('A6 다시 누르면 끄고 예약 모두 취소', E("Object.keys(window.__alarms||{}).length")==0 and E("document.querySelector('#alertBtn').textContent")=='🔔', E("Object.keys(window.__alarms||{})"))
    E("const s=document.querySelector('#alertLead');s.value='30';s.dispatchEvent(new Event('change'))")
    E("__QA.select(34.70,128.60,'먼 바다')"); pg.wait_for_timeout(300)
    E("document.querySelector('#alertBtn').click()"); pg.wait_for_timeout(1500)
    S2=E("JSON.parse(AndroidBridge.getPref('alertSet')||'null')")
    check('A7 ⚙ 30분 전 설정 반영 + 바위 없는 곳은 만조만', S2 and [x['kind'] for x in S2['items']]==['hi'] and all(round((x['ms']-x['at'])/60000)==30 or x['at']-E("Date.now()")<15000 for x in S2['items']), S2 and [(x['kind'],round((x['ms']-x['at'])/60000)) for x in S2['items']])
    check('A8 한 번에 한 곳만 (이전 지점 알림은 취소)', E("Object.keys(window.__alarms||{}).length")==len(S2['items']))
    check('A9 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
