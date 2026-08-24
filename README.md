# ZETIN Drone — 발표자료

자작 드론 비행제어기 프로젝트(ZETIN Drone)의 **발표자료와 대외 공개물**만 모은
저장소다. 펌웨어·지상국 코드는 여기 없다.

- 엔지니어링 저장소: **[lightminn/zetin-drone](https://github.com/lightminn/zetin-drone)**
- **수치의 정답은 엔지니어링 저장소다.** 상수·텔레메트리 필드 번호·프로토콜
  규격을 이 저장소에 옮겨 적지 않는다. 슬라이드가 코드와 어긋나면 코드가 맞다.

## 자료

| 자료 | 대상 | 편집 원본 | 공개 URL |
|---|---|---|---|
| AI 창업캠프 드론 기술 교안 | 드론·제어 입문자, 2시간 30분 | [`index.html`](docs/presentations/ai-startup-camp-drone/index.html) | https://lightminn.github.io/zetin-drone-presentations/ |
| 10분 요약본 | 개발 결과 소개 10분 | [`index.html`](docs/presentations/ai-startup-camp-drone-10min/index.html) | https://lightminn.github.io/zetin-drone-presentations/10min/ |

주장과 그 근거의 대응은 각 덱의 `SOURCES.md`가 갖는다. 성숙도 경계(코드로 확인
/ 벤치·비행으로 확인 / 아직 확인 안 됨)를 그 문서가 구분해 두었으므로,
슬라이드에서 "검증"이라고 쓸 때는 그중 무엇인지 함께 밝힌다.

<!-- 옛 주소 https://lightminn.github.io/zetin-drone/ 와 /10min/ 은 위 주소로
     리다이렉트된다. 외부 쇼케이스가 옛 주소를 링크하고 있어 유지한다. -->

## 발표 실행

```bash
cd docs/presentations/ai-startup-camp-drone
./present.sh          # 로컬 서버를 띄우고 브라우저를 연다. 창을 닫으면 서버도 내려간다
./present.sh 8010     # 포트 지정
```

저장소만 복제하면 네트워크 없이 발표할 수 있다. 영상·이미지는 모두 `assets/`에
로컬 자산으로 들어 있다.

## 모바일 실습 랩

`docs/presentations/ai-startup-camp-drone/mobile-lab/`은 참가자가 QR로 접속해
동시에 참여하는 교육용 시뮬레이션이다. **실제 기체·펌웨어·지상국과 연결되지
않는다.** 운영 방법은 [해당 README](docs/presentations/ai-startup-camp-drone/mobile-lab/README.md),
서버 배포는 [Oracle 웹 호스팅 가이드](docs/oracle_web_hosting.md)를 따른다.

## 산출물 만들기

HTML이 편집 원본이고 PDF·PPTX는 내용이 확정된 뒤 만드는 배포 산출물이다.

```bash
python tools/build_presentation_site.py --output _site   # Pages와 동일한 정적 사이트
node docs/presentations/ai-startup-camp-drone/export_pptx.cjs
```

Manim 시각자료를 다시 렌더링하려면:

```bash
pip install -r docs/presentations/ai-startup-camp-drone/visualizations/requirements-render.txt
docs/presentations/ai-startup-camp-drone/visualizations/render_visualizations.sh
```

렌더 스크래치는 `media/`에 쌓이고 gitignore 대상이다. 덱은 `media/`가 아니라
`assets/`의 산출물을 참조한다.

## 확인

```bash
python -m unittest discover -s tools -p "test_*.py"
```

덱 레이아웃·영상 자동재생·PPTX 내보내기·모바일 랩·Oracle 배포를 검사한다.

## 설계 기록

`docs/superpowers/`의 날짜가 박힌 설계·계획 문서다. 사후 수정하지 않고, 틀린
것으로 밝혀지면 정정을 병기한다.
