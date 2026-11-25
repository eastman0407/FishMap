"""Focused regressions for the two-page header, light mode and map toolbar."""
from pathlib import Path

source = Path('test/qa_realshape.py').read_text().split('    c0=calls()')[0]
source = source.replace("br.new_page(viewport={'width':411,'height':700})",
                        "br.new_page(viewport={'width':360,'height':780}, has_touch=True)")
exec(source + r'''
    E("__QA.setTheme('light')")
    # Wait for the initial network fixtures before substituting display states.
    pg.wait_for_timeout(3000)
    check('상단 지도 버튼 4개는 글자 없이 독립된 접근성 이름을 가짐',
          E("[...document.querySelectorAll('.side button')].every(b=>!b.querySelector('small')&&!!b.getAttribute('aria-label'))"))
    check('달력 아이콘이 날짜별 탭을 엶', E("""()=>{
        document.querySelector('#planBtn').click();
        const active=document.querySelector('.ptabs .on').dataset.tab;
        document.querySelector('#planClose').click();
        return active==='plan';
    }"""))
    night=pg.locator('#nightBtn')
    pg.wait_for_timeout(300)
    bounds=night.bounding_box()
    cdp=pg.context.new_cdp_session(pg)
    point={'x':bounds['x']+bounds['width']/2,'y':bounds['y']+bounds['height']/2}
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[point]})
    pg.wait_for_timeout(680)
    check('길게 누르면 밤낚시 설명만 보임', pg.locator('#tip').is_visible() and pg.locator('#tip').inner_text()=='밤낚시')
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    check('길게 누르고 손을 떼도 모드와 글자 선택이 남지 않음',
          E("document.documentElement.dataset.theme==='light' && !getSelection().toString() && getComputedStyle(document.querySelector('#nightBtn span')).userSelect==='none'"))
    pg.wait_for_timeout(1500)
    check('설명은 닫히고 짧게 누르면 밤낚시 모드가 동작',
          not pg.locator('#tip').is_visible() and E("document.querySelector('#nightBtn').click(); document.documentElement.dataset.theme==='night'"))
    E("__QA.setTheme('light')")
    pages=E("""()=>{
      const ids=['tideChip','phaseChip','driftChip','wxChip','windChip','skyChip'];
      const q=id=>document.getElementById(id);
      for(const id of ids)q(id).style.display='none';
      const state=()=>[__QA.NCP.n,q('ncPages').hidden,q('ncDots').hidden];
      __QA.ncRepage();const empty=state();
      q('tideChip').style.display='block';q('tideChip').textContent='창선도 관측소 · 만조 20:32';
      __QA.ncRepage();const one=state();
      for(const id of ids.filter(id=>id!=='wxChip')){
        q(id).style.display='block';q(id).textContent+=' 바람 파고 예보 긴 문장 20:32';
      }
      __QA.ncRepage(); const two=state();
      return [empty,one,two,[...q('ncSlide').children].every(p=>p.scrollWidth<=p.clientWidth+1)];
    }""")
    check('빈 페이지는 접고, 긴 문구도 최대 두 페이지', pages==[[0,True,True],[1,False,True],[2,False,False],True], pages)
    colors=E("""()=>{
      const read=(el,key)=>getComputedStyle(el)[key].match(/[0-9.]+/g).slice(0,3).map(Number);
      const l=rgb=>rgb.map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4).reduce((a,x,i)=>a+x*[.2126,.7152,.0722][i],0);
      const ratio=(a,b)=>(Math.max(l(a),l(b))+.05)/(Math.min(l(a),l(b))+.05);
      const station=document.createElement('span');station.className='cfst';document.body.append(station);
      const button=document.querySelector('#nightBtn'), dot=document.querySelector('#ncDots .on');
      return [ratio(read(station,'color'),read(station,'backgroundColor')),
        ratio(read(button,'borderTopColor'),[255,255,255]),
        ratio(read(dot,'backgroundColor'),[255,255,255])];
    }""")
    check('밝은 모드 유속 글씨 4.5 이상, 버튼 윤곽과 페이지 점은 3 이상',
          colors[0]>=4.5 and min(colors[1:])>=3,colors)
    check('스크립트 오류 없음',not errs,errs)
    br.close()
print(f'결과 {sum(map(bool,res))}/{len(res)}')
''')
