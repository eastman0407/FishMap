# build-49 시험: U-1 바로 앞바다, U-3(H-10) 조석 시험 6가지, U-10 지점 상태창·시트, U-7 그래프, U-11 추천 정리, U-2 입질 위치, U-4 M2, U-5, U-8, U-12 움직임
# 바탕은 qa_b48 (조석·바람·주소 가짜 응답) + TideBED 가짜 응답(문서 예시 좌표+min=60만 00, 나머지 10)
import sys, time, math
sys.argv=sys.argv[:1]
_c=open('test/qa_b48.py').read(); exec(_c.split("exec(src+'''")[0])
src=src+_c.split("exec(src+'''")[1].split("    go(13,34.92,128.07,0); pg.wait_for_timeout(800)\n    btn=")[0]
src=src.replace("""  if(url.includes('tideFcstHghLw')){""","""  if(url.includes('/tidebed/')){window.__tbCalls=(window.__tbCalls||[]); window.__tbCalls.push(url); const q=new URL(url).searchParams;
    if(q.get('min')==='60'&&q.get('lat')==='33.96194'){const it=[];for(let k=0;k<5;k++)it.push({obsvtrNm:'모슬포',lat:'33.2',lot:'126.2',slctdDt:'2026-11-21 0'+k+':00',slctdHgt:String(100+k)});
      return reply(200,JSON.stringify({response:{header:{resultCode:'00'},body:{items:{item:it}}}}));}
    return reply(200,JSON.stringify({response:{header:{resultCode:'10',resultMsg:'INVALID_REQUEST_PARAMETER_ERROR'}}}));}
  if(url.includes('tideFcstHghLw')){""",1)
exec(src+r'''
    def wait(js,limit):
        t=time.time()
        while time.time()-t<limit:
            if E(js): return round(time.time()-t,1)
            pg.wait_for_timeout(200)
        return None
    def rect(q): return E(f"(()=>{{const e=document.querySelector('{q}'); if(!e)return null; const r=e.getBoundingClientRect(); return [r.left,r.top,r.right,r.bottom,getComputedStyle(e).display,getComputedStyle(e).visibility,+getComputedStyle(e).opacity]}})()")
    def shown(q): r=rect(q); return bool(r and r[4]!='none' and r[5]!='hidden' and r[2]-r[0]>0)
    def tap(x,y):
        E(f"(()=>{{const m=document.querySelector('#map').getBoundingClientRect(); _map.fire('click',{{latlng:_map.containerPointToLatLng([{x}-m.left,{y}-m.top])}});}})()"); pg.wait_for_timeout(400)
    W=411
    # ── U-10 상태창 ──
    go(13,34.92,128.07,0); pg.wait_for_timeout(1500)
    E("document.querySelector('#nowSeg button[data-v=now]').click()"); pg.wait_for_timeout(300)
    tap(200,470)
    fc=rect('#fCard'); inf=shown('#info'); pin=E("(()=>{const p=__QA.map.latLngToContainerPoint([__QA.sel().lat,__QA.sel().lng]);const m=document.querySelector('#map').getBoundingClientRect();return [p.x+m.left,p.y+m.top]})()")
    check('C1 바다를 찍으면 시트 대신 상태창(F28)이 뜸', fc and fc[4]=='block' and not inf, [fc,inf])
    tl=E("(()=>{const t=document.querySelector('#fCard .tail').getBoundingClientRect();return [t.left+t.width/2,t.top+t.height/2]})()")
    check('C2 상태창이 찍은 자리를 가리지 않고(위쪽), 꼬리가 자리를 가리킴', fc and not (fc[0]<=pin[0]<=fc[2] and fc[1]<=pin[1]<=fc[3]) and abs(tl[0]-pin[0])<10 and abs(tl[1]-pin[1])<22, [fc,pin,tl])
    check('C3 상태창 화면 안 (좌우 8px 이상 여유)', fc[0]>=7 and fc[2]<=W-7, fc)
    bg=E("getComputedStyle(document.querySelector('#fCard')).backgroundColor")
    check('C4 반투명 85%', '0.85' in bg, bg)
    txt=E("document.querySelector('#fCard').innerText")
    check('C5 유속·방향·상태·다음 정조·물높이·[📈 그래프]·☆·✕', all(k in txt for k in ['유속','방향','상태','다음 정조','🌊','📈 그래프','⭐ 주변 추천']) and E("!!document.querySelector('#fcStar')&&!!document.querySelector('#fcClose')"), txt.replace('\n',' | '))
    # 지도 움직이면 따라감
    # (build-50) 상태창이 오른쪽 버튼 줄(.side)과 겹치면 아래로 비켜가므로, 위에 뜨는 모양에서 비교하려고 먼저 지도를 아래로 밀어 둠
    E("_map.panBy(0,-150)"); pg.wait_for_timeout(300); fc=rect('#fCard')
    E("_map.panBy(30,-40)"); pg.wait_for_timeout(300); fc2=rect('#fCard')
    check('C6 지도를 움직이면 상태창이 자리를 따라감', fc2 and abs((fc2[0]-fc[0])+30)<=2 and abs((fc2[1]-fc[1])-40)<=2, [fc[:2],fc2[:2]])
    E("_map.panBy(-30,40)"); pg.wait_for_timeout(300)
    # 위쪽 자리: 아래로
    tap(200,175); fc3=rect('#fCard'); p3=E("(()=>{const p=__QA.map.latLngToContainerPoint([__QA.sel().lat,__QA.sel().lng]);const m=document.querySelector('#map').getBoundingClientRect();return [p.x+m.left,p.y+m.top]})()")
    nc=rect('#nowCard')
    check('C7 화면 위쪽 자리는 상태창이 아래로 (지금 카드에 안 가려짐)', fc3 and fc3[1]>p3[1] and E("document.querySelector('#fCard').classList.contains('below')"), [fc3,p3,nc])
    tap(200,470)
    # 그래프 → 시트
    E("document.querySelector('#fcGraph').click()"); pg.wait_for_timeout(500)
    check('C8 [📈 그래프] → 상태창 닫히고 시트(그래프) 열림', shown('#info') and not shown('#fCard') and E("__QA.PV.mode")=='sheet')
    ih=rect('#info');
    check('C9 시트 높이 화면 절반쯤 (40~62%)', ih and 0.38<=(ih[3]-ih[1])/860<=0.62, round((ih[3]-ih[1])/860,2))
    lg=rect('.legend'); bf=rect('#biteFab')
    check('C10 시트 펼친 동안 범례·입질 FAB 숨김', lg[6]==0 and bf[6]==0, [lg[6],bf[6]])
    st=E("document.querySelector('#info').innerText")
    check('C11 시트: ☆ 저장·🔔·🎣 입질! + 요약 줄 + 그래프 + 자리 정보 2×2(이 자리 바람·위성 수온·조류 지점·달)', all(k in st for k in ['저장','🔔','🎣 입질!','이 자리 바람','위성 수온','조류 지점','달']) and E("document.querySelectorAll('#iMore>div').length")==4 and E("document.querySelector('#iSum').textContent.length")>5, st.replace('\n',' | ')[:300])
    wcell=E("document.querySelector('#iMore>div').textContent")
    check('C12 이 자리 바람 칸에 세기 숫자(m/s) 함께, 밀림·하늘 문장 없음', 'm/s' in wcell and '밀려요' not in st and E("document.querySelector('#iWind').textContent")=='', wcell)
    pg.screenshot(path='/tmp/b49_sheet.png')
    # 시트 아래로 끌기 → 상태창
    g=E("(()=>{const r=document.querySelector('#infoGrip').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
    pg.mouse.move(g[0],g[1]); pg.mouse.down();
    for k in range(1,9): pg.mouse.move(g[0],g[1]+k*30); pg.wait_for_timeout(16)
    pg.mouse.up(); pg.wait_for_timeout(600)
    check('C13 시트를 아래로 끌면 시트가 내려가고 상태창이 다시 뜸', shown('#fCard') and not shown('#info') and E("!!__QA.sel()"))
    E("document.querySelector('#fcGraph').click()"); pg.wait_for_timeout(400)
    E("document.querySelector('#infoDown').click()"); pg.wait_for_timeout(600)
    check('C14 시트 ▾ 버튼 → 상태창', shown('#fCard') and not shown('#info'))
    E("document.querySelector('#fcGraph').click()"); pg.wait_for_timeout(400)
    b1=E("window.__onBack()"); pg.wait_for_timeout(500); m1=E("__QA.PV.mode")
    b2=E("window.__onBack()"); pg.wait_for_timeout(200); m2=E("__QA.PV.mode")
    check('C15 뒤로가기: 시트 → 상태창 → 닫힘', b1 and m1=='card' and b2 and m2=='none' and not E("!!__QA.sel()"), [b1,m1,b2,m2])
    tap(200,470); E("document.querySelector('#fcClose').click()"); pg.wait_for_timeout(200)
    check('C16 ✕ → 둘 다 닫힘', not shown('#fCard') and not shown('#info') and not E("!!__QA.sel()"))
    tap(200,470); pg.screenshot(path='/tmp/b49_card.png')
    # 상태창 ☆ (저장 안 된 곳 → 시트에서 이름 칸)
    E("document.querySelector('#fcStar').click()"); pg.wait_for_timeout(300)
    check('C17 상태창 ☆ → 시트 열고 이름 칸', shown('#info') and E("getComputedStyle(document.querySelector('#namebox')).display")=='flex')
    E("window.__onBack()"); E("window.__onBack()"); pg.wait_for_timeout(300)
    # 누르는 범위
    tap(200,470)
    hits=E("""(()=>{const o=[];for(const q of ['#fcStar','#fcClose','#fcGraph','#fcNearRec']){const e=document.querySelector(q),r=e.getBoundingClientRect(),a=getComputedStyle(e,'::after');
      const w=Math.max(r.width,parseFloat(a.width)||0),h=Math.max(r.height,parseFloat(a.height)||0); const top=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2); o.push([q,Math.round(w),Math.round(h),top===e||e.contains(top)]);}return o;})()""")
    check('C18 상태창 버튼 누르는 범위 40+ · 가운데 누르면 자기 자신', all(h[1]>=40 and h[2]>=40 and h[3] for h in hits), hits)
    E("document.querySelector('#fcClose').click()")
    # ── U-1 바로 앞바다 ──
    go(14,34.882,128.096,6000)
    E("document.querySelector('#simBtn').click()"); t=wait("__QA.SIM.on&&__QA.SIM.done",150)
    pt=E("""(()=>{const th=__QA.tH(); for(let y=120;y<__QA.H()-60;y+=3)for(let x=20;x<__QA.W()-20;x+=3){if(__QA.isWater(x,y))continue; let near=false; for(const [dx,dy] of [[8,0],[-8,0],[0,8],[0,-8]])if(__QA.isWater(x+dx,y+dy))near=true;
      if(!near)continue; const ll=_map.containerPointToLatLng([x,y]); if(__QA.flowAt(ll.lat,ll.lng,th)===null)return [x,y,ll.lat,ll.lng];} return null;})()""")
    if pt:
        E(f"__QA.select({pt[2]},{pt[3]},'육지 칸')"); pg.wait_for_timeout(400)
        s1=E("[document.querySelector('#iState').textContent,document.querySelector('#iSpeed').textContent,document.querySelector('#iNear').textContent]")
        check('N1 육지 칸을 찍어도 "자료 없음" 대신 바로 앞바다 값 + "(바로 앞바다)"', s1[0]!='자료 없음' and 'kn' in s1[1] and s1[2]=='(바로 앞바다)', [t,s1])
    else: check('N1 육지 칸(벽) 찾기', False, t)
    nf=E("(()=>{const r=__QA.nearFlow(34.5,129.5,__QA.tH()); return r?r.k:null})()")
    check('N2 근처에 바다 값이 없고 예보도 없으면 null → "자료 없음" 그대로', nf is None, nf)
    E("document.querySelector('#simBtn').click()"); E("__QA.pointView('none')")
    # ── H-10 조석 시험 6가지 ──
    E("__QA.tbTest()"); wait("window.__tbRes&&window.__tbRes.length===6",20)
    out=E("document.querySelector('#tbOut').textContent"); cs=E("window.__tbCalls.slice(-6)")
    check('T1 ⚙️ 조석 시험이 6가지 모양을 한 번에 물어봄', len(cs)==6 and 'min=60' in cs[0] and 'lat=33.96194' in cs[0] and 'min=1&' in cs[2] and 'min=' not in cs[3] and 'reqDate' not in cs[4], [c.split('?')[1].replace('serviceKey=K&','') for c in cs])
    check('T2 결과에 ✅/❌와 "되는 모양: ① 문서 예시 그대로"', '되는 모양: ① 문서 예시 그대로' in out and out.count('❌')==5 and out.count('✅')==1, out[:300])
    check('T3 키가 안 보임', 'serviceKey=K' not in out)
    ERRS_AT=len(errs)
''' + open('test/qa_b49_part2.py').read() + r'''
    check('Z 스크립트 오류 없음', not errs, errs[:3])
    br.close()
print(f'\n결과 {sum(res)}/{len(res)}')
''')
