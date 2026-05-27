"""
NMK: Arabic text shaping helper for raylib UI.

raylib does not support Arabic contextual joining or RTL bidi.
This module applies arabic_reshaper + python-bidi to convert
logical Unicode text into visual form ready for left-to-right rendering.

Usage:
    from openpilot.system.ui.lib.arabic_text import shape_arabic
    text = shape_arabic("مرحبا بكم")  # returns visual form
    rl.draw_text_ex(font, text, position, size, 0, color)
"""
from functools import lru_cache
import arabic_reshaper
from bidi.algorithm import get_display


def _has_arabic(text: str) -> bool:
  """Check if text contains any Arabic characters."""
  for ch in text:
    cp = ord(ch)
    if 0x0600 <= cp <= 0x06FF or 0xFB50 <= cp <= 0xFDFF or 0xFE70 <= cp <= 0xFEFF:
      return True
  return False


@lru_cache(maxsize=1024)
def shape_arabic(text: str) -> str:
  """
  Convert logical Arabic text to visual form for raylib rendering.

  - Applies contextual joining (initial/medial/final/isolated forms)
  - Applies RTL bidi reordering
  - Cached for performance (UI labels processed only once)
  - Pure ASCII/Latin text returned unchanged
  """
  if not text or not _has_arabic(text):
    return text
  reshaped = arabic_reshaper.reshape(text)
  return get_display(reshaped)
