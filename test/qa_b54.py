# build-54 시험 (2묶음): U-43 상태창 같은 틀, U-44 시·구 띄어쓰기, U-49 수온 섞기
# 바탕은 qa_b49 (가짜 조석·바람·주소·관측소 응답 + 시험용 지도)
import sys
_c=open('test/qa_b49.py').read()
head=_c.split("    # ── U-10 상태창 ──")[0]
body=r'''
    PP="document.querySelector('#pinPop').classList.contains('show')"
    FC="document.querySelector('#fCard').classList.contains('show')"
    go(13,34.92,128.07,0); pg.wait_for_timeout(1500)
    E("document.querySelector('#nowSeg button[data-v=now]').click()"); pg.wait_for_timeout(300)
    # ── U-44 ──
    r=E("['창원시성산구','안산시상록구','포항시남구','사천시','수원시','중구','서귀포시','부산 해운대구'].map(__QA.sggFixName)")
    check('N1 시·구 이름 붙은 것만 띄움 (사천시·중구 등은 그대로)', r==['창원시 성산구','안산시 상록구','포항시 남구','사천시','수원시','중구','서귀포시','부산 해운대구'], r)
    E("__QA.recLoad()"); pg.wait_for_timeout(800)
    bad=E("__QA.REC.data.filter(r=>/시.+구$/.test(r.n)&&!/시 .+구$/.test(r.n)).map(r=>r.n)")
    check('N2 지역 목록에 붙은 이름이 하나도 없음', bad==[], bad)
    E("__QA.recInit()"); pg.wait_for_timeout(800)
    E("(()=>{const s=document.querySelector('#recSido'); s.value='경남'; s.dispatchEvent(new Event('change'));})()")
    txt=E("[...document.querySelectorAll('#recSgg option')].map(o=>o.textContent)")
    check("N3 '(해안선 NNNkm)' 표기 + 창원시 성산구 띄어쓰기", txt and all('(해안선 ' in t for t in txt) and any(t.startswith('창원시 성산구') for t in txt), txt[:4])
    pn=E("(()=>{const r=__QA.REC.data.find(x=>x.n==='창원시 성산구'); if(!r)return null; return __QA.placeName(r.p[0],r.p[1]);})()")
    check('N4 찍은 자리 이름 = 사천과 같은 짧은 모양 (창원 성산구 ○○동 앞바다)', pn and pn.startswith('창원 성산구 ') and pn.endswith('바다'), pn)
    # ── U-49 수온 ──
    E("__QA.select(34.92,128.07,null)"); pg.wait_for_timeout(800)
    E("__QA.pointView('none')")
    LAT,LON=34.92,128.07
    def setObs(dkm,dv,dh=0):
        return E(f"""(()=>{{const la={LAT}, lo={LON}+{dkm}/(111*Math.cos({LAT}*Math.PI/180)), th=__QA.tH()+{dh}, ms=Date.now(), at=new Date(ms+9*3600e3).toISOString().slice(0,16).replace('T',' ');
          const tho=(ms-Date.parse(new Date().toISOString()))/3600000; const fs=__QA.tempAt(la,lo,__QA.tH()); if(fs==null)return null;
          __QA.DTO.st=[{{c:'TST',la,lo,n:'시험관측소'}}]; __QA.WT.obs.clear(); __QA.WT.obs.set('TST',{{o:{{st:'시험관측소',sc:'TST',la,lo,wtem:fs+{dv},at}},at:Date.now()}});
          const w=__QA.wtemp({LAT},{LON},th); return w?[w.src,+(w.v-w.f).toFixed(3),+w.K.toFixed(3),+w.km.toFixed(1)]:null;}})()""")
    E("__QA.WT.obs.clear(); __QA.DTO.st=[]")
    w0=E(f"(()=>{{const w=__QA.wtemp({LAT},{LON},__QA.tH()); return w?[w.src,w.v===w.f]:null;}})()")
    check('W1 관측소 자료가 없으면 예보 그대로', w0==['예보',True], w0)
    w1=setObs(0.2,1.0)
    check('W2 관측소가 바로 옆이면 실측쪽 K≈0.8 (보정 +0.8℃)', w1 and w1[0]=='섞음' and abs(w1[1]-0.8)<0.05 and abs(w1[2]-0.8)<0.05, w1)
    w2=setObs(15,1.0)
    check('W3 15km면 K=0.8×e⁻¹≈0.29', w2 and abs(w2[2]-0.294)<0.02 and abs(w2[1]-w2[2])<0.02, w2)
    nn=E(f"(()=>{{const m=(d)=>{{__QA.DTO.st=[{{c:'X',la:{LAT},lo:{LON}+d/(111*Math.cos({LAT}*Math.PI/180)),n:'x'}}]; return !!__QA.wtNear({LAT},{LON});}}; return [m(29),m(31)];}})()")
    check('W4 관측소가 30km 안이면 쓰고 넘으면 안 씀', nn==[True,False], nn)
    setObs(0.2,1.0)
    k_now=E(f"__QA.wtemp({LAT},{LON},__QA.tH()).K"); k_fut=E(f"__QA.wtemp({LAT},{LON},__QA.tH()+24)")
    kf=k_fut['K'] if k_fut else None
    check('W5 내일 값은 보정이 e⁻¹배로 줄어듦', kf is not None and abs(kf/k_now-0.368)<0.03, [k_now,kf])
    E("__QA.DTO.st=[{c:'TST',la:%s,lo:%s,n:'시험관측소'}]"%(LAT,LON)); E("__QA.saveFavs&&0")
    E("__QA.select(%s,%s,null)"%(LAT,LON)); pg.wait_for_timeout(700)
    tx=E("document.querySelector('#fcTemp').textContent")
    check("W6 상태창엔 '🌡 14.6℃' 숫자만 (근거·'예보' 글자 없음)", re.fullmatch(r'\s*·\s*🌡️?\s*\d+\.\d℃',tx or '') is not None, tx)
    E("__QA.wtSaveDiff({sc:'TST',la:%s,lo:%s,wtem:15.5,at:new Date(Date.now()+9*3600e3).toISOString().slice(0,16).replace('T',' ')})"%(LAT,LON))
    sv=E("__QA.pref('wtDiff','')")
    check('W7 관측−예보 차이를 날마다 저장', 'TST' in (sv or ''), (sv or '')[:80])
    # ── U-43 ──
    E("__QA.pointView('none')"); tap(200,470); pg.wait_for_timeout(800)
    m=E("""(()=>{const f=document.querySelector('#fCard'), r=e=>{const b=document.querySelector(e).getBoundingClientRect();return [Math.round(b.width),Math.round(b.height)];};
      return {on:f.classList.contains('show'), h:f.offsetHeight, w:f.offsetWidth, big:getComputedStyle(document.querySelector('#iSlack')).fontSize, btn:['#fcGraph','#fcNav','#fcNearRec'].map(r), ov:[...document.querySelectorAll('#fCard .fc-a button')].some(b=>b.scrollWidth>b.clientWidth+1),
      lbl:[...document.querySelectorAll('#fCard .fc-a button')].map(b=>b.textContent), badge:document.querySelector('#iSlackIn').textContent, v:document.querySelector('#fCard .fc-v').textContent};})()""")
    check('F1 F28: 다음 정조 큰 칸 24px + [N시간 뒤] 딱지', m['on'] and m['big']=='24px' and re.search(r'(분|시간) 뒤',m['badge'] or ''), [m['big'],m['badge']])
    check('F2 버튼 3개 ≥44px 높이, 글자 안 넘침', all(b[1]>=44 for b in m['btn']) and not m['ov'] and m['lbl']==['📈 그래프','🚗 길 안내','⭐ 주변 추천'], [m['btn'],m['ov'],m['lbl']])
    check('F3 F28 높이 ≤ 270px (시안 254)', m['h']<=270, [m['h'],m['w']])
    check('F4 유속·방향·상태·🌡 한 줄', all(k in m['v'] for k in ['유속','kn','🌡']), m['v'])
    E("document.querySelector('#fcNav').click()"); pg.wait_for_timeout(300)
    nv=E("[document.querySelector('#fcNavs').style.display, document.querySelectorAll('#fcNavs [data-nav]').length]")
    check('F5 [🚗 길 안내] → TMAP·카카오맵·네이버지도 고르기', nv==['',3], nv)
    d=E("(()=>{const d=__QA.fcDest(); const s=__QA.sel(); const cp=__QA.coastPt(s.lat,s.lng); return [d.la,d.lo,cp&&cp.km<15?cp.la:s.lat,cp&&cp.km<15?cp.lo:s.lng];})()")
    check('F6 F28 길 안내 목적지 = 가장 가까운 해안 점 (U-16과 같은 점)', d[0]==d[2] and d[1]==d[3], d)
    E("__QA.NAVS.tmap&&0; document.querySelector('#fcNavs [data-nav=tmap]').click()"); pg.wait_for_timeout(300)
    nl=E("window.__navLast&&window.__navLast.url||''")
    check('F7 TMAP 주소에 해안 점 좌표', ('%.4f'%d[0]) in nl or ('%.3f'%d[0]) in nl, nl[:140])
    E("__QA.pointView('none')")
    E("""(()=>{const c=__QA.map.containerPointToLatLng([200,300]), n=Date.now(); __QA.pinPop({la:c.lat,lo:c.lng,score:82,fav:'시험 자리',dong:'시험동',rocks:2,
      best:{sp:0.8,f:1,w:{s:n+3600e3,t:n+7200e3,ms:n+5400e3,hi:true}}},0,{n:'시험군'});})()"""); pg.wait_for_timeout(500)
    p6=E("""(()=>{const f=document.querySelector('#pinPop'); return {h:f.offsetHeight, lbl:[...f.querySelectorAll('.fc-a button')].map(b=>b.textContent), hasStar:!!f.querySelector('.pp-h .star'), win:!!f.querySelector('.pp-win'), v:f.querySelector('.fc-v').textContent,
      btn:[...f.querySelectorAll('.fc-a button')].map(b=>Math.round(b.getBoundingClientRect().height)), ov:[...f.querySelectorAll('.fc-a button')].some(b=>b.scrollWidth>b.clientWidth+1)};})()""")
    check('P1 P6: 같은 버튼 3개 + 헤더 ☆ + 승부 시간 큰 칸', p6['lbl']==['📈 그래프','🚗 길 안내','⭐ 주변 추천'] and p6['hasStar'] and p6['win'] and all(b>=44 for b in p6['btn']) and not p6['ov'], p6)
    check('P2 P6 높이 ≤ 290px (시안 271) · 유속·🌡 한 줄', p6['h']<=290 and '유속' in p6['v'] and '🌡' in p6['v'], [p6['h'],p6['v']])
    E("document.querySelector('#pinPop [data-a=navs]').click()"); pg.wait_for_timeout(200)
    pn2=E("document.querySelector('#pinPop .navs').style.display")
    check('P3 P6 [🚗 길 안내] → 3개 고르기', pn2=='', pn2)
    # 큰 글씨 130%: 그림 글자 빼고도 안 넘침
    E("document.documentElement.style.fontSize='130%'; __QA.fcFit()"); pg.wait_for_timeout(300)
    bg=E("[document.querySelector('#pinPop .fc-a').classList.contains('noemo'), [...document.querySelectorAll('#pinPop .fc-a button')].some(b=>b.scrollWidth>b.clientWidth+1)]")
    check('P4 큰 글씨에서도 버튼 글자가 안 넘침 (넘치면 그림 글자 뺌)', bg[1] is False, bg)
    E("document.documentElement.style.fontSize=''")
    check('Z 스크립트 오류 없음', not errs, errs[:3])
    br.close()
print(f'\n결과 {sum(res)}/{len(res)}')
'''
pre,inner=head.split("exec(src+r'''")
exec(pre+"exec(src+r'''"+inner+body+"''')")
