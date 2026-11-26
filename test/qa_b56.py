# build-61 (1묶음): H-15 흐름 방향 믿음 · H-12 테두리 값 고정 · H-14 지금 따라가기
#  지키는 시험(H-15 ⑥): 확대·축소 중 어떤 순간에도 '화면에 그리는 방향'이 끝 값과 90° 넘게 다르면 실패
import sys, time, json, math
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0]
exec(src+r'''
    PTS=[[34.885,128.09],[34.878,128.10],[34.889,128.085],[34.870,128.11],[34.875,128.10],[34.882,128.096]]
    PT="JSON.stringify(%s.map(([a,o])=>{__QA.simFramePrep(); const q=_map.latLngToContainerPoint([a,o]); const v=__QA.flowDraw(q.x,q.y,__QA.tH()); const f=__QA.flowAt(a,o,__QA.tH()); return v?[+v.vE.toFixed(4),+v.vN.toFixed(4),+v.c.toFixed(2),!!(f&&f.pend)]:null}))"%json.dumps(PTS)
    def done(): return E("__QA.SIM.on&&__QA.SIM.done")
    def run(act,limit=90):
        act(); t=time.time(); snaps=[]
        while time.time()-t<limit:
            snaps.append(json.loads(E(PT)))
            if done() and time.time()-t>2.5: break
            pg.wait_for_timeout(100)
        return snaps,json.loads(E(PT))
    E("const s=document.querySelector('#slider');s.value=620;s.dispatchEvent(new Event('input'))")
    go(13,34.882,128.096,0)
    s13,f13=run(lambda:E("document.querySelector('#simBtn').classList.contains('on')||document.querySelector('#simBtn').click()"))
    check('H1 계산 전 임시 흐름선을 표시하지 않음', all(v is None for v in s13[0]), s13[0])
    check('H2 완료한 값만 표시하며 기다리는 중의 방향이 최종값과 같음',
          all(f13) and all(v is None or v==f13[i] for row in s13 for i,v in enumerate(row)),f13)
    for z,lat,lon in [(15,34.882,128.096),(12,34.882,128.096),(13,34.896,128.112),(13,34.882,128.096)]:
        snaps,final=run(lambda:go(z,lat,lon,0),12)
        check(f'확대 {z}, 이동 {lat}/{lon}: 매 표본의 같은 지점 유속·유향 유지',
              final==f13 and all(row==f13 for row in snaps),final)
    no_roms=E("""(()=>{
        const keep=__QA.ROMS.mem; __QA.ROMS.mem=new Map();
        try{
            const p=_map.latLngToContainerPoint([34.882,128.096]);
            __QA.simFramePrep();
            const v=__QA.flowDraw(p.x,p.y,__QA.tH());
            return [__QA.baseAt(34.882,128.096,__QA.tH())===null, !!(v&&v.est), __QA.okSpot(p.x,p.y)];
        }finally{__QA.ROMS.mem=keep;}
    })()""")
    check('완료한 항내 추정만 있는 바다에도 흐름선 생성',no_roms==[True,True,True],no_roms)
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
    E("document.querySelector('#nowBtn').click()")
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
    # 확대·축소 중에는 선을 흐리게 하고, 끝나면 이전 배율의 픽셀을 제거한다.
    E("const s=document.querySelector('#slider'); s.value=__QA.tMin(); s.dispatchEvent(new Event('input'))")
    pg.wait_for_function("""() => {
        const c=document.querySelector('#flow'); if(!c||!c.width) return false;
        return c.getContext('2d').getImageData(0,0,c.width,c.height).data.some((v,i)=>i%4===3&&v>0);
    }""")
    trails=E("""(()=>{
        const c=document.querySelector('#flow'); const g=c.getContext('2d');
        const ink=()=>g.getImageData(0,0,c.width,c.height).data.some((v,i)=>i%4===3&&v>0);
        _map.fire('movestart'); _map.fire('zoomanim',{center:_map.getCenter(),zoom:15});
        const during=c.style.transform.includes('scale(4)');   // 확대 중 캔버스가 함께 확대 (단일 캔버스)
        _map._z=15; _map.fire('moveend');
        const zoomClear=!ink()&&!c.style.transform;            // 확대 확정 후 이전 배율 픽셀 폐기 (build-74)
        g.fillRect(100,100,10,10);
        _map.panBy(5,5);
        const pan=ink();                                       // 같은 배율 이동은 이어 그림
        return [during,zoomClear,pan];
    })()""")
    check('H14 확대 중 캔버스 확대, 확대 확정 후 이전 배율 잔상 폐기, 같은 배율 이동 유지 (build-65 단일 캔버스)', all(trails), trails)
    expired=E("""(()=>{
        const c=document.querySelector('#flow'); const g=c.getContext('2d');
        const run=hz=>{ g.save(); g.setTransform(1,0,0,1,0,0);
            g.globalCompositeOperation='source-over'; g.clearRect(0,0,c.width,c.height);
            g.fillStyle='#4fbacd'; g.fillRect(40,8,12,12);
            const a0=g.getImageData(45,13,1,1).data[3];
            for(let i=0;i<hz;i++){const dt=1/hz; g.globalCompositeOperation='destination-in'; g.fillStyle='rgba(0,0,0,'+Math.exp(-dt/0.16)+')'; g.fillRect(0,0,c.width,c.height); g.globalCompositeOperation='source-over';}
            const a1=g.getImageData(45,13,1,1).data[3]; g.restore(); return [a0,a1];
        };
        const r=[30,60,120].map(run);
        const bright=r.every(x=>x[0]>200);                      // 처음엔 선명
        const faded=r.every(x=>x[1]<20);                        // 1초 뒤 거의 사라짐(누적 안 됨)
        const consistent=Math.max(...r.map(x=>x[1]))-Math.min(...r.map(x=>x[1]))<8; // 주사율 달라도 감쇠 같음
        return [bright,faded,consistent];
    })()""")
    check('H16 흐름선 꼬리가 1초 뒤 사라지고(누적 없음) 30·60·120Hz에서 감쇠가 같음(주사율 무관)',
          all(expired), expired)
    E("__QA.select(34.882,128.096,'고정 유속 시험')")
    point="""()=>{
        const s=__QA.sel(), v=__QA.flowAt(s.lat,s.lng,__QA.tH());
        return v&&v.est&&!v.pend?[v.vE,v.vN]:null;
    }"""
    pg.wait_for_function(point,timeout=90000)
    v13=E('('+point+')()')
    keys=E("__QA.SIM.sz")
    data=[]
    for zoom in (15,13):
        go(zoom,34.882,128.096,0)
        pg.wait_for_function(f"__QA.SIM.sz=={keys}",timeout=15000)
        pg.wait_for_function(point,timeout=90000)
        data.append([E('('+point+')()'),E("__QA.SIM.sz")])
    check('H15 같은 지점·시각에서 13→15→13단계 유속·방향과 정밀 구역 고정',
          bool(keys) and all(ks==keys and math.dist(v,v13)<1e-6 for v,ks in data), [v13,data])
    # H17·H18 (검토 3): 흐름선이 실제로 보이고, 프레임마다 입자가 움직여 유속을 나타내는지
    go(13,34.9,128.09,0)
    pg.wait_for_timeout(2200)
    PAINT="""(()=>{const c=document.querySelector('#flow');const W=__QA.W(),H=__QA.H();
        const off=document.createElement('canvas');off.width=W;off.height=H;const o=off.getContext('2d');o.drawImage(c,0,0,W,H);
        const d=o.getImageData(0,0,W,H).data;let p=0;for(let i=3;i<d.length;i+=4)if(d[i]>8)p++;return p/(W*H);})()"""
    samples=[]
    for _ in range(6):
        samples.append(E(PAINT)); pg.wait_for_timeout(120)
    painted=max(samples)
    check('H17 흐름선이 화면에 보임 (칠해진 픽셀 ≥ 0.3%)', painted>=0.003, f'{round(painted*100,2)}%')
    p0=E("__QA.parts().slice(0,40).map(p=>[Math.round(p.x),Math.round(p.y)])")
    pg.wait_for_timeout(350)
    p1=E("__QA.parts().slice(0,40).map(p=>[Math.round(p.x),Math.round(p.y)])")
    moved=sum(1 for a,b in zip(p0,p1) if a!=b)
    check('H18 입자가 프레임마다 이동 (움직임으로 유속 표현, REQ-37·U-64)', moved>=20, f'{moved}/40 이동')
    check('H13 스크립트 오류 없음', not errs, errs[:2])
    print(f"결과: {sum(res)}/{len(res)}")
    br.close()
''')
