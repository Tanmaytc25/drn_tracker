import unittest
from app import calculate_risk

class TestDRN(unittest.TestCase):
    def test_risk_score_max(self):
        self.assertEqual(calculate_risk(5,5,5,5), 100.0)

    def test_risk_score_min(self):
        self.assertEqual(calculate_risk(0,0,0,0), 0.0)

    def test_risk_score_mid(self):
        score = calculate_risk(3,2,1,0)
        self.assertTrue(0 <= score <= 100)

if __name__ == "__main__":
    unittest.main()

