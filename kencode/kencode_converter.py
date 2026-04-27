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
kencode_converter.py  v2.0
===========================
Reads a Python source file and, for each line, produces:
  - KS  : Kencode Sequence   e.g. [W][O][B][W]
  - KVI : Kencode Verbal Instruction  e.g. x equals digit 10

Usage:
    python kencode_converter.py <python_file.py>

Outputs a CSV: <stem>_kencode.csv
"""

import re, sys, csv
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONTROL-FLOW KEYWORDS → [K]
# "is" is NOT here — only a standalone operator, not a name-part classifier
# ─────────────────────────────────────────────────────────────────────────────
CONTROL_KEYWORDS = {
    "if","elif","else","while","for","in","not","and","or",
    "with","as","return","import","from","class","def","try",
    "except","raise","pass","break","continue","lambda","yield",
    "global","nonlocal","del","assert",
    "True","False","None",
    "print",
}

OPERATOR_VERBAL = {
    "**=":"power equal","//=":"floor divided equal",
    "+=":"plus equal","-=":"minus equal","*=":"times equal",
    "/=":"divided equal","%=":"modulo equal",
    "**":"power","//":"floor divided by",
    "==":"is equal","!=":"not equal",
    "<=":"less or equal",">=":"greater or equal",
    "<":"less than",">":"greater than",
    "=":"equals","+":"plus","-":"minus","*":"times","/":"divided by","%":"modulo",
    "in":"in","not":"not","and":"and","or":"or","is":"is",
}

ALIGN_VERBAL = {"<":"left-align",">":"right-align","^":"center-align"}

NUM_WORDS = {
    "0":"zero","1":"one","2":"two","3":"three","4":"four",
    "5":"five","6":"six","7":"seven","8":"eight","9":"nine",
    "10":"ten","11":"eleven","12":"twelve","13":"thirteen","14":"fourteen",
    "15":"fifteen","16":"sixteen","17":"seventeen","18":"eighteen","19":"nineteen",
    "20":"twenty","30":"thirty","40":"forty","50":"fifty","60":"sixty",
    "70":"seventy","80":"eighty","90":"ninety","100":"hundred",
}

ESCAPE_VERBAL = {
    r'\\':  'backslash',
    r"\'":  'single quote',
    r'\"':  'double quote',
    r'\a':  'bell',
    r'\b':  'backspace',
    r'\f':  'form feed',
    r'\n':  'new line',
    r'\r':  'carriage return',
    r'\t':  'horizontal tab',
    r'\v':  'vertical tab',
}
_ESC_RE = r'(\\\\|\\\'|\\"|\\a|\\b|\\f|\\n|\\r|\\t|\\v|\\[0-7]{3}|\\x[0-9a-fA-F]{2}|\\u[0-9a-fA-F]{4})'

def _esc_verbal(esc):
    """Return list of verbal words for one escape sequence."""
    v = ESCAPE_VERBAL.get(esc)
    if v: return v.split()
    if re.match(r'\\[0-7]{3}', esc): return ['octal', esc[1:]]
    if re.match(r'\\x[0-9a-fA-F]{2}', esc, re.I): return ['hex', esc[2:]]
    if re.match(r'\\u[0-9a-fA-F]{4}', esc, re.I): return ['unicode', esc[2:]]
    return [esc]

def string_content_tokens(raw):
    """
    Convert the inside of a string literal into Token list.
    Rule:
      - First plain-word run  → [B]string  [W]w1 [W]w2 ...
      - Each escape sequence  → [B]special  [W]verbal_word(s)
      - Subsequent plain runs → bare [W]w tokens (no new [B]string)
    Words are split on both spaces and underscores.
    """
    parts = re.split(_ESC_RE, raw)
    toks, first_plain = [], True
    for part in parts:
        if not part:
            continue
        if re.fullmatch(_ESC_RE, part):
            toks.append(B('special'))
            for w in _esc_verbal(part):
                toks.append(W(w))
            first_plain = False
        else:
            # split on whitespace then underscores
            raw_words = part.split()
            words = []
            for rw in raw_words:
                words += split_snake(rw) if '_' in rw else [rw]
            if not words:
                continue
            if first_plain:
                toks.append(B('string'))
                first_plain = False
            for w in words:
                toks.append(W(w))
    return toks


def num_verbal(n):
    return NUM_WORDS.get(n.lstrip("0") or "0", n)

def split_camel(name):
    parts = re.findall(r'[A-Z][a-z]*|[a-z]+|[0-9]+', name)
    return [p.lower() for p in parts] if parts else [name.lower()]

def split_snake(name):
    return [p for p in name.split("_") if p]

def is_dunder(name):
    return name.startswith("__") and name.endswith("__")

def dunder_core(name):
    return name.strip("_")

# ─────────────────────────────────────────────────────────────────────────────
# Token
# ─────────────────────────────────────────────────────────────────────────────
class Token:
    def __init__(self, tag, verbal):
        self.tag = f"[{tag}]"
        self.verbal = verbal
    def __repr__(self):
        return f"Token({self.tag},{self.verbal!r})"

def K(v): return Token("K", v)
def O(v): return Token("O", v)
def W(v): return Token("W", v)
def B(v): return Token("B", v)

# ─────────────────────────────────────────────────────────────────────────────
# _split_args — split on top-level commas
# ─────────────────────────────────────────────────────────────────────────────
def _split_args(s):
    depth, cur, result, in_q, qc = 0, [], [], False, None
    for ch in s:
        if in_q:
            cur.append(ch)
            if ch == qc: in_q = False
        elif ch in ('"',"'"):
            in_q, qc = True, ch; cur.append(ch)
        elif ch in "([{": depth += 1; cur.append(ch)
        elif ch in ")]}": depth -= 1; cur.append(ch)
        elif ch == ',' and depth == 0:
            result.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    if cur: result.append("".join(cur))
    return result

# ─────────────────────────────────────────────────────────────────────────────
# lhs_tokens — LHS names are always [W], never [K]
# is_valid → [W]is [W]valid   (NOT [K]is)
# ─────────────────────────────────────────────────────────────────────────────
def lhs_tokens(name):
    """Always produce [W] tokens for LHS names. Bare '_' → [B]ignore."""
    if name.strip() == "_":
        return [B("ignore")]
    parts = split_snake(name)
    return [W(num_verbal(p) if p.isdigit() else p) for p in parts]

# ─────────────────────────────────────────────────────────────────────────────
# classify_value — classify a single value string → Token list
# ─────────────────────────────────────────────────────────────────────────────
def classify_value(val):
    val = val.strip()
    if not val: return []

    if val in ("True","False","None"):
        return [K(val.lower())]

    str_m = re.fullmatch(r'(["\'])(.*?)\1', val, re.DOTALL)
    if str_m:
        return string_content_tokens(str_m.group(2)) or [B("string"), W("")]

    fm = re.fullmatch(r'(-?)(\d+)\.(\d+)', val)
    if fm:
        sign, ip, dp = fm.groups()
        toks = [B("digit"), W(num_verbal(ip)), B("point"), W(dp)]
        return [O("minus")] + toks if sign else toks

    im = re.fullmatch(r'(-?)(\d+)', val)
    if im:
        sign, digits = im.groups()
        toks = [B("digit"), W(num_verbal(digits))]
        return [O("minus")] + toks if sign else toks

    if val == "_":
        return [B("ignore")]
    if val.startswith("lambda"):
        return parse_lambda_expr(val)

    # no-arg call: Dog()  Counter()
    noarg_m = re.fullmatch(r'([A-Za-z_][\w_]*)\(\)', val)
    if noarg_m:
        return [B("call")] + [W(p) for p in split_snake(noarg_m.group(1))]

    # obj.attr access: person.name
    if "." in val and re.fullmatch(r'[\w_]+(?:\.[\w_]+)+', val):
        return parse_attr_chain(val)

    # function call with args: len(x) / data_dict["names"] / nested calls
    if "(" in val or "[" in val:
        return classify_atom(val)

    # expression with operator: a*2  x+1  n-1
    if re.search(r'[\+\-\*/%]|==|!=|<=|>=', val):
        return parse_expression(val)

    parts = split_snake(val)
    toks = [B("variable")]
    for p in parts: toks.append(W(num_verbal(p) if p.isdigit() else p))
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# find_top_level_op — find first top-level occurrence of op pattern
# ─────────────────────────────────────────────────────────────────────────────
def _find_top_level_op(expr, op_pat):
    depth, in_q, qc = 0, False, None
    i = 0
    while i < len(expr):
        ch = expr[i]
        if in_q:
            if ch == qc: in_q = False
            i += 1; continue
        if ch in ('"',"'"):
            in_q, qc = True, ch; i += 1; continue
        if ch in "([{": depth += 1; i += 1; continue
        if ch in ")]}": depth -= 1; i += 1; continue
        if depth == 0:
            m = re.match(op_pat, expr[i:])
            if m: return i, m.end()
        i += 1
    return None, None

# ─────────────────────────────────────────────────────────────────────────────
# parse_expression — full expression tokeniser
# ─────────────────────────────────────────────────────────────────────────────
def parse_expression(expr):
    expr = expr.strip()
    if not expr: return []

    # Operator precedence (lowest first for left-to-right splitting)
    ops = [
        (r'\bor\b',              "or"),
        (r'\band\b',             "and"),
        (r'\bnot\b',             "not"),
        (r'==',                  "=="),
        (r'!=',                  "!="),
        (r'<=',                  "<="),
        (r'>=',                  ">="),
        (r'(?<![=!<>])<(?![=>])','<'),
        (r'(?<![=!<>])>(?![=>])','>' ),
        (r'\bin\b',              "in"),
        (r'(?<!\*)\+',           "+"),
        (r'(?<!\w)-(?!\d)',      "-"),
        (r'\*\*',                "**"),
        (r'(?<!\*)\*(?!\*)',     "*"),
        (r'//',                  "//"),
        (r'(?<!/)/(?!/)',        "/"),
        (r'%',                   "%"),
    ]
    for op_pat, op_str in ops:
        idx, op_len = _find_top_level_op(expr, op_pat)
        if idx is not None:
            left  = expr[:idx].strip()
            right = expr[idx+op_len:].strip()
            if left and right:
                return parse_expression(left) + \
                       [O(OPERATOR_VERBAL.get(op_str, op_str))] + \
                       parse_expression(right)

    return classify_atom(expr)


def _extract_call(expr):
    """
    If expr is a top-level function call like  list(filter(...))  or  obj.method(a,b),
    return (fname, args_raw). Otherwise return None.
    """
    m = re.match(r'([\w_.]+(?:\(\)\.[\w_]+)?)\(', expr)
    if not m: return None
    fname = m.group(1)
    start = m.end()
    depth, i = 1, start
    in_q, qc = False, None
    while i < len(expr) and depth > 0:
        ch = expr[i]
        if in_q:
            if ch == qc: in_q = False
        elif ch in ('"',"'"): in_q, qc = True, ch
        elif ch == '(': depth += 1
        elif ch == ')': depth -= 1
        i += 1
    if depth == 0 and i == len(expr):
        return fname, expr[start:i-1]
    return None

# ─────────────────────────────────────────────────────────────────────────────
# classify_atom — a single indivisible expression unit
# ─────────────────────────────────────────────────────────────────────────────
def classify_atom(expr):
    expr = expr.strip()
    if not expr: return []

    if expr in ("True","False","None"):
        return [K(expr.lower())]

    str_m = re.fullmatch(r'(["\'])(.*?)\1', expr, re.DOTALL)
    if str_m:
        return string_content_tokens(str_m.group(2)) or [B("string"), W("")]

    if re.fullmatch(r'-?\d+\.\d+', expr): return classify_value(expr)
    if re.fullmatch(r'-?\d+', expr):       return classify_value(expr)

    # Function call (possibly chained):  func(args)  obj.method(args)
    # Use balanced-paren extraction so nested calls work: list(filter(lambda x: ...))
    call_r = _extract_call(expr)
    if call_r:
        return parse_call_expr(call_r[0], call_r[1])

    # Subscript chain: name[i]  or  name[i][j]
    sub_m = re.fullmatch(r'(\w+)((?:\[[^\]]*\])+)', expr)
    if sub_m:
        return parse_subscript_chain(sub_m.group(1), sub_m.group(2))

    # Attribute chain
    if "." in expr:
        return parse_attr_chain(expr)

    # Keyword (single word)
    if expr in CONTROL_KEYWORDS:
        return [K(expr.lower())]

    # Multi-word keyword expression: "not False", "True and False"
    words = expr.split()
    if all(w in CONTROL_KEYWORDS for w in words):
        return [K(w.lower()) for w in words]

    # Variable
    parts = split_snake(expr)
    toks = [B("variable")]
    for p in parts: toks.append(W(num_verbal(p) if p.isdigit() else p))
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_attr_chain — obj.attr / obj.method() / obj.attr.method()
# ─────────────────────────────────────────────────────────────────────────────
def parse_attr_chain(expr):
    has_call = expr.endswith("()")
    bare = expr[:-2] if has_call else expr
    parts = bare.split(".")
    toks = []
    for i, part in enumerate(parts):
        sub = split_snake(part)
        if i == 0:
            toks.append(B("variable"))
            for s in sub: toks.append(W(s))
        else:
            is_last = (i == len(parts) - 1)
            bw = "method" if (is_last and has_call) else "attribute"
            toks.append(B(bw))
            for s in sub: toks.append(W(s))
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_call_expr — [B]call [W]... [B]pass args  (no pass if no args)
# ─────────────────────────────────────────────────────────────────────────────
def parse_call_expr(fname, args_raw):
    args_raw = args_raw.strip()

    # dunder: __init__(...)
    if is_dunder(fname):
        core = dunder_core(fname)
        toks = [B("call"), B("hook"), W(core)]
        if args_raw:
            toks.append(B("pass"))
            toks += parse_args_list(args_raw)
        return toks

    # super().__init__(name) — fname is "super().__init__"
    if "()." in fname:
        # e.g. super().__init__  → call super + hook init
        prefix, dunder_m = fname.split("().", 1)
        toks = [B("call")] + [W(p) for p in split_snake(prefix)]
        if is_dunder(dunder_m):
            toks += [B("hook"), W(dunder_core(dunder_m))]
        else:
            toks += [B("method")] + [W(p) for p in split_snake(dunder_m)]
        if args_raw:
            toks.append(B("pass"))
            toks += parse_args_list(args_raw)
        return toks

    # obj.method(args)
    if "." in fname:
        parts = fname.split(".")
        obj_parts = split_snake(parts[0])
        toks = [B("variable")]
        for p in obj_parts: toks.append(W(p))
        for mid in parts[1:-1]:
            toks.append(B("attribute"))
            for p in split_snake(mid): toks.append(W(p))
        last = parts[-1]
        toks.append(B("method"))
        for p in split_snake(last): toks.append(W(p))
        if args_raw:
            toks.append(B("pass"))
            toks += parse_args_list(args_raw)
        return toks

    # plain call
    name_parts = split_snake(fname)
    toks = [B("call")]
    for p in name_parts: toks.append(W(p))
    if args_raw:
        toks.append(B("pass"))
        toks += parse_args_list(args_raw)
    return toks

def parse_args_list(args_raw):
    """
    Parse comma-separated args into tokens.
    Rule for [B]pass between args:
    - Plain value args (digit/string/variable) do NOT get an inter-arg pass —
      they share the opening [B]pass emitted by parse_call_expr.
    - After a lambda or nested-call arg (which "closes" a complex expression),
      emit [B]pass before the next arg because the lambda consumed the pass context.
    """
    toks = []
    args = [a.strip() for a in _split_args(args_raw) if a.strip()]
    prev_was_complex = False   # True after lambda or nested call arg
    for i, arg in enumerate(args):
        if i > 0 and prev_was_complex:
            toks.append(B("pass"))
        if arg.startswith("lambda"):
            toks += parse_lambda_expr(arg)
            prev_was_complex = True
            continue
        # *args unpacking → [B]list [B]unpack [W]name
        # **kwargs unpacking → [B]dictionary [B]unpack [W]name
        if arg.startswith("**"):
            toks += [B("dictionary"), B("unpack")] + [W(p) for p in split_snake(arg[2:])]
            prev_was_complex = False
            continue
        if arg.startswith("*"):
            toks += [B("list"), B("unpack")] + [W(p) for p in split_snake(arg[1:])]
            prev_was_complex = False
            continue
        kw_m = re.fullmatch(r'(\w+)\s*=\s*(.+)', arg)
        if kw_m:
            name, val = kw_m.group(1), kw_m.group(2).strip()
            toks += [B("variable"), W(name), O("equals")] + classify_value(val)
            prev_was_complex = False
            continue
        toks += classify_value(arg)
        prev_was_complex = False
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_subscript_chain — name[0][1]  name['key']
# ─────────────────────────────────────────────────────────────────────────────
def parse_subscript_chain(name, brackets):
    name_parts = split_snake(name)
    toks = [B("variable")]
    for p in name_parts: toks.append(W(num_verbal(p) if p.isdigit() else p))
    for idx_s in re.findall(r'\[([^\]]*)\]', brackets):
        idx_s = idx_s.strip()
        if re.fullmatch(r'["\'].*["\']', idx_s):
            toks += [B("key"), B("string"), W(idx_s[1:-1])]
        elif re.fullmatch(r'-\d+', idx_s):
            toks += [B("index"), B("digit"), O("minus"), W(num_verbal(idx_s[1:]))]
        elif re.fullmatch(r'\d+', idx_s):
            toks += [B("index"), B("digit"), W(num_verbal(idx_s))]
        else:
            parts = split_snake(idx_s)
            toks += [B("index"), B("variable")] + [W(p) for p in parts]
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_collection_literal — [..] {..} (..) comprehensions
# ─────────────────────────────────────────────────────────────────────────────

def _split_comprehension(inner):
    """
    Given the inside of a {…} comprehension (braces already stripped),
    find the top-level 'for' keyword and split into:
      type='dict' → key, value, var, iter
      type='set'  → expr, var, iter
    Returns None if not a comprehension.
    """
    # find top-level 'for'
    depth, in_q, qc, i = 0, False, None, 0
    for_idx = None
    while i < len(inner):
        ch = inner[i]
        if in_q:
            if ch == qc: in_q = False
            i += 1; continue
        if ch in ('"',"'"): in_q, qc = True, ch; i += 1; continue
        if ch in "([{": depth += 1; i += 1; continue
        if ch in ")]}": depth -= 1; i += 1; continue
        if depth == 0:
            m = re.match(r'\bfor\b', inner[i:])
            if m:
                for_idx = i; break
        i += 1
    if for_idx is None:
        return None

    before_for = inner[:for_idx].strip()
    after_for  = inner[for_idx + 3:].strip()

    # split after_for on top-level 'in'
    depth, in_q, qc, i = 0, False, None, 0
    in_idx = None
    while i < len(after_for):
        ch = after_for[i]
        if in_q:
            if ch == qc: in_q = False
            i += 1; continue
        if ch in ('"',"'"): in_q, qc = True, ch; i += 1; continue
        if ch in "([{": depth += 1; i += 1; continue
        if ch in ")]}": depth -= 1; i += 1; continue
        if depth == 0:
            m = re.match(r'\bin\b', after_for[i:])
            if m:
                in_idx = i; break
        i += 1
    if in_idx is None:
        return None

    var_s  = after_for[:in_idx].strip()
    iter_s = after_for[in_idx + 2:].strip()

    # check if before_for has a top-level colon → dict comp
    depth, in_q, qc, i = 0, False, None, 0
    colon_idx = None
    while i < len(before_for):
        ch = before_for[i]
        if in_q:
            if ch == qc: in_q = False
            i += 1; continue
        if ch in ('"',"'"): in_q, qc = True, ch; i += 1; continue
        if ch in "([{": depth += 1; i += 1; continue
        if ch in ")]}": depth -= 1; i += 1; continue
        if depth == 0 and ch == ':':
            colon_idx = i; break
        i += 1

    if colon_idx is not None:
        key_s = before_for[:colon_idx].strip()
        val_s = before_for[colon_idx+1:].strip()
        return {'type': 'dict', 'key': key_s, 'value': val_s, 'var': var_s, 'iter': iter_s}
    else:
        return {'type': 'set', 'expr': before_for, 'var': var_s, 'iter': iter_s}


def _for_vars(var_s):
    """Emit tokens for loop variable(s). _ → [B]ignore, others → [B]variable [W]..."""
    toks = []
    for vp in _split_args(var_s):
        vp = vp.strip()
        if vp == "_":
            toks.append(B("ignore"))
        else:
            toks += [B("variable")] + [W(p) for p in split_snake(vp)]
    return toks

def parse_collection_literal(lit):
    lit = lit.strip()

    # list comprehension
    lc = re.fullmatch(r'\[(.+)\s+for\s+(.+?)\s+in\s+(.+)\]', lit)
    if lc:
        return [B("list")] + parse_expression(lc.group(1).strip()) + \
               [K("for")] + _for_vars(lc.group(2).strip()) + \
               [K("in")] + classify_atom(lc.group(3).strip())

    # dict/set comprehension — use smart splitter to handle nested dicts as values
    if lit.startswith("{") and lit.endswith("}"):
        comp = _split_comprehension(lit[1:-1])
        if comp and comp['type'] == 'dict':
            toks = [B("dict"), B("key")] + classify_value(comp['key'])
            toks += [B("value")] + parse_rhs(comp['value'])
            toks += [K("for")] + _for_vars(comp['var'])
            toks += [K("in")] + classify_atom(comp['iter'])
            return toks
        if comp and comp['type'] == 'set':
            toks = [B("set")] + parse_expression(comp['expr'])
            toks += [K("for")] + _for_vars(comp['var'])
            toks += [K("in")] + classify_atom(comp['iter'])
            return toks

    # list literal [1, 2, 3]
    if lit.startswith("[") and lit.endswith("]"):
        inner = lit[1:-1].strip()
        if not inner: return [B("list")]
        toks = [B("list")]
        for item in _split_args(inner):
            item = item.strip()
            nl = parse_collection_literal(item)
            toks += nl if nl is not None else classify_value(item)
        return toks

    # set literal {1,2,3} — no colon, no for
    if lit.startswith("{") and lit.endswith("}"):
        inner = lit[1:-1].strip()
        if ":" not in inner and "for" not in inner:
            if not inner: return [B("set")]
            toks = [B("set")]
            for item in _split_args(inner):
                toks += classify_value(item.strip())
            return toks

    # tuple literal (1,2,3)
    if lit.startswith("(") and lit.endswith(")"):
        inner = lit[1:-1].strip()
        if not inner: return [B("tuple")]
        toks = [B("tuple")]
        for item in _split_args(inner):
            toks += classify_value(item.strip())
        return toks

    return None

# ─────────────────────────────────────────────────────────────────────────────
# parse_lambda_expr
# ─────────────────────────────────────────────────────────────────────────────
def parse_lambda_expr(expr):
    m = re.match(r'^lambda\s+(.*?):\s*(.+)$', expr.strip())
    if not m:
        return [K("lambda")]
    params_raw, body = m.group(1).strip(), m.group(2).strip()
    toks = [K("lambda")]
    for p in _split_args(params_raw):
        p = p.strip()
        if p == "*":                toks.append(B("keyword-only"))
        elif p.startswith("**"):    toks += [B("dictionary"), W(p[2:])]
        elif p.startswith("*"):     toks += [B("tuple"), W(p[1:])]
        elif "=" in p:
            name, default = p.split("=", 1)
            toks += [B("variable"), W(name.strip()), O("equals")] + classify_value(default.strip())
        else:
            toks += [B("variable"), W(p)]
    toks.append(B("expression"))
    toks += parse_expression(body)
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_fstring_content
# ─────────────────────────────────────────────────────────────────────────────
def parse_fstring_content(content):
    toks = []
    for part in re.split(r'(\{[^}]+\})', content):
        if not part: continue
        if part.startswith('{') and part.endswith('}'):
            inner = part[1:-1].strip()
            fs = re.match(r'(.+?):([<>^])?(\d+)?(\.(\d+))?([fdse%])?$', inner)
            if fs:
                var_s, align, width, _, prec, _ = fs.groups()
                toks.append(B("formatting"))
                # self.name or obj.attr inside {}
                if "." in var_s.strip():
                    toks += parse_attr_chain(var_s.strip())
                else:
                    toks += classify_value(var_s.strip())
                if align: toks.append(B(ALIGN_VERBAL[align]))
                if width: toks += [B("digit"), W(num_verbal(width))]
                if prec:  toks += [B("precision"), B("point"), W(prec)]
            else:
                toks.append(B("formatting"))
                if "." in inner and not any(c in inner for c in "+-*/%"):
                    toks += parse_attr_chain(inner)
                else:
                    toks += parse_expression(inner)
        else:
            toks += string_content_tokens(part)
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_comment
# ─────────────────────────────────────────────────────────────────────────────
def parse_comment(line):
    m = re.match(r'^#(.*)', line)
    if not m: return None
    text = m.group(1).strip()
    return [B("comment")] + [W(w) for w in text.split()]

# ─────────────────────────────────────────────────────────────────────────────
# parse_indent_prefix
# ─────────────────────────────────────────────────────────────────────────────
def parse_indent_prefix(line):
    m = re.match(r'^((?:    |\t)+)(.*)', line)
    if not m: return [], line
    indent_str, rest = m.group(1), m.group(2)
    count = indent_str.count("    ") or indent_str.count("\t")
    return [W(str(count)), B("tab")], rest

# ─────────────────────────────────────────────────────────────────────────────
# parse_except
# ─────────────────────────────────────────────────────────────────────────────
def parse_except(line):
    if re.match(r'^except\s*:', line): return [K("except")]
    m = re.match(r'^except\s+([A-Z]\w+)\s*(?:as\s+(\w+))?:', line)
    if not m: return None
    exc_class, alias = m.group(1), m.group(2)
    toks = [K("except"), B("type")] + [W(w) for w in split_camel(exc_class)]
    if alias: toks += [K("as"), B("variable"), W(alias)]
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_with_open — 1 or 2 string args
# ─────────────────────────────────────────────────────────────────────────────
def parse_with_open(line):
    m = re.match(r'^with\s+open\((.+?)\)\s+as\s+(\w+):', line)
    if not m: return None
    args_raw, alias = m.group(1), m.group(2)
    toks = [K("with"), B("call"), W("open"), B("pass")]
    for arg in _split_args(args_raw):
        arg = arg.strip()
        sm = re.fullmatch(r'(["\'])(.*?)\1', arg)
        if sm:
            verbal = sm.group(2).replace(".", " dot ").replace("/", " slash ")
            toks.append(B("string"))
            for part in verbal.split(): toks.append(W(part))
        else:
            toks += classify_value(arg)
    toks += [K("as"), B("variable"), W(alias)]
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_def
# ─────────────────────────────────────────────────────────────────────────────
def parse_def(line):
    m = re.match(r'^def\s+([\w_]+)\s*\(([^)]*)\):', line)
    if not m: return None
    fname, params_raw = m.group(1), m.group(2).strip()
    if is_dunder(fname):
        toks = [K("def"), B("hook"), W(dunder_core(fname))]
    else:
        toks = [K("def")] + [W(p) for p in split_snake(fname)]
    if not params_raw: return toks
    toks.append(B("pass"))
    for param in _split_args(params_raw):
        param = param.strip()
        if not param:         continue
        if param == "*":      toks.append(B("keyword-only"))
        elif param == "self": toks += [B("variable"), W("self")]
        elif param.startswith("**"): toks += [B("dictionary"), W(param[2:])]
        elif param.startswith("*"):  toks += [B("tuple"), W(param[1:])]
        elif "=" in param:
            name, default = param.split("=", 1)
            toks += [B("variable"), W(name.strip()), O("equals")] + classify_value(default.strip())
        else:
            toks += [B("variable")] + [W(p) for p in split_snake(param)]
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_class
# ─────────────────────────────────────────────────────────────────────────────
def parse_class(line):
    m = re.match(r'^class\s+([\w_]+)\s*(?:\(([^)]*)\))?:', line)
    if not m: return None
    cname, parents = m.group(1), m.group(2)
    toks = [K("class")] + [W(p) for p in split_snake(cname)]
    if parents and parents.strip():
        toks.append(B("pass"))
        for par in _split_args(parents):
            toks += [B("variable"), W(par.strip())]
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_for
# ─────────────────────────────────────────────────────────────────────────────
def parse_for(line):
    m = re.match(r'^for\s+(.+?)\s+in\s+(.+?):', line)
    if not m: return None
    var_s, iter_s = m.group(1).strip(), m.group(2).strip()
    toks = [K("for")]
    for vp in _split_args(var_s):
        vp = vp.strip()
        if vp == "_":
            toks.append(B("ignore"))
        else:
            toks += [B("variable")] + [W(p) for p in split_snake(vp)]
    toks.append(K("in"))
    toks += classify_atom(iter_s)
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_return
# ─────────────────────────────────────────────────────────────────────────────
def parse_return(val_s):
    val_s = val_s.strip()
    toks = [K("return")]
    if not val_s: return toks
    # delegate to parse_rhs — handles dicts, collections, f-strings, ternary, expressions
    toks += parse_rhs(val_s)
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_print_stmt
# ─────────────────────────────────────────────────────────────────────────────
def parse_print_stmt(content):
    content = content.strip()
    toks = [K("print")]
    fs_m = re.match(r'^f(["\'])(.*?)\1$', content, re.DOTALL)
    if fs_m:
        toks.append(B("f-string"))
        toks += parse_fstring_content(fs_m.group(2))
        return toks
    args = _split_args(content)
    if len(args) > 1:
        for arg in args:
            toks += classify_value(arg.strip())
        return toks
    # use parse_expression so 'in','not','and','or' work correctly
    toks += parse_expression(content)
    return toks

# ─────────────────────────────────────────────────────────────────────────────
# parse_rhs
# ─────────────────────────────────────────────────────────────────────────────
def parse_rhs(rhs_s):
    rhs_s = rhs_s.strip()
    # lambda rhs
    if rhs_s.startswith("lambda"):
        return parse_lambda_expr(rhs_s)
    fs_m = re.match(r'^f(["\'])(.*?)\1$', rhs_s, re.DOTALL)
    if fs_m:
        return [B("f-string")] + parse_fstring_content(fs_m.group(2))
    # dict literal (has colons, no for)
    if rhs_s.startswith("{") and rhs_s.endswith("}"):
        inner = rhs_s[1:-1].strip()
        if ":" in inner and "for" not in inner:
            pairs = _split_args(inner)
            toks = []
            for pair in pairs:
                kv = re.match(r'\s*(.+?)\s*:\s*(.+)', pair.strip())
                if not kv: continue
                raw_k, raw_v = kv.group(1).strip(), kv.group(2).strip()
                toks.append(B("key")); toks += classify_value(raw_k)
                toks.append(B("value")); toks += classify_value(raw_v)
            return toks
    cl = parse_collection_literal(rhs_s)
    if cl is not None: return cl
    # ternary:  "Pass" if score >= 50 else "Fail"
    tern_m = re.match(r'^(.+?)\s+if\s+(.+?)\s+else\s+(.+)$', rhs_s)
    if tern_m:
        return classify_value(tern_m.group(1).strip()) + \
               [K("if")] + parse_expression(tern_m.group(2).strip()) + \
               [K("else")] + classify_value(tern_m.group(3).strip())
    return parse_expression(rhs_s)

# ─────────────────────────────────────────────────────────────────────────────
# parse_assignment_line
# ─────────────────────────────────────────────────────────────────────────────
def parse_assignment_line(line):
    line = line.strip()
    # compound:  x += 5  /  Counter.count += 1
    comp_m = re.match(r'^(.+?)\s*(\*\*=|//=|[+\-*/%]=)\s*(.+)$', line)
    if comp_m:
        lhs_s, op, rhs_s = comp_m.group(1).strip(), comp_m.group(2), comp_m.group(3).strip()
        if "." in lhs_s:
            lhs_toks = parse_attr_chain(lhs_s)
        elif "[" in lhs_s:
            sub_m = re.fullmatch(r'([\w_]+)((?:\[[^\]]*\])+)', lhs_s)
            lhs_toks = parse_subscript_chain(sub_m.group(1), sub_m.group(2)) if sub_m else lhs_tokens(lhs_s)
        else:
            lhs_toks = lhs_tokens(lhs_s)
        return lhs_toks + [O(OPERATOR_VERBAL.get(op, op))] + classify_value(rhs_s)

    eq_m = re.match(r'^(.+?)\s*=\s*(.+)$', line)
    if not eq_m: return None
    lhs_s, rhs_s = eq_m.group(1).strip(), eq_m.group(2).strip()

    # subscript LHS:  my_dict["c"] = 3
    sub_lhs = re.fullmatch(r'([\w_]+)((?:\[[^\]]*\])+)', lhs_s)
    if sub_lhs:
        toks = parse_subscript_chain(sub_lhs.group(1), sub_lhs.group(2))
        return toks + [O("equals")] + classify_value(rhs_s)

    # attr LHS:  self.name = x  /  Counter.count = ...
    attr_lhs = re.match(r'^([\w_]+)\.([\w_]+)$', lhs_s)
    if attr_lhs:
        obj_s, attr_s = attr_lhs.group(1), attr_lhs.group(2)
        toks = [B("variable")] + [W(p) for p in split_snake(obj_s)] + \
               [B("attribute")] + [W(p) for p in split_snake(attr_s)]
        return toks + [O("equals")] + classify_value(rhs_s)

    # multi-target:  div, mod = divmod(...)  /  num, _, last = (1, 2, 3)
    if "," in lhs_s:
        lhs_toks = []
        for vp in _split_args(lhs_s):
            vp = vp.strip()
            if vp == "_":
                lhs_toks.append(B("ignore"))
            else:
                lhs_toks += [B("variable")] + [W(p) for p in split_snake(vp)]
        return lhs_toks + [O("equals")] + parse_rhs(rhs_s)

    return lhs_tokens(lhs_s) + [O("equals")] + parse_rhs(rhs_s)

# ─────────────────────────────────────────────────────────────────────────────
# parse_standalone_call_line
# ─────────────────────────────────────────────────────────────────────────────
def parse_standalone_call_line(line):
    line = line.strip()
    # obj.method(args)  incl. super().__init__(name)
    m = re.fullmatch(r'([\w_]+(?:\(\))?\.[_\w]+(?:\.[_\w]+)*)\(([^)]*)\)', line)
    if m: return parse_call_expr(m.group(1), m.group(2))
    # plain func(args)
    m = re.fullmatch(r'([a-zA-Z_][\w_]*)\(([^)]*)\)', line)
    if m: return parse_call_expr(m.group(1), m.group(2))
    return None

# ─────────────────────────────────────────────────────────────────────────────
# Master dispatcher
# ─────────────────────────────────────────────────────────────────────────────
def parse_line(raw_line):
    stripped = raw_line.rstrip()
    if not stripped.strip(): return "", ""

    indent_toks, line = parse_indent_prefix(stripped)
    line = line.strip()
    tokens = None

    if tokens is None: tokens = parse_comment(line)
    if tokens is None: tokens = parse_except(line)
    if tokens is None: tokens = parse_with_open(line)

    if tokens is None:
        if   re.match(r'^else\s*:', line):   tokens = [K("else")]
        elif re.match(r'^try\s*:',  line):   tokens = [K("try")]
        elif line == "pass":                  tokens = [K("pass")]
        elif line == "break":                 tokens = [K("break")]
        elif line == "continue":              tokens = [K("continue")]

    if tokens is None:
        m = re.match(r'^(from|import)\s+(.+)', line)
        if m:
            kw, rest = m.group(1), m.group(2)
            toks = [K(kw)]
            for p in rest.split():
                toks.append(K("import") if p == "import" else W(p))
            tokens = toks

    if tokens is None: tokens = parse_def(line)
    if tokens is None: tokens = parse_class(line)
    if tokens is None: tokens = parse_for(line)

    if tokens is None:
        m = re.match(r'^(if|elif|while)\s+(.+?):\s*$', line)
        if m:
            tokens = [K(m.group(1))] + parse_expression(m.group(2).strip())

    if tokens is None:
        m = re.match(r'^return(.*)', line)
        if m: tokens = parse_return(m.group(1))

    if tokens is None:
        m = re.match(r'^print\((.+)\)$', line)
        if m: tokens = parse_print_stmt(m.group(1))
        elif line == "print()": tokens = [K("print")]

    if tokens is None: tokens = parse_assignment_line(line)
    if tokens is None: tokens = parse_standalone_call_line(line)

    if tokens is None:
        tokens = []
        for word in line.split():
            if word in CONTROL_KEYWORDS: tokens.append(K(word))
            elif re.match(r'^\d+$', word): tokens += [B("digit"), W(num_verbal(word))]
            else: tokens.append(W(word))

    all_tokens = indent_toks + tokens
    ks  = "".join(t.tag    for t in all_tokens)
    kvi = " ".join(t.verbal for t in all_tokens)
    return ks, kvi

# ─────────────────────────────────────────────────────────────────────────────
# File processing
# ─────────────────────────────────────────────────────────────────────────────
def process_file(path):
    src = Path(path)
    if not src.exists():
        print(f"Error: file not found: {path}"); sys.exit(1)
    lines = src.read_text(encoding="utf-8").splitlines()
    out_path = src.with_name(src.stem + "_kencode.csv")
    rows = []
    for i, raw_line in enumerate(lines, 1):
        ks, kvi = parse_line(raw_line)
        rows.append({"line_no":i,"python_code":raw_line.rstrip(),"KS":ks,"KVI":kvi})
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["line_no","python_code","KS","KVI"])
        writer.writeheader(); writer.writerows(rows)
    print(f"\n{'='*70}\n  Kencode output for: {src.name}\n{'='*70}")
    for row in rows:
        if not row["KS"]: continue
        print(f"\nLine {row['line_no']:>3}: {row['python_code']}")
        print(f"  KS : {row['KS']}")
        print(f"  KVI: {row['KVI']}")
    print(f"\n{'='*70}\n  CSV saved to: {out_path}\n{'='*70}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python kencode_converter.py <python_file.py>"); sys.exit(1)
    process_file(sys.argv[1])


# ---------------------------------------------------------------------------
# CLI entry point (used by pip-installed console_scripts)
# ---------------------------------------------------------------------------

def main_cli():
    """Entry point for the `kencode` command installed by pip."""
    process_file(sys.argv[1] if len(sys.argv) > 1 else (
        print("Usage: kencode <python_file.py>") or sys.exit(1)))
