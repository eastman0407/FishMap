# 출조 계획 시험 (REQ-43). 조석 칩 시험의 가짜 응답을 3주로 늘리고 조차가 사리·조금으로 바뀌게 함
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
  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""")
# 기준 만조: 오늘 0시(KST)+11시41분
src=src.replace('BRIDGE=r"""','BRIDGE=r"""window.__HI0=(()=>{const d=new Date();d.setHours(0,0,0,0);return d.getTime()+(11*60+41)*60000;})();')
assert 'tideFcstHghLw' in src
exec(src+'''
    go(13,34.92,128.07,0)
    for _ in range(60):
        if E("!!__QA.TIDE.cur"): break
        pg.wait_for_timeout(500)
    pg.wait_for_timeout(6000)  # 조류 예보 받기
    E("document.querySelector('#planBtn').click()")
    for _ in range(80):
        if E("!!__QA.PLAN.res"): break
        pg.wait_for_timeout(300)
    R=E("(()=>{const R=__QA.PLAN.res;return R&&{n:R.days.length,st:R.st.n,d0:R.days[0].d,today:__QA.tideDay(),ex:R.days.map(d=>d.ex.length),rg:R.days.map(d=>d.rg),str:R.days.map(d=>d.str)}})()")
    E("document.querySelector('.ptabs [data-tab=plan]').click()"); pg.wait_for_timeout(200)
    cal=E("[document.querySelectorAll('#planCal .pc').length, document.querySelectorAll('#planCal .pc:disabled').length, new Date(__QA.tideDay()).getDay(), document.querySelectorAll('#planCal .pc.today').length, document.querySelector('.ptabs [data-tab=plan]').textContent]")
    check('P1 (U-50) 📅 날짜별: 이번 주 일요일부터 3주 달력 21칸, 오늘 전 날은 못 누름, 오늘 표시', R and R['n']==21 and R['d0']==R['today']-cal[2]*86400000 and cal[0]==21 and cal[1]==cal[2] and cal[3]==1 and cal[4]=='📅 날짜별', [R and R['n'],cal])
    check('P2 날마다 만조·간조 3~4개 (21일째까지)', R and all(3<=x<=4 for x in R['ex']), R and R['ex'])
    s_=set(R['str']) if R else set()
    check('P3 조차를 날마다 계산하고 사리 쪽/조금 쪽 세기 표시', R and all(r and r>0.5 for r in R['rg']) and any('사리' in x for x in s_) and any('조금' in x for x in s_), [R and [round(r,2) for r in R['rg'][:8]], sorted(s_)])
    W=E("__QA.PLAN.res.days[1].wins.map(w=>[(w.x.ms-w.s)/60000,(w.t-w.x.ms)/60000])")
    check('P4 승부 시간 = 만조·간조 앞뒤 1시간 30분', W and all(a==90 and b==90 for a,b in W), W)
    G=E("""(()=>{let n=0,bad=0;for(const d of __QA.PLAN.res.days)for(const w of d.wins){if(!w.gold)continue;n++;const r=d.sun.rise,s=d.sun.set;
      const ok=(w.s<r+60*60000&&w.t>r-30*60000)||(w.s<s+30*60000&&w.t>s-60*60000);if(!ok)bad++;}return [n,bad,document.querySelectorAll('#planCal em').length,__QA.PLAN.res.days.filter(d=>d.d>=__QA.tideDay()).length]})()""")
    check('P5 ⭐ 해뜰녘·해질녘 겹침 계산 확인 + 달력 ⭐는 물 도는 때가 해뜰·해질 ±30분인 날만(전부는 아님)', G[0]>0 and G[1]==0 and 0<G[2]<G[3], G)
    S=E("(()=>{const d=__QA.PLAN.res.days[0].sun,h=m=>new Date(m).getHours()+new Date(m).getMinutes()/60;return [h(d.rise),h(d.set)]})()")
    check('P6 해 뜨는·지는 시각 (사천 근처 상식 범위)', 5<S[0]<8 and 17<S[1]<20.5, S)
    i0=cal[2]
    E(f"document.querySelectorAll('#planCal .pc')[{i0+1}].click()"); pg.wait_for_timeout(200); F1=E("document.querySelector('#planDay').textContent")
    E(f"document.querySelectorAll('#planCal .pc')[{i0+10}].click()"); pg.wait_for_timeout(200); F2=E("[document.querySelector('#planDay').textContent, document.querySelector('#pdRec').disabled]")
    check('P7 고른 날 카드: 예보 있는 날은 유속 최대, 열흘 뒤는 "유속 예보 전"·추천 버튼 막힘(7일 안만)', '유속 최대' in F1 and '유속 예보 전' in F2[0] and F2[1] is True, [F1[:80],F2])
    E(f"document.querySelectorAll('#planCal .pc')[{i0+1}].click()"); pg.wait_for_timeout(200)
    dt=E("[document.querySelector('#planCal .pc.on').dataset.pi, document.querySelector('#planDay').textContent, document.querySelector('#pdMap').textContent, document.querySelector('#pdRec').textContent]")
    check('P8 날짜를 누르면 그 날 카드(물때·조차·승부 시간·도착 권장·해) + [🗺️ 이 날 지도로][⭐ 이 날 추천]', dt[0]==str(i0+1) and all(k in dt[1] for k in ['승부','도착 권장','☀️','조차','음력']) and dt[2]=='🗺️ 이 날 지도로' and dt[3]=='⭐ 이 날 추천', dt[1][:160])
    pg.screenshot(path='/tmp/shot_cal.png')
    # U-50 이 날 지도로 / 오늘로 / 이 날 추천
    E(f"document.querySelectorAll('#planCal .pc')[{i0+10}].click()"); pg.wait_for_timeout(150); E("document.querySelector('#pdMap').click()"); pg.wait_for_timeout(400)
    v=E("[__QA.VDAY.k, document.querySelector('#planPanel').classList.contains('show'), +document.querySelector('#slider').min, +document.querySelector('#slider').max, __QA.tMin(), document.querySelector('#vdayTag').textContent, document.querySelector('#nowBtn').textContent, document.querySelector('#nowSegNow').textContent, __QA.NOWF.on, document.querySelector('#slNow').style.display, document.querySelector('#timeLabel').textContent]")
    check('P12 [🗺️ 이 날 지도로] → 창 닫히고 시간 막대가 그날 0~24시, "📅 날짜 보는 중", 지금→그날·↩ 오늘로, 지금 따라가기 꺼짐', v[0]==10 and not v[1] and v[2]==14400 and v[3]==15840 and 14400<=v[4]<=15840 and '보는 중' in v[5] and v[6]=='↩ 오늘로' and v[7]=='그날' and v[8] is False and v[9]=='none', v)
    pg.screenshot(path='/tmp/shot_vday.png')
    E("const s=document.querySelector('#slider'); s.value=99999; s.dispatchEvent(new Event('input'))"); hi=E("__QA.tMin()")
    E("document.querySelector('#play').click()"); pg.wait_for_timeout(300); pl=E("__QA.tMin()"); E("document.querySelector('#play').click()")
    check('P13 그날 막대는 그날 24시를 넘지 않고, 끝에서 ▶ 누르면 그날 0시부터 재생', hi==15840 and 14400<=pl<14460, [hi,pl])
    E("document.querySelector('#nowBtn').click()"); pg.wait_for_timeout(300)
    o=E("[__QA.VDAY.k, __QA.tMin()===__QA.nowMin(), document.querySelector('#vdayTag').hidden, document.querySelector('#nowBtn').textContent, +document.querySelector('#slider').max, __QA.NOWF.on]")
    check('P14 [↩ 오늘로] → 오늘·지금으로 돌아오고 지금 따라가기 다시 켜짐', o==[0,True,True,'지금',2880,True], o)
    E("document.querySelector('#planBtn').click(); document.querySelector('.ptabs [data-tab=plan]').click()"); pg.wait_for_timeout(300)
    E(f"document.querySelectorAll('#planCal .pc')[{i0+2}].click()"); pg.wait_for_timeout(150); E("document.querySelector('#pdRec').click()"); pg.wait_for_timeout(300)
    r=E("[document.querySelector('.ptabs [data-tab=rec]').classList.contains('on'), document.querySelector('#recDay').value]")
    check('P15 [⭐ 이 날 추천] → 추천 탭이 그 날짜로', r==[True,'2'], r)
    E("while(window.__onBack&&window.__onBack()){}")
    # 기준 바꾸기: 즐겨찾기 추가 후 다시 열기
    pg.screenshot(path='/tmp/shot_plan.png')
    E("localStorage.setItem('fishmap.favs.v1',JSON.stringify([{lat:34.85,lng:128.2,name:'테스트포인트'}]))")
    E("__QA.openPlan()"); pg.wait_for_timeout(300)
    opts=E("[...document.querySelectorAll('#planBase option')].map(o=>o.textContent)")
    check('P9 기준 지점 고르기 (화면 가운데·선택 지점·즐겨찾기)', any('화면 가운데' in o for o in opts), opts)
    E("window.__onBack()"); check('P10 뒤로가기로 닫힘', not E("document.querySelector('#planPanel').classList.contains('show')"))
    check('P11 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
