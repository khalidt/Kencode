"""
Basic tests for the Kencode package.
Run with: pytest tests/
"""

import pytest
from kencode import python_to_kencode, kencode_to_python, decode_kvi


class TestConverter:
    """Python → Kencode conversion tests."""

    def test_integer_assignment(self):
        ks, kvi = python_to_kencode("x = 10")
        assert ks  == "[W][O][B][W]"
        assert kvi == "x equals digit ten"

    def test_string_assignment(self):
        ks, kvi = python_to_kencode('name = "Alice"')
        assert ks  == "[W][O][B][W]"
        assert kvi == "name equals string Alice"

    def test_float_assignment(self):
        ks, kvi = python_to_kencode("y = 3.5")
        assert ks  == "[W][O][B][W][B][W]"
        assert kvi == "y equals digit three point 5"

    def test_boolean_assignment(self):
        ks, kvi = python_to_kencode("is_valid = True")
        assert ks  == "[W][W][O][K]"
        assert kvi == "is valid equals true"

    def test_print_expression(self):
        ks, kvi = python_to_kencode("print(x + y)")
        assert ks  == "[K][B][W][O][B][W]"
        assert kvi == "print variable x plus variable y"

    def test_for_loop(self):
        ks, kvi = python_to_kencode("for i in range(5):")
        assert ks  == "[K][B][W][K][B][W][B][B][W]"
        assert kvi == "for variable i in call range pass digit five"

    def test_def_function(self):
        ks, kvi = python_to_kencode("def greet(name):")
        assert "[K]" in ks
        assert "def" in kvi
        assert "greet" in kvi

    def test_comment(self):
        ks, kvi = python_to_kencode("# this is a comment")
        assert ks.startswith("[B]")
        assert kvi.startswith("comment")

    def test_blank_line(self):
        ks, kvi = python_to_kencode("")
        assert ks  == ""
        assert kvi == ""

    def test_list_literal(self):
        ks, kvi = python_to_kencode("my_list = [1, 2, 3]")
        assert "list" in kvi
        assert "digit" in kvi

    def test_ignore_placeholder(self):
        ks, kvi = python_to_kencode("a, _, b = (1, 2, 3)")
        assert "ignore" in kvi
        assert "[B]" in ks

    def test_indentation(self):
        ks, kvi = python_to_kencode("    x = 10")
        assert kvi.startswith("1 tab")
        assert ks.startswith("[W][B]")

    def test_lambda(self):
        ks, kvi = python_to_kencode("square = lambda x: x**2")
        assert "lambda" in kvi
        assert "expression" in kvi


class TestDecoder:
    """KVI → Python conversion tests."""

    def test_integer_assignment(self):
        ks, py = decode_kvi("x equals digit ten")
        assert py == "x = 10"
        assert "[W][O][B][W]" == ks

    def test_string_assignment(self):
        ks, py = decode_kvi("name equals string Alice")
        assert py == 'name = "Alice"'

    def test_boolean_assignment(self):
        ks, py = decode_kvi("is valid equals true")
        assert py == "is_valid = True"

    def test_for_loop(self):
        ks, py = decode_kvi("for variable i in call range pass digit five")
        assert py == "for i in range(5):"

    def test_def_with_dunder(self):
        ks, py = decode_kvi("1 tab def hook init pass variable self variable name")
        assert py == "    def __init__(self, name):"

    def test_except(self):
        ks, py = decode_kvi("except type zero division error")
        assert py == "except ZeroDivisionError:"

    def test_ignore_placeholder(self):
        ks, py = decode_kvi(
            "variable num ignore variable last equals tuple digit one digit two digit three"
        )
        assert py == "num, _, last = (1, 2, 3)"

    def test_lambda_filter(self):
        ks, py = decode_kvi(
            "even numbers equals call list pass call filter pass "
            "lambda variable x expression variable x modulo digit two "
            "is equal digit zero pass variable numbers"
        )
        assert py == "even_numbers = list(filter(lambda x: x % 2 == 0, numbers))"

    def test_blank_line(self):
        ks, py = decode_kvi("")
        assert ks == ""
        assert py == ""

    def test_comment(self):
        ks, py = decode_kvi("comment this is a test")
        assert py == "# this is a test"


class TestRoundTrip:
    """Convert Python → KVI → Python and verify round-trip fidelity."""

    ROUND_TRIP_CASES = [
        "x = 10",
        'name = "Alice"',
        "y = 3.5",
        "for i in range(5):",
        "    def __init__(self, name):",
        "except ZeroDivisionError:",
    ]

    @pytest.mark.parametrize("python_line", ROUND_TRIP_CASES)
    def test_round_trip(self, python_line):
        _, kvi = python_to_kencode(python_line)
        _, recovered = decode_kvi(kvi)
        assert recovered == python_line, (
            f"Round-trip failed:\n"
            f"  Original : {python_line!r}\n"
            f"  KVI      : {kvi!r}\n"
            f"  Recovered: {recovered!r}"
        )
