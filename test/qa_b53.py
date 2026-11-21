# build-53 시험 (2차-다): U-16 찍은 자리 이름 = 읍·면·동 앞바다(좌표는 작게) · U-26 지도 앱 공유로 위치 받기
# 바탕은 qa_flow(qa_b48 가짜 응답). 브이월드 주소→좌표·장소 검색·짧은 링크 따라가기는 가짜 응답으로 대신함
import sys, time, re
sys.argv=sys.argv[:1]
_c=open('test/qa_b48.py').read(); exec(_c.split("exec(src+'''")[0])
src=src+_c.split("exec(src+'''")[1].split("    go(13,34.92,128.07,0); pg.wait_for_timeout(800)\n    btn=")[0]
# 브이월드 주소→좌표(getcoord)·장소 검색 가짜 응답 (getAddress 가짜보다 먼저)
src=src.replace("  if(url.includes('api.vworld.kr/req/address')){",
"""  if(url.includes('request=getcoord')){window.__gcCalls=(window.__gcCalls||0)+1; window.__gcUrl=url;
    if(window.__gcNone||(window.__gcRoadNone&&url.includes('type=road')))return reply(200,JSON.stringify({response:{status:'NOT_FOUND'}}));
    return reply(200,JSON.stringify({response:{status:'OK',result:{point:{x:'128.0810',y:'34.9190'}}}}));}
  if(url.includes('api.vworld.kr/req/search')){window.__psCalls=(window.__psCalls||0)+1; if(window.__psNone)return reply(200,JSON.stringify({response:{status:'NOT_FOUND'}}));
    return reply(200,JSON.stringify({response:{status:'OK',result:{items:[{title:'노산공원',point:{x:'128.0650',y:'34.9220'}}]}}}));}
  if(url.includes('api.vworld.kr/req/address')){""")
exec(src+r'''
    def tapmap(x,y):
        E(f"(()=>{{const m=document.querySelector('#map').getBoundingClientRect(); _map.fire('click',{{latlng:_map.containerPointToLatLng([{x}-m.left,{y}-m.top])}});}})()"); pg.wait_for_timeout(500)
    def text(q): return E(f"(()=>{{const e=document.querySelector('{q}'); return e?e.innerText:''}})()")
    E("__QA.setPref('vworldKey','VK')")
    go(13,34.93,128.07,0); pg.wait_for_timeout(1200)
    # ── U-16 ──
    E("__QA.pointView&&__QA.pointView('none')"); tapmap(200,470); pg.wait_for_timeout(800)
    nm=E("document.querySelector('#fcName').innerText"); co=E("(document.querySelector('#fcName .co')||{}).innerText||''")
    check('A1 바다를 찍으면 이름이 읍·면·동 + 앞바다/바깥 바다, 좌표는 아래 작은 글씨', re.search(r'[가-힣]+(동|면|읍|리)\s*(앞바다|바깥 바다)',nm) and re.match(r'\d+\.\d{3}, \d+\.\d{3}$',co), nm.replace('\n',' | '))
    fs=E("[getComputedStyle(document.querySelector('#fcName .co')).fontSize, getComputedStyle(document.querySelector('#fcName')).fontSize]")
    check('A2 좌표 글씨 12px(최소 글씨 기준) · 이름보다 작음', fs[0]=='12px' and float(fs[1][:-2])>12, fs)
    nmS=E("[document.querySelector('#iname').textContent, document.querySelector('#fcName').textContent]")
    check('A3 그래프 시트 이름도 같음', nmS[0]==nmS[1], nmS)
    pn=E("[__QA.placeName(34.90,128.07), __QA.placeName(37.5,127.0), __QA.placeName(34.5,128.07)]")
    check('A4 해안에서 15km 넘게 먼 곳(내륙 서울)은 이름 없음 → 좌표 그대로', pn[1] is None and pn[0], pn)
    E("__QA.select(34.92,128.07,'내 포인트')"); pg.wait_for_timeout(500)
    a5=E("document.querySelector('#fcName').innerText")
    check('A5 즐겨찾기·검색 이름은 그대로 + 같은 모양으로 좌표 작게', a5.split('\n')==['내 포인트','34.920, 128.070'], a5)
    # ── U-26 글 읽기 ──
    P=E("""[__QA.shareParse("[네이버 지도]\\n삼천포항\\n경남 사천시 동서동 123-4\\nhttps://naver.me/xAbC12"),
      __QA.shareParse("[TMAP] 남일대해수욕장 경상남도 사천시 향촌동 산 25 https://tmap.life/abc"),
      __QA.shareParse("카카오맵에서 장소를 확인해보세요. 노산공원 경남 사천시 서금동 101-1 https://kko.to/xyz"),
      __QA.shareParse("삼천포항")]""")
    check('B1 네이버 공유 글: 앱·이름·주소·링크', P[0]['app']=='네이버지도' and P[0]['name']=='삼천포항' and P[0]['addr']=='경남 사천시 동서동 123-4' and P[0]['url'].startswith('https://naver.me'), P[0])
    check('B2 TMAP 한 줄 글 + 산 번지 알아봄', P[1]['app']=='TMAP' and P[1]['name']=='남일대해수욕장' and P[1]['san'], P[1])
    check('B3 카카오 글: 안내 문장 빼고 장소 이름만', P[2]['app']=='카카오맵' and P[2]['name']=='노산공원', P[2])
    check('B4 보통 검색어는 공유 글이 아님(지금처럼 검색)', not P[3]['share'], P[3])
    C=E("""[__QA.coordsIn("https://map.naver.com/p?c=14259000.5,4144000.2,15,0,0,0,dh"), __QA.coordsIn('{"x":"128.0712","y":"34.9254"}'), __QA.coordsIn('lat=34.92541&lng=128.07123'), __QA.coordsIn('https://naver.me/abc')]""")
    check('B5 링크·쪽 안 좌표 찾기(네이버 미터 좌표·x/y·lat/lng), 없으면 null', abs(C[0]['la']-34.8536)<0.001 and C[1]['lo']==128.0712 and C[2]['la']==34.92541 and C[3] is None, C)
    # ── U-26 받기: 링크 좌표 우선 ──
    E("""AndroidBridge.resolveUrl=(u,id)=>{window.__rsUrl=u; setTimeout(()=>window.__nativeCb(id,200,JSON.stringify({chain:[u,'https://m.place.naver.com/place/1?lat=34.92541&lng=128.07123'],body:''})),20);};
         AndroidBridge.takeShare=()=>{const t=window.__pend||''; window.__pend=''; return t;};""")
    E("window.__pend='[네이버 지도]\\n삼천포항\\n경남 사천시 동서동 123-4\\nhttps://naver.me/xAbC12'; window.__shareIn()"); pg.wait_for_timeout(1500)
    s=E("[__QA.sel().lat,__QA.sel().lng,__QA.sel().name]"); t=text('#toast')
    check('C1 안드 공유로 받기: 짧은 링크를 따라가 좌표로 핀 + 상태창, 이름=장소 이름', abs(s[0]-34.92541)<1e-6 and s[2]=='삼천포항' and E("document.querySelector('#fCard').classList.contains('show')||getComputedStyle(document.querySelector('#fCard')).display!='none'"), s)
    check('C2 안내: "네이버지도에서 받음 · 링크 좌표 기준 · 여기 맞아요?" + [옮겨 찍기]', '네이버지도에서 받음' in t and '링크 좌표 기준' in t and '옮겨 찍기' in t, t)
    # 옮겨 찍기
    E("[...document.querySelectorAll('#toast button')].find(b=>b.textContent==='옮겨 찍기').click()"); pg.wait_for_timeout(300)
    tapmap(150,520); s2=E("[__QA.sel().lat,__QA.sel().name]")
    check('C3 [옮겨 찍기] → 지도를 누른 자리로 핀이 옮겨지고 이름은 그대로', abs(s2[0]-s[0])>1e-4 and s2[1]=='삼천포항' and E("__QA.SHARE.move")==None, s2)
    tapmap(250,420); tapmap(250,420)  # U-27: 창이 떠 있으면 첫 누름은 닫기, 두 번째 누름이 새 자리
    check('C4 옮긴 뒤 다음 누름은 보통대로(창 닫기 → 새 자리, 이름 자동)', E("__QA.sel().name")!='삼천포항', E("__QA.sel().name"))
    # ── 링크에 좌표 없음 → 주소 → 브이월드 도로명 실패 → 지번 ──
    E("AndroidBridge.resolveUrl=(u,id)=>setTimeout(()=>window.__nativeCb(id,200,JSON.stringify({chain:[u],body:'<html>no</html>'})),20); window.__gcRoadNone=1; window.__gcCalls=0")
    E("window.__pend='[TMAP] 남일대해수욕장 경상남도 사천시 향촌동 산 25 https://tmap.life/abc'; window.__shareIn()"); pg.wait_for_timeout(1500)
    s=E("[__QA.sel().lat,__QA.sel().lng,__QA.sel().name]"); t=text('#toast')
    check('D1 링크에 좌표가 없으면 주소로: 도로명 실패 → 지번으로 다시', abs(s[0]-34.919)<1e-6 and E("window.__gcCalls")==2 and s[2]=='남일대해수욕장', [s,E("window.__gcCalls")])
    check('D2 산 번지면 "바닷가와 멀 수 있어요" 안내', '주소 기준' in t and '산 번지' in t, t)
    # ── 웹판·검색창 붙여넣기 (링크 못 따라감) → 장소 이름 ──
    E("delete AndroidBridge.resolveUrl; window.__gcNone=1; window.__psCalls=0")
    pg.fill('#q','카카오맵에서 장소를 확인해보세요. 노산공원 경남 사천시 서금동 101-1 https://kko.to/xyz'); E("document.querySelector('#sform').requestSubmit()"); pg.wait_for_timeout(2500)
    s=E("[__QA.sel().lat,__QA.sel().name]"); t=text('#toast')
    check('E1 검색창에 공유 글 붙여넣기 → 주소 못 찾으면 장소 이름(브이월드 장소 검색)으로', abs(s[0]-34.922)<1e-6 and s[1]=='노산공원' and E("window.__psCalls")==1 and '장소 이름 기준' in t, [s,t])
    check('E2 검색창은 비워지고 결과 목록은 닫힘', E("document.querySelector('#q').value")=='' and E("getComputedStyle(document.querySelector('#results')).display")=='none')
    # ── 못 찾음 ──
    E("window.__psNone=1"); E("__QA.setPref('vworldKey','')")
    E("__QA.shareIn('[네이버 지도]\\n없는곳')"); pg.wait_for_timeout(1500)
    check('F1 못 찾으면 핀을 옮기지 않고 안내', '못 찾았어요' in text('#toast') and E("__QA.sel().name")=='노산공원', text('#toast'))
    # ── ⚙️ 공유 링크 시험 ──
    E("__QA.setPref('vworldKey','VK'); window.__gcNone=0; window.__gcRoadNone=0")
    E("document.querySelector('#shTestIn').value='[네이버 지도] 삼천포항 경남 사천시 동서동 123-4'; document.querySelector('#shTest').click()"); pg.wait_for_timeout(1500)
    o=E("document.querySelector('#tbOut').textContent")
    check('G1 ⚙️ 공유 링크 시험: 단계별 기록(글 읽기 → 주소 → 결과), 키는 안 보임', '글 읽기' in o and '주소 → 좌표' in o and '결과: 34.91900' in o and 'VK' not in o, o.replace('\n',' | ')[:200])
    check('Z 스크립트 오류 없음', not errs, errs[:3])
    br.close()
print(f'\n결과 {sum(res)}/{len(res)}')
''')
