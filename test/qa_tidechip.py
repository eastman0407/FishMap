# 조석 칩 시험: 다가오는 만조/간조, 들물·날물 단계, 물때 이름, 오늘 조석 목록 (build-24)
# 조석예보 가짜 응답: 삼천포(DT_0001) 한 곳, 물높이 = 150 + 130·cos(2π(t−기준만조)/12.42시간) cm
import sys, time, math, datetime
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
src=src.replace("""  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""",
"""  if(url.includes('tideFcstTime')){const q=new URL(url).searchParams;
    if(q.get('obsCode')!=='DT_0001')return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));
    const rd=q.get('reqDate'),y=+rd.slice(0,4),m=+rd.slice(4,6)-1,d=+rd.slice(6,8),step=+q.get('min')||60,n=Math.min(+q.get('numOfRows')||10,1440/step),items=[];
    const base=Date.UTC(y,m,d)-9*3600e3, HI=window.__HI0;
    for(let k=0;k<n;k++){const t=base+k*step*60000,dt=new Date(t+9*3600e3),p=v=>String(v).padStart(2,'0');
      items.push({obsvtrNm:'삼천포',lat:34.925,lot:128.07,predcDt:`${dt.getUTCFullYear()}-${p(dt.getUTCMonth()+1)}-${p(dt.getUTCDate())} ${p(dt.getUTCHours())}:${p(dt.getUTCMinutes())}:00`,
        tdlvHgt:+(150+130*Math.cos(2*Math.PI*(t-HI)/(12.42*3600e3))).toFixed(1)});}
    return reply(200,JSON.stringify({response:{header:{resultCode:'00'},body:{items:{item:items}}}}));}
  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""")
# 기준 만조: 오늘 0시(KST)+11시41분
src=src.replace('BRIDGE=r"""','BRIDGE=r"""window.__HI0=(()=>{const d=new Date();d.setHours(0,0,0,0);return d.getTime()+(11*60+41)*60000;})();')
assert 'tideFcstTime' in src
exec(src+'''
    def setT(m):
        E(f"const s=document.querySelector('#slider');s.value={m};s.dispatchEvent(new Event('input'))"); pg.wait_for_timeout(300)
    go(13,34.92,128.07,0)
    for _ in range(60):
        if E("!!__QA.TIDE.cur"): break
        pg.wait_for_timeout(500)
    P=12.42*60
    hi=[11*60+41+k*P for k in range(-2,4)]; lo=[h+P/2 for h in hi]
    ext=sorted([(m,'만조') for m in hi]+[(m,'간조') for m in lo])
    def nxt(m): return next(e for e in ext if e[0]>m)
    hm=lambda m:f"{int(m//60)%24:02d}:{int(round(m%60))%60:02d}"
    setT(14*60+40); t=E("document.querySelector('#tideChip').textContent"); want=nxt(14*60+40)
    check('C1 다가오는 조석 표시 (삼천포·종류·시각)', '삼천포' in t and want[1] in t, f'{t} / 기대 {want[1]} {hm(want[0])}')
    got=E("__QA.tideExtremes(__QA.TIDE.cur.ser,__QA.tideDay(),__QA.tideDay()+86400e3).map(e=>[(e.ms-__QA.tideDay())/60000,e.hi])")
    err=max(min(abs(g[0]-x[0]) for x in ext if (x[1]=='만조')==g[1]) for g in got)
    check('C2 만조·간조 시각 정확도 (10분 간격 자료 → 3분 이내)', got and err<=3, f'{len(got)}개, 최대 오차 {err:.1f}분')
    low0=next(e[0] for e in ext if e[1]=='간조' and e[0]>0)
    setT(int(low0+60)//10*10); a=E("document.querySelector('#phaseChip').textContent")
    setT(int(low0+P/4)//10*10); b=E("document.querySelector('#phaseChip').textContent")
    setT(int(low0+P/2-10)//10*10); c=E("document.querySelector('#phaseChip').textContent")
    setT(int(low0+P/2+90)//10*10); d=E("document.querySelector('#phaseChip').textContent")
    check('C3 들물·날물 단계 (간조 1시간 뒤 초들물 → 중들물 → 만조 정조 → 초날물)', a.startswith('초들물') and b.startswith('중들물') and c.startswith('만조') and d.startswith('초날물'), [a,b,c,d])
    check('C4 물때를 우리말로 (예: 13물→열셋물)', E("__QA.mulWord('13물')")=='열셋물' and E("__QA.mulWord('조금')")=='조금' and '물' in a or '조금' in a or '무시' in a, a)
    setT(14*60+40); E("document.querySelector('#tideChip').click()"); pg.wait_for_timeout(300)
    items=E("[...document.querySelectorAll('#tideList li')].map(l=>[l.className,l.textContent])")
    nxtli=[x for x in items if 'next' in x[0]]
    check('C5 누르면 오늘 조석 목록(지난 것 흐리게, 다가오는 것 강조)', E("document.querySelector('#tidePanel').classList.contains('show')") and len(items)>=3 and len(nxtli)==1 and any('past' in x[0] for x in items), items)
    E("window.__onBack()"); check('C6 뒤로가기로 닫힘', not E("document.querySelector('#tidePanel').classList.contains('show')"))
    check('C7 칩이 배지 옆 한 줄 영역에 배치', E("document.querySelector('#tideChip').parentElement.className")=='topchips')
    check('C8 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
