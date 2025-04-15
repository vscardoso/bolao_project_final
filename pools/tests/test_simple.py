from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """Um teste simples que sempre deve passar"""
        self.assertEqual(1 + 1, 2)