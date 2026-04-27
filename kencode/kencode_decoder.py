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
kencode_decoder.py  v2.0
=========================
Bidirectional Kencode converter: KVI -> KS + Python code.

Usage:
    python kencode_decoder.py                    # interactive REPL
    python kencode_decoder.py "kvi instruction"  # single line
    python kencode_decoder.py -f kvi_file.txt    # file of KVI lines
"""

import re, sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NUM_VERBAL = {
    "zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,
    "six":6,"seven":7,"eight":8,"nine":9,"ten":10,"eleven":11,
    "twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,"sixteen":16,
    "seventeen":17,"eighteen":18,"nineteen":19,"twenty":20,"thirty":30,
    "forty":40,"fifty":50,"sixty":60,"seventy":70,"eighty":80,
    "ninety":90,"hundred":100,
}

def num_to_digit(v):
    return str(NUM_VERBAL.get(v.lower(), v))

OPERATOR_VERBAL = {
    "equals":"=","plus equal":"+=","minus equal":"-=","times equal":"*=",
    "divided equal":"/=","modulo equal":"%=","power equal":"**=",
    "floor divided equal":"//=","is equal":"==","not equal":"!=",
    "less or equal":"<=","greater or equal":">=","less than":"<",
    "greater than":">","plus":"+","minus":"-","times":"*",
    "divided by":"/","floor divided by":"//","modulo":"%","power":"**",
    "in":"in","not":"not","and":"and","or":"or","is":"is",
}
OP_KEYS = sorted(OPERATOR_VERBAL.keys(), key=len, reverse=True)

ESCAPE_MAP = {
    "new line":"\\n","horizontal tab":"\\t","backslash":"\\\\",
    "single quote":"\\'","double quote":'\\"',"carriage return":"\\r",
    "backspace":"\\b","form feed":"\\f","bell":"\\a","vertical tab":"\\v",
}

BASE_WORDS = {
    "comment","tab","variable","digit","point","string","special",
    "call","pass","object","attribute","method","key","value",
    "list","set","tuple","dict","index","f-string","formatting",
    "precision","left-align","right-align","center-align",
    "expression","hook","type","ignore","unpack","keyword-only","dictionary",
}
BASE_WORDS_2 = {"list unpack","dictionary unpack"}

CONTROL_KW = {
    "if","elif","else","while","for","in","not","and","or",
    "with","as","return","import","from","class","def","try",
    "except","raise","pass","break","continue","lambda","yield",
    "global","nonlocal","del","assert","print","true","false","none",
}

# ---------------------------------------------------------------------------
# Token
# ---------------------------------------------------------------------------
class T:
    __slots__ = ("tag","verbal")
    def __init__(self, tag, verbal):
        self.tag    = f"[{tag}]"
        self.verbal = verbal
    def __repr__(self):
        return f"T({self.tag},{self.verbal!r})"

def K(v): return T("K", v)
def O(v): return T("O", v)
def W(v): return T("W", v)
def B(v): return T("B", v)

# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

def tokenise_kvi(kvi):
    words = kvi.split()
    n     = len(words)
    toks  = []
    i     = 0
    while i < n:
        w  = words[i]
        wl = w.lower()

        # indent prefix
        if wl.isdigit() and i+1 < n and words[i+1].lower() == "tab":
            toks.append(W(w)); toks.append(B("tab")); i += 2; continue

        # two-word base-words
        if i+1 < n:
            two = f"{wl} {words[i+1].lower()}"
            if two in BASE_WORDS_2:
                toks.append(B(two)); i += 2; continue

        # single base-word
        if wl in BASE_WORDS:
            toks.append(B(wl)); i += 1; continue

        # ambiguous keywords: always [K] (in, not, and, or)
        if wl in ("in","not","and","or"):
            toks.append(K(wl)); i += 1; continue

        # "is equal" as two-word [O]; bare "is" as [O] only between value tokens
        if wl == "is":
            # try two-word "is equal" first
            if i+1 < n and words[i+1].lower() == "equal":
                toks.append(O("is equal")); i += 2; continue
            # bare "is": only [O] when preceded by a value token
            prev_ok = bool(toks) and toks[-1].tag in ("[W]","[K]")
            if prev_ok:
                toks.append(O("is")); i += 1; continue
            else:
                toks.append(W(w)); i += 1; continue

        # multi-word operator (greedy, longest first)
        matched = False
        for op in OP_KEYS:
            if op in ("in","not","and","or","is","is equal"): continue  # already handled
            op_ws = op.split()
            end = i + len(op_ws)
            if end <= n:
                cand = " ".join(words[i:end]).lower()
                if cand == op:
                    toks.append(O(op)); i = end; matched = True; break
        if matched: continue

        # control keyword
        if wl in CONTROL_KW:
            toks.append(K(wl)); i += 1; continue

        # plain word
        toks.append(W(w)); i += 1
    return toks

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, toks):
        self.toks = toks
        self.pos  = 0

    def peek(self, offset=0):
        idx = self.pos + offset
        return self.toks[idx] if idx < len(self.toks) else None

    def consume(self):
        t = self.toks[self.pos]; self.pos += 1; return t

    def at_end(self):
        return self.pos >= len(self.toks)

    def collect_W(self):
        ws = []
        while self.peek() and self.peek().tag == "[W]":
            ws.append(self.consume().verbal)
        return ws

    def words_to_name(self, ws):
        return "_".join(ws)

    # -- value parser --

    def parse_value(self):
        t = self.peek()
        if not t: return ""

        if t.tag == "[B]" and t.verbal == "ignore":
            self.consume(); return "_"

        if t.tag == "[B]" and t.verbal in ("variable","object"):
            self.consume()
            name = self.words_to_name(self.collect_W())
            return self._chain(name)

        if t.tag == "[B]" and t.verbal == "digit":
            self.consume()
            ws = self.collect_W()
            if not ws: return "0"
            int_part = num_to_digit(ws[0])
            if self.peek() and self.peek().tag == "[B]" and self.peek().verbal == "point":
                self.consume()
                dec_ws = self.collect_W()
                return f"{int_part}.{dec_ws[0] if dec_ws else '0'}"
            return int_part

        if t.tag == "[B]" and t.verbal == "string":
            self.consume(); return self._string_content()

        if t.tag == "[K]" and t.verbal.lower() in ("true","false","none"):
            return self.consume().verbal.capitalize()

        if t.tag == "[B]" and t.verbal == "call":
            return self._call()

        if t.tag == "[K]" and t.verbal == "lambda":
            return self._lambda()

        if t.tag == "[B]" and t.verbal == "f-string":
            return self._fstring()

        if t.tag == "[B]" and t.verbal in ("list","set","tuple"):
            return self._collection(t.verbal)

        if t.tag == "[B]" and t.verbal in ("list unpack","dictionary unpack"):
            self.consume()
            name = self.words_to_name(self.collect_W())
            prefix = "*" if "list" in t.verbal else "**"
            return f"{prefix}{name}"

        return ""

    def _chain(self, base):
        result = base
        while self.peek() and self.peek().tag == "[B]":
            bw = self.peek().verbal
            if bw == "attribute":
                self.consume()
                result += f".{self.words_to_name(self.collect_W())}"
            elif bw == "method":
                self.consume()
                meth = self.words_to_name(self.collect_W())
                if self.peek() and self.peek().tag == "[B]" and self.peek().verbal == "pass":
                    self.consume(); args = self._args()
                    result += f".{meth}({args})"
                else:
                    result += f".{meth}()"
            elif bw == "index":
                self.consume()
                it = self.peek()
                if it and it.tag == "[B]" and it.verbal == "digit":
                    self.consume()
                    neg = ""
                    if self.peek() and self.peek().tag == "[O]" and self.peek().verbal == "minus":
                        self.consume(); neg = "-"
                    ws = self.collect_W()
                    n = num_to_digit(ws[0]) if ws else "0"
                    result += f"[{neg}{n}]"
                elif it and it.tag == "[B]" and it.verbal == "string":
                    self.consume(); s = self._string_content(); result += f"[{s}]"
                elif it and it.tag == "[B]" and it.verbal == "variable":
                    self.consume(); result += f"[{self.words_to_name(self.collect_W())}]"
            elif bw == "key":
                self.consume()
                kt = self.peek()
                if kt and kt.tag == "[B]" and kt.verbal == "string":
                    self.consume(); s = self._string_content(); result += f"[{s}]"
                elif kt and kt.tag == "[B]" and kt.verbal == "digit":
                    self.consume(); ws = self.collect_W()
                    result += f"[{num_to_digit(ws[0]) if ws else '0'}]"
            elif bw == "dict":
                # "data dict key string ages" → data["ages"]
                self.consume()
                if self.peek() and self.peek().tag == "[B]" and self.peek().verbal == "key":
                    self.consume()
                    kt = self.peek()
                    if kt and kt.tag == "[B]" and kt.verbal == "string":
                        self.consume(); s = self._string_content(); result += f"[{s}]"
                    elif kt and kt.tag == "[B]" and kt.verbal == "digit":
                        self.consume(); ws = self.collect_W()
                        result += f"[{num_to_digit(ws[0]) if ws else '0'}]"
            else:
                break
        return result

    def _string_content(self):
        # Collect words — also absorb [O]/[K] tokens that are plain English words
        # appearing inside string text (is, and, or, not, in)
        PLAIN_OPS = {"is","and","or","not","in"}
        STRING_STOP = {"formatting","special","f-string","call","variable","digit",
                       "key","value","list","set","tuple","dict","object","attribute",
                       "method","index","expression","hook","type","ignore","pass"}

        def collect_string_words():
            ws = []
            while self.peek():
                t = self.peek()
                if t.tag == "[W]":
                    ws.append(self.consume().verbal)
                elif t.tag in ("[O]","[K]") and t.verbal in PLAIN_OPS:
                    # Absorb if followed by more string content (not a hard stop)
                    nxt = self.peek(1)
                    if nxt is None or (nxt.tag == "[B]" and nxt.verbal in STRING_STOP):
                        # "is" immediately before [B]formatting → absorb it as string word
                        ws.append(self.consume().verbal)
                    elif nxt.tag in ("[W]","[O]","[K]"):
                        ws.append(self.consume().verbal)
                    else:
                        break
                else:
                    break
            return ws

        ws = collect_string_words()
        parts = [" ".join(ws)]
        while self.peek() and self.peek().tag == "[B]" and self.peek().verbal == "special":
            self.consume()
            esc_ws = collect_string_words()
            esc = " ".join(esc_ws)
            if esc.startswith("octal "): parts.append(f"\\{esc[6:]}")
            elif esc.startswith("hex "): parts.append(f"\\x{esc[4:]}")
            elif esc.startswith("unicode "): parts.append(f"\\u{esc[8:]}")
            else: parts.append(ESCAPE_MAP.get(esc, f"\\?{esc}"))
            trail = collect_string_words()
            if trail: parts.append(" ".join(trail))
        return '"' + "".join(parts) + '"'

    def _call(self):
        self.consume()   # consume "call"
        if self.peek() and self.peek().tag == "[B]" and self.peek().verbal == "hook":
            self.consume()
            fname = f"__{self.words_to_name(self.collect_W())}__"
        else:
            # After "call", function name may come as [W] words OR a single [B] word
            # used as a function name (e.g. "list", "filter", "range", "map", "zip")
            fname_parts = []
            while self.peek():
                t = self.peek()
                if t.tag == "[W]":
                    fname_parts.append(self.consume().verbal)
                elif t.tag == "[B]" and t.verbal not in ("pass","hook") and not fname_parts:
                    # First token after call is a [B] base-word used as function name
                    fname_parts.append(self.consume().verbal)
                    break
                else:
                    break
            fname = "_".join(fname_parts)
        if self.peek() and self.peek().tag == "[B]" and self.peek().verbal == "pass":
            self.consume(); args = self._args()
            return f"{fname}({args})"
        return f"{fname}()"

    def _args(self):
        items = []
        VALUE_B = {
            "variable","digit","string","call","object","list","tuple",
            "set","ignore","list unpack","dictionary unpack","f-string","hook","dictionary",
        }
        while not self.at_end():
            t = self.peek()
            if t.tag == "[B]" and t.verbal == "pass":
                self.consume(); continue
            if t.tag == "[B]" and t.verbal in VALUE_B:
                # keyword arg?
                if t.verbal == "variable":
                    self.consume()
                    ws = self.collect_W(); name = self.words_to_name(ws)
                    if self.peek() and self.peek().tag=="[O]" and self.peek().verbal=="equals":
                        self.consume(); val = self.parse_value()
                        items.append(f"{name}={val}")
                    else:
                        items.append(self._chain(name))
                else:
                    items.append(self.parse_value())
            elif t.tag == "[K]" and t.verbal in ("true","false","none","lambda"):
                items.append(self.parse_value())
            else:
                break
        return ", ".join(items)

    def _collection(self, kind):
        self.consume()
        VALUE_B = {"digit","string","variable","call","list","tuple","set","ignore","object"}
        items = []
        while not self.at_end():
            t = self.peek()
            if t.tag == "[B]" and t.verbal in VALUE_B:
                items.append(self.parse_value())
            elif t.tag == "[K]" and t.verbal in ("true","false","none"):
                items.append(self.parse_value())
            else:
                break
        if kind == "list":  return "[" + ", ".join(items) + "]"
        if kind == "tuple": return "(" + ", ".join(items) + ")"
        return "{" + ", ".join(items) + "}"

    def _lambda(self):
        self.consume()
        params = []
        PARAM_B = {"variable","keyword-only","tuple","dictionary"}
        while self.peek() and self.peek().tag=="[B]" and self.peek().verbal in PARAM_B:
            bw = self.consume().verbal
            if bw == "keyword-only": params.append("*"); continue
            name = self.words_to_name(self.collect_W())
            if bw == "tuple":        params.append(f"*{name}")
            elif bw == "dictionary": params.append(f"**{name}")
            elif self.peek() and self.peek().tag=="[O]" and self.peek().verbal=="equals":
                self.consume(); params.append(f"{name}={self.parse_value()}")
            else: params.append(name)
        body = "None"
        if self.peek() and self.peek().tag=="[B]" and self.peek().verbal=="expression":
            self.consume(); body = self._expr()
        return f"lambda {', '.join(params)}: {body}"

    def _fstring(self):
        self.consume(); content = ""
        while not self.at_end():
            t = self.peek()
            if t.tag == "[B]" and t.verbal == "string":
                self.consume()
                s = self._string_content()
                raw = s[1:-1]
                # add trailing space if followed by a formatting block
                if self.peek() and self.peek().tag=="[B]" and self.peek().verbal=="formatting":
                    raw += " "
                content += raw
            elif t.tag == "[B]" and t.verbal == "formatting":
                self.consume()
                py_v = self.parse_value(); fmt = ""
                if self.peek() and self.peek().tag == "[B]":
                    bw = self.peek().verbal
                    align_map = {"left-align":"<","right-align":">","center-align":"^"}
                    if bw in align_map:
                        self.consume(); ac = align_map[bw]
                        if self.peek() and self.peek().verbal == "digit":
                            self.consume(); ws = self.collect_W()
                            n = num_to_digit(ws[0]) if ws else ""
                            fmt = f":{ac}{n}"
                    elif bw == "precision":
                        self.consume(); self.consume()
                        ws = self.collect_W(); fmt = f":.{ws[0] if ws else '2'}f"
                content += "{" + py_v + fmt + "}"
            else: break
        return f'f"{content}"'

    def _expr(self):
        left = self.parse_value()
        while self.peek() and self.peek().tag == "[O]":
            op_t = self.consume()
            op_sym = OPERATOR_VERBAL.get(op_t.verbal, op_t.verbal)
            left = f"{left} {op_sym} {self.parse_value()}"
        return left

# ---------------------------------------------------------------------------
# Line decoder helpers
# ---------------------------------------------------------------------------

def _parse_condition(p):
    parts = []
    VALUE_B = {"variable","digit","string","call","object","list","tuple","set","ignore"}
    while not p.at_end():
        t = p.peek()
        if t.tag == "[K]" and t.verbal.lower() in ("not","and","or","in","true","false","none"):
            v = p.consume().verbal
            parts.append(v.capitalize() if v.lower() in ("true","false","none") else v)
        elif t.tag == "[O]":
            op_t = p.consume()
            parts.append(OPERATOR_VERBAL.get(op_t.verbal, op_t.verbal))
        elif t.tag == "[B]" and t.verbal in VALUE_B:
            parts.append(p.parse_value())
        else:
            break
    return " ".join(parts)

def _parse_rhs(p):
    t = p.peek()
    if not t: return ""
    if t.tag == "[B]" and t.verbal == "key":
        return _parse_dict_pairs(p)
    if t.tag == "[B]" and t.verbal == "dict":
        p.consume(); return _parse_dict_pairs(p)
    val = p.parse_value()
    while p.peek() and p.peek().tag == "[O]":
        op_t = p.consume()
        op_sym = OPERATOR_VERBAL.get(op_t.verbal, op_t.verbal)
        val = f"{val} {op_sym} {p.parse_value()}"
    # ternary
    if p.peek() and p.peek().tag == "[K]" and p.peek().verbal == "if":
        p.consume(); cond = _parse_condition(p)
        if p.peek() and p.peek().tag == "[K]" and p.peek().verbal == "else":
            p.consume(); val = f"{val} if {cond} else {p.parse_value()}"
    return val

def _parse_dict_pairs(p):
    pairs = []
    while p.peek() and p.peek().tag == "[B]" and p.peek().verbal == "key":
        p.consume(); k = p.parse_value()
        if p.peek() and p.peek().tag == "[B]" and p.peek().verbal == "value":
            p.consume(); v = _parse_rhs(p)
            pairs.append(f"{k}: {v}")
    return "{" + ", ".join(pairs) + "}"

def _for_vars(p):
    vs = []
    while p.peek() and not (p.peek().tag=="[K]" and p.peek().verbal=="in"):
        t = p.peek()
        if t.tag == "[B]" and t.verbal == "ignore":
            p.consume(); vs.append("_")
        elif t.tag == "[B]" and t.verbal == "variable":
            p.consume()
            ws = p.collect_W()
            if not ws and p.peek() and p.peek().tag == "[B]":
                # [B]word used as variable name (e.g. key, value, list, set)
                ws = [p.consume().verbal]
            vs.append(p.words_to_name(ws))
        else: break
    return ", ".join(vs)

def _collect_lhs(p):
    """Collect LHS name parts (plain [W], [B]variable, [B]ignore) before [O]."""
    parts = []
    while not p.at_end():
        t = p.peek()
        if t.tag == "[B]" and t.verbal == "variable":
            p.consume()
            ws = p.collect_W()
            name = p.words_to_name(ws)
            # extend with attribute/index chain (e.g. self.name on LHS)
            while p.peek() and p.peek().tag == "[B]" and p.peek().verbal in ("attribute","index","key"):
                bw = p.consume().verbal
                if bw == "attribute":
                    ws2 = p.collect_W()
                    if not ws2 and p.peek() and p.peek().tag == "[B]":
                        ws2 = [p.consume().verbal]
                    name += "." + p.words_to_name(ws2)
                elif bw in ("index","key"):
                    kt = p.peek()
                    if kt and kt.tag == "[B]" and kt.verbal == "string":
                        p.consume(); s_ws = p.collect_W(); name += f'[\"{" ".join(s_ws)}\"]'
                    elif kt and kt.tag == "[B]" and kt.verbal == "digit":
                        p.consume(); ws2 = p.collect_W()
                        name += f"[{num_to_digit(ws2[0]) if ws2 else '0'}]"
            parts.append(name)
        elif t.tag == "[B]" and t.verbal == "ignore":
            p.consume(); parts.append("_")
        elif t.tag == "[W]":
            ws = p.collect_W()
            name = p.words_to_name(ws)
            # ambiguity: "my list equals ..." → "list" is [B] but acts as name part
            if (p.peek() and p.peek().tag == "[B]"
                    and p.peek().verbal in ("list","set","tuple","dict","dictionary")
                    and p.peek(1) and p.peek(1).tag == "[O]"):
                suffix = p.consume().verbal
                name = name + "_" + suffix
            parts.append(name)
        else: break
    return parts

# ---------------------------------------------------------------------------
# Main line decoder
# ---------------------------------------------------------------------------

def decode_line(kvi):
    kvi = kvi.strip()
    if not kvi: return ""
    toks = tokenise_kvi(kvi)
    p    = Parser(toks)

    # indentation
    indent = ""
    if p.peek() and p.peek().tag=="[W]" and p.peek().verbal.isdigit():
        if p.peek(1) and p.peek(1).tag=="[B]" and p.peek(1).verbal=="tab":
            indent = "    " * int(p.consume().verbal); p.consume()

    t = p.peek()
    if not t: return indent.rstrip()

    # comment
    if t.tag == "[B]" and t.verbal == "comment":
        p.consume()
        ws = []
        while not p.at_end(): ws.append(p.consume().verbal)
        return indent + "# " + " ".join(ws)

    # except
    if t.tag == "[K]" and t.verbal == "except":
        p.consume()
        if p.peek() and p.peek().tag=="[B]" and p.peek().verbal=="type":
            p.consume()
            parts = []
            while p.peek() and p.peek().tag=="[W]":
                parts.append(p.consume().verbal.capitalize())
            exc = "".join(parts)
            alias = ""
            if p.peek() and p.peek().tag=="[K]" and p.peek().verbal=="as":
                p.consume()
                if p.peek() and p.peek().tag=="[B]": p.consume()
                alias = " as " + p.words_to_name(p.collect_W())
            return indent + f"except {exc}{alias}:"
        return indent + "except:"

    # with open(...)
    if t.tag == "[K]" and t.verbal == "with":
        p.consume()
        for _ in range(3):  # skip: call, open, pass
            if p.peek() and p.peek().tag in ("[B]","[W]"): p.consume()
        args = []
        while p.peek() and not (p.peek().tag=="[K]" and p.peek().verbal=="as"):
            tok = p.peek()
            if tok.tag == "[B]" and tok.verbal == "string":
                p.consume()
                s = p._string_content()
                # restore dots: "test dot txt" -> "test.txt"
                inner = s[1:-1].replace(" dot ", ".").replace(" slash ", "/")
                args.append(f'"{inner}"')
            else: break
        alias = ""
        if p.peek() and p.peek().tag=="[K]" and p.peek().verbal=="as":
            p.consume()
            if p.peek() and p.peek().tag=="[B]": p.consume()
            alias = p.words_to_name(p.collect_W())
        return indent + f"with open({', '.join(args)}) as {alias}:"

    # def
    if t.tag == "[K]" and t.verbal == "def":
        p.consume()
        if p.peek() and p.peek().tag=="[B]" and p.peek().verbal=="hook":
            p.consume(); fname = f"__{p.words_to_name(p.collect_W())}__"
        else:
            fname = p.words_to_name(p.collect_W())
        params = []
        if p.peek() and p.peek().tag=="[B]" and p.peek().verbal=="pass":
            p.consume()
            PARAM_B = {"variable","tuple","dictionary","keyword-only"}
            while not p.at_end():
                pt = p.peek()
                if pt.tag=="[B]" and pt.verbal in PARAM_B:
                    bw = p.consume().verbal
                    if bw == "keyword-only": params.append("*"); continue
                    pname = p.words_to_name(p.collect_W())
                    if bw == "tuple":        params.append(f"*{pname}")
                    elif bw == "dictionary": params.append(f"**{pname}")
                    elif p.peek() and p.peek().tag=="[O]" and p.peek().verbal=="equals":
                        p.consume(); params.append(f"{pname}={p.parse_value()}")
                    else: params.append(pname)
                else: break
        return indent + f"def {fname}({', '.join(params)}):"

    # class
    if t.tag == "[K]" and t.verbal == "class":
        p.consume(); cname = p.words_to_name(p.collect_W())
        parents = []
        if p.peek() and p.peek().tag=="[B]" and p.peek().verbal=="pass":
            p.consume()
            while not p.at_end():
                pt = p.peek()
                if pt.tag=="[B]" and pt.verbal=="variable":
                    p.consume(); parents.append(p.words_to_name(p.collect_W()))
                else: break
        return indent + (f"class {cname}({', '.join(parents)}):" if parents
                         else f"class {cname}:")

    # for
    if t.tag == "[K]" and t.verbal == "for":
        p.consume(); var_str = _for_vars(p)
        if p.peek() and p.peek().tag=="[K]" and p.peek().verbal=="in": p.consume()
        iter_py = p.parse_value()
        # handle pass after iterable (for range(5) where _call() left args empty)
        # _call() in parse_value() handles pass+args internally
        # so iter_py is already complete (e.g. "range(5)")
        return indent + f"for {var_str} in {iter_py}:"

    # if / elif / while
    if t.tag == "[K]" and t.verbal in ("if","elif","while"):
        kw = p.consume().verbal
        return indent + f"{kw} {_parse_condition(p)}:"

    # else / try
    if t.tag == "[K]" and t.verbal in ("else","try"):
        return indent + p.consume().verbal + ":"

    # pass / break / continue
    if t.tag == "[K]" and t.verbal in ("pass","break","continue"):
        return indent + p.consume().verbal

    # return
    if t.tag == "[K]" and t.verbal == "return":
        p.consume()
        return indent + ("return" if p.at_end() else f"return {_parse_rhs(p)}")

    # import / from
    if t.tag == "[K]" and t.verbal in ("import","from"):
        kw = p.consume().verbal
        ws = []
        while not p.at_end(): ws.append(p.consume().verbal)
        return indent + f"{kw} {' '.join(ws)}"

    # print
    if t.tag == "[K]" and t.verbal == "print":
        p.consume()
        VALUE_B = {"variable","digit","string","call","object","list","tuple",
                   "set","ignore","f-string","list unpack","dictionary unpack"}
        args = []
        while not p.at_end():
            pt = p.peek()
            if pt.tag=="[B]" and pt.verbal in VALUE_B:
                py_v = p.parse_value()
                while p.peek() and p.peek().tag=="[O]":
                    op_t = p.consume()
                    py_v = f"{py_v} {OPERATOR_VERBAL.get(op_t.verbal, op_t.verbal)} {p.parse_value()}"
                args.append(py_v)
            elif pt.tag=="[K]" and pt.verbal in ("true","false","none","lambda"):
                args.append(p.parse_value())
            else: break
        return indent + f"print({', '.join(args)})"

    # assignment / compound / standalone
    lhs_parts = _collect_lhs(p)

    if not lhs_parts:
        return indent + _parse_rhs(p)

    t = p.peek()
    if not t or t.tag != "[O]":
        # standalone method call or bare expression
        base = ", ".join(lhs_parts) if len(lhs_parts)>1 else lhs_parts[0]
        if not p.at_end():
            # check for attribute/method chain on the base
            chain = p._chain(base) if base != lhs_parts[0] else base
            # peek for method/attribute
            chained = p._chain(lhs_parts[0])
            return indent + chained
        return indent + base

    op_verbal = p.consume().verbal
    op_sym    = OPERATOR_VERBAL.get(op_verbal, op_verbal)
    rhs       = _parse_rhs(p)
    lhs       = ", ".join(lhs_parts) if len(lhs_parts)>1 else lhs_parts[0]
    return indent + f"{lhs} {op_sym} {rhs}"

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def decode_kvi(kvi):
    kvi = kvi.strip()
    if not kvi: return "", ""
    toks = tokenise_kvi(kvi)
    ks   = "".join(t.tag for t in toks)
    py   = decode_line(kvi)
    return ks, py

def process_kvi(kvi):
    ks, py = decode_kvi(kvi)
    print(f"KS  : {ks}")
    print(f"PY  : {py}")

def process_file(path):
    src = Path(path)
    if not src.exists():
        print(f"Error: {path} not found"); return
    for i, line in enumerate(src.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"): continue
        print(f"\nLine {i:>3}: {line}")
        process_kvi(line)
    print()

def repl():
    print("Kencode KVI -> Python  (type 'quit' to exit)\n")
    while True:
        try:
            kvi = input("KVI> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if kvi.lower() in ("quit","exit","q"): break
        if kvi: process_kvi(kvi)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        repl()
    elif sys.argv[1] == "-f" and len(sys.argv) > 2:
        process_file(sys.argv[2])
    else:
        process_kvi(" ".join(sys.argv[1:]))


# ---------------------------------------------------------------------------
# CLI entry point (used by pip-installed console_scripts)
# ---------------------------------------------------------------------------

def main_cli():
    """Entry point for the `kencode-decode` command installed by pip."""
    if len(sys.argv) == 1:
        repl()
    elif sys.argv[1] == "-f" and len(sys.argv) > 2:
        process_file(sys.argv[2])
    else:
        process_kvi(" ".join(sys.argv[1:]))
