# 1단계 시험: 빈 대답 저장 금지·예보 회차 섞임 방지·기존 흐름 유지·청소 (build-22)
# 앱의 저장(캐시) 동작을 브리지에서 흉내: 기간 안 저장본은 2000000+분, dropCache 지원, cleanCache 기록
import sys, time, urllib.request
sys.argv=sys.argv[:1]
src=open('test/qa_realshape.py').read().split("    c0=calls()")[0].replace("res.append(c)","res.append(bool(c))")
src=src.replace('''BRIDGE=r"""window.AndroidBridge={_p:{dataKey:'K'},getPref(k){return this._p[k]||''},setPref(k,v){this._p[k]=v},dropCache(){},clearCache(){},shareText(t){window.__shared=t},''',
'''BRIDGE=r"""window.__cache=new Map();window.__drops=0;window.__cleans=[];window.AndroidBridge={_p:{dataKey:'K'},getPref(k){return this._p[k]||''},setPref(k,v){this._p[k]=v},dropCache(u){if(window.__cache.delete(u))window.__drops++},clearCache(){},shareText(t){window.__shared=t},
 cleanCache(r){window.__cleans.push(r);return '3,4096'},appVersion(){return '시험 (22)'},''')
src=src.replace("""  fetch(url.replace('https://apis.data.go.kr/1192136/roms/GetRomsApiService','http://localhost:9098/roms')).then(r=>r.text().then(t=>reply(r.status,t)));}};""",
"""  const c=window.__cache.get(url); if(m>0&&c&&Date.now()-c.at<m*60000)return reply(2000000+Math.floor((Date.now()-c.at)/60000),c.body);
  fetch(url.replace('https://apis.data.go.kr/1192136/roms/GetRomsApiService','http://localhost:9098/roms')).then(r=>r.text().then(t=>{if(r.status===200&&m>0)window.__cache.set(url,{at:Date.now(),body:t});reply(r.status,t);}));}};""")
assert 'window.__cache.get(url)' in src
mode=lambda q:urllib.request.urlopen('http://localhost:9098/mode?'+q).read()
exec(src+'''
    COV="""(()=>{let h=0,w=0;for(let yy=0;yy<10;yy++)for(let xx=0;xx<6;xx++){const x=(xx+.5)*__QA.W()/6,y=(yy+.5)*__QA.H()/10;if(!__QA.isWater(x,y))continue;w++;
      const ll=_map.containerPointToLatLng([x,y]);if(__QA.baseAt(ll.lat,ll.lng,__QA.tH()))h++;}return [h,w];})()"""
    # S1: 서버가 잠깐 빈 대답 → 앱은 저장하지 않음 → 서버 회복 후 다시 오면 채워짐 (실기기 11-14 결함 재현 방지)
    for _ in range(60):
        if not E("__QA.RD.loading"): break
        pg.wait_for_timeout(500)
    pg.wait_for_timeout(1500)
    E("window.__cache.clear();__QA.RD.reqId++;__QA.ROMS.mem.clear();__QA.setRealData({times:[],points:[]},null);__QA.RD.have=null")  # 앱을 막 켠 상태처럼 (이전에 받은 흐름 없음)
    mode('empty=1'); go(13,34.86,128.20,9000)
    e0=E(COV); n_empty=E("Object.values(__QA.ROMS.stat).filter(v=>v.got===0).length")
    mode('empty=0'); E("for(const [k,v] of __QA.ROMS.mem)v.at-=11*60000"); go(12,34.86,128.20,3000); go(13,34.86,128.20,9000)
    e1=E(COV)
    check('S1 일시적 빈 대답을 저장하지 않고 다시 받아 채움', e0[0]==0 and e1[1]>0 and e1[0]/e1[1]>=0.9, f'빈 대답 때 {e0[0]}/{e0[1]} → 회복 후 {e1[0]}/{e1[1]} (빈 칸 {n_empty})')
    check('S2 빈 대답은 휴대폰 저장소에 남지 않음', E("[...window.__cache.values()].every(c=>!c.body.includes('NODATA'))"))
    # S3: 저장본이 빈 대답이면(예전 버전이 남긴 것) 버리고 새로 물어봄
    E("for(const k of [...window.__cache.keys()])if(k.includes('pageNo=1&'))window.__cache.set(k,{at:Date.now(),body:JSON.stringify({header:{resultCode:'03'}})})")
    E("__QA.ROMS.mem.clear();__QA.RD.have=null"); go(13,34.86,128.20,9000)
    st=E("Object.values(__QA.ROMS.stat).filter(v=>v.retried)")
    check('S3 빈 저장본은 버리고 서버에 다시 물어봄', len(st)>0 and all(v['got']>0 for v in st), [v.get('retried') for v in st][:3])
    # S4/S5: 새 예보 회차 발표 → 옛 회차와 섞지 않음
    t_before=E("__QA.RD.times.length"); run0=E("__QA.ROMS.run")
    mode('run=1')
    # 한 칸만 서버에서 새로 받게 함 (나머지는 아직 옛 회차 저장본) → 실기기처럼 섞일 상황
    E("(()=>{const k=[...__QA.ROMS.mem.keys()].find(k=>k[0]==='d');const v=__QA.ROMS.mem.get(k);__QA.ROMS.mem.delete(k);for(const u of [...window.__cache.keys()])if(u.includes('ymin='+v.b.s+'&')&&u.includes('xmin='+v.b.w+'&'))window.__cache.delete(u);__QA.RD.have=null;})()")
    go(13,34.87,128.21,12000); go(13,34.86,128.20,9000)
    runs=E("[...new Set([...__QA.ROMS.mem.values()].filter(v=>v.items.length).map(v=>v.run))].length")
    check('S4 새 회차가 나오면 옛 회차 칸은 버리고 한 벌만 씀', E("__QA.ROMS.run")>run0 and runs==1, f'회차 수 {runs}')
    check('S5 시각 수가 한 회차(178)를 넘지 않음 (실기기 202개 결함)', E("__QA.RD.times.length")==178, f'{t_before} → {E("__QA.RD.times.length")}')
    e2=E(COV); check('S6 회차 바꾼 뒤에도 바다 전체에 흐름', e2[1]>0 and e2[0]/e2[1]>=0.9, e2)
    # S7: 새로 받은 결과가 적어도 이미 받은 흐름은 지우지 않음
    before=E(COV); mode('empty=1'); E("for(const [k,v] of __QA.ROMS.mem)if(!v.items.length)__QA.ROMS.mem.delete(k)")
    E("_map.panBy(160,0)"); pg.wait_for_timeout(6000); E("_map.panBy(-160,0)"); pg.wait_for_timeout(3000); after=E(COV); mode('empty=0')
    check('S7 새 대답이 비어도 원래 화면 흐름 유지', after[1]>0 and after[0]>=before[0]*0.9, f'{before} → {after}')
    # S8: 청소
    check('S8 앱 켤 때 지난 자료 청소 1번 (규칙 전달)', E("window.__cleans.length")==1 and 'roms:11520' in E("window.__cleans[0]"), E("window.__cleans"))
    d=pg.evaluate("__QA.runDiag()")
    check('S9 진단: 버전·받은 곳(새로/저장)·예보 회차·청소 표시', all(x in d for x in ['v시험 (22)','받은 곳:','예보 회차:','지난 자료 청소:']), [l for l in d.split(chr(10)) if '받은 곳' in l or '회차' in l or '청소' in l])
    check('S10 스크립트 오류 없음', not errs, errs[:2])
    br.close()
print(f"결과: {sum(res)}/{len(res)}")
''')
