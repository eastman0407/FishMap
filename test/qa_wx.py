# 날씨 더하기 시험 (build-37, REQ-58): ROMS 수온·단기예보 파고/강수/하늘·ASOS 지난 비·조위관측소 수온/기압·점수 배율. 바탕은 섬 나누기 시험. 가짜 Overpass: 사천 육지에서 가장 가까운 섬 하나에만 다리. 바탕은 시·군·구 추천 시험(REQ-46). 가짜 응답은 출조 계획 시험과 같음. 조석 칩 시험의 가짜 응답을 3주로 늘리고 조차가 사리·조금으로 바뀌게 함
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
    # ROMS 수온을 위치·시간마다 다르게: 동쪽일수록 따뜻, 하루에 1.5℃씩 내려감
    w0=E("[__QA.RD.pts.some(p=>p.w&&p.w.some(x=>x!=null)), __QA.tempAt(34.90,128.10,__QA.tH())]")
    w=E("(()=>{__QA.RD.pts.forEach(p=>{p.w=__QA.RD.times.map(t=>14+(p.lon-128.0)*10-(t-Date.now())/864e5*1.5);}); return [w0=true, __QA.tempAt(34.90,128.10,__QA.tH()), __QA.tempChange(34.90,128.10,__QA.tH())];})()".replace('w0=true','true'))
    w[0]=w0[0] and w0[1] is not None and abs(w0[1]-16.3)<0.01
    check('W1 ROMS 응답의 수온 칸을 읽고 위치·시간으로 보간', w[0] and w[1] is not None and abs(w[1]-(14+1.0))<0.6 and w[2] is not None and abs(w[2]+1.5)<0.2, w)
    E("window.__wav=2.0; window.__pcp='1.0mm'; __QA.WIND.key=''")
    E("_map.fire('moveend')"); pg.wait_for_timeout(3000)
    chip=E("[document.querySelector('#wxChip').textContent, document.querySelector('#warnChip').textContent, getComputedStyle(document.querySelector('#warnChip')).display]")
    check('W2 지금 카드: 수온·파고·하늘 줄 + 파도 경고(1.5m 이상)', '℃' in chip[0] and '2.0m' in chip[0] and E("document.querySelector('#skyChip').textContent.length>0") and '파고 2.0m' in chip[1] and chip[2]!='none', chip)
    check('W3 바람을 꺼 둬도 단기예보(파고·강수)는 받음', E("!!__QA.WX.data&&!__QA.WIND.on"), E("[!!__QA.WX.data,__QA.WIND.on,window.__kmaCalls]"))
    ru=E("window.__asosUrl||''")
    import re as _re
    check('W4 지난 비: 가장 가까운 ASOS(남해 295), 전날까지 요청', 'stnIds=295' in ru and 'dateCd=HR' in ru and E("__QA.RAIN.obs")==0, [ru[-80:], E("__QA.RAIN.obs")])
    E("window.__rn=6; __QA.RAIN.key=''; __QA.RAIN.obs=null"); E("_map.fire('moveend')"); pg.wait_for_timeout(2500)
    r48=E("__QA.rain48()"); wn=E("document.querySelector('#warnChip').textContent")
    check('W5 이틀 비 = ASOS 합 + 오늘 예보 강수 → 30mm 넘으면 흙탕물·민물 경고', r48 is not None and r48>=36 and '흙탕물' in wn, [r48, wn])
    # 추천: 점수 배율·등급·수온 이유
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(200)
    for _ in range(200):
        pg.wait_for_timeout(300)
        if E("!__QA.REC.busy"): break
    E("AndroidBridge._p.recBasis='area'; document.querySelector('.ptabs [data-tab=rec]').click()"); pg.wait_for_timeout(800)
    E("window.__wav=0.5; window.__rn=0; window.__pcp='강수없음'; __QA.RAIN.key=''")
    E("__QA.REC.res=null; document.querySelector('#recGo').click()")
    for _ in range(300):
        if E("!__QA.REC.busy&&!!__QA.REC.res"): break
        pg.wait_for_timeout(300)
    E("__QA.RD.pts.forEach(p=>{p.w=__QA.RD.times.map(t=>14+(p.lon-128.0)*10);})")
    E("__QA.REC.res=null; document.querySelector('#recGo').click()")
    for _ in range(300):
        if E("!__QA.REC.busy&&!!__QA.REC.res"): break
        pg.wait_for_timeout(300)
    R=E("__QA.REC.res")
    l1=E("[...document.querySelectorAll('#recList li .rcs')].map(x=>x.textContent)")
    shown=[int(x.replace('좋음','').replace('괜찮음','').replace('보통','').replace('약함','').replace('점','')) for x in l1]
    exp=[min(100,round(c['score']*125)) for c in R['pick']]
    check('W6 보이는 점수 = 계산 점수 ×1.25 (100에서 멈춤) + 등급 글자', shown==exp and all(any(g in x for g in ['좋음','괜찮음','보통','약함']) for x in l1), [l1[:3], exp[:3]])
    l2=E("[...document.querySelectorAll('#recList li .rc-c')].map(x=>x.textContent)")
    check('W7 이유에 수온과 지역 안 비교(추운 철 → 따뜻한/차가운 편)', all('℃' in x for x in l2) and R['Tmed'] is not None and R['Tmed']<15, [l2[0][-60:], R['Tmed']])
    tw=[(c['T'],c['tc']) for c in R['pick'] if not c.get('fav') and c['T'] is not None]
    check('W8 추운 철엔 이 지역 가운데값보다 따뜻한 곳 수온 점수가 높음', all((t>R['Tmed']+0.3)<= (tc>0.5) for t,tc in tw if abs(t-R['Tmed'])>0.3), tw)
    base=[c['score'] for c in R['pick']]
    E("window.__wav=3.0; __QA.REC.res=null; __QA.WIND.key=''; document.querySelector('#recGo').click()")
    for _ in range(300):
        if E("!__QA.REC.busy&&!!__QA.REC.res"): break
        pg.wait_for_timeout(300)
    R2=E("__QA.REC.res"); pens=[c['pen'] for c in R2['pick'] if not c.get('fav')]
    check('W9 파고 2.5m 넘으면 감점 + 이유에 ⚠ 파고', pens and all(abs(p-0.15)<1e-6 for p in pens) and '⚠ 파고 3.0m' in E("document.querySelector('#recList li .rc-c').textContent").replace('\\ufe0f',''), pens)
    E("window.__wav=0.5; __QA.WIND.key=''")
    E("window.__onBack()"); pg.wait_for_timeout(200)
    # 기록: 수온·파고·비 + 관측 기압(늦게 채움)
    for _ in range(100):
        if E("!__QA.REC.busy"): break
        pg.wait_for_timeout(300)
    E("__QA.placeMe(34.93,128.06,20); while(window.__onBack()){}"); E("document.querySelector('#biteFab').click()")
    for _ in range(60):
        L=E("JSON.parse(localStorage.getItem('fishmap.log.v1')||'[]')")
        if L and L[0].get('pa') is not None: break
        pg.wait_for_timeout(500)
    r=L[0] if L else {}
    check('W10 입질 기록: 수온 예보·파고·하늘·이틀 비', r.get('wt') is not None and r.get('wav') is not None and r.get('sky')=='흐림' and 'rain' in r, {k:r.get(k) for k in ['wt','wav','sky','rain']})
    check('W11 입질 기록: 가까운 조위관측소 관측 수온·기압·3시간 변화 (나중에 채움)', r.get('obsSt')=='삼천포' and r.get('obsWt')==15.2 and abs(r.get('pa',0)-1009.5)<0.01 and r.get('dpa')==-1.5, {k:r.get(k) for k in ['obsSt','obsWt','pa','dpa']})
    E("document.querySelector('#planBtn').click(); document.querySelector('.ptabs [data-tab=log]').click()"); pg.wait_for_timeout(500)
    lg=E("document.querySelector('#logList').textContent")
    check('W12 기록 목록에 기압·수온 표시', '기압 1010hPa' in lg and '수온' in lg, lg[:160])
    E("window.__shared=''; document.querySelector('#logCsv').click()")
    csv=E("window.__shared||''")
    check('W13 CSV에 새 칸 (수온·기압·파고·이틀 비)', '관측 수온(℃)' in csv and '3시간 기압 변화' in csv and '파고(m)' in csv, csv[:120])
    check('W14 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
