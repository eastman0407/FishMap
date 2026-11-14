# 4단계 시험: 예보 점이 빈 곳을 항내 추정으로 채우고, 먼 곳은 '자료 부족'으로 구분 (build-22)
import sys, time
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
exec(src+'''
    def wait(js,limit):
        t=time.time()
        while time.time()-t<limit:
            if E(js): return round(time.time()-t,1)
            pg.wait_for_timeout(300)
        return None
    E("document.querySelector('#simBtn').click()"); go(13,34.882,128.096,500); wait("__QA.SIM.on&&__QA.SIM.done",180)
    # 섬 남쪽 바다의 예보 점을 반경 약 6km 지워 '예보 모델에 점이 없는 만' 상황을 만듦
    HOLE=(34.875,128.10)
    E(f"""(()=>{{const R=__QA.RD,keep=R.pts.filter(p=>Math.hypot(p.lat-{HOLE[0]},(p.lon-{HOLE[1]})*0.82)>0.055);__QA.setRealData({{times:R.times,points:keep}},null);__QA.simTimeChanged(true);}})()""")
    wait("__QA.SIM.on&&__QA.SIM.done",180)
    v=E(f"__QA.flowAt({HOLE[0]},{HOLE[1]},__QA.tH())"); b=E(f"__QA.baseAt({HOLE[0]},{HOLE[1]},__QA.tH())")
    check('F1 예보 점이 없는 곳(가운데)도 항내 추정으로 흐름을 채움', b is None and v is not None and v.get('est'), f'예보 {b} → 추정 {v and round((v["vE"]**2+v["vN"]**2)**.5,3)}kn')
    check('F2 그곳은 "자료 부족"으로 구분', v is not None and v.get('low') is True, v)
    w=E("__QA.flowAt(34.84,128.13,__QA.tH())")
    check('F3 예보 점 가까운 곳은 자료 부족 아님', w is not None and not w.get('low'), w)
    E(f"_map.fire('click',{{latlng:{{lat:{HOLE[0]},lng:{HOLE[1]}}}}})"); pg.wait_for_timeout(500)
    check('F4 정보카드에 "자료 부족" 표시', '자료 부족' in pg.inner_text('#iState'), pg.inner_text('#iState'))
    check('F5 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
