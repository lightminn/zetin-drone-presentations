from style import *
import numpy as np
import json
from pathlib import Path

STATS = Path(__file__).parent / "poshold_stats.json"


class Slide07(Scene):
    """3901-L0X: 광류(수평 이동), 거리(높이), 회전 성분. ASPECT=1.55"""

    def construct(self):
        gy = -3.0
        ground = Line(LEFT * 6.2 + UP * gy, RIGHT * 6.2 + UP * gy, color=INK, stroke_width=4)
        dots = VGroup(*[Dot(radius=0.07, color=MUTED).move_to([x, gy + 0.001, 0]) for x in np.arange(-6.0, 6.1, 0.55)])
        hx = ValueTracker(-1.5)     # 기체 x
        hh = ValueTracker(2.6)      # 지면 위 높이
        tilt = ValueTracker(0.0)    # 기체 기울기(rad)
        fov = 0.37                  # 시야 반각(42도 근사)
        def make_drone():
            body = RoundedRectangle(width=2.0, height=0.42, corner_radius=0.16, fill_color=INK, fill_opacity=1, stroke_width=0)
            mod = RoundedRectangle(width=0.5, height=0.22, corner_radius=0.05, fill_color=BLUE, fill_opacity=1, stroke_width=0).shift(DOWN * 0.32)
            g = VGroup(body, mod).rotate(tilt.get_value(), about_point=ORIGIN)
            return g.move_to([hx.get_value(), gy + hh.get_value(), 0])
        drone = always_redraw(make_drone)
        cone = Polygon(ORIGIN, ORIGIN, ORIGIN, fill_color=TEAL, fill_opacity=0.16, stroke_color=TEAL, stroke_width=3)
        beam = DashedLine(ORIGIN, DOWN, color=AMBER, stroke_width=5, dash_length=0.18)
        def cone_upd(m):
            cx, cy, a, h = hx.get_value(), gy + hh.get_value() - 0.35, tilt.get_value(), hh.get_value() - 0.35
            apex = np.array([cx, cy, 0])
            # 광축은 기체 기울기만큼 회전, 지면과의 교점 계산
            def hit(angle):
                d = np.array([np.sin(angle), -np.cos(angle), 0])
                return apex + d * (h / np.cos(angle))
            m.set_points_as_corners([apex, hit(a - fov), hit(a + fov), apex])
        def beam_upd(m):
            cx, cy, a, h = hx.get_value(), gy + hh.get_value() - 0.35, tilt.get_value(), hh.get_value() - 0.35
            apex = np.array([cx, cy, 0])
            end = apex + np.array([np.sin(a), -np.cos(a), 0]) * (h / np.cos(a))
            m.become(DashedLine(apex, end, color=AMBER, stroke_width=5, dash_length=0.18))
        cone.add_updater(cone_upd)
        beam.add_updater(beam_upd)
        # 광류 화살표: 지면 텍스처가 기체 아래에서 움직이는 방향/크기
        flow = Arrow(ORIGIN, LEFT, color=RED, buff=0, stroke_width=10)
        flow_len = ValueTracker(0.0)
        def flow_upd(m):
            L = flow_len.get_value()
            c = np.array([hx.get_value(), gy + 0.45, 0])
            if abs(L) < 0.05:
                m.become(Arrow(c, c + LEFT * 0.01, color=RED, buff=0).set_opacity(0))
            else:
                m.become(Arrow(c + RIGHT * L / 2, c - RIGHT * L / 2, color=RED, buff=0, stroke_width=10, max_tip_length_to_length_ratio=0.3))
        flow.add_updater(flow_upd)
        h_lab = T("높이 h", 26, AMBER, True)
        h_lab.add_updater(lambda m: m.move_to([hx.get_value() + 0.75, gy + hh.get_value() / 2 - 0.1, 0]))
        step = T("", 30, INK, True)
        cap = VGroup()
        self.add(ground, dots, cone, beam, drone, flow, h_lab)
        lbl_f = T("광류 PMW3901", 24, TEAL, True).move_to([-4.6, 3.4, 0])
        lbl_r = T("거리 VL53L0X", 24, AMBER, True).move_to([-4.6, 2.9, 0])
        self.add(lbl_f, lbl_r)

        def caption(txt, color=INK):
            c = T(txt, 29, color, True).move_to([0, -3.75, 0])
            return c
        # 1) 수평 이동 → 광류
        c1 = caption("1  기체가 이동하면 바닥 무늬가 반대로 움직여 보임", RED)
        self.play(FadeIn(c1), run_time=0.5)
        self.play(hx.animate.set_value(2.0), flow_len.animate.set_value(1.5), run_time=3.2, rate_func=linear)
        self.wait(0.3)
        # 2) 높이가 높으면 같은 속도도 작게 보임 → 높이 곱함
        self.play(FadeOut(c1), run_time=0.3)
        c2 = caption("2  같은 속도라도 높을수록 광류가 작음 → 거리 센서 높이를 곱함", AMBER)
        self.play(FadeIn(c2), run_time=0.5)
        self.play(hh.animate.set_value(4.3), flow_len.animate.set_value(0.75), run_time=2.0)
        self.play(hx.animate.set_value(-1.0), run_time=2.4, rate_func=linear)
        self.wait(0.3)
        # 3) 제자리 기울임 → 가짜 광류, 자이로 회전분 차감
        self.play(FadeOut(c2), hh.animate.set_value(2.6), flow_len.animate.set_value(0), run_time=1.0)
        c3 = caption("3  제자리에서 기울기만 바뀌어도 광류 발생 → 자이로 회전분 차감", TEAL)
        self.play(FadeIn(c3), run_time=0.5)
        self.play(tilt.animate.set_value(0.30), flow_len.animate.set_value(1.1), run_time=1.6)
        self.play(tilt.animate.set_value(-0.25), flow_len.animate.set_value(-0.95), run_time=1.6)
        self.play(tilt.animate.set_value(0.0), flow_len.animate.set_value(0), run_time=1.0)
        self.wait(1.6)


class Slide08(Scene):
    """패킷 수신 주기와 거리 유효성 규칙. ASPECT=1.55"""

    def construct(self):
        x0, x1 = -5.6, 2.6
        parser = labeled(3.0, 2.8, "MSPv2", "패킷 수신", stroke=BLUE, tsize=32, ssize=22).move_to([4.6, 1.9, 0])
        lane1 = Line([x0, 3.0, 0], [x1, 3.0, 0], color=TEAL, stroke_width=2)
        lane2 = Line([x0, 0.9, 0], [x1, 0.9, 0], color=AMBER, stroke_width=2)
        t1 = T("광류 약 10 Hz", 28, TEAL, True).move_to([-4.2, 3.55, 0])
        t2 = T("거리 약 28 Hz", 28, AMBER, True).move_to([-4.2, 1.45, 0])
        self.add(lane1, lane2, t1, t2, parser)
        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)
        # 패킷: 이동하는 틱. 속도 3.0 unit/s
        v = 2.9
        def stream(y, period, color, h):
            g = VGroup()
            def upd(m):
                t = clock.get_value()
                m.become(VGroup(*[
                    Line([x0 + ((t - k * period) * v) % (x1 - x0 + 0.01), y - h / 2, 0], [x0 + ((t - k * period) * v) % (x1 - x0 + 0.01), y + h / 2, 0],
                         color=color, stroke_width=6) for k in range(0, int((x1 - x0) / (period * v)) + 2)]))
            g.add_updater(upd)
            return g
        s1 = stream(3.0, 1.0, TEAL, 0.55)    # 100 ms → 1.0 s 로 시간 확대
        s2 = stream(0.9, 0.35, AMBER, 0.45)  # 35 ms → 0.35 s
        self.add(s1, s2)
        self.wait(3.0)
        # 판정 규칙
        okc = labeled(4.6, 1.9, "거리 1.2 m · 품질 255", "0 이상이면 유효 → 고도값으로 사용", stroke=GREEN, tsize=26, ssize=20).move_to([-3.2, -1.5, 0])
        bad = labeled(4.6, 1.9, "거리 −1 · 품질 255", "음수는 범위 밖 → 품질값은 보지 않음", stroke=RED, tsize=26, ssize=20).move_to([3.0, -1.5, 0])
        ok_mark = T("유효", 30, GREEN, True).next_to(okc, DOWN, buff=0.25)
        bad_mark = T("무효", 30, RED, True).next_to(bad, DOWN, buff=0.25)
        rule = T("거리 유효성은 품질값이 아니라 거리값의 부호로 판정", 28, INK, True).move_to([0, -3.7, 0])
        self.play(FadeIn(okc), FadeIn(bad), run_time=0.7)
        self.play(FadeIn(ok_mark), FadeIn(bad_mark), run_time=0.5)
        self.play(FadeIn(rule), run_time=0.6)
        self.wait(3.6)


class Slide09(Scene):
    """위치 유지 4단계 파이프라인. 와이드 ASPECT=5.0"""

    def construct(self):
        names = [("1  보정", "손으로 흔들어\n광류·자이로 정렬", BLUE),
                 ("2  속도 환산", "광류 − 자이로 회전분\n× 지면 높이", TEAL),
                 ("3  가속도 보정", "가속도계 입력에서\n광류 가속도분 차감", AMBER),
                 ("4  목표 각도", "속도를 줄이는 방향\n위치 오차 최대 1.0 m", RED)]
        xs = [-12.6, -4.2, 4.2, 12.6]
        boxes = VGroup()
        for (n, sub, col), x in zip(names, xs):
            b = card(7.0, 4.5, stroke=col, sw=6)
            t = T(n, 40, col, True).move_to(b.get_center() + UP * 1.35)
            s = T(sub, 29, INK, line_spacing=0.9).move_to(b.get_center() + DOWN * 0.55)
            boxes.add(VGroup(b, t, s).move_to([x, 0.2, 0]))
        arrows = VGroup(*[Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.12, color=MUTED, stroke_width=7,
                                max_tip_length_to_length_ratio=0.3) for i in range(3)])
        head = T("광류 기반 수평 위치 유지", 34, MUTED, True).move_to([-16.5, 3.5, 0])
        self.add(head)
        self.play(AnimationGroup(*[FadeIn(b, shift=UP * 0.3) for b in boxes], lag_ratio=0.25), run_time=2.0)
        self.play(FadeIn(arrows), run_time=0.5)
        # 데이터 패킷이 파이프라인을 따라 이동
        pkt = Dot(radius=0.28, color=RED).move_to(boxes[0].get_left() + LEFT * 0.9)
        self.play(FadeIn(pkt), run_time=0.3)
        for i, bx in enumerate(boxes):
            self.play(pkt.animate.move_to(bx[0].get_center() + DOWN * 1.75), bx[0].animate.set_stroke(width=14), run_time=0.9)
            self.play(bx[0].animate.set_stroke(width=6), run_time=0.3)
        self.play(pkt.animate.move_to(boxes[-1].get_right() + RIGHT * 0.9), run_time=0.7)
        # 한 번 더 순환
        pkt2 = Dot(radius=0.28, color=RED).move_to(boxes[0].get_left() + LEFT * 0.9)
        self.play(FadeOut(pkt), FadeIn(pkt2), run_time=0.3)
        self.play(pkt2.animate.move_to(boxes[-1].get_right() + RIGHT * 0.9), run_time=3.0, rate_func=linear)
        self.wait(1.5)


class Slide10(Scene):
    """오늘 테더 비행별 위치 유지 지표. ASPECT=1.55"""

    def construct(self):
        d = json.loads(STATS.read_text())
        n = len(d)
        x0, x1 = -4.6, 5.9
        slot = (x1 - x0) / n
        cx = lambda i: x0 + slot * (i + 0.5)
        # (a) 최장 연속 활성 시간: 기준선 y=0.75, 최대 높이 2.1
        ya_base, ya_h, amax = 0.75, 2.1, 25.0
        ta = T("위치 유지 최장 연속 구간 (s)", 28, INK, True).move_to([-2.6, 3.7, 0])
        base_a = Line([x0, ya_base, 0], [x1, ya_base, 0], color=MUTED, stroke_width=3)
        # (b) 수평 속도 RMS
        yb_base, yb_h, bmax = -2.55, 2.0, 0.25
        tb = T("수평 속도 RMS (m/s)", 28, INK, True).move_to([-3.0, -0.25, 0])
        base_b = Line([x0, yb_base, 0], [x1, yb_base, 0], color=MUTED, stroke_width=3)
        leg = VGroup(Square(0.28, fill_color=BLUE, fill_opacity=1, stroke_width=0), T("위치 유지 구간", 22, INK),
                     Square(0.28, fill_color=AMBER, fill_opacity=1, stroke_width=0), T("그 밖", 22, INK)).arrange(RIGHT, buff=0.18)
        leg.move_to([3.6, -0.25, 0])
        self.add(ta, tb, base_a, base_b, leg)
        ta_times = VGroup(*[T(o["time"], 20, MUTED).move_to([cx(i), ya_base - 0.28, 0]) for i, o in enumerate(d)])
        tb_times = VGroup(*[T(o["time"], 20, MUTED).move_to([cx(i), yb_base - 0.28, 0]) for i, o in enumerate(d)])
        self.add(ta_times, tb_times)
        anims = []
        for i, o in enumerate(d):
            v = o["longest_active_s"]
            if v <= 0:
                anims.append(FadeIn(T("끔", 24, MUTED, True).move_to([cx(i), ya_base + 0.3, 0])))
            else:
                h = ya_h * v / amax
                r = Rectangle(width=0.62, height=h, stroke_width=0, fill_color=BLUE, fill_opacity=1).move_to([cx(i), ya_base + h / 2, 0])
                lab = T(f"{v:.1f}", 24, BLUE, True).next_to(r, UP, buff=0.08)
                anims.append(AnimationGroup(GrowFromEdge(r, DOWN), FadeIn(lab, shift=UP * 0.1)))
        self.play(AnimationGroup(*anims, lag_ratio=0.35), run_time=3.6)
        self.wait(0.4)
        bars_b = []
        for i, o in enumerate(d):
            for key, col, dx in (("rms_active", BLUE, -0.34), ("rms_other", AMBER, 0.34)):
                v = o[key]
                if v is None:
                    continue
                h = yb_h * v / bmax
                r = Rectangle(width=0.6, height=h, stroke_width=0, fill_color=col, fill_opacity=1).move_to([cx(i) + dx, yb_base + h / 2, 0])
                lab = T(f"{v:.2f}", 20, INK).next_to(r, UP, buff=0.06)
                bars_b.append(AnimationGroup(GrowFromEdge(r, DOWN), FadeIn(lab)))
        self.play(AnimationGroup(*bars_b, lag_ratio=0.12), run_time=3.8)
        res = T("위치 유지 구간의 수평 속도가 5회 모두 더 낮음 (평균 약 32 %)", 26, BLUE, True).move_to([0, -3.65, 0])
        self.play(FadeIn(res), run_time=0.6)
        self.wait(2.4)


class Slide11(Scene):
    """카메라 구성: BEC 전원, 비행제어기 와이파이 공유. ASPECT=1.55"""

    def construct(self):
        pcb = labeled(4.4, 2.3, "비행제어 PCB", "ESP32-S3 · 와이파이를 엶", stroke=BLUE, tsize=32, ssize=22).move_to([-3.8, 2.2, 0])
        cam = labeled(4.4, 2.3, "카메라 보드", "ESP32-CAM 호환보드", stroke=TEAL, tsize=32, ssize=22).move_to([3.8, 2.2, 0])
        pos_q = T("장착 위치 ?  미정", 22, MUTED).move_to(cam.get_bottom() + UP * 0.35)
        bec = labeled(4.2, 1.7, "ESC의 BEC", "5 V 전원", stroke=RED, tsize=30, ssize=22).move_to([0, -2.7, 0])
        self.add(pcb, cam, pos_q, bec)
        p1 = Line(bec.get_top() + LEFT * 1.2, pcb.get_bottom() + RIGHT * 0.2, color=RED, stroke_width=5)
        p2 = Line(bec.get_top() + RIGHT * 1.2, cam.get_bottom() + LEFT * 0.2, color=RED, stroke_width=5)
        self.play(Create(p1), Create(p2), run_time=1.0)
        pw = T("전원만 공급", 24, RED, True).move_to([4.7, -0.55, 0])
        self.play(FadeIn(pw), run_time=0.4)
        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)
        for ln in (p1, p2):
            for k in range(3):
                dd = Dot(radius=0.12, color=RED)
                dd.add_updater(lambda m, ln=ln, k=k: m.move_to(ln.point_from_proportion(((clock.get_value() * 0.5) + k / 3) % 1)))
                self.add(dd)
        self.wait(1.5)
        wf = VGroup(*[Arc(radius=r, start_angle=PI / 2 - 0.9, angle=1.8, stroke_color=BLUE, stroke_width=6) for r in (0.4, 0.75, 1.1)])
        wf.move_to([0, 2.55, 0])
        link = DashedLine(pcb.get_right(), cam.get_left(), color=BLUE, stroke_width=5, dash_length=0.2)
        wlab = T("같은 와이파이로\n영상 전송", 26, BLUE, True, line_spacing=0.9).move_to([0, 0.35, 0])
        self.play(Create(link), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(a) for a in wf], lag_ratio=0.3), FadeIn(wlab), run_time=1.2)
        for _ in range(3):
            self.play(LaggedStart(*[a.animate.set_stroke(opacity=0.25) for a in wf], lag_ratio=0.25), run_time=0.7)
            self.play(LaggedStart(*[a.animate.set_stroke(opacity=1.0) for a in wf], lag_ratio=0.25), run_time=0.7)
        self.wait(1.6)
