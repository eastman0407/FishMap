# build-48 시험 (REQ-78 L13·F27): 위성 수온 — 받기 주소, 반투명 겹침(유속 점 아래), 범례·날짜, 경계선, M8 값, 지도 이동, 실패 안내·예비 서버, 끄기, 진단. 바탕은 qa_b45
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
    E("""(()=>{window.__sst=[]; const og=window.AndroidBridge.httpGet.bind(window.AndroidBridge);
      window.__sstBody=u=>{const q=decodeURIComponent(u.split('?')[1]); const m=[...q.matchAll(/\\(([-0-9.]+)\\):(\\d+):\\(([-0-9.]+)\\)/g)].map(x=>[+x[1],+x[2],+x[3]]); const [la,lo]=m, rows=[];
        for(let a=la[0];a<=la[2]+1e-9;a+=0.01*la[1])for(let o=lo[0];o<=lo[2]+1e-9;o+=0.01*lo[1]){const A=+a.toFixed(3),O=+o.toFixed(3); rows.push(['2026-11-19T09:00:00Z',A,O,A>34.95?null:+(14+(A-34.8)*10+(O-128)*5).toFixed(2)]);}
        return JSON.stringify({table:{columnNames:['time','latitude','longitude','analysed_sst'],rows}});};
      window.AndroidBridge.httpGet=(u,id,m)=>{if(u.includes('erddap')){window.__sst.push(u); if(window.__sstFail)return setTimeout(()=>window.__nativeCb(id,-1,'x'),3); return setTimeout(()=>window.__nativeCb(id,200,window.__sstBody(u)),3);} return og(u,id,m);};})()""")
    go(13,34.92,128.07,0); pg.wait_for_timeout(800)
    btn=E("(()=>{const b=document.querySelector('#sstBtn');return b?[b.closest('#layerPanel')!=null,b.parentNode.textContent.trim()]:null})()")
    E("document.querySelector('#sstBtn').click()"); pg.wait_for_timeout(1500)
    u=E("window.__sst.slice()"); q=E(f"decodeURIComponent({u[0]!r}.split('?')[1])") if u else ''
    check('T1 P1 레이어에 🌡️ 위성 수온 → 켜면 NASA MUR(jplMURSST41) 최신 날짜를 지금 화면 범위로 요청', btn and btn[0] and '위성 수온' in btn[1] and len(u)==1 and 'jplMURSST41' in u[0] and q.startswith('analysed_sst[(last)]'), [btn,q])
    ov=E("(()=>{const o=__QA.SST.ov; if(!o)return null; const pane=o._image&&o._image.parentNode; return [o.options.opacity, pane?getComputedStyle(pane).zIndex:null, getComputedStyle(document.querySelector('#flow')).zIndex, document.querySelector('#sstBtn').classList.contains('on')]})()")
    check('T2 반투명(24%) 색 겹침이 유속 점(흐름 캔버스)보다 아래에 깔림', ov and abs(ov[0]-0.24)<1e-6 and int(ov[1] or 400)<int(ov[2]) and ov[3], ov)
    lg=E("[getComputedStyle(document.querySelector('#sstLeg')).display, document.querySelector('#sstLeg').textContent, __QA.SST.g.mn, __QA.SST.g.mx, __QA.SST.g.lines]")
    check('T3 범례에 "11/19 기준"·흰 선 0.5℃·최저~최고 숫자', lg[0]=='block' and '11/19 기준' in lg[1] and '0.5℃' in lg[1] and f"{lg[2]:.1f}" in lg[1] and f"{lg[3]:.1f}" in lg[1], lg[:2])
    check('T4 0.5℃마다 경계선을 그림', lg[4]>0, lg[4])
    E("__QA.select(34.92,128.07,'시험 자리')"); pg.wait_for_timeout(400); m8=E("document.querySelector('#iMore').textContent")
    exp=14+(34.92-34.8)*10+(128.07-128)*5
    check('T5 바다를 누르면 M8에 "🛰️ 위성 수온 x℃ (11/19 기준)"', '🛰️ 위성 수온' in m8 and '11/19 기준' in m8 and f"{exp:.1f}" in m8, [m8[-60:],round(exp,1)])
    near=E("__QA.sstAt(34.97,128.07)")
    check('T6 육지(자료 없는 칸) 바로 옆은 가까운 바다 칸 값 + "바로 앞바다" 표시, 너무 멀면 없음', near and near['near'] and E("__QA.sstAt(36.5,129.9)") is None, near)
    n0=len(u); E("__QA.SST.key&&0"); go(13,34.80,128.20,0); pg.wait_for_timeout(1700); n1=E("window.__sst.length")
    go(13,34.80,128.20,0); pg.wait_for_timeout(1500); n2=E("window.__sst.length")
    check('T7 지도를 옮기면 새 범위로 다시 받고, 같은 화면이면 다시 안 받음', n1==n0+1 and n2==n1, [n0,n1,n2])
    E("document.querySelector('#sstBtn').click()"); pg.wait_for_timeout(300)
    off=E("[__QA.SST.ov, getComputedStyle(document.querySelector('#sstLeg')).display, !/\d℃/.test([...document.querySelectorAll('#iMore>div')].find(d=>d.textContent.includes('위성')).textContent), document.querySelector('#sstBtn').classList.contains('on')]")
    check('T8 끄면 색·범례가 사라지고 M8 수온 칸은 값 대신 "꺼짐" (build-49 2×2 칸)', off==[None,'none',True,False], off)
    E("window.__sstFail=true; window.__sst=[]; document.querySelector('#sstBtn').click()"); pg.wait_for_timeout(1500)
    fl=E("[window.__sst.length, window.__sst.map(x=>x.split('/erddap')[0]), document.querySelector('#toast').textContent, document.querySelector('#sstLeg').textContent]")
    check('T9 받지 못하면 예비 서버까지 시도하고 "못 받았어요" 안내·범례 "못 받음"', fl[0]==2 and 'upwell' in fl[1][1] and '못 받았어요' in fl[2] and '못 받음' in fl[3], fl)
    E("window.__sstFail=false; document.querySelector('#sstBtn').click()")
    E("document.querySelector('#setPanel').classList.add('show'); document.querySelector('#sstTest').click()"); pg.wait_for_timeout(1200)
    dg=E("document.querySelector('#tbOut').textContent")
    check('T10 ⚙️ 진단 "위성 수온 받기 시험": 서버·칸 수·수온 범위·기준 날짜', 'coastwatch' in dg and '칸' in dg and '기준' in dg and '℃' in dg, dg[:150])
    kv=E("__QA.sstParse(JSON.stringify({table:{columnNames:['time','latitude','longitude','analysed_sst'],rows:[['2026-11-19T09:00:00Z',34.9,128,288.15],['2026-11-19T09:00:00Z',34.9,128.01,null]]}})).mn")
    check('T11 켈빈(K)으로 와도 ℃로 바꿈', abs(kv-15.0)<0.01, kv)
    check('T12 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
