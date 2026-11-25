// Runs the app's sampler against completed, pending and land-overlap fixtures.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync('app/src/main/assets/index.html', 'utf8');
const start = html.indexOf('function currentTileAt(');
const end = html.indexOf('function flowDraw(', start);
const SC = 12, DOM = 171 * SC, STRIDE = DOM - 24 * SC, FS = 3, FIELD_LEVEL = 15;
const SIM = {tiles: new Map()}, CONF = {realData: true}, ROMS = {run: 1}, sT = () => 620;
const baseAt = () => ({vE: 1, vN: 0});
const sample = eval(html.slice(start, end) + '\ncurrentAtWorld');
function tile(ix, iy, east, north) {
  const length = 171 * 171;
  const result = {
    state: 'ready', ox: ix * STRIDE, oy: iy * STRIDE, gx: 171,
    solid: new Uint8Array(length), wantedHash: 1, resultRun: 1,
    cur: {done: true, t: 620, h: 1, scale: 1,
      u: new Float32Array(length).fill(east), v: new Float32Array(length).fill(-north)},
  };
  SIM.tiles.set('15:' + ix + ',' + iy, result);
  return result;
}
const a = tile(0, 0, 1, 0), b = tile(1, 0, 0, 1);
const seam = STRIDE + (DOM - STRIDE) / 2;
const at = (x, y = 900) => sample(x, y, 0, 0, 620);
const before = at(seam - 0.01), after = at(seam + 0.01);
assert.ok(Math.hypot(after.vE - before.vE, after.vN - before.vN) < 0.001);
assert.equal(at(seam).vE, 0.5);
assert.equal(at(seam).vN, 0.5);
assert.equal(at(STRIDE - 1).vE, 1);
assert.equal(at(DOM + 1).vN, 1);
b.cur.done = false;
assert.equal(at(seam - 1).pend, true);
assert.equal(at(STRIDE).vE, 1);
b.cur.done = true;
b.resultRun = 0;
assert.equal(at(seam).pend, true);
b.resultRun = 1;
b.solid[75 * b.gx + 12] = 1;
assert.equal(at(seam), null);
b.solid.fill(0);
a.cur.u.fill(0);
a.cur.u[75 * a.gx + 60] = 2;
const x = 60.75 * SC, y = 75.5 * SC;
assert.equal(at(x, y).vE, 1.5);
const c = tile(0, 1, 1, 0);
tile(1, 1, 0, 1);
a.cur.u.fill(1);
const center = at(seam, seam);
assert.equal(center.vE, 0.5);
assert.equal(center.vN, 0.5);
c.cur.done = false;
assert.equal(at(seam, seam).pend, true);
console.log('유속 경계 시험 통과: 셀 보간, 두 구역과 네 구역 연결, 계산 대기, 예보 회차, 육지');
