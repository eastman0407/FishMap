# 새 API 3개 시험 (build-33, REQ-52~54): TideBED 예측 조위 · 조류예보(시계열) · 자연과학용 수심정보
# 가짜 응답은 활용가이드(hwp) 응답 모양 그대로: TideBED=slctdDt/slctdHgt/obsvtrNm/josi/jogo, 조류예보=predcDt/crdir(16방위)/crsp(cm/s), 수심=lat/lot/dpwt+totalCount
import sys, time
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
MOCK=r"""  const q=new URL(url).searchParams, p2=v=>String(v).padStart(2,'0'), kst=t=>{const d=new Date(t+9*3600e3);return `${d.getUTCFullYear()}-${p2(d.getUTCMonth()+1)}-${p2(d.getUTCDate())} ${p2(d.getUTCHours())}:${p2(d.getUTCMinutes())}`;};
  const ok=(items,tc)=>reply(200,JSON.stringify({response:{header:{resultCode:'00',resultMsg:'NORMAL_SERVICE'},body:{items:{item:items},totalCount:tc==null?items.length:tc,numOfRows:300,pageNo:+q.get('pageNo')||1}}}));
  const day0=()=>{const rd=q.get('reqDate');return Date.UTC(+rd.slice(0,4),+rd.slice(4,6)-1,+rd.slice(6,8))-9*3600e3;};
  if(url.includes('/tidebed/')){window.__tbCalls=(window.__tbCalls||0)+1;
    if(window.__tbFail)return reply(200,JSON.stringify({response:{header:{resultCode:'30',resultMsg:'SERVICE_KEY_IS_NOT_REGISTERED_ERROR'}}}));
    const d0=day0(),P=12.42*3600e3,items=[];
    for(let t=d0;t<d0+86400e3;t+=600000){const s=t-14*60000; items.push({obsvtrNm:'삼천포',lot:'128.0700',lat:'34.9250',obsrvnDt:kst(t),obsrvnHgt:'0',slctdDt:kst(s),
      slctdHgt:(150+130*Math.cos(2*Math.PI*(s-window.__HI0)/P)).toFixed(2),jogo:0.98,josi:'-14분',msl:150});}
    return ok(items);}
  if(url.includes('/tideFcstHghLw/')){window.__tideCalls=(window.__tideCalls||0)+1;return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));}
  if(url.includes('/crntFcstTime/')){window.__cfCalls=(window.__cfCalls||0)+1; const c=q.get('obsCode');
    let la,lo,nm; if(c==='22LTC02'){la=34.905;lo=128.095;nm='대방수도';} else {let h=0;for(const ch of c)h=(h*31+ch.charCodeAt(0))%1000; la=36+h/1000;lo=126+h/2000;nm='먼곳'+c;}
    const d0=day0(),items=[]; for(let t=d0;t<d0+86400e3;t+=3600e3)items.push({obsvtrNm:nm,lot:String(lo),lat:String(la),predcDt:kst(t),crdir:'동남동',crsp:'51.44'});
    const n=+q.get('numOfRows')||10; return ok(items.slice(0,n),items.length);}
  if(url.includes('/waterDepth/')){window.__dpCalls=(window.__dpCalls||0)+1;
    const y0=+q.get('ymin'),y1=+q.get('ymax'),x0=+q.get('xmin'),x1=+q.get('xmax'),all=[],mid=(y0+y1)/2;
    for(let y=Math.ceil(y0/0.00135)*0.00135;y<=y1;y+=0.00135)for(let x=Math.ceil(x0/0.0016)*0.0016;x<=x1;x+=0.0016)all.push({lat:y.toFixed(5),lot:x.toFixed(5),dpwt:(y>mid?2:20).toFixed(3)});
    const pg=+q.get('pageNo')||1; return ok(all.slice((pg-1)*300,pg*300),all.length);}
"""
src=src.replace("""  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""",
  MOCK+"""  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""")
src=src.replace('BRIDGE=r"""','BRIDGE=r"""window.__HI0=(()=>{const d=new Date();d.setHours(0,0,0,0);return d.getTime()+(11*60+41)*60000;})();')
assert '/tidebed/' in src
exec(src+'''
    def until(js,limit=60):
        t=time.time()
        while time.time()-t<limit:
            if E(js): return True
            pg.wait_for_timeout(300)
        return False
    go(13,34.92,128.07,0)
    until("!!__QA.TIDE.cur",60)
    st=E("__QA.TIDE.cur&&__QA.TIDE.cur.st")
    check('N1 조석을 TideBED(좌표 보정)로 받음 · 기준항 이름 표시', st and st.get('bed') and st.get('n')=='삼천포', st)
    check('N2 예전 관측소 166곳 확인을 안 함 (고·저조 API 호출 0번)', not E("window.__tideCalls"), E("[window.__tideCalls,window.__tbCalls]"))
    D0=E("__QA.tideDay()")
    got=E("__QA.tideExtremes(__QA.TIDE.cur.ser,__QA.tideDay(),__QA.tideDay()+86400e3).map(e=>[(e.ms-__QA.tideDay())/60000,e.hi,e.h])")
    P=12.42*60; hi=[11*60+41+k*P for k in range(-2,4)]; ext=sorted([(m,True) for m in hi]+[(m+P/2,False) for m in hi])
    err=max(min(abs(g[0]-x[0]) for x in ext if x[1]==g[1]) for g in got) if got else 99
    hs=[g[2] for g in got]
    check('N3 10분 곡선에서 만조·간조 시각 찾기 (조시차 반영된 곡선 그대로, 3분 이내, 높이 2.8m/0.2m)', len(got)>=3 and err<=3 and all(abs(h-2.8)<0.05 or abs(h-0.2)<0.05 for h in hs), f'{len(got)}개, 최대 오차 {err:.1f}분, 높이 {hs}')
    E(f"Date.now=()=>{D0}+(14*60+40)*60000; __QA.updateTideChips()")
    chip=E("document.querySelector('#tideChip').textContent"); ph=E("document.querySelector('#phaseChip').textContent")
    check('N4 조석 칩·물 상태 정상', '삼천포' in chip and ('만조' in chip or '간조' in chip) and ('물' in ph or '조금' in ph or '무시' in ph), [chip,ph])
    E("document.querySelector('#tideChip').click()"); pg.wait_for_timeout(300)
    sub=E("document.querySelector('#tideSub').textContent")
    check('N5 조석표에 보정 정보(기준항·시간차·높이비) 표시', '기준항 삼천포' in sub and '-14분' in sub and '0.98' in sub, sub)
    E("window.__onBack()")
    E("__QA.openPlan()"); until("!__QA.PLAN.busy&&!!__QA.PLAN.res",60)
    ps=E("document.querySelector('#planSub').textContent"); nd=E("__QA.PLAN.res?__QA.PLAN.res.days.filter(d=>d.ex.length>=3).length:0")
    check('N6 📅 3주 계획도 TideBED로 (21일 모두 만조·간조 3개 이상)', '기준항 삼천포' in ps and nd==21, [ps,nd])
    E("window.__onBack()")
    # 실패하면 30분간 예전 방식으로 자동 전환
    r=E("(async()=>{window.__tbFail=true; __QA.TB.bad=0; const o=await __QA.tideExAt(36.5,126.3,__QA.tideDay(),1); window.__tbFail=false; return [__QA.tbUse(),__QA.TB.why,o.st&&o.st.bed,window.__tideCalls||0];})()")
    check('N7 TideBED가 안 되면 예전 관측소 방식으로 전환 + 이유 기록', r[0]==False and '30' in str(r[1]) and not r[2] and r[3]>0, r)
    E("__QA.TB.bad=0")
    # 조류예보 지점
    go(13,34.92,128.07,0); until("__QA.CF.st&&__QA.CF.st.length>100&&__QA.CF.ser.size>0",90)
    n=E("__QA.CF.st?__QA.CF.st.length:0")
    check('N8 조류예보 지점 위치를 한 번 받아 저장 (204곳)', n==204 and E("AndroidBridge.getPref('cfSt1').length>1000"), n)
    pg.wait_for_timeout(1500); E("const o=L.divIcon;window.__ic=[];L.divIcon=x=>{window.__ic.push(x.html);return o(x)};__QA.cfDraw();L.divIcon=o")
    mk=E("window.__ic.filter(h=>h.includes('cfst'))")
    check('N9 화면 안 지점을 보라색 화살표로 표시 (동남동 0.51 m/s)', any('0.51 m/s' in m for m in mk), mk[:3])
    v=E("(()=>{const v=__QA.cfFill(34.905,128.095,__QA.tH());return v&&[v.vE,v.vN];})()")
    import math
    check('N10 ⚓ 보조값: 유향 동남동(112.5°)·1노트를 동·북 성분으로', v and abs(math.hypot(*v)-1)<0.02 and abs(math.degrees(math.atan2(v[0],v[1]))-112.5)<1, v)
    calls_after=E("window.__cfCalls"); go(13,34.921,128.071,3000)
    check('N11 다시 움직여도 지점 목록을 또 받지 않음', E("window.__cfCalls")-calls_after<=8, [calls_after,E("window.__cfCalls")])
    # 수심 반영 (정밀 단계) — 번들 격자(BADA2024)로 칸마다 바닥 마찰. 격자 경로가 쓰이고 마찰이 깊이에 따라 다른지 확인
    E("__QA.DGRID.data=undefined;__QA.DGRID.load=null")  # 격자 다시 로드되게
    go(16,34.898,128.096,500)
    ok=until("__QA.SIM.done&&[...__QA.SIM.tiles.values()].some(t=>t.kz)",120)
    info=E("(()=>{const T=[...__QA.SIM.tiles.values()].find(t=>t.kz);if(!T)return null;let pos=0,cnt=0,mx=0;for(let i=0;i<T.kz.length;i++){if(T.solid[i])continue;cnt++;const k=T.kz[i];if(k>0)pos++;if(k>mx)mx=k;}return [T.hmed,pos,cnt,+mx.toFixed(5),__QA.DEPTH.last];})()")
    # 격자 사용('격자')·마찰 최대값>0·마찰이 칸마다 다름(깊은 칸은 0, 얕은 칸은 양수 → pos<cnt)
    # (헤드리스 sim 워커가 안 도는 환경에선 타일 미완료로 실패 — 알려진 한계. CI/실기기에서 통과. 격자 로직 자체는 qa_depthgrid.js로 검증)
    check('N12 번들 격자로 수심 마찰 (격자 사용·깊이 따라 마찰 다름)', ok and info and info[4]=='격자' and info[3]>0 and 0<info[1]<info[2], info)
    cb=E("['tbChk','cfChk','depthChk'].map(i=>document.getElementById(i).checked)")
    check('N13 ⚙ 새 설정 3개 (기본 켬)', cb==[True,True,True], cb)
    check('N14 스크립트 오류 없음', not errs, errs[:3])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
