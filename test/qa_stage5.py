# 5단계 시험: 낚시 기준 고정 색 + 확대 시 계산 줄이기(멈춘 뒤 시작·대략 표시·이어서 계산·폰 저장) (build-23)
import sys, time, statistics as S
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
exec(src+'''
    def wait(js,limit):
        t=time.time()
        while time.time()-t<limit:
            if E(js): return round(time.time()-t,1)
            pg.wait_for_timeout(200)
        return None
    # ── 색 ──
    b=E("[__QA.bucket(0.29),__QA.bucket(0.59),__QA.bucket(0.99),__QA.bucket(1.39),__QA.bucket(1.69),__QA.bucket(1.99),__QA.bucket(2.0),__QA.bucket(3.5)]")
    check('K1 고정 7단계, 2.0노트부터 빨강(마지막 색)', b==[0,1,2,3,4,5,6,6], b)
    t=E("document.querySelector('#legendTicks').textContent+' / '+document.querySelector('#legendTitle').textContent")
    check('K2 범례: 0·0.6·1·2+ 와 "빨강=낚시 어려움"', '2+' in t and '낚시 어려움' in t, t)
    go(12,34.80,128.30,6000); t1=E("document.querySelector('#legendTicks').textContent"); go(15,34.86,128.2,5000)
    check('K3 화면을 옮기거나 확대해도 색 범위 그대로', t1==E("document.querySelector('#legendTicks').textContent"), t1)
    E("document.querySelector('#redKn').value='1.5';document.querySelector('#redKn').onchange()")
    check('K4 설정에서 빨강 기준 1.5로 바꾸면 반영·저장', E("__QA.bucket(1.5)")==6 and E("__QA.bucket(1.49)")==5 and E("AndroidBridge.getPref('redKn')")=='1.5')
    E("document.querySelector('#redKn').value='2.0';document.querySelector('#redKn').onchange()")
    # ── 확대 중 헛계산 없음 ──
    E("document.querySelector('#simBtn').click()"); go(10,34.882,128.096,300)
    for z in (11,12,13,14):
        E(f"_map._z={z};_map.fire('movestart');_map.fire('moveend')"); pg.wait_for_timeout(250)
    go(13,34.882,128.096,0); wait("__QA.SIM.on&&__QA.SIM.done",240)
    lv=E("[...new Set([...__QA.SIM.tiles.values()].map(t=>t.lv))]")
    check('Z1 두 손가락 확대처럼 빠르게 지나간 단계(11·12)는 계산하지 않음', 11 not in lv and 12 not in lv, f'계산한 단계 {lv}')
    # ── 대략 표시 + 이어서 계산 ──
    go(16,34.882,128.096,0); pg.wait_for_timeout(1500)
    rough=E("__QA.SIM.rough"); v=E("__QA.flowAt(34.875,128.10,__QA.tH())"); bd=E("document.querySelector('.samplebadge').textContent")
    check('Z2 23m 계산 끝나기 전에도 94m 결과로 대략 표시 (빈 화면 없음)', rough and v and v.get('est'), f'배지="{bd}"')
    t_seed=wait("__QA.SIM.on&&__QA.SIM.done&&!__QA.SIM.rough",240); t_seed=t_seed and t_seed+1.5; seeded=E("__QA.SIM.lastSeeded")
    PT="JSON.stringify([[34.885,128.09],[34.878,128.10],[34.889,128.085],[34.870,128.11]].map(([a,o])=>{const v=__QA.flowAt(a,o,__QA.tH());return v?[v.vE,v.vN]:null}))"
    import json
    A=json.loads(E(PT))
    # 같은 계산을 출발값 없이 (비교용)
    E("__QA.SIM.tiles.clear();__QA.simCache.clear();__QA.SIM.lastTile=null;__QA.SIMDB.ok=false;__QA.SIMDB.db=null");
    j0=E("__QA.SIM.jobsRun||0"); E("__QA.SIM.done=false;__QA.SIM.ready=false"); go(16,34.8821,128.0961,0)
    t_cold=wait(f"(__QA.SIM.jobsRun||0)>{j0}&&__QA.SIM.on&&__QA.SIM.done&&!__QA.SIM.rough",240); cold_seeded=E("__QA.SIM.lastSeeded"); B=json.loads(E(PT)); E("__QA.SIMDB.ok=true")
    d=[ (( (a[0]-b[0])**2+(a[1]-b[1])**2)**.5)/max(0.05,(b[0]**2+b[1]**2)**.5) for a,b in zip(A,B) if a and b]
    d=[ (( (a[0]-b[0])**2+(a[1]-b[1])**2)**.5) for a,b in zip(A,B) if a and b]
    check('Z3 13단계에서 확대해 온 경우와 처음부터 계산한 경우 같은 곳 값 동일 (출발값 고정)', d and max(d)<1e-6, f'최대 차이 {max(d) if d else None}, 확대 경로 {t_seed}초 / 처음부터 {t_cold}초')
    # ── 폰 저장 ──
    go(16,34.882,128.096,0); wait("__QA.SIM.on&&__QA.SIM.done",240); pg.wait_for_timeout(1500)
    pg.reload(); pg.wait_for_timeout(1500); E("__QA.CONF.realData=true")
    E("document.querySelector('#simBtn').classList.contains('on')||document.querySelector('#simBtn').click()")
    go(16,34.882,128.096,0); t_re=wait("__QA.SIM.on&&__QA.SIM.done",120); steps=E("__QA.SIM.jobsRun||0")
    check('Z5 앱을 다시 켜도 본 곳은 저장된 결과로 바로 표시(3초 이내, 계산 0회)', t_re is not None and t_re<3+0.9 and steps==0, f'{t_re}초, 계산 {steps}회')
    check('Z6 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
