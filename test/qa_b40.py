# build-40 시험 (REQ-65~69): 지점 시트 끌어서 접기·근처 조류예보 지점·흐린 숫자(FE0F 전체 검사)·물길 전체 지점 값·지금 카드 폭 고정. 바탕은 qa_more
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
    import re
    BG="document.querySelector('.samplebadge').textContent"
    b=E(BG)
    check('N1 배지는 상태만 (단계·칸 크기 없음), 단계는 진단에', '칸' not in b and '구역' not in b and '단계' in E("__QA.runDiag()"), b)
    R="(()=>{const r=document.querySelector('#nowCard').getBoundingClientRect();return [Math.round(r.left),Math.round(r.right),Math.round(r.bottom)];})()"
    w0=E(R); go(10,34.92,128.07,1500); w1=E(R); go(14,34.92,128.07,1500); w2=E(R)
    check('N2 카드 폭 고정: 확대 12·10·14 모두 화면 양쪽 끝(10px)까지 같은 폭', len({(a[0],a[1]) for a in [w0,w1,w2]})==1 and w0[0]==10 and w0[1]==401, [w0,w1,w2])
    sd=E("(()=>{const r=document.querySelector('.side').getBoundingClientRect();return [Math.round(r.top),Math.round(r.left),Math.round(r.bottom)];})()")
    check('N3 (U-48 접기 없앰) M2(◎·☰)가 카드 바로 아래', w2[2]<=sd[0]<=w2[2]+12, [w2,sd])
    w4=E(R)
    sd2=E("(()=>{const r=document.querySelector('.side').getBoundingClientRect();return [Math.round(r.top),Math.round(r.bottom),Math.round(r.left)];})()")
    fab=E("(()=>{const r=document.querySelector('#biteFab').getBoundingClientRect();return Math.round(r.top);})()")
    check('N4 펴면 M2가 카드 아래(겹침 없음), 가로 두 개라 입질 버튼과도 안 겹침', w4[2]<=sd2[0]<=w4[2]+12 and sd2[1]<fab, [w4,sd2,fab])
    E("document.querySelector('#tideChip').textContent='🌊 '+'아주긴관측소이름'.repeat(8)+' · 만조 05:26'"); pg.wait_for_timeout(200)
    lc=E("(()=>{const e=document.querySelector('#tideChip');return [e.scrollWidth>e.clientWidth,Math.round(e.getBoundingClientRect().height)];})()"); w5=E(R)
    check('N5 아주 긴 글: 카드 폭 그대로, 한 줄로 … 자르기', lc[0] and lc[1]<=32 and w5[:2]==w4[:2], [lc,w5])
    E("__QA.updateTideChips()")
    TE='⚙⚠⛴🌬🗑🗺🛰🌡🌧☀☁'
    def bad(t): return [m.group(0)+'?' for m in re.finditer('['+TE+'](?!️)',t)]
    src=open('/tmp/qa/index.html',encoding='utf-8').read().replace('\\\\uFE0F','️')
    found=bad(src)
    texts=[]
    E("__QA.select(34.92,128.07,'시험 자리')"); pg.wait_for_timeout(600); texts.append(E("document.body.innerText"))
    for js in ["document.querySelector('#layersBtn').click()","document.querySelector('#setBtn').click()","document.querySelector('#tideChip').click()","document.querySelector('#planBtn').click()","document.querySelector('#favBtn').click()"]:
        E(js); pg.wait_for_timeout(700); texts.append(E("document.body.innerText")); E("while(window.__onBack&&window.__onBack()){}")
    for t in ['plan','log','rec']:
        E("document.querySelector('#planBtn').click()"); E(f"document.querySelector('.ptabs [data-tab={t}]').click()"); pg.wait_for_timeout(1200); texts.append(E("document.body.innerText")); E("while(window.__onBack&&window.__onBack()){}")
    fr=[x for t in texts for x in bad(t)]
    check('N6 FE0F 빠진 그림 글자 없음 (코드 전체 + 메인·시트·P1~P5·탭 화면 글 전체)', not found and not fr, [found[:5],fr[:5]])
    E("__QA.select(34.92,128.07,'시험 자리')"); pg.wait_for_timeout(600)
    iw=E("document.querySelector('#iMore').innerHTML")
    check('N7 지점 시트 바람·달 줄: 그림·숫자를 따로 (흐림 방지)', 'class="num"' in iw and 'class="emo"' in iw, iw[:160])
    E("""(()=>{const now=Date.now(); __QA.CF.on=true; __QA.CF.st=[{c:'TT01',n:'시험지점',la:34.9216,lo:128.07}]; __QA.CF.ser.set('TT01',{t:[now-7200e3,now+7200e3],vE:[-1,-1],vN:[1,1]});})()""")
    t1=E("__QA.cfNearText(34.92,128.07,__QA.tH())"); t2=E("__QA.cfNearText(34.928,128.07,__QA.tH())")
    check('N8 근처(500m 안) 조류예보 지점 값·방향·거리, 멀면 안 보임', '시험지점 0.73 m/s' in t1 and '북서쪽' in t1 and '180m' in t1 and t2=='', [t1,t2])
    E("__QA.updateUI()"); im=E("document.querySelector('#iMore').textContent")
    check('N9 지점 시트에 근처 지점 칸 표시 (build-49: 자리 정보 2×2의 "📍 조류 지점")', '조류 지점' in im and '시험지점' in im, im[:120])
    ac=E("""(()=>{const gx=40,gy=40,ch=new Uint8Array(gx*gy).fill(1); for(let y=0;y<gy;y++)for(let x=15;x<=20;x++)ch[y*gx+x]=0;
      const T={gx,gy,solid:ch}, open={gx,gy,solid:new Uint8Array(gx*gy)};
      const a=__QA.anchorCells(T,{cx:17,cy:20,vE:0,vN:1.5},94), b=__QA.anchorCells(open,{cx:17,cy:20,vE:0,vN:1.5},94), c=__QA.anchorCells(T,{cx:17,cy:20,vE:0,vN:0},94);
      return [a.length, a.filter(z=>z[1]<1).length, b.length, c.length, Math.min(...a.map(z=>z[0]%gx)), Math.max(...a.map(z=>z[0]%gx))];})()""")
    check('N10 좁은 물길(폭 6칸): 폭 전체 × 앞뒤 2칸 = 30칸(가장자리 0.8), 넓은 바다·멈춤은 3×3', ac[0]==30 and ac[1]==10 and ac[2]==9 and ac[3]==9 and ac[4]==15 and ac[5]==20, ac)
    # N11~N14(예전 M8 끌기)는 build-41 REQ-70에서 방식이 바뀌어 qa_b41로 옮김
    check('N15 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
