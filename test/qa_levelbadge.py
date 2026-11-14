# 계산 단계 표시 시험 (build-25)
import sys, time, re
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
exec(src+'''
    def wait(js,limit):
        t=time.time()
        while time.time()-t<limit:
            if E(js): return True
            pg.wait_for_timeout(300)
    B="document.querySelector('.samplebadge').textContent"
    E("document.querySelector('#simBtn').click()")
    go(13,34.882,128.096,0); wait("__QA.SIM.on&&__QA.SIM.done",240); b13=E(B)
    m=re.search(r'칸 (\\d+)m', b13 or '')
    check('L1 13단계: 배지에 "보통(칸 약 94m·구역 약 16km)"', '보통' in b13 and m and 85<=int(m.group(1))<=100 and '구역 1' in b13, b13)
    go(16,34.882,128.096,0); pg.wait_for_timeout(300); b16now=E(B); wait("__QA.SIM.sz===16&&__QA.SIM.on&&__QA.SIM.done",240); b16=E(B)
    m=re.search(r'칸 (\\d+)m', b16 or '')
    check('L2 16단계: 배지에 "정밀(칸 약 23m·구역 약 4km)"', '정밀' in b16 and m and 20<=int(m.group(1))<=26 and ('구역 3.' in b16 or '구역 4' in b16) and '정밀' in b16now, [b16now,b16])
    go(11.5,34.882,128.096,0); wait("__QA.SIM.sz===12",240); b11=E(B)
    check('L3 11~13단계: "넓게"', '넓게' in b11, b11)
    E("document.querySelector('#simBtn').click()"); go(13,34.882,128.096,2500)
    check('L4 OFF면 단계 표시 없음', '칸 ' not in E(B), E(B))
    d=pg.evaluate("__QA.runDiag()"); check('L5 진단에도 단계 표시', '단계' in d)
    check('L6 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
