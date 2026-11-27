# CLAUDE.md — 바다흐름지도(FishMap) 작업 지침

이 파일은 모든 세션 시작 시 로드된다. 작업 전에 읽고 따른다.

## 이 프로젝트가 뭔가
- **바다흐름지도**: 낚시인을 위한 조류·유속 지도 앱. 위성지도 위에 시간대별 물 흐름(흐름선), 항내 추정 유속, 조석·물때, 바위, 낚시 포인트 등을 보여준다.
- **형태 두 가지**: ① 안드로이드 앱(WebView, 단일 `app/src/main/assets/index.html`) ② 설치 없이 브라우저로 여는 단일 HTML(공개 웹판).
- **현재 형상**: `app/build.gradle`의 `versionName` 참고. 릴리스 번호(build-N)는 GitHub Actions 실행 번호이고, **빌드 때 CI가 `versionCode`를 이 실행 번호로 자동 설정**한다(build.yml) → Play 중복 업로드 방지. build.gradle의 versionCode 값은 자리표시(빌드 시 덮어씀). `versionName`은 사람이 올릴 때만 바꾼다.

## 핵심 파일
- `app/src/main/assets/index.html` — 앱 전체(화면·로직·흐름선·계산)가 든 단일 파일(약 400KB). 거의 모든 작업은 여기서 한다.
- `app/src/main/java/kr/fishmap/app/MainActivity.java` — 안드로이드 WebView 껍데기·네이티브 다리(AndroidBridge: getPref/setPref/httpGet/haptic/알람 등).
- `형상관리.md` — **요구사항 추적·빌드 이력·검증 기록·화면 이름표.** 기능 변경 시 같은 커밋으로 갱신한다.
- `docs/PROGRESS.md` — **작업 진행 로그(최근 세션 요약·대기 항목).** 아래 '대화 마무리 규칙' 참고.
- `docs/이름표.md`, `docs/이름표/*.png` — 화면·기능 이름표(이미지). `tools/make_nametags.py`로 재생성.
- `docs/앱개발표준.md` — 디자인 표준(HIG·터치 44·대비 4.5:1·한 줄 원칙 등).
- `test/` — 브라우저 QA(파이썬, Playwright)·node 단위시험. `test/tools/` 하네스.

## 유속 계산(방정식) — 함부로 바꾸지 말 것
- **예보**: 국립해양조사원 ROMS. `realAt`→`forecastPatch`(고정 0.1° 블록·예보 회차 확인)→`interpAt`(삼각형 선형보간 + 가장자리 Wendland 가중치).
- **항내 추정**: D2Q9 격자 볼츠만(LBM) Web Worker(`WORKER_SRC`). 고정 지리 격자 `FIELD_LEVEL=15`. `currentAtWorld`가 셀 이중선형 + smoothstep 이음매 보간. 조류예보 지점은 `anchorCells`/`stationForcing`으로 넛징.
- 이 계산은 검증된 상태다. **시현(그리는 법)과 계산(방정식)을 구분**하고, 계산은 사용자가 명시적으로 지시할 때만 손댄다.

## 유속 시현(그리는 법) — build-65 방식
- 단일 캔버스 `#flow`, 지수 감쇠 꼬리(τ 0.16s, 60fps에서 프레임당 ≈0.9), 선 1.5px, 촘촘한 밀도.
- `flowStep`: √속도 보정으로 약한 물살도 길게 흐르게. dt 기준이라 60fps에서 build-65와 같고 120Hz에서 안 빨라진다.
- 확대할수록 입자가 나뉘며 촘촘(줌 비례, 상한 3600). 확대 전환은 이전 캔버스를 배율 맞춰 이어 그려 끊김 없음.
- 항내 계산 중엔 빈 바다 대신 **예보 방향을 흰 선**으로, 완료되면 색으로.

## 작업 규칙 (형상관리.md의 사용자 지시)
1. 기능 변경 시 `형상관리.md`를 같은 커밋으로 갱신(빌드 이력·검증 기록).
2. **문제 보고 → 바로 고치지 말고** 재현·원인 확인 → 원인·수정안 보고 → 승인 후 수정.
3. **기능 개선·추가 전 초안 먼저**(화면 모습·동작·영향·시험 계획) 보여주고 확인받는다.
4. **안 된다고 섣불리 판단 말 것** — 직접 시도·시험해 확인.
5. **화면·기능 이름표 갱신**(화면·버튼·탭 변경 시 `docs/이름표.md` + 이미지).
6. **디자인 표준**(`docs/앱개발표준.md`) 따르고 점검표 통과 후 빌드.
7. **개선 사항은 모아서 한 번에**: 논의 중인 지시·후보는 대기 항목으로 적어두고, 사용자가 묶음 업데이트를 지시하면 함께 수정·검증·배포.
8. 변경은 **브라우저 QA로 검증**(아래) 후 빌드. 실기기만 볼 수 있는 건 '실기기 확인 필요'로 남긴다.

## 검증(시험)
- 브라우저 QA: `python3 test/tools/mkqa.py` 로 시험 페이지 만든 뒤 `bash test/tools/run_one.sh <qa_이름>` (가짜 ROMS 서버 + 스텁 Leaflet). 주요: `qa_b56`(흐름선·유향), `qa_flow`, `qa_ui`, `qa_design`, `qa_b69`(포인트), `qa_tidechip`.
- 물리 단위시험: `node test/qa_current_seam.js`, `node test/qa_current_forcing.js`, `node test/qa_depthgrid.js`(번들 수심 격자 보간·격자→바닥 마찰·육지 벽). 수온: `node test/qa_watertemp.js`(섬 건너편 차단·확대 수준 무관·관측소 경계·위성 보간, TILES_DIR 타일 필요 — `make_depth_tiles.py --bbox 127.5 34.4 128.6 35.3`, BADA 원본은 `git lfs pull`).
- 이 컨테이너엔 파이썬 playwright가 없을 수 있음 → `pip install playwright==<node playwright 버전>`(브라우저는 /opt/pw-browsers 것 사용, `playwright install` 금지).
- 미리 계산(다음 시각): `qa_precalc`(가드·토글·한도600). 쉴 때 앞 12시간 치를 SIMDB에 저장, 화면(`T.cur`)은 안 건드림. ⚙️ `⏩ 다음 시각 미리 계산`(기본 켬).
- 번들 수심(**전국, 타일식**): `app/src/main/assets/depth/`(`index.json` + `<bx>_<by>.json` 타일, 0.5°블록·150m·평균해수면). 전국 BADA(`DB/BADA2024_v1.1.txt.gz`, LFS)에서 **CI가 `tools/make_depth_tiles.py`로 생성** — 저장소엔 원본만, 타일은 빌드 산출물(gitignore). 전역 격자(원점 glon0/glat0, 셀 I행 J열, 블록 bx=⌊J/bc⌋). 앱은 **보는 구역 블록만** 메모리(LRU 16, `blkEnsure`). 웹 단일 HTML은 `build_web.py`가 **남해안만 임베드**(전국은 못 넣음). 육지 마스크는 BADA 점이 150m 안에 없으면 육지(-9999). 덮는 구역은 격자(오프라인), 밖은 자연과학용 수심 API. 수심→바닥 마찰(`K=K0+KZ`)은 그대로. 로컬 시험은 `make_depth_tiles.py --bbox`로 일부 타일 생성 후.
- **동시에 두 QA 배치를 돌리지 말 것** — `run_one.sh`가 `pkill chrome`을 해서 서로 죽인다. 순차로.
- 알려진 기존 실패(수정 전부터, 환경/하네스 문제라 무관): `qa_realshape` R2·R8, `qa_nest` S1(헤드리스 sim 워커 미완료), `qa_tidechip` C3·C9, `qa_levelbadge` L1·L2(배지 이름 노후화).

## 빌드·배포
- **앱**: `main`에 푸시하면 GitHub Actions(`.github/workflows/build.yml`)가 APK·서명 AAB·단일 HTML을 만들어 `build-<run_number>` 공개 릴리스로 올린다. (수동 실행 `gh workflow run build.yml --ref <branch>` 도 가능.)
- **아이폰/공개 웹**: 릴리스의 `fishmap-N.html`을 받아 `eastman0407/fishmap-web` 저장소 `index.html`로 올리고 main에 푸시 → GitHub Pages(`https://eastman0407.github.io/fishmap-web/`) 자동 배포. 릴리스 자산은 `gh api repos/eastman0407/FishMap/releases/assets/<id> -H "Accept: application/octet-stream"` 로 받는다(`gh release download`는 이 환경에서 GraphQL 403).
- 작업 브랜치는 `ccr-...`. main 푸시가 자동 권한 분류기에 막히면 한 번 더 시도하면 통과할 때가 있다.

## 팀 작업 (사용자 지시 2026-11-27)
- 사용자는 Claude하고만 대화한다. Claude가 총괄(설계·일부 구현·리뷰·통합·배포), **GPT·Grok은 구현 팀원**으로 Claude가 API로 업무를 지시한다.
- 상세: `docs/팀작업.md`. 도구: `python3 tools/team/team.py` (codex/ask/apply/new/ping/models). GPT는 기본으로 Codex CLI(구독 로그인, 세션마다 `codex login --device-auth`). 지시서는 `team/tasks/`.
- 유속 계산은 팀원에게 맡기지 않는다. 팀원 코드는 리뷰·QA 통과 후에만 합치고, main 푸시는 Claude만.

## 대화 마무리 규칙 (사용자 지시 2026-11-26)
- 사용자가 **"대화를 마칠게"**(또는 비슷한 종료 신호)라고 하면, 그 세션에서 한 일을 **`docs/PROGRESS.md`에 요약해 갱신하고 커밋·푸시**한다. (무엇을 바꿨는지, 현재 형상, 남은 대기 항목.)
