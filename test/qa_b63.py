# build-63: U-30 물 차오름 경고 · U-31 내 입질 패턴
import sys, json
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0]
exec(src+r'''
    go(16,34.92,128.07,1500)
    LA,LO=34.9203,128.0702
    SETUP="""(()=>{const now=Date.now(), t=[], h=[]; for(let k=-18;k<=36;k++){t.push(now+k*600000); h.push(0.8+0.5*k/6);}
      __QA.TIDE.cur={ser:{t,h,unit:1},st:{n:'삼천포',c:'X'}}; __QA.ROCK.data=[[34.9204,128.0703,1,-1.0]]; __QA.FOLLOW.on=true;
      __QA.RISE.ack=''; __QA.RISE.snooze=0; __QA.RISE.mini=false; window.__riseBuzz=0; return 1;})()"""
    E(SETUP)
    E(f"__QA.riseCheck({LA},{LO},true)")
    w=E("[!document.querySelector('#riseWarn').hidden, document.querySelector('#riseMin').textContent, document.querySelector('#riseEst').textContent, window.__riseBuzz]")
    check('R1 50m 안 간출암이 30분 안에 잠기면 → 화면 전체 경고 + 긴 진동, 남은 분·추정 안내', w[0] and w[1] in ('약 24','약 25') and '삼천포' in w[2] and '추정' in w[2] and w[3]==1, w)
    full=E("(()=>{const r=document.querySelector('#riseWarn').getBoundingClientRect();return [Math.round(r.width),Math.round(r.height),innerWidth,innerHeight]})()")
    bt=E("[...document.querySelectorAll('#riseWarn .btns button')].map(b=>{const r=b.getBoundingClientRect();return [b.textContent,Math.round(r.height),Math.round(r.bottom)]})")
    check('R2 경고는 화면 전체를 덮고, 버튼 2개(56px)는 손이 닿는 아래쪽', full[0]==full[2] and full[1]==full[3] and all(b[1]>=56 for b in bt) and bt[-1][2]>full[3]-80, [full,bt])
    cr=E("""(()=>{const P=s=>s.match(/[\\d.]+/g).map(Number), L=c=>{const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2])};
      const fg=P(getComputedStyle(document.querySelector('#riseH')).color), bg=[120,10,6]; return +((L(fg)+.05)/(L(bg)+.05)).toFixed(2);})()""")
    check('R3 경고 글자 대비 4.5:1 이상 (흰 글씨 / 빨간 바탕)', cr>=4.5, cr)
    E(f"__QA.riseCheck({LA},{LO},true)")
    check('R4 같은 경고는 한 번만 울림(위치가 와도 다시 진동 안 함)', E("window.__riseBuzz")==1)
    E("document.querySelector('#riseOk').click()")
    b=E("[document.querySelector('#riseWarn').hidden, !document.querySelector('#riseBand').hidden, document.querySelector('#riseBandT').textContent]")
    check('R5 [확인했어요] → 경고 닫히고 지도 위 빨간 띠 "잠기기 N분 전"', b[0] and b[1] and b[2].startswith('잠기기 ') and b[2].endswith('분 전'), b)
    E("document.querySelector('#riseFold').click()"); f=E("[document.querySelector('#riseBand').hidden, !document.querySelector('#risePill').hidden, document.querySelector('#risePill').getBoundingClientRect().height]")
    E("document.querySelector('#risePill').click()"); f2=E("!document.querySelector('#riseBand').hidden")
    check('R6 띠 [접기] → 작은 ⚠️ 알약(44px), 누르면 다시 띠', f[0] and f[1] and f[2]>=44 and f2, [f,f2])
    E(f"__QA.riseCheck({LA+0.0009},{LO},true)")
    check('R7 바위에서 50m 넘게 멀어지면 띠가 사라짐', E("document.querySelector('#riseBand').hidden&&document.querySelector('#risePill').hidden&&document.querySelector('#riseWarn').hidden"))
    E(SETUP); E(f"__QA.riseCheck({LA},{LO},true)"); E("document.querySelector('#riseLater').click()")
    s1=E("[document.querySelector('#riseWarn').hidden, !document.querySelector('#riseBand').hidden]")
    E("__QA.RISE.snooze=Date.now()-1"); E(f"__QA.riseCheck({LA},{LO},true)")
    s2=E("[!document.querySelector('#riseWarn').hidden, window.__riseBuzz]")
    check('R8 [10분 뒤 다시] → 띠로 있다가 10분 뒤 다시 화면 경고·진동', s1==[True,True] and s2==[True,2], [s1,s2])
    E("__QA.ROCK.data=[[34.9204,128.0703,1,-2.0]]; __QA.RISE.ack=''; window.__riseBuzz=0"); E(f"__QA.riseCheck({LA},{LO},true)")
    check('R9 잠기기까지 30분 넘게 남았으면 알리지 않음', E("document.querySelector('#riseWarn').hidden&&document.querySelector('#riseBand').hidden") and E("window.__riseBuzz")==0)
    E(SETUP); E("__QA.FOLLOW.on=false"); E(f"__QA.riseCheck({LA},{LO},true)")
    check('R10 위치 따라가기를 끄면 경고도 없음', E("document.querySelector('#riseWarn').hidden&&document.querySelector('#riseBand').hidden"))
    ll=E(f"(()=>{{const q=_map.unproject([{CX}+300,{CY}+650],15);return [q.lat,q.lng]}})()")  # 시험 지도 섬 왼쪽 끝
    import math
    TL,TO=ll[0],ll[1]-150/(111320*math.cos(math.radians(ll[0])))
    go(16,TL,TO,1500); sh=E(f"__QA.riseShore({TL},{TO})")
    check('R11 가장 가까운 뭍(화면 바다 판별): 섬 끝까지 약 150m · 동쪽 근처', sh is not None and 100<=sh['m']<=200 and sh['dir'] in ['동북동','동','동남동'] and sh['dir'] in ['북','북북동','북동','동북동','동','동남동','남동','남남동','남','남남서','남서','서남서','서','서북서','북서','북북서'], sh)
    E("__QA.FOLLOW.on=false; __QA.RISE.ev=null; document.querySelector('#riseWarn').hidden=true; document.querySelector('#riseBand').hidden=true")
    # ── U-31 ──
    def mk(n):
        return E(f"""(()=>{{const a=[], ph=['들물 중반','들물 초반','날물 중반','들물 막바지','정조(물 멈춤)'], now=Date.now();
          for(let i=0;i<{n};i++){{const d=new Date(now-i*86400000); d.setHours(5+(i%3===2?1:0),30,0,0); a.push({{t:d.getTime(),lat:34.92,lng:128.07,name:'x',mul:['6물','7물','7물'][i%3],phase:ph[i%5],sp:0.3+(i%4)*0.1,wt:14+(i%3),fish:i%3?'갑오징어':'광어',memo:''}});}}
          __QA.saveLog(a); __QA.renderLog(); return a.length;}})()""")
    mk(3)
    p1=E("[document.querySelector('#logPat').textContent, document.querySelector('#logPat .prog i').style.width]")
    check('P1 기록 10번 전: "기록 3번 · 10번이 되면" + 모으는 막대(30%)', '기록 3번' in p1[0] and '10번이 되면' in p1[0] and p1[1]=='30%', p1)
    mk(14)
    p2=E("[document.querySelector('#logPat').textContent, [...document.querySelectorAll('#logPat .bar em')].map(e=>e.textContent), [...document.querySelectorAll('#logPat .chip')].map(e=>e.textContent)]")
    check('P2 기록 14번: 들물·날물·물 멈춤 막대(횟수·비율)', p2[1]==['9번 (64%)','3번 (21%)','2번 (14%)'], p2[1])
    check('P3 잘 잡힌 유속·시간·수온·물때 칩 + 적은 기록 안내', any('유속' in c and 'm/s' in c for c in p2[2]) and any('시간' in c for c in p2[2]) and any('수온' in c for c in p2[2]) and any('7물' in c for c in p2[2]) and '경향' in p2[0], p2[2])
    check('P4 점수 반영 스위치는 처음엔 꺼짐', E("document.querySelector('#patChk').checked") is False and E("AndroidBridge.getPref('patOn')")=='')
    E("document.querySelector('#patChk').click()"); on=E("AndroidBridge.getPref('patOn')")
    pb=E("""(()=>{const P=__QA.myPattern(), d=new Date(); d.setHours(5,0,0,0); const w={s:d.getTime(),t:d.getTime()+3*3600e3};
      return [__QA.patBias({best:{sp:0.45,w}},P), __QA.patBias({best:{sp:1.5,w:{s:w.s+10*3600e3,t:w.t+10*3600e3}}},P), __QA.patBias({best:{sp:0.45,w}},null)].map(v=>+v.toFixed(3));})()""")
    check('P5 켜면 저장, 내 패턴과 맞는 자리 +0.08(보이는 점수 +10), 안 맞으면 −0.03, 꺼짐이면 0', on=='1' and pb==[0.08,-0.03,0], [on,pb])
    E("document.querySelector('#planBtn').click(); document.querySelector('.ptabs [data-tab=log]').click()"); pg.wait_for_timeout(300)
    sw=E("(()=>{const r=document.querySelector('#logPat .tog').getBoundingClientRect();return Math.round(r.height)})()")
    check('P6 스위치 줄 누르는 범위 44 이상', sw>=44, sw)
    E("AndroidBridge.setPref('patOn','')")
    check('Z 스크립트 오류 없음', not errs, errs[:2])
    print(f"결과: {sum(res)}/{len(res)}")
    br.close()
''')
