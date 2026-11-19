# 육지·섬 나누기 시험 (build-35, REQ-56). 가짜 Overpass: 사천 육지에서 가장 가까운 섬 하나에만 다리. 바탕은 시·군·구 추천 시험(REQ-46). 가짜 응답은 출조 계획 시험과 같음. 조석 칩 시험의 가짜 응답을 3주로 늘리고 조차가 사리·조금으로 바뀌게 함
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
  if(url.includes('/api/interpreter')){window.__ovpCalls=(window.__ovpCalls||0)+1; if(window.__ovpFail)return reply(-1,'x');
    return reply(200,JSON.stringify({elements:window.__ovp||[]}));}
  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""")
# 기준 만조: 오늘 0시(KST)+11시41분
src=src.replace('BRIDGE=r"""','BRIDGE=r"""window.__HI0=(()=>{const d=new Date();d.setHours(0,0,0,0);return d.getTime()+(11*60+41)*60000;})();')
assert 'tideFcstHghLw' in src
exec(src+'''
    go(11,34.95,128.06,0)
    for _ in range(60):
        if E("!!__QA.TIDE.cur"): break
        pg.wait_for_timeout(500)
    # 사천시: 다리 놓을 섬 = 육지 점과 가장 가까운 섬 고리
    setup=E("""(async()=>{const d=await __QA.recLoad?null:null;})()""")
    info=E("""(async()=>{const r=await fetch('sgg.json').then(r=>r.json());const s=r.find(x=>x.n==='사천시');
      let best=null;const P=s.p;for(let i=0;i<P.length/2;i++){if(s.ri[i]>=0)continue;for(let j=0;j<P.length/2;j++){const g=s.ri[j];if(g<0)continue;
        const d=Math.hypot(P[2*i]-P[2*j],(P[2*i+1]-P[2*j+1])*0.82)*111000;if(d>150&&(!best||d<best.d))best={d,i,j,g};}}
      const a={lat:P[2*best.i],lon:P[2*best.i+1]},b={lat:P[2*best.j],lon:P[2*best.j+1]},m={lat:(a.lat+b.lat)/2,lon:(a.lon+b.lon)/2};
      window.__ovp=[{type:'way',tags:{highway:'primary',bridge:'yes'},geometry:[a,m]},{type:'way',tags:{highway:'primary',bridge:'yes'},geometry:[m,b]},
        {type:'way',tags:{highway:'footway',bridge:'yes'},geometry:[a,{lat:a.lat+0.0001,lon:a.lon}]}];
      const kinds={l:0,i:0};for(const g of s.ri)g<0?kinds.l++:kinds.i++;
      return {ring:best.g,d:Math.round(best.d),rings:Object.keys(s.is).length,kinds};})()""")
    print('사천', info)
    check('I1 해안 점마다 육지/섬 고리 번호 (사천: 섬 고리 여럿)', info['rings']>=5 and info['kinds']['l']>50 and info['kinds']['i']>50, info)
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(200)
    for _ in range(200):
        pg.wait_for_timeout(300)
        if E("!__QA.REC.busy"): break
    E("document.querySelector('.ptabs [data-tab=rec]').click()"); pg.wait_for_timeout(1500)
    cbs=E("[...document.querySelectorAll('#tabRec .kindbox input')].map(x=>[x.dataset.k,x.checked])")
    check('I2 체크 3개 (기본: 육지·다리 섬 켬, 배 섬 끔)', cbs==[['l',True],['b',True],['f',False]], cbs)
    def run():
        E("__QA.REC.res=null; document.querySelector('#recGo').click()")
        for _ in range(300):
            if E("!__QA.REC.busy&&!!__QA.REC.res"): break
            pg.wait_for_timeout(300)
        return E("__QA.REC.res")
    R=run()
    kinds=[c.get('isl') for c in R['pick'] if not c.get('fav')]
    rings=set(c['ring'] for c in R['pick'] if c.get('isl')=='b')
    check('I3 다리 놓인 섬은 🌉, 배 섬은 빠짐 (지도 자료로 판별)', R.get('kindSrc')=='osm' and 'f' not in kinds and all(r==info['ring'] for r in rings), [kinds, rings, R.get('kindSrc')])
    sub=E("document.querySelector('#recSub').textContent"); li=E("[...document.querySelectorAll('#recList li .l1 span:first-child')].map(x=>x.textContent)")
    check('I4 목록에 종류 아이콘·점수 높은 순 종합', ('🚗' in ''.join(li) or '🌉' in ''.join(li)) and '종합' in sub and [round(c['score'],6) for c in R['pick']]==sorted([round(c['score'],6) for c in R['pick']],reverse=True), [li[:5], sub[:80]])
    # 배 섬만
    E("const b=[...document.querySelectorAll('#tabRec .kindbox input')];b[2].checked=true;b[2].onchange();b[0].checked=false;b[0].onchange();b[1].checked=false;b[1].onchange();")
    pg.wait_for_timeout(500); R2=run(); k2=set(c.get('isl') for c in R2['pick'] if not c.get('fav'))
    check('I5 ⛴만 고르면 배 타는 섬만', k2=={'f'}, k2)
    E("const b=[...document.querySelectorAll('#tabRec .kindbox input')];b[2].checked=false;b[2].onchange();")
    check('I6 하나도 안 고르면 막음', E("[...document.querySelectorAll('#tabRec .kindbox input')].some(x=>x.checked)") and E("AndroidBridge.getPref('recKinds')")=='f', E("AndroidBridge.getPref('recKinds')"))
    # 모두 고르면 종합
    E("const b=[...document.querySelectorAll('#tabRec .kindbox input')];for(const x of b){x.checked=true;x.onchange();}")
    pg.wait_for_timeout(300); R3=run(); k3=[c.get('isl') for c in R3['pick'] if not c.get('fav')]
    check('I7 셋 다 고르면 한 목록에서 점수로 종합', len(k3)>=3 and R3['kinds']=='lbf' and E("document.querySelectorAll('#tabToday .kindbox input:checked').length")==3, [k3, R3['kinds']])
    # 길게 눌러 바꾸기
    i=next((n for n,c in enumerate(R3['pick']) if c.get('isl')=='f'),None)
    if i is not None:
        ring=R3['pick'][i]['ring']
        E("(i=>[...document.querySelectorAll('#recList li')][i].dispatchEvent(new MouseEvent('contextmenu',{bubbles:true,cancelable:true})))("+str(i)+")")
        pg.wait_for_timeout(500)
        for _ in range(300):
            if E("!__QA.REC.busy&&!!__QA.REC.res"): break
            pg.wait_for_timeout(300)
        ov=E("JSON.parse(AndroidBridge.getPref('islOv')||'{}')")
        R4=E("__QA.REC.res"); k4=[c.get('isl') for c in R4['pick'] if c.get('ring')==ring]
        check('I8 섬을 길게 누르면 배↔다리 직접 바꿈 (저장)', ov.get(str(ring))=='b' and all(k=='b' for k in k4), [ov, k4])
    else: check('I8 섬을 길게 누르면 배↔다리 직접 바꿈 (저장)', False, '배 섬 없음')
    # 지도 자료를 못 받으면 추정
    E("window.__ovpFail=true; AndroidBridge._p.islOv='{}'"); E("AndroidBridge.dropCache=()=>{}")
    R5=E("(async()=>{const d=await fetch('sgg.json').then(r=>r.json());const s=d.find(x=>x.n==='남해군');const f=await __QA.REC_kind(s);let c={l:0,b:0,f:0};for(let i=0;i<s.p.length/2;i++)c[f(i)]++;return [c,__QA.REC.kindSrc];})()") if E("!!__QA.REC_kind") else None
    if R5: check('I9 지도 자료 실패 시 추정 (남해 큰 섬 → 다리)', R5[0]['b']>R5[0]['f'] and R5[1]=='guess', R5)
    bk=E("fetch('index.html').then(r=>r.text()).then(t=>(t.match(/BAK_PREFS=\\[[^\\]]*\\]/)||[''])[0])")
    check('I10 백업에 체크·직접 바꾼 분류 포함', 'recKinds' in bk and 'islOv' in bk, bk[-60:])
    check('I11 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
