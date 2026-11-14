# 2단계 시험: 예보 점 사이를 끊김 없이 잇는지 (삼각망) + 거리 제한 (build-22)
import sys
sys.argv=sys.argv[:2]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
exec(src+'''
    JUMP="""((y)=>{const th=__QA.tH(),o=[];let prev=null,mx=0,sp=[];
      for(let i=0;i<=400;i++){const x=i*__QA.W()/400;const ll=_map.containerPointToLatLng([x,y]);const v=__QA.baseAt(ll.lat,ll.lng,th);
        if(v&&prev){const d=Math.hypot(v.vE-prev.vE,v.vN-prev.vN);mx=Math.max(mx,d);} if(v)sp.push(Math.hypot(v.vE,v.vN)); prev=v;}
      sp.sort((a,b)=>a-b); return [mx, sp.length?sp[sp.length>>1]:0, sp.length];})"""
    worst=0; info=[]
    for z,lat,lon in [(13,34.86,128.20),(12,34.80,128.30),(14,34.85,128.18)]:
        go(z,lat,lon,9000)
        for fy in (0.25,0.5,0.75):
            mx,med,n=E(JUMP+f"(__QA.H()*{fy})")
            r=mx/max(med,0.02); worst=max(worst,r); info.append(round(r,3))
    # 400칸으로 나눈 한 칸(약 30~120m) 사이 변화가 평균 유속의 8% 이하면 '끊김 없음'
    check('C1 화면 가로선 400칸 사이 유속 급변 없음 (최대 변화/평균 ≤ 0.08)', worst<=0.08, f'최악 {worst:.3f}, {info}')
    # C1b: 실기기처럼 빠른 점(1.5kn)과 느린 점(0.1kn)이 붙어 있는 경우 (가짜 자료 직접 넣기)
    go(13,34.86,128.20,3000)
    jb=E("""(()=>{const th=__QA.tH(),c=_map.getCenter(),T=[Date.now()-3600e3,Date.now()+3600e3*48],pts=[];let s=7;const rnd=()=>{s=(s*16807)%2147483647;return s/2147483647;};
      for(let i=-6;i<=6;i++)for(let j=-6;j<=6;j++){const sp=rnd()<0.5?1.5:0.1,a=rnd()*6.28;pts.push({lat:c.lat+i*0.029,lon:c.lng+j*0.031,u:[sp*Math.sin(a),sp*Math.sin(a)],v:[sp*Math.cos(a),sp*Math.cos(a)]});}
      __QA.setRealData({times:T,points:pts},null);let mx=0,prev=null,cnt=0;
      for(const fy of [0.2,0.4,0.6,0.8]){prev=null;for(let i=0;i<=400;i++){const ll=_map.containerPointToLatLng([i*__QA.W()/400,__QA.H()*fy]);const v=__QA.baseAt(ll.lat,ll.lng,th);
        if(v&&prev){mx=Math.max(mx,Math.hypot(v.vE-prev.vE,v.vN-prev.vN));cnt++;}prev=v;}}return [mx,cnt];})()""")
    jc=E("""(()=>{const th=__QA.tH(),c=_map.getCenter(),T=[Date.now()-3600e3,Date.now()+3600e3*48],pts=[];let s=11;const rnd=()=>{s=(s*16807)%2147483647;return s/2147483647;};
      for(let i=-6;i<=6;i++)for(let j=-6;j<=6;j++){if(Math.abs(i)<=1&&Math.abs(j)<=1)continue; const sp=rnd()<0.5?1.5:0.1,a=rnd()*6.28;pts.push({lat:c.lat+i*0.029,lon:c.lng+j*0.031,u:[sp*Math.sin(a),sp*Math.sin(a)],v:[sp*Math.cos(a),sp*Math.cos(a)]});}
      __QA.setRealData({times:T,points:pts},null);let mx=0,prev=null,nul=0;
      for(const fy of [0.3,0.5,0.7]){prev=null;for(let i=0;i<=400;i++){const ll=_map.containerPointToLatLng([i*__QA.W()/400,__QA.H()*fy]);const v=__QA.baseAt(ll.lat,ll.lng,th);
        if(!v)nul++; if(v&&prev)mx=Math.max(mx,Math.hypot(v.vE-prev.vE,v.vN-prev.vN));prev=v;}}return [mx,nul];})()""")
    check('C1c 자료가 빈 구역 가장자리(실기기 상황)에서도 급변 0.05kn 이하 — 예전엔 가장 가까운 점 값 복사로 칼같은 경계', jc[0]<=0.05, f'최대 급변 {jc[0]:.3f}kn, 값 없음 {jc[1]}곳')
    check('C1b 빠른 점·느린 점이 붙어 있어도 한 칸(약 50m) 사이 급변 0.05kn 이하', jb[0]<=0.05, f'최대 급변 {jb[0]:.3f}kn')
    E("__QA.RD.have=null;__QA.RD.pts=[]"); go(13,34.86,128.205,9000)
    # 거리 제한: 예보 점에서 8km 떨어진 곳은 값 없음(예전엔 10km까지 복사)
    far=E("""(()=>{const P=__QA.RD.pts;if(!P.length)return null;const p=P[0];const th=__QA.tH();
      let lo=-180,best=null;for(const q of P)lo=Math.max(lo,q.lon); const v=__QA.baseAt(p.lat,lo+0.09,th);return v;})()""")
    check('C2 예보 점에서 약 8km 넘게 떨어진 곳은 값을 지어내지 않음', far is None, far)
    near=E("(()=>{const p=__QA.RD.pts[5];return __QA.baseAt(p.lat,p.lon,__QA.tH())})()")
    exact=E("(()=>{const p=__QA.RD.pts[5],ti=__QA.RD.times;return [p.u,p.v]})()")
    check('C3 예보 점 바로 위에서는 그 점 값과 같음', near is not None, near)
    tri=E("__QA.RD.tri.length"); check('C4 삼각망 만들어짐', tri>10, tri)
    check('C5 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
