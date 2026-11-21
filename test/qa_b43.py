# build-43 시험 (REQ-72): 추천 찾는 중 로딩(M10), 추천 핀 팝업(P6)·주소(브이월드)·길 안내(TMAP·카카오맵·네이버지도). 바탕은 qa_more
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
  if(url.includes('api.vworld.kr/req/address')){window.__addrCalls=(window.__addrCalls||0)+1; if(window.__addrNone)return reply(200,JSON.stringify({response:{status:'NOT_FOUND'}}));
    return reply(200,JSON.stringify({response:{status:'OK',result:[{type:'parcel',text:'경상남도 사천시 서포면 비토리 123'},{type:'road',text:'경상남도 사천시 서포면 비토길 45'}]}}));}
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
    pg.set_viewport_size({'width':411,'height':860})
    E("window.AndroidBridge._p.vworldKey='VWKEY'; window.__nav=[]; window.AndroidBridge.openExt=(u,p)=>{window.__nav.push([u,p]); return window.__noApp?'store':'ok';}; window.AndroidBridge.copyText=t=>{window.__copy=t;}")
    E("_map.fire('moveend')"); pg.wait_for_timeout(2500)
    def mid(q): r=E(f"(()=>{{const r=document.querySelector('{q}').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];}})()"); return r
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(300)
    E("AndroidBridge._p.recBasis='area'; document.querySelector('.ptabs [data-tab=rec]').click()"); pg.wait_for_timeout(1200)
    for _ in range(200):
        if E("!__QA.REC.busy"): break
        pg.wait_for_timeout(300)
    E("__QA.REC.res=null; document.querySelector('#recGo').click()"); pg.wait_for_timeout(150)
    E("while(window.__onBack&&window.__onBack()){}"); pg.wait_for_timeout(200)
    subs=set(); seen=False
    for _ in range(300):
        st=E("[document.querySelector('#loadOv').classList.contains('show'), document.querySelector('#loadSub').textContent, !!__QA.REC.busy]")
        if st[0]: seen=True; subs.add(st[1])
        if not st[2]: break
        pg.wait_for_timeout(150)
    cs=E("(()=>{const r=document.querySelector('#loadOv').getBoundingClientRect(),m=document.querySelector('#map').getBoundingClientRect();return [Math.round(r.left+r.width/2-(m.left+m.width/2)),Math.round(r.top+r.height/2-(m.top+m.height/2)),getComputedStyle(document.querySelector('#loadOv')).pointerEvents];})()")
    check('P1 추천 계산 중 지도로 나오면 가운데 반투명 로딩 (단계 n/4 표시, 지도 조작 통과)', seen and any('/4 ' in x for x in subs) and E("getComputedStyle(document.querySelector('#loadOv')).pointerEvents")=='none', [seen,list(subs)[:4]])
    pg.wait_for_timeout(900)  # build-49 U-12: 끝나면 ✓ "다 찾았어요"를 0.7초 보여 준 뒤 사라짐
    after=E("[document.querySelector('#loadOv').classList.contains('show'), document.querySelector('#toast').textContent]")
    check('P2 끝나면 로딩 사라지고 "추천 N곳을 지도에 표시" 알림', (not after[0]) and '지도에 표시' in after[1], after)
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(300); E("AndroidBridge._p.recBasis='area'; document.querySelector('.ptabs [data-tab=rec]').click()"); pg.wait_for_timeout(300)
    E("__QA.REC.ovOn=true; __QA.loadOv()"); inP=E("document.querySelector('#loadOv').classList.contains('show')"); E("__QA.REC.ovOn=false; __QA.loadOv()")
    E("while(window.__onBack&&window.__onBack()){}")
    check('P3 출조 도우미 창이 열려 있으면 로딩 안 띄움 (창 안에 진행 글이 있으니까)', not inP)
    n=E("__QA.REC.layer._items.length")
    E("__QA.REC.layer._items[0].fire('click')"); pg.wait_for_timeout(500)
    pp=E("[document.querySelector('#pinPop').classList.contains('show'), document.querySelector('#pinPop').textContent, document.querySelector('#info').classList.contains('show')]")
    first=E("document.querySelector('#recList li .rcn').textContent")
    check('P4 지도 핀(L6)을 누르면 팝업(P6): 이름·점수·승부 시간·이유, 지점 시트는 안 열림', pp[0] and not pp[2] and first[1:5] in pp[1] and '점' in pp[1] and '승부' in pp[1] and n>=3, [n,pp[1][:160],first])
    pg.wait_for_timeout(400); ad=E("document.querySelector('#ppAddr').textContent")
    check('P5 주소(브이월드): 도로명 + 지번', '비토길 45' in ad and '비토리 123' in ad and E("__QA.ADDR.last")=='OK', ad)
    E("document.querySelector('#pinPop [data-a=copy]').click()")
    check('P6 주소 복사', E("window.__copy")=='경상남도 사천시 서포면 비토길 45', E("window.__copy"))
    for k in ['tmap','kakao','naver']: E(f"document.querySelector('#pinPop [data-nav={k}]').click()")
    nv=E("window.__nav"); la,lo=E("[__QA.REC.res.pick[0].la.toFixed(6),__QA.REC.res.pick[0].lo.toFixed(6)]")
    ok=(nv[0][0].startswith('tmap://route?rGoName=') and f'rGoX={lo}' in nv[0][0] and f'rGoY={la}' in nv[0][0] and nv[0][1]=='com.skt.tmap.ku'
        and nv[1][0]==f'kakaomap://route?ep={la},{lo}&by=CAR' and nv[1][1]=='net.daum.android.map'
        and nv[2][0].startswith(f'nmap://route/car?dlat={la}&dlng={lo}&dname=') and nv[2][0].endswith('&appname=kr.fishmap.app') and nv[2][1]=='com.nhn.android.nmap')
    check('P7 길 안내 3개: TMAP·카카오맵·네이버지도 주소(좌표·장소 이름·앱 이름)', ok, nv)
    E("window.__noApp=1; document.querySelector('#pinPop [data-nav=tmap]').click(); window.__noApp=0")
    check('P8 앱이 없으면 Play 스토어로 보냈다고 알림', '스토어' in E("document.querySelector('#toast').textContent"), E("document.querySelector('#toast').textContent"))
    E("__QA.ADDR.cache.clear(); window.__addrNone=1"); E("__QA.REC.layer._items[1].fire('click')"); pg.wait_for_timeout(500)
    ad2=E("document.querySelector('#ppAddr').textContent"); E("window.__addrNone=0")
    check('P9 주소가 없으면 읍·면·동 + 좌표로 대신', '해안 근처 (' in ad2 and E("__QA.ADDR.last")=='NOT_FOUND', ad2)
    E("document.querySelector('#pinPop [data-a=sel]').click()"); pg.wait_for_timeout(400)
    s1=E("[document.querySelector('#pinPop').classList.contains('show'), document.querySelector('#info').classList.contains('show'), document.querySelector('#iname').textContent]")
    check('P10 이 자리 자세히 = 팝업 닫고 지점 시트(M8)', (not s1[0]) and s1[1] and s1[2].startswith('추천 2'), s1)
    E("document.querySelector('#closeInfo').click()"); E("__QA.REC.layer._items[0].fire('click')"); pg.wait_for_timeout(300)
    E("window.__onBack()"); b1=E("document.querySelector('#pinPop').classList.contains('show')")
    E("__QA.REC.layer._items[0].fire('click')"); pg.wait_for_timeout(300); E("document.querySelector('#pinPop [data-a=fav]').click()"); pg.wait_for_timeout(400)
    fv=E("[document.querySelector('#info').classList.contains('show'), getComputedStyle(document.querySelector('#namebox')).display]")
    check('P11 뒤로가기로 팝업 닫힘, ☆ 저장 = 지점 시트 + 이름 칸', (not b1) and fv[0] and fv[1]!='none', [b1,fv])
    E("__QA.pointView('none')")
    for _ in range(200):
        if E("!__QA.REC.busy&&!!__QA.REC.res&&!!__QA.REC.res.pick"): break
        pg.wait_for_timeout(300)
    E("while(window.__onBack&&window.__onBack()){}"); E("__QA.REC.layer._items[0].fire('click')"); pg.wait_for_timeout(300)
    check('P12 추천 탭(P4-1) 핀을 다시 눌러도 같은 팝업', E("document.querySelector('#pinPop').classList.contains('show')"))
    d=E("__QA.runDiag()"); check('P13 진단에 주소 찾기 결과', '주소 찾기(브이월드)' in d)
    check('P14 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
