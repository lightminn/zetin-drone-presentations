from style import *
import numpy as np
import json
from pathlib import Path


def lane_poly(ts, ys, x0, x1, tmax, yc, yscale, color, sw=6):
    pts = [np.array([x0 + (x1 - x0) * t / tmax, yc + y * yscale, 0]) for t, y in zip(ts, ys)]
    m = VMobject(stroke_color=color, stroke_width=sw)
    m.set_points_as_corners(pts)
    return m


class Slide04(Scene):
    """상보필터: 자이로(고속·드리프트), 가속도계(기준·진동), 융합. ASPECT=1.55"""

    def construct(self):
        tmax, dt = 10.0, 0.02
        ts = np.arange(0, tmax + dt, dt)
        rng = np.random.default_rng(7)
        true = np.interp(ts, [0, 2.0, 3.6, 6.4, 8.0, 10], [0, 0, 10, 10, 0, 0])
        true = np.convolve(true, np.ones(15) / 15, mode="same")
        rate = np.gradient(true, dt)
        gyro_meas = rate + 0.6  # 바이어스 0.6 deg/s
        gyro = np.cumsum(gyro_meas) * dt
        noise = rng.normal(0, 1.3, len(ts)) * (1 + 2.2 * ((ts > 4.2) & (ts < 6.4)))
        acc = true + noise
        fused = np.zeros_like(ts)
        a = 0.985
        for i in range(1, len(ts)):
            fused[i] = a * (fused[i - 1] + gyro_meas[i] * dt) + (1 - a) * acc[i]
        x0, x1 = -1.9, 5.8
        lanes = [(2.3, RED, "자이로", "빠르지만\n시간이 지나면 흘러감", gyro),
                 (-0.2, AMBER, "가속도계", "중력 기준이 있으나\n진동에 흔들림", acc),
                 (-2.75, GREEN, "상보필터", "짧은 움직임은 자이로\n긴 기준은 가속도계", fused)]
        ys = 0.095
        g = VGroup()
        for yc, col, name, sub, _ in lanes:
            base = DashedLine([x0, yc, 0], [x1, yc, 0], color=MUTED, stroke_width=2, dash_length=0.12)
            ref = lane_poly(ts, true, x0, x1, tmax, yc, ys, MUTED, 3).set_stroke(opacity=0.55)
            nm = T(name, 34, col, True).move_to([-6.0, yc + 0.45, 0], aligned_edge=LEFT)
            sb = T(sub, 20, MUTED, line_spacing=0.8).next_to(nm, DOWN, buff=0.12, aligned_edge=LEFT)
            g.add(base, ref, nm, sb)
        legend = VGroup(Line(ORIGIN, RIGHT * 0.6, color=MUTED, stroke_width=4), T("실제 기울기", 22, MUTED)).arrange(RIGHT, buff=0.2)
        legend.to_corner(UR, buff=0.3)
        self.add(g, legend)
        curves = [lane_poly(ts, y, x0, x1, tmax, yc, ys, col) for (yc, col, _, _, y) in lanes]
        cursor = Line([x0, -3.7, 0], [x0, 3.9, 0], color=BLUE, stroke_width=3)
        t_tr = ValueTracker(0)
        cursor.add_updater(lambda m: m.move_to([x0 + (x1 - x0) * t_tr.get_value() / tmax, 0.1, 0]))
        self.add(cursor)
        for c in curves:
            c.set_stroke(opacity=1)
        self.play(AnimationGroup(*[Create(c, rate_func=linear) for c in curves], t_tr.animate(rate_func=linear).set_value(tmax), lag_ratio=0),
                  run_time=8.5)
        cursor.clear_updaters()
        self.play(FadeOut(cursor), run_time=0.4)
        self.wait(2.0)


class Slide06L(Scene):
    """스틱 중립에서 기체가 흘러감 → 조종자가 반대로 조향. ASPECT=1.667"""

    def construct(self):
        quad, motors, props, labels = quad_top(0.55, with_labels=False)
        quad.move_to(LEFT * 4.2 + UP * 0.5)
        for p in props.values():
            p.add_updater(lambda m, dt: m.rotate(14 * dt))
        # 조종 스틱(우측)
        gate = Circle(radius=0.95, color=MUTED, stroke_width=4, fill_color=PAPER, fill_opacity=1).move_to(RIGHT * 4.4 + DOWN * 0.8)
        stick = Dot(radius=0.24, color=BLUE).move_to(gate.get_center())
        sl = T("조종 스틱", 24, MUTED).next_to(gate, DOWN, buff=0.25)
        title = T("센서가 없어 기체 스스로 위치를 보정하지 못함", 28, INK, True).to_edge(UP, buff=0.35)
        ground = Line(LEFT * 6.6, RIGHT * 6.6, color=MUTED, stroke_width=2).move_to(DOWN * 2.1)
        d_on = ValueTracker(0)
        drift = Arrow(ORIGIN, RIGHT, color=RED, buff=0, stroke_width=9)
        dl = T("수평 드리프트", 26, RED, True)
        def drift_upd(m):
            c = quad.get_center()
            m.become(Arrow(c + RIGHT * 1.9, c + RIGHT * 3.4, color=RED, buff=0, stroke_width=9).set_opacity(d_on.get_value()))
        def dl_upd(m):
            m.move_to(quad.get_center() + DOWN * 2.0).set_opacity(d_on.get_value())
        drift.add_updater(drift_upd)
        dl.add_updater(dl_upd)
        pl = T("조종자 역방향 조향", 26, BLUE, True).next_to(gate, UP, buff=0.4).set_opacity(0)
        self.add(drift, dl)
        self.add(title, quad, gate, stick, sl)
        self.wait(0.6)
        # 1) 스틱 중립, 기체 흘러감
        self.play(quad.animate.shift(RIGHT * 2.6), d_on.animate.set_value(1), run_time=3.0, rate_func=linear)
        self.wait(0.3)
        # 2) 조종자 반대 입력
        self.play(stick.animate.shift(LEFT * 0.62), pl.animate.set_opacity(1), run_time=0.7)
        self.play(quad.animate.shift(LEFT * 2.6), d_on.animate.set_value(0), run_time=2.6)
        self.play(stick.animate.move_to(gate.get_center()), pl.animate.set_opacity(0), run_time=0.7)
        self.wait(0.3)
        # 3) 다시 흘러감
        self.play(quad.animate.shift(RIGHT * 2.2), d_on.animate.set_value(1), run_time=2.4, rate_func=linear)
        self.wait(1.2)


class Slide06R(Scene):
    """출력 여유가 줄면 roll·pitch가 먼저, 남은 범위에 yaw. ASPECT=1.667"""

    def construct(self):
        title = T("모터 출력 허용 범위 안에서의 배분", 30, INK, True).to_edge(UP, buff=0.4)
        rng_w = ValueTracker(11.0)
        rp = 4.2          # roll·pitch 요구량(고정)
        yaw_want = 3.6    # yaw 요구량
        x_left = -5.6
        box = Rectangle(height=1.5, stroke_color=INK, stroke_width=5, fill_color=PAPER, fill_opacity=1)
        box.add_updater(lambda m: m.stretch_to_fit_width(rng_w.get_value()).move_to([x_left + rng_w.get_value() / 2, 0.6, 0]))
        rp_bar = Rectangle(height=1.5, width=rp, stroke_width=0, fill_color=BLUE, fill_opacity=1)
        rp_bar.move_to([x_left + rp / 2, 0.6, 0])
        def yaw_updater(m):
            room = max(min(rng_w.get_value() - rp, yaw_want), 0.001)
            m.become(Rectangle(height=1.5, width=room, stroke_width=0, fill_color=AMBER, fill_opacity=1).move_to([x_left + rp + room / 2, 0.6, 0]))
        yaw_bar = Rectangle(height=1.5, width=yaw_want, stroke_width=0, fill_color=AMBER, fill_opacity=1)
        yaw_bar.add_updater(yaw_updater)
        want = DashedVMobject(Rectangle(height=1.5, width=yaw_want, stroke_color=AMBER, stroke_width=4, fill_opacity=0)
                              .move_to([x_left + rp + yaw_want / 2, 0.6, 0]), num_dashes=40)
        want_lab = T("yaw 요구량", 22, AMBER).move_to([x_left + rp + yaw_want / 2, -0.55, 0])
        rp_lab = T("roll · pitch", 30, PAPER, True).move_to(rp_bar)
        yaw_lab = T("yaw", 30, PAPER, True)
        yaw_lab.add_updater(lambda m: m.move_to(yaw_bar).set_opacity(1 if yaw_bar.width > 0.9 else 0))
        cap1 = T("roll · pitch는 먼저 전부 배분", 28, BLUE, True).move_to([x_left + rp / 2, -1.55, 0])
        cap2 = T("남은 범위만큼만 yaw 배분", 28, AMBER, True).move_to([0.2, -2.35, 0])
        rng_lab = T("출력 허용 범위", 24, MUTED)
        rng_lab.add_updater(lambda m: m.next_to(box, UP, buff=0.2, aligned_edge=RIGHT))
        thr = T("스로틀이 낮아져 출력 여유가 줄어듦", 26, MUTED).move_to([-0.5, 2.75, 0])
        arrow = Arrow([3.0, 2.75, 0], [5.4, 2.75, 0], color=MUTED, buff=0, stroke_width=6)
        self.add(title, box, rp_bar, yaw_bar, want, rp_lab, yaw_lab, want_lab, rng_lab)
        self.play(FadeIn(cap1), run_time=0.6)
        self.wait(0.8)
        self.play(FadeIn(thr), FadeIn(arrow), FadeIn(cap2), run_time=0.6)
        self.play(rng_w.animate.set_value(6.4), run_time=4.0, rate_func=smooth)
        self.wait(1.0)
        self.play(rng_w.animate.set_value(4.2 + 0.001), run_time=2.0, rate_func=smooth)
        self.wait(1.5)
        # 출력이 roll·pitch만으로 한계에 도달해도 roll·pitch는 유지
        note = T("수평 자세(roll · pitch)가 최우선", 28, BLUE, True).move_to([0, -3.3, 0])
        self.play(FadeIn(note), run_time=0.6)
        self.wait(1.6)
