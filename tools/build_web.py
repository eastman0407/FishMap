#!/usr/bin/env python3
"""물흐름 지도 HTML 한 파일 버전 만들기 (REQ-50).
앱의 assets/index.html + Leaflet + 바위·갯벌·행정구역 자료를 fishmap.html 하나로 합친다.
사용: python3 tools/build_web.py --assets app/src/main/assets --version 1.30 --out dist/fishmap.html
      [--leaflet-js 경로] [--leaflet-css 경로]   (기본: assets/lib/leaflet.min.*)
"""
import argparse, base64, json, os, re, sys

ap = argparse.ArgumentParser()
ap.add_argument('--assets', default='app/src/main/assets')
ap.add_argument('--version', default='')
ap.add_argument('--out', default='dist/fishmap.html')
ap.add_argument('--leaflet-js'); ap.add_argument('--leaflet-css')
a = ap.parse_args()

A = a.assets
html = open(os.path.join(A, 'index.html'), encoding='utf-8').read()
ljs = a.leaflet_js or os.path.join(A, 'lib', 'leaflet.min.js')
lcss = a.leaflet_css or os.path.join(A, 'lib', 'leaflet.min.css')
js = open(ljs, encoding='utf-8').read()
css = open(lcss, encoding='utf-8').read() if os.path.exists(lcss) else ''
img_dir = os.path.join(os.path.dirname(lcss), 'images')
def data_uri(m):
    p = os.path.join(img_dir, m.group(1))
    if not os.path.exists(p): return m.group(0)
    return 'url(data:image/png;base64,%s)' % base64.b64encode(open(p, 'rb').read()).decode()
css = re.sub(r'url\(images/([^)]+)\)', data_uri, css)

safe = lambda t: t.replace('</', '<\\/')  # 스크립트 안에서 </script> 끊김 방지
head_old = re.search(r'<link rel="stylesheet" href="lib/leaflet\.min\.css"[^>]*>\s*<script src="lib/leaflet\.min\.js"></script>\s*<script>if\(!window\.L\)[^\n]*</script>', html)
if not head_old: sys.exit('Leaflet 불러오는 부분을 못 찾음')
emb = {n: json.load(open(os.path.join(A, n), encoding='utf-8')) for n in ('rocks.json', 'tidal.json', 'sgg.json', 'fishing-spots.json')}
# 번들 수심 격자(타일식, BADA2024): 웹 단일 HTML엔 전국을 다 못 넣으므로 남해안 범위만 임베드.
# 앱(APK)은 assets/depth 전체를 그때그때 읽음. 웹은 임베드한 타일만 쓰고 나머지는 수심 없음.
_DEPTH = os.path.join(A, 'depth')
if os.path.exists(os.path.join(_DEPTH, 'index.json')):
    WB = (127.0, 33.9, 129.4, 35.3)  # 웹 임베드 범위(남해안): W,S,E,N
    idx = json.load(open(os.path.join(_DEPTH, 'index.json'), encoding='utf-8'))
    glon0, glat0, dlon, dlat, bc, br = idx['glon0'], idx['glat0'], idx['dlon'], idx['dlat'], idx['bc'], idx['br']
    keep = []
    for key in idx['tiles']:
        bx, by = map(int, key.split('_'))
        tw, te = glon0 + bx * bc * dlon, glon0 + (bx + 1) * bc * dlon
        ts, tn = glat0 + by * br * dlat, glat0 + (by + 1) * br * dlat
        if te >= WB[0] and tw <= WB[2] and tn >= WB[1] and ts <= WB[3]:
            keep.append(key)
    webidx = dict(idx); webidx['tiles'] = keep
    emb['depth/index.json'] = webidx
    for key in keep:
        emb['depth/' + key + '.json'] = json.load(open(os.path.join(_DEPTH, key + '.json'), encoding='utf-8'))
if os.path.exists(os.path.join(A, 'bridges.json')):  # REQ-60 섬 다리 자료 (CI에서 만듦)
    emb['bridges.json'] = json.load(open(os.path.join(A, 'bridges.json'), encoding='utf-8'))
new_head = ('<style>' + css + '</style>\n<script>' + safe(js) + '</script>\n'
            '<script>window.__WEBVER=' + json.dumps(a.version) + ';window.__EMBED=' + safe(json.dumps(emb, ensure_ascii=False, separators=(',', ':'))) + ';</script>')
html = html[:head_old.start()] + new_head + html[head_old.end():]
html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="theme-color" content="#0a1520">', 1)
os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
open(a.out, 'w', encoding='utf-8').write(html)
print('만듦:', a.out, round(len(html.encode()) / 1024), 'KB')
