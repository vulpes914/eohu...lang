# 어흐랭

오늘도 Slop을 만들었다. GPU야 미안해.

이 영광을 어머니 [아희](https://aheui.github.io/jsaheui/jsaheui_en.html), 아버지 [엄랭](https://github.com/rycont/umjunsik-lang)과 형 [혀엉...](https://xnuk.github.io/elmhyeong/)에게 바칩니다.

[사용해보기](https://vulpes914.github.io/eohulang/)

## 여기 있는 것

- `docs/index.html`: 브라우저에서 바로 돌리는 어흐랭 페이지
- `examples/`: 예제 코드
- `src/eohulang/`: 파이썬 구현체

## 구현체

어흐랭은 선언부와 본문으로 나뉜다.

- 선언부는 `ㅇㅎ`, `대꼴`, `후방주의`, `19`, `꼴.`, `꼴,`로 `어흐.` `어흐,` `어흐..` `어흐,,` `어흐...` `어흐,,,`의 역할을 정한다.
- 본문은 선언된 `어흐` 파생 토큰과 `어흐ㅋㅋ`, `ㅗㅜㅑ`만으로 이루어진다.
- 파이썬 구현체는 이 코드를 Brainfuck 명령열로 변환한 다음 실행한다.
- 웹 구현체는 같은 규칙을 브라우저 안에서 그대로 돌린다.

## 실행

- 웹으로 보기: `docs/index.html`
- 로컬 실행: `python eohulang.py run examples/hello_world.eohu`
- Brainfuck 변환: `python eohulang.py compile-bf path/to/program.bf`
