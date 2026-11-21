# build-62 (4묶음 + 작은 묶음): U-46 화면 모드 · U-47 손전등 · H-7 물때 방식 · U-45 ⑤ 같은 이름 마을
import sys, json
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0]
exec(src+r'''
    from PIL import Image
    go(13,34.92,128.07,1500)
    th=lambda: E("document.documentElement.dataset.theme")
    E("__QA.setTheme('dark')")
    check('T1 어둡게 = 원래 색(바탕 #0a1520)', th()=='dark' and E("getComputedStyle(document.body).backgroundColor")=='rgb(10, 21, 32)', th())
    E("__QA.setTheme('light')")
    bg=E("[getComputedStyle(document.body).backgroundColor,getComputedStyle(document.querySelector('#nowCard')).backgroundColor,getComputedStyle(document.body).color]")
    check('T2 밝게 = 밝은 바탕·어두운 글자 (위성 지도는 그대로)', th()=='light' and bg[0]=='rgb(233, 238, 242)' and bg[1].startswith('rgba(255, 255, 255') and bg[2]=='rgb(20, 32, 44)', bg)
    D3=r"""const P=s=>{const m=s.match(/[\d.]+/g);return m?m.map(Number):[0,0,0,0]}; const lum=c=>{const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2]);};
      const vis=e=>{if(!e.checkVisibility||!e.checkVisibility({opacityProperty:true,visibilityProperty:true}))return false; const r=e.getBoundingClientRect(); return r.width>0&&r.height>0&&r.bottom>0&&r.top<innerHeight;};
      const bgOf=e=>{let p=e;while(p&&p!==document.documentElement){const c=P(getComputedStyle(p).backgroundColor); if(c.length>=3&&(c.length<4||c[3]>0.5))return c; p=p.parentElement;} return null;};
      const o=[];for(const e of document.querySelectorAll('body *')){if(!e.firstChild)continue; let t=''; for(const n of e.childNodes)if(n.nodeType===3)t+=n.textContent; if(!t.trim()||!vis(e))continue; if(/\p{Extended_Pictographic}/u.test(t.trim())&&t.trim().length<=2)continue;
        const cs=getComputedStyle(e), fg=P(cs.color), bg=bgOf(e); if(!bg||(fg.length>3&&fg[3]<0.3))continue; if(parseFloat(cs.opacity)<0.6)continue; if(e.closest('button:disabled,.past'))continue;
        const L1=lum(fg),L2=lum(bg), cr=(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05), fs=parseFloat(cs.fontSize), big=fs>=24||(fs>=18.66&&+cs.fontWeight>=700);
        if(cr<(big?3:4.5))o.push([e.id||e.className||e.tagName,+cr.toFixed(2),t.trim().slice(0,10)]);} return o;"""
    v1=E("(()=>{"+D3+"})()")
    E("_map.fire('click',{latlng:_map.containerPointToLatLng([200,470])})"); pg.wait_for_timeout(700); v2=E("(()=>{"+D3+"})()"); E("__QA.pointView('none')")
    E("document.querySelector('#layersBtn').click(); document.querySelector('#setBtn').click()"); pg.wait_for_timeout(300); v3=E("(()=>{"+D3+"})()")
    E("document.querySelector('#setClose').click(); document.querySelector('#planBtn').click()"); pg.wait_for_timeout(300); v4=E("(()=>{"+D3+"})()")
    E("while(window.__onBack&&window.__onBack()){}")
    check('T3 밝게: 글자 대비 4.5:1(큰 글자 3:1) — 메인·지점 상태창·설정·출조 도우미', not (v1+v2+v3+v4), (v1+v2+v3+v4)[:5])
    # 설정 세그
    E("document.querySelector('#layersBtn').click(); document.querySelector('#setBtn').click()"); pg.wait_for_timeout(300)
    seg=E("[...document.querySelectorAll('#themeSeg button')].map(b=>{const r=b.getBoundingClientRect();return [b.textContent,Math.round(r.width),Math.round(r.height),b.classList.contains('on')]})")
    pg.set_viewport_size({'width':360,'height':700}); pg.wait_for_timeout(200)
    one=E("(()=>{const t=new Set([...document.querySelectorAll('#themeSeg button')].map(b=>Math.round(b.getBoundingClientRect().top)));return t.size})()")
    pg.set_viewport_size({'width':411,'height':700})
    check('T4 ⚙️ 화면 모드 4칸 한 줄(폭 360에서도), 높이 44, 지금 고른 칸 표시', [x[0] for x in seg]==['📱 시스템','☀️ 밝게','🌙 어둡게','🔴 밤낚시'] and all(x[2]>=44 for x in seg) and one==1 and seg[1][3], seg)
    E("document.querySelector('#themeSeg [data-t=system]').click()")
    E("window.__mq=matchMedia('(prefers-color-scheme: light)').matches")
    check('T5 시스템 = 폰 설정 따라감, 고른 값 저장', E("AndroidBridge.getPref('theme')")=='system' and th()==('light' if E("window.__mq") else 'dark'), th())
    pg.emulate_media(color_scheme='light'); pg.wait_for_timeout(200); a=th(); pg.emulate_media(color_scheme='dark'); pg.wait_for_timeout(200); b=th()
    check('T6 시스템 모드에서 폰이 밝게/어둡게로 바뀌면 바로 따라감', a=='light' and b=='dark', [a,b])
    E("document.querySelector('#setClose').click(); while(window.__onBack&&window.__onBack()){}")
    # 🔴 바로 켜기 + 손전등
    E("AndroidBridge.torchOk=()=>'0'; AndroidBridge.torch=on=>{window.__torch=on;return 'ok'}; AndroidBridge.setNight=on=>{window.__nb=on;}")
    nb=E("(()=>{const b=document.querySelector('#nightBtn'),r=b.getBoundingClientRect(),s=document.querySelector('.side .ibtn').getBoundingClientRect();return [b===document.querySelector('.side .ibtn'),Math.round(r.width),Math.round(r.height)]})()")
    E("document.querySelector('#nightBtn').click()"); pg.wait_for_timeout(400)
    st=E("[document.documentElement.dataset.theme, document.querySelector('#nightBtn').getAttribute('aria-pressed'), window.__nb, document.querySelector('#torchBtn').hidden, AndroidBridge.getPref('nightOn')]")
    check('T7 🔴 = 지도 버튼 줄 맨 앞(44×44), 한 번 누르면 밤낚시 + 화면 밝기 낮춤 + 🔦 나타남', nb[0] and nb[1]>=44 and st==['night','true',True,False,'1'], [nb,st])
    pg.screenshot(path='/tmp/b62_night.png'); im=Image.open('/tmp/b62_night.png').convert('RGB')
    E("document.querySelector('#flow').style.visibility='hidden'"); pg.wait_for_timeout(100); pg.screenshot(path='/tmp/b62_night_noflow.png'); im2=Image.open('/tmp/b62_night_noflow.png').convert('RGB'); E("document.querySelector('#flow').style.visibility=''")
    R0=E("(()=>{const r=document.querySelector('#nowCard').getBoundingClientRect();return [r.left,r.top,r.right,r.bottom].map(Math.round)})()")
    px=[im.getpixel((x,y)) for x in range(R0[0]+4,R0[2]-4,3) for y in range(R0[1]+4,R0[3]-4,3)]
    bright=[p for p in px if max(p)>60]; red=[p for p in bright if p[0]>=1.6*p[1] and p[0]>=1.6*p[2]]
    check('T8 밤낚시: 지금 카드의 밝은 점(글자·그림)이 모두 붉은색 (초록·파랑이 붉은색의 60% 미만)', bright and len(red)==len(bright), [len(red),len(bright),[p for p in bright if p not in red][:3]])
    # 지도 바탕(시험 지도 타일)도 붉게
    mp=[im2.getpixel((x,600)) for x in range(20,390,20)]; mb=[p for p in mp if max(p)>25]
    check('T9 밤낚시: 지도도 붉게 거름(흐름선·범례 색 막대는 유속 뜻을 위해 그대로)', mb and all(p[0]>=p[2] for p in mb) and E("getComputedStyle(document.querySelector('#flow')).filter")=='none' and E("getComputedStyle(document.querySelector('#legendBar')).filter")=='none', mb[:4])
    tb=E("(()=>{const t=document.querySelector('#torchBtn').getBoundingClientRect(),f=document.querySelector('#biteFab').getBoundingClientRect();return [Math.round(t.width),Math.round(t.height),Math.round(f.top-t.bottom),Math.abs((t.left+t.right)/2-(f.left+f.right)/2)<4]})()")
    check('T10 🔦 54px, 입질 버튼 바로 위(겹치지 않음, 가운데 맞춤)', tb[0]==54 and tb[1]==54 and 4<=tb[2]<=20 and tb[3], tb)
    E("document.querySelector('#torchBtn').click()"); t1=E("[window.__torch, document.querySelector('#torchBtn').classList.contains('on'), document.querySelector('#torchBtn').getAttribute('aria-pressed')]")
    E("window.__torchOff()"); t2=E("document.querySelector('#torchBtn').classList.contains('on')")
    check('T11 🔦 누르면 손전등 켜짐(빛나는 표시) · 앱이 뒤로 가면 꺼짐 표시', t1==[True,True,'true'] and t2 is False, [t1,t2])
    E("document.querySelector('#torchBtn').click()"); E("document.querySelector('#nightBtn').click()"); pg.wait_for_timeout(300)
    back=E("[document.documentElement.dataset.theme, window.__torch, document.querySelector('#torchBtn').hidden, window.__nb]")
    check('T12 🔴 다시 누르면 원래 모드(시스템→어둡게)로, 손전등 꺼짐·숨김, 밝기 원래대로', back==['dark',False,True,False], back)
    E("delete AndroidBridge.torchOk"); E("document.querySelector('#nightBtn').click()"); hid=E("document.querySelector('#torchBtn').hidden"); E("document.querySelector('#nightBtn').click()")
    check('T13 손전등이 없는 곳(웹판)은 🔦 버튼 숨김', hid is True)
    # 흐름 흰 선 색: 위성 = 흰색, 거리 지도 = 진한 회색 (코드 확인)
    check('T14 계산 중 흰 선: 위성 지도엔 흰색, 밝은 거리 지도엔 진한 회색', E("__QA.flowDraw.toString().length>0") and "mode==='street'?'#2b3742':'#ffffff'" in open('app/src/main/assets/index.html',encoding='utf-8').read())
    # H-7 물때 방식
    E("document.querySelector('#layersBtn').click(); document.querySelector('#setBtn').click()")
    m=[]
    for k in ['7','8','auto']:
        E(f"document.querySelector('#mulSeg [data-m=\"{k}\"]').click()"); m.append([E("__QA.MULSYS.v"),E("__QA.isWestSea(34.9,128.1)"),E("__QA.isWestSea(36.5,126.3)"),E("AndroidBridge.getPref('mulSys')")])
    lab=E("document.querySelector('#timeLabel').textContent")
    check('T15 ⚙️ 물때 이름 방식 [자동][7물식][8물식] — 고른 대로 계산·저장 (자동: 사천 8물식, 태안 7물식)', m==[['7',True,True,'7'],['8',False,False,'8'],['auto',False,True,'auto']] and '물' in lab, m)
    E("document.querySelector('#setClose').click()")
    d7=E("__QA.mulddae(Date.UTC(2026,10,9,3),true).name"); d8=E("__QA.mulddae(Date.UTC(2026,10,9,3),false).name")
    check('T16 7물식은 8물식보다 한 물 적게(조금·무시 빼고)', d7!=d8, [d7,d8])
    # U-45 ⑤
    r=E("[__QA.riOf({parcel:'경상남도 사천시 서포면 비토리 123'}),__QA.riOf({parcel:'경상남도 사천시 서포면 자혜리 산 12-1'}),__QA.riOf({parcel:'경상남도 사천시 향촌동 1'}),__QA.riOf(null)]")
    check('T17 지번 주소에서 리 이름 꺼냄(산 번지 포함), 동 주소·없음은 빈칸', r==['비토리','자혜리','',''], r)
    E("AndroidBridge.setPref('vworldKey','K')")
    out=E("""(async()=>{const ul=document.createElement('ul'); document.body.appendChild(ul);
      const P=[{la:34.91,lo:128.01,dong:'서포면',isl:'l'},{la:34.93,lo:128.03,dong:'서포면',isl:'l'},{la:34.95,lo:128.05,dong:'향촌동',isl:'l'}];
      __QA.ADDR.cache.set('34.91000,128.01000',{parcel:'경상남도 사천시 서포면 비토리 12'}); __QA.ADDR.cache.set('34.93000,128.03000',{parcel:'경상남도 사천시 서포면 자혜리 5'});
      ul.innerHTML=P.map((c,i)=>`<li data-i="${i}"><span class="rcn">x</span></li>`).join(''); ul._P=P;
      __QA.recVillage(ul,P,{n:'사천시'}); await new Promise(r=>setTimeout(r,200));
      const o=[...ul.querySelectorAll('.rcn')].map(e=>e.textContent); ul.remove(); return o;})()""")
    check('T18 같은 이름(서포면 해안)이 둘이면 리 이름을 작게 붙여 구분, 다른 이름은 그대로', out==['x· 비토리','x· 자혜리','x'], out)
    check('T19 스크립트 오류 없음', not errs, errs[:2])
    print(f"결과: {sum(res)}/{len(res)}")
    br.close()
''')
