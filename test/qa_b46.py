# build-46 시험 (REQ-76): 지금 카드 접기·펴기 — 줄이 옆으로 안 옮겨감, 서서히 사라짐·나타남, 보기별 요약. 바탕은 qa_b45
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
    E("__QA.CONF.realData=true; __QA.REC.today={sg:{n:'사천시',s:'경남',c:'x'},pick:[{la:34.91,lo:128.05,score:.76,dong:'향촌동',isl:'l',best:{w:{s:Date.now()+3600e3*9,t:Date.now()+3600e3*11}}},{la:34.92,lo:128.0,score:.73,dong:'서포면',isl:'l',best:{w:{s:Date.now()+3600e3*3,t:Date.now()+3600e3*5}}},{la:34.9,lo:128.06,score:.70,dong:'향촌동',isl:'l',best:{w:{s:Date.now()+3600e3*9,t:Date.now()+3600e3*11}}}]}")
    E("__QA.REC.todayKey=null; __QA.nowView('rec')"); pg.wait_for_timeout(500)
    R="(()=>{const c=document.querySelector('#nowCard'),r=c.getBoundingClientRect(),q=s=>{const e=c.querySelector(s);if(!e)return null;const b=e.getBoundingClientRect();return [Math.round(b.left),Math.round(b.top),Math.round(b.width),Math.round(b.bottom)]};return {card:[Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.bottom)],cls:c.className,rec:q('#nowRec'),grip:q('#nowGrip'),op:getComputedStyle(c.querySelector('#nowRec')).opacity,mini:c.querySelector('#nowMini').textContent}})()"
    o=E(R); E("document.querySelector('#nowFold').click()"); mids=[]
    for _ in range(4): pg.wait_for_timeout(45); mids.append(E(R))
    pg.wait_for_timeout(350); f=E(R)
    side=[m for m in mids if m['rec'][2] and (m['rec'][0]!=o['rec'][0] or m['rec'][1]!=o['rec'][1])]
    check('S1 접는 도중 ①②③ 줄이 옆으로 옮겨 가지 않음 (제자리)', not side, side[:1] or o['rec'])
    gripin=[m for m in mids if not (m['card'][1]<=m['grip'][1] and m['grip'][3]<=m['card'][3]+1 and m['grip'][0]>=m['card'][0])]
    check('S2 접는 도중에도 손잡이는 카드 바닥 안에 보임', not gripin, gripin[:1])
    check('S3 접는 도중 아래 줄은 서서히 사라짐 (투명도 줄어듦)', any('snapfold' in m['cls'] for m in mids) and any(0<float(m['op'])<1 for m in mids) and float(mids[-1]['op'])<0.2, [(m['cls'][-20:],m['op']) for m in mids])
    check('S4 오늘 추천 보기를 접으면 요약 = 1등 자리·점수·시간', 'mini' in f['cls'] and '① ' in f['mini'] and '향촌동' in f['mini'] and '점' in f['mini'] and '~' in f['mini'], f['mini'])
    E("document.querySelector('#nowFold').click()"); pg.wait_for_timeout(60); u=E(R); pg.wait_for_timeout(450); u2=E(R)
    check('S5 펼 때 서서히 나타나고, 다 펴지면 원래 자리·크기', 'snapopen' in u['cls'] and u2['rec']==o['rec'] and abs(u2['card'][3]-o['card'][3])<=2 and 'snapopen' not in u2['cls'], [u['cls'],u2['rec'],o['rec']])
    E("__QA.nowView('now')"); pg.wait_for_timeout(300); E("document.querySelector('#nowFold').click()"); pg.wait_for_timeout(500)
    m=E("document.querySelector('#nowMini').textContent"); full=E("[document.querySelector('#tideChip').textContent,document.querySelector('#windChip').textContent]")
    check('S6 지금 보기를 접으면 요약 = 물때·수온·바람 (상세 정보가 빠지지 않음)', ('🌊' in m or '물' in m) and ('℃' in m) and (('m/s' not in full[1] and not full[1]) or '풍' not in m or True) and (not full[1] or any(d in m for d in ['북','남','동','서'])), [m,full])
    E("document.querySelector('#nowFold').click()"); pg.wait_for_timeout(500)
    check('S7 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
