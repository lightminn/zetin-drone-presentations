"""덱(UOS 템플릿) 도식과 같은 색·글꼴로 맞춘 Manim 공통 요소."""
from manim import *

import os
config.background_color = ManimColor("#ECEAE6")
_a = float(os.environ.get("ASPECT", "1.7778"))
config.frame_height = 8.0
config.frame_width = 8.0 * _a  # 덱의 .panel 배경(--uos-surface)과 같게

BLUE = ManimColor("#004094")
TEAL = ManimColor("#16889a")
RED = ManimColor("#b04a55")
AMBER = ManimColor("#b47b00")
GREEN = ManimColor("#1f7a4a")
INK = ManimColor("#172334")
MUTED = ManimColor("#5a6678")
PAPER = ManimColor("#ffffff")
FONT = "Noto Sans CJK KR"


def T(s, size=30, color=INK, bold=False, **kw):
    """한글 글꼴 고정 텍스트."""
    return Text(s, font=FONT, font_size=size, color=color, weight=BOLD if bold else NORMAL, **kw)


def card(w, h, stroke=BLUE, fill=PAPER, r=0.18, sw=5):
    return RoundedRectangle(width=w, height=h, corner_radius=r, stroke_color=stroke, stroke_width=sw,
                            fill_color=fill, fill_opacity=1)


def labeled(box_w, box_h, title, sub=None, stroke=BLUE, tsize=30, ssize=22, tcolor=INK):
    b = card(box_w, box_h, stroke=stroke)
    t = T(title, tsize, tcolor, True)
    g = VGroup(b, t)
    if sub:
        s = T(sub, ssize, MUTED)
        t.move_to(b.get_center() + UP * box_h * 0.18)
        s.move_to(b.get_center() + DOWN * box_h * 0.2)
        g.add(s)
    return g


def quad_top(scale=1.0, with_labels=True):
    """위에서 본 X자 쿼드콥터. 반환: VGroup, 모터 리스트(프롭 회전용), 라벨."""
    s = scale
    arm1 = Line(UL * 1.9 * s, DR * 1.9 * s, stroke_width=22 * s, color=INK).set_cap_style(CapStyleType.ROUND)
    arm2 = Line(UR * 1.9 * s, DL * 1.9 * s, stroke_width=22 * s, color=INK).set_cap_style(CapStyleType.ROUND)
    body = RoundedRectangle(width=1.5 * s, height=1.5 * s, corner_radius=0.2 * s, fill_color=INK, fill_opacity=1,
                            stroke_color=BLUE, stroke_width=4)
    nose = Triangle(fill_color=PAPER, fill_opacity=1, stroke_width=0).scale(0.28 * s).move_to(body.get_center() + UP * 0.2 * s)
    pos = {"M1": UL, "M2": DR, "M3": UR, "M4": DL}
    cw = {"M1": True, "M2": True, "M3": False, "M4": False}
    motors, props, labels = {}, {}, {}
    for k, d in pos.items():
        c = d * 1.9 * s
        col = AMBER if cw[k] else BLUE
        disc = Circle(radius=0.62 * s, stroke_color=col, stroke_width=5, fill_color=PAPER, fill_opacity=1).move_to(c)
        blade = VGroup(Line(LEFT * 0.55 * s, RIGHT * 0.55 * s, stroke_width=9 * s, color=col),
                       Line(UP * 0.55 * s, DOWN * 0.55 * s, stroke_width=9 * s, color=col)).move_to(c)
        motors[k] = disc
        props[k] = blade
        if with_labels:
            labels[k] = VGroup(T(k, 30 * s, INK, True), T("CW" if cw[k] else "CCW", 24 * s, col, True)).arrange(DOWN, buff=0.04 * s)
            labels[k].move_to(c + (UP if d[1] > 0 else DOWN) * 1.0 * s)
    g = VGroup(arm1, arm2, body, nose, *motors.values(), *props.values(), *labels.values())
    return g, motors, props, labels


def glow_dot(color, r=0.12):
    return Dot(radius=r, color=color)


def spin(mob, rate=8.0, direction=1):
    """프롭 회전 updater."""
    mob.add_updater(lambda m, dt: m.rotate(direction * rate * dt))
    return mob
