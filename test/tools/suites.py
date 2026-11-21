# 시험 묶음 (U-37, 11-21): 빌드 번호가 아니라 '화면·기능'별로 묶음. 빠른 시험은 만드는 도중, 전체 시험은 끝에 한 번.
# 사용: python3 test/tools/suites.py quick | full | <묶음 이름> | qa_xxx ...
import sys, subprocess, time, re, os
GROUPS={
 '할 일(처음부터 끝까지)':['qa_flow'],
 '디자인 자동 검사':['qa_design'],
 '지도·흐름선·항내 추정':['qa_realshape','qa_full','qa_sim','qa_stage1','qa_stage2','qa_stage4','qa_stage5','qa_h11','qa_nest','qa_levelbadge','qa_tidal','qa_b56'],
 '조석·물때':['qa_tidechip','qa_newapi'],
 '위 카드(M3)':['qa_b40','qa_b42','qa_b46','qa_more'],
 '상태창·그래프 시트(F28·M8)·움직임':['qa_b41','qa_b49','qa_b52','qa_b54','qa_b55'],
 '추천(P4·P6)':['qa_rec','qa_island','qa_b43','qa_b44','qa_ui'],
 '기록·계획·알림':['qa_log','qa_plan','qa_alert'],
 '날씨·수온':['qa_wx','qa_b48'],
 '설정·백업·웹판·화면 모드':['qa_web','qa_b47','qa_b62'],
 '이름·공유 받기':['qa_b53'],
 '터치·감성':['qa_b45'],
}
QUICK=['qa_flow','qa_design','qa_b56']  # H-15 ⑥: 흐름 방향 지키는 시험은 빠른 시험에 (11-22)
# 알려진 실패: 고장탐구 번호가 붙은 것만. 여기 있는 것만 실패해도 '⚠️ 알려진 실패'로 표시(새 실패는 ❌)
KNOWN_FAIL={}  # H-12 고침(build-61): qa_stage5 Z5 통과
def run(names):
    here=os.path.dirname(os.path.abspath(__file__)); subprocess.run(['python3',os.path.join(here,'mkqa.py')],check=True)
    rows=[]; t00=time.time()
    for n in names:
        t0=time.time(); subprocess.run([os.path.join(here,'run_one.sh'),n]); dt=time.time()-t0
        log=open(f'/tmp/r_{n}.log',errors='ignore').read()
        m=re.findall(r'결과[^0-9]*(\d+)\s*/\s*(\d+)',log); ok,tot=(int(m[-1][0]),int(m[-1][1])) if m else (0,0)
        crash='Traceback' in log and not m
        fails=re.findall(r'^❌ (\S+)',log,re.M); kf=KNOWN_FAIL.get(n); known=bool(kf) and tot>0 and fails==[kf[0]]
        rows.append((n,ok,tot,dt,crash,known))
        mark='✅' if (tot and ok==tot) else ('⚠️' if known else '❌')
        print(f"{mark} {n:16s} {ok}/{tot}  {dt/60:4.1f}분{'  (중간에 멈춤)' if crash else ''}{'  알려진 실패 '+kf[1] if known else ''}",flush=True)
    bad=[r for r in rows if (not r[2] or r[1]!=r[2]) and not r[5]]
    s=f"\n합계 {sum(r[1] for r in rows)}/{sum(r[2] for r in rows)} · {len(rows)}개 묶음 · {(time.time()-t00)/60:.1f}분 · 실패 묶음 {len(bad)}개 {[r[0] for r in bad]}"
    print(s); open('/tmp/qa_summary.txt','w').write('\n'.join(f"{r[0]} {r[1]}/{r[2]} {r[3]/60:.1f}분" for r in rows)+s)
    return not bad
if __name__=='__main__':
    a=sys.argv[1:] or ['quick']
    if a==['quick']: names=QUICK
    elif a==['full']: names=[n for g in GROUPS.values() for n in g]
    elif a[0] in GROUPS: names=GROUPS[a[0]]
    else: names=a
    sys.exit(0 if run(names) else 1)
