#!/bin/bash
# 시험 하나 돌리기: 가짜 예보 서버(9098)·시험 페이지 서버(8094)를 켜고 실행. 사용: test/tools/run_one.sh qa_flow
cd "$(dirname "$0")/../.."
pgrep -f mock_roms_real >/dev/null || (nohup node test/mock_roms_real.js >/tmp/mock.log 2>&1 &)
pgrep -f "http.server 8094" >/dev/null || (cd /tmp/qa && nohup python3 -m http.server 8094 >/dev/null 2>&1 &)
sleep 1; curl -s localhost:9098/reset >/dev/null
pkill -f chrome 2>/dev/null
timeout ${QA_TIMEOUT:-900} python3 -u test/$1.py > /tmp/r_$1.log 2>&1
