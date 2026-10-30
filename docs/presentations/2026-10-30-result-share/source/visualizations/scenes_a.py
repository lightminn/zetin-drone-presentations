from style import *
import numpy as np


class Slide03(Scene):
    """네 로터 추력 배분(롤·피치·요)과 캐스케이드 루프. 와이드(2400x480)."""

    def construct(self):
        quad, motors, props, labels = quad_top(1.0)
        quad.move_to(LEFT * 16.0)
        # 모터별 추력 값과 막대
        th = {k: ValueTracker(0.55) for k in motors}
        bars = {}
        for k in motors:
            c = motors[k].get_center()
            side = LEFT if c[0] < quad.get_center()[0] else RIGHT
            base = c + side * 1.35 + DOWN * 1.0
            frame = Rectangle(width=0.38, height=2.0, stroke_color=MUTED, stroke_width=2, fill_opacity=0).move_to(base + UP * 1.0)
            bar = Rectangle(width=0.38, height=1.0, stroke_width=0, fill_color=BLUE, fill_opacity=1)
            def upd(m, b=base, v=th[k]):
                h = max(v.get_value() * 2.0, 0.04)
                m.become(Rectangle(width=0.38, height=h, stroke_width=0, fill_color=BLUE, fill_opacity=1).move_to(b + UP * h / 2))
            bar.add_updater(upd)
            bars[k] = (frame, bar, base)
        # 프롭 회전: 추력에 비례
        for k, p in props.items():
            direction = -1 if k in ("M1", "M2") else 1
            p.add_updater(lambda m, dt, v=th[k], d=direction: m.rotate(d * (4 + 26 * v.get_value()) * dt))

        # 수식 열
        def line(name, sgn):
            terms = [T(name + " =", 44, INK, True), T("T", 44, BLUE, True)]
            for sym, s in zip("PRY", sgn):
                terms.append(T(("+ " if s > 0 else "− ") + sym, 44, MUTED, True))
            return VGroup(*terms).arrange(RIGHT, buff=0.28)
        lines = VGroup(line("M1", (-1, +1, -1)), line("M2", (+1, -1, -1)), line("M3", (-1, -1, +1)), line("M4", (+1, +1, +1)))
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to(LEFT * 5.2 + DOWN * 0.3)
        note = T("T 합추력 · R 롤 · P 피치 · Y 요", 28, MUTED).next_to(lines, DOWN, buff=0.35, aligned_edge=LEFT)
        title = T("합추력 T", 50, BLUE, True).move_to(LEFT * 5.2 + UP * 3.0).align_to(lines, LEFT)

        # 제어 루프 블록
        bx = [8.6, 12.9, 17.2, 21.5]
        names = [("바깥 루프", "각도 · 250 Hz", BLUE), ("안쪽 루프", "각속도 · 1 kHz", BLUE), ("믹서", "모터 4개로 배분", AMBER), ("모터", "ESC PWM", TEAL)]
        boxes = VGroup(*[labeled(3.8, 2.4, n, s, stroke=c, tsize=36, ssize=26) for (n, s, c) in names])
        for b, x in zip(boxes, bx):
            b.move_to(RIGHT * (x - 3.4) + DOWN * 0.3)
        boxes.shift(LEFT * 0.0)
        arrows = VGroup(*[Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.12, color=MUTED, stroke_width=5,
                                max_tip_length_to_length_ratio=0.35) for i in range(3)])
        loop_title = T("바깥 루프 1회마다 안쪽 루프 4회", 32, MUTED).next_to(boxes, UP, buff=0.6)

        # 루프 점멸(바깥 250Hz : 안쪽 1kHz = 1 : 4)
        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)

        def flash_updater(period):
            def f(m):
                ph = (clock.get_value() % period) / period
                m.set_stroke(width=5 + 9 * max(0, 1 - ph * 5), opacity=1)
            return f
        boxes[0][0].add_updater(flash_updater(2.0))
        boxes[1][0].add_updater(flash_updater(0.5))

        self.play(FadeIn(quad), run_time=0.6)
        self.add(*[bars[k][0] for k in motors], *[bars[k][1] for k in motors])
        self.play(FadeIn(lines), FadeIn(title), FadeIn(note), run_time=0.6)
        self.play(FadeIn(boxes), FadeIn(arrows), FadeIn(loop_title), run_time=0.7)
        self.wait(1.6)

        def phase(name, color, delta, colored_syms):
            # delta: 모터별 추력 변화, colored_syms: 수식에서 강조할 항 인덱스(P=2,R=3,Y=4)
            anims = [th[k].animate.set_value(0.55 + d) for k, d in delta.items()]
            anims.append(Transform(title, T(name, 50, color, True).move_to(title).align_to(lines, LEFT)))
            for ln in lines:
                for i in (2, 3, 4):
                    anims.append(ln[i].animate.set_color(color if i == colored_syms else MUTED))
            self.play(*anims, run_time=1.0)
            self.wait(2.0)

        phase("롤 R: 좌우 출력 차이", AMBER, {"M1": .28, "M4": .28, "M2": -.28, "M3": -.28}, 3)
        phase("피치 P: 앞뒤 출력 차이", RED, {"M2": .28, "M4": .28, "M1": -.28, "M3": -.28}, 2)
        phase("요 Y: CW·CCW 쌍 출력 차이", GREEN, {"M3": .28, "M4": .28, "M1": -.28, "M2": -.28}, 4)
        # 호버로 복귀
        self.play(*[th[k].animate.set_value(0.55) for k in th], Transform(title, T("합추력 T", 50, BLUE, True).move_to(title).align_to(lines, LEFT)),
                  *[lines[j][i].animate.set_color(MUTED) for j in range(4) for i in (2, 3, 4)], run_time=1.0)
        self.wait(1.5)
