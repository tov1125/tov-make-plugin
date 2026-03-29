# Slide-HDML 아키텍처 레퍼런스

이 문서는 HTML 슬라이드 엔진의 상세 구현 패턴을 담고 있다. SKILL.md의 규칙만으로 부족할 때 참고한다.

## 목차
1. [CSS 레이아웃 아키텍처](#1-css-레이아웃-아키텍처)
2. [전환 효과 CSS 상세](#2-전환-효과-css-상세)
3. [빌드 효과 CSS 상세](#3-빌드-효과-css-상세)
4. [JS 엔진 구조](#4-js-엔진-구조)
5. [GPU 가속 규칙](#5-gpu-가속-규칙)
6. [브라우저 호환성 주의사항](#6-브라우저-호환성-주의사항)

---

## 1. CSS 레이아웃 아키텍처

### 4-레이어 구조

```
[레이어 1] .deck        — 뷰포트 전체, 레터박스 배경
[레이어 2] .slide        — 16:9 고정, absolute 스택
[레이어 3] .slide-content — 패딩/타이포그래피, 내부 레이아웃
[레이어 4] .fragment     — 빌드 효과 요소
```

### 16:9 비율 고정 수학

```css
/* 뷰포트가 16:9보다 넓으면 → 높이가 제한 요소 */
/* 뷰포트가 16:9보다 좁으면 → 너비가 제한 요소 */
--slide-w: min(100vw, calc(100vh * 16 / 9));
--slide-h: min(100vh, calc(100vw * 9 / 16));
```

`min()` 함수가 자동으로 제한 축을 선택한다. `aspect-ratio: 16/9`는 보강용으로만 사용.

### 슬라이드 스택 배치

모든 슬라이드가 같은 위치에 겹쳐 있고, `opacity`/`visibility`/`transform`으로 보이기/숨기기를 제어한다. 스크롤이 전혀 없다.

```css
.slide {
  position: absolute;
  /* inset: 0이 아니라 width/height를 직접 지정 (16:9 고정 때문) */
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

.slide.active {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  z-index: 1;
}
```

---

## 2. 전환 효과 CSS 상세

### Fade (기본)

```css
.slide[data-transition="fade"],
.slide:not([data-transition]) {
  transition: opacity 0.5s ease;
}
```

가장 단순. 나가는 슬라이드는 `active` 제거 → opacity: 0, 들어오는 슬라이드는 `active` 추가 → opacity: 1.

### Slide (수평 밀기)

```css
.slide[data-transition="slide"] {
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.15s ease;
}

/* 진입 시작 위치 */
.slide[data-transition="slide"].enter-from-right {
  transform: translate3d(100%, 0, 0);
}
.slide[data-transition="slide"].enter-from-left {
  transform: translate3d(-100%, 0, 0);
}

/* 퇴장 방향 */
.slide[data-transition="slide"].exit-to-left {
  transform: translate3d(-100%, 0, 0);
  opacity: 1; visibility: visible; pointer-events: none;
  z-index: 1;
}
.slide[data-transition="slide"].exit-to-right {
  transform: translate3d(100%, 0, 0);
  opacity: 1; visibility: visible; pointer-events: none;
  z-index: 1;
}
```

JS에서 진입 슬라이드의 시작 위치를 설정할 때 `transition: none`으로 잠시 비활성화 → reflow → 다시 활성화.

### Zoom (확대/축소)

```css
.slide[data-transition="zoom"] {
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.5s ease;
}
.slide[data-transition="zoom"]:not(.active) {
  transform: scale3d(0.85, 0.85, 1);
}
.slide[data-transition="zoom"].zoom-out {
  transform: scale3d(1.15, 1.15, 1);
  opacity: 0;
  z-index: 2;
}
```

---

## 3. 빌드 효과 CSS 상세

### 기본 fragment

```css
.fragment {
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.5s ease,
              transform 0.5s cubic-bezier(0.4, 0, 0.2, 1),
              filter 0.5s ease;
}
.fragment.visible {
  opacity: 1;
  visibility: inherit;
}
```

### fade-up

```css
.fragment.fade-up {
  transform: translateY(30px);
}
.fragment.fade-up.visible {
  transform: translateY(0);
}
```

### grow-in

```css
.fragment.grow-in {
  transform: scale(0.5);
}
.fragment.grow-in.visible {
  transform: scale(1);
}
```

### 추가 가능한 효과

```css
/* blur 해제 */
.fragment.blur {
  filter: blur(5px);
  opacity: 0.3;
}
.fragment.blur.visible {
  filter: none;
  opacity: 1;
}

/* 왼쪽에서 슬라이드 인 */
.fragment.fade-right {
  transform: translateX(-30px);
}
.fragment.fade-right.visible {
  transform: translateX(0);
}
```

---

## 4. JS 엔진 구조

### 상태 관리

```js
const slides = [...document.querySelectorAll('.slide')];
const total = slides.length;
let current = 0;
let currentStep = 0;
let isAnimating = false;
let autoPlayTimers = [];

const TRANSITION_MS = 500;
const STEP_DELAY = 400;
const CODE_STEP_DELAY = 800;
```

### 핵심 함수

| 함수 | 역할 |
|------|------|
| `goTo(index, direction)` | 슬라이드 전환 + 입력 잠금 + 전환 후 autoPlay 호출 |
| `advance()` / `retreat()` | autoPlay 취소 + goTo 호출 |
| `autoPlaySlide(slide)` | fragment 순차 등장 + 코드 하이라이트 단계 자동 전환 |
| `cancelAutoPlay()` | 진행 중인 autoPlay 타이머 모두 취소 |
| `updateUI()` | 진행 바 + 카운터 + URL 해시 업데이트 |

### 전환 cleanup 패턴

```js
const cleanup = () => {
  clearTimeout(safetyTimer);
  prev.classList.remove('active', 'exit-to-left', 'exit-to-right', 'zoom-out');
  prev.style.willChange = '';
  next.style.willChange = '';
  current = index;
  isAnimating = false;
  updateUI();
  autoPlaySlide(next); // 전환 완료 후 자동 재생
};

// Primary: transitionend
prev.addEventListener('transitionend', onEnd);
// Safety: setTimeout fallback
const safetyTimer = setTimeout(cleanup, TRANSITION_MS + 100);
```

### 터치 스와이프 판별

```
최소 거리: 50px
최대 시간: 300ms
최대 각도: 30도 (수평에서)
이벤트: touchstart → changedTouches[0].clientX/Y 저장
       touchend → 거리/시간/각도 판별 → advance()/retreat()
passive: true (touchstart, touchend)
```

---

## 5. GPU 가속 규칙

### 애니메이션에 사용해도 되는 속성 (GPU 컴포지터 전용)
- `transform` (translate3d, scale3d, rotate3d)
- `opacity`

### 애니메이션에 사용하면 안 되는 속성 (레이아웃/페인트 트리거)
- `width`, `height`, `top`, `left`, `right`, `bottom`
- `margin`, `padding`
- `background-color` (변경 시)

### will-change 관리
- 전환 직전에 `style.willChange = 'transform, opacity'` 설정
- 전환 완료 후 `style.willChange = ''` 제거
- 모든 슬라이드에 상시 설정하면 GPU 메모리 과다 사용

### backface-visibility
```css
.slide {
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}
```

---

## 6. 브라우저 호환성 주의사항

| 기능 | 최소 지원 | 대응 |
|------|----------|------|
| `100dvh` | Chrome 108, Safari 15.4 | `100vh` 폴백 먼저 선언 |
| `aspect-ratio` | Chrome 88, Safari 15 | `min()/calc()` 로 자체 해결 |
| `min()` / `max()` | Chrome 79, Safari 11.1 | 거의 모든 모던 브라우저 지원 |
| `clamp()` | Chrome 79, Safari 13.1 | 폴백 불필요 (96%+ 지원) |
| `inset: 0` | Chrome 87, Safari 14.1 | 필요시 `top:0;right:0;bottom:0;left:0` |
| `backdrop-filter` | Chrome 76, Safari 9 | `-webkit-` 접두사 추가 |
| `e.key` | 모든 모던 브라우저 | `keyCode` 사용 금지 (deprecated) |
| Fullscreen API | Chrome 71, Safari 16.4 | `webkitRequestFullscreen` 폴백 |

### 모바일 주의

- `touchend`에서 `touches[0]` 접근 불가 → `changedTouches[0]` 사용
- 모바일 Safari에서 `100vh`가 주소창 포함 높이 → `100dvh` 사용
- iOS에서 Fullscreen API 미지원 → 에러 핸들링 필요
