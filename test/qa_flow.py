# 할 일 시험 (U-37, 11-21) — 사용자가 하는 일을 처음부터 끝까지 따라감. UX 가이드 7장 '과업 기반 시험'.
# 버튼은 가능한 한 '보이는 글자'로 찾아 실제 손가락처럼 누름(화면 모양이 바뀌어도 덜 깨지게). 누른 횟수도 잼.
# 각 과업의 통과 기준은 형상관리.md '1-3. 통과 기준(H-9)'의 같은 번호와 맞춤.
import sys, time, re
sys.argv=sys.argv[:1]
_c=open('test/qa_b48.py').read(); exec(_c.split("exec(src+'''")[0])
src=src+_c.split("exec(src+'''")[1].split("    go(13,34.92,128.07,0); pg.wait_for_timeout(800)\n    btn=")[0]
exec(src+r'''
    TAPS=[0]
    def wait(js,limit):
        t=time.time()
        while time.time()-t<limit:
            if E(js): return round(time.time()-t,1)
            pg.wait_for_timeout(200)
        return None
    def tapmap(x,y):
        TAPS[0]+=1; E(f"(()=>{{const m=document.querySelector('#map').getBoundingClientRect(); _map.fire('click',{{latlng:_map.containerPointToLatLng([{x}-m.left,{y}-m.top])}});}})()"); pg.wait_for_timeout(400)
    def press(text, within='body'):
        """보이는 버튼·칩·줄 가운데 글자가 들어 있는 것을 손가락으로 누름. 못 찾으면 False"""
        r=E(f"""(()=>{{const els=[...document.querySelectorAll('{within} button, {within} .rr, {within} li, {within} [data-go], {within} label, {within} .fav')].filter(e=>e.checkVisibility&&e.checkVisibility({{opacityProperty:true,visibilityProperty:true}})&&e.getBoundingClientRect().width>0);
          const e=els.find(e=>e.textContent.replace(/\\s+/g,' ').includes({text!r})); if(!e)return null; e.scrollIntoView({{block:'nearest'}}); const r=e.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];}})()""")
        if not r: return False
        TAPS[0]+=1; pg.mouse.click(r[0],r[1]); pg.wait_for_timeout(450); return True
    def shown(q): return E(f"(()=>{{const e=document.querySelector('{q}'); return !!(e&&e.checkVisibility({{opacityProperty:true,visibilityProperty:true}}))}})()")
    def text(q): return E(f"(()=>{{const e=document.querySelector('{q}'); return e?e.innerText:''}})()")
    go(13,34.93,128.07,0); pg.wait_for_timeout(1200); E("document.querySelector('#nowSeg [data-v=now]').click()")
    # ── T1 찍은 자리의 '언제 물이 멈추나'를 한 번에 ──
    TAPS[0]=0; tapmap(200,470)
    c=text('#fCard')
    check('T1 바다를 한 번 누르면 유속·방향·다음 정조 시각이 바로 보임 (누름 1번)', TAPS[0]==1 and shown('#fCard') and re.search(r'다음 정조\s*\n?\s*(?:\S+\s+)?\d\d:\d\d',c) and 'm/s' in c, [TAPS[0], c.replace('\n',' | ')[:120]])
    # ── T2 그래프로 하루 흐름 보고, 시각을 옮기면 값이 따라옴, 내리면 같은 자리 상태창 ──
    s0=text('#iSum') if shown('#info') else ''
    TAPS[0]=0; ok=press('상세 보기')
    g1=E("[document.querySelector('#tide')._g&&document.querySelector('#tide')._g.hs.filter(v=>v!=null).length, document.querySelector('#iSum').innerText]")
    E("const s=document.querySelector('#slider');s.value=+s.value+240;s.dispatchEvent(new Event('input'))"); pg.wait_for_timeout(400)
    g2=E("document.querySelector('#iSum').innerText")
    pg.mouse.click(*E("(()=>{const r=document.querySelector('#infoGrip').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")); pg.wait_for_timeout(600)
    check('T2 [그래프] → 하루 물높이·유속 그래프, 시각을 옮기면 요약이 바뀌고, 손잡이를 누르면 같은 자리 상태창으로', ok and g1[0]>=140 and g1[1]!=g2 and shown('#fCard') and not shown('#info'), [ok,g1[0],g1[1][:30],g2[:30]])
    E("document.querySelector('#nowBtn').click()")
    # ── T3 즐겨찾기 저장 → 목록에서 다시 열기 ──
    TAPS[0]=0; press('☆','#fCard'); E("document.querySelector('#favName').value='흐름 시험 자리'"); press('저장','#namebox')
    E("__QA.pointView('none')"); press('★','.top'); ok=press('흐름 시험 자리','#favPanel')
    check('T3 ☆ → 이름 → 저장 → ★ 목록에서 누르면 그 자리 상태창 (누름 5번 이하)', ok and shown('#fCard') and '흐름 시험 자리' in text('#fcName') and TAPS[0]<=5, [TAPS[0], text('#fcName')])
    E("__QA.pointView('none')")
    # ── T4 입질 기록 → 기록 탭에서 어종 적기 → 다시 열어도 남아 있음 ──
    E("__QA.saveLog([])"); E("__QA.placeMe(34.93,128.07,10)")
    TAPS[0]=0; press('입질','.mapbox'); n=E("__QA.loadLog().length")
    opened=press('기록 보기','#toast'); press('이름 없는','#logList') or press('내 위치','#logList')
    E("(()=>{const i=document.querySelector('#logList [data-f=fish]'); i.value='갑오징어'; i.dispatchEvent(new Event('change',{bubbles:true}));})()"); pg.wait_for_timeout(200)
    E("document.querySelector('#planClose').click()"); E("document.querySelector('#planBtn').click()"); press('기록','.ptabs')
    check('T4 🎣 한 번에 기록 → 📓 기록 탭에서 어종 적기 → 다시 열어도 남음', opened and n==1 and E("__QA.loadLog()[0].fish")=='갑오징어' and '갑오징어' in text('#logList'), [n, E("__QA.loadLog()[0].fish")])
    E("document.querySelector('#planClose').click()")
    # ── T5 주변 추천 → 핀 → 길 안내 앱이 그 자리로 ──
    go(13,34.93,128.07,0); pg.wait_for_timeout(800)
    E("window.__nav=[]; window.AndroidBridge.openExt=(u,p)=>{window.__nav.push([u,p]); return 'ok';}")
    TAPS[0]=0; tapmap(200,470); press('주변 추천','#fCard'); t=wait("!__QA.REC.busy&&__QA.REC.res&&__QA.REC.res.pick&&__QA.REC.res.pick.length>0",240)
    pin=E("__QA.REC.layer.getLayers().filter(l=>l.options&&l.options.icon).length")
    E("__QA.REC.layer.getLayers().find(l=>l.options&&l.options.icon).fire('click')"); TAPS[0]+=1; pg.wait_for_timeout(500)
    c=E("[document.querySelector('#pinPop')._c.c.la, document.querySelector('#pinPop')._c.c.lo]")
    press('길 안내','#pinPop'); press('TMAP','#pinPop'); nav=E("window.__navLast?[window.__navLast.url,window.__navLast.pkg]:null")
    okc=nav and f"rGoX={c[1]:.6f}" in nav[0] and f"rGoY={c[0]:.6f}" in nav[0]
    check('T5 자리 → ⭐ 주변 추천 → 핀 → TMAP: 그 핀 좌표로 길 안내 (누름 5번: U-43 길 안내 → 앱 고르기 한 단계 추가)', t is not None and pin>0 and okc and TAPS[0]==5, [t, pin, TAPS[0], nav and nav[0][:90]])
    E("__QA.pinPopClose()")
    # ── T6 뒤로가기(제스처)는 늘 맨 위 창부터 닫음 ──
    tapmap(200,470); press('상세 보기'); E("document.querySelector('#planBtn').click()")
    seq=[]
    for _ in range(4):
        r=E("window.__onBack()"); pg.wait_for_timeout(350)
        seq.append([r, E("document.querySelector('#planPanel').classList.contains('show')"), E("__QA.PV.mode")])
    check('T6 뒤로가기: 출조 도우미 → 그래프 시트 → 상태창 → 끝(앱 뒤로)', seq==[[True,False,'sheet'],[True,False,'card'],[True,False,'none'],[False,False,'none']], seq)
    # ── T7 인터넷이 끊겨도 본 곳의 흐름·조석은 계속 보임 ──
    E("window.dispatchEvent(new Event('offline'))"); tapmap(200,470)
    c=text('#fCard')
    check('T7 인터넷이 끊겨도 안내가 뜨고, 본 곳의 유속·조석은 그대로', shown('#offBar') and 'm/s' in c and '🌊' in c, c.replace('\n',' | ')[:100])
    E("window.dispatchEvent(new Event('online'))")
    check('Z 스크립트 오류 없음', not errs, errs[:3])
    br.close()
print(f'\n결과 {sum(res)}/{len(res)}')
''')
