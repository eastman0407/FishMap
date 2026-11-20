# 조과 기록장 시험 (REQ-44). 가짜 응답은 출조 계획 시험과 같음. 조석 칩 시험의 가짜 응답을 3주로 늘리고 조차가 사리·조금으로 바뀌게 함
# 원래: 조석 칩 시험: 다가오는 만조/간조, 들물·날물 단계, 물때 이름, 오늘 조석 목록 (build-24)
# 조석예보(고,저조) 가짜 응답: 삼천포(DT_0061) 한 곳, 만조 280cm·간조 20cm, 주기 12.42시간 (활용가이드 261106 응답 모양)
import sys, time, math, datetime
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
src=src.replace("""  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""",
"""  if(url.includes('tideFcstHghLw')){const q=new URL(url).searchParams; window.__tideCalls=(window.__tideCalls||0)+1;
    if(q.get('obsCode')!=='DT_0061')return reply(200,JSON.stringify({response:{header:{resultCode:'03',resultMsg:'NODATA_ERROR'}}}));
    const rd=q.get('reqDate'),y=+rd.slice(0,4),m=+rd.slice(4,6)-1,d=+rd.slice(6,8),day0=Date.UTC(y,m,d)-9*3600e3,P=12.42*3600e3,items=[],p2=v=>String(v).padStart(2,'0');
    for(let k=-6;k<=50;k++)for(const hi of [true,false]){const t=window.__HI0+k*P+(hi?0:P/2); if(t<day0||t>=day0+86400e3)continue;
      const dt=new Date(t+9*3600e3),pm=dt.getUTCHours()>=12;
      items.push({obsvtrNm:'삼천포',lot:'128.0700',lat:'34.9250',predcDt:`${dt.getUTCFullYear()}-${p2(dt.getUTCMonth()+1)}-${p2(dt.getUTCDate())} ${p2(dt.getUTCHours())}:${p2(dt.getUTCMinutes())}`,
        predcTdlvVl:(150+(hi?1:-1)*130*(0.6+0.4*Math.cos(2*Math.PI*(t-window.__HI0)/(14.77*86400e3)))).toFixed(1),extrSe:String(hi?(pm?3:1):(pm?4:2))});}
    items.sort((a,b)=>a.predcDt<b.predcDt?-1:1); const n=+q.get('numOfRows')||10;
    return reply(200,JSON.stringify({response:{header:{resultCode:'00',resultMsg:'NORMAL_SERVICE'},body:{items:{item:items.slice(0,n)},totalCount:items.length}}}));}
  if(!url.includes('/roms/'))return reply(200,JSON.stringify({response:{header:{resultCode:'03'}}}));""")
# 기준 만조: 오늘 0시(KST)+11시41분
src=src.replace('BRIDGE=r"""','BRIDGE=r"""window.__HI0=(()=>{const d=new Date();d.setHours(0,0,0,0);return d.getTime()+(11*60+41)*60000;})();')
assert 'tideFcstHghLw' in src
exec(src+'''
    go(13,34.92,128.07,0)
    for _ in range(60):
        if E("!!__QA.TIDE.cur"): break
        pg.wait_for_timeout(500)
    pg.wait_for_timeout(6000)
    E("localStorage.removeItem('fishmap.log.v1')")
    E("__QA.select(34.92,128.07,'실안 바위')"); pg.wait_for_timeout(500)
    E("document.querySelector('#biteBtn').click()")
    r=E("JSON.parse(localStorage.getItem('fishmap.log.v1')||'[]')")
    r0=r[0] if r else {}
    check('L1 🎣 입질! 한 번에 시각·장소·물때·들물/날물·조차·유속 자동 저장', len(r)==1 and r0.get('name')=='실안 바위' and r0.get('mul') and r0.get('phase') and r0.get('rg') and r0.get('sp') is not None and abs(r0['t']/1000-E("Date.now()")/1000)<60, r0)
    E("document.querySelector('#planBtn').click()"); pg.wait_for_timeout(300)
    E("document.querySelector('.ptabs [data-tab=log]').click()"); pg.wait_for_timeout(200)
    items=E("[...document.querySelectorAll('#logList>li')].map(l=>l.textContent)"); sm=E("document.querySelector('#logSum').textContent")
    check('L2 📓 기록 탭에 목록과 요약(들물/날물 횟수·많이 온 물때)', len(items)==1 and '실안 바위' in items[0] and '입질 1번' in sm and ('들물' in sm or '날물' in sm or '멈춤' in sm), [items, sm])
    E("document.querySelector('#logList>li').click()")
    E("const i=document.querySelector('#logList [data-f=fish]');i.value='갑오징어';i.dispatchEvent(new Event('change',{bubbles:true}))")
    E("const m=document.querySelector('#logList [data-f=memo]');m.value='에기 3.0호';m.dispatchEvent(new Event('change',{bubbles:true}))")
    r=E("JSON.parse(localStorage.getItem('fishmap.log.v1'))")
    check('L3 어종·메모 적으면 저장 (목록에 🐟 표시)', r[0]['fish']=='갑오징어' and r[0]['memo']=='에기 3.0호' and '🐟 갑오징어' in E("document.querySelector('#logList .l1').textContent"), r[0])
    E("document.querySelector('#logCsv').click()"); csv=E("window.__shared||''")
    lines=csv.lstrip(chr(0xfeff)).split(chr(10))
    check('L4 📤 CSV 보내기 (엑셀용 한글, 머리줄+기록)', csv.startswith(chr(0xfeff)) and '들물/날물' in lines[0] and len(lines)==2 and '갑오징어' in lines[1] and '실안 바위' in lines[1], lines)
    m0=E("window.__markers||0"); E("const c=document.querySelector('#logPins');c.checked=true;c.dispatchEvent(new Event('change'))"); m1=E("window.__markers||0")
    check('L5 지도에 기록 위치 표시 켜기', m1>m0 and E("AndroidBridge.getPref('logPins')")=='1', [m0,m1])
    E("document.querySelector('#biteBtn').click()"); E("__QA.renderLog&&__QA.renderLog()")
    E("document.querySelector('.ptabs [data-tab=log]').click()"); pg.wait_for_timeout(100)
    n2=E("document.querySelectorAll('#logList>li').length")
    E("document.querySelector('#logList>li').click()"); E("document.querySelector('#logList>li [data-del]').click()")
    n3=E("JSON.parse(localStorage.getItem('fishmap.log.v1')).length")
    n4=n3; ut=E("document.querySelector('#toast').textContent")
    check('L6 새 기록이 맨 위, 지우기는 한 번에 + [되돌리기] (REQ-75, 두 번 누르기 확인 대신)', n2==2 and n3==1 and '되돌리기' in ut, [n2,n3,ut])
    E("document.querySelector('#logList>li').click()"); E("document.querySelector('#logList>li [data-go]').click()"); pg.wait_for_timeout(300)
    check('L7 🗺 지도에서 보기 → 패널 닫고 그 지점 선택', not E("document.querySelector('#planPanel').classList.contains('show')") and E("__QA.sel()&&__QA.sel().name")=='실안 바위', E("__QA.sel()&&__QA.sel().name"))
    check('L8 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
