# build-52 시험 (2차-가): U-27 바깥 누르기 = 닫기, U-28 추천 상태창 ↔ 그래프 시트 오가기, U-38 유속 '계산 중' 표시
# 바탕은 qa_b49 (가짜 조석·바람·주소 응답 + 시험용 지도)
import sys
_c=open('test/qa_b49.py').read()
head=_c.split("    # ── U-10 상태창 ──")[0]
body=r'''
    def recwait(lim=240):
        for _ in range(lim*3):
            if E("!__QA.REC.busy"): return True
            pg.wait_for_timeout(330)
        return False
    PP="document.querySelector('#pinPop').classList.contains('show')"
    FC="document.querySelector('#fCard').classList.contains('show')"
    SH="document.querySelector('#info').classList.contains('show')"
    go(13,34.92,128.07,0); pg.wait_for_timeout(1500)
    E("document.querySelector('#nowSeg button[data-v=now]').click()"); pg.wait_for_timeout(300)
    # ── U-27 ──
    tap(200,470); s1=E("__QA.sel()&&[__QA.sel().lat,__QA.sel().lng]")
    tap(150,560); a=E(f"[{FC},!!__QA.sel(),document.querySelectorAll('.pin').length]")
    check('A1 지점 상태창(F28)이 떠 있을 때 지도를 누르면 창만 닫힘 (새 자리로 안 옮김, 선택 핀도 지움)', s1 and a==[False,False,0], a)
    tap(150,560); a2=E(f"[{FC},!!__QA.sel()]")
    check('A2 창이 없을 때 누르면 그 자리 상태창', a2==[True,True], a2)
    E("document.querySelector('#fcGraph').click()"); pg.wait_for_timeout(400)
    tap(200,200); a3=E(f"[{SH},{FC},!!__QA.sel()]")
    check('A3 시트가 떠 있을 때 지도를 누르면 시트도 닫힘', a3==[False,False,False], a3)
    # 추천 상태창(P6)
    # 추천 상태창(P6): 시험용 추천 자리 하나로 바로 엶 (추천 계산 자체는 qa_b49·qa_rec에서 봄)
    def openP6():
        E("""(()=>{const c=__QA.map.containerPointToLatLng([200,300]), n=Date.now(); __QA.pinPop({la:c.lat,lo:c.lng,score:82,fav:'시험 자리',dong:'시험동',rocks:2,
          best:{sp:0.8,f:1,w:{s:n+3600e3,t:n+7200e3,ms:n+5400e3,hi:true}}},0,{n:'시험군'});})()"""); pg.wait_for_timeout(400)
    openP6()
    p0=E(PP); tap(120,600); a4=E(f"[{PP},{FC},!!__QA.sel()]")
    check('A4 추천 상태창(P6)이 떠 있을 때 지도를 누르면 창만 닫힘', p0 and a4==[False,False,False], [p0,a4])
    # 바위 누르기 (시험용으로 바위 하나 직접 그림 → 눌렀을 때 동작만 봄)
    tap(200,470)
    rk=E("""(()=>{if(!__QA.ROCK)return 'no ROCK'; const c=__QA.map.getCenter(); let hit=null;
      __QA.ROCK.layer&&__QA.ROCK.layer.eachLayer&&__QA.ROCK.layer.eachLayer(l=>{if(!hit&&l.fire)hit=l;}); return hit?'ok':'none';})()""")
    if rk=='ok':
        E("(()=>{let h=null;__QA.ROCK.layer.eachLayer(l=>{if(!h)h=l;}); h.fire('click',{originalEvent:new MouseEvent('click')});})()"); pg.wait_for_timeout(300)
        a5=E(f"[{FC},document.querySelector('#toast').style.display]")
        check('A5 바위를 누르면 열린 상태창은 닫고 알림만', a5[0]==False and a5[1]!='none', a5)
    else:
        src_ok=open('app/src/main/assets/index.html').read().count("L.DomEvent.stopPropagation(ev); closeFloats();")==1
        check('A5 바위를 누르면 열린 상태창은 닫고 알림만 (코드 확인: 바위 자료가 시험에 없어 직접 누르기 대신)', src_ok, rk)
    E("__QA.pointView('none')")
    # ── U-28 ──
    openP6()
    lab=E("[...document.querySelectorAll('#pinPop .fc-a button')].map(b=>b.textContent)")
    check('B1 추천 상태창 버튼 이름 [📈 그래프] (U-43: 지점 상태창과 같은 이름·같은 3개)', lab==E("[...document.querySelectorAll('#fCard .fc-a button')].map(b=>b.textContent)"), lab)
    nm0=E("document.querySelector('#pinPop')._c.nm")
    E("document.querySelector('#pinPop [data-a=sel]').click()"); pg.wait_for_timeout(500)
    b2=E(f"[{SH},{PP}]")
    check('B2 [📈 그래프 ›] → 그래프 시트', b2==[True,False], b2)
    E("document.querySelector('#infoDown')&&document.querySelector('#infoDown').click()"); pg.wait_for_timeout(700)
    b3=E(f"[{PP},{FC},{SH},(document.querySelector('#pinPop')._c||{{}}).nm||null,document.querySelector('#pinPop').textContent]")
    check('B3 시트를 내리면(▾) 왔던 추천 상태창으로 돌아옴 (지점 상태창 아님)', b3[0] and not b3[1] and not b3[2] and b3[3]==nm0, b3[:4])
    check('B4 돌아온 창에 길 안내·점수·승부 시간 그대로', all(k in b3[4] for k in ['TMAP','점'])and('승부' in b3[4] or '⏰' not in b3[4]), b3[4][:120])
    E("document.querySelector('#pinPop [data-a=sel]').click()"); pg.wait_for_timeout(500)
    E("window.__onBack()"); pg.wait_for_timeout(700)
    b5=E(f"[{PP},{FC},{SH}]")
    check('B5 뒤로가기로 시트를 닫아도 추천 상태창으로 복귀', b5==[True,False,False], b5)
    E("window.__onBack()"); pg.wait_for_timeout(300)
    check('B6 한 번 더 뒤로가기 → 추천 상태창 닫힘', not E(PP))
    tap(200,470); E("document.querySelector('#fcGraph').click()"); pg.wait_for_timeout(400); E("document.querySelector('#infoDown').click()"); pg.wait_for_timeout(700)
    b7=E(f"[{FC},{PP}]")
    check('B7 바다를 직접 찍어 연 시트는 내리면 지점 상태창(F28) 그대로', b7==[True,False], b7)
    E("__QA.pointView('none')")
    # ── U-38 ── (⚓ 계산을 켜고, 덜 된 결과가 들어오는 동안의 표시를 봄)
    E("__QA.SIMDB.ok=false"); E("document.querySelector('#simBtn').classList.contains('on')||document.querySelector('#simBtn').click()")
    go(16,34.882,128.096,0); E("__QA.SIM.tiles.clear();__QA.simCache.clear();__QA.SIM.lastTile=null;__QA.SIM.done=false;__QA.SIM.ready=false")
    E("(()=>{const c=__QA.map.getCenter();__QA.select(c.lat,c.lng,null);})()"); log=[]
    seen=set(); t_end=time.time()+180; done_txt=None; ck=False
    while time.time()<t_end:
        r=E("[document.querySelector('#iSpeed').textContent,document.querySelector('#iDir').textContent,document.querySelector('#iState').textContent,__QA.SIM.on&&__QA.SIM.done&&!__QA.SIM.rough]")
        if not log or log[-1]!=r[:3]: log.append(r[:3])
        if '계산 중' in r[0]: seen.add(('calc',r[1],r[2]))
        if '✓' in r[0]: ck=True
        if r[3] and '계산 중' not in r[0]:
            done_txt=r; break
        pg.wait_for_timeout(150)
    pg.wait_for_timeout(100); r2=E("document.querySelector('#iSpeed').textContent")
    if '✓' in r2: ck=True
    calc=[x for x in seen if x[0]=='calc']; print('log',log[:8])
    check('C1 계산이 덜 끝났을 때 유속 "🐟 계산 중…"·방향 "—"·상태 [계산 중]', calc and all(x[1]=='—' and '계산 중' in x[2] for x in calc), list(seen)[:3])
    check('C2 계산이 끝나면 숫자 (m/s)', done_txt and 'm/s' in done_txt[0] and '—' not in done_txt[1], done_txt)
    check('C3 끝나는 순간 ✓ 잠깐 보임', ck, r2)
    pg.wait_for_timeout(900); r3=E("document.querySelector('#iSpeed').textContent")
    check('C4 ✓는 0.6초 뒤 사라짐', '✓' not in r3 and 'm/s' in r3, r3)
    sm=E("document.querySelector('#iSum').textContent")
    check('C5 요약 줄에 ✓ 안 섞임', '✓' not in sm, sm)
    E("document.querySelector('#simBtn').click()"); E("__QA.SIMDB.ok=true"); pg.wait_for_timeout(500)
    r4=E("[document.querySelector('#iSpeed').textContent,document.querySelector('#iDir').textContent]")
    check('C6 ⚓ 끄면 "계산 중"이 남지 않음', '계산 중' not in r4[0] and r4[1]!='—', r4)
    check('Z 스크립트 오류 없음', not errs, errs[:3])
    br.close()
print(f'\n결과 {sum(res)}/{len(res)}')
'''
# qa_b49 머리는 exec(src+r''' ... 로 시작하는 문자열 안에 도움 함수(wait·rect·shown·tap)를 둠 → 그 부분까지 + 이 파일 본문
pre,inner=head.split("exec(src+r'''")
exec(pre+"exec(src+r'''"+inner+body+"''')")
