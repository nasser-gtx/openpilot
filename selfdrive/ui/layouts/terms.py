"""
NMK Terms & Conditions Screen — shown after Welcome.
Saves HasAcceptedTerms = terms_version on accept.
"""
import pyray as rl
from openpilot.common.params import Params
from openpilot.system.version import terms_version
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.arabic_text import shape_arabic
from openpilot.system.ui.widgets import Widget


BG_COLOR = rl.Color(20, 20, 20, 255)
PANEL_COLOR = rl.Color(40, 40, 40, 255)
TITLE_COLOR = rl.WHITE
TEXT_COLOR = rl.Color(220, 220, 220, 255)
ACCENT_COLOR = rl.Color(70, 91, 234, 255)
ACCENT_PRESSED = rl.Color(50, 71, 200, 255)
DANGER_COLOR = rl.Color(80, 80, 80, 255)
DANGER_PRESSED = rl.Color(60, 60, 60, 255)

TITLE = shape_arabic("الشروط والأحكام")
BODY_LINES = [
  shape_arabic("القائد الآلي نظام مساعدة للسائق وليس قيادة ذاتية."),
  shape_arabic("أنت مسؤول عن قيادة السيارة في جميع الأوقات."),
  "",
  shape_arabic("• ابقَ منتبهاً للطريق دائماً"),
  shape_arabic("• ضع يديك على عجلة القيادة"),
  shape_arabic("• التزم بأنظمة المرور"),
  "",
  shape_arabic("باستخدامك القائد الآلي توافق على تحمّل المسؤولية"),
  shape_arabic("الكاملة عن القيادة وقراءة دليل المستخدم قبل البدء."),
  "",
  shape_arabic("للاطلاع على الشروط كاملة:"),
  "https://nmk.sa/terms",
]
ACCEPT_TEXT = shape_arabic("أوافق")
DECLINE_TEXT = shape_arabic("رفض")

TITLE_SIZE = 90
BODY_SIZE = 42
BUTTON_SIZE = 64


class TermsScreen(Widget):
  def __init__(self, on_accept=None, on_decline=None):
    super().__init__()
    self._params = Params()
    self._on_accept = on_accept
    self._on_decline = on_decline
    self._accept_rect = rl.Rectangle(0, 0, 0, 0)
    self._decline_rect = rl.Rectangle(0, 0, 0, 0)
    self._accept_pressed = False
    self._decline_pressed = False
    self._click_started_in = None
    self._fired = False

  def _render(self, _):
    rect = self._rect
    rl.draw_rectangle_rec(rect, BG_COLOR)
    cx = rect.x + rect.width / 2

    # Title
    title_font = gui_app.font(FontWeight.BOLD)
    title_sz = measure_text_cached(title_font, TITLE, TITLE_SIZE)
    rl.draw_text_ex(title_font, TITLE,
      rl.Vector2(cx - title_sz.x / 2, rect.y + 60),
      TITLE_SIZE, 0, TITLE_COLOR)

    # Accent line
    rl.draw_rectangle_rounded(
      rl.Rectangle(cx - 100, rect.y + 180, 200, 6), 1.0, 4, ACCENT_COLOR)

    # Body panel
    panel_x = rect.x + 120
    panel_w = rect.width - 240
    panel_y = rect.y + 230
    panel_h = rect.height - 460
    rl.draw_rectangle_rounded(
      rl.Rectangle(panel_x, panel_y, panel_w, panel_h),
      0.03, 8, PANEL_COLOR)

    # Body lines (right-aligned)
    body_font = gui_app.font(FontWeight.NORMAL)
    line_h = BODY_SIZE + 18
    cur_y = panel_y + 50
    for line in BODY_LINES:
      if not line:
        cur_y += line_h // 2
        continue
      line_sz = measure_text_cached(body_font, line, BODY_SIZE)
      line_x = panel_x + panel_w - 50 - line_sz.x
      color = ACCENT_COLOR if line.startswith("http") else TEXT_COLOR
      rl.draw_text_ex(body_font, line, rl.Vector2(line_x, cur_y),
                      BODY_SIZE, 0, color)
      cur_y += line_h

    # Buttons
    btn_y = rect.y + rect.height - 180
    btn_h = 130
    btn_w = (rect.width - 360) / 2
    spacing = 60
    decline_x = rect.x + 120
    accept_x = decline_x + btn_w + spacing
    self._decline_rect = rl.Rectangle(decline_x, btn_y, btn_w, btn_h)
    self._accept_rect = rl.Rectangle(accept_x, btn_y, btn_w, btn_h)

    self._handle_input()

    btn_font = gui_app.font(FontWeight.SEMI_BOLD)
    # Decline
    dc = DANGER_PRESSED if self._decline_pressed else DANGER_COLOR
    rl.draw_rectangle_rounded(self._decline_rect, 0.4, 12, dc)
    dec_sz = measure_text_cached(btn_font, DECLINE_TEXT, BUTTON_SIZE)
    rl.draw_text_ex(btn_font, DECLINE_TEXT,
      rl.Vector2(decline_x + (btn_w - dec_sz.x) / 2,
                 btn_y + (btn_h - dec_sz.y) / 2 - 4),
      BUTTON_SIZE, 0, rl.WHITE)
    # Accept
    ac = ACCENT_PRESSED if self._accept_pressed else ACCENT_COLOR
    rl.draw_rectangle_rounded(self._accept_rect, 0.4, 12, ac)
    acc_sz = measure_text_cached(btn_font, ACCEPT_TEXT, BUTTON_SIZE)
    rl.draw_text_ex(btn_font, ACCEPT_TEXT,
      rl.Vector2(accept_x + (btn_w - acc_sz.x) / 2,
                 btn_y + (btn_h - acc_sz.y) / 2 - 4),
      BUTTON_SIZE, 0, rl.WHITE)

  def _handle_input(self):
    if self._fired:
      return
    for event in gui_app.mouse_events:
      pt = rl.Vector2(event.pos.x, event.pos.y)
      in_accept = rl.check_collision_point_rec(pt, self._accept_rect)
      in_decline = rl.check_collision_point_rec(pt, self._decline_rect)
      if event.left_pressed:
        if in_accept:
          self._click_started_in = "accept"; self._accept_pressed = True
        elif in_decline:
          self._click_started_in = "decline"; self._decline_pressed = True
      elif event.left_released:
        if self._click_started_in == "accept" and in_accept:
          self._fired = True
          self._params.put("HasAcceptedTerms", terms_version)
          if self._on_accept: self._on_accept()
        elif self._click_started_in == "decline" and in_decline:
          self._fired = True
          if self._on_decline: self._on_decline()
        self._click_started_in = None
        self._accept_pressed = False
        self._decline_pressed = False
      elif event.left_down:
        self._accept_pressed = (self._click_started_in == "accept" and in_accept)
        self._decline_pressed = (self._click_started_in == "decline" and in_decline)


if __name__ == "__main__":
  gui_app.init_window("Terms Test")
  scr = TermsScreen(
    on_accept=lambda: print("✓ accepted"),
    on_decline=lambda: print("✗ declined"))
  full = rl.Rectangle(0, 0, gui_app.width, gui_app.height)
  for _ in gui_app.render():
    scr.render(full)
