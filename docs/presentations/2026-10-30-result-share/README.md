# 2026-10-30 중간보고 — 자작 드론 비행제어와 광류 위치 유지

`index.html`이 발표용 웹 덱이다(13장 + 표지, 사무적·기술적 중간보고 어조). 도식 자리는 Manim으로 만든 영상(`assets/anim/*.mp4`)이다.
영상은 해당 장이 열리면 음소거로 자동 재생되고 반복한다.

공개본은 https://lightminn.github.io/zetin-drone-presentations/2026-10-30-result-share/ 에서 확인한다.

## 로컬 발표

```bash
cd docs/presentations/2026-10-30-result-share
./present.sh
```

## 근거와 한계

- 수치의 정답은 엔지니어링 저장소(`lightminn/zetin-drone`)의 코드와 비행 로그다. 슬라이드와 어긋나면 코드가 맞다.
- 10장(테더 실기체 시험)의 그래프는 2026-10-30 비행 로그에서 `source/make_poshold_stats.py`로 뽑은 값이다.
  속도는 광류 추정값이며 외부 기준 위치와 대조한 값이 아니다. 위치 유지를 끈 비행은 1회뿐이다.
- 영상은 개념 설명용 애니메이션이다. 10장 막대 그래프만 실측 로그 값이고, 나머지는 실측 데이터가 아니다.
- 8월 로그에는 광류 위치·속도 기록이 없어 8월 대비 수치 비교는 하지 않았다.

## 다시 만들기

```bash
# 영상 (Manim Community 0.19, LaTeX 불필요)
cd source/visualizations && ./render_all.sh && ./encode.sh   # 결과: anim_out/ → assets/anim/ 로 복사
# 문구(slides.json)와 도식 → index.html (video) / PDF용 정지 프레임판(pdf)
python3 source/build.py source/slides.json index.html video
python3 source/build.py source/slides.json index_pdf.html pdf
```

`support.js`, `vendor/`는 10분 덱의 복사본이다. `deck-stage.js`는 같은 파일에서 영상 재생 시 기본 컨트롤을
`data-anim` 영상에는 켜지 않도록 한 줄만 고쳤다.
