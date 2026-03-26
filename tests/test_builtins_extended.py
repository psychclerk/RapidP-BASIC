"""Test suite for Phase 1-2 builtins: rnd, peek/poke, locate, color, cls, etc."""
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rp_runtime.builtins import (
    rnd, randomize, peek, poke, locate, color, cls, csrlin, pos_func,
    screen_func, inkey, sizeof, memcpy, memset, memcmp, codeptr,
    freefile, filelen, beep, sound, eof_func, lof, seek_func,
    line_input, write_hash, pcopy,
    # Existing builtins
    rp_print, chr, asc, left, right, mid, len, instr, ucase, lcase,
    val, str_func, abs, sqr, hex_func, bin_func, oct_func,
    space, string, ltrim, rtrim, trim, iif, sgn, fix, frac, cint,
    ceil, acos, asin, tan, floor_func, round_func,
    field_func, tally, convbase, insert_func, replace_func, reverse_func,
    rinstr, delete_func, hextodec,
    rgb, lbound, ubound, randomize, timer, environ, curdir, fileexists,
)


class TestRND(unittest.TestCase):
    def test_rnd_no_args(self):
        """RND() returns float between 0 and 1."""
        for _ in range(100):
            v = rnd()
            self.assertIsInstance(v, float)
            self.assertGreaterEqual(v, 0.0)
            self.assertLess(v, 1.0)

    def test_rnd_with_arg(self):
        """RND(n) returns int between 0 and n-1."""
        for _ in range(100):
            v = rnd(200)
            self.assertIsInstance(v, int)
            self.assertGreaterEqual(v, 0)
            self.assertLessEqual(v, 199)

    def test_rnd_with_small_arg(self):
        v = rnd(1)
        self.assertEqual(v, 0)

    def test_randomize(self):
        randomize(42)
        a = rnd(1000)
        randomize(42)
        b = rnd(1000)
        self.assertEqual(a, b)


class TestPeekPoke(unittest.TestCase):
    def setUp(self):
        cls()  # Clear screen buffer

    def test_poke_and_peek(self):
        poke(0x0105, 65)  # row 1, col 5, char 'A'
        self.assertEqual(peek(0x0105), 65)

    def test_peek_default(self):
        # Unset location should return space (32)
        self.assertEqual(peek(0x0A0A), 32)

    def test_screen_func(self):
        poke(0x0305, 72)  # 'H'
        self.assertEqual(screen_func(3, 5), 72)


class TestLocateColor(unittest.TestCase):
    def test_locate(self):
        locate(10, 20)
        self.assertEqual(csrlin(), 10)
        self.assertEqual(pos_func(), 20)

    def test_cls_resets_cursor(self):
        locate(5, 5)
        cls()
        self.assertEqual(csrlin(), 1)
        self.assertEqual(pos_func(), 1)


class TestMemory(unittest.TestCase):
    def test_sizeof_int(self):
        self.assertEqual(sizeof(42), 4)

    def test_sizeof_float(self):
        self.assertEqual(sizeof(3.14), 8)

    def test_sizeof_string(self):
        self.assertEqual(sizeof("hello"), 5)

    def test_memcpy(self):
        src = [1, 2, 3, 4, 5]
        dest = [0, 0, 0, 0, 0]
        memcpy(dest, src, 3)
        self.assertEqual(dest, [1, 2, 3, 0, 0])

    def test_memset(self):
        buf = [0, 0, 0, 0, 0]
        memset(buf, 7, 3)
        self.assertEqual(buf, [7, 7, 7, 0, 0])

    def test_memcmp_equal(self):
        self.assertEqual(memcmp([1, 2, 3], [1, 2, 3], 3), 0)

    def test_memcmp_less(self):
        self.assertEqual(memcmp([1, 2, 3], [1, 2, 4], 3), -1)

    def test_memcmp_greater(self):
        self.assertEqual(memcmp([1, 2, 4], [1, 2, 3], 3), 1)


class TestCodeptr(unittest.TestCase):
    def test_codeptr_returns_id(self):
        def foo(): pass
        self.assertEqual(codeptr(foo), id(foo))


class TestFileOps(unittest.TestCase):
    def test_freefile(self):
        self.assertEqual(freefile(), 1)

    def test_filelen_nonexistent(self):
        self.assertEqual(filelen("nonexistent_file_xyz.tmp"), 0)

    def test_filelen_real(self):
        size = filelen(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "compile.py"))
        self.assertGreater(size, 0)


class TestInkey(unittest.TestCase):
    def test_inkey_returns_empty(self):
        self.assertEqual(inkey(), "")


class TestExistingBuiltins(unittest.TestCase):
    """Verify existing builtins still work after changes."""
    def test_chr_asc(self):
        self.assertEqual(chr(65), 'A')
        self.assertEqual(asc('A'), 65)

    def test_left_right_mid(self):
        self.assertEqual(left("Hello", 3), "Hel")
        self.assertEqual(right("Hello", 3), "llo")
        self.assertEqual(mid("Hello", 2, 3), "ell")

    def test_len(self):
        self.assertEqual(len("Hello"), 5)

    def test_instr(self):
        self.assertEqual(instr("Hello World", "World"), 7)

    def test_ucase_lcase(self):
        self.assertEqual(ucase("hello"), "HELLO")
        self.assertEqual(lcase("HELLO"), "hello")

    def test_val(self):
        self.assertEqual(val("42"), 42)
        self.assertEqual(val("3.14"), 3.14)
        self.assertEqual(val(""), 0)

    def test_str_func(self):
        self.assertEqual(str_func(42), "42")

    def test_math(self):
        self.assertEqual(abs(-5), 5)
        self.assertAlmostEqual(sqr(4), 2.0)
        self.assertEqual(sgn(-3), -1)
        self.assertEqual(sgn(0), 0)
        self.assertEqual(sgn(5), 1)

    def test_hex_bin_oct(self):
        self.assertEqual(hex_func(255), "FF")
        self.assertEqual(bin_func(10), "1010")
        self.assertEqual(oct_func(8), "10")

    def test_trim(self):
        self.assertEqual(ltrim("  hi"), "hi")
        self.assertEqual(rtrim("hi  "), "hi")
        self.assertEqual(trim("  hi  "), "hi")

    def test_space_string(self):
        self.assertEqual(space(5), "     ")
        self.assertEqual(string(3, "X"), "XXX")

    def test_iif(self):
        self.assertEqual(iif(True, "yes", "no"), "yes")
        self.assertEqual(iif(False, "yes", "no"), "no")

    def test_fix_frac(self):
        self.assertEqual(fix(3.7), 3)
        self.assertAlmostEqual(frac(3.7), 0.7)

    def test_field(self):
        self.assertEqual(field_func("a,b,c", ",", 2), "b")

    def test_tally(self):
        self.assertEqual(tally("banana", "a"), 3)

    def test_convbase(self):
        self.assertEqual(convbase("FF", 16, 10), "255")
        self.assertEqual(convbase("10", 10, 2), "1010")

    def test_insert_func(self):
        self.assertEqual(insert_func("Hello World", 6, " Beautiful"), "Hello Beautiful World")

    def test_replace_func(self):
        self.assertEqual(replace_func("Hello World", "World", "Python"), "Hello Python")

    def test_reverse(self):
        self.assertEqual(reverse_func("Hello"), "olleH")

    def test_rinstr(self):
        self.assertEqual(rinstr("abcabc", "bc"), 5)

    def test_delete_func(self):
        self.assertEqual(delete_func("Hello", 2, 3), "Ho")

    def test_hextodec(self):
        self.assertEqual(hextodec("FF"), 255)

    def test_rgb(self):
        # RGB in RapidP is actually BGR byte order
        c = rgb(255, 0, 0)  # Red
        self.assertEqual(c & 0xFF, 255)  # R byte

    def test_lbound_ubound(self):
        arr = [1, 2, 3, 4, 5]
        self.assertEqual(lbound(arr), 0)
        self.assertEqual(ubound(arr), 4)

    def test_timer(self):
        t = timer()
        self.assertGreater(t, 0)

    def test_environ(self):
        self.assertIsInstance(environ("PATH"), str)

    def test_curdir(self):
        self.assertTrue(os.path.isabs(curdir()))

    def test_ceil(self):
        self.assertEqual(ceil(2.1), 3)

    def test_round(self):
        self.assertEqual(round_func(2.5), 2)  # Python banker's rounding
        self.assertEqual(round_func(2.55, 1), 2.5)


if __name__ == '__main__':
    unittest.main()
