import unittest

from core.utils.strings import to_camel


class TestStringMethods(unittest.TestCase):

    def test_to_camel(self):
        self.assertEqual(to_camel("title"), "title")
        self.assertEqual(to_camel("id"), "id")
        self.assertEqual(to_camel("long_name"), "longName")
        self.assertEqual(to_camel("long_name_with_numbers_1"), "longNameWithNumbers1")
        self.assertEqual(to_camel("long_name_with_numbers_1_2"), "longNameWithNumbers12")
        self.assertEqual(to_camel("long_name_with_numbers_1_3"), "longNameWithNumbers13")
        self.assertEqual(to_camel("long_name_w_short_letters"), "longNameWShortLetters")
        self.assertEqual(to_camel("even_longer_one"), "evenLongerOne")


if __name__ == "__main__":
    unittest.main()
