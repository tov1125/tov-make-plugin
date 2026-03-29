---
name: slide-hdml
description: 순수 HTML/CSS/JS 단일 파일 슬라이드 프레젠테이션을 생성하는 스킬. 사용자가 자연어("발표자료 만들어줘", "슬라이드 생성해줘")로 요청하거나, 기존 문서(마크다운, 텍스트, PDF, URL, PPTX, HWPX 등)를 슬라이드로 변환하려 할 때 사용한다. '프레젠테이션', '슬라이드', '발표', 'PPT', '발표자료', 'deck', 'presentation' 등의 키워드가 나오면 이 스킬을 사용하라. 단, 기존 PPTX/PDF를 편집하는 것이 아니라, 항상 새로운 HTML 슬라이드를 생성하는 방식이다.
---

# Slide-HDML: 순수 HTML 슬라이드 생성 스킬

외부 라이브러리 없이 **순수 HTML/CSS/JS 단일 파일**로 완결되는 웹 슬라이드를 생성한다. 브라우저에서 바로 열면 동작한다.

## 워크플로우

### Phase 1: 입력 분석

**경로 A — 자연어** : 슬라이드 수, 주제, 톤, 대상 청중 파악. 부족하면 간결하게 질문.
**경로 B — 문서 변환** : MD/텍스트/PDF/URL/PPTX/HWPX → Read/WebFetch로 읽기 → 슬라이드 단위로 분절.

### Phase 2: 슬라이드 계획

구성안을 사용자에게 보여준다 (빠른 진행 원하면 생략 가능):
```
1. [타이틀] 제목 — theme-dark, fade
2. [본문] 핵심 기능 — theme-light, slide, 빌드 4단계
3. [코드] 예시 — theme-code, zoom, 라인 하이라이트
4. [마무리] Thank You — theme-dark, zoom
```

### Phase 3: HTML 생성

아래 **완전한 템플릿**의 `<!-- SLIDES HERE -->` 부분만 사용자 콘텐츠로 교체한다. CSS/JS 엔진은 그대로 복사한다. 새로 짜지 않는다.

---

## 완전한 HTML 템플릿

이 템플릿을 그대로 복사하고, `{제목}` 과 `<!-- SLIDES HERE -->` 부분만 교체한다.

```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{제목}</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;font-family:'Pretendard',system-ui,-apple-system,sans-serif;background:#0a0a0a}

/* Deck */
.deck{width:100vw;height:100vh;height:100dvh;display:grid;place-items:center;position:relative}

/* Slide 16:9 */
.slide{
  --sw:min(100vw,calc(100vh*16/9));--sh:min(100vh,calc(100vw*9/16));
  width:var(--sw);height:var(--sh);aspect-ratio:16/9;
  position:absolute;overflow:hidden;opacity:0;visibility:hidden;pointer-events:none;
  transform:translate3d(0,0,0);backface-visibility:hidden;
  display:grid;place-items:center;
}
.slide.active{opacity:1;visibility:visible;pointer-events:auto;transform:translate3d(0,0,0) scale3d(1,1,1);z-index:1}

/* Transitions */
.slide[data-transition="fade"],.slide:not([data-transition]){transition:opacity .5s ease}
.slide[data-transition="slide"]{transition:transform .5s cubic-bezier(.4,0,.2,1),opacity .15s ease}
.slide[data-transition="slide"].enter-from-right{transform:translate3d(100%,0,0)}
.slide[data-transition="slide"].enter-from-left{transform:translate3d(-100%,0,0)}
.slide[data-transition="slide"].exit-to-left{transform:translate3d(-100%,0,0);opacity:1;visibility:visible;pointer-events:none;z-index:1}
.slide[data-transition="slide"].exit-to-right{transform:translate3d(100%,0,0);opacity:1;visibility:visible;pointer-events:none;z-index:1}
.slide[data-transition="zoom"]{transition:transform .5s cubic-bezier(.4,0,.2,1),opacity .5s ease}
.slide[data-transition="zoom"]:not(.active){transform:scale3d(.85,.85,1)}
.slide[data-transition="zoom"].zoom-out{transform:scale3d(1.15,1.15,1);opacity:0;z-index:2}

/* Content */
.slide-content{width:100%;height:100%;padding:6% 8%;display:flex;flex-direction:column;justify-content:center}
.slide-content h1{font-size:clamp(28px,5vw,80px);font-weight:800;line-height:1.2;margin-bottom:.3em}
.slide-content h2{font-size:clamp(22px,3.2vw,56px);font-weight:700;line-height:1.3;margin-bottom:.5em}
.slide-content p{font-size:clamp(14px,1.8vw,32px);line-height:1.7;color:#555}
.slide-content ul,.slide-content ol{padding-left:1.5em;font-size:clamp(14px,1.8vw,30px);line-height:1.8}
.slide-content li{margin-bottom:.3em}

/* Themes */
.slide.theme-dark{background:linear-gradient(135deg,#1a1a2e,#16213e);color:#f0f0f0}
.slide.theme-dark p,.slide.theme-dark li{color:#aab}
.slide.theme-light{background:#fff;color:#1a1a2e}
.slide.theme-accent{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff}
.slide.theme-accent p,.slide.theme-accent li{color:rgba(255,255,255,.85)}
.slide.theme-code{background:#1e1e1e;color:#d4d4d4}

/* Columns */
.columns{display:grid;grid-template-columns:1fr 1fr;gap:clamp(16px,2vw,48px);width:100%;margin-top:.8em}

/* Fragments */
.fragment{opacity:0;visibility:hidden;transition:opacity .5s ease,transform .5s cubic-bezier(.4,0,.2,1),filter .5s ease}
.fragment.visible{opacity:1;visibility:inherit}
.fragment.fade-up{transform:translateY(30px)}.fragment.fade-up.visible{transform:translateY(0)}
.fragment.grow-in{transform:scale(.5)}.fragment.grow-in.visible{transform:scale(1)}

/* Code block */
.code-block{background:#0d1117;border-radius:12px;padding:1.2em 1.5em;font-family:'Fira Code','SF Mono',monospace;font-size:clamp(12px,1.4vw,22px);line-height:1.7;overflow-x:auto;width:100%;margin-top:.8em;counter-reset:line}
.code-block .line{display:block;padding:0 .5em 0 3em;position:relative;border-left:3px solid transparent;transition:background .3s ease,opacity .3s ease,border-color .3s ease}
.code-block .line::before{counter-increment:line;content:counter(line);position:absolute;left:0;width:2.2em;text-align:right;color:#484848;padding-right:.5em;user-select:none}
.code-block .line.highlight{background:rgba(56,139,253,.15);border-left-color:#388bfd}
.code-block.has-highlight .line:not(.highlight){opacity:.35}
.syn-keyword{color:#ff7b72}.syn-string{color:#a5d6ff}.syn-comment{color:#8b949e;font-style:italic}
.syn-number{color:#79c0ff}.syn-function{color:#d2a8ff}.syn-builtin{color:#ffa657}

/* Progress bar */
.progress-bar{position:fixed;top:0;left:0;width:100%;height:3px;background:rgba(255,255,255,.1);z-index:100}
.progress-fill{height:100%;width:0%;background:linear-gradient(90deg,#667eea,#764ba2);transition:width .3s ease}

/* Nav */
.slide-nav{position:fixed;bottom:clamp(10px,2vh,24px);left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:.8rem;z-index:100;background:rgba(0,0,0,.6);padding:.4rem 1rem;border-radius:2rem;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);opacity:0;transition:opacity .3s}
.deck:hover~.slide-nav,.slide-nav:hover{opacity:1}
.slide-nav button{background:none;border:none;color:#ccc;font-size:1rem;cursor:pointer;padding:.3rem .5rem;border-radius:4px;transition:background .2s,color .2s;line-height:1}
.slide-nav button:hover{background:rgba(255,255,255,.15);color:#fff}
.slide-counter{color:#888;font-size:.8rem;font-variant-numeric:tabular-nums;min-width:5ch;text-align:center;user-select:none}

/* Speaker notes */
.speaker-notes{display:none}
.speaker-notes.visible{display:block;position:fixed;bottom:50px;left:50%;transform:translateX(-50%);width:min(90vw,700px);background:rgba(0,0,0,.9);color:#eee;padding:1em 1.5em;border-radius:12px;font-size:.9rem;line-height:1.6;z-index:200;max-height:30vh;overflow-y:auto}

@media(prefers-reduced-motion:reduce){.slide,.fragment{transition-duration:.01ms!important}}
</style>
</head>
<body>

<main class="deck" role="region" aria-roledescription="presentation">
<!-- SLIDES HERE -->
</main>

<div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
<nav class="slide-nav" aria-label="Slide navigation">
  <button class="nav-prev" aria-label="Previous slide">&#9664;</button>
  <span class="slide-counter" id="slideCounter" aria-live="polite"></span>
  <button class="nav-next" aria-label="Next slide">&#9654;</button>
</nav>

<script>
(()=>{
'use strict';
const slides=[...document.querySelectorAll('.slide')],total=slides.length;
let current=0,currentStep=0,isAnimating=false,autoPlayTimers=[];
const TM=500,SM=100,SD=400,CD=800;

function getFragments(s){return[...s.querySelectorAll('.fragment')].sort((a,b)=>(parseInt(a.dataset.step)||0)-(parseInt(b.dataset.step)||0))}
function getMaxStep(s){const f=getFragments(s);return f.length?Math.max(...f.map(x=>parseInt(x.dataset.step)||0)):0}
function updateFragments(s,step){getFragments(s).forEach(f=>{f.classList.toggle('visible',(parseInt(f.dataset.step)||0)<=step)})}
function resetFragments(s){s.querySelectorAll('.fragment').forEach(f=>f.classList.remove('visible'))}

function cancelAutoPlay(){autoPlayTimers.forEach(t=>clearTimeout(t));autoPlayTimers=[]}
function autoPlaySlide(s){
  cancelAutoPlay();
  const mx=getMaxStep(s),cbs=getCodeBlocks(s);let d=SD;
  for(let i=1;i<=mx;i++){const st=i;autoPlayTimers.push(setTimeout(()=>{currentStep=st;updateFragments(s,st)},d));d+=SD}
  for(const b of cbs){for(let i=0;i<b._hlSteps.length;i++){const idx=i;autoPlayTimers.push(setTimeout(()=>{b._hlCurrent=idx;updateCodeHL(b,idx)},d));d+=CD}}
}

function getCodeBlocks(s){return[...s.querySelectorAll('.code-block[data-line-numbers]')]}
function parseLS(spec){return spec.split('|').map(g=>{const l=[];g.split(',').forEach(p=>{const r=p.trim().split('-').map(Number);if(r.length===2)for(let i=r[0];i<=r[1];i++)l.push(i);else l.push(r[0])});return l})}
function updateCodeHL(b,si){const st=b._hlSteps,ls=b.querySelectorAll('.line');if(si<0||si>=st.length){b.classList.remove('has-highlight');ls.forEach(l=>l.classList.remove('highlight'));return}b.classList.add('has-highlight');const n=st[si];ls.forEach((l,i)=>l.classList.toggle('highlight',n.includes(i+1)))}
function initCB(){document.querySelectorAll('.code-block[data-line-numbers]').forEach(b=>{b._hlSteps=parseLS(b.dataset.lineNumbers);b._hlCurrent=-1})}

function goTo(idx,dir='forward'){
  if(isAnimating||idx<0||idx>=total||idx===current)return;
  isAnimating=true;
  const prev=slides[current],next=slides[idx],tr=next.dataset.transition||'fade';
  prev.style.willChange='transform,opacity';next.style.willChange='transform,opacity';
  resetFragments(next);currentStep=0;
  getCodeBlocks(next).forEach(b=>{b._hlCurrent=-1;updateCodeHL(b,-1)});

  if(tr==='slide'){
    next.style.transition='none';
    next.classList.add(dir==='forward'?'enter-from-right':'enter-from-left');
    next.classList.add('active');next.offsetHeight;next.style.transition='';
    next.classList.remove('enter-from-right','enter-from-left');
    prev.classList.add(dir==='forward'?'exit-to-left':'exit-to-right');
  }else if(tr==='zoom'){next.classList.add('active');prev.classList.add('zoom-out')}
  else{next.classList.add('active')}

  const cleanup=()=>{clearTimeout(sf);prev.classList.remove('active','exit-to-left','exit-to-right','zoom-out');prev.style.willChange='';next.style.willChange='';current=idx;isAnimating=false;updateUI();autoPlaySlide(next)};
  const onEnd=e=>{if(e.target!==prev)return;prev.removeEventListener('transitionend',onEnd);cleanup()};
  prev.addEventListener('transitionend',onEnd);
  const sf=setTimeout(()=>{prev.removeEventListener('transitionend',onEnd);cleanup()},TM+SM);
}

function advance(){cancelAutoPlay();goTo(current+1,'forward')}
function retreat(){cancelAutoPlay();goTo(current-1,'backward')}
function updateUI(){
  document.getElementById('progressFill').style.width=`${total>1?(current/(total-1))*100:100}%`;
  document.getElementById('slideCounter').textContent=`${current+1} / ${total}`;
  history.replaceState(null,'',`#slide-${current+1}`);
  if(notesVisible){document.querySelectorAll('.speaker-notes').forEach(n=>n.classList.toggle('visible',n.closest('.slide')===slides[current]))}
}

document.addEventListener('keydown',e=>{
  if(e.target.matches('input,textarea,select,[contenteditable]')||e.repeat)return;
  switch(e.key){
    case'ArrowRight':case'ArrowDown':case' ':case'PageDown':e.preventDefault();advance();break;
    case'ArrowLeft':case'ArrowUp':case'PageUp':e.preventDefault();retreat();break;
    case'Home':e.preventDefault();cancelAutoPlay();goTo(0,'backward');break;
    case'End':e.preventDefault();cancelAutoPlay();goTo(total-1,'forward');break;
    case'f':case'F':if(!e.ctrlKey&&!e.metaKey){e.preventDefault();document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen().catch(()=>{})}break;
    case's':case'S':if(!e.ctrlKey&&!e.metaKey){e.preventDefault();toggleNotes()}break;
  }
});

document.querySelector('.nav-prev').addEventListener('click',retreat);
document.querySelector('.nav-next').addEventListener('click',advance);

let tsx=0,tsy=0,tst=0;
document.addEventListener('touchstart',e=>{const t=e.changedTouches[0];tsx=t.clientX;tsy=t.clientY;tst=Date.now()},{passive:true});
document.addEventListener('touchend',e=>{const t=e.changedTouches[0],dx=t.clientX-tsx,dy=t.clientY-tsy;if(Date.now()-tst>300||Math.abs(dx)<50)return;if(Math.atan2(Math.abs(dy),Math.abs(dx))*180/Math.PI>30)return;dx<0?advance():retreat()},{passive:true});

let notesVisible=false;
function toggleNotes(){notesVisible=!notesVisible;document.querySelectorAll('.speaker-notes').forEach(n=>n.classList.toggle('visible',notesVisible&&n.closest('.slide')===slides[current]))}

function slideFromHash(){const m=location.hash.match(/^#slide-(\d+)$/);if(m){const n=parseInt(m[1],10);if(n>=1&&n<=total)return n-1}return 0}
window.addEventListener('hashchange',()=>{const i=slideFromHash();if(i!==current){cancelAutoPlay();goTo(i,i>current?'forward':'backward')}});

initCB();
const ss=slideFromHash();
if(ss!==0){slides[0].classList.remove('active');slides[ss].classList.add('active');current=ss}
updateUI();autoPlaySlide(slides[current]);
})();
</script>
</body>
</html>
```

---

## 슬라이드 작성 규칙

`<!-- SLIDES HERE -->` 자리에 아래 형식으로 슬라이드를 채운다. 첫 번째에만 `active` 클래스.

### 기본 슬라이드

```html
<section class="slide theme-dark active" data-transition="fade" aria-roledescription="slide">
  <div class="slide-content">
    <h1>제목</h1>
    <p class="fragment fade-up" data-step="1">부제</p>
  </div>
</section>
```

### 리스트 슬라이드

```html
<section class="slide theme-light" data-transition="slide" aria-roledescription="slide">
  <div class="slide-content">
    <h2>주제</h2>
    <ul>
      <li class="fragment fade-up" data-step="1">항목 1</li>
      <li class="fragment fade-up" data-step="2">항목 2</li>
      <li class="fragment fade-up" data-step="3">항목 3</li>
    </ul>
  </div>
</section>
```

### 2단 컬럼

```html
<section class="slide theme-accent" data-transition="fade" aria-roledescription="slide">
  <div class="slide-content">
    <h2>비교</h2>
    <div class="columns">
      <div class="fragment grow-in" data-step="1"><h3>A</h3><p>설명</p></div>
      <div class="fragment grow-in" data-step="2"><h3>B</h3><p>설명</p></div>
    </div>
  </div>
</section>
```

### 코드 블록 (라인 하이라이트)

```html
<section class="slide theme-code" data-transition="zoom" aria-roledescription="slide">
  <div class="slide-content">
    <h2 style="color:#e6e6e6">코드 예시</h2>
    <pre class="code-block" data-line-numbers="1|2-3"><code><span class="line"><span class="syn-keyword">const</span> x = <span class="syn-number">1</span>;</span>
<span class="line"><span class="syn-keyword">const</span> y = <span class="syn-number">2</span>;</span>
<span class="line"><span class="syn-comment">// 합계</span></span></code></pre>
  </div>
</section>
```

### 발표자 노트

슬라이드 안에 `<div class="speaker-notes">` 를 추가하면 S키로 토글:

```html
<div class="speaker-notes">이 슬라이드에서는 시장 규모를 강조하세요.</div>
```

---

## 콘텐츠 가이드

1. **한 슬라이드, 한 메시지** — 텍스트가 많으면 분할
2. **h1은 타이틀만**, h2는 슬라이드 제목, p/li는 본문
3. **빌드 순서** — 논리적 흐름에 따라 `data-step` 배정, 핵심은 마지막
4. **전환**: 순서 흐름 → `slide`, 세부 진입 → `zoom`, 기본 → `fade`
5. **테마**: 첫/끝 → `theme-dark`, 본문 → `theme-light`, 강조 → `theme-accent`
6. **커스텀 테마**: 사용자가 브랜드 색상을 지정하면 추가 `.slide.theme-brand` CSS 생성

---

## 레퍼런스

상세한 CSS/JS 아키텍처, GPU 가속, 브라우저 호환성이 궁금하면 `references/architecture.md`를 참고한다. 일반적인 슬라이드 생성에는 이 SKILL.md만으로 충분하다.
