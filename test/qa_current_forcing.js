const assert = require('node:assert/strict');
const fs = require('node:fs');
const html = fs.readFileSync('app/src/main/assets/index.html','utf8');
const start = html.indexOf('function anchorCells('), end = html.indexOf('function simBC(', start);
const {anchorCells,stationForcing} = new Function(html.slice(start,end)+'\nreturn {anchorCells,stationForcing}')();
const gx=55,gy=31,solid=new Uint8Array(gx*gy);
for (const y of [8,22]) solid.fill(1,y*gx,(y+1)*gx);
const tile={gx,gy,solid}, station={cx:27,cy:15,vE:1,vN:0};
const cells=new Map(anchorCells(tile,station,47));
const idx=(x,y)=>y*gx+x;
assert.equal(cells.get(idx(27,15)),1);
for(let offset=1;offset<=12;offset++){
  assert.ok(cells.get(idx(27+offset,15))<cells.get(idx(26+offset,15)));
  assert.equal(cells.get(idx(27+offset,15)),cells.get(idx(27-offset,15)));
}
assert.ok(!cells.has(idx(27,23)));
assert.ok(!cells.has(idx(40,15)));
const field=stationForcing(tile,[station],47,0.07);
assert.ok(field.rate[idx(27,15)]<0.01);
assert.ok(Math.abs(field.east[idx(30,15)]-.07)<1e-7);
assert.equal(field.rate[idx(27,23)],0);
const distance=eval(html.match(/const flowDistance=(.*);/)[1]);
for(const fps of [30,60,120]){
  assert.ok(Math.abs(fps*distance(0.5*3.6/1.852,1/fps)-8)<1e-9);
  assert.ok(Math.abs(fps*distance(3.6/1.852,1/fps)-16)<1e-9);
}
console.log('통과: 물길 안 점진적 보정, 방파제 너머 차단, 주사율과 무관한 이동량');

// Run the production solver with and without a station on the same channel.
const vm=require('node:vm');
const worker=html.split('const WORKER_SRC=`')[1].split('`;')[0];
function solve(anchor) {
  const bcIdx=[],bcNb=[],bcIn=[],bcU=[],bcV=[];
  for(let y=0;y<gy;y++)for(const x of [0,gx-1]){
    if(solid[idx(x,y)])continue;
    bcIdx.push(idx(x,y)); bcNb.push(idx(x===0?1:gx-2,y));
    bcIn.push(x===0?1:0); bcU.push(.025); bcV.push(0);
  }
  const context=vm.createContext({onmessage:null,setTimeout:()=>1,
    fixture:{type:'init',gx,gy,solid,bcIdx,bcNb,bcIn,bcU,bcV,anchor}});
  vm.runInContext(worker+'\nonmessage({data:fixture});for(let i=0;i<2600;i++)step();',context);
  return vm.runInContext('Array.from(S.au,v=>v/S.avgN)',context);
}
const baseline=solve(null), corrected=solve(field);
const stationDelta=corrected[idx(27,15)]-baseline[idx(27,15)];
assert.ok(stationDelta>0);
assert.ok(corrected[idx(27,15)]<0.07);
const grad=Math.max(...Array.from({length:20},(_,i)=>Math.abs(corrected[idx(18+i,15)]-corrected[idx(17+i,15)])));
assert.ok(grad<stationDelta*0.4);
console.log('통과: 실제 계산기에서 지점 보정이 전달되며 이웃 셀 사이 속도가 급변하지 않음');
