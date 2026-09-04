#!/usr/bin/env python3
"""Contract tests for the 2026-2 recruit presentation deck."""

from __future__ import annotations

import filecmp
import json
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

try:
    import websocket
except ImportError:  # pragma: no cover - environment-dependent skip
    websocket = None


REPO_ROOT = Path(__file__).resolve().parents[1]
DECK_DIR = REPO_ROOT / "docs" / "presentations" / "2026-2-recruit"
HTML_PATH = DECK_DIR / "index.html"
PRESENT_PATH = DECK_DIR / "present.sh"
TEN_MIN_DIR = REPO_ROOT / "docs" / "presentations" / "ai-startup-camp-drone-10min"
CHROME_BIN = (
    shutil.which("google-chrome-stable")
    or shutil.which("google-chrome")
    or shutil.which("chromium")
)


def _unused_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class _DeckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: list[dict[str, str | None]] = []
        self.images: list[dict[str, str | None]] = []
        self.videos: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "section":
            self.sections.append(attributes)
        elif tag == "img":
            self.images.append(attributes)
        elif tag == "video":
            self.videos.append(attributes)


class PresentationRecruitHtmlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = HTML_PATH.read_text(encoding="utf-8")
        self.parser = _DeckParser()
        self.parser.feed(self.source)

    def slide_source(self, screen_label: str) -> str:
        match = re.search(
            rf'<section\b(?=[^>]*data-screen-label="{re.escape(screen_label)}")[^>]*>'
            r".*?</section>",
            self.source,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, f"missing slide {screen_label}")
        return match.group(0)

    def test_deck_has_two_slides_with_notes(self) -> None:
        self.assertEqual(len(self.parser.sections), 2)
        self.assertEqual(
            [item.get("data-screen-label") for item in self.parser.sections],
            ["01", "02"],
        )
        self.assertTrue(all(item.get("data-label") for item in self.parser.sections))
        self.assertTrue(
            all(item.get("data-speaker-notes", "").strip() for item in self.parser.sections)
        )

    def test_deck_mentions_required_text_and_uses_required_assets(self) -> None:
        normalized = re.sub(r"\s+", " ", self.source)
        for phrase in (
            "상용 비행제어기 없이, 첫 비행까지",
            "앞으로의 목표, 함께할 사람",
            "실제 기체 · 테더로 이동 범위를 제한한 비행 시험",
            "직접 설계한 프레임 · 실제 기체",
            "자체 비행제어 PCB · ESP32-S3",
            "비행제어 SW 직접 구현",
            "기체·보드 직접 설계",
            "실제 비행으로 검증",
            "경험 없어도 됩니다",
            "이런 사람을 찾습니다",
            "드론 팀 모집 폼",
            "github.com/lightminn/zetin-drone",
        ):
            self.assertIn(phrase, normalized)
        for image in (
            "assets/assembled-bench.jpeg",
            "assets/pcb-built.jpeg",
            "assets/form-qr.png",
            "assets/github-qr.png",
        ):
            self.assertIn(f'src="{image}"', self.source)
        self.assertEqual(len(self.parser.videos), 1)
        video = self.parser.videos[0]
        self.assertEqual(video.get("src"), "assets/hover_demo.mp4")
        for attribute in ("controls", "loop", "muted", "playsinline", "preload"):
            self.assertIn(attribute, video)
        self.assertEqual(video.get("preload"), "metadata")
        self.assertTrue((DECK_DIR / "assets" / "hover_demo.mp4").is_file())
        self.assertNotIn('src="assets/cad-top.png"', self.source)

    def test_source_video_is_chrome_compatible_h264_30fps(self) -> None:
        ffprobe = shutil.which("ffprobe")
        if ffprobe is None:
            self.skipTest("ffprobe is not available")
        result = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_name,width,height,r_frame_rate",
                "-of",
                "json",
                str(DECK_DIR / "assets" / "hover_demo.mp4"),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        stream = payload["streams"][0]
        self.assertEqual(stream["codec_name"], "h264")
        self.assertEqual(stream["width"], 1280)
        self.assertEqual(stream["height"], 720)
        self.assertEqual(stream["r_frame_rate"], "30/1")

    def test_runtime_files_match_ten_minute_deck_byte_for_byte(self) -> None:
        for filename in ("support.js", "deck-stage.js"):
            self.assertTrue(
                filecmp.cmp(DECK_DIR / filename, TEN_MIN_DIR / filename, shallow=False),
                msg=filename,
            )
        for path in (DECK_DIR / "vendor").rglob("*"):
            if path.is_file():
                counterpart = TEN_MIN_DIR / path.relative_to(DECK_DIR)
                self.assertTrue(filecmp.cmp(path, counterpart, shallow=False), msg=str(path))

    def test_present_script_only_changes_mktemp_prefix(self) -> None:
        script = PRESENT_PATH.read_text(encoding="utf-8")
        original = (TEN_MIN_DIR / "present.sh").read_text(encoding="utf-8")
        self.assertTrue(PRESENT_PATH.stat().st_mode & 0o111)
        self.assertEqual(
            script.replace("drone-recruit-presentation", "drone-summary-presentation"),
            original,
        )

    def test_form_link_is_a_real_google_form(self) -> None:
        match = re.search(r'data-form-link href="([^"]+)"', self.source)
        self.assertIsNotNone(match, "missing data-form-link anchor")
        url = match.group(1)
        self.assertRegex(url, r"^https://(forms\.gle/|docs\.google\.com/forms/)")
        self.assertNotIn("PLACEHOLDER", self.source)
        github = re.search(r'data-github-link href="([^"]+)"', self.source)
        self.assertIsNotNone(github, "missing data-github-link anchor")
        self.assertEqual(github.group(1), "https://github.com/lightminn/zetin-drone")

    def test_no_commit_hash_or_day_specific_date_leaks(self) -> None:
        self.assertIsNone(re.search(r"\b[0-9a-f]{40}\b", self.source))
        self.assertIsNone(re.search(r"\b2026-0?\d-\d\d\b", self.source))


@unittest.skipUnless(CHROME_BIN and websocket, "Chrome and websocket-client are required")
class PresentationRecruitBrowserWrapTests(unittest.TestCase):
    server: subprocess.Popen[bytes]
    chrome: subprocess.Popen[bytes]
    ws: websocket.WebSocket
    command_id: int

    @classmethod
    def setUpClass(cls) -> None:
        cls.http_port = _unused_port()
        cls.debug_port = _unused_port()
        cls.runtime = tempfile.TemporaryDirectory(prefix="zetin-recruit-wrap-")
        cls.server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "http.server",
                str(cls.http_port),
                "--bind",
                "127.0.0.1",
                "--directory",
                str(DECK_DIR),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        cls.chrome = subprocess.Popen(
            [
                CHROME_BIN,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1280,720",
                f"--remote-debugging-port={cls.debug_port}",
                "--remote-allow-origins=*",
                f"--user-data-dir={Path(cls.runtime.name) / 'profile'}",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        deadline = time.monotonic() + 5.0
        target = None
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{cls.debug_port}/json", timeout=0.2
                ) as response:
                    targets = json.load(response)
                target = next(item for item in targets if item.get("type") == "page")
                break
            except (OSError, StopIteration, ValueError):
                time.sleep(0.05)
        if target is None:
            cls._stop_processes()
            cls.runtime.cleanup()
            raise RuntimeError("Chrome DevTools target did not become ready")

        cls.ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=5)
        cls.command_id = 0
        cls._call("Page.enable")
        cls._call("Runtime.enable")
        cls._call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1280, "height": 720, "deviceScaleFactor": 1, "mobile": False},
        )
        cls._call("Page.navigate", {"url": f"http://127.0.0.1:{cls.http_port}/#1"})

        deadline = time.monotonic() + 10.0
        while time.monotonic() < deadline:
            if cls._evaluate(
                "document.readyState === 'complete' && "
                "document.querySelector('deck-stage')?._slides?.length === 2 && "
                "document.fonts.status === 'loaded'"
            ):
                cls._evaluate(
                    "(() => { const stage = document.querySelector('deck-stage'); "
                    "stage.setAttribute('no-rail', ''); stage._fit(); return true; })()"
                )
                return
            time.sleep(0.05)
        raise RuntimeError("2-slide presentation did not become ready")

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "ws"):
            cls.ws.close()
        cls._stop_processes()
        if hasattr(cls, "runtime"):
            cls.runtime.cleanup()

    @classmethod
    def _stop_processes(cls) -> None:
        for name in ("chrome", "server"):
            process = getattr(cls, name, None)
            if process is None or process.poll() is not None:
                continue
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)

    @classmethod
    def _call(cls, method: str, params: dict | None = None) -> dict:
        cls.command_id += 1
        cls.ws.send(
            json.dumps({"id": cls.command_id, "method": method, "params": params or {}})
        )
        while True:
            message = json.loads(cls.ws.recv())
            if message.get("id") != cls.command_id:
                continue
            if "error" in message:
                raise RuntimeError(message["error"])
            return message.get("result", {})

    @classmethod
    def _evaluate(cls, expression: str):
        response = cls._call(
            "Runtime.evaluate", {"expression": expression, "returnByValue": True}
        )
        if "exceptionDetails" in response:
            raise RuntimeError(response["exceptionDetails"])
        return response["result"].get("value")

    def test_whitespace_delimited_tokens_do_not_split_across_visual_lines(self) -> None:
        splits = self._evaluate(
            """
            (() => {
              const stage = document.querySelector('deck-stage');
              const findings = [];
              const lineFor = (range) => [...range.getClientRects()]
                .filter((rect) => rect.width > 0 && rect.height > 0)
                .map((rect) => Math.round(rect.top * 10) / 10);
              for (const [index, slide] of stage._slides.entries()) {
                stage.goTo(index);
                stage._fit();
                const walker = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
                for (let node = walker.nextNode(); node; node = walker.nextNode()) {
                  const parent = node.parentElement;
                  if (!parent || !/[가-힣]/.test(node.data)) continue;
                  const style = getComputedStyle(parent);
                  if (style.display === 'none' || style.visibility === 'hidden') continue;
                  for (const match of node.data.matchAll(/\\S+/g)) {
                    const token = match[0];
                    if (!/[가-힣]/.test(token)) continue;
                    const range = document.createRange();
                    range.setStart(node, match.index);
                    range.setEnd(node, match.index + token.length);
                    const visualLines = [...new Set(lineFor(range))];
                    if (visualLines.length > 1) {
                      findings.push({
                        slide: index + 1,
                        token,
                        lines: visualLines,
                        context: parent.textContent.trim().replace(/\\s+/g, ' ').slice(0, 120),
                      });
                    }
                  }
                }
              }
              return findings;
            })()
            """
        )
        self.assertEqual(splits, [], f"mid-token visual line breaks: {splits}")

    def test_recruit_slides_fit_the_1280_by_720_content_frame(self) -> None:
        result = self._evaluate(
            """
            (() => {
              const stage = document.querySelector('deck-stage');
              const findings = {};
              const slideNumbers = [1, 2];
              const textNodes = (root) => {
                const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
                const nodes = [];
                for (let node = walker.nextNode(); node; node = walker.nextNode()) {
                  if (node.data.trim()) nodes.push(node);
                }
                return nodes;
              };
              const visualLines = (element) => {
                const range = document.createRange();
                range.selectNodeContents(element);
                return [...new Set([...range.getClientRects()]
                  .filter((rect) => rect.width > 0 && rect.height > 0)
                  .map((rect) => Math.round(rect.top * 10) / 10))].length;
              };
              for (const number of slideNumbers) {
                stage.goTo(number - 1);
                stage._fit();
                const slide = stage._slides[number - 1];
                const slideRect = slide.getBoundingClientRect();
                const elements = [...slide.querySelectorAll('[data-result-element]')];
                const textElements = [...slide.querySelectorAll('*')].filter((element) => {
                  const hasOwnText = [...element.childNodes].some((node) =>
                    node.nodeType === Node.TEXT_NODE && node.textContent.trim()
                  );
                  return hasOwnText;
                });
                const overflow = [];
                for (const element of textElements) {
                  let current = element;
                  let inside = true;
                  while (current && current !== slide) {
                    const rect = current.getBoundingClientRect();
                    if (
                      rect.left < slideRect.left - 1 ||
                      rect.top < slideRect.top - 1 ||
                      rect.right > slideRect.right + 1 ||
                      rect.bottom > slideRect.bottom + 1
                    ) {
                      inside = false;
                      break;
                    }
                    current = current.parentElement;
                  }
                  if (!inside) overflow.push(element.textContent.trim().slice(0, 80));
                }
                const smallText = textElements.flatMap((element) => {
                  const style = getComputedStyle(element);
                  const size = Number.parseFloat(style.fontSize);
                  return size < 18.7 ? [element.textContent.trim().slice(0, 80)] : [];
                });
                const overlaps = [];
                for (let i = 0; i < elements.length; i++) {
                  for (let j = i + 1; j < elements.length; j++) {
                    const a = elements[i].getBoundingClientRect();
                    const b = elements[j].getBoundingClientRect();
                    const separated =
                      a.right <= b.left + 1 ||
                      b.right <= a.left + 1 ||
                      a.bottom <= b.top + 1 ||
                      b.bottom <= a.top + 1;
                    if (!separated) overlaps.push([i, j]);
                  }
                }
                const tokenSplits = [];
                for (const node of textNodes(slide)) {
                  const parent = node.parentElement;
                  if (!parent || !/[가-힣]/.test(node.data)) continue;
                  for (const match of node.data.matchAll(/\\S+/g)) {
                    const token = match[0];
                    if (!/[가-힣]/.test(token)) continue;
                    const range = document.createRange();
                    range.setStart(node, match.index);
                    range.setEnd(node, match.index + token.length);
                    const lines = [...new Set([...range.getClientRects()]
                      .filter((rect) => rect.width > 0 && rect.height > 0)
                      .map((rect) => Math.round(rect.top * 10) / 10))];
                    if (lines.length > 1) tokenSplits.push(token);
                  }
                }
                const lineCounts = {};
                for (const element of slide.querySelectorAll('[data-lines]')) {
                  lineCounts[element.dataset.lines] = lineCounts[element.dataset.lines] || [];
                  lineCounts[element.dataset.lines].push(visualLines(element));
                }
                const video = slide.querySelector('video');
                findings[number] = {
                  refresh: slide.querySelector('[data-result-refresh]')?.dataset.resultRefresh || null,
                  markedElements: elements.length,
                  overflow,
                  smallText,
                  overlaps,
                  tokenSplits,
                  lineCounts,
                  videoRect: video ? {
                    width: Math.round(video.getBoundingClientRect().width),
                    height: Math.round(video.getBoundingClientRect().height),
                    paused: video.paused,
                    muted: video.muted,
                  } : null,
                  slideHeight: Math.round(slideRect.height),
                };
              }
              return findings;
            })()
            """
        )
        for number in (1, 2):
            with self.subTest(slide=number):
                item = result[str(number)]
                self.assertEqual(item["refresh"], str(number), result)
                self.assertGreaterEqual(item["markedElements"], 1, result)
                self.assertEqual(item["overflow"], [], result)
                self.assertEqual(item["smallText"], [], result)
                self.assertEqual(item["overlaps"], [], result)
                self.assertEqual(item["tokenSplits"], [], result)
                if number == 1:
                    self.assertEqual(item["lineCounts"], {}, result)
                    self.assertIsNotNone(item["videoRect"], result)
                    self.assertGreaterEqual(item["videoRect"]["height"], item["slideHeight"] * 0.45, result)
                    self.assertFalse(item["videoRect"]["paused"], result)
                    self.assertTrue(item["videoRect"]["muted"], result)
                else:
                    self.assertTrue(item["lineCounts"], result)
                    for declared, counts in item["lineCounts"].items():
                        self.assertEqual(counts, [int(declared)] * len(counts), result)
                    self.assertEqual(len(item["lineCounts"].get("2", [])), 1, result)
                    self.assertEqual(len(item["lineCounts"].get("1", [])), 7, result)

    def test_real_hover_video_autoplays_and_resets_after_leaving_slide(self) -> None:
        self._evaluate("document.querySelector('deck-stage').goTo(0)")
        self._evaluate("document.querySelector('deck-stage')._fit()")
        deadline = time.monotonic() + 8.0
        after_enter = None
        while time.monotonic() < deadline:
            after_enter = self._evaluate(
                """
                (() => {
                  const video = document.querySelector('deck-stage')._slides[0].querySelector('video');
                  return video ? {
                    paused: video.paused,
                    muted: video.muted,
                    currentTime: video.currentTime
                  } : null;
                })()
                """
            )
            if after_enter and not after_enter["paused"]:
                break
            time.sleep(0.1)
        self.assertIsNotNone(after_enter, "video never appeared on slide 1")
        self.assertFalse(after_enter["paused"], after_enter)
        self.assertTrue(after_enter["muted"], after_enter)
        self.assertGreaterEqual(after_enter["currentTime"], 0, after_enter)

        self._evaluate("document.querySelector('deck-stage').goTo(1)")
        self._evaluate("document.querySelector('deck-stage')._fit()")
        deadline = time.monotonic() + 8.0
        after_leave = None
        while time.monotonic() < deadline:
            after_leave = self._evaluate(
                """
                (() => {
                  const video = document.querySelector('deck-stage')._slides[0].querySelector('video');
                  return video ? {
                    paused: video.paused,
                    muted: video.muted,
                    currentTime: video.currentTime
                  } : null;
                })()
                """
            )
            if after_leave and after_leave["paused"]:
                break
            time.sleep(0.1)
        self.assertIsNotNone(after_leave, "video never settled after leaving slide 1")
        self.assertTrue(after_leave["paused"], after_leave)


if __name__ == "__main__":
    unittest.main()
