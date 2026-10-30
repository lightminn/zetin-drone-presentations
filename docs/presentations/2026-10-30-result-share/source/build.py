#!/usr/bin/env python3
"""slides.json(agy가 쓴 문구) + 도식(SVG)을 8월 특강 덱 틀(UOS 템플릿)에 얹어 index.html 로 만든다."""
import html
import json
import sys
from pathlib import Path

SLIDES = Path(sys.argv[1])
OUT = Path(sys.argv[2])
MODE = sys.argv[3] if len(sys.argv) > 3 else "svg"   # svg | video | pdf
slides = json.loads(SLIDES.read_text())
E = html.escape

HEAD = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>자작 드론 비행제어와 신규 센서</title>
  <link rel="stylesheet" href="vendor/uos-slide-template/fonts/fonts.css">
  <link rel="stylesheet" href="vendor/uos-slide-template/_ds_bundle.css">
  <link rel="stylesheet" href="vendor/uos-slide-template/styles.css">
  <script src="vendor/uos-slide-template/_ds_bundle.js"></script>
  <style>
    body { margin: 0; background: #202225; font-family: "Noto Sans CJK KR", "Noto Sans KR", sans-serif; word-break: keep-all; overflow-wrap: normal; }
    .fill { width: 100%; height: 100%; min-width: 0; min-height: 0; }
    .page { display: grid; grid-template-rows: auto minmax(0,1fr) auto auto; gap: 10px; width: 100%; height: 100%; }
    .hl { font-size: 36px; font-weight: 800; color: var(--uos-ink); line-height: 1.2; padding: 2px 0 4px; }
    .uos-content-slide__title { font-weight: 800 !important; font-size: 22px !important; }
    .eyebrow { font-size: 19px; color: var(--uos-blue); font-weight: 800; letter-spacing: .02em; }
    .muted { color: var(--uos-ink-muted); }
    .panel { background: var(--uos-surface); border-radius: 4px; }
    .keyline { background: var(--uos-blue); color: #fff; border-radius: 4px; padding: 11px 22px; font-size: 22px; font-weight: 700; line-height: 1.35; }
    .foot { font-size: 15.5px; line-height: 1.3; color: var(--uos-ink-muted); padding-bottom: 2px; }
    .bt { font-size: 24px; font-weight: 800; line-height: 1.3; }
    .bb { font-size: 20px; line-height: 1.42; margin-top: 5px; }
    .blk { padding: 10px 0 12px; border-top: 1px solid var(--uos-rule); }
    .blk:first-child { border-top: 0; }
    .num { color: var(--uos-blue); font-weight: 800; font-size: 26px; }
    .step { display: flex; flex-direction: column; gap: 6px; padding: 12px 14px 12px; background: #f6f7f9; border-top: 5px solid var(--uos-blue); border-radius: 0 0 4px 4px; min-height: 0; }
    .tbl { width: 100%; border-collapse: collapse; font-size: 20px; }
    .tbl th { background: var(--uos-blue); color: #fff; text-align: left; padding: 11px 14px; font-weight: 800; }
    .tbl td { padding: 12px 14px; border-bottom: 1px solid var(--uos-rule); line-height: 1.35; vertical-align: middle; }
    .tbl td:first-child { font-weight: 800; }
    .tag { display: inline-block; padding: 3px 10px; border-radius: 3px; font-weight: 800; font-size: 18px; white-space: nowrap; }
    .t-fly { background: #e3efe6; color: #1f6a3a; }
    .t-bench { background: #e6eef8; color: #004094; }
    .t-sil { background: #fff1d6; color: #8a5f00; }
    .t-plan { background: #eceff3; color: #4a5568; }
    figure { margin: 0; }
    img, video { display: block; }
    svg text { font-family: "Noto Sans CJK KR", "Noto Sans KR", sans-serif; }
  </style>
</helmet>

<x-import component-from-global-scope="deck-stage" from="./deck-stage.js" width="1280" height="720" hint-size="100%,100%">
"""
TAIL = """
</x-import>
</x-dc>
</body>
</html>
"""

BLUE, TEAL, RED, AMBER, INK, MUTED = "#004094", "#16889a", "#b04a55", "#b47b00", "#172334", "#5a6678"

# ---------------------------------------------------------------- 도식 (SVG)


def svg_quad():
    """위에서 본 X자 쿼드콥터와 모터 회전 방향."""
    def motor(cx, cy, name, cw):
        col, fill, lab = (AMBER, "#fffaf0", "CW") if cw else (BLUE, "#f2f7fd", "CCW")
        arc = (f'<path d="M{cx-22} {cy-33} A34 34 0 1 1 {cx-33} {cy-18}" fill="none" stroke="{col}" stroke-width="4" marker-end="url(#a{"w" if cw else "c"})"/>' if cw else
               f'<path d="M{cx+22} {cy-33} A34 34 0 1 0 {cx+33} {cy-18}" fill="none" stroke="{col}" stroke-width="4" marker-end="url(#a{"w" if cw else "c"})"/>')
        return (f'<circle cx="{cx}" cy="{cy}" r="30" fill="{fill}" stroke="{col}" stroke-width="4"/>'
                f'<text x="{cx}" y="{cy-2}" text-anchor="middle" font-size="19" font-weight="800" fill="{INK}">{name}</text>'
                f'<text x="{cx}" y="{cy+18}" text-anchor="middle" font-size="15" font-weight="800" fill="{col}">{lab}</text>' + arc)
    return f"""<svg viewBox="0 0 360 260" role="img" aria-label="X자 쿼드콥터의 모터 배치와 회전 방향" style="width:100%;height:100%">
<defs>
<marker id="aw" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="{AMBER}"/></marker>
<marker id="ac" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="{BLUE}"/></marker>
</defs>
<line x1="90" y1="62" x2="270" y2="198" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>
<line x1="270" y1="62" x2="90" y2="198" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>
<rect x="148" y="100" width="64" height="60" rx="10" fill="{INK}" stroke="{BLUE}" stroke-width="3"/>
<path d="M180 108 L193 130 H167 Z" fill="#fff"/><text x="180" y="150" text-anchor="middle" font-size="14" font-weight="800" fill="#fff">앞</text>
{motor(88, 58, "M1", True)}{motor(272, 58, "M3", False)}{motor(88, 202, "M4", False)}{motor(272, 202, "M2", True)}
</svg>"""


def svg_filter():
    """상보필터: 자이로(고속 응답 · 적분 드리프트), 가속도계(중력 기준 · 진동 노이즈), 융합."""
    return f"""<svg viewBox="0 0 560 330" role="img" aria-label="자이로, 가속도계, 상보필터의 출력 비교" style="width:100%;height:100%">
<g font-size="20" font-weight="800">
<text x="16" y="52" fill="{RED}">자이로</text><text x="16" y="76" font-size="16" font-weight="500" fill="{MUTED}">고속 응답 · 적분 드리프트</text>
<text x="16" y="162" fill="{AMBER}">가속도계</text><text x="16" y="186" font-size="16" font-weight="500" fill="{MUTED}">중력 기준 · 진동 노이즈</text>
<text x="16" y="272" fill="#1f7a4a">상보필터</text><text x="16" y="296" font-size="16" font-weight="500" fill="{MUTED}">응답성과 기준 유지</text>
</g>
<g fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
<path d="M190 84 C260 78 300 66 370 52 S490 30 545 24" stroke="{RED}"/>
<path d="M190 168 l14 -14 l14 20 l14 -22 l14 22 l14 -20 l14 18 l14 -22 l14 22 l14 -18 l14 20 l14 -22 l14 20 l14 -18 l14 20 l14 -22 l14 22 l14 -18 l14 16" stroke="{AMBER}"/>
<path d="M190 296 C260 288 300 262 370 258 S490 250 545 250" stroke="#1f7a4a" stroke-width="5"/>
</g>
<g stroke="{MUTED}" stroke-dasharray="4 6" stroke-width="1.5"><line x1="190" y1="110" x2="545" y2="110"/><line x1="190" y1="214" x2="545" y2="214"/></g>
<text x="545" y="324" text-anchor="end" font-size="15" fill="{MUTED}">시간 →</text>
</svg>"""


def svg_drift():
    """스틱을 놓아도 기체가 흘러가고 조종자가 반대로 민다."""
    return f"""<svg viewBox="0 0 420 300" role="img" aria-label="스틱을 중립에 둬도 흘러가는 기체" style="width:100%;height:100%">
<defs>
<marker id="dr" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="16" refX="12" refY="8" orient="auto"><path d="M0,0 L16,8 L0,16 Z" fill="{RED}"/></marker>
<marker id="db" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="16" refX="12" refY="8" orient="auto"><path d="M0,0 L16,8 L0,16 Z" fill="{BLUE}"/></marker>
</defs>
<g transform="translate(150 140)">
<line x1="-46" y1="-46" x2="46" y2="46" stroke="{INK}" stroke-width="12" stroke-linecap="round"/><line x1="46" y1="-46" x2="-46" y2="46" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>
<rect x="-22" y="-20" width="44" height="40" rx="8" fill="{INK}"/>
<g fill="#f2f7fd" stroke="{BLUE}" stroke-width="3"><circle cx="-46" cy="-46" r="17"/><circle cx="46" cy="-46" r="17"/><circle cx="-46" cy="46" r="17"/><circle cx="46" cy="46" r="17"/></g>
</g>
<path d="M215 140 H388" stroke="{RED}" stroke-width="7" marker-end="url(#dr)"/>
<text x="300" y="112" text-anchor="middle" font-size="19" font-weight="800" fill="{RED}">수평 드리프트</text>
<path d="M388 205 H215" stroke="{BLUE}" stroke-width="7" stroke-dasharray="2 0" marker-end="url(#db)"/>
<text x="300" y="240" text-anchor="middle" font-size="19" font-weight="800" fill="{BLUE}">조종자 역방향 조향</text>
<text x="150" y="272" text-anchor="middle" font-size="17" fill="{MUTED}">기체 상면도</text>
</svg>"""


def svg_alloc():
    """모터 출력 범위에서 roll/pitch를 먼저 나누고 남은 범위에 yaw."""
    def bar(y, rp, yaw, label):
        w = 520
        return (f'<text x="0" y="{y-12}" font-size="17" font-weight="800" fill="{INK}">{label}</text>'
                f'<rect x="0" y="{y}" width="{w}" height="46" rx="4" fill="#fff" stroke="{MUTED}" stroke-width="2"/>'
                f'<rect x="0" y="{y}" width="{rp}" height="46" rx="4" fill="{BLUE}"/>'
                f'<text x="{rp/2}" y="{y+30}" text-anchor="middle" font-size="18" font-weight="800" fill="#fff">roll·pitch</text>'
                + (f'<rect x="{rp}" y="{y}" width="{yaw}" height="46" fill="{AMBER}"/><text x="{rp+yaw/2}" y="{y+30}" text-anchor="middle" font-size="18" font-weight="800" fill="#fff">yaw</text>' if yaw > 50 else
                   f'<rect x="{rp}" y="{y}" width="{max(yaw,0)}" height="46" fill="{AMBER}"/>' ))
    return f"""<svg viewBox="0 0 540 300" role="img" aria-label="모터 출력 여유에 따른 roll pitch yaw 배분" style="width:100%;height:100%">
<g transform="translate(10 30)">
{bar(26, 190, 250, "출력 여유가 클 때")}
{bar(126, 420, 80, "출력 여유가 작을 때")}
<text x="0" y="226" font-size="17" fill="{MUTED}">출력 허용 범위에서 roll·pitch를 우선 배분하고 잔여 범위에 yaw 배분</text>
</g>
</svg>"""


def svg_sensor():
    """3901-L0X: 바닥을 내려다보는 광류 센서와 거리 센서."""
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="{MUTED}"/>' for x, y in
                   [(110, 292), (150, 300), (205, 290), (265, 301), (320, 291), (372, 299), (430, 290), (480, 300)])
    return f"""<svg viewBox="0 0 580 330" role="img" aria-label="바닥을 내려다보는 광류 센서와 거리 센서" style="width:100%;height:100%">
<defs><marker id="fl" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="11" refY="7" orient="auto"><path d="M0,0 L14,7 L0,14 Z" fill="{RED}"/></marker></defs>
<rect x="190" y="28" width="200" height="40" rx="8" fill="{INK}"/><text x="290" y="54" text-anchor="middle" font-size="17" font-weight="800" fill="#fff">기체</text>
<rect x="262" y="68" width="56" height="22" rx="4" fill="{BLUE}"/><text x="332" y="85" font-size="16" font-weight="800" fill="{BLUE}">3901-L0X</text>
<path d="M290 90 L130 296 H450 Z" fill="{TEAL}" opacity=".13"/>
<line x1="290" y1="90" x2="130" y2="296" stroke="{TEAL}" stroke-width="2.5"/><line x1="290" y1="90" x2="450" y2="296" stroke="{TEAL}" stroke-width="2.5"/>
<line x1="290" y1="90" x2="290" y2="296" stroke="{AMBER}" stroke-width="4" stroke-dasharray="9 6"/>
<line x1="60" y1="296" x2="540" y2="296" stroke="{INK}" stroke-width="3"/>{dots}
<path d="M200 270 H350" stroke="{RED}" stroke-width="5" marker-end="url(#fl)"/>
<text x="236" y="136" text-anchor="end" font-size="17" font-weight="800" fill="{TEAL}">광류 PMW3901</text><text x="236" y="158" text-anchor="end" font-size="15" fill="{MUTED}">시야각 42°</text>
<text x="346" y="136" font-size="17" font-weight="800" fill="{AMBER}">거리 VL53L0X</text><text x="346" y="158" font-size="15" fill="{MUTED}">높이 80~2000 mm</text>
<text x="275" y="322" text-anchor="middle" font-size="15" fill="{RED}" font-weight="800">지면 텍스처 이동량 → 수평 속도</text>
</svg>"""


def svg_frames():
    """프레임 주기와 유효성 판정 규칙."""
    t1 = "".join(f'<line x1="{20+i*52}" y1="46" x2="{20+i*52}" y2="76" stroke="{TEAL}" stroke-width="5"/>' for i in range(10))
    t2 = "".join(f'<line x1="{20+i*18.2:.1f}" y1="124" x2="{20+i*18.2:.1f}" y2="154" stroke="{AMBER}" stroke-width="4"/>' for i in range(28))
    return f"""<svg viewBox="0 0 520 330" role="img" aria-label="광류와 거리 프레임 주기와 거리 유효성 규칙" style="width:100%;height:100%">
<text x="20" y="30" font-size="18" font-weight="800" fill="{TEAL}">광류 약 10 Hz (99~102 ms)</text>{t1}
<text x="20" y="108" font-size="18" font-weight="800" fill="{AMBER}">거리 약 28 Hz (약 35 ms)</text>{t2}
<rect x="20" y="190" width="230" height="110" rx="6" fill="#e3efe6" stroke="#1f7a4a" stroke-width="2"/>
<text x="135" y="220" text-anchor="middle" font-size="18" font-weight="800" fill="#1f6a3a">거리 1.2 m</text>
<text x="135" y="246" text-anchor="middle" font-size="16" fill="{INK}">0 이상이면 유효</text>
<text x="135" y="276" text-anchor="middle" font-size="17" font-weight="800" fill="#1f6a3a">고도값으로 사용</text>
<rect x="270" y="190" width="230" height="110" rx="6" fill="#f8e6e8" stroke="{RED}" stroke-width="2"/>
<text x="385" y="220" text-anchor="middle" font-size="18" font-weight="800" fill="{RED}">거리 −1 · 품질 255</text>
<text x="385" y="246" text-anchor="middle" font-size="16" fill="{INK}">음수는 측정 범위 밖</text>
<text x="385" y="276" text-anchor="middle" font-size="17" font-weight="800" fill="{RED}">품질값 미사용</text>
</svg>"""


def svg_tilt():
    """기울어진 기체와 속도 계산식."""
    return f"""<svg viewBox="0 0 560 230" role="img" aria-label="기울어진 기체와 수평 속도 계산식" style="width:100%;height:100%">
<defs><marker id="tb" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="11" refY="7" orient="auto"><path d="M0,0 L14,7 L0,14 Z" fill="{BLUE}"/></marker></defs>
<line x1="20" y1="200" x2="270" y2="200" stroke="{INK}" stroke-width="3"/>
<g transform="rotate(-14 130 70)"><rect x="70" y="56" width="120" height="26" rx="8" fill="{INK}"/><rect x="118" y="82" width="24" height="12" rx="3" fill="{BLUE}"/></g>
<line x1="130" y1="92" x2="130" y2="200" stroke="{AMBER}" stroke-width="4" stroke-dasharray="8 6"/>
<text x="140" y="150" font-size="17" font-weight="800" fill="{AMBER}">높이</text>
<path d="M150 40 H250" stroke="{BLUE}" stroke-width="5" marker-end="url(#tb)"/><text x="200" y="30" text-anchor="middle" font-size="16" font-weight="800" fill="{BLUE}">수평 속도</text>
<g font-size="20" font-weight="800" fill="{INK}">
<text x="300" y="74">수평 속도</text>
<text x="300" y="112" fill="{BLUE}">= (광류 − 자이로 회전분)</text>
<text x="300" y="146" fill="{AMBER}">× 지면까지 높이</text>
</g>
<text x="300" y="190" font-size="16" fill="{MUTED}">자세 변화만으로도 광류가 생기므로 회전 성분을 차감</text>
</svg>"""


def svg_camera():
    """BEC 전원, 같은 와이파이로 영상 전송. 장착 위치만 미정."""
    arcs = "".join(f'<path d="M{290-r} {86-r*0.55:.1f} A{r} {r} 0 0 1 {290+r} {86-r*0.55:.1f}" fill="none" stroke="{BLUE}" stroke-width="4" stroke-linecap="round"/>' for r in (14, 28, 42))
    return f"""<svg viewBox="0 0 580 330" role="img" aria-label="카메라 보드의 전원과 와이파이 영상 전송 구성도" style="width:100%;height:100%">
<defs><marker id="cp" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="11" refY="7" orient="auto"><path d="M0,0 L14,7 L0,14 Z" fill="{RED}"/></marker></defs>
<rect x="14" y="36" width="190" height="130" rx="10" fill="#eaf2fb" stroke="{BLUE}" stroke-width="4"/>
<text x="109" y="76" text-anchor="middle" font-size="20" font-weight="800" fill="{BLUE}">비행제어 PCB</text>
<text x="109" y="104" text-anchor="middle" font-size="16" fill="{INK}">ESP32-S3</text><text x="109" y="130" text-anchor="middle" font-size="16" font-weight="800" fill="{BLUE}">와이파이를 엶</text>
<rect x="376" y="36" width="190" height="130" rx="10" fill="#eef9fb" stroke="{TEAL}" stroke-width="4"/>
<text x="471" y="76" text-anchor="middle" font-size="20" font-weight="800" fill="{TEAL}">카메라 보드</text>
<text x="471" y="104" text-anchor="middle" font-size="16" fill="{INK}">ESP32-CAM 호환보드</text><text x="471" y="130" text-anchor="middle" font-size="16" font-weight="800" fill="{TEAL}">같은 와이파이에 접속</text>
{arcs}
<circle cx="290" cy="94" r="5" fill="{BLUE}"/>
<text x="290" y="132" text-anchor="middle" font-size="16" font-weight="800" fill="{BLUE}">영상 전송</text>
<rect x="195" y="236" width="190" height="62" rx="8" fill="#fff" stroke="{RED}" stroke-width="3"/>
<text x="290" y="262" text-anchor="middle" font-size="18" font-weight="800" fill="{RED}">ESC의 BEC</text><text x="290" y="284" text-anchor="middle" font-size="15" fill="{MUTED}">5 V 전원</text>
<path d="M240 234 L120 172" stroke="{RED}" stroke-width="4" marker-end="url(#cp)"/>
<path d="M385 250 L520 172" stroke="{RED}" stroke-width="4" marker-end="url(#cp)"/>
<text x="505" y="236" text-anchor="middle" font-size="16" font-weight="800" fill="{RED}">전원만 공급</text>
<text x="471" y="154" text-anchor="middle" font-size="15" fill="{MUTED}">장착 위치 ? 미정</text>
</svg>"""


def svg_poshold():
    """오늘 테더 비행(실로그): 위 막대 = 위치 유지 최장 연속 시간, 아래 막대 = 켠 구간 대 그 밖 구간의 수평 이동 속도."""
    d = json.loads((Path(__file__).parent / "poshold_stats.json").read_text())
    n = len(d)
    x0, x1 = 70, 566
    slot = (x1 - x0) / n
    cx = lambda i: x0 + slot * (i + 0.5)
    out = []
    ya0, ya1, amax = 38, 140, 25.0
    Ya = lambda v: ya1 - (ya1 - ya0) * v / amax
    out.append(f'<text x="{x0-50}" y="18" font-size="16" font-weight="800" fill="{INK}">위치 유지가 한 번에 이어진 최장 시간 (초)</text>')
    for v in (0, 10, 20):
        out.append(f'<line x1="{x0}" y1="{Ya(v):.1f}" x2="{x1}" y2="{Ya(v):.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 6"/>'
                   f'<text x="{x0-8}" y="{Ya(v)+5:.1f}" text-anchor="end" font-size="14" fill="{MUTED}">{v}</text>')
    for i, o in enumerate(d):
        v = o["longest_active_s"]
        if v > 0:
            out.append(f'<rect x="{cx(i)-20:.1f}" y="{Ya(v):.1f}" width="40" height="{ya1-Ya(v):.1f}" fill="{BLUE}"/>'
                       f'<text x="{cx(i):.1f}" y="{Ya(v)-6:.1f}" text-anchor="middle" font-size="14" font-weight="800" fill="{BLUE}">{v:.1f}</text>')
        else:
            out.append(f'<text x="{cx(i):.1f}" y="{ya1-8}" text-anchor="middle" font-size="14" font-weight="800" fill="{MUTED}">끔</text>')
    yb0, yb1, bmax = 216, 292, 0.25
    Yb = lambda v: yb1 - (yb1 - yb0) * v / bmax
    out.append(f'<text x="{x0-50}" y="188" font-size="16" font-weight="800" fill="{INK}">수평 이동 속도 (m/s) · 낮을수록 덜 움직임</text>')
    out.append(f'<rect x="{x0-46}" y="198" width="14" height="10" fill="{BLUE}"/><text x="{x0-28}" y="208" font-size="14" fill="{INK}">위치 유지를 켠 구간</text>'
               f'<rect x="{x0+116}" y="198" width="14" height="10" fill="{AMBER}"/><text x="{x0+134}" y="208" font-size="14" fill="{INK}">그 밖 구간(이착륙 포함)</text>')
    for v in (0, 0.1, 0.2):
        out.append(f'<line x1="{x0}" y1="{Yb(v):.1f}" x2="{x1}" y2="{Yb(v):.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 6"/>'
                   f'<text x="{x0-8}" y="{Yb(v)+5:.1f}" text-anchor="end" font-size="14" fill="{MUTED}">{v:g}</text>')
    for i, o in enumerate(d):
        for key, col, dx in (("rms_active", BLUE, -17), ("rms_other", AMBER, 17)):
            v = o[key]
            if v is None:
                continue
            out.append(f'<rect x="{cx(i)+dx-16:.1f}" y="{Yb(v):.1f}" width="32" height="{yb1-Yb(v):.1f}" fill="{col}"/>'
                       f'<text x="{cx(i)+dx:.1f}" y="{Yb(v)-5:.1f}" text-anchor="middle" font-size="13" fill="{INK}">{v:.2f}</text>')
        lab = f"{i+1}회" + (" · 끔" if o["longest_active_s"] == 0 else "")
        out.append(f'<text x="{cx(i):.1f}" y="{yb1+22}" text-anchor="middle" font-size="15" fill="{MUTED}">{lab}</text>')
    out.append(f'<text x="{(x0+x1)/2}" y="343" text-anchor="middle" font-size="16" font-weight="800" fill="{BLUE}">켠 구간의 속도가 5회 모두 더 낮음 (평균 약 32 %)</text>')
    return f"""<svg viewBox="0 0 580 352" role="img" aria-label="비행별 위치 유지 최장 시간과 수평 이동 속도 비교" style="width:100%;height:100%">{"".join(out)}</svg>"""


def svg_loops():
    """제어 루프 블록: 목표 각도 → 바깥(250Hz) → 안쪽(1kHz) → 믹서 → 모터."""
    def box(x, w, a, b, col):
        return (f'<rect x="{x}" y="14" width="{w}" height="74" rx="8" fill="#fff" stroke="{col}" stroke-width="3"/>'
                f'<text x="{x+w/2}" y="46" text-anchor="middle" font-size="18" font-weight="800" fill="{INK}">{a}</text>'
                f'<text x="{x+w/2}" y="70" text-anchor="middle" font-size="14" fill="{MUTED}">{b}</text>')
    return f"""<svg viewBox="0 0 560 102" role="img" aria-label="바깥 각도 루프에서 안쪽 각속도 루프와 믹서로 이어지는 제어 구조" style="width:100%;height:100%">
<defs><marker id="lp" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="11" refY="7" orient="auto"><path d="M0,0 L14,7 L0,14 Z" fill="{MUTED}"/></marker></defs>
{box(0, 118, "바깥 루프", "각도 · 250 Hz", BLUE)}{box(148, 118, "안쪽 루프", "각속도 · 1 kHz", BLUE)}{box(296, 110, "믹서", "4개로 배분", AMBER)}{box(436, 118, "모터 출력", "ESC PWM", TEAL)}
<g stroke="{MUTED}" stroke-width="3" marker-end="url(#lp)"><path d="M120 51 H146"/><path d="M268 51 H294"/><path d="M408 51 H434"/></g>
</svg>"""


# ---------------------------------------------------------------- 조각

ASSETS = {
    "photo:pcb-built": ("img", "assets/pcb-built.jpeg", "left center", "scale(1.30)"),
    "photo:assembled-bench": ("img", "assets/assembled-bench.jpeg", "center", ""),
    "photo:cad-top": ("img", "assets/cad-top.png", "center", ""),
    "photo:frame-iterations": ("img", "assets/frame-iterations.jpeg", "center", ""),
    "chart:telemetry-motor-balance": ("img", "assets/telemetry-motor-balance.png", "center", ""),
    "video:hover_demo": ("video", "assets/hover_demo.mp4", "center", ""),
}
DIAGRAMS = {3: svg_quad, 4: svg_filter, 6: None, 7: svg_sensor, 8: svg_frames, 9: svg_tilt, 10: svg_poshold, 11: svg_camera}


ANIM = {4: "slide04", 7: "slide07", 8: "slide08"}   # 영상으로 만든 장(3·6장은 별도 처리). 9·10·11장은 정지 도식


def anim_el(name):
    """Manim 영상(웹) 또는 대표 프레임(PDF)."""
    if MODE == "video":
        return (f'<video class="anim" data-anim src="assets/anim/{name}.mp4" poster="assets/anim/{name}.jpg" muted loop playsinline autoplay '
                f'preload="auto" style="width:100%;height:100%;object-fit:contain;background:#ECEAE6"></video>')
    return f'<img src="assets/anim/{name}.jpg" alt="" style="width:100%;height:100%;object-fit:contain;background:#ECEAE6">'


def paras(text):
    return E(text).replace("\n", "<br>")


def media_el(visual, n):
    if MODE != "svg" and n in ANIM:
        return anim_el(ANIM[n])
    if n in (4, 7, 8, 10, 11):
        return DIAGRAMS[n]()
    for key, (kind, src, pos, tf) in ASSETS.items():
        if visual.startswith(key):
            if kind == "video":
                return (f'<video src="{src}" poster="assets/hover_poster.jpg" controls loop muted playsinline preload="metadata" '
                        f'style="width:100%;height:100%;object-fit:cover;background:#06152f;border-radius:4px"></video>')
            style = f"width:100%;height:100%;object-fit:cover;object-position:{pos};"
            if tf:
                style += f"transform:{tf};transform-origin:{pos};"
            return f'<img src="{src}" alt="" style="{style}">'
    fn = DIAGRAMS.get(n)
    return fn() if fn else ""


def blocks_html(blocks, numbered=False):
    out = []
    for i, b in enumerate(blocks, 1):
        head = (f'<span class="num">{i:02d}</span> ' if numbered else "") + paras(b["title"])
        out.append(f'<div class="blk"><div class="bt">{head}</div><div class="bb muted">{paras(b["body"])}</div></div>')
    return "".join(out)


def page(s, main):
    eyebrow = f'<div class="hl">{paras(s["headline"])}</div>'
    band = f'<div class="keyline">{E(s["band"])}</div>' if s["band"] else "<div></div>"
    foot = f'<div class="foot">{E(s["footnote"])}</div>' if s["footnote"] else "<div></div>"
    return f'<div class="page">{eyebrow}{main}{band}{foot}</div>'


def L_media(s):
    n = s["n"]
    fig = media_el(s["visual"], n)
    cap = ""
    main = (f'<div style="display:grid;grid-template-columns:1.12fr .88fr;gap:26px;min-height:0">'
            f'<div class="panel" style="padding:{0 if (MODE != "svg" and n in ANIM) else 10}px;min-height:0;overflow:hidden;display:flex;align-items:center;justify-content:center">{fig}</div>'
            f'<div style="display:flex;flex-direction:column;justify-content:center;min-height:0">{blocks_html(s["blocks"])}</div></div>')
    return page(s, main)


def L_steps(s):
    n = s["n"]
    fig = media_el(s["visual"], n)
    extra = ""
    if MODE != "svg" and n == 3:
        extra = f'<div class="panel" style="padding:0;min-height:0;overflow:hidden">{anim_el("slide03")}</div>'
    elif n == 3:
        extra = (f'<div style="display:grid;grid-template-columns:.62fr 1fr;gap:20px;min-height:0">'
                 f'<div class="panel" style="padding:6px;min-height:0">{svg_quad()}</div>'
                 f'<div style="display:flex;flex-direction:column;justify-content:center;gap:14px">'
                 f'<div class="panel" style="padding:12px 18px;font-size:21px;line-height:1.55;font-weight:700">'
                 f'<span class="muted" style="font-weight:500;font-size:17px">T 합추력, R·P·Y 보정량</span><br>'
                 f'M1 = T − P + R − Y　M2 = T + P − R − Y<br>M3 = T − P − R + Y　M4 = T + P + R + Y</div>'
                 f'<div style="height:96px">{svg_loops()}</div></div></div>')
    elif n == 9:
        extra = f'<div class="panel" style="padding:8px;min-height:0">{svg_tilt()}</div>'
    cols = "".join(
        f'<div class="step"><div class="num">{i:02d}</div><div class="bt" style="font-size:21px">{paras(b["title"])}</div>'
        f'<div class="bb muted" style="font-size:18px;margin-top:0">{paras(b["body"])}</div></div>'
        for i, b in enumerate(s["blocks"], 1))
    main = (f'<div style="display:grid;grid-template-rows:minmax(0,1fr) auto;gap:14px;min-height:0">{extra}'
            f'<div style="display:grid;grid-template-columns:repeat({len(s["blocks"])},1fr);gap:12px">{cols}</div></div>')
    return page(s, main)


def L_compare(s):
    n = s["n"]
    panels = []
    if n == 6:
        figs = [anim_el("slide06L"), anim_el("slide06R")] if MODE != "svg" else [svg_drift(), svg_alloc()]
    elif n == 10:
        figs = [CARD10_L, CARD10_R]
    else:
        figs = ["", ""]
    for fig, b in zip(figs, s["blocks"]):
        panels.append(f'<div style="display:flex;flex-direction:column;gap:10px;min-height:0">'
                      f'<div class="panel" style="flex:1;min-height:0;padding:{0 if (MODE != "svg" and n == 6) else 10}px;display:flex;align-items:center;justify-content:center;overflow:hidden">{fig}</div>'
                      f'<div><div class="bt">{paras(b["title"])}</div><div class="bb muted">{paras(b["body"])}</div></div></div>')
    main = f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:26px;min-height:0">{"".join(panels)}</div>'
    return page(s, main)


CARD10_L = """<div style="width:100%;padding:8px 14px;display:flex;flex-direction:column;gap:12px;font-size:20px;line-height:1.4">
<div style="font-weight:800;color:#004094;font-size:21px">시험 조건</div>
<div>높이 0.5 m에서 호버, 초기 0.3 m/s로 이동, 트림 오차 1°</div>
<div style="font-weight:800;color:#1f6a3a;font-size:21px;margin-top:6px">합격 기준</div>
<div>12초 뒤 속도 0.05 m/s 미만<br>최대 위치 오차 0.5 m 미만</div></div>"""
CARD10_R = """<div style="width:100%;padding:8px 14px;display:flex;flex-direction:column;gap:12px;font-size:20px;line-height:1.4">
<div style="font-weight:800;color:#8a5f00;font-size:21px">광류 프레임 23 % 유실·손상</div>
<div>폭주하지 않음 (최대 위치 오차 1.5 m 미만 기준)</div>
<div style="font-weight:800;color:#b04a55;font-size:21px;margin-top:6px">보정 부호를 일부러 반대로</div>
<div>같은 조건에서 위치 오차가 커짐 (음성 대조)</div></div>"""


def tag_for(text):
    if "실비행" in text:
        return "t-fly"
    if "벤치" in text:
        return "t-bench"
    if "시뮬" in text:
        return "t-sil"
    return "t-plan"


def L_table(s):
    t = s["table"]
    head = "".join(f"<th>{E(h)}</th>" for h in t["head"])
    rows = []
    for r in t["rows"]:
        cells = []
        for j, c in enumerate(r):
            if len(r) == 3 and j == 1:
                cells.append(f'<td><span class="tag {tag_for(c)}">{E(c)}</span></td>')
            else:
                cells.append(f"<td>{E(c)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    main = (f'<div style="display:flex;align-items:center;min-height:0"><table class="tbl"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')
    return page(s, main)


def L_list3(s):
    return L_media(s)


def section_html(s, inner, notes):
    label = E(s["section"] or s["headline"].split("\n")[0])
    return (f'<section data-label="{label}" data-screen-label="{s["n"]:02d}" '
            f'data-speaker-notes="{E(s["script"], quote=True)}" style="background:#fff">\n{inner}\n</section>')


def render(s):
    lay = s["layout"]
    if lay == "cover":
        inner = (f'<x-import component-from-global-scope="UOSSlideDS.TitleSlide" hint-size="100%,100%" '
                 f'subtitle="{E(s.get("subtitle", ""), quote=True)}" date="2026.10.30 결과보고회" title="{E(s["headline"], quote=True)}"></x-import>')
        return section_html(s, inner, s["script"])
    if lay == "closing":
        body = (f'<div style="display:grid;place-items:center;height:100%;text-align:center;font-size:44px;font-weight:800;color:{BLUE};line-height:1.5">'
                f'{paras(s["headline"])}</div>')
        inner = (f'<x-import component-from-global-scope="UOSSlideDS.ContentSlide" hint-size="100%,100%" title="">'
                 f'<div class="fill">{body}</div></x-import>')
        return section_html(s, inner, s["script"])
    fn = {"media": L_media, "steps": L_steps, "compare": L_compare, "table": L_table, "list3": L_list3}[lay]
    inner = (f'<x-import component-from-global-scope="UOSSlideDS.ContentSlide" hint-size="100%,100%" title="{E(s["section"], quote=True)}">'
             f'<div class="fill">{fn(s)}</div></x-import>')
    return section_html(s, inner, s["script"])


OUT.write_text(HEAD + "\n".join(render(s) for s in slides) + TAIL)
print("wrote", OUT, len(slides), "slides")
