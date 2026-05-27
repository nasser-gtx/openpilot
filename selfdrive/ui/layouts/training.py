"""
NMK Training Screen — original openpilot style.
Tap right side of screen to advance, left side to go back.
Saves CompletedTrainingVersion on finish.
"""
import pyray as rl
from openpilot.common.params import Params
from openpilot.system.version import training_version
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget


TOTAL_STEPS = 19  # step0.png .. step18.png
INDICATOR_COLOR = rl.Color(255, 255, 255, 180)
INDICATOR_BG = rl.Color(0, 0, 0, 120)


class TrainingScreen(Widget):
  def __init__(self, on_complete=None):
    super().__init__()
    self._params = Params()
    self._on_complete = on_complete
    self._current_step = 0
    self._completed = False  # Guard against double-fire

  def _render(self, _):
    rect = self._rect
    rl.draw_rectangle_rec(rect, rl.BLACK)

    # Full-screen image (preserving aspect ratio)
    img_path = f"training/step{self._current_step}.png"
    try:
      texture = gui_app.texture(img_path, int(rect.width), int(rect.height),
                                keep_aspect_ratio=True)
      img_x = rect.x + (rect.width - texture.width) / 2
      img_y = rect.y + (rect.height - texture.height) / 2
      rl.draw_texture(texture, int(img_x), int(img_y), rl.WHITE)
    except Exception:
      pass

    # Handle taps (right half = next, left half = back)
    self._handle_taps(rect)

  def _handle_taps(self, rect):
    if self._completed:
      return
    mid_x = rect.x + rect.width / 2

    for event in gui_app.mouse_events:
      # ONLY react on left_released (avoids press+release double-fire)
      if not event.left_released:
        continue

      if event.pos.x >= mid_x:
        # Right half → advance (or complete)
        self._advance()
      else:
        # Left half → previous (no-op on step 0)
        if self._current_step > 0:
          self._current_step -= 1
      # Process only ONE tap per frame
      return

  def _advance(self):
    if self._completed:
      return
    if self._current_step >= TOTAL_STEPS - 1:
      self._completed = True
      self._params.put("CompletedTrainingVersion", training_version)
      if self._on_complete:
        self._on_complete()
    else:
      self._current_step += 1


if __name__ == "__main__":
  gui_app.init_window("Training Test")
  scr = TrainingScreen(on_complete=lambda: print("✓ Training complete"))
  full = rl.Rectangle(0, 0, gui_app.width, gui_app.height)
  for _ in gui_app.render():
    scr.render(full)
