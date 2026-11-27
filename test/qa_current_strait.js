// 최종안: 경계값 baseCor = ROMS + K·(cf-ROMS), K=cap·exp(-(d/L)^2), 가까운 cf만(섬 건너편 제외).
// + 내부 forcing 반경·세기 상향. 바깥 ROMS는 동쪽(반대), cf는 수로서 서쪽 1.04.
const fs=require('fs'), vm=require('vm');
const html=fs.readFileSync('app/src/main/assets/index.html','utf8');
const worker=html.split('const WORKER_SRC=`')[1].split('`;')[0];
const s0=html.indexOf('function anchorCells('), e0=html.indexOf('function simBC(',s0);
const baseForcing=html.slice(s0,e0);
const gx=140,gy=80, idx=(x,y)=>y*gx+x, CELL=47;
const solid=new Uint8Array(gx*gy); const cL=45,cR=95;
for(let y=0;y<gy;y++)for(let x=0;x<gx;x++){const inBasin=x<cL||x>=cR, inCh=y>=35&&y<45; if(!(inBasin||inCh))solid[idx(x,y)]=1;}
for(let x=0;x<gx;x++){solid[idx(x,0)]=1;solid[idx(x,gy-1)]=1;}
const KX=0.82, lat0=34.90, lon0=127.80, dLat=CELL/111000, dLon=CELL/(111000*KX);
const cellLL=(x,y)=>({lat:lat0+(gy-1-y)*dLat, lon:lon0+x*dLon});
const dir=248*Math.PI/180, spd=1.04, bcSpd=0.09;
const st=cellLL(70,40); const cfVec={vE:spd*Math.sin(dir), vN:spd*Math.cos(dir)};
function baseCor(ve,vn,lat,lon,L,cap){
  const d=Math.hypot((lat-st.lat)*111000,(lon-st.lon)*111000*KX), w=Math.exp(-((d/L)**2)), K=cap*w;
  return {vE:ve+K*(cfVec.vE-ve), vN:vn+K*(cfVec.vN-vn)};
}
function solve(mul,rad,L,cap,steps=5000){
  const {anchorCells,stationForcing}=new Function(baseForcing.replace('radius=600','radius='+rad).replace('rate[i]=0.008*','rate[i]='+(0.008*mul)+'*')+'\nreturn{anchorCells,stationForcing}')();
  const station={cx:70,cy:40,vE:cfVec.vE,vN:cfVec.vN};
  const mx=Math.max(spd,bcSpd), scale=0.07/mx;
  const bcIdx=[],bcNb=[],bcIn=[],bcU=[],bcV=[];
  for(let y=1;y<gy-1;y++)for(const x of [0,gx-1]){if(solid[idx(x,y)])continue; const ll=cellLL(x,y);
    const c=baseCor(bcSpd,0,ll.lat,ll.lon,L,cap); bcIdx.push(idx(x,y)); bcNb.push(idx(x===0?1:gx-2,y)); bcIn.push(x===0?1:0); bcU.push(c.vE*scale); bcV.push(-c.vN*scale);}
  const anchor=stationForcing({gx,gy,solid},[station],CELL,scale);
  const ctx=vm.createContext({onmessage:null,setTimeout:()=>1,fixture:{type:'init',gx,gy,solid,bcIdx,bcNb,bcIn,bcU,bcV,anchor}});
  vm.runInContext(worker+`\nonmessage({data:fixture});for(let i=0;i<${steps};i++)step();`,ctx);
  const u=vm.runInContext('Array.from(S.au,v=>v/S.avgN)',ctx), v=vm.runInContext('Array.from(S.av,v=>v/S.avgN)',ctx);
  const sp=i=>Math.hypot(u[i],v[i])/scale, ang=i=>Math.round(Math.atan2(u[idx[0]||i&&u[i],1])*0); 
  const dirDeg=i=>{let d=Math.atan2(u[i],-v[i])*180/Math.PI; return Math.round((d+360)%360);};
  return {st:sp(idx(70,40)), stDir:dirDeg(idx(70,40)), mouth:sp(idx(48,40)), far:sp(idx(20,15)), farDir:dirDeg(idx(20,15))};
}
let pass=0,fail=0; const t=(n,f)=>{try{f();pass++;console.log('  OK  '+n);}catch(e){fail++;console.log('  X   '+n+' — '+e.message);}};
const assert=require('node:assert/strict');
// REQ-104: 좁은 수로 + 반대 방향 ROMS 경계에서, cf 보정 경계 + 상향 forcing이 수로를 실제 방향으로 흐르게 하는가
const nocorr=solve(1,600,1,0);       // cf 경계보정 끔(cap0)·옛 forcing
const fixed=solve(5,1100,1800,0.9);  // 지금 코드 상수
const off=d=>Math.abs(((d-248)+540)%360-180); // cf 방향(248°)과의 차
console.log(`  (보정 끔: ${nocorr.st.toFixed(2)}@${nocorr.stDir}° 차${off(nocorr.stDir)}° · 지금: ${fixed.st.toFixed(2)}@${fixed.stDir}° 차${off(fixed.stDir)}° · 먼바다 ${fixed.far.toFixed(2)})`);
t('지금 상수: 수로 지점이 점 예보의 절반 이상', ()=>assert.ok(fixed.st>=0.52, '지점 '+fixed.st.toFixed(2)+' (목표 1.04)'));
t('지금 상수: 수로 방향이 cf(248°)의 ±35° 안', ()=>assert.ok(off(fixed.stDir)<=35,'방향차 '+off(fixed.stDir)+'°'));
t('cf 경계보정이 방향을 cf 쪽으로 더 끌어온다(끔보다 가까움)', ()=>assert.ok(off(fixed.stDir)<=off(nocorr.stDir)+1,`끔 ${off(nocorr.stDir)}° vs 지금 ${off(fixed.stDir)}°`));
t('먼 열린바다는 느림 (<0.25) — 보정이 넓은 바다로 안 샌다', ()=>assert.ok(fixed.far<0.25,'먼바다 '+fixed.far.toFixed(2)));
console.log(`\n${pass} 통과, ${fail} 실패`); process.exit(fail?1:0);
