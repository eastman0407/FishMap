# build-45 시험 (REQ-75): 누르는 범위 44+, 눌린 모양, 못 누르는 상태, 진동, 스프링, 되돌리기. 바탕은 qa_b44
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
    E("window.__hapN=[]; window.AndroidBridge.haptic=k=>window.__hapN.push(k)")
    E("__QA.select(34.92,128.07,'시험 자리')"); pg.wait_for_timeout(900)
    # 1. 누르는 범위: 보이는 상자 + ::after 상자 중 큰 쪽이 44 이상, 가운데를 누르면 자기 자신(이웃에 가려지지 않음)
    HIT="""(sel)=>[...document.querySelectorAll(sel)].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect(),a=getComputedStyle(e,'::after');
      const aw=a.content&&a.content!=='none'?parseFloat(a.width)||0:0, ah=a.content&&a.content!=='none'?parseFloat(a.height)||0:0;
      const cx=r.left+r.width/2, cy=r.top+r.height/2, hit=document.elementFromPoint(cx,cy);
      return [e.id||e.className||e.textContent.trim().slice(0,6), Math.round(Math.max(r.width,aw)), Math.round(Math.max(r.height,ah)), !!hit&&(hit===e||e.contains(hit))];})"""
    def hit(sel): return E(f"({HIT})('{sel}')")
    a=[]
    for q in ['#nowFold','#nowSeg button','#starBtn','#alertBtn','#biteBtn','#closeInfo','.search .go','#infoGrip','#nowGrip']: a+=hit(q)
    small=[x for x in a if x[1]<44 or x[2]<44]; blocked=[x for x in a if not x[3]]
    check('H1 메인·시트 버튼 누르는 범위 모두 44 이상', a and not small, small or len(a))
    check('H2 버튼 가운데를 누르면 자기 자신 (넓힌 범위가 이웃을 가리지 않음)', not blocked, blocked)
    E("document.querySelector('#setBtn')&&document.querySelector('#setBtn').click(); document.querySelector('#setPanel').classList.add('show')"); pg.wait_for_timeout(300)
    cb=E("[...document.querySelectorAll('#setPanel label')].filter(l=>l.querySelector('input[type=checkbox]')&&l.offsetParent).map(l=>Math.round(l.getBoundingClientRect().height))")
    check('H3 설정 체크 줄 높이 44 이상', cb and min(cb)>=44, cb)
    E("document.querySelector('#setPanel').classList.remove('show')")
    st=E("(()=>{const b=document.querySelector('#starBtn'),c=getComputedStyle(b);return [c.transitionDuration, [...document.styleSheets].some(s=>{try{return [...s.cssRules].some(r=>/button:active/.test(r.selectorText||'')&&/scale/.test(r.cssText))}catch(e){return false}})];})()")
    check('H4 눌린 모양: 누르면 0.08초 안에 작아지고 밝아짐', '0.08s' in st[0] and st[1], st)
    E("__QA.REC.busy=true; __QA.recBtn()"); d=E("(()=>{const b=document.querySelector('#recGo');return [b.disabled,b.textContent,getComputedStyle(b).opacity];})()")
    E("__QA.REC.busy=false; __QA.recBtn()"); d2=E("[document.querySelector('#recGo').disabled,document.querySelector('#recGo').textContent]")
    check('H5 계산 중엔 추천 받기 흐리게 + "계산 중…", 끝나면 원래대로', d==[True,'계산 중…','0.45'] and d2==[False,'이 지역 추천 받기'], [d,d2])
    # 진동
    E("window.__hapN=[]; document.querySelector('#biteBtn').click()"); pg.wait_for_timeout(200)
    h1=E("window.__hapN.slice()")
    E("window.AndroidBridge._p.haptic='0'; window.__hapN=[]; document.querySelector('#biteBtn').click()"); h2=E("window.__hapN.length"); E("window.AndroidBridge._p.haptic='1'")
    check('H6 입질 기록하면 확인 진동, 설정에서 끄면 안 울림', h1==['done'] and h2==0, [h1,h2])
    E("window.__hapN=[]; __QA.INFO_DRAG.animate(true)"); pg.wait_for_timeout(450); f1=E("window.__hapN.slice()")
    E("__QA.INFO_DRAG.animate(true)"); pg.wait_for_timeout(450); f2=E("window.__hapN.length")
    E("__QA.INFO_DRAG.animate(false)"); pg.wait_for_timeout(450); f3=E("window.__hapN.length")
    sp=E("(()=>{const e=document.querySelector('#info');e.classList.add('snap');const t=getComputedStyle(e).transitionTimingFunction+' '+getComputedStyle(e).transitionDuration;e.classList.remove('snap');return t;})()")
    check('H7 시트 접기·펴기 바뀔 때만 톡 + 스프링(끝에서 살짝 넘침, 0.3초)', f1==['tick'] and f2==1 and f3==2 and '1.35' in sp and '0.3s' in sp, [f1,f2,f3,sp])
    # 되돌리기: 입질 기록 지우기
    n0=E("__QA.loadLog().length"); E("__QA.renderLog()")
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(200); E("document.querySelector('.ptabs [data-tab=log]')&&document.querySelector('.ptabs [data-tab=log]').click()"); pg.wait_for_timeout(300)
    E("document.querySelector('#logList>li [data-del]').click()"); n1=E("__QA.loadLog().length"); tt=E("document.querySelector('#toast').textContent")
    E("document.querySelector('#toast .undo').click()"); n2=E("__QA.loadLog().length")
    check('H8 입질 기록 지우면 바로 지워지고 [되돌리기]로 복원', n1==n0-1 and '되돌리기' in tt and n2==n0, [n0,n1,n2,tt])
    E("while(window.__onBack&&window.__onBack()){}"); E("__QA.select(34.92,128.07,'시험 자리')"); pg.wait_for_timeout(500)
    E("__QA.saveFavs([{name:'A',lat:34.9,lng:128.0},{name:'시험 자리',lat:34.92,lng:128.07}]); __QA.updateUI()")
    E("document.querySelector('#starBtn').click()"); m1=E("__QA.loadFavs().length"); E("document.querySelector('#toast .undo').click()"); m2=E("__QA.loadFavs().map(f=>f.name)")
    check('H9 즐겨찾기 빼기도 [되돌리기]로 복원', m1==1 and m2==['A','시험 자리'], [m1,m2])
    E("document.querySelector('#favPanel').classList.add('show'); __QA.renderFavList()"); pg.wait_for_timeout(200)
    fd=hit('#favPanel .del')
    E("document.querySelector('#favPanel .del').click()"); k1=E("__QA.loadFavs().length"); E("document.querySelector('#toast .undo').click()"); k2=E("__QA.loadFavs().length")
    check('H10 즐겨찾기 창 ✕: 누르는 범위 44+, 지우면 되돌리기', fd and all(x[1]>=44 and x[2]>=44 for x in fd) and k1==1 and k2==2, [fd,k1,k2])
    E("document.querySelector('#favPanel').classList.remove('show')")
    E("__QA.REC.res={pick:[{la:34.91,lo:128.05,score:.7,isl:'l',dong:'향촌동',kind:'갯바위',wins:[]}],sg:{n:'사천시',s:'경남',c:'x'},kindSrc:'osm'}; __QA.recRender(document.querySelector('#recList'),__QA.REC.res)")
    p0=E("__QA.REC.layer._items.length"); E("document.querySelector('#recClear').click()"); p1=E("__QA.REC.layer._items.length")
    E("document.querySelector('#toast .undo').click()"); p2=E("__QA.REC.layer._items.length")
    check('H11 추천 핀 지우기도 [되돌리기]로 복원', p0==1 and p1==0 and p2==1, [p0,p1,p2])
    pin=E("(()=>{const d=document.createElement('div');d.innerHTML='<div class=recpin>1</div><div class=favpin>⭐</div>';document.body.appendChild(d);const r=[...d.children].map(e=>{const a=getComputedStyle(e,'::after');return [parseFloat(a.width),parseFloat(a.height)];});d.remove();return r;})()")
    check('H12 지도 핀(추천·별)도 누르는 범위 44', all(w>=44 and h>=44 for w,h in pin), pin)
    check('H13 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
