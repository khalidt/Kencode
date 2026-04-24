# Kencode Approach: Accessible Programming Through Natural Language

> **Try it online:** [Kencode page](https://khalidalkhaldi.pythonanywhere.com/).

---

## Table of Contents

1. [What is Kencode?](#what-is-kencode)
2. [Why Kencode?](#why-kencode)
3. [How It Works, The Core Idea](#how-it-works)
4. [Kencode classification](#kencode-classification-four-token-types)
5. [Base-Word Reference Table](#base-word-reference-table)
6. [Operator Reference Table](#operator-reference-table)
7. [Escape Sequence Reference](#escape-sequence-reference)
8. [The Kencode Sequence (KS)   General Rule](#the-kencode-sequence-general-rule)
9. [Reading a Kencode Instruction](#reading-a-kencode-instruction)
10. [Complete Examples by Category](#complete-examples-by-category)
11. [For Non-Technical Users](#for-non-technical-users)
12. [For Technical Users](#for-technical-users)
13. [The Converter Tool](#the-converter-tool)
14. [Advantages of Kencode](#advantages-of-kencode)
15. [License](#license)
16. [Citation and Reference](#citation-and-reference)

---

## What is Kencode?

**Kencode** is a bidirectional mapping method between Python programming code and natural spoken/written language instructions. It was designed to make programming accessible to people who face difficulties with the punctuation and special characters that conventional programming requires, such as people using voice input, alternative keyboards, or those learning to code for the first time.

With Kencode, instead of typing:

```python
student = 'James'
```

You write or speak:

```
student equals string James
```

And instead of:

```python
for i in range(5):
```

You write or speak:

```
for variable i in call range pass digit five
```

Kencode is **fully bidirectional**: you can convert Python → Kencode, or Kencode → Python.

---

## Why Kencode?

Programming languages rely heavily on punctuation `()`, `[]`, `{}`, `'`, `"`, `#`, `:`, `=`, `+=`, and special characters that are difficult for many people to type or dictate. This creates a significant barrier:

- People using **voice-to-text** input struggle with special characters
- People with **motor disabilities** find special-character keyboard shortcuts difficult
- **Beginner programmers** often confuse punctuation rules and syntax symbols
- People using **alternative input devices** may not have easy access to symbol keys
- **Non-native speakers** learning programming face both language and syntax barriers simultaneously

Kencode solves this by providing a clean, word-based alternative that maps one-to-one with real Python code; no information is lost, and any valid Kencode instruction can be converted back to exactly the Python it represents.

---

## How It Works

Kencode works by breaking every Python statement into a sequence of classified tokens. Each token falls into one of four categories, and the sequence of categories is called the **Kencode Sequence (KS)**. Alongside the KS, each token also has a verbal form, a plain English word or phrase, which together form the **Kencode Verbal Instruction (KVI)**.

```
Python:   x = 10
KS:       [W] [O] [B] [W]
KVI:      x   equals digit ten
```

The KS tells you *what kind* of thing each token is. The KVI tells you *what it says*. Together, they give a complete, unambiguous description of the Python code in natural language.

---

## Kencode classification (Four Token Types)

Every token in a programming statement is classified by Kencode into four types. As a result, every token in the Kencode instruction is one of exactly four types:

| Symbol | Name | Meaning | Examples |
|--------|------|---------|---------|
| `[K]` | **Keyword** | A Python reserved word that controls program flow or structure | `if`, `for`, `while`, `def`, `class`, `return`, `True`, `False`, `print` |
| `[O]` | **Operator** | A mathematical, logical, or assignment operation | `=`, `+`, `-`, `*`, `/`, `==`, `>=`, `and`, `or` |
| `[W]` | **Word** | A user-defined name, variable, number verbal, or string content | `student`, `ten`, `Alice`, `my`, `list` |
| `[B]` | **Base-word** | A Kencode structural word that classifies or bridges tokens | `variable`, `digit`, `string`, `call`, `pass`, `list`, `key`, `value` |

### Key Rules

- `[K]` tokens come from Python's built-in reserved words. They appear in the KVI exactly as they are in Python (lowercased).
- `[O]` tokens are translated to their verbal equivalents: `==` becomes `is equal`, `>=` becomes `greater or equal`, `**` becomes `power`.
- `[W]` tokens are plain words, variable names (split on underscores), string content, or verbalized numbers.
- `[B]` tokens are the *glue* of Kencode. They are added (they don't exist in Python) to indicate the type of value or structure that follows.

**note** Programming statements provide [K], [O], and [W]. so we need to add only [B] to construct valid Kencode instruction.
---

## Base-Word Reference Table

Base-words `[B]` are the heart of Kencode. They are structural words added to make the meaning of each token clear without punctuation.

| Base-Word | KS Tag | Associated Type | Description |
|-----------|--------|-----------------|-------------|
| `variable` | `[B]` | Data / names | A named reference to a stored value |
| `digit` | `[B]` | Numbers | A numeric literal (integer or float) |
| `point` | `[B]` | Numbers | The decimal point in a float (e.g. `3.5` → `digit three point 5`) |
| `string` | `[B]` | Text | An immutable sequence of characters |
| `special` | `[B]` | Escape sequences | Introduces an escape character within a string |
| `list` | `[B]` | Collections | An ordered, mutable collection `[...]` |
| `tuple` | `[B]` | Collections | An ordered, immutable collection `(...)` |
| `set` | `[B]` | Collections | An unordered, unique-value collection `{...}` |
| `dict` | `[B]` | Collections | A dictionary comprehension marker |
| `key` | `[B]` | Dictionaries | The key in a key-value pair or subscript `["key"]` |
| `value` | `[B]` | Dictionaries | The value in a key-value pair |
| `index` | `[B]` | Lists / strings | A positional subscript `[0]`, `[-1]` |
| `call` | `[B]` | Functions | Marks the start of a function call |
| `pass` | `[B]` | Functions | Marks the start of arguments passed to a call |
| `object` | `[B]` | OOP | An object being accessed via dot notation |
| `attribute` | `[B]` | OOP | A property accessed with a dot (non-callable) |
| `method` | `[B]` | OOP | A callable property accessed with a dot |
| `hook` | `[B]` | OOP | A dunder (double-underscore) method like `__init__` |
| `tab` | `[B]` | Structure | Represents one indentation level (preceded by a count `[W]`) |
| `comment` | `[B]` | Structure | Marks a comment line (replaces `#`) |
| `f-string` | `[B]` | Formatting | An f-string literal `f"..."` |
| `formatting` | `[B]` | Formatting | A `{...}` expression inside an f-string |
| `precision` | `[B]` | Formatting | A `.Nf` format specifier |
| `left-align` | `[B]` | Formatting | The `:<N` alignment specifier |
| `right-align` | `[B]` | Formatting | The `:>N` alignment specifier |
| `center-align` | `[B]` | Formatting | The `:^N` alignment specifier |
| `expression` | `[B]` | Lambda | Marks the body of a lambda expression |
| `type` | `[B]` | Exceptions | Introduces an exception class name |
| `ignore` | `[B]` | Placeholder | Represents `_` (the throwaway variable) |
| `keyword-only` | `[B]` | Functions | The `*` separator in function parameters |
| `dictionary` | `[B]` | Functions | A `**kwargs`-style parameter or argument |
| `list unpack` | `[B][B]` | Functions | A `*args` unpacking in a function call |
| `dictionary unpack` | `[B][B]` | Functions | A `**kwargs` unpacking in a function call |

---

## Operator Reference Table

All Python operators are classified as `[O]` and translated to verbal English:

| Python Symbol | KVI Verbal | Category |
|--------------|------------|----------|
| `=` | `equals` | Assignment |
| `+=` | `plus equal` | Compound assignment |
| `-=` | `minus equal` | Compound assignment |
| `*=` | `times equal` | Compound assignment |
| `/=` | `divided equal` | Compound assignment |
| `%=` | `modulo equal` | Compound assignment |
| `**=` | `power equal` | Compound assignment |
| `//=` | `floor divided equal` | Compound assignment |
| `+` | `plus` | Arithmetic |
| `-` | `minus` | Arithmetic |
| `*` | `times` | Arithmetic |
| `/` | `divided by` | Arithmetic |
| `//` | `floor divided by` | Arithmetic |
| `%` | `modulo` | Arithmetic |
| `**` | `power` | Arithmetic |
| `==` | `is equal` | Comparison |
| `!=` | `not equal` | Comparison |
| `<` | `less than` | Comparison |
| `>` | `greater than` | Comparison |
| `<=` | `less or equal` | Comparison |
| `>=` | `greater or equal` | Comparison |
| `in` | `in` | Membership |
| `not` | `not` | Logical |
| `and` | `and` | Logical |
| `or` | `or` | Logical |
| `is` | `is` | Identity |

---

## Escape Sequence Reference

When a string contains special characters, Kencode uses the `[B]special` base-word followed by the verbal description of the escape:

| Escape | KVI Verbal | Meaning |
|--------|-----------|---------|
| `\n` | `new line` | Newline character |
| `\t` | `horizontal tab` | Horizontal tab |
| `\\` | `backslash` | Literal backslash |
| `\'` | `single quote` | Literal single quote |
| `\"` | `double quote` | Literal double quote |
| `\r` | `carriage return` | Carriage return |
| `\b` | `backspace` | Backspace |
| `\f` | `form feed` | Form feed |
| `\a` | `bell` | Bell / alert |
| `\v` | `vertical tab` | Vertical tab |
| `\ooo` | `octal ooo` | Octal value |
| `\xhh` | `hex hh` | Hexadecimal value |
| `\uXXXX` | `unicode XXXX` | Unicode code point |

### Example

```python
lines = ["line one\n", "line two\n"]
```

```
KS:  [W][O][B][B][W][W][B][W][W][B][W][W][B][W][W]
KVI: lines equals list string line one special new line string line two special new line
```

---

## The Kencode Sequence General Rule

The Kencode Sequence (KS) is the backbone of the system. It captures the *structural pattern* of a Python statement using only the four token symbols. This is the **single general regex rule** that validates any KS:


$$
^{(?:\d+\s+)?(?:\[(?:K|O|W|B)\]\s)*(?:\[(?:W|K)\])$}
$$


**Breakdown:**

| Part | Meaning |
|------|---------|
| `^` | Start of the sequence |
| `(?:\d+\s+)?` | Optional indent prefix, a digit followed by a space (e.g. `1 ` for one indent level) |
| `(\[(?:K\|O\|W\|B)\])+` | One or more tags, each exactly `[K]`, `[O]`, `[W]`, or `[B]` |
| `$` | End of the sequence |

This rule enforces that:
- Only the four valid tag letters are used
- Tags are always bracket-enclosed
- Indentation is expressed as a plain count, not as blank space
- Any combination and any length is valid, the grammar is open

---

## Reading a Kencode Instruction

A Kencode instruction reads left to right. Base-words `[B]` act as **type classifiers**, they always appear immediately before the token they describe:

```
[W]my [W]list [O]equals [B]list [B]digit [W]one [B]digit [W]two [B]digit [W]three
```

Which corresponds to:

```python
my_list = [1, 2, 3]
```

### Structural patterns to recognise

| Pattern | Meaning | Python example |
|---------|---------|---------------|
| `[W][O][B][W]` | Simple assignment | `x = 10` |
| `[W][O][B][W][B][W]` | Float assignment | `y = 3.5` |
| `[W][O][B][W]` | String assignment | `name = "Alice"` |
| `[K][B][W][K][B][W][B][B][W]` | For loop with call | `for i in range(5):` |
| `[B][W][B][B][args...]` | Function call | `greet("Alice")` |
| `[W][B][W]` | Method call (no args) | `my_list.sort()` |
| `[W][B][W][B][B][W]` | Method call (with args) | `my_list.append(4)` |
| `[K][B][W][B][B][W][B][W]` | def with parameters | `def greet(self):` |
| `[W][B][K][B][W][B][B][W][B][W]` | `__init__` with indent | `    def __init__(self, name):` |

---

## Complete Examples by Category

### Variables and Data Types

| Python | KS | KVI |
|--------|----|-----|
| `x = 10` | `[W][O][B][W]` | `x equals digit ten` |
| `y = 3.5` | `[W][O][B][W][B][W]` | `y equals digit three point 5` |
| `name = "Alice"` | `[W][O][B][W]` | `name equals string Alice` |
| `is_valid = True` | `[W][W][O][K]` | `is valid equals true` |
| `my_list = [1, 2, 3]` | `[W][W][O][B][B][W][B][W][B][W]` | `my list equals list digit one digit two digit three` |
| `my_tuple = (1, 2, 3)` | `[W][W][O][B][B][W][B][W][B][W]` | `my tuple equals tuple digit one digit two digit three` |
| `my_set = {1, 2, 3}` | `[W][W][O][B][B][W][B][W][B][W]` | `my set equals set digit one digit two digit three` |

### Operators and Expressions

| Python | KS | KVI |
|--------|----|-----|
| `print(x + y)` | `[K][B][W][O][B][W]` | `print variable x plus variable y` |
| `print(a ** b)` | `[K][B][W][O][B][W]` | `print variable a power variable b` |
| `x += 5` | `[W][O][B][W]` | `x plus equal digit five` |
| `result = "Pass" if score >= 50 else "Fail"` | `[W][O][B][W][K][B][W][O][B][W][K][B][W]` | `result equals string Pass if variable score greater or equal digit fifty else string Fail` |

### Control Flow

| Python | KS | KVI |
|--------|----|-----|
| `if result:` | `[K][B][W]` | `if variable result` |
| `if True:` | `[K][K]` | `if true` |
| `if num == 0:` | `[K][B][W][O][B][W]` | `if variable num is equal digit zero` |
| `elif num > 0:` | `[K][B][W][O][B][W]` | `elif variable num greater than digit zero` |
| `else:` | `[K]` | `else` |
| `while count < 5:` | `[K][B][W][O][B][W]` | `while variable count less than digit five` |
| `for i in range(5):` | `[K][B][W][K][B][W][B][B][W]` | `for variable i in call range pass digit five` |
| `for i in range(1, 10, 2):` | `[K][B][W][K][B][W][B][B][W][B][W][B][W]` | `for variable i in call range pass digit one digit ten digit two` |
| `for _ in range(3):` | `[K][B][K][B][W][B][B][W]` | `for ignore in call range pass digit three` |
| `for key, value in my_dict.items():` | `[K][B][W][B][W][K][B][W][W][B][W]` | `for variable key variable value in variable my dict method items` |

### Functions

| Python | KS | KVI |
|--------|----|-----|
| `def greet():` | `[K][W]` | `def greet` |
| `def add(a, b):` | `[K][W][B][B][W][B][W]` | `def add pass variable a variable b` |
| `def power(base, exp=2):` | `[K][W][B][B][W][B][W][O][B][W]` | `def power pass variable base variable exp equals digit two` |
| `def variable_args(*args):` | `[K][W][W][B][B][W]` | `def variable args pass tuple args` |
| `def keyword_args(**kwargs):` | `[K][W][W][B][B][W]` | `def keyword args pass dictionary kwargs` |
| `greet()` | `[B][W]` | `call greet` |
| `int(num_str)` | `[B][W][B][B][W][W]` | `call int pass variable num str` |
| `result = f(*args)` | `[W][O][B][W][B][B][B][W]` | `result equals call f pass list unpack args` |
| `result = f(**kwargs)` | `[W][O][B][W][B][B][B][W]` | `result equals call f pass dictionary unpack kwargs` |

### Classes and Objects

| Python | KS | KVI |
|--------|----|-----|
| `class Person:` | `[K][W]` | `class Person` |
| `class Dog(Animal):` | `[K][W][B][B][W]` | `class Dog pass variable Animal` |
| `    def __init__(self, name):` | `[W][B][K][B][W][B][B][W][B][W]` | `1 tab def hook init pass variable self variable name` |
| `    def greet(self):` | `[W][B][K][W][B][B][W]` | `1 tab def greet pass variable self` |
| `self.name = name` | `[B][W][B][W][O][B][W]` | `variable self attribute name equals variable name` |
| `name = person.name` | `[W][O][B][W][B][W]` | `name equals variable person attribute name` |
| `cat.make_sound()` | `[W][B][W][W]` | `cat method make sound` |
| `super().__init__(name)` | `[W][B][B][W][B][W][B][B][W]` | `2 tab call super hook init pass variable name` |

### Dictionaries

| Python | KS | KVI |
|--------|----|-----|
| `customer = {'name': 'Alice', 'age': 30}` | `[W][O][B][B][W][B][B][W][B][B][W][B][B][W]` | `customer equals key string name value string Alice key string age value digit thirty` |
| `my_dict["c"] = 3` | `[B][W][W][B][B][W][O][B][W]` | `variable my dict key string c equals digit three` |
| `customer['age']` | `[W][B][B][W]` | `customer key string age` |

### F-strings and Formatting

| Python | KS | KVI |
|--------|----|-----|
| `message = f"My name is {name}"` | `[W][O][B][B][W][W][W][B][B][W]` | `message equals f-string string My name is formatting variable name` |
| `return f"Hello {self.name}"` | `[K][B][B][W][B][B][W][B][W]` | `return f-string string Hello formatting variable self attribute name` |
| `f"{price:.2f}"` | `[B][B][W][B][B][W][W]` | `formatting variable price precision point 2` |
| `f"{'hi':<10}"` | `[B][B][B][W][B][B][W]` | `formatting string hi left-align digit ten` |

### Indentation

Indentation is represented by a number (count of 4-space units) followed by the base-word `tab`:

| Python | KS | KVI |
|--------|----|-----|
| `    x = 10` (1 indent) | `[W][B][W][O][B][W]` | `1 tab x equals digit ten` |
| `        print(x)` (2 indents) | `[W][B][K][B][W]` | `2 tab print variable x` |

### Exception Handling

| Python | KS | KVI |
|--------|----|-----|
| `try:` | `[K]` | `try` |
| `except ZeroDivisionError:` | `[K][B][W][W][W]` | `except type zero division error` |
| `except ValueError as e:` | `[K][B][W][W][K][B][W]` | `except type value error as variable e` |

### File Operations

| Python | KS | KVI |
|--------|----|-----|
| `with open("test.txt", "w") as f:` | `[K][B][W][B][B][W][W][W][B][W][K][B][W]` | `with call open pass string test dot txt string w as variable f` |

### Lambda and Higher-Order Functions

| Python | KS | KVI |
|--------|----|-----|
| `square = lambda x: x**2` | `[W][O][K][B][W][B][B][W][O][B][W]` | `square equals lambda variable x expression variable x power digit two` |
| `even_numbers = list(filter(lambda x: x % 2 == 0, numbers))` | `[W][W][O][B][B][B][B][W][B][K][B][W][B][B][W][O][B][W][O][B][W][B][B][W]` | `even numbers equals call list pass call filter pass lambda variable x expression variable x modulo digit two is equal digit zero pass variable numbers` |

### Comprehensions

| Python | KS | KVI |
|--------|----|-----|
| `[x * 2 for x in range(5)]` | `[B][B][W][O][B][W][K][B][W][K][B][W][B][B][W]` | `list variable x times digit two for variable x in call range pass digit five` |
| `{x for x in range(5)}` | `[B][B][W][K][B][W][K][B][W][B][B][W]` | `set variable x for variable x in call range pass digit five` |
| `[Person(n, a) for n, a in zip(names, ages)]` | `[B][B][W][B][B][W][B][W][K][B][W][B][W][K][B][W][B][B][W][B][W]` | `list call Person pass variable n variable a for variable n variable a in call zip pass variable names variable ages` |

### Multi-Target Assignment and Ignore

| Python | KS | KVI |
|--------|----|-----|
| `num, _, last = (1, 2, 3)` | `[B][W][B][B][W][O][B][B][W][B][W][B][W]` | `variable num ignore variable last equals tuple digit one digit two digit three` |
| `for _ in range(3):` | `[K][B][K][B][W][B][B][W]` | `for ignore in call range pass digit three` |

---

## For Non-Technical Users

If you have never programmed before, here is a plain English explanation of how Kencode works.

### Think of it like giving instructions in plain English

When a programmer writes `x = 10`, they are telling the computer "create a storage box called x and put the number 10 in it." In Kencode, you would say exactly that kind of thing, but in a structured way: `x equals digit ten`.

### The four building blocks

Every Kencode instruction is built from four kinds of words:

1. **Keywords**: These are Python's own words, like `if`, `for`, `while`, `print`, `True`, `False`. They do exactly what they sound like.

2. **Operators**: These are words for mathematical and logical actions: `equals`, `plus`, `minus`, `times`, `divided by`, `is equal`, `greater than`, and so on.

3. **Words**: These are *your* words, the names you choose for variables, or the content of text, or verbalized numbers like `ten`, `Alice`, `my list`.

4. **Base-words**: These are special helper words added by Kencode to make the meaning clear. They tell you *what type* the next word is. For example, `digit` before a number tells you it is a number; `string` before words tells you they are text; `variable` tells you it is a stored value; `call` tells you a function is being run.

### A simple example step by step

Python code: `name = "Alice"`

In Kencode you say: **name equals string Alice**

- `name` → a **Word** [W], this is the name you are choosing for your storage box
- `equals` → an **Operator** [O], you are storing something into it
- `string` → a **Base-word** [B], what follows is text (not a number, not a box name)
- `Alice` → a **Word** [W], the actual text content

Reading it back: *"The box called 'name' gets the text value 'Alice'."*

### You can use Kencode to speak programs out loud

Because Kencode replaces all punctuation with words, you can read any Kencode instruction aloud as a normal English sentence. This makes it usable with:
- Voice dictation software
- Screen readers
- Assisted communication devices
- Any situation where typing symbols is difficult

---

## For Technical Users

### Token classification rules

**LHS vs RHS distinction:** Left-hand side names (variable names being assigned to) always emit plain `[W]` tokens, they are never prefixed with `[B]variable`. The `[B]variable` prefix is used only on the *right-hand side* or inside expressions, where a name appears as a value being read, not written.

```python
x = y        # x → [W]  (LHS, no prefix)
             # y → [B]variable [W]y  (RHS, typed)
```

**Snake_case splitting:** Variable names with underscores are split into separate `[W]` tokens:
```
my_list → [W]my [W]list
is_valid = True → [W]is [W]valid [O]equals [K]true
```
Note: `is` in `is_valid` is `[W]` (a name part), not `[K]` (a keyword), because it is part of a variable name.

**Number verbalization:** Numbers up to 100 are verbalized; larger numbers pass through as digits:
```
10  → digit ten
50  → digit fifty
993 → digit 993
```

**Multi-word operators:** Some operators translate to multi-word KVI phrases, which produce one `[O]` token but multiple words in the KVI:

| Python | KS tag | KVI phrase |
|--------|--------|-----------|
| `==` | `[O]` | `is equal` (2 words) |
| `/=` | `[O]` | `divided equal` (2 words) |
| `>=` | `[O]` | `greater or equal` (3 words) |
| `//` | `[O]` | `floor divided by` (3 words) |

This means the count of `[K/O/W/B]` tags in the KS will be less than or equal to the word count in the KVI. The KS tag count is the authoritative measure.

**Function call argument passing:** The `[B]pass` base-word separates a function name from its arguments. For calls with multiple arguments, plain value arguments share the opening `pass`; a fresh `[B]pass` is emitted only after a lambda argument (which consumes the pass context):

```python
filter(lambda x: x > 0, numbers)
→ call filter pass lambda variable x expression variable x greater than digit zero pass variable numbers
```

**Inter-argument `pass` rule:**
- Plain typed args (digit, string, variable) → no inter-arg pass, they share the opening one
- After a lambda arg → emit `[B]pass` before the next arg

### Handling ambiguity

The following words have context-sensitive classification:

| Word | As `[K]` | As `[W]` |
|------|----------|----------|
| `is` | Standalone operator between two values | Part of a variable name (`is_valid`) |
| `list` | Collection base-word in RHS context | Part of a variable name (`my_list`) on LHS |
| `True`/`False`/`None` | Always `[K]` Python keywords | Never `[W]` |
| `print` | Always `[K]` in Kencode | Never `[W]` |

---

## The Converter Tool

The project includes two Python files:

### `kencode_converter.py` — Python → Kencode

Reads a `.py` source file and converts it to KS and KVI for every line.

```bash
python kencode_converter.py my_script.py
```

Output:
- Terminal display showing KS and KVI for each line
- A CSV file `my_script_kencode.csv` with columns: `line_no`, `python_code`, `KS`, `KVI`

### `kencode_decoder.py` — KVI → Python + KS

Takes a KVI instruction (spoken/typed in natural language) and reconstructs the Python code and KS.

```bash
# Interactive REPL
python kencode_decoder.py

# Single instruction
python kencode_decoder.py "even numbers equals call list pass call filter pass lambda variable x expression variable x modulo digit two is equal digit zero pass variable numbers"

# Batch file
python kencode_decoder.py -f my_instructions.txt
```

Output for each KVI:
```
KS  : [W][W][O][B][B][B][B][W][B][K][B][W][B][B][W][O][B][W][O][B][W][B][B][W]
PY  : even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
```


## Advantages of Kencode

### Accessibility
- Removes all special characters and punctuation from programming, no `()`, `{}`, `[]`, `'`, `"`, `#`, or `:` required
- Fully compatible with voice dictation and text-to-speech systems
- Usable with alternative input devices and assisted communication technology
- Reduces cognitive load for learners by separating *what* a token is from *what it means*

### Clarity and Learnability
- Every statement becomes a readable English sentence
- The `[B]` base-word system makes data types and structure explicit, no guessing whether something is a number, text, or variable
- Beginners can reason about code structure without knowing syntax rules
- KS patterns provide a visual grammar, learners can see structural patterns before mastering syntax

### Completeness
- Full coverage of Python: variables, operators, control flow, functions, classes, OOP, dictionaries, collections, comprehensions, lambdas, f-strings, exception handling, file I/O, imports, and more
- Bidirectional, any valid Kencode instruction converts back to the exact Python it represents
- No information is lost in either direction

### Flexibility
- Works as a standalone command-line tool, a web API, or an importable library
- The KS regex rule is language-agnostic, the same four-token system could extend to other programming languages
- Escape sequences, format specifiers, decorators, and advanced Python constructs are all covered

---

## Quick Reference Card

```
[K] Keyword    → if elif else while for in with as return def class
                  try except raise import from lambda True False None print

[O] Operator   → equals  plus  minus  times  divided by  modulo  power
                  is equal  not equal  less than  greater than
                  less or equal  greater or equal  plus equal  ...

[W] Word       → any variable name (snake parts)
                  verbalized numbers: one two three ... ten twenty fifty
                  string content words

[B] Base-word  → variable  digit  point  string  special
                  call  pass  object  attribute  method  hook
                  list  tuple  set  dict  key  value  index
                  f-string  formatting  precision  left-align  right-align  center-align
                  expression  type  ignore  tab  comment  keyword-only  dictionary
                  list unpack  dictionary unpack

GENERAL RULE (regex):  ^(?:\d+\s+)?(?:\[(?:K|O|W|B)\]\s)*(?:\[(?:W|K)\])$     
```

---

*Kencode was created to make programming accessible to everyone, regardless of physical ability, keyboard layout, or programming experience. If a computer can understand it, so should you.*

---

## License
<p align="center">
  <a href="https://github.com/khalidt/Kencode"><strong>Kencode</strong></a> © 2025 by 
  <a href="https://github.com/khalidt/Kencode">Khalid Alkhaldi</a>  
  is licensed under  
  <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>
</p>

<p align="center">
  <img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg" width="20">
  <img src="https://mirrors.creativecommons.org/presskit/icons/by.svg" width="20">
  <img src="https://mirrors.creativecommons.org/presskit/icons/nc.svg" width="20">
  <img src="https://mirrors.creativecommons.org/presskit/icons/sa.svg" width="20">
</p>

---
## Citation and Reference

Kencode is introduced and formally described in the following research paper. If you use Kencode in your research, teaching, software, or any published work, please cite the original paper using one of the formats below.

---

### Original Research Paper

> **Alkhaldi, K., Qassem, A., & Ludi, S. (2025).** Kencode: Advancing Voice-Based Programming Through an Innovative, Standardized, and Taxonomic Structuring Approach. *Journal of Visual Language and Computing*, 8–17. https://doi.org/10.18293/JVLC2025-N3-079

📄 **Full paper (open access):** [http://ksiresearch.org/jvlc/journal/JVLC2025N3/JVLC079.pdf](http://ksiresearch.org/jvlc/journal/JVLC2025N3/JVLC079.pdf)

---

### BibTeX

```bibtex
@article{Alkhaldi2025Kencode,
  author  = {Khalid Alkhaldi and Asrar Qassem and Stephanie Ludi},
  title   = {Kencode: Advancing Voice-Based Programming Through an Innovative,
             Standardized, and Taxonomic Structuring Approach},
  journal = {Journal of Visual Language and Computing},
  year    = {2025},
  pages   = {8--17},
  doi     = {10.18293/JVLC2025-N3-079},
  url     = {http://ksiresearch.org/jvlc/journal/JVLC2025N3/JVLC079.pdf}
}
```


### Acknowledgment Template

If Kencode contributed to your work but is not a primary citation subject, you may acknowledge it as follows:

> *"Code examples in this work were represented using the Kencode natural language mapping system (Alkhaldi et al., 2025). The online tool is available at https://khalidalkhaldi.pythonanywhere.com/"*

---

> **Note:** If you publish work that builds upon, extends, or evaluates Kencode, the authors welcome notification. The tool is provided freely for educational, research, and accessibility purposes in the spirit of the original paper's mission to advance voice-based and accessible programming.
