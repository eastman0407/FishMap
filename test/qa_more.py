# build-38 시험 (REQ-59~64): 카드 접기·숫자 표시·바람/달/구름·점수 점검·조석 시험·섬 다리 미리 넣기. 바탕은 날씨 더하기 시험(REQ-58): ROMS 수온·단기예보 파고/강수/하늘·ASOS 지난 비·조위관측소 수온/기압·점수 배율. 바탕은 섬 나누기 시험. 가짜 Overpass: 사천 육지에서 가장 가까운 섬 하나에만 다리. 바탕은 시·군·구 추천 시험(REQ-46). 가짜 응답은 출조 계획 시험과 같음. 조석 칩 시험의 가짜 응답을 3주로 늘리고 조차가 사리·조금으로 바뀌게 함
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
  if(url.includes('getVilageFcst')){window.__kmaCalls=(window.__kmaCalls||0)+1; const p2=v=>String(v).padStart(2,'0'), items=[];
    for(let h=-6;h<60;h++){const d=new Date(Date.now()+h*3600e3); const fd=`${d.getFullYear()}${p2(d.getMonth()+1)}${p2(d.getDate())}`, ft=p2(d.getHours())+'00';
      for(const [c,v] of [['UUU','2.0'],['VVV','-1.0'],['WAV',String(window.__wav||0.5)],['PCP',h<=0?(window.__pcp||'강수없음'):'강수없음'],['SKY','4'],['PTY','0']])items.push({category:c,fcstDate:fd,fcstTime:ft,fcstValue:v});}
    return reply(200,JSON.stringify({response:{header:{resultCode:'00'},body:{items:{item:items},totalCount:items.length}}}));}
  if(url.includes('AsosHourlyInfoService')){window.__asosCalls=(window.__asosCalls||0)+1; window.__asosUrl=url; const items=[];
    for(let h=0;h<48;h++)items.push({tm:'x',stnId:'295',stnNm:'남해',rn:h<6?String(window.__rn||0):'',pa:'1012.0'});
    return reply(200,JSON.stringify({response:{header:{resultCode:'00'},body:{items:{item:items},totalCount:48}}}));}
  if(url.includes('/dtRecent/')){window.__dtCalls=(window.__dtCalls||0)+1; const c=new URL(url).searchParams.get('obsCode'); const p2=v=>String(v).padStart(2,'0');
    if(c!=='DT_0061'&&c!=='DT_0014'){const la=36+(c.charCodeAt(6)%9)*0.1;return reply(200,JSON.stringify({response:{header:{resultCode:'00'},body:{items:{item:[{obsvtrNm:c,lat:String(la),lot:'126.5',obsrvnDt:'2026-11-20 00:00',atmpr:'1015.0',wtem:'14.0'}]}}}}));}
    const n=+new URL(url).searchParams.get('numOfRows')||10, rows=[]; for(let h=0;h<Math.min(n,8);h++){const d=new Date(Date.now()-(7-h)*3600e3);
      rows.push({obsvtrNm:c==='DT_0061'?'삼천포':'통영',lat:c==='DT_0061'?'34.9250':'34.8270',lot:c==='DT_0061'?'128.0700':'128.4340',obsrvnDt:`${d.getFullYear()}-${p2(d.getMonth()+1)}-${p2(d.getDate())} ${p2(d.getHours())}:00`,atmpr:String(1013-h*0.5),wtem:'15.2'});}
    return reply(200,JSON.stringify({response:{header:{resultCode:'00'},body:{items:{item:rows}}}}));}
  if(url.includes('/api/interpreter')){window.__ovpCalls=(window.__ovpCalls||0)+1; if(window.__ovpFail)return reply(-1,'x');
    return reply(200,JSON.stringify({elements:window.__ovp||[]}));}
  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""")
# 기준 만조: 오늘 0시(KST)+11시41분
src=src.replace('BRIDGE=r"""','BRIDGE=r"""window.__HI0=(()=>{const d=new Date();d.setHours(0,0,0,0);return d.getTime()+(11*60+41)*60000;})();')
assert 'tideFcstHghLw' in src
exec(src+'''
    go(12,34.92,128.07,0)
    for _ in range(60):
        if E("!!__QA.TIDE.cur&&__QA.RD.pts.length>0&&!__QA.RD.loading"): break
        pg.wait_for_timeout(500)
    E("__QA.RD.pts.forEach(p=>{p.w=__QA.RD.times.map(t=>14+(p.lon-128.0)*10-(t-Date.now())/864e5*1.5);})")
    E("_map.fire('moveend')"); pg.wait_for_timeout(3000)
    ch=E("[document.querySelector('#wxChip').textContent, document.querySelector('#wxChip').innerHTML]")
    check('M1 수온 줄: (어제보다 ±x) 문구, 하루 글자 없음', ('어제보다' in ch[0] or '내일' in ch[0]) and '하루' not in ch[0], ch[0])
    check('M2 그림 글자 뒤 FE0F + 숫자는 따로(고정폭 굵게)', '️' in ch[1] and 'class="num"' in ch[1] and 'class="emo"' in ch[1], ch[1][:120])
    E("document.querySelector('#nowFold').click()"); pg.wait_for_timeout(200)
    f=E("[document.querySelector('#nowCard').classList.contains('mini'), document.querySelector('#nowMini').textContent, getComputedStyle(document.querySelector('#tideChip')).display, window.AndroidBridge._p.nowMini, document.querySelector('#planPanel').classList.contains('show')]")
    check('M3 ▴ 누르면 한 줄(다음 물때·수온)로 접히고 상태 저장, 출조 도우미는 안 열림', f[0] and '℃' in f[1] and '🌊' in f[1] and f[2]=='none' and f[3]=='1' and not f[4], f)
    E("__QA.updateTideChips()"); f2=E("document.querySelector('#nowCard').classList.contains('mini')")
    E("document.querySelector('#nowFold').click()"); pg.wait_for_timeout(200)
    f3=E("[document.querySelector('#nowCard').classList.contains('mini'), getComputedStyle(document.querySelector('#wxChip')).display, window.AndroidBridge._p.nowMini]")
    check('M4 다시 그려도 접힌 채 유지, ▾ 누르면 펴짐', f2 and not f3[0] and f3[1]!='none' and f3[2]=='0', [f2,f3])
    ws=E("(()=>{const th=__QA.tH(); return ['290','110','200'].map(f=>{const r=__QA.windSide(th,34.92,128.07,+f);return r&&r.k;});})()")
    check('M5 바람 판정: 서북서풍(가짜 예보) → 바다가 서쪽이면 앞바람, 동쪽이면 뒷바람, 남쪽이면 옆바람', ws==['앞','뒤','옆'], ws)
    far=E("__QA.windSide(__QA.tH()+24*10,34.92,128.07,290)")
    check('M6 바람 예보 범위 밖(10일 뒤)은 판정 안 함', far is None, far)
    sd=E("__QA.seaDir(34.92,128.07)")
    check('M7 바다 쪽 방향을 찾음 (화면 바다판별 또는 예보 칸)', sd is not None and 0<=sd<360, sd)
    mp=E("[__QA.moonPhase(Date.UTC(2026,10,24,14)), __QA.moonPhase(Date.UTC(2026,10,9,7)), __QA.moonTimes(Date.UTC(2026,10,20)-9*3600e3,37.57,126.98)]")
    check('M8 달: 2026-11-24 보름(98%↑), 11-09 그믐(2%↓), 뜨고 지는 시각 계산', mp[0]['pct']>=98 and mp[0]['name']=='보름달' and mp[1]['pct']<=2 and mp[2]['rise'] and mp[2]['set'], [mp[0]['pct'],mp[1]['pct']])
    E("__QA.select(34.92,128.07,'시험 자리')"); pg.wait_for_timeout(500)
    im=E("document.querySelector('#iMore').innerHTML")
    check('M9 지점 시트에 바람(앞/뒷/옆)·달·하늘', '🌙' in im and any(x in im for x in ['앞바람','뒷바람','옆바람','바람 약함']) and '흐림' in im, im[:200])
    E("while(window.__onBack()){}")
    E("__QA.placeMe(34.93,128.06,20); while(window.__onBack()){}"); E("document.querySelector('#biteFab').click()"); pg.wait_for_timeout(800)
    L=E("JSON.parse(localStorage.getItem('fishmap.log.v1')||'[]')")
    check('M10 입질 기록에 그때 점수(0~100)와 출처', bool(L) and isinstance(L[0].get('sc'),int) and 0<=L[0]['sc']<=100 and L[0].get('scs') in ('추천','계산'), {k:L[0].get(k) for k in ['sc','scs']} if L else L)
    E("localStorage.setItem('fishmap.log.v1',JSON.stringify([...[85,90,82,70,72,66,55,40,88,91].map((v,i)=>({t:i,sc:v})),{t:99},{t:98}]))")
    E("document.querySelector('#scBtn').click()"); sc=E("[document.querySelector('#scOut').textContent, __QA.scoreCheck(JSON.parse(localStorage.getItem('fishmap.log.v1'))).rows.map(r=>r.n)]")
    check('M11 점수 점검 표: 점수대별 입질 수·비율, 예전 기록 수, 10개 넘으면 비교 안내', sc[1]==[5,3,1,1] and '50%' in sc[0] and '예전 기록 2개' in sc[0] and '잘 맞는' in sc[0], sc)
    E("localStorage.setItem('fishmap.log.v1',JSON.stringify([{t:1,sc:70}]))"); E("document.querySelector('#scBtn').click()")
    check('M12 기록이 적으면 "아직 자료가 적어요"', '자료가 적어요' in E("document.querySelector('#scOut').textContent"))
    E("window.AndroidBridge._p.dataKey='SeCrEtKeY12+/=abc'")
    E("document.querySelector('#tbTest').click()")
    t=''
    for _ in range(40):
        t=E("document.querySelector('#tbOut').textContent")
        if '── xml' in t: break
        pg.wait_for_timeout(250)
    check('M13 ⚙ 조석 시험: json·xml 응답코드·앞부분 표시, 키는 안 보임', 'json' in t and '── xml' in t and '결과코드' in t and 'SeCrEtKeY' not in t and 'serviceKey=***' in t, t[:200])
    mk=E("__QA.keyMask('a?serviceKey=SeCrEtKeY12%2B%2F%3Dabc&x=1 SeCrEtKeY12+/=abc')")
    check('M14 키 가리기 (원문·인코딩 둘 다)', 'SeCrEtKeY' not in mk, mk)
    E("window.AndroidBridge._p.dataKey='K'")
    k=E("""(async()=>{const all=await __QA.recLoad(), sg=all.find(r=>r.n==='사천시'), rs=Object.keys(sg.is||{}).map(Number); window.__ovpCalls=0;
      __QA.REC.pre={made:'2026-11-20',sgg:{[sg.c]:{r:[rs[0]],d:'2026-11-20'}}}; const f=await __QA.REC_kind(sg);
      const i0=sg.ri.indexOf(rs[0]), i1=sg.ri.findIndex(r=>r>=0&&r!==rs[0]);
      return [__QA.REC.kindSrc, f(i0), i1>=0?f(i1):'f', window.__ovpCalls, rs.length];})()""")
    check('M15 미리 넣은 다리 자료가 있으면 지도 서버에 묻지 않고 그 자료로 판별', k[0]=='pre' and k[1]=='b' and k[2]=='f' and k[3]==0, k)
    k2=E("""(async()=>{const all=await __QA.recLoad(), sg=all.find(r=>r.n==='사천시'); __QA.REC.pre={made:'x',sgg:{}}; window.__ovpCalls=0; window.__ovpFail=1;
      const f=await __QA.REC_kind(sg); window.__ovpFail=0; return [__QA.REC.kindSrc, window.__ovpCalls, __QA.REC.ovpErr, !!__QA.REC.ovpRaw];})()""")
    check('M16 자료에 없는 곳은 지도 서버 4곳 × 2바퀴까지 다시 묻고, 못 받으면 추정', k2[0]=='guess' and k2[1]==8 and k2[3], k2)
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(300)
    E("document.querySelector('.ptabs [data-tab=plan]')&&document.querySelector('.ptabs [data-tab=plan]').click()")
    for _ in range(100):
        if E("!!__QA.PLAN.res&&!__QA.PLAN.busy"): break
        pg.wait_for_timeout(300)
    pl=E("[...document.querySelectorAll('#planList li .l2')].slice(0,3).map(x=>x.textContent)")
    check('M17 출조 계획 줄마다 달 밝기 (가까운 날은 하늘)', bool(pl) and all('🌙' in x for x in pl) and any('흐림' in x for x in pl), pl)
    check('M18 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
