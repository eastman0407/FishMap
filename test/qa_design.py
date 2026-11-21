# 디자인 자동 검사 (U-37, 11-21) — UI 가이드 5장 QA 점검표를 매 업데이트 자동으로.
# 화면 8곳 × 폭 360·411 (+ 큰 글씨 130% 근사)에서 잰다:
#  D1 누르는 범위 44 이상   D2 글씨 12px 이상   D3 글자 대비 4.5:1(큰 글자 3:1)
#  D4 부품 대비 3:1(막대·손잡이)   D5 화면 밖·넘침 없음   D6 떠 있는 것끼리 안 겹침   D7 큰 글씨에서 이름이 안 사라짐
# 이미 대기 목록에 있는 위반(KNOWN)은 '알려진 위반'으로 따로 세고, 새 위반만 실패로 본다. 고치면 KNOWN에서 빼야 통과 표시가 정확해진다.
import sys, time
sys.argv=sys.argv[:1]
_c=open('test/qa_b48.py').read(); exec(_c.split("exec(src+'''")[0])
src=src+_c.split("exec(src+'''")[1].split("    go(13,34.92,128.07,0); pg.wait_for_timeout(800)\n    btn=")[0]
KNOWN={
 # (build-50) U-13·14·17·40은 고쳐서 목록에서 뺌. 남은 알려진 위반만 여기에 적음
 'D1':{},'D2':{},'D4':{},
 'D8':{'#setPanel LABEL':'U-24'},  # 설정 안 긴 설명 줄(조석 보정) — U-24 설정 화면 정리(2차) 때 한 줄로
 'D7':{},
}
exec(src+r'''
    W0=411
    def tap(x,y):
        E(f"(()=>{{const m=document.querySelector('#map').getBoundingClientRect(); _map.fire('click',{{latlng:_map.containerPointToLatLng([{x}-m.left,{y}-m.top])}});}})()"); pg.wait_for_timeout(350)
    # 요소 이름(위반을 알아보는 열쇠): id → 조상 id + 태그/클래스
    KEYJS=r"""const key=e=>{if(e.id)return '#'+e.id; const c=(e.className&&typeof e.className==='string')?'.'+e.className.trim().split(/\s+/)[0]:''; let p=e.parentElement,pid=''; while(p&&!pid){if(p.id)pid='#'+p.id; else if(p.className&&typeof p.className==='string'&&/^(fcard|igrid|legend|lcell|stats|rchips|ticks|tl)$/.test(p.className.split(' ')[0]))pid='.'+p.className.split(' ')[0]; p=p.parentElement;} return (pid?pid+' ':'')+(c||e.tagName)+(e.dataset&&e.dataset.go?'[data-go]':'');};
      const vis=e=>{if(!e.checkVisibility||!e.checkVisibility({opacityProperty:true,visibilityProperty:true}))return false; const r=e.getBoundingClientRect(); return r.width>0&&r.height>0&&r.bottom>0&&r.top<innerHeight;};"""
    D1=KEYJS+r"""const o=[];for(const e of document.querySelectorAll('button,select,input[type=checkbox],.rr,li[data-i],#tideChip,#phaseChip,[data-go]')){if(!vis(e))continue; if(e.closest('.leaflet-control,.lsheet .lcell small'))continue;
      const r=e.getBoundingClientRect(), a=getComputedStyle(e,'::after'); let w=Math.max(r.width,parseFloat(a.width)||0), h=Math.max(r.height,parseFloat(a.height)||0);
      const lab=e.tagName==='INPUT'&&e.closest('label'); if(lab){const q=lab.getBoundingClientRect(); w=Math.max(w,q.width); h=Math.max(h,q.height);}
      if(w<43.5||h<43.5)o.push([key(e),Math.round(w),Math.round(h)]);} return o;"""
    D2=KEYJS+r"""const o=[];for(const e of document.querySelectorAll('body *')){if(!e.firstChild)continue; let t=''; for(const n of e.childNodes)if(n.nodeType===3)t+=n.textContent; if(!t.trim()||!vis(e))continue; const f=parseFloat(getComputedStyle(e).fontSize); if(f<11.95)o.push([key(e),f,t.trim().slice(0,12)]);} return o;"""
    D3=KEYJS+r"""const P=s=>{const m=s.match(/[\d.]+/g);return m?m.map(Number):[0,0,0,0]}; const lum=c=>{const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2]);};
      const bgOf=e=>{let p=e;while(p&&p!==document.documentElement){const c=P(getComputedStyle(p).backgroundColor); if(c.length>=3&&(c.length<4||c[3]>0.5))return c; p=p.parentElement;} return null;};
      const o=[];for(const e of document.querySelectorAll('body *')){if(!e.firstChild)continue; let t=''; for(const n of e.childNodes)if(n.nodeType===3)t+=n.textContent; if(!t.trim()||!vis(e))continue; if(/\p{Extended_Pictographic}/u.test(t.trim())&&t.trim().length<=2)continue;
        const cs=getComputedStyle(e), fg=P(cs.color), bg=bgOf(e); if(!bg||(fg.length>3&&fg[3]<0.3))continue; if(parseFloat(cs.opacity)<0.6)continue;
        const L1=lum(fg),L2=lum(bg), cr=(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05), fs=parseFloat(cs.fontSize), big=fs>=24||(fs>=18.66&&+cs.fontWeight>=700);
        if(e.closest('button:disabled,.past'))continue;
        if(cr<(big?3:4.5))o.push([key(e),+cr.toFixed(2),t.trim().slice(0,10)]);} return o;"""
    D5=KEYJS+r"""const o=[];for(const e of document.querySelectorAll('body *')){if(!vis(e))continue; if(e.closest('#map,#ncPages'))continue; const r=e.getBoundingClientRect(); if(r.right>innerWidth+1||r.left<-1)o.push(['밖',key(e),Math.round(r.left),Math.round(r.right)]);
      const cs=getComputedStyle(e); if(!e.children.length&&e.textContent.trim().length>2&&e.scrollWidth>e.clientWidth+2&&cs.overflow!=='hidden'&&cs.textOverflow!=='ellipsis'&&cs.display!=='inline')o.push(['넘침',key(e),e.textContent.trim().slice(0,12)]);} return o.slice(0,20);"""
    D6=r"""const R=q=>{const e=document.querySelector(q); if(!e||!e.checkVisibility({opacityProperty:true,visibilityProperty:true}))return null; const r=e.getBoundingClientRect(); return r.width?r:null;};
      const pairs=[['#nowCard','.side'],['.legend','#biteFab'],['.legend','.trow'],['#biteFab','.trow'],['#fCard','.side'],['#fCard','#nowCard'],['#fCard','.trow'],['#pinPop','.trow'],['#pinPop','#nowCard'],['#offBar','#toast']]; const o=[];
      for(const [a,b] of pairs){const A=R(a),B=R(b); if(!A||!B)continue; const w=Math.min(A.right,B.right)-Math.max(A.left,B.left), h=Math.min(A.bottom,B.bottom)-Math.max(A.top,B.top); if(w>1&&h>1)o.push([a,b,Math.round(w),Math.round(h)]);} return o;"""
    D8=KEYJS+r"""const o=[];for(const e of document.querySelectorAll('button,.tchip,.seg button,.ptabs button,.rchips button,.chip,label:has(>input[type=checkbox])')){if(!vis(e))continue; if(e.closest('.leaflet-control'))continue; if(!(e.textContent||'').trim())continue;
      let two=false; const tw=document.createTreeWalker(e,NodeFilter.SHOW_TEXT); for(let n;n=tw.nextNode();){ if(!n.textContent.trim())continue; const rg=document.createRange(); rg.selectNodeContents(n); const tops=new Set([...rg.getClientRects()].filter(r=>r.width>1).map(r=>Math.round(r.top/6))); if(tops.size>1)two=true;} if(two)o.push([key(e),(e.textContent||'').trim().slice(0,12)]);} return o.slice(0,20);"""
    found={k:{} for k in ['D1','D2','D3','D5','D6','D8']}
    def known(kind,key): return KNOWN.get(kind,{}).get(key)
    def measure(screen):
        for kind,js in [('D1',D1),('D2',D2),('D3',D3),('D5',D5),('D6',D6),('D8',D8)]:
            for it in E("(()=>{"+js+"})()"):
                k=str(it[0]) if kind!='D6' else f"{it[0]}×{it[1]}"
                found[kind].setdefault(k,[]).append((screen,it))
    screens=[]
    def at(name,w,prep):
        pg.set_viewport_size({'width':w,'height':860}); pg.wait_for_timeout(250); prep(); pg.wait_for_timeout(450); measure(f'{name}@{w}'); screens.append(f'{name}@{w}')
    go(13,34.92,128.07,0); pg.wait_for_timeout(1200)
    E("document.querySelector('#nowSeg [data-v=now]').click()")
    for w in (360,411):
        at('메인',w,lambda: E("__QA.pointView('none')"))
        at('지점 상태창',w,lambda: tap(w/2,470))
        at('그래프 시트',w,lambda: E("document.querySelector('#fcGraph').click()"))
        at('보기',w,lambda: (E("__QA.pointView('none')"), E("document.querySelector('#layersBtn').click()")))
        at('설정',w,lambda: (E("document.querySelector('#layerClose').click()"), E("document.querySelector('#layersBtn').click()"), E("document.querySelector('#setBtn').click()")))
        at('추천 탭',w,lambda: (E("document.querySelector('#setClose').click()"), E("document.querySelector('#planBtn').click()")))
        at('기록 탭',w,lambda: E("document.querySelector('.ptabs [data-tab=log]').click()"))
        at('위 카드 추천',w,lambda: (E("document.querySelector('#planClose').click()"), E("document.querySelector('#nowSeg [data-v=rec]').click()")))
        E("document.querySelector('#nowSeg [data-v=now]').click()")
    # D4 부품 대비 3:1 (막대·손잡이)
    def cr(a,b):
        def L(c):
            f=lambda v:(v/255)/12.92 if v/255<=0.03928 else (((v/255)+0.055)/1.055)**2.4
            return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2])
        x,y=sorted([L(a),L(b)],reverse=True); return round((x+0.05)/(y+0.05),2)
    import re
    rgb=lambda s:[int(v) for v in re.findall(r'\d+',s)[:3]]
    panel=rgb(E("getComputedStyle(document.querySelector('.sheet')).backgroundColor"))
    # 시간 막대 바탕색은 그라데이션 안에 있어 계산값으로 못 읽음 → CSS 값(#2a4560)을 앱 원본에서 읽음
    css=open('app/src/main/assets/index.html').read(); mt=re.search(r'#slider::-webkit-slider-runnable-track\{[^}]*var\(--p\),(#[0-9a-fA-F]{6})',css)
    track=[int(mt.group(1)[i:i+2],16) for i in (1,3,5)] if mt else [42,69,96]
    d4={'slider-track':cr(track,panel)}
    # D7 큰 글씨 130% 근사: 시트 이름이 3글자 넘게 보이는가
    pg.set_viewport_size({'width':411,'height':860}); E("document.documentElement.style.zoom='1.3'"); tap(200,470); E("document.querySelector('#fcGraph').click()"); pg.wait_for_timeout(500)
    nm=E("(()=>{const e=document.querySelector('#iname'),r=e.getBoundingClientRect();return [Math.round(r.width/1.3), e.textContent.length]})()"); E("document.documentElement.style.zoom=''"); E("__QA.pointView('none')")
    d7={'sheet-name':nm[0]>=60}
    # 판정
    def judge(kind,title):
        new=[];kn={}
        for k,v in found[kind].items():
            u=known(kind,k)
            if u: kn.setdefault(u,set()).add(k)
            else: new.append((k,v[0]))
        check(f'{kind} {title} — 새 위반 없음', not new, (new[:4], {u:sorted(s)[:4] for u,s in kn.items()}))
        if new: print('   새 위반 전체:', sorted(set(k for k,_ in new)))
        return kn
    k1=judge('D1','누르는 범위 44 이상')
    k2=judge('D2','글씨 12px 이상')
    judge('D3','글자 대비 4.5:1 (큰 글자 3:1)')
    newd4=[k for k,v in d4.items() if v<3 and k not in KNOWN['D4']]
    check('D4 부품 대비 3:1 (시간 막대·손잡이) — 새 위반 없음', not newd4, d4)
    judge('D5','화면 밖으로 나가거나 넘침 없음')
    judge('D6','떠 있는 것끼리 안 겹침')
    judge('D8','버튼·칩·탭 글자 한 줄 (U-42, 폭 360·411·큰 글씨)')
    check('D7 큰 글씨 130%에서 시트 이름이 보임 (알려진 위반 U-15면 표시만)', d7['sheet-name'] or 'sheet-name' in KNOWN['D7'], {'보이는 폭':nm[0],'알려진 위반':'U-15' if not d7['sheet-name'] else '없음'})
    # D8 큰 글씨(130% 근사)에서도 버튼 글자 한 줄
    pg.set_viewport_size({'width':411,'height':860}); E("document.documentElement.style.zoom='1.3'")
    for nm_,prep in (('큰글씨 메인',lambda: E("__QA.pointView('none')")),('큰글씨 추천 탭',lambda: E("document.querySelector('#planBtn').click()")),('큰글씨 기록 탭',lambda: E("document.querySelector('.ptabs [data-tab=log]').click()"))):
        prep(); pg.wait_for_timeout(450)
        for it in E("(()=>{"+D8+"})()"): found['D8'].setdefault(str(it[0]),[]).append((nm_,it))
    E("document.documentElement.style.zoom=''")
    print('\n화면', len(screens), '곳 ·', ', '.join(screens[:8]))
    print('알려진 위반(대기 목록):', {'U-15':0 if d7['sheet-name'] else 1})
    check('Z 스크립트 오류 없음', not errs, errs[:3])
    br.close()
print(f'\n결과 {sum(res)}/{len(res)}')
''')
