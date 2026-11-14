# 항내 추정 ON/OFF·과속·받기 실패 시험 (build-20). 실제 모양 모의 서버(9098) + 합성 OSM 타일
import sys, time, statistics as S
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0]
src=src.replace("BRIDGE=r\"\"\"window.AndroidBridge={","BRIDGE=r\"\"\"window.__failN=0;window.__failBox=null;window.AndroidBridge={")
src=src.replace("  if(!url.includes('/roms/'))return reply(200,","  if(url.includes('/roms/')&&window.__failBox&&(()=>{const q=new URL(url).searchParams;return +q.get('ymin')>=window.__failBox[0]&&+q.get('ymax')<=window.__failBox[1]&&+q.get('xmin')>=window.__failBox[2]&&+q.get('xmax')<=window.__failBox[3]})())return reply(-1,'timeout');\n  if(!url.includes('/roms/'))return reply(200,")
exec(src+'''
    def wait(js,limit):
        t=time.time()
        while time.time()-t<limit:
            if E(js): return round(time.time()-t,1)
            pg.wait_for_timeout(200)
        return None
    RATIO="""(()=>{const th=__QA.tH(),o=[];for(let yy=1;yy<20;yy++)for(let xx=1;xx<10;xx++){const x=xx*__QA.W()/10,y=yy*__QA.H()/20;
      if(!__QA.isWater(x,y))continue;const ll=_map.containerPointToLatLng([x,y]);const a=__QA.flowAt(ll.lat,ll.lng,th),b=__QA.baseAt(ll.lat,ll.lng,th);
      if(a&&b&&a.est&&Math.hypot(b.vE,b.vN)>0.05)o.push(Math.hypot(a.vE,a.vN)/Math.hypot(b.vE,b.vN));}return o;})()"""
    # S1 OFF 13단계: 계산 안 함 (지금과 같음)
    go(13,34.882,128.096,6000)
    check('S1 OFF·13단계: 항내 추정 꺼짐(기존 동작)', not E("__QA.SIM.on"), E("document.querySelector('.samplebadge').textContent"))
    # S2 ON 13단계: 화면 전체 계산
    E("document.querySelector('#simBtn').click()"); t=wait("__QA.SIM.on&&__QA.SIM.done",120)
    cov=E("""(()=>{let w=0,h=0;for(let yy=0;yy<10;yy++)for(let xx=0;xx<6;xx++){const x=(xx+.5)*__QA.W()/6,y=(yy+.5)*__QA.H()/10;if(!__QA.isWater(x,y))continue;w++;
      const ll=_map.containerPointToLatLng([x,y]);const v=__QA.flowAt(ll.lat,ll.lng,__QA.tH());if(v&&v.est)h++;}return [h,w];})()""")
    check('S2 ON·13단계: 계산 완료 + 화면 바다 전체가 추정값', t is not None and cov[1] and cov[0]/cov[1]>=0.95, f'{t}초, 단계 {E("__QA.SIM.sz")}, {cov[0]}/{cov[1]}곳')
    check('S3 ON 상태 저장(다음 실행 유지)', E("AndroidBridge.getPref('simMode')")=='1')
    r=sorted(E(RATIO)); check('S4 ON·13단계 추정/예보 속도비 0.75~1.33 (과속 수정)', r and 0.75<=S.median(r)<=1.33, f'중앙값 {S.median(r):.2f}, 10~90% {r[len(r)//10]:.2f}~{r[-len(r)//10]:.2f}, 표본 {len(r)}' if r else '표본 없음')
    # S5 16단계 섬 옆 속도비 (예전 1.69배)
    go(16,34.882,128.096,500); wait("__QA.SIM.on&&__QA.SIM.done",120)
    FAR="""(()=>{const T=[...__QA.SIM.tiles.values()].find(t=>__QA.SIM.view.includes(t.key)&&t.cur&&t.solid);const s={gx:T.gx,gy:T.gy,solid:T.solid,u:T.cur.u,v:T.cur.v,scale:T.cur.scale,ox:T.ox,oy:T.oy,sz:T.lv},gx=s.gx,gy=s.gy,N=gx*gy,d=new Int32Array(N).fill(1e9),q=[];
      for(let i=0;i<N;i++)if(s.solid[i]){d[i]=0;q.push(i);}
      for(let h=0;h<q.length;h++){const c=q[h],X=c%gx,Y=(c/gx)|0;for(const[dx,dy] of [[1,0],[-1,0],[0,1],[0,-1]]){const x=X+dx,y=Y+dy;if(x<0||y<0||x>=gx||y>=gy)continue;const j=y*gx+x;if(d[j]>d[c]+1){d[j]=d[c]+1;q.push(j);}}}
      const o=[];for(let Y=15;Y<gy-15;Y+=3)for(let X=15;X<gx-15;X+=3){const i=Y*gx+X;if(d[i]<45)continue;
        const ll=_map.unproject([s.ox+(X+0.5)*12,s.oy+(Y+0.5)*12],s.sz),b=__QA.baseAt(ll.lat,ll.lng,__QA.tH());if(!b)continue;const bs=Math.hypot(b.vE,b.vN);if(bs<0.05)continue;
        o.push(Math.hypot(s.u[i],s.v[i])/s.scale/bs);}return o;})()"""
    r=sorted(E(FAR)); check('S5 16단계 섬에서 1km 이상 떨어진 바다 속도비 0.75~1.33 (수정 전 1.12)', r and 0.75<=S.median(r)<=1.33, f'중앙값 {S.median(r):.2f}, 10~90% {r[len(r)//10]:.2f}~{r[-len(r)//10]:.2f}' if r else '표본 없음')
    # S6 구역 가장자리·겹침에서 끊김 없음: 화면을 가로지르는 선 3개에서 이웃 칸 사이 급변
    go(13,34.882,128.096,500); wait("__QA.SIM.on&&__QA.SIM.done",180)
    jump=E("""(()=>{const th=__QA.tH();let mx=0,med=[];for(const fy of [0.3,0.5,0.7]){let prev=null;for(let i=0;i<=400;i++){const ll=_map.containerPointToLatLng([i*__QA.W()/400,__QA.H()*fy]);
      const v=__QA.flowAt(ll.lat,ll.lng,th);if(v&&prev)mx=Math.max(mx,Math.hypot(v.vE-prev.vE,v.vN-prev.vN));if(v)med.push(Math.hypot(v.vE,v.vN));prev=v;}}med.sort((a,b)=>a-b);return [mx,med[med.length>>1]];})()""")
    check('S6 구역 경계·겹침에서 끊김 없음 (이웃 칸 급변 ≤ 평균의 35%)', jump[0]<=0.35*max(jump[1],0.05), f'최대 급변 {jump[0]:.3f}kn, 평균 {jump[1]:.3f}kn, 구역 {E("__QA.SIM.view.length")}개')
    # S6b 옮겨도·같은 범위에서 확대해도 같은 곳 결과가 같음 (고정 구역)
    PT="JSON.stringify([[34.885,128.09],[34.878,128.10],[34.889,128.085]].map(([a,o])=>{const v=__QA.flowAt(a,o,__QA.tH());return v?[+v.vE.toFixed(5),+v.vN.toFixed(5)]:null}))"
    a0=E(PT); E("_map.panBy(120,-90)"); pg.wait_for_timeout(800); wait("__QA.SIM.on&&__QA.SIM.done",180); a1=E(PT)
    go(14,34.882,128.096,500); wait("__QA.SIM.on&&__QA.SIM.done",180); a2=E(PT)
    check('S6b 옮기거나 13→14단계로 확대해도 같은 곳 값 동일', a0==a1==a2 and 'null' not in a0, f'{a0} | {a1} | {a2}')
    # S7 OFF 되돌리기
    E("document.querySelector('#simBtn').click()"); go(13,34.882,128.096,3000)
    check('S7 OFF로 되돌리면 13단계 계산 꺼짐', not E("__QA.SIM.on"))
    # S8~S10 받기 실패: 특정 칸 계속 실패 → 표시 → 복구 후 다시 받기
    E("__QA.ROMS.mem.clear()"); E("window.__failBox=[34.70,34.80,128.20,128.30]")
    go(12,34.75,128.25,15000)
    f=E("__QA.RD.failed.length"); b=E("document.querySelector('.samplebadge').textContent")
    check('S8 실패 칸을 기록하고 배지에 표시', f>0 and '못 받음' in b, f'{f}칸, 배지="{b}"')
    check('S9 실패 칸은 받음 목록에서 빠짐', E("__QA.RD.failed.every(k=>!__QA.RD.have.has(k))"))
    E("window.__failBox=null"); E("_map.panBy(20,10)"); pg.wait_for_timeout(9000)
    check('S10 인터넷 복구 후 조금 움직이면 다시 받아 채움', E("__QA.RD.failed.length")==0, E("document.querySelector('.samplebadge').textContent"))
    check('S11 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
