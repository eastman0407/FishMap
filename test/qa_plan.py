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
    rows=E("document.querySelectorAll('#planList>li').length")
    check('P1 📅 누르면 출조 도우미가 열리고 오늘부터 21일 줄', R and R['n']==21 and rows==21 and R['d0']==R['today'], [R and R['n'],rows])
    check('P2 날마다 만조·간조 3~4개 (21일째까지)', R and all(3<=x<=4 for x in R['ex']), R and R['ex'])
    s_=set(R['str']) if R else set()
    check('P3 조차를 날마다 계산하고 사리 쪽/조금 쪽 세기 표시', R and all(r and r>0.5 for r in R['rg']) and any('사리' in x for x in s_) and any('조금' in x for x in s_), [R and [round(r,2) for r in R['rg'][:8]], sorted(s_)])
    W=E("__QA.PLAN.res.days[1].wins.map(w=>[(w.x.ms-w.s)/60000,(w.t-w.x.ms)/60000])")
    check('P4 승부 시간 = 만조·간조 앞뒤 1시간 30분', W and all(a==90 and b==90 for a,b in W), W)
    G=E("""(()=>{let n=0,bad=0;for(const d of __QA.PLAN.res.days)for(const w of d.wins){if(!w.gold)continue;n++;const r=d.sun.rise,s=d.sun.set;
      const ok=(w.s<r+60*60000&&w.t>r-30*60000)||(w.s<s+30*60000&&w.t>s-60*60000);if(!ok)bad++;}return [n,bad,document.querySelectorAll('#planList .gold').length]})()""")
    check('P5 ⭐ 해뜰녘·해질녘과 겹치는 승부 시간 표시 (겹침 계산 확인)', G[0]>0 and G[1]==0 and G[2]>0, G)
    S=E("(()=>{const d=__QA.PLAN.res.days[0].sun,h=m=>new Date(m).getHours()+new Date(m).getMinutes()/60;return [h(d.rise),h(d.set)]})()")
    check('P6 해 뜨는·지는 시각 (사천 근처 상식 범위)', 5<S[0]<8 and 17<S[1]<20.5, S)
    F=E("[...document.querySelectorAll('#planList .l2')].map(x=>x.textContent)")
    check('P7 유속은 예보 있는 날만 표시, 그 뒤는 "유속 예보 전"', any('유속 최대' in x for x in F[:3]) and all('유속 예보 전' in x for x in F[10:]), [F[0],F[12]])
    E("document.querySelector('#planList>li:nth-child(2)').click()"); pg.wait_for_timeout(200)
    dt=E("(()=>{const li=document.querySelector('#planList>li:nth-child(2)');return [li.classList.contains('open'),li.querySelector('.det').textContent,getComputedStyle(li.querySelector('.det')).display]})()")
    check('P8 하루를 누르면 상세(만조·간조, 승부 시간, 도착 권장, 쉬는 때, 해, 물때·조차)', dt[0] and dt[2]=='block' and all(k in dt[1] for k in ['만조','승부 시간','도착 권장','쉬는 때','뜸','조차']), dt[1][:160])
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
