# 둥지 계산 시험 (build-34, REQ-55): 정밀(16) 구역은 감싸는 보통(14) 구역을 먼저 계산하고 그 결과를 테두리 값으로 씀
import sys, time, math
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
exec(src+'''
    def until(js,limit=120):
        t=time.time()
        while time.time()-t<limit:
            if E(js): return time.time()-t
            pg.wait_for_timeout(300)
        return None
    go(16,34.898,128.096,500)
    t1=until("__QA.SIM.done",180)
    par=E("__QA.SIM.par"); pd=E("__QA.SIM.par.map(k=>{const T=__QA.SIM.tiles.get(k);return T&&[T.lv,T.state,!!(T.cur&&T.cur.done)]})")
    check('S1 정밀 화면이면 감싸는 보통(14) 구역도 계산', par and all(x and x[0]==14 for x in pd) and any(x[2] for x in pd), [par,pd,t1])
    r=E("""(()=>{const k=__QA.SIM.view.find(k=>{const T=__QA.SIM.tiles.get(k);return T&&T.cur&&T.cur.done;});const T=__QA.SIM.tiles.get(k);
      const b=__QA.simBC(T,__QA.tH()); let n=0,same=0;
      for(let q=0;q<T.bcIdx.length;q+=7){const i=T.bcIdx[q],X=i%T.gx,Y=(i/T.gx)|0,ll=_map.unproject([T.ox+(X+.5)*12,T.oy+(Y+.5)*12],T.lv),v=__QA.nestAt(ll.lat,ll.lng);
        if(!v)continue;n++; if(Math.abs(b.bcU[q]/b.scale-v.vE)<1e-3&&Math.abs(-b.bcV[q]/b.scale-v.vN)<1e-3)same++;}
      return [n,same];})()""")
    check('S2 정밀 구역 테두리 = 보통 구역 계산 결과', r[0]>20 and r[1]==r[0], r)
    D3="""(()=>{const out=[];const S=_map.getSize();for(let yy=1;yy<6;yy++)for(let xx=1;xx<4;xx++){const x=xx*S.x/4,y=yy*S.y/6;
      const ll=_map.containerPointToLatLng([x,y]),a=__QA.flowAt(ll.lat,ll.lng,__QA.tH()),b=__QA.nestAt(ll.lat,ll.lng);
      if(a&&b&&Math.hypot(b.vE,b.vN)>0.05){let g=Math.abs(Math.atan2(a.vE,a.vN)-Math.atan2(b.vE,b.vN))*180/Math.PI;if(g>180)g=360-g;out.push(g);}}return out;})()"""
    d=E(D3)
    if not d:
        go(16,34.884,128.095,500); until("__QA.SIM.done",180)
        d=E(D3)
    med=sorted(d)[len(d)//2] if d else 999
    check('S3 정밀 결과와 보통 결과 방향이 서로 이어짐 (가운데값 30° 이내)', d and med<30, f'{len(d)}곳, 가운데값 {med:.0f}°')
    E("_map.panBy(30,20)"); pg.wait_for_timeout(500); go(16,34.899,128.097,500); t2=until("__QA.SIM.done",60)
    check('S4 조금 움직여 다시 와도 빨리 표시 (5초 이내)', t2 is not None and t2<5, t2)
    go(13,34.898,128.096,2500)
    check('S5 보통 단계(13)에서는 둥지 없음', E("__QA.SIM.par.length")==0, E("__QA.SIM.par"))
    check('S6 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
