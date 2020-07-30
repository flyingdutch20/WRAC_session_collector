from unittest import TestCase

def fun(x):
    return x + 1

class Test(TestCase):
    def test_scrape_classfit(self):
        self.assertEqual(fun(3), 4)
