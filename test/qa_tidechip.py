# 조석 칩 시험: 다가오는 만조/간조, 들물·날물 단계, 물때 이름, 오늘 조석 목록 (build-24)
# 조석예보(고,저조) 가짜 응답: 삼천포(DT_0061) 한 곳, 만조 280cm·간조 20cm, 주기 12.42시간 (활용가이드 261106 응답 모양)
import sys, time, math, datetime
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
src=src.replace("""  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""",
"""  if(url.includes('tideFcstHghLw')){const q=new URL(url).searchParams; window.__tideCalls=(window.__tideCalls||0)+1;
    if(q.get('obsCode')!=='DT_0061')return reply(200,JSON.stringify({response:{header:{resultCode:'03',resultMsg:'NODATA_ERROR'}}}));
    const rd=q.get('reqDate'),y=+rd.slice(0,4),m=+rd.slice(4,6)-1,d=+rd.slice(6,8),day0=Date.UTC(y,m,d)-9*3600e3,P=12.42*3600e3,items=[],p2=v=>String(v).padStart(2,'0');
    for(let k=-6;k<=6;k++)for(const hi of [true,false]){const t=window.__HI0+k*P+(hi?0:P/2); if(t<day0||t>=day0+86400e3)continue;
      const dt=new Date(t+9*3600e3),pm=dt.getUTCHours()>=12;
      items.push({obsvtrNm:'삼천포',lot:'128.0700',lat:'34.9250',predcDt:`${dt.getUTCFullYear()}-${p2(dt.getUTCMonth()+1)}-${p2(dt.getUTCDate())} ${p2(dt.getUTCHours())}:${p2(dt.getUTCMinutes())}`,
        predcTdlvVl:(hi?280:20).toFixed(1),extrSe:String(hi?(pm?3:1):(pm?4:2))});}
    items.sort((a,b)=>a.predcDt<b.predcDt?-1:1); const n=+q.get('numOfRows')||10;
    return reply(200,JSON.stringify({response:{header:{resultCode:'00',resultMsg:'NORMAL_SERVICE'},body:{items:{item:items.slice(0,n)},totalCount:items.length}}}));}
  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""")
# 기준 만조: 오늘 0시(KST)+11시41분
src=src.replace('BRIDGE=r"""','BRIDGE=r"""window.__HI0=(()=>{const d=new Date();d.setHours(0,0,0,0);return d.getTime()+(11*60+41)*60000;})();')
assert 'tideFcstHghLw' in src
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
    check('C2 만조·간조 시각이 고·저조 API 값 그대로 (1분 이내)', got and err<=1, f'{len(got)}개, 최대 오차 {err:.1f}분')
    check('C2b 관측소 166곳 목록에서 삼천포(DT_0061) 찾음 + 이후엔 저장된 목록 사용', E("__QA.TIDE.cur.st.c")=='DT_0061' and E("AndroidBridge.getPref('tideSt2').includes('DT_0061')"), E("[__QA.TIDE.cur.st,window.__tideCalls]"))
    h=E("__QA.tideNow()"); check('C2c 물높이 곡선(바위 잠김용)도 만들어짐', h is not None and 0.1<h<2.9, h)
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
