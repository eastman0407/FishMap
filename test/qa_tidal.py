# 갯벌 범위 점선 시험 (build-21)
import sys
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
exec(src+'''
    N="__QA.tidalLayer._items.length"
    go(12,37.0562,126.5003,1500)
    n12=E(N); st=E("__QA.tidalLayer._items[0]&&__QA.tidalLayer._items[0].o")
    check('T1 기본 켜짐: 12단계 갯벌 구역(당진·평택) 표시', E("__QA.TIDAL.on") and n12>0, f'{n12}개')
    check('T2 점선·옅은 채움·터치 막지 않음', st and st.get('dashArray') and st.get('fillOpacity',1)<=0.2 and st.get('interactive') is False, st)
    go(10,37.0562,126.5003,800); check('T3 10단계에서는 숨김', E(N)==0, E(N))
    go(12,34.95,128.0,800); check('T4 자료 없는 곳(사천만)은 표시 없음', E(N)==0, E(N))
    go(12,37.0562,126.5003,800)
    E("document.querySelector('#tidalChk').checked=false;document.querySelector('#tidalChk').onchange()"); pg.wait_for_timeout(300)
    check('T5 설정에서 끄면 사라지고 저장', E(N)==0 and E("AndroidBridge.getPref('tidalOn')")=='0')
    E("document.querySelector('#tidalChk').checked=true;document.querySelector('#tidalChk').onchange()"); pg.wait_for_timeout(500)
    check('T6 다시 켜면 표시', E(N)>0, E(N))
    ring=E("__QA.TIDAL.data.find(t=>t[0]<37.06&&t[2]>37.05)")
    check('T7 좌표 변환 위치 확인(당진 해안 위도·경도 범위)', ring and 36.9<ring[0]<37.2 and 126.3<ring[1]<126.9, ring[:4] if ring else None)
    check('T8 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
