#!/usr/bin/env python3
"""섬 다리 자료 만들기 (REQ-60). GitHub Actions에서 실행 (인터넷 되는 곳).
OpenStreetMap 다리·터널 길(Overpass)을 시·군·구마다 받아, 앱의 islandBridges()와 같은 방법으로
'육지에서 다리로 닿는 섬 고리 번호'를 찾아 bridges.json 으로 저장한다.
사용: python3 tools/make_bridges.py --assets app/src/main/assets --out app/src/main/assets/bridges.json
실패한 시·군·구는 --old 파일(지난 릴리스 자료)에 있으면 그것을 그대로 씀.
"""
import argparse, json, math, os, sys, time, urllib.parse, urllib.request, datetime

ap = argparse.ArgumentParser()
ap.add_argument('--assets', default='app/src/main/assets')
ap.add_argument('--out', default='app/src/main/assets/bridges.json')
ap.add_argument('--old', default='')
ap.add_argument('--sleep', type=float, default=2.0)
a = ap.parse_args()

HOSTS = ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter',
         'https://overpass.private.coffee/api/interpreter', 'https://maps.mail.ru/osm/tools/overpass/api/interpreter']

def dist(la1, lo1, la2, lo2):
    R = 6371000; p1 = math.radians(la1); p2 = math.radians(la2)
    dp = p2 - p1; dl = math.radians(lo2 - lo1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

def fetch(q):
    last = ''
    for rnd in range(3):
        for h in HOSTS:
            try:
                req = urllib.request.Request(h, data=urllib.parse.urlencode({'data': q}).encode(),
                                             headers={'User-Agent': 'FishMap-bridges/1 (github.com/eastman0407)'})
                with urllib.request.urlopen(req, timeout=90) as r:
                    j = json.loads(r.read().decode('utf-8'))
                if isinstance(j.get('elements'), list):
                    return j, ''
                last = h + ': 응답 모양 다름'
            except Exception as e:
                last = h + ': ' + str(e)[:80]
            time.sleep(1)
        time.sleep(5 * (rnd + 1))
    return None, last

def rings_for(sg, all_):
    b = sg['b']; pad = 0.03
    bb = f"{b[0]-pad:.3f},{b[1]-pad:.3f},{b[2]+pad:.3f},{b[3]+pad:.3f}"
    q = f'[out:json][timeout:60];(way["highway"]["bridge"]["bridge"!="no"]({bb});way["highway"]["tunnel"]["tunnel"!="no"]({bb}););out geom;'
    js, err = fetch(q)
    if js is None:
        return None, err
    G = 0.01; bins = {}
    for r in all_:
        P = r['p']; ri = r.get('ri')
        if P[0] < b[0] - 0.2 or P[0] > b[2] + 0.2:
            continue
        for i in range(0, len(P), 2):
            la, lo = P[i], P[i + 1]
            if la < b[0]-pad-0.01 or la > b[2]+pad+0.01 or lo < b[1]-pad-0.01 or lo > b[3]+pad+0.01:
                continue
            bins.setdefault((math.floor(la / G), math.floor(lo / G)), []).append((la, lo, ri[i // 2] if ri else -1))

    def ring_at(la, lo):
        best = None; bd = 450; A = math.floor(la / G); C = math.floor(lo / G)
        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                for q2 in bins.get((A + x, C + y), ()):
                    d = dist(la, lo, q2[0], q2[1])
                    if d < bd:
                        bd = d; best = q2[2]
        return best

    W = [e for e in js['elements'] if e.get('type') == 'way' and e.get('geometry') and len(e['geometry']) >= 2]
    key = lambda p: f"{p['lat']:.6f},{p['lon']:.6f}"
    par = list(range(len(W)))
    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    ends = {}
    for i, w in enumerate(W):
        for p in (w['geometry'][0], w['geometry'][-1]):
            k = key(p)
            if k in ends: par[f(i)] = f(ends[k])
            else: ends[k] = i
    grp = {}
    for i, w in enumerate(W):
        grp.setdefault(f(i), []).append(w)
    adj = {}
    def link(x, y):
        adj.setdefault(x, set()).add(y); adj.setdefault(y, set()).add(x)
    for ws in grp.values():
        ln = 0; cnt = {}
        for w in ws:
            g = w['geometry']
            for i in range(1, len(g)):
                ln += dist(g[i-1]['lat'], g[i-1]['lon'], g[i]['lat'], g[i]['lon'])
            for p in (g[0], g[-1]):
                k = key(p); c = cnt.setdefault(k, [0, p]); c[0] += 1
        if ln < 100:
            continue
        rs = set()
        for n, p in cnt.values():
            if n != 1: continue
            r = ring_at(p['lat'], p['lon'])
            if r is not None: rs.add(r)
        L2 = list(rs)
        for i in range(1, len(L2)): link(L2[0], L2[i])
    seen = {-1}; st = [-1]
    while st:
        x = st.pop()
        for y in adj.get(x, ()):
            if y not in seen: seen.add(y); st.append(y)
    seen.discard(-1)
    return sorted(seen), ''

all_ = json.load(open(os.path.join(a.assets, 'sgg.json'), encoding='utf-8'))
old = {}
if a.old and os.path.exists(a.old):
    try: old = json.load(open(a.old, encoding='utf-8')).get('sgg', {})
    except Exception: old = {}
out = {}; ok = 0; reused = 0; fail = []
today = datetime.date.today().isoformat()
for sg in all_:
    if not sg.get('is'):          # 섬이 없는 곳은 받을 필요 없음
        out[sg['c']] = {'r': [], 'd': today}; ok += 1; continue
    rs, err = rings_for(sg, all_)
    if rs is not None:
        out[sg['c']] = {'r': rs, 'd': today}; ok += 1
        print(f"{sg['s']} {sg['n']}: 다리 섬 {len(rs)}곳", flush=True)
    elif sg['c'] in old:
        out[sg['c']] = old[sg['c']]; reused += 1
        print(f"{sg['s']} {sg['n']}: 실패 → 지난 자료 씀 ({err})", flush=True)
    else:
        fail.append(sg['c']); print(f"{sg['s']} {sg['n']}: 실패 ({err})", flush=True)
    time.sleep(a.sleep)
json.dump({'made': today, 'sgg': out}, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'완료: 새로 {ok}, 지난 자료 {reused}, 실패 {len(fail)}')
