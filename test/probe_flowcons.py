import sys, time, json, math
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
exec(src+r'''
    PTS=[[34.885,128.09],[34.878,128.10],[34.889,128.085],[34.870,128.11],[34.875,128.10],[34.882,128.096]]
    PT="JSON.stringify(%s.map(([a,o])=>{const v=__QA.flowAt(a,o,__QA.tH());return v?[+v.vE.toFixed(4),+v.vN.toFixed(4),!!v.est,!!v.pend]:null}))"%json.dumps(PTS)
    def ang(a,b):
        if not a or not b: return None
        if math.hypot(a[0],a[1])<0.03 or math.hypot(b[0],b[1])<0.03: return None  # 거의 정조는 방향 의미 없음
        d=math.degrees(math.atan2(a[1],a[0])-math.atan2(b[1],b[0])); d=(d+180)%360-180; return abs(d)
    def done(): return E("__QA.SIM.on&&__QA.SIM.done&&!__QA.SIM.rough")
    def run(label,act,lim=200):
        act(); t=time.time(); snaps=[]
        while time.time()-t<lim:
            snaps.append(json.loads(E(PT)))
            if done() and time.time()-t>1.5: break
            pg.wait_for_timeout(250)
        fin=json.loads(E(PT)); worst=[]
        for s in snaps:
            for i in range(len(PTS)):
                a=ang(s[i],fin[i]); 
                if a is not None: worst.append(a)
        mx=max(worst) if worst else 0
        print(f"[{label}] {round(time.time()-t,1)}초 · 중간 화면 수 {len(snaps)} · 끝 값과 가장 큰 방향 차이 {mx:.0f}° · 90° 넘은 순간 {sum(1 for w in worst if w>90)}회 · 45° 넘은 {sum(1 for w in worst if w>45)}회")
        return fin
    E("document.querySelector('#simBtn').classList.contains('on')||document.querySelector('#simBtn').click()")
    go(12,34.882,128.096,3000)
    F={}
    F[13]=run('13단계로 확대',lambda:go(13,34.882,128.096,0))
    F[14]=run('14단계로 확대',lambda:go(14,34.882,128.096,0))
    F[15]=run('15단계로 확대',lambda:go(15,34.882,128.096,0))
    F[16]=run('16단계로 확대',lambda:go(16,34.882,128.096,0))
    F['16e']=run('16단계 옆으로 이동(동쪽 700m)',lambda:go(16,34.882,128.104,0))
    F['16b']=run('16단계 제자리로 돌아옴',lambda:go(16,34.882,128.096,0))
    F['14b']=run('14단계로 축소',lambda:go(14,34.882,128.096,0))
    F['13b']=run('13단계로 축소',lambda:go(13,34.882,128.096,0))
    print('\n같은 시각·같은 자리, 단계끼리 끝 값 방향 차이(°):')
    keys=[13,14,15,16,'16b','14b','13b']
    for i,p in enumerate(PTS):
        row=[]
        for k in keys:
            a=ang(F[k][i],F[16][i]); row.append('-' if a is None else f"{a:.0f}")
        sp=[round(math.hypot(F[k][i][0],F[k][i][1]),2) if F[k][i] else None for k in keys]
        print(p,'16단계와 차이',dict(zip(map(str,keys),row)),'속도',sp)
    br.close()
''')
