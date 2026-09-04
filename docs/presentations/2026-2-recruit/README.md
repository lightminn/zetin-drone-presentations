# 2026-2 개강총회 드론 팀 모집 자료

`index.html`이 편집 원본인 2장짜리 개강총회 모집용 웹 덱이다. 내용은 `10분 요약본`과 엔지니어링 저장소 `README.md`의 "어디까지 왔나"를 바탕으로 정리했다.
`assets/hover_demo.mp4`는 10분 덱의 같은 이름 파일을 그대로 복사한 것이다.
`assets/form-qr.png`는 2쪽 하단 구글폼 모집 링크의 QR이다. 링크가 바뀌면 `index.html`의 `data-form-link` 주소를 고치고 `qrencode -o assets/form-qr.png -s 10 -m 2 -l M "<새 링크>"` 로 다시 만든다.

공개본은 https://lightminn.github.io/zetin-drone-presentations/2026-2-recruit/ 에서 확인한다.

## 로컬 발표

```bash
cd docs/presentations/2026-2-recruit
./present.sh
```

## 검증

```bash
/home/light/anaconda3/bin/python -m unittest tools.test_presentation_recruit -v
```

성숙도 표현(어디까지 검증됐는지)은 엔지니어링 저장소 README·`docs/project_overview.md`가 원본이며, 바뀌면 그쪽을 먼저 고친다.

`support.js`, `deck-stage.js`, `vendor/`는 10분 덱의 복사본이고, 테스트가 byte-identical 여부를 확인한다.
