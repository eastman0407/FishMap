// 번들 수심 격자(타일식)와 index.html의 격자 함수 검증. 물리 공식은 안 건드림.
// 좌표→수심/육지 변환, 블록 경계 넘는 이중선형, 격자→바닥 마찰(simDepthFromGrid)을 본다.
// 테스트 타일은 TILES_DIR(기본 scratchpad/depthtiles)에서 읽는다 — 없으면 건너뜀.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync('app/src/main/assets/index.html', 'utf8');

const TILES_DIR = process.env.TILES_DIR ||
  '/tmp/claude-0/-home-user/cbc7023a-6de0-5234-968b-22b5be54049f/scratchpad/depthtiles';
if (!fs.existsSync(path.join(TILES_DIR, 'index.json'))) {
  console.log('테스트 타일 없음(' + TILES_DIR + ') → 건너뜀. make_depth_tiles.py로 생성'); process.exit(0);
}
const G = JSON.parse(fs.readFileSync(path.join(TILES_DIR, 'index.json'), 'utf8'));
G.set = new Set(G.tiles);

// index.html에서 타일 격자 함수들만 떼어 평가 (DGRID·map 주입)
const start = html.indexOf('const blkKeyOf=');
const end = html.indexOf('// 이 계산 구역(+1셀 여유)');
assert.ok(start > 0 && end > start, '격자 함수 블록을 못 찾음');
const DGRID = { blocks: new Map(), land: G.land };
for (const key of G.tiles) DGRID.blocks.set(key, JSON.parse(fs.readFileSync(path.join(TILES_DIR, key + '.json'), 'utf8')));
const mod = {};
(function () {
  eval(html.slice(start, end) +
    '\nmod.cellAt=cellAt;mod.depthGridIsLand=depthGridIsLand;mod.depthGridDepth=depthGridDepth;mod.blkKeyOf=blkKeyOf;');
})();
const { cellAt, depthGridIsLand, depthGridDepth, blkKeyOf } = mod;

let pass = 0, fail = 0;
const t = (name, fn) => { try { fn(); pass++; console.log('  OK  ' + name); }
  catch (e) { fail++; console.log('  X   ' + name + ' — ' + e.message); } };

const cx = J => G.glon0 + (J + 0.5) * G.dlon;   // 전역 열 J 중심 경도
const cy = I => G.glat0 + (I + 0.5) * G.dlat;    // 전역 행 I 중심 위도
// 어떤 타일의 전역 (I,J) 범위
const some = DGRID.blocks.get(G.tiles[0]);
const J0 = some.bx * G.bc, I0 = some.by * G.br;

t('index 헤더: tiles·격자 파라미터', () => assert.ok(G.tiles.length && G.dlon && G.bc && G.br));

t('타일 셀 중심 == depthGridDepth(바다 셀)', () => {
  let got = 0;
  for (const key of G.tiles) { const tl = DGRID.blocks.get(key);
    for (let li = 0; li < G.br && got < 60; li += 7) for (let lj = 0; lj < G.bc && got < 60; lj += 7) {
      const v = tl.data[li * G.bc + lj]; if (v == null || v === G.land) continue;
      const I = tl.by * G.br + li, J = tl.bx * G.bc + lj;
      const d = depthGridDepth(G, cy(I), cx(J));
      assert.ok(Math.abs(d - v) < 1e-6, `셀(${I},${J}) ${v} vs ${d}`); got++; } }
  assert.ok(got > 20, '검사한 바다 셀 부족: ' + got);
});

t('cellAt: 전역 인덱스로 원래 값 반환', () => {
  const tl = some; let got = 0;
  for (let li = 0; li < G.br && got < 20; li += 11) for (let lj = 0; lj < G.bc && got < 20; lj += 11) {
    assert.equal(cellAt(G, tl.by * G.br + li, tl.bx * G.bc + lj), tl.data[li * G.bc + lj]); got++; }
});

t('육지 셀 depthGridIsLand=true', () => {
  let got = 0;
  for (const key of G.tiles) { const tl = DGRID.blocks.get(key);
    for (let i = 0; i < tl.data.length && got < 30; i++) if (tl.data[i] === G.land) {
      const I = tl.by * G.br + ((i / G.bc) | 0), J = tl.bx * G.bc + (i % G.bc);
      assert.equal(depthGridIsLand(G, cy(I), cx(J)), true); got++; } }
  assert.ok(got > 5, '육지 셀 표본 부족');
});

t('로드 안 된/범위 밖 블록은 undefined, 깊이 null', () => {
  assert.equal(cellAt(G, -5, -5), undefined);
  assert.equal(cellAt(G, I0, J0 - 99999), undefined);          // 아주 먼 열(로드 안 된 블록)
  assert.equal(depthGridDepth(G, 10.0, 100.0), null);
});

t('블록 경계를 넘는 이중선형(전역 인덱스 연속)', () => {
  // 서로 이웃한 두 타일을 찾아, 그 경계 열에서 좌우 셀이 둘 다 바다인 지점의 중간값 확인
  let done = false;
  for (const key of G.tiles) { const [bx, by] = key.split('_').map(Number);
    if (!G.set.has((bx + 1) + '_' + by)) continue;             // 동쪽 이웃 있음
    const Jb = (bx + 1) * G.bc;                                 // 경계 전역 열
    for (let li = 0; li < G.br && !done; li++) { const I = by * G.br + li;
      const a = cellAt(G, I, Jb - 1), b = cellAt(G, I, Jb);     // 서쪽 끝 / 동쪽 첫 칸(다른 타일)
      if (a == null || a === G.land || b == null || b === G.land) continue;
      const mid = depthGridDepth(G, cy(I), (cx(Jb - 1) + cx(Jb)) / 2);
      const lo = Math.min(a, b) - 1e-6, hi = Math.max(a, b) + 1e-6;
      assert.ok(mid >= lo && mid <= hi, `경계 중간 ${mid} ∉ [${a},${b}] (타일 ${key}↔${bx+1}_${by})`);
      done = true; } }
  assert.ok(done, '인접 두 타일의 바다 경계쌍을 못 찾음(테스트 타일 배치 확인)');
});

// ── simDepthFromGrid 직접 검증 (헤드리스 sim 워커 없이) ──
const SC = 12, FIELD_LEVEL = 15, WS = 256 * 2 ** FIELD_LEVEL;
const project = (lat, lon) => { const s = Math.sin(lat * Math.PI / 180);
  return { x: (lon + 180) / 360 * WS, y: (0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)) * WS }; };
const unproject = p => { const x = Array.isArray(p) ? p[0] : p.x, y = Array.isArray(p) ? p[1] : p.y;
  const lon = x / WS * 360 - 180, n = Math.PI - 2 * Math.PI * y / WS;
  return { lng: lon, lat: 180 / Math.PI * Math.atan(0.5 * (Math.exp(n) - Math.exp(-n))) }; };
const env = { map: { unproject }, SC, depthGridDepth, DEPTH: { cache: new Map(), last: '', gridCells: 0 } };
const fromGridSrc = html.slice(html.indexOf('function simDepthFromGrid('), html.indexOf('async function simDepthWait('));
const simDepthFromGrid = new Function('map', 'SC', 'depthGridDepth', 'DEPTH',
  fromGridSrc + '\nreturn simDepthFromGrid;')(env.map, env.SC, depthGridDepth, env.DEPTH);

// 로드된 타일 중앙 좌표로 합성 계산 구역 만들기
const ctrI = some.by * G.br + G.br / 2, ctrJ = some.bx * G.bc + G.bc / 2;
function makeTile(lat, lon, g) {
  const c = project(lat, lon), ox = Math.round(c.x - g / 2 * SC), oy = Math.round(c.y - g / 2 * SC);
  const T = { gx: g, gy: g, ox, oy, lv: FIELD_LEVEL, key: 'test:' + lat + ',' + lon, solid: new Uint8Array(g * g) };
  let land = 0;
  for (let i = 0; i < g * g; i++) { const X = i % g, Y = (i / g) | 0, ll = unproject([ox + (X + 0.5) * SC, oy + (Y + 0.5) * SC]);
    if (depthGridIsLand(G, ll.lat, ll.lng)) { T.solid[i] = 1; land++; } }
  return { T, land };
}
t('simDepthFromGrid: 타일에서 kz 생성·깊이 따라 다름', () => {
  const { T } = makeTile(cy(ctrI), cx(ctrJ), 40); simDepthFromGrid(T, G);
  assert.equal(env.DEPTH.last, '격자');
  let water = 0, mx = 0, mn = Infinity;
  for (let i = 0; i < T.kz.length; i++) { if (T.solid[i]) continue; water++; if (T.kz[i] > mx) mx = T.kz[i]; if (T.kz[i] < mn) mn = T.kz[i]; }
  assert.ok(water > 20 && mx > 0 && mx > mn, `물칸·마찰 변화 있어야: water=${water} mx=${mx} mn=${mn}`); // 깊이 따라 다름
});
t('simDepthFromGrid: 얕은 칸 마찰 ≥ 깊은 칸(실제 격자값 단조성)', () => {
  const { T } = makeTile(cy(ctrI), cx(ctrJ), 40); simDepthFromGrid(T, G);
  let shD = 1e9, dpD = -1, shI = -1, dpI = -1;
  for (let i = 0; i < T.kz.length; i++) { if (T.solid[i]) continue;
    const X = i % T.gx, Y = (i / T.gx) | 0, ll = unproject([T.ox + (X + 0.5) * SC, T.oy + (Y + 0.5) * SC]);
    const d = depthGridDepth(G, ll.lat, ll.lng); if (d == null) continue;
    if (d < shD) { shD = d; shI = i; } if (d > dpD) { dpD = d; dpI = i; } }
  assert.ok(shI >= 0 && dpI >= 0 && dpD > shD, '얕은/깊은 칸 확보');
  assert.ok(T.kz[shI] >= T.kz[dpI] - 1e-9, `얕은칸 kz(${T.kz[shI]},${shD}m) ≥ 깊은칸(${T.kz[dpI]},${dpD}m)`);
});

console.log(`\n수심격자(타일) 시험: ${pass} 통과, ${fail} 실패`);
process.exit(fail ? 1 : 0);
