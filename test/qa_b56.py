# build-56 (1묶음): H-15 흐름 방향 믿음 · H-12 테두리 값 고정 · H-14 지금 따라가기
#  지키는 시험(H-15 ⑥): 확대·축소 중 어떤 순간에도 '화면에 그리는 방향'이 끝 값과 90° 넘게 다르면 실패
import sys, time, json, math
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0]
exec(src+r'''
    PTS=[[34.885,128.09],[34.878,128.10],[34.889,128.085],[34.870,128.11],[34.875,128.10],[34.882,128.096]]
    PT="JSON.stringify(%s.map(([a,o])=>{__QA.simFramePrep(); const q=_map.latLngToContainerPoint([a,o]); const v=__QA.flowDraw(q.x,q.y,__QA.tH()); const f=__QA.flowAt(a,o,__QA.tH()); return v?[+v.vE.toFixed(4),+v.vN.toFixed(4),+v.c.toFixed(2),!!(f&&f.pend)]:null}))"%json.dumps(PTS)
    def ang(a,b):
        if not a or not b: return None
        if math.hypot(a[0],a[1])<0.03 or math.hypot(b[0],b[1])<0.03: return None  # 거의 정조는 방향 의미 없음
        d=math.degrees(math.atan2(a[1],a[0])-math.atan2(b[1],b[0])); d=(d+180)%360-180; return abs(d)
    def done(): return E("__QA.SIM.on&&__QA.SIM.done")
    def run(act,lim=150):
        act(); t=time.time(); snaps=[]
        while time.time()-t<lim:
            snaps.append(json.loads(E(PT)))
            if done() and time.time()-t>2.5: break
            pg.wait_for_timeout(200)
        pg.wait_for_timeout(1200); fin=json.loads(E(PT))
        worst=[a for s in snaps for i in range(len(PTS)) for a in [ang(s[i],fin[i])] if a is not None]
        return snaps,fin,(max(worst) if worst else 0),sum(1 for w in worst if w>90)
    E("document.querySelector('#simBtn').classList.contains('on')||document.querySelector('#simBtn').click()")
    go(12,34.882,128.096,3000)
    s13,f13,m13,n13=run(lambda:go(13,34.882,128.096,0))
    first=[x for x in s13[0] if x]
    check('H1 ⚓ 처음 계산: 계산 중엔 흰 선(유속 색 0)으로 예보 방향만, 숫자는 계산 중', len(first)>0 and all(x[2]==0 for x in first) and all(x[3] for x in first), s13[0])
    mid=[x for s in s13 for x in s if x and 0<x[2]<1]
    check('H2 끝난 결과는 1초에 걸쳐 색이 입혀짐(중간 색 비중이 보임) → 끝나면 전체 색', len(mid)>0 and all(x and x[2]==1 for x in f13), [len(mid), f13])
    check('H3 13단계로 확대하는 동안 화면 방향이 끝 값과 90° 넘게 다른 순간 없음', n13==0, f'가장 큰 차이 {m13:.0f}°')
    s15,f15,m15,n15=run(lambda:go(15,34.882,128.096,0))
    check('H4 15단계로 확대(더 자세한 계산)하는 동안도 90° 넘는 순간 없음', n15==0, f'가장 큰 차이 {m15:.0f}°')
    p15=[x for s in s15 for x in s if x]
    check('H5 15단계 계산 중에도 이미 끝난 13단계 결과(색)로 보여 줌 — 흰 선으로 돌아가지 않음', all(x[2]>0 for x in p15), sorted({x[2] for x in p15})[:4])
    s13b,f13b,m13b,n13b=run(lambda:go(13,34.882,128.096,0),lim=8)
    same=all(a is None or a<1 for a in [ang(f13b[i],f15[i]) for i in range(len(PTS))])
    check('H6 다시 13단계로 축소해도 자세한(16) 결과를 그대로 씀 → 방향이 안 바뀜', same and n13b==0, [f13b[:2],f15[:2]])
    # 배지: ⚓ 정밀 계산 중 n/m
    E("__QA.SIM.view.length&&0"); bd=E("__QA.simProg()")
    check('H7 계산 중 배지 글: ⚓ 정밀 계산 중 n/m', bd.startswith('⚓ 정밀 계산 중 ') and '/' in bd, bd)
    # H-12: 같은 구역·같은 점이면 테두리 보간이 받은 점 순서·화면 단계와 상관없이 같음
    h=E("""(()=>{const T=[...__QA.SIM.tiles.values()].find(t=>t.state==='ready'&&!t.nodata); if(!T)return null;
      const a=__QA.simInterp(T); const ll=_map.unproject([T.ox+300,T.oy+300],T.lv); const v1=__QA.interpAt(a,ll.lat,ll.lng,__QA.tH());
      const keep=__QA.RD.pts; __QA.RD.pts=keep.slice().reverse().concat(keep.slice(0,5)); T.ipVer=-1; const v2=__QA.interpAt(__QA.simInterp(T),ll.lat,ll.lng,__QA.tH());
      __QA.RD.pts=keep; T.ipVer=-1; __QA.simInterp(T); return [v1&&+v1.vE.toFixed(6),v2&&+v2.vE.toFixed(6)];})()""")
    check('H8 (H-12) 테두리 값: 받은 점 순서가 달라도(중복 포함) 같은 값', h and h[0] is not None and h[0]==h[1], h)
    # H-14 지금 따라가기
    nm=E("__QA.nowMin()"); tm=E("__QA.tMin()")
    check('H9 지금 = 실제 분(10분 반올림 안 함)', tm==nm and E("__QA.sT()")==round(nm/10)*10, [tm,nm])
    E("const s=document.querySelector('#slider'); s.value=600; s.dispatchEvent(new Event('input'))")
    off=E("[__QA.NOWF.on, __QA.tMin()]")
    E("const o=Date.now; Date.now=()=>o()+180000; __QA.nowFollow(); window.__t1=__QA.tMin(); Date.now=o;")
    check('H10 시간 막대를 움직이면 따라가기 꺼짐(시각 그대로)', off==[False,600] and E("window.__t1")==600, [off,E("window.__t1")])
    E("document.querySelector('#nowBtn').click()")
    E("const o=Date.now; Date.now=()=>o()+180000; __QA.nowFollow(); window.__t2=[__QA.tMin(),__QA.nowMin(),document.querySelector('#timeLabel').textContent]; Date.now=o;")
    t2=E("window.__t2")
    check('H11 [지금]을 누르면 따라가기 켜짐 → 3분 뒤 시각도 따라감(1분 단위 표시)', E("__QA.NOWF.on") and t2[0]==t2[1] and t2[0]==nm+3, t2)
    E("document.querySelector('#play').click(); document.querySelector('#play').click()")
    check('H12 재생을 누르면 따라가기 꺼짐', not E("__QA.NOWF.on"))
    check('H13 스크립트 오류 없음', not errs, errs[:2])
    print(f"결과: {sum(res)}/{len(res)}")
    br.close()
''')
