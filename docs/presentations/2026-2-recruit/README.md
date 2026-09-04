# 2026-2 개강총회 드론 팀 모집 자료

`index.html`이 편집 원본인 2장짜리 개강총회 모집용 웹 덱이다. 내용은 `10분 요약본`과 엔지니어링 저장소 `README.md`의 "어디까지 왔나"를 바탕으로 정리했다.

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

수치(176초, 5/5, 1 kHz)는 엔지니어링 저장소 README·`docs/project_overview.md`가 원본이며, 바뀌면 그쪽을 먼저 고친다.

`support.js`, `deck-stage.js`, `vendor/`는 10분 덱의 복사본이고, 테스트가 byte-identical 여부를 확인한다.
