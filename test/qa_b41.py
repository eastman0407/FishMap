# build-41 시험 (REQ-70): 지점 시트를 지도 위 떠 있는 창으로(지도 고정), 손가락 따라가는 접기·펴기(M3·M8), 넓은 잡기 면적, 1/4·튕김 기준. 바탕은 qa_more
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
    pg.set_viewport_size({'width':411,'height':860})
    E("_map.fire('moveend')"); pg.wait_for_timeout(2500)
    def rect(q): return E(f"(()=>{{const r=document.querySelector('{q}').getBoundingClientRect();return [Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height),Math.round(r.bottom)];}})()")
    def mid(q): r=rect(q); return [r[0]+r[2]/2, r[1]+r[3]/2]
    def drag(p,dy,slow=True,release=True):
        pg.mouse.move(p[0],p[1]); pg.mouse.down(); n=max(1,int(abs(dy)//10)); 
        for k in range(1,n+1):
            pg.mouse.move(p[0],p[1]+dy*k/n)
            if slow: pg.wait_for_timeout(40)
        if slow: pg.wait_for_timeout(200)
        if release: pg.mouse.up(); pg.wait_for_timeout(350)
    C="(()=>{const c=__QA.map.getCenter();return [+c.lat.toFixed(6),+c.lng.toFixed(6)];})()"
    E("__QA.select(34.92,128.07,'시험 자리')"); pg.wait_for_timeout(900)
    m0=rect('#map'); c0=E(C); full=rect('#info')[3]
    FO="document.querySelector('#info').classList.contains('fold')"
    # 끄는 중 손가락 따라오기 (시트 가운데 바람 줄을 잡음 = 넓은 면적)
    p=mid('#iMore'); drag(p,30,release=False); hmid=rect('#info')[3]
    check('D1 M8: 시트 가운데를 잡고 30px 내리면 높이가 손가락만큼 줄어듦 (놓기 전)', abs((full-hmid)-30)<=3, [full,hmid])
    pg.mouse.up(); pg.wait_for_timeout(350); back=rect('#info')[3]
    check('D2 1/4 덜 끌고 놓으면 원래대로', abs(back-full)<=2 and not E(FO), [full,back])
    mini=E("__QA.infoMiniH()"); trav=full-mini
    drag(mid('#iMore'),int(trav*0.3)+5); h=rect('#info'); st=rect('#info .stats')
    check('D3 1/4 넘게 끌고 놓으면 끝까지 접힘: 머리 + 숫자 4칸(M8-3)까지만', E(FO) and abs(h[3]-mini)<=2 and st[4]<=h[4], [h,st,mini])
    m1=rect('#map'); c1=E(C)
    check('D4 시트를 접어도 지도(M4) 크기·위치 그대로', m1==m0 and c1==c0, [m0,m1,c0,c1])
    p=mid('#info .stats'); drag(p,-30,slow=False); 
    check('D5 빠르게 위로 튕기면(30px) 펴짐', not E(FO) and abs(rect('#info')[3]-full)<=3, rect('#info'))
    pg.mouse.click(*mid('#infoGrip')); pg.wait_for_timeout(350); a1=E(FO)
    pg.mouse.click(*mid('#iMore')); pg.wait_for_timeout(350); a2=E(FO)
    pg.mouse.click(*mid('#infoGrip')); pg.wait_for_timeout(350); a3=E(FO)
    check('D6 손잡이 톡 = 접기·펴기, 다른 곳 톡은 그대로', a1 and a2 and not a3, [a1,a2,a3])
    drag(mid('#starBtn'),40); nb=E("getComputedStyle(document.querySelector('#namebox')).display")
    E("document.querySelector('#info').classList.contains('fold')&&0"); pg.mouse.click(*mid('#info .stats')); pg.wait_for_timeout(100)
    if E(FO): pg.mouse.click(*mid('#infoGrip')); pg.wait_for_timeout(350)
    pg.mouse.click(*mid('#starBtn')); pg.wait_for_timeout(300); nb2=E("getComputedStyle(document.querySelector('#namebox')).display")
    check('D7 버튼 위에서 시작한 끌기는 버튼이 안 눌림, 그냥 누르면 버튼 동작', nb=='none' and nb2!='none', [nb,nb2])
    E("document.querySelector('#namebox').style.display='none'"); E("__QA.updateUI()")
    lg=rect('.legend'); fb=rect('#biteFab'); inf=rect('#info')
    check('D8 범례(M5)·입질 버튼(M6)이 시트 위로 따라 올라가 안 가려짐', lg[4]<=inf[1] and fb[4]<=inf[1], [lg,fb,inf])
    # M3 지금 카드
    nf=rect('#nowCard'); m2=rect('#map')
    drag(mid('#wxChip'),-80); n1=rect('#nowCard'); mi=E("document.querySelector('#nowCard').classList.contains('mini')")
    check('D9 M3: 카드 가운데를 잡고 위로 끌면 접힘 (지도 그대로)', mi and n1[3]<nf[3]-40 and rect('#map')==m2, [nf,n1,mi])
    sd=rect('.side')
    check('D10 접힌 카드 아래로 M2가 따라 올라감', n1[4]<=sd[1]<=n1[4]+12, [n1,sd])
    drag(mid('#nowCard'),70); n2=rect('#nowCard'); mi2=E("document.querySelector('#nowCard').classList.contains('mini')")
    check('D11 아래로 끌면 펴짐', (not mi2) and abs(n2[3]-nf[3])<=3, [nf,n2])
    pg.mouse.click(*mid('#nowGrip')); pg.wait_for_timeout(350); g1=E("document.querySelector('#nowCard').classList.contains('mini')")
    pg.mouse.click(*mid('#nowGrip')); pg.wait_for_timeout(350); g2=E("document.querySelector('#nowCard').classList.contains('mini')")
    pg.mouse.click(*mid('#nowFold')); pg.wait_for_timeout(350); g3=E("document.querySelector('#nowCard').classList.contains('mini')")
    pg.mouse.click(*mid('#nowFold')); pg.wait_for_timeout(350)
    check('D12 손잡이(M3-7)·▴ 톡 = 접기·펴기', g1 and not g2 and g3, [g1,g2,g3])
    pg.mouse.click(*mid('#tideChip')); pg.wait_for_timeout(400); p3=E("document.querySelector('#tidePanel').classList.contains('show')"); E("while(window.__onBack&&window.__onBack()){}")
    drag(mid('#tideChip'),-60); pg.wait_for_timeout(200); p3b=E("document.querySelector('#tidePanel').classList.contains('show')")
    pg.mouse.click(*mid('#nowFold')); pg.wait_for_timeout(350)
    check('D13 🌊 줄 그냥 누르면 오늘 조석(P3), 끌면 안 열림', p3 and not p3b, [p3,p3b])
    E("__QA.select(34.92,128.07,'시험 자리')"); pg.wait_for_timeout(600)
    H=E("document.querySelector('#map').clientHeight"); ih=rect('#info')[3]
    ll=E(f"(()=>{{const p=__QA.map.containerPointToLatLng([200,{H}-40]);return [p.lat,p.lng];}})()")
    E(f"__QA.select({ll[0]},{ll[1]},'아래쪽 자리')"); pg.wait_for_timeout(900)
    y=E(f"__QA.map.latLngToContainerPoint([{ll[0]},{ll[1]}]).y")
    check('D14 시트에 가려질 점을 고르면 그때 한 번만 지도를 올려 보이게', y < H-ih, [y,H,ih])
    check('D15 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
