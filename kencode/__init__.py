# =============================================================================
# Kencode — Accessible Programming Through Natural Language
# =============================================================================
# Copyright (c) 2025  Khalid Alkhaldi <k.t.alkhaldi@gmail.com>
#
# Licensed under the Creative Commons Attribution-NonCommercial-ShareAlike
# 4.0 International License (CC BY-NC-SA 4.0).
# You may not use this file for commercial purposes.
# Full license: https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# Author  : Khalid Alkhaldi
# Email   : k.t.alkhaldi@gmail.com
# GitHub  : https://github.com/khalidt
# Website : https://khalidalkhaldi.pythonanywhere.com/
# Version : 1.0.0
# =============================================================================

"""
Kencode — Accessible Programming Through Natural Language
=========================================================

Kencode maps Python code to natural language sequences and back,
making programming accessible without punctuation or special characters.

Based on the research paper:
    Alkhaldi, K., Qassem, A., & Ludi, S. (2025).
    Kencode: Advancing Voice-Based Programming Through an Innovative,
    Standardized, and Taxonomic Structuring Approach.
    Journal of Visual Language and Computing, 8-17.
    https://doi.org/10.18293/JVLC2025-N3-079

Author  : Khalid Alkhaldi <k.t.alkhaldi@gmail.com>
GitHub  : https://github.com/khalidt
Website : https://khalidalkhaldi.pythonanywhere.com/
"""

from .kencode_converter import parse_line as python_to_kencode
from .kencode_decoder   import decode_kvi, decode_line as kencode_to_python

__version__   = "1.0.0"
__author__    = "Khalid Alkhaldi"
__email__     = "k.t.alkhaldi@gmail.com"
__license__   = "CC BY-NC-SA 4.0"
__url__       = "https://github.com/khalidt/kencode"

__all__ = [
    "python_to_kencode",
    "kencode_to_python",
    "decode_kvi",
]
