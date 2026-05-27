"""
NMK Welcome Screen — shown on first boot.
Saves "WelcomeCompleted" param after user taps Start.
"""
import pyray as rl
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.arabic_text import shape_arabic
from openpilot.system.ui.widgets import Widget


# ───── Colors ─────
BG_COLOR = rl.Color(20, 20, 20, 255)
ACCENT_COLOR = rl.Color(70, 91, 234, 255)
ACCENT_PRESSED = rl.Color(50, 71, 200, 255)
TITLE_COLOR = rl.WHITE
SUBTITLE_COLOR = rl.Color(200, 200, 200, 255)
FOOTER_COLOR = rl.Color(120, 120, 120, 255)
DIVIDER_COLOR = rl.Color(70, 91, 234, 200)

# ───── Texts (Arabic by default) ─────
TITLE_TEXT = shape_arabic("مرحباً بكم في القائد الآلي")
SUBTITLE_TEXT = shape_arabic("نظام مساعدة السائق المتقدم")
BRAND_TEXT = shape_arabic("بواسطة NMK.Ai")
BUTTON_TEXT = shape_arabic("ابدأ")
FOOTER_TEXT = "nmk.sa"

# ───── Sizes ─────
TITLE_SIZE = 120
SUBTITLE_SIZE = 60
BRAND_SIZE = 48
BUTTON_FONT_SIZE = 70
FOOTER_SIZE = 36

BUTTON_W = 520
BUTTON_H = 150


class WelcomeScreen(Widget):
  def __init__(self, on_complete=None):
    super().__init__()
    self._on_complete = on_complete
    self._button_rect = rl.Rectangle(0, 0, BUTTON_W, BUTTON_H)
    self._button_pressed = False
    self._click_started_in_button = False

  def _render(self, _):
    rect = self._rect

    # Background
    rl.draw_rectangle_rec(rect, BG_COLOR)

    cx = rect.x + rect.width / 2
    cy = rect.y + rect.height / 2

    # ── Title ──
    title_font = gui_app.font(FontWeight.BOLD)
    title_sz = measure_text_cached(title_font, TITLE_TEXT, TITLE_SIZE)
    rl.draw_text_ex(
      title_font, TITLE_TEXT,
      rl.Vector2(cx - title_sz.x / 2, cy - 280),
      TITLE_SIZE, 0, TITLE_COLOR
    )

    # ── Accent divider line under title ──
    line_w = 200
    rl.draw_rectangle_rounded(
      rl.Rectangle(cx - line_w / 2, cy - 140, line_w, 6),
      1.0, 4, DIVIDER_COLOR
    )

    # ── Subtitle ──
    sub_font = gui_app.font(FontWeight.NORMAL)
    sub_sz = measure_text_cached(sub_font, SUBTITLE_TEXT, SUBTITLE_SIZE)
    rl.draw_text_ex(
      sub_font, SUBTITLE_TEXT,
      rl.Vector2(cx - sub_sz.x / 2, cy - 90),
      SUBTITLE_SIZE, 0, SUBTITLE_COLOR
    )

    # ── Brand line ──
    brand_font = gui_app.font(FontWeight.MEDIUM)
    brand_sz = measure_text_cached(brand_font, BRAND_TEXT, BRAND_SIZE)
    rl.draw_text_ex(
      brand_font, BRAND_TEXT,
      rl.Vector2(cx - brand_sz.x / 2, cy - 20),
      BRAND_SIZE, 0, SUBTITLE_COLOR
    )

    # ── Start Button ──
    btn_x = cx - BUTTON_W / 2
    btn_y = cy + 100
    self._button_rect = rl.Rectangle(btn_x, btn_y, BUTTON_W, BUTTON_H)

    self._handle_button_input()

    btn_color = ACCENT_PRESSED if self._button_pressed else ACCENT_COLOR
    rl.draw_rectangle_rounded(self._button_rect, 0.4, 12, btn_color)

    btn_font = gui_app.font(FontWeight.SEMI_BOLD)
    btn_text_sz = measure_text_cached(btn_font, BUTTON_TEXT, BUTTON_FONT_SIZE)
    rl.draw_text_ex(
      btn_font, BUTTON_TEXT,
      rl.Vector2(
        btn_x + (BUTTON_W - btn_text_sz.x) / 2,
        btn_y + (BUTTON_H - btn_text_sz.y) / 2 - 4,
      ),
      BUTTON_FONT_SIZE, 0, rl.WHITE
    )

    # ── Footer ──
    foot_font = gui_app.font(FontWeight.MEDIUM)
    foot_sz = measure_text_cached(foot_font, FOOTER_TEXT, FOOTER_SIZE)
    rl.draw_text_ex(
      foot_font, FOOTER_TEXT,
      rl.Vector2(cx - foot_sz.x / 2, rect.y + rect.height - 80),
      FOOTER_SIZE, 0, FOOTER_COLOR
    )

  def _handle_button_input(self):
    for event in gui_app.mouse_events:
      pt = rl.Vector2(event.pos.x, event.pos.y)
      in_btn = rl.check_collision_point_rec(pt, self._button_rect)

      if event.left_pressed and in_btn:
        self._click_started_in_button = True
        self._button_pressed = True
      elif event.left_released:
        if self._click_started_in_button and in_btn:
          self._complete()
        self._click_started_in_button = False
        self._button_pressed = False
      elif event.left_down:
        self._button_pressed = self._click_started_in_button and in_btn

  def _complete(self):
    # NMK: No param write; HasAcceptedTerms acts as the gate for Welcome
    if self._on_complete is not None:
      self._on_complete()


# ───── Standalone test mode ─────
# Run: python -m openpilot.selfdrive.ui.layouts.welcome
if __name__ == "__main__":
  gui_app.init_window("Welcome Test")
  welcome = WelcomeScreen(on_complete=lambda: print("✓ Welcome complete!"))
  full_rect = rl.Rectangle(0, 0, gui_app.width, gui_app.height)

  for _ in gui_app.render():
    welcome.render(full_rect)
