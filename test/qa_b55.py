# build-55 시험 (3묶음): U-48 지금 카드 쪽 넘기기 + 날씨 그림, U-45 추천 목록 카드
import sys
_c=open('test/qa_b49.py').read()
head=_c.split("    # ── U-10 상태창 ──")[0]
body=r'''
    go(13,34.92,128.07,0); pg.wait_for_timeout(1800)
    E("__QA.nowView('now')"); pg.wait_for_timeout(400)
    R=lambda q:E(f"(()=>{{const e=document.querySelector('{q}'); if(!e)return null; const b=e.getBoundingClientRect(); return [Math.round(b.left),Math.round(b.top),Math.round(b.width),Math.round(b.height)];}})()")
    check('C1 접기·끌기 손잡이 없어짐 + 탭 줄 + 쪽 영역', E("!document.querySelector('#nowFold')&&!document.querySelector('#nowGrip')&&!!document.querySelector('#ncPages')&&!!document.querySelector('#nowSeg')"), None)
    h=E("document.querySelector('#nowCard').offsetHeight")
    check('C2 지금 카드 높이 ≤ 125px (시안 97)', h<=125, h)
    sty=E("[document.querySelector('#tideChip').offsetParent!==null, document.querySelector('#phaseChip').textContent, document.querySelector('#ncDots').children.length, window.__QA.NCP.n]")
    check('C3 1쪽: 물때 칩 보임, 쪽 표시 막대 있음', sty[0] and sty[2]>=2, sty)
    E("__QA.ncGo(1,true)"); pg.wait_for_timeout(300)
    wt=E("document.querySelector('#wtChip').textContent")
    ov=E("[...document.querySelectorAll('.ncpg')].map(p=>p.scrollWidth<=p.clientWidth+1)")
    check("C4 2쪽: 수온 칩에 '내일 ±0.0' 글자 + 칩이 안 잘림", ('내일' in (wt or '') and re.search(r'[+−]\d\.\d',wt or '')) and all(ov), [wt,ov])
    E("__QA.ncGo(0,true)"); pg.wait_for_timeout(250)
    box=R('#ncPages'); cx,cy=box[0]+box[2]/2, box[1]+box[3]/2
    c0=E("[__QA.map.getCenter().lat,__QA.map.getCenter().lng]")
    def drag(dx,dur):
        pg.mouse.move(cx,cy); pg.mouse.down(); n=6
        for k in range(1,n+1):
            pg.mouse.move(cx+dx*k/n,cy); pg.wait_for_timeout(int(dur/n))
        pg.mouse.up(); pg.wait_for_timeout(350)
    drag(-30,700); i1=E("__QA.NCP.i")      # 짧고 느림 (폭 10% 안팎) → 제자리
    check('S1 조금만(30px) 천천히 밀면 제자리', i1==0, i1)
    drag(-int(box[2]*0.4),700); i2=E("__QA.NCP.i")
    check('S2 폭 30% 넘게 밀면 다음 쪽으로 딱 넘어감', i2==1, [i2,box[2]])
    drag(80,0); i3=E("__QA.NCP.i")
    check('S3 짧아도 빠르게 튕기면 이전 쪽', i3==0, i3)
    c1=E("[__QA.map.getCenter().lat,__QA.map.getCenter().lng]")
    check('S4 카드 위에서 밀어도 지도는 안 움직임', c0==c1, [c0,c1])
    # 칩 눌림은 살아 있음
    E("__QA.ncGo(0,true)"); pg.wait_for_timeout(200)
    # 날씨 그림
    ic=E("""(()=>{const out={}; for(const [k,w] of Object.entries({sun:{sky:1,pty:0},cloud:{sky:3,pty:0},grey:{sky:4,pty:0},rain:{sky:4,pty:1},shower:{sky:3,pty:4},sleet:{sky:4,pty:2},snow:{sky:4,pty:3}})){const r=__QA.wxIcon(w,12); out[k]=r.e+r.t;} out.night=__QA.wxIcon({sky:1,pty:0},23).e; return out;})()""")
    want={'sun':'☀️','cloud':'⛅','grey':'☁️','rain':'☔비','shower':'🌦️소나기','sleet':'🌨️비/눈','snow':'❄️눈'}
    check('W1 날씨 그림: 맑음 ☀️·구름많음 ⛅·흐림 ☁️ (그림만) / 비 ☔·소나기 🌦️·비/눈 🌨️·눈 ❄️ (그림+글자), 밤 🌙', all(ic[k]==v for k,v in want.items()) and ic['night']=='🌙', ic)
    # 큰 글씨: 넘치면 쪽이 늘고 칩은 안 잘림
    E("document.documentElement.style.fontSize='130%'; __QA.ncRepage()"); pg.wait_for_timeout(300)
    r130=E("[__QA.NCP.n,[...document.querySelectorAll('.ncpg')].every(p=>p.scrollWidth<=p.clientWidth+1)]")
    E("document.documentElement.style.fontSize='200%'; __QA.ncRepage()"); pg.wait_for_timeout(300)
    r200=E("[__QA.NCP.n,[...document.querySelectorAll('.ncpg')].every(p=>p.scrollWidth<=p.clientWidth+1)]")
    check('B1 큰 글씨(130%·200%)에서도 칩이 안 잘리고, 넘치면 쪽이 늘어남', r130[1] and r200[1] and r200[0]>=r130[0]>=2, [r130,r200])
    E("document.documentElement.style.fontSize=''; __QA.ncRepage()")
    # 오늘 추천 보기 ↔ 지금
    E("__QA.nowView('rec')"); pg.wait_for_timeout(300)
    v1=E("[getComputedStyle(document.querySelector('#ncPages')).display,getComputedStyle(document.querySelector('#nowRec')).display]")
    E("__QA.nowView('now')"); pg.wait_for_timeout(300)
    v2=E("getComputedStyle(document.querySelector('#ncPages')).display")
    check('V1 ⭐ 오늘 추천으로 바꾸면 쪽 영역 숨고, 지금으로 돌아오면 다시 보임', v1[0]=='none' and v1[1]!='none' and v2!='none', [v1,v2])
    check('Z 스크립트 오류 없음', not errs, errs[:3])
    br.close()
print(f'\n결과 {sum(res)}/{len(res)}')
'''
pre,inner=head.split("exec(src+r'''")
exec(pre+"exec(src+r'''"+inner+body+"''')")
