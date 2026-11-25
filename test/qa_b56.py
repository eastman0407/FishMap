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
        return [...document.querySelectorAll('#flow canvas')].some(c=>
            c.getContext('2d').getImageData(0,0,c.width,c.height).data.some((v,i)=>i%4===3&&v>0));
    }""")
    trails=E("""(()=>{
        const c=document.querySelector('#flow');
        const ink=()=>[...c.children].some(layer=>
            layer.getContext('2d').getImageData(0,0,layer.width,layer.height).data.some((v,i)=>i%4===3&&v>0));
        _map.fire('movestart'); _map.fire('zoomanim',{center:_map.getCenter(),zoom:15});
        const during=ink()&&c.style.transform.includes('scale(4)')&&c.style.opacity==='0';
        _map._z=15; _map.fire('moveend');
        const zoomIn=!ink()&&!c.style.transform&&!c.style.opacity;
        c.firstElementChild.getContext('2d').fillRect(100,100,10,10);
        _map.panBy(5,5);
        const pan=ink()&&c.style.opacity==='';
        _map.fire('movestart'); _map._z=13; _map.fire('moveend');
        const zoomOut=!ink()&&!c.style.transform&&!c.style.opacity;
        return [during,zoomIn,pan,zoomOut];
    })()""")
    check('H14 확대 중 페이드, 확대·축소 직후 잔상 제거, 같은 배율 이동 중 유지', all(trails), trails)
    expired=E("""(()=>{
        const {flowTrailContext,clearFlowTrails}=__QA;
        const layers=[...document.querySelectorAll('#flow canvas')];
        const hasInk=x=>layers.some(layer=>layer.getContext('2d').getImageData(x,10,1,1).data[3]>0);
        return [30,60,120].map(hz=>{
            clearFlowTrails();
            const old=flowTrailContext(1000);
            old.fillStyle='rgba(80,135,155,.06)'; old.fillRect(4,4,20,20);
            const drawn=hasInk(10);
            for(let i=1;i<=hz;i++){
                const current=flowTrailContext(1000+i*1000/hz);
                current.fillStyle='#4fbacd'; current.fillRect(45,4,20,20);
            }
            const steady=!hasInk(10)&&hasInk(60);
            flowTrailContext(10000);
            const paused=!hasInk(10)&&!hasInk(60);
            clearFlowTrails();
            return [drawn,steady,paused];
        });
    })()""")
    check('H16 30·60·120Hz에서 희미한 픽셀 만료와 새 흐름 유지, 화면 복귀 후 초기화',
          all(all(row) for row in expired), expired)
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
    check('H13 스크립트 오류 없음', not errs, errs[:2])
    print(f"결과: {sum(res)}/{len(res)}")
    br.close()
''')
