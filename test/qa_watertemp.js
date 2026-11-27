// 수온 알고리즘 검증 (T-001 창선도: 섬 건너편 섞임·확대 수준 의존·관측소 경계 계단·위성 칸 계단)
// index.html의 수온 함수를 그대로 떼어 실제 육지 칸(번들 수심 타일)과 가짜 ROMS 점으로 평가한다.
// 타일은 TILES_DIR에서 읽음 — 창선도 둘레(127.5~128.6E, 34.4~35.3N)가 있어야 함:
//   python3 tools/make_depth_tiles.py --out <TILES_DIR> --bbox 127.5 34.4 128.6 35.3   (BADA 원본은 git lfs pull)
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync('app/src/main/assets/index.html', 'utf8');
const TILES_DIR = process.env.TILES_DIR || '/tmp/claude-0/-home-user/f66aeebd-2121-50cc-a842-099770923ef8/scratchpad/depthtiles';
if (!fs.existsSync(path.join(TILES_DIR, 'index.json'))) { console.log('테스트 타일 없음(' + TILES_DIR + ') → 건너뜀. make_depth_tiles.py로 생성'); process.exit(0); }
const G = JSON.parse(fs.readFileSync(path.join(TILES_DIR, 'index.json'), 'utf8')); G.set = new Set(G.tiles);
const cut = (a, b) => { const i = html.indexOf(a), j = html.indexOf(b, i); assert.ok(i > 0 && j > i, '못 찾음: ' + a); return html.slice(i, j); };

// ── 앱 쪽 환경 흉내 ──
const KX = 0.82;
const RD = { pts: [], bins: new Map(), R: 0.033, ver: 1, times: [0] };
const DGRID = { index: G, blocks: new Map() }; const depthGridReady = () => {}; const blkEnsure = () => Promise.resolve(null);
for (const key of G.tiles) DGRID.blocks.set(key, JSON.parse(fs.readFileSync(path.join(TILES_DIR, key + '.json'), 'utf8')));
const timeIdx = () => ({ i: 0, f: 0, out: false });
const t0 = new Date(Date.UTC(2026, 10, 27, 3, 0, 0)); // 12:00 KST
const DTO = { st: [] }, WT = { obs: new Map(), pend: new Set() };
const distM = (a1, o1, a2, o2) => { const r = Math.PI / 180, x = (o2 - o1) * r * Math.cos((a1 + a2) / 2 * r), y = (a2 - a1) * r; return Math.hypot(x, y) * 6371e3; };
const SST = { g: null }; const sstDay = () => '11/26';
eval(cut('const blkKeyOf=', '// 블록 비동기 로드').replace('const blkKeyOf', 'var blkKeyOf')); eval(cut('function cellAt(', '// 가장자리 땅 칸은'));
var WT_P; eval(cut('const WT_P=', 'WT={obs').replace('const WT_P=', 'WT_P=').replace(/,\s*$/, ';'));
eval(cut('const TEMP_RD=', '// 하루 사이 수온 변화').replace('const TEMP_RD', 'var TEMP_RD'));
eval(cut('function wtNearAll(', 'function wtObsMs('));
eval(cut('function wtObsMs(', '// 관측−예보 차이를'));
eval(cut('function wtemp(', 'const wtText='));
eval(cut('function sstAt(', 'function sstSet('));

let pass = 0, fail = 0;
const t = (name, fn) => { try { const r = fn(); pass++; console.log('  OK  ' + name + (r ? ' — ' + r : '')); }
  catch (e) { fail++; console.log('  X   ' + name + ' — ' + e.message); } };

// 가짜 ROMS 점 (실제 응답 간격 0.029°×0.031°), 육지 칸엔 점 없음. 수온 = f(위치)
const isLand = (la, lo) => depthGridIsLand(G, la, lo);
function setPts(f, box = [34.55, 35.15, 127.80, 128.45], R = 0.033) {
  RD.pts = []; RD.bins = new Map(); RD.R = R; RD.ver++;
  for (let la = box[0]; la < box[1]; la += 0.029) for (let lo = box[2]; lo < box[3]; lo += 0.031) {
    if (isLand(la, lo)) continue; const p = { lat: la, lon: lo, w: [f(la, lo)] }; RD.pts.push(p);
    const k = Math.floor(la / R) + ',' + Math.floor(lo / R); (RD.bins.get(k) || RD.bins.set(k, []).get(k)).push(p);
  }
}
const rebin = R => { const pts = RD.pts; RD.bins = new Map(); RD.R = R; RD.ver++; for (const p of pts) { const k = Math.floor(p.lat / R) + ',' + Math.floor(p.lon / R); (RD.bins.get(k) || RD.bins.set(k, []).get(k)).push(p); } };
// 독립 판정: 두 점 사이 직선이 100m 넘게 이어진 육지(섬·반도)를 지나는가 (양 끝 300m 제외, 25m 간격).
// 격자 한 칸 모서리를 스치는 것(바위·칸 모양)은 물을 가르는 땅이 아니라 셈하지 않음
function crossesStrict(a1, o1, a2, o2) { const L = Math.hypot((a2 - a1) * 111e3, (o2 - o1) * 111e3 * KX), n = Math.ceil(L / 25); let run = 0;
  for (let s = 1; s < n; s++) { const u = s / n; if (Math.min(u, 1 - u) * L < 300) { run = 0; continue; }
    if (isLand(a1 + (a2 - a1) * u, o1 + (o2 - o1) * u)) { if (++run * L / n >= 100) return true; } else run = 0; } return false; }

const probes = { '서쪽 강진만 쪽': [34.890, 127.955], '북쪽 삼천포 해협': [34.935, 128.020], '창선 가운데 만': [34.900, 128.025], '동쪽 사천만 바깥': [34.880, 128.090], '남동쪽': [34.850, 128.100] };
for (const [n, [la, lo]] of Object.entries(probes)) assert.ok(!isLand(la, lo), n + ' 가 육지');

console.log('[A] 섬 건너편 차단 · 확대 수준과 무관');
setPts((la, lo) => 15 + (lo - 128) * 10); // 부드러운 수온(경도 0.1°당 1℃)
t('창선도 둘레 5곳: 쓰는 점 중 섬을 건너는 점 0개', () => {
  for (const R of [0.033, 0.08, 0.2]) { rebin(R);
    for (const [n, [la, lo]] of Object.entries(probes)) {
      const bad = tempNbrs(la, lo).filter(p => crossesStrict(Math.round(la * 500) / 500, Math.round(lo * 500) / 500, p.lat, p.lon));
      assert.equal(bad.length, 0, `${n} R=${R}: 건너는 점 ${bad.length}`); } }
});
t('같은 자리 수온이 확대 수준(R 0.033/0.08/0.2)에 따라 안 바뀜(차 < 0.01℃)', () => {
  const o = [];
  for (const [n, [la, lo]] of Object.entries(probes)) {
    const v = [0.033, 0.08, 0.2].map(R => { rebin(R); return tempAt(la, lo, 0); });
    assert.ok(v.every(x => x != null), n + ' 값 없음');
    const d = Math.max(...v) - Math.min(...v); assert.ok(d < 0.01, `${n}: ${v.map(x => x.toFixed(2))}`); o.push(n.split(' ')[0] + ' ' + v[0].toFixed(2));
  } return o.join(', ');
});
t('창선도 둘레 바다 칸에서 수온이 비는 곳 3% 미만', () => {
  rebin(0.033); let n = 0, nul = 0;
  for (let la = 34.83; la < 34.96; la += 0.004) for (let lo = 127.93; lo < 128.12; lo += 0.004) { if (isLand(la, lo)) continue; n++; if (tempAt(la, lo, 0) == null) nul++; }
  assert.ok(nul / n < 0.03, `${nul}/${n}`); return `${nul}/${n}칸`;
});
t('계단 수온(강진만 13℃ / 그 밖 16℃)에서 동쪽 바다는 16℃ 그대로', () => {
  setPts((la, lo) => (lo < 127.975 && la > 34.84) ? 13 : 16);
  for (const R of [0.033, 0.08, 0.2]) { rebin(R); const v = tempAt(34.880, 128.090, 0); assert.ok(Math.abs(v - 16) < 1e-9, `R=${R}: ${v}`); }
});

console.log('[B] 관측소 보정: 경계 계단 없음');
setPts(() => 15, [33.65, 33.95, 127.95, 128.45]); rebin(0.033); // 타일 밖(육지 판단 없음) 균일 15℃
const ST = (c, la, lo) => ({ c, la, lo, n: c });
const obs = (st, v) => WT.obs.set(st.c, { o: { wtem: v, at: '2026-11-27 12:00', la: st.la, lo: st.lo, sc: st.c }, at: Date.now() });
const A = ST('A', 33.80, 128.05), B = ST('B', 33.80, 128.35);
t('관측소 하나: 예전(U-49) 식과 같음', () => {
  DTO.st = [A]; WT.obs.clear(); obs(A, 17);
  const w = wtemp(33.80, 128.12, 0), d = distM(33.80, 128.12, A.la, A.lo) / 1000, K = Math.exp(-((d / 15) ** 2)) * 0.8;
  assert.ok(Math.abs(w.v - (15 + K * 2)) < 1e-9, `${w.v} vs ${15 + K * 2}`); return `${d.toFixed(1)}km, ${w.v.toFixed(3)}℃`;
});
t('두 관측소(17℃/14℃) 사이를 100m씩 걸어도 한 걸음 변화 < 0.05℃', () => {
  DTO.st = [A, B]; WT.obs.clear(); obs(A, 17); obs(B, 14); let prev = null, mx = 0;
  for (let lo = 128.06; lo <= 128.34; lo += 0.0011) { const v = wtemp(33.80, lo, 0).v; if (prev != null) mx = Math.max(mx, Math.abs(v - prev)); prev = v; }
  // 예전 식(가장 가까운 한 곳)이었다면 가운데에서 계단: K(13.7km)×3℃
  const dm = distM(33.80, 128.20, A.la, A.lo) / 1000, old = Math.exp(-((dm / 15) ** 2)) * 0.8 * 3;
  assert.ok(mx < 0.05, `최대 ${mx.toFixed(3)}`); return `최대 ${mx.toFixed(3)}℃ (예전 식이면 가운데 ${old.toFixed(2)}℃ 계단)`;
});
t('섬 건너편 관측소는 안 씀(창선 동쪽 바다 ↔ 강진만 안쪽 관측소)', () => {
  setPts(() => 15); rebin(0.033);
  const W = ST('W', 34.905, 127.935); DTO.st = [W]; WT.obs.clear(); obs(W, 18);
  assert.ok(!isLand(W.la, W.lo)); const w = wtemp(34.880, 128.090, 0); assert.equal(w.src, '예보', '섬 너머 관측소를 섞음');
});

console.log('[D] 위성 수온 칸 보간');
SST.g = { las: [34.80, 34.81, 34.82], los: [128.00, 128.01, 128.02], nx: 3, ny: 3, v: new Float32Array([10, 12, 14, 11, 13, 15, NaN, NaN, NaN]) };
t('칸 중심 = 그 칸 값', () => { assert.ok(Math.abs(sstAt(34.81, 128.01).t - 13) < 1e-6); });
t('두 칸 가운데 = 평균', () => { assert.ok(Math.abs(sstAt(34.80, 128.005).t - 11) < 1e-6); });
t('한쪽이 NaN이면 남은 칸 값', () => { const r = sstAt(34.815, 128.01); assert.ok(Math.abs(r.t - 13) < 1e-6, String(r.t)); });
t('범위 밖(0.02° 넘음)은 null', () => { assert.equal(sstAt(34.70, 128.01), null); });

console.log(`\n${pass} 통과, ${fail} 실패`); process.exit(fail ? 1 : 0);
