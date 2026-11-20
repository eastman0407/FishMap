# build-42 시험 (REQ-71): 지금 카드 재배치(4줄·배지 머리 줄) + 보기 토글(지금 ↔ ⭐ 오늘 추천). 바탕은 qa_more
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
    E("__QA.updateTideChips(); __QA.updateUI&&0"); pg.wait_for_timeout(300)
    c=rect('#nowCard'); t=rect('#tideChip'); ph=rect('#phaseChip')
    check('K1 지금 보기: 카드 높이 낮아짐(4줄, 120px 이하) · 조석과 물때가 한 줄', c[3]<=120 and abs(t[1]-ph[1])<=3 and ph[0]>t[0], [c,t,ph])
    fit=E("['#tideChip','#phaseChip','#wxChip','#windChip'].map(q=>{const e=document.querySelector(q);return [q,e.scrollWidth<=e.clientWidth+1,e.textContent.slice(0,40)];})")
    check('K2 모든 줄이 카드 폭 안에 들어감 (잘림 없음)', all(x[1] for x in fit), fit)
    b=rect('.samplebadge'); h=rect('#nowHead'); bt=E("document.querySelector('.samplebadge').textContent")
    check('K3 상태 배지가 머리 줄 안 오른쪽(점 + 짧은 글)', h[1]<=b[1] and b[4]<=h[4] and b[0]>h[0]+150 and len(bt)<=12, [h,b,bt])
    E("document.querySelector('#nowHead').click()"); pg.wait_for_timeout(300)
    check('K4 머리 줄 빈 곳을 눌러도 출조 도우미가 안 열림 (토글로 바뀜)', not E("document.querySelector('#planPanel').classList.contains('show')"))
    pg.mouse.click(*mid('#nowSeg button[data-v=rec]')); pg.wait_for_timeout(300)
    v=E("[document.querySelector('#nowCard').classList.contains('recv'), getComputedStyle(document.querySelector('#tideChip').parentNode).display, getComputedStyle(document.querySelector('#nowRec')).display, window.AndroidBridge._p.nowView]")
    check('K5 ⭐ 오늘 추천 누르면 추천 보기로 바뀌고 기억', v[0] and v[1]=='none' and v[2]!='none' and v[3]=='rec', v)
    for _ in range(200):
        if E("document.querySelectorAll('#nowRec .rr').length>0"): break
        pg.wait_for_timeout(300)
    rr=E("[...document.querySelectorAll('#nowRec .rr')].map(r=>r.textContent)")
    import re
    check('K6 오늘 추천 3곳: 이름·점수·승부 시간', len(rr)==3 and all('점' in x and re.search(r'\\d\\d:\\d\\d~\\d\\d:\\d\\d',x) for x in rr), rr)
    c2=rect('#nowCard'); fit2=E("[...document.querySelectorAll('#nowRec .rr .nm')].every(e=>e.getBoundingClientRect().right<=document.querySelector('#nowCard').getBoundingClientRect().right)")
    check('K7 추천 보기도 카드 폭 안 · 높이 비슷(150px 이하)', fit2 and c2[3]<=150 and c2[2]==c[2], [c,c2])
    pg.mouse.click(*mid('#nowRec .rr')); pg.wait_for_timeout(600)
    sh=E("[document.querySelector('#info').classList.contains('show'), document.querySelector('#iname').textContent]")
    check('K8 추천 줄 누르면 그 자리 지점 시트(M8)', sh[0] and sh[1].startswith('추천 1'), sh)
    E("document.querySelector('#closeInfo').click()")
    pg.mouse.click(*mid('#nowRec .more b')); pg.wait_for_timeout(500)
    pp=E("[document.querySelector('#planPanel').classList.contains('show'), document.querySelector('.ptabs [data-tab=today]').classList.contains('on')]")
    check('K9 자세히 › = 출조 도우미 ⭐ 오늘 탭', pp==[True,True], pp)
    E("while(window.__onBack&&window.__onBack()){}")
    pg.mouse.click(*mid('#nowFold')); pg.wait_for_timeout(450); m1=E("document.querySelector('#nowCard').classList.contains('mini')")
    pg.mouse.click(*mid('#nowFold')); pg.wait_for_timeout(450); m2=E("[document.querySelector('#nowCard').classList.contains('mini'),document.querySelector('#nowCard').classList.contains('recv')]")
    check('K10 추천 보기에서도 접기·펴기, 펴면 추천 보기 그대로', m1 and m2==[False,True], [m1,m2])
    E("__QA.nowView()"); r2=E("document.querySelector('#nowCard').classList.contains('recv')")
    pg.mouse.click(*mid('#nowSeg button[data-v=now]')); pg.wait_for_timeout(300)
    n2=E("[document.querySelector('#nowCard').classList.contains('recv'), window.AndroidBridge._p.nowView]")
    check('K11 다시 그려도 보기 유지, 지금 누르면 돌아옴', r2 and n2==[False,'now'], [r2,n2])
    check('K12 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
