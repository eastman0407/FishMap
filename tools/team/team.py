#!/usr/bin/env python3
"""Claude(총괄)가 GPT·Grok 팀원에게 작업을 맡기고 결과를 받아 적용하는 도구.

  python3 tools/team/team.py ping   --to gpt|grok           # 연결·키 확인
  python3 tools/team/team.py models --to gpt|grok           # 쓸 수 있는 모델 목록
  python3 tools/team/team.py new    T-001 "제목" --to gpt    # 작업지시서 만들기
  python3 tools/team/team.py ask    --to gpt --task team/tasks/T-001.md \
          --ctx app/src/main/assets/index.html:1200-1350 [--ctx 파일 ...] [--hard | --model M]
  python3 tools/team/team.py apply  team/out/T-001.gpt.1.md [--dry]

API 키는 환경변수(OPENAI_API_KEY / XAI_API_KEY) 또는 세션 프록시가 넣어 준다.
"""
import argparse, json, os, re, ssl, sys, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
OUT = ROOT / "team" / "out"
TASKS = ROOT / "team" / "tasks"


def member(to):
    if to not in ("gpt", "grok"):
        sys.exit("--to 는 gpt 또는 grok")
    return CFG[to]


def _ctx():
    ca = "/root/.ccr/ca-bundle.crt"
    return ssl.create_default_context(cafile=ca) if os.path.exists(ca) else ssl.create_default_context()


def call(m, path, body=None, timeout=None):
    # 키가 환경변수에 없으면 자리표시 값을 보낸다(세션 프록시가 진짜 키로 바꿔 넣음).
    key = os.environ.get(m["key_env"]) or "proxy-injected"
    req = urllib.request.Request(
        m["base"] + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout or CFG["timeout_sec"], context=_ctx()) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:800]
            if re.search(r"insufficient_quota|credit|spending limit", msg):
                sys.exit(f"[{m['name']}] API 크레딧 없음 — 결제 페이지에서 충전 필요: {msg[:300]}")
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(5 * (attempt + 1)); continue
            sys.exit(f"[{m['name']}] HTTP {e.code}: {msg}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(5 * (attempt + 1)); continue
            sys.exit(f"[{m['name']}] 연결 실패: {e}")


def read_ctx(spec):
    """'경로' 또는 '경로:시작-끝'(1부터, 끝 포함)."""
    mt = re.match(r"^(.*?):(\d+)-(\d+)$", spec)
    path, a, b = (mt.group(1), int(mt.group(2)), int(mt.group(3))) if mt else (spec, None, None)
    lines = (ROOT / path).read_text(encoding="utf-8").splitlines(keepends=True)
    if a:
        lines = lines[a - 1:b]
    where = f"{path} {a}~{b}행" if a else f"{path} 전체"
    return f"----- 참고 코드: {where} (원본 그대로) -----\n" + "".join(lines) + "\n----- 끝 -----\n"


def cmd_ask(args):
    m = member(args.to)
    task_path = ROOT / args.task
    task = task_path.read_text(encoding="utf-8")
    ctx = "".join(read_ctx(c) for c in (args.ctx or []))
    if len(ctx) > CFG["max_context_chars"]:
        sys.exit(f"참고 코드가 너무 큼({len(ctx)}자 > {CFG['max_context_chars']}). 구역을 줄일 것.")
    if args.feedback:
        task += "\n\n## 이전 제출에 대한 총괄(Claude) 피드백\n" + (ROOT / args.feedback).read_text(encoding="utf-8")
    body = {
        "model": args.model or (m["model_hard"] if args.hard else m["model"]),
        "messages": [
            {"role": "system", "content": (HERE / "system_prompt.md").read_text(encoding="utf-8")},
            {"role": "user", "content": "# 작업지시서\n" + task + "\n\n" + ctx},
        ],
    }
    t0 = time.time()
    res = call(m, "/chat/completions", body)
    text = res["choices"][0]["message"]["content"]
    OUT.mkdir(parents=True, exist_ok=True)
    stem = task_path.stem
    n = 1
    while (OUT / f"{stem}.{args.to}.{n}.md").exists():
        n += 1
    out = OUT / f"{stem}.{args.to}.{n}.md"
    usage = res.get("usage", {})
    price = m.get("price_per_mtok", {}).get(body["model"])
    cost = ""
    if price and usage:
        usd = (usage.get("prompt_tokens", 0) * price[0] + usage.get("completion_tokens", 0) * price[1]) / 1e6
        cost = f", 추정 ${usd:.3f}"
    out.write_text(
        f"<!-- {m['name']} model={res.get('model', body['model'])} "
        f"sec={time.time() - t0:.0f} usage={json.dumps(usage)} -->\n" + text,
        encoding="utf-8",
    )
    print(f"[{m['name']}] 답변 저장: {out.relative_to(ROOT)}  ({time.time() - t0:.0f}초, 입력 {usage.get('prompt_tokens')}·출력 {usage.get('completion_tokens')} 토큰{cost})")
    print(f"블록 {len(parse_blocks(text))}개")


BLOCK = re.compile(r"<<<<<<< SEARCH[ \t]*([^\n]*)\n(.*?)^=======[ \t]*\n(.*?)^>>>>>>> REPLACE", re.S | re.M)


def parse_blocks(text):
    return [(p.strip(), s, r) for p, s, r in BLOCK.findall(text)]


def cmd_apply(args):
    text = (ROOT / args.answer).read_text(encoding="utf-8")
    blocks = parse_blocks(text)
    if not blocks:
        sys.exit("SEARCH/REPLACE 블록이 없음")
    files, bad = {}, []
    for i, (path, s, r) in enumerate(blocks, 1):
        if not path:
            bad.append(f"#{i}: 파일 경로 없음"); continue
        fp = ROOT / path
        if path not in files:
            files[path] = fp.read_text(encoding="utf-8") if fp.exists() else None
        cur = files[path]
        if s.strip() == "":
            if cur is not None:
                bad.append(f"#{i} {path}: 새 파일인데 이미 있음"); continue
            files[path] = r; continue
        if cur is None:
            bad.append(f"#{i} {path}: 파일 없음"); continue
        k = cur.count(s)
        if k != 1:
            bad.append(f"#{i} {path}: SEARCH가 {k}곳에 맞음(1곳이어야 함)\n    첫 줄: {s.splitlines()[0][:100]!r}"); continue
        files[path] = cur.replace(s, r, 1)
    if bad:
        print("적용 실패 — 아무것도 바꾸지 않음:\n  " + "\n  ".join(bad)); sys.exit(1)
    for path, content in files.items():
        print(("[미리보기] " if args.dry else "") + f"고침: {path}")
        if not args.dry:
            (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
            (ROOT / path).write_text(content, encoding="utf-8")
    print(f"블록 {len(blocks)}개 {'확인' if args.dry else '적용'} 완료")


def cmd_new(args):
    TASKS.mkdir(parents=True, exist_ok=True)
    p = TASKS / f"{args.id}.md"
    if p.exists():
        sys.exit(f"이미 있음: {p.relative_to(ROOT)}")
    t = (TASKS / "_양식.md").read_text(encoding="utf-8")
    t = t.replace("T-000", args.id).replace("제목", args.title, 1).replace("GPT | Grok", member(args.to)["name"])
    p.write_text(t, encoding="utf-8")
    print(p.relative_to(ROOT))


def cmd_models(args):
    m = member(args.to)
    for x in sorted(d["id"] for d in call(m, "/models", timeout=60).get("data", [])):
        print(x)


def cmd_ping(args):
    m = member(args.to)
    res = call(m, "/chat/completions", {"model": args.model or m["model"],
               "messages": [{"role": "user", "content": "한 단어로 답해: 준비됐어?"}]}, timeout=120)
    print(f"[{m['name']}] {res.get('model')}: {res['choices'][0]['message']['content'].strip()[:80]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ask"); a.add_argument("--to", required=True); a.add_argument("--task", required=True)
    a.add_argument("--ctx", action="append"); a.add_argument("--model"); a.add_argument("--feedback")
    a.add_argument("--hard", action="store_true", help="어려운 작업: 상급 모델(model_hard) 사용")
    a.set_defaults(f=cmd_ask)
    b = sub.add_parser("apply"); b.add_argument("answer"); b.add_argument("--dry", action="store_true"); b.set_defaults(f=cmd_apply)
    c = sub.add_parser("new"); c.add_argument("id"); c.add_argument("title"); c.add_argument("--to", required=True); c.set_defaults(f=cmd_new)
    d = sub.add_parser("models"); d.add_argument("--to", required=True); d.set_defaults(f=cmd_models)
    e = sub.add_parser("ping"); e.add_argument("--to", required=True); e.add_argument("--model"); e.set_defaults(f=cmd_ping)
    args = ap.parse_args(); args.f(args)


if __name__ == "__main__":
    main()
