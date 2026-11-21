# H-11 시험 (build-50): 다시 켜도 항내 계산을 저장에서 꺼내 씀 — 94m 결과를 줄여 저장해 23m 열쇠가 바뀌던 문제
# H-11 시험: 낚시 기준 고정 색 + 확대 시 계산 줄이기(멈춘 뒤 시작·대략 표시·이어서 계산·폰 저장) (build-23)
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

    SPY="(()=>{const D=__QA.SIMDB;if(D.__spy)return;D.__spy=1;window.__put=[];window.__get=[];const p=D.put.bind(D),g=D.get.bind(D);D.put=(k,v)=>{__put.push(k);return p(k,v)};D.get=k=>g(k).then(r=>{__get.push([k,!!(r&&r.u)]);return r})})()"
    E("document.querySelector('#simBtn').click()"); E(SPY)
    go(16,34.882,128.096,0); wait("__QA.SIM.on&&__QA.SIM.done",240); pg.wait_for_timeout(1500)
    P1=E("__put"); G1=E("__get")
    pg.reload(); pg.wait_for_timeout(1500); E("__QA.CONF.realData=true"); E(SPY)
    E("document.querySelector('#simBtn').classList.contains('on')||document.querySelector('#simBtn').click()")
    go(16,34.882,128.096,0); t_re=wait("__QA.SIM.on&&__QA.SIM.done",120); steps=E("__QA.SIM.jobsRun||0")
    P2=E("__put"); G2=E("__get")
    import json
    n14a=len([k for k in P1 if k.startswith('14:')]); n16a=len([k for k in P1 if k.startswith('16:')])
    keyOK=all(any(g[0]==k and g[1] for g in G2) for k in P1)
    check('H1 계산이 끝나면 94m·23m 결과가 폰에 저장됨', n14a>=1 and n16a>=1, P1)
    check('H2 앱을 다시 켜면 저장된 94m·23m 결과를 모두 찾음 (열쇠 동일)', keyOK and len(G2)>=2, G2)
    check('H3 다시 켠 뒤 계산 0회·3초 이내 (H-11)', steps==0 and t_re is not None and t_re<3, f'{t_re}초, 계산 {steps}회')
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
