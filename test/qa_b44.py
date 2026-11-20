# build-44 시험 (REQ-73·74): 즐겨찾기 추천 핀 겹침 제거(⭐ 하나만, 누르면 추천 팝업), 뒤로가기 닫는 순서. 바탕은 qa_b43
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
    E("document.querySelector('.ptabs [data-tab=rec]').click()"); pg.wait_for_timeout(1200)
    for _ in range(200):
        if E("!__QA.REC.busy"): break
        pg.wait_for_timeout(300)
    E("__QA.REC.res=null; document.querySelector('#recGo').click()"); pg.wait_for_timeout(300)
    for _ in range(300):
        if E("!__QA.REC.busy&&!!__QA.REC.res&&!!__QA.REC.res.pick"): break
        pg.wait_for_timeout(300)
    E("while(window.__onBack&&window.__onBack()){}")
    n=E("__QA.REC.res.pick.length")
    # 추천 2번을 즐겨찾기로 만들고 다시 그림
    E("""(()=>{const R=__QA.REC.res,c=R.pick[1]; c.fav='테스트포인트'; __QA.saveFavs([{lat:c.la,lng:c.lo,name:'테스트포인트'}]); __QA.recRender(document.querySelector('#recList'),R);})()""")
    pins=E("__QA.REC.layer._items.filter(m=>m.options&&m.options.icon).length"); favs=E("__QA.favLayer._items.length")
    html=E("__QA.REC.layer._items.filter(m=>m.options&&m.options.icon).map(m=>m.options.icon.options.html).join('')")
    check('B1 즐겨찾기 추천은 숫자 핀을 안 그림 (겹침 없음)', pins==n-1 and '⭐' not in html and 'recpin fav' not in html, [n,pins])
    check('B2 그 자리에는 ⭐ 핀 하나만', favs==1, favs)
    check('B3 목록에는 "⭐ 이름" 그대로', '⭐ 테스트포인트' in E("document.querySelector('#recList').textContent"))
    E("__QA.favLayer._items[0].fire('click')"); pg.wait_for_timeout(500)
    pp=E("[document.querySelector('#pinPop').classList.contains('show'), document.querySelector('#pinPop').textContent]")
    check('B4 추천이 떠 있을 때 ⭐ 누르면 추천 팝업(정보 + 길 안내)', pp[0] and '테스트포인트' in pp[1] and 'TMAP' in pp[1], pp[1][:60])
    # 뒤로가기: 팝업 → 시트 → 끝(false)
    E("document.querySelector('#pinPop [data-a=sel]').click()"); pg.wait_for_timeout(400)
    E("__QA.favLayer._items[0].fire('click')"); pg.wait_for_timeout(400)
    seq=[E("[document.querySelector('#pinPop').classList.contains('show'),document.querySelector('#info').classList.contains('show')]")]
    r1=E("window.__onBack()"); seq.append(E("[document.querySelector('#pinPop').classList.contains('show'),document.querySelector('#info').classList.contains('show')]"))
    r2=E("window.__onBack()"); seq.append(E("[document.querySelector('#pinPop').classList.contains('show'),document.querySelector('#info').classList.contains('show')]"))
    r3=E("window.__onBack()")
    check('B5 뒤로가기: 팝업 먼저 → 지점 시트 → 열린 창 없으면 false(앱 뒤로)', seq==[[True,True],[False,True],[False,False]] and r1 and r2 and r3 is False, [seq,r1,r2,r3])
    E("document.querySelector('#recClear').click()"); pg.wait_for_timeout(200)
    E("__QA.favLayer._items[0].fire('click')"); pg.wait_for_timeout(500)
    st=E("[document.querySelector('#pinPop').classList.contains('show'),document.querySelector('#info').classList.contains('show'),document.querySelector('#iname').textContent]")
    check('B6 추천을 지우면 ⭐ 누를 때 지점 시트(예전처럼)', st[0] is False and st[1] and '테스트포인트' in st[2], st)
    check('B7 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
