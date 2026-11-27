// 번들 수심 격자(depth_grid.json)와 index.html의 격자 보간 함수 검증.
// 물리 공식은 안 건드림 — 좌표→수심/육지 변환이 맞는지만 본다.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync('app/src/main/assets/index.html', 'utf8');
const G = JSON.parse(fs.readFileSync('app/src/main/assets/depth_grid.json', 'utf8'));

// index.html에서 순수 격자 함수들만 떼어 그대로 평가 (map 등 외부 의존 없음)
const start = html.indexOf('function depthGridCell(');
const end = html.indexOf('function simDepthFromGrid(');
assert.ok(start > 0 && end > start, '격자 함수 블록을 못 찾음');
const mod = {};
(function () {
  eval(html.slice(start, end) +
    '\nmod.depthGridCell=depthGridCell;mod.depthGridIsLand=depthGridIsLand;mod.depthGridDepth=depthGridDepth;');
})();
const depthGridCell = mod.depthGridCell, depthGridIsLand = mod.depthGridIsLand, depthGridDepth = mod.depthGridDepth;

let pass = 0, fail = 0;
const t = (name, fn) => { try { fn(); pass++; console.log('  OK  ' + name); }
  catch (e) { fail++; console.log('  X   ' + name + ' — ' + e.message); } };

const cx = j => G.lon0 + (j + 0.5) * G.dlon;   // 열 j 중심 경도
const cy = i => G.lat0 + (i + 0.5) * G.dlat;   // 행 i 중심 위도

// 1) 헤더 무결성
t('격자 크기 = data 길이', () => assert.equal(G.ncols * G.nrows, G.data.length));
t('기준면 MSL', () => assert.equal(G.datum, 'MSL'));

// 2) 셀 중심에서 depthGridDepth == 그 셀 값(바다 셀)
t('바다 셀 중심은 원래 값과 거의 같음', () => {
  let got = 0;
  for (let i = 0; i < G.nrows && got < 50; i++) for (let j = 0; j < G.ncols && got < 50; j++) {
    const v = G.data[i * G.ncols + j];
    if (v == null || v === G.land) continue;
    const d = depthGridDepth(G, cy(i), cx(j));
    assert.ok(Math.abs(d - v) < 1e-6, `셀(${i},${j}) ${v} vs ${d}`);
    got++;
  }
  assert.ok(got > 10, '검사한 바다 셀이 너무 적음');
});

// 3) 육지 셀은 land로 판정되고, depth 보간은 주변 바다만 쓰거나 null
t('육지 셀은 depthGridIsLand=true', () => {
  let got = 0;
  for (let i = 0; i < G.nrows && got < 30; i++) for (let j = 0; j < G.ncols && got < 30; j++) {
    if (G.data[i * G.ncols + j] !== G.land) continue;
    assert.equal(depthGridIsLand(G, cy(i), cx(j)), true);
    got++;
  }
  assert.ok(got > 5, '육지 셀 표본 부족');
});

// 4) 범위 밖은 undefined / null
t('격자 밖 셀은 undefined, 깊이 null', () => {
  assert.equal(depthGridCell(G, 34.0, 127.0), undefined);
  assert.equal(depthGridDepth(G, 34.0, 127.0), null);
  assert.equal(depthGridCell(G, 36.0, 129.0), undefined);
});

// 5) 이중선형: 두 바다 셀 사이 중간점은 두 값 사이
t('인접 바다 셀 중간점은 두 값 사이', () => {
  let got = 0;
  for (let i = 0; i < G.nrows && got < 20; i++) for (let j = 0; j < G.ncols - 1 && got < 20; j++) {
    const a = G.data[i * G.ncols + j], b = G.data[i * G.ncols + j + 1];
    if (a == null || a === G.land || b == null || b === G.land) continue;
    const mid = depthGridDepth(G, cy(i), (cx(j) + cx(j + 1)) / 2);
    const lo = Math.min(a, b) - 1e-6, hi = Math.max(a, b) + 1e-6;
    assert.ok(mid >= lo && mid <= hi, `중간 ${mid} ∉ [${a},${b}]`);
    got++;
  }
  assert.ok(got > 5, '인접 바다쌍 표본 부족');
});

// 6) 간출/육지경계 음수 수심도 그대로 보간 (부호 안 바뀜)
t('수심 부호 유지(양수=깊이)', () => {
  const sea = G.data.filter(v => v != null && v !== G.land);
  assert.ok(Math.max(...sea) > 20, '깊은 곳이 양수여야 함');
});

// ── simDepthFromGrid(격자→바닥 마찰 kz) 직접 검증 (헤드리스 sim 워커 없이) ──
// 웹 메르카토르 project/unproject (Leaflet과 동일: zoom z에서 world=256*2^z)
const SC = 12, FIELD_LEVEL = 15, WS = 256 * 2 ** FIELD_LEVEL;
const project = (lat, lon) => {
  const s = Math.sin(lat * Math.PI / 180);
  return {x: (lon + 180) / 360 * WS, y: (0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)) * WS};
};
const unproject = (p) => {
  const x = Array.isArray(p) ? p[0] : p.x, y = Array.isArray(p) ? p[1] : p.y;
  const lon = x / WS * 360 - 180, n = Math.PI - 2 * Math.PI * y / WS;
  return {lng: lon, lat: 180 / Math.PI * Math.atan(0.5 * (Math.exp(n) - Math.exp(-n)))};
};
const env = {map: {unproject: (p) => unproject(p)}, SC, FIELD_LEVEL,
  depthGridDepth, depthGridIsLand,
  DEPTH: {cache: new Map(), last: '', gridCells: 0}};
const fromGridSrc = html.slice(html.indexOf('function simDepthFromGrid('), html.indexOf('async function simDepthWait('));
const simDepthFromGrid = new Function('map', 'SC', 'depthGridDepth', 'DEPTH',
  fromGridSrc + '\nreturn simDepthFromGrid;')(env.map, env.SC, depthGridDepth, env.DEPTH);

// 사천 바다 한가운데를 덮는 합성 타일 (34.90~34.93, 128.05~128.09 근처)
function makeTile(lat, lon, g) {
  const topLeft = project(lat + 0.5 * g * 0.0000085 * 0, lon); // 대략 중심 기준
  const c = project(lat, lon);
  const ox = Math.round(c.x - g / 2 * SC), oy = Math.round(c.y - g / 2 * SC);
  const T = {gx: g, gy: g, ox, oy, lv: FIELD_LEVEL, key: 'test:' + lat + ',' + lon, solid: new Uint8Array(g * g)};
  // 격자상 육지인 칸은 solid로 표시(실제 simBuildTile의 육지 보강과 같은 판정)
  let landCnt = 0;
  for (let i = 0; i < g * g; i++) {
    const X = i % g, Y = (i / g) | 0, ll = unproject([ox + (X + 0.5) * SC, oy + (Y + 0.5) * SC]);
    if (depthGridIsLand(G, ll.lat, ll.lng)) { T.solid[i] = 1; landCnt++; }
  }
  return {T, landCnt};
}

t('simDepthFromGrid: 격자로 kz 생성·깊이에 따라 다름', () => {
  const {T} = makeTile(34.915, 128.06, 40);
  simDepthFromGrid(T, G);
  assert.equal(env.DEPTH.last, '격자', 'DEPTH.last가 격자여야');
  assert.ok(T.kz && T.kz.length === T.gx * T.gy, 'kz 배열 생성');
  let pos = 0, water = 0, mx = 0;
  for (let i = 0; i < T.kz.length; i++) { if (T.solid[i]) continue; water++; if (T.kz[i] > 0) pos++; if (T.kz[i] > mx) mx = T.kz[i]; }
  assert.ok(water > 20, '물칸 충분: ' + water);
  assert.ok(mx > 0, '마찰 최대값 > 0');
  assert.ok(pos < water, '일부 깊은 칸은 마찰 0 (깊이 따라 다름): pos=' + pos + '/' + water);
  assert.ok(T.hmed > 0, 'hmed > 0');
});

t('simDepthFromGrid: 얕은 칸 마찰 ≥ 깊은 칸 (공식 단조성, 실제 격자값)', () => {
  const {T} = makeTile(34.915, 128.06, 40);
  simDepthFromGrid(T, G);
  // 각 물칸의 실제 격자 수심을 다시 구해, 가장 얕은/깊은 칸의 kz 비교
  let shLat, shLon, shD = 1e9, dpD = -1, shI = -1, dpI = -1;
  for (let i = 0; i < T.kz.length; i++) {
    if (T.solid[i]) continue;
    const X = i % T.gx, Y = (i / T.gx) | 0, ll = unproject([T.ox + (X + 0.5) * SC, T.oy + (Y + 0.5) * SC]);
    const d = depthGridDepth(G, ll.lat, ll.lng); if (d == null) continue;
    if (d < shD) { shD = d; shI = i; } if (d > dpD) { dpD = d; dpI = i; }
  }
  assert.ok(shI >= 0 && dpI >= 0 && dpD > shD, '얕은/깊은 칸 확보');
  assert.ok(T.kz[shI] >= T.kz[dpI] - 1e-9, `얕은칸 kz(${T.kz[shI]},${shD}m) ≥ 깊은칸 kz(${T.kz[dpI]},${dpD}m)`);
});

t('육지 보강: 격자 육지 칸이 solid로 잡힘', () => {
  // 해안에 걸치는 타일을 골라 육지 칸이 실제로 있는지
  const {landCnt} = makeTile(34.95, 128.03, 50);
  assert.ok(landCnt > 0, '해안 타일에서 격자 육지 칸이 벽으로 잡혀야: ' + landCnt);
});

console.log(`\n수심격자 시험: ${pass} 통과, ${fail} 실패`);
process.exit(fail ? 1 : 0);
