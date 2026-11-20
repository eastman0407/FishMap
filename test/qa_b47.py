# build-47 시험 (REQ-77 F26): 설정 옮기기 링크 — 만들기·풀기, 링크로 열기(저장 물음·주소 지움), 만료, 붙여넣기, 취소, 즐겨찾기 합치기. 바탕은 qa_b45
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
    E("window.AndroidBridge._p.dataKey='TESTKEY+/=한글1234'; __QA.saveFavs([{name:'비토섬 갯바위',lat:34.9012,lng:127.9988},{name:'A',lat:34.9,lng:128.0}])")
    url=E("__QA.xferMake({key:true,vw:true,fav:true})"); d=E(f"__QA.xferParse({url!r})")
    check('X1 링크 = 웹판 주소 + #cfg-, 키가 글자 그대로 안 보임, 풀면 같은 값', url.startswith('https://eastman0407.github.io/fishmap-web/#cfg-') and 'TESTKEY' not in url and d['p']=={'dataKey':'TESTKEY+/=한글1234','vworldKey':'VWKEY'} and d['f'][0]['n']=='비토섬 갯바위', [url[:60],d.get('p')])
    check('X2 7일 뒤 만료 시각이 들어 있음', abs(d['exp']-E("Date.now()")-7*864e5)<60000, d['exp'])
    nk=E("__QA.xferParse(__QA.xferMake({key:false,vw:true,fav:false})).p")
    check('X3 고른 것만 들어감 (공공데이터 키 빼기)', nk=={'vworldKey':'VWKEY'}, nk)
    # 설정 창: 버튼·체크
    E("document.querySelector('#setPanel').classList.add('show'); document.querySelector('#xferOut').click()"); pg.wait_for_timeout(200)
    xb=E("[getComputedStyle(document.querySelector('#xferBox')).display, [...document.querySelectorAll('#xferBox label')].map(l=>Math.round(l.getBoundingClientRect().height))]")
    E("window.__shared=null; window.AndroidBridge.shareText=t=>{window.__shared=t}; document.querySelector('#xferMake').click()"); sh=E("window.__shared||''")
    check('X4 ⚙ 📤 설정 옮기기 → 체크 3개(44 높이) → 공유 창으로 링크 보냄', xb[0]=='block' and len(xb[1])==3 and min(xb[1])>=44 and '#cfg-' in sh and '7일' in sh, [xb,sh[:50]])
    # 붙여넣기 → 저장 물음 → 취소하면 아무것도 안 바뀜
    E("window.AndroidBridge._p.dataKey='OLD'; document.querySelector('#bakIn').click()"); E(f"document.querySelector('#bakText').value='받은 링크: '+{url!r}+' 끝'; document.querySelector('#bakApply').click()"); pg.wait_for_timeout(200)
    a1=E("[getComputedStyle(document.querySelector('#xferAsk')).display, document.querySelector('#xferMsg').textContent]")
    E("document.querySelector('#xferNo').click()"); a2=E("[getComputedStyle(document.querySelector('#xferAsk')).display, window.AndroidBridge._p.dataKey]")
    check('X5 백업 칸에 링크를 붙여넣으면 저장 물음(옮길 것 이름) → 취소하면 그대로', a1[0]=='flex' and '공공데이터 키' in a1[1] and '즐겨찾기 2곳' in a1[1] and a2==['none','OLD'], [a1,a2])
    E(f"document.querySelector('#bakApply').click()"); pg.wait_for_timeout(150)
    E("__QA.saveFavs([{name:'A',lat:34.9,lng:128.0}]); document.querySelector('#xferYes').click()"); pg.wait_for_timeout(200)
    a3=E("[window.AndroidBridge._p.dataKey, window.AndroidBridge._p.vworldKey, __QA.loadFavs().map(f=>f.name)]")
    check('X6 저장하면 키가 들어가고 즐겨찾기는 겹치지 않게 더해짐', a3==['TESTKEY+/=한글1234','VWKEY',['A','비토섬 갯바위']], a3)
    old=E("(()=>{const d={v:1,exp:Date.now()-1000,p:{dataKey:'X'}};return __QA.WEB_URL+'#cfg-'+__QA.b64u.enc(JSON.stringify(d));})()")
    try: E(f"__QA.xferParse({old!r})"); ex=''
    except Exception as e: ex=str(e)
    bad=''
    try: E("__QA.xferParse('https://x/#cfg-abc$$')")
    except Exception as e: bad=str(e)
    check('X7 만료된 링크·깨진 링크는 이유를 알려주고 안 받음', '만료' in ex and ('깨졌' in bad or '아니에요' in bad), [ex[-40:],bad[-40:]])
    # 링크로 바로 열기: 주소의 #cfg 부분이 지워지고 저장 물음이 뜸
    E("window.AndroidBridge._p.dataKey='OLD2'")
    pg.wait_for_timeout(1800)  # X6의 다시 불러오기 끝나기
    base=pg.url.split('#')[0]; pg.goto(base+'#cfg-'+url.split('#cfg-')[1]); pg.wait_for_timeout(2500)
    h0=E("[location.hash, getComputedStyle(document.querySelector('#xferAsk')).display]"); E("document.querySelector('#xferAsk').style.display='none'")
    pg.goto('about:blank'); pg.goto(base+'#cfg-'+url.split('#cfg-')[1]); pg.wait_for_timeout(6000)
    h=E("[location.hash, getComputedStyle(document.querySelector('#xferAsk')).display, document.querySelector('#xferMsg').textContent]")
    check('X8 이미 열린 웹판에서 링크를 눌러도 주소의 키 부분은 지워지고 저장 물음', h0==['','flex'], h0)
    check('X10 새로 열 때도 주소의 키 부분은 바로 지워지고 저장할지 물어봄', h[0]=='' and h[1]=='flex' and '저장할까요' in h[2], h)
    check('X9 스크립트 오류 없음', not [e for e in errs if 'reload' not in e], errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
