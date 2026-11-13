// 실제 국립해양조사원 ROMS 응답을 흉내내는 가짜 서버 (build-17 실기기 진단 결과 기준, 2026-11-14)
//  - 지점 하나당 178시간(어제 00시부터 1시간 간격), 지점순 정렬
//  - 시각 칸 predcDt "YYYY-MM-DD HH:MM:SS", 숫자 칸은 숫자형, 유속 crsp는 m/s
//  - 격자 간격 약 0.029°(위도) x 0.031°(경도), 살짝 비틀린 격자
//  - 구역에 지점 없으면 resultCode 3
const http=require('http');
const T0=(()=>{const d=new Date(Date.now()+9*3600e3);d.setUTCHours(0,0,0,0);return d.getTime()-9*3600e3-86400e3;})(); // 어제 00시 KST
const NT=178, DLAT=0.0287, DLON=0.0313;
function pts(s,n,w,e){
  const out=[];
  for(let i=Math.ceil((s-34)/DLAT)-1;i<=Math.floor((n-34)/DLAT)+1;i++)for(let j=Math.ceil((w-127)/DLON)-1;j<=Math.floor((e-127)/DLON)+1;j++){
    const lat=+(34+i*DLAT+0.004*Math.sin(j*0.7)).toFixed(5), lon=+(127+j*DLON+0.003*Math.cos(i*0.9)).toFixed(5);
    if(lat>=s&&lat<=n&&lon>=w&&lon<=e)out.push([lat,lon]);
  }
  return out.sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
}
let calls=0;
http.createServer((req,res)=>{
  const u=new URL(req.url,'http://x'); const q=k=>+u.searchParams.get(k);
  if(u.pathname==='/calls'){res.end(String(calls));return;}
  if(u.pathname==='/reset'){calls=0;res.end('0');return;}
  calls++;
  const P=pts(q('ymin'),q('ymax'),q('xmin'),q('xmax')), page=q('pageNo')||1, rows=Math.min(300,q('numOfRows')||10);
  const total=P.length*NT;
  res.writeHead(200,{'Content-Type':'application/json','Access-Control-Allow-Origin':'*'});
  if(!total){res.end(JSON.stringify({header:{resultCode:'03',resultMsg:'NODATA_ERROR'}}));return;}
  const items=[];
  for(let r=(page-1)*rows;r<Math.min(total,page*rows);r++){
    const [lat,lon]=P[Math.floor(r/NT)], h=r%NT, t=new Date(T0+h*3600e3+9*3600e3), p=n=>String(n).padStart(2,'0');
    const ph=2*Math.PI*h/12.42+lat*3+lon*2;
    items.push({predcDt:`${t.getUTCFullYear()}-${p(t.getUTCMonth()+1)}-${p(t.getUTCDate())} ${p(t.getUTCHours())}:00:00`,
      lat,lot:lon,crdir:+(Math.sin(ph)>0?75+lat*10%30:255+lon*10%30).toFixed(2),crsp:+(Math.abs(Math.sin(ph))*0.45+0.02).toFixed(2),wtem:16.3});
  }
  res.end(JSON.stringify({header:{resultCode:'00',resultMsg:'NORMAL_SERVICE'},body:{pageNo:page,numOfRows:rows,totalCount:total,items:{item:items}}}));
}).listen(9098);
