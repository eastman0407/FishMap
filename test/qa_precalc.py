# (B) 다음 시각 미리 계산 — 가드/토글 검증. 헤드리스 환경에서 sim 워커가 타일을 완료 못 해도
# 확인 가능한 '안전장치'만 본다(미리 계산이 화면을 안 건드리고, 쉴 때만·끄면 안 함·상태 바뀌면 비움).
import sys, time
from playwright.sync_api import sync_playwright

res=[]
def check(name, ok, detail=''):
    res.append(bool(ok)); print(('✅ ' if ok else '❌ ')+name+(' — '+str(detail) if detail else ''))

with sync_playwright() as p:
    br=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=br.new_page()
    errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('http://localhost:8094/index.html', wait_until='domcontentloaded')
    pg.wait_for_timeout(2000)
    E=lambda js: pg.evaluate(js)

    # 1) 기본값: 켬·12시간·600 한도
    check('P1 기본값 PRE.on=켬, hours=12', E("__QA.PRE.on")==True and E("__QA.PRE.hours")==12, [E("__QA.PRE.on"),E("__QA.PRE.hours")])
    check('P2 보관 한도 600 (SIMDB.clean 호출값)', E("document.documentElement.outerHTML.includes('SIMDB.clean(8,600)')"), 'OK')

    # 2) 체크박스가 PRE.on을 따라감 + 끄면 pref 저장·SIM.pre 비움
    E("__QA.SIM.pre=[{x:1},{x:2}]")  # 가짜로 채워두고
    E("document.getElementById('preChk').checked=false; document.getElementById('preChk').onchange()")
    check('P3 끄면 PRE.on=false·pref 0·SIM.pre 비움', E("__QA.PRE.on")==False and E("__QA.pref('preCalcOn','1')")=='0' and E("__QA.SIM.pre.length")==0,
          [E("__QA.PRE.on"), E("__QA.pref('preCalcOn','1')"), E("__QA.SIM.pre.length")])

    # 3) 꺼진 상태에서 simPrefetchPump 불러도 아무 일 없음(잡 안 생김)
    E("__QA.SIM.job=null; __QA.SIM.preGen=-1; __QA.simPrefetchPump()")
    pg.wait_for_timeout(300)
    check('P4 꺼짐이면 미리 계산 시작 안 함', E("__QA.SIM.job")==None and E("__QA.SIM.pre.length")==0, [E("__QA.SIM.job"), E("__QA.SIM.pre.length")])

    # 4) 다시 켜기
    E("document.getElementById('preChk').checked=true; document.getElementById('preChk').onchange()")
    check('P5 다시 켜면 PRE.on=true·pref 1', E("__QA.PRE.on")==True and E("__QA.pref('preCalcOn','1')")=='1', E("__QA.PRE.on"))

    # 5) 켜져 있어도 볼 게 준비 안 됨(SIM.done=false)·view 없음이면 미리 계산 시작 안 함(쉴 때만)
    E("__QA.SIM.view=[]; __QA.SIM.done=false; __QA.SIM.job=null; __QA.SIM.pre=[]; __QA.SIM.preGen=-1; __QA.simPrefetchPump()")
    pg.wait_for_timeout(300)
    check('P6 볼 것 준비 전/빈 화면이면 미리 계산 안 함', E("__QA.SIM.job")==None and E("__QA.SIM.pre.length")==0, [E("__QA.SIM.job"), E("__QA.SIM.pre.length")])

    # 6) 진단에 '미리 계산' 줄이 있음
    diag=E("(()=>{try{return __QA.runDiag();}catch(e){return (window.__lastDiag||'')}})()") or ''
    has=('미리 계산' in (diag if isinstance(diag,str) else '')) or ('미리 계산' in E("document.documentElement.outerHTML"))
    check('P7 진단/코드에 미리 계산 표시 존재', has, '')

    check('P8 스크립트 오류 없음', not errs, errs[:3])
    br.close()

print(f"결과: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
