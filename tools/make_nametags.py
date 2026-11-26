#!/usr/bin/env python3
# 화면·기능 이름표 이미지 생성 (검토 5, build-77~): 앱 HTML을 Chromium으로 띄워 주요 화면을 캡처해
# docs/이름표/*.png 로 저장한다. docs/이름표.md 가 이 이미지를 표와 함께 보여준다(깃허브 인라인 렌더).
# 사용: python3 tools/make_nametags.py   (Chromium 필요, 네트워크 불필요 — 지도 타일은 바다색으로 대체)
import os, sys, http.server, socketserver, threading, shutil, tempfile, base64, functools
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, 'app/src/main/assets')
OUT = os.path.join(ROOT, 'docs/이름표')
os.makedirs(OUT, exist_ok=True)
SITE = tempfile.mkdtemp()
for f in os.listdir(A):
    if f.endswith(('.html', '.json')):
        shutil.copy(os.path.join(A, f), SITE)

PORT = 8771
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE)
httpd = socketserver.TCPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

BRIDGE = ("window.AndroidBridge={_p:{},getPref(k){return this._p[k]||''},setPref(k,v){this._p[k]=v},"
          "dropCache(){},clearCache(){},shareText(){},httpGet(u,id){setTimeout(()=>window.__nativeCb(id,200,'{}'),4)}};")
TILE = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')

def route(r):
    u = r.request.url
    if u.startswith(f'http://127.0.0.1:{PORT}') or u.endswith('.js') and 'leaflet' in u:
        return r.continue_()
    if any(u.endswith(e) for e in ('.png', '.jpg', '.jpeg')) or any(s in u for s in ('tile', 'vworld', 'arcgis')):
        return r.fulfill(body=TILE, content_type='image/png', headers={'Access-Control-Allow-Origin': '*'})
    return r.continue_()

shots = []
with sync_playwright() as p:
    br = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = br.new_page(viewport={'width': 411, 'height': 760}, device_scale_factor=2)
    pg.add_init_script(BRIDGE)
    pg.route('**/*', route)
    pg.goto(f'http://127.0.0.1:{PORT}/index.html', wait_until='domcontentloaded')
    pg.wait_for_function("document.getElementById('nowCard')", timeout=8000)
    pg.wait_for_timeout(1800)
    # 1) 메인 화면 (검색·지도 중심·지금 카드·네 도구 아이콘)
    pg.screenshot(path=os.path.join(OUT, '1_메인화면.png'), clip={'x': 0, 'y': 0, 'width': 411, 'height': 300})
    shots.append('1_메인화면.png')
    # 2) 지도 보기 시트 (P1): 지도 종류·레이어 토글
    pg.evaluate("document.getElementById('layersBtn').click()")
    pg.wait_for_timeout(500)
    pg.screenshot(path=os.path.join(OUT, '2_지도보기시트.png'), clip={'x': 0, 'y': 300, 'width': 411, 'height': 460})
    shots.append('2_지도보기시트.png')
    pg.evaluate("window.__onBack&&window.__onBack()")
    pg.wait_for_timeout(300)
    # 3) 설정 (P2): 글자 크기·화면 모드·물때 등
    pg.evaluate("document.getElementById('layersBtn').click()")
    pg.wait_for_timeout(300)
    pg.evaluate("document.getElementById('setBtn').click()")
    pg.wait_for_timeout(500)
    pg.screenshot(path=os.path.join(OUT, '3_설정.png'), full_page=False)
    shots.append('3_설정.png')
    br.close()
httpd.shutdown()
print('이름표 이미지 생성:', OUT)
for s in shots:
    print(' -', s)
