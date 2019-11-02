#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `insurance_solvency2_data` package."""

import unittest
import numpy as np
import pandas as pd

from datetime import datetime

from solvency2_data import solvency2_data

class TestSmithWilson(unittest.TestCase):

    def test_read_input_date(self):
        """Test of read input date function"""

        # Input
        date = datetime(2017,12,31)

        # Expected output
        expected = datetime(2017, 12, 31, 0, 0)

        # Actual output
        d = solvency2_data.read(date, path = "tests/test_data/")
        actual = d['input_date']

        # Assert
        self.assertEqual(type(actual), type(expected), "Read function, input_date: returned types not matching")
        self.assertEqual(actual, expected, "Read function, input_date: returned values not matching")

    def test_read_reference_date(self):
        """Test of read reference date function"""

        # Input
        date = datetime(2017,12,31)

        # Expected output
        expected = '20171231'

        # Actual output
        d = solvency2_data.read(date, path = "tests/test_data/")
        actual = d['reference_date']

        # Assert
        self.assertEqual(type(actual), type(expected), "Read function, reference_date: returned types not matching")
        self.assertEqual(actual, expected, "Read function, reference_date: returned values not matching")

    def test_read_meta_date(self):
        """Test of read meta data function"""

        # Input
        date = datetime(2017,12,31)

        # Expected output
        expected = pd.Series(index = ['Info', 'Coupon_freq', 'LLP', 'Convergence', 'UFR', 'alpha', 'CRA', 'VA', 'reference date'], 
                             data = ['EUR_31_12_2017_SWP_LLP_20_EXT_40_UFR_4.2', 1, 20, 40, 4.2, 0.126759, 10, 4, '20171231'],
                             name = 'Euro')

        # Actual output
        d = solvency2_data.read(date, path = "tests/test_data/")
        actual = d['meta'].loc[:,'Euro']

        # Assert
        self.assertEqual(type(actual), type(expected), "Read function, meta data: returned types not matching")
        assert (actual == expected).all(), "Read function, meta data: returned values not matching"

    def test_read_spot_rates(self):
        """Test of read spot rates function"""

        # Input
        date = datetime(2017,12,31)

        # Expected output
        expected = pd.Series(index = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                      20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
                                      37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53,
                                      54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
                                      71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87,
                                      88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103,
                                      104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116,
                                      117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129,
                                      130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142,
                                      143, 144, 145, 146, 147, 148, 149, 150],
                             data = [-0.00358, -0.0025, -0.00088, 0.00069, 0.00209, 0.00347, 0.00469,
                                      0.00585, 0.00695, 0.00802, 0.00897, 0.00982, 0.01059, 0.01125,
                                      0.01177, 0.01217, 0.01249, 0.0128, 0.01316, 0.01357, 0.01408,
                                      0.01464, 0.01524, 0.01586, 0.01649, 0.01713, 0.01775, 0.01837,
                                      0.01897, 0.01956, 0.02013, 0.02069, 0.02122, 0.02174, 0.02223,
                                      0.02271, 0.02317, 0.02362, 0.02404, 0.02445, 0.02485, 0.02523,
                                      0.02559, 0.02594, 0.02628, 0.0266, 0.02692, 0.02722, 0.02751,
                                      0.02779, 0.02806, 0.02832, 0.02857, 0.02881, 0.02905, 0.02928,
                                      0.02949, 0.02971, 0.02991, 0.03011, 0.0303, 0.03049, 0.03067,
                                      0.03084, 0.03101, 0.03118, 0.03134, 0.03149, 0.03164, 0.03179,
                                      0.03193, 0.03207, 0.03221, 0.03234, 0.03247, 0.03259, 0.03271,
                                      0.03283, 0.03295, 0.03306, 0.03317, 0.03328, 0.03338, 0.03348,
                                      0.03358, 0.03368, 0.03378, 0.03387, 0.03396, 0.03405, 0.03414,
                                      0.03422, 0.0343, 0.03439, 0.03447, 0.03454, 0.03462, 0.0347,
                                      0.03477, 0.03484, 0.03491, 0.03498, 0.03505, 0.03512, 0.03518,
                                      0.03525, 0.03531, 0.03537, 0.03543, 0.03549, 0.03555, 0.03561,
                                      0.03566, 0.03572, 0.03577, 0.03583, 0.03588, 0.03593, 0.03598,
                                      0.03603, 0.03608, 0.03613, 0.03618, 0.03622, 0.03627, 0.03631,
                                      0.03636, 0.0364, 0.03645, 0.03649, 0.03653, 0.03657, 0.03661,
                                      0.03665, 0.03669, 0.03673, 0.03677, 0.03681, 0.03684, 0.03688,
                                      0.03692, 0.03695, 0.03699, 0.03702, 0.03706, 0.03709, 0.03712,
                                      0.03716, 0.03719, 0.03722],
                             name = 'Euro')

        # Actual output
        d = solvency2_data.read(date, path = "tests/test_data/")
        actual = d['RFR_spot_no_VA']['Euro']

        # Assert
        self.assertEqual(type(actual), type(expected), "Read function, spot rates: returned types not matching")
        assert (actual == expected).all(), "Read function, spot rates: returned values not matching"

    def test_big_h(self):
        """Test of big_h function"""

        # Input
        u = 1.1
        v = 1.2

        # Expected output
        expected = np.float64(0.697710712843422)

        # Actual output
        actual = solvency2_data.big_h(u,v)

        # Assert
        self.assertEqual(type(actual), type(expected), "Returned types not matching")
        self.assertTupleEqual(actual.shape, expected.shape, "Shapes not matching")
        np.testing.assert_almost_equal(actual, expected, decimal=8, err_msg="big_h output not matching")

    def test_big_g_1(self):
        """Test of big_g 1"""

        # Input
        alfa = 1.1
        q = np.array([[1,      0,      0,     0], 
                      [0,   1.01,      0,     0], 
                      [0,      0,   1.02,     0], 
                      [0,      0,      0,  1.03]])
        t2 = 1
        tau = 0.9
        nrofcoup = 1

        #Expected output
        expected = np.float64(-0.7248604952614899) 

        #Actual output
        actual = solvency2_data.big_g(alfa, q, nrofcoup, t2, tau)[0]

        # Assert
        self.assertEqual(type(actual), type(expected), "Returned types not matching")
        self.assertTupleEqual(actual.shape, expected.shape, "Shapes not matching")
        np.testing.assert_almost_equal(actual, expected, decimal=8, err_msg="big_g output not matching")

    def test_big_g_2(self):
        """Test of big_g 2"""

        # Input
        alfa = 1.1
        q = np.array([[1,      0,      0,     0], 
                      [0,   1.01,      0,     0], 
                      [0,      0,   1.02,     0], 
                      [0,      0,      0,  1.03]])
        t2 = 1
        tau = 0.9
        nrofcoup = 1

        #Expected output
        expected = np.array([[0.03861839], [-0.02275808], [0.01393944], [-0.0168802]])

        #Actual output
        actual = solvency2_data.big_g(alfa, q, nrofcoup, t2, tau)[1]

        # Assert
        self.assertEqual(type(actual), type(expected), "Returned types not matching")
        self.assertTupleEqual(actual.shape, expected.shape, "Shapes not matching")
        np.testing.assert_almost_equal(actual, expected, decimal=8, err_msg="big_g output not matching")

    def test_smith_wilson(self):

        liqmat = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20]
        rates = { 1: -0.00525, 
                  2: -0.00553, 
                  3: -0.00559,
                  4: -0.00534,
                  5: -0.00505,
                  6: -0.00467,
                  7: -0.00420,
                  8: -0.00366,
                  9: -0.00309,
                  10: -0.00254,
                  12: -0.00150,
                  15: -0.00024,
                  20:  0.00092}
        instrument = "Zero"
        nrofcoup = 1
        cra = 0.0
        ufr = 0.0
        tau = 1
        alfamin = 0.05
        t2 = 60
        nrofcoup = 1

        #Expected output
        expected = np.array([ 0.00000000e+00, -5.25000000e-03, -5.53000000e-03, -5.59000000e-03,
                             -5.34000000e-03, -5.05000000e-03, -4.67000000e-03, -4.20000000e-03,
                             -3.66000000e-03, -3.09000000e-03, -2.54000000e-03, -2.00662955e-03,
                             -1.50000000e-03, -1.03211946e-03, -6.10363926e-04, -2.40000000e-04,
                              7.67955874e-05,  3.45746494e-04,  5.72972040e-04,  7.63178566e-04,
                              9.20000000e-04,  1.04680054e-03,  1.14834606e-03,  1.22899633e-03,
                              1.29230832e-03,  1.34120112e-03,  1.37808266e-03,  1.40494828e-03,
                              1.42345803e-03,  1.43499784e-03,  1.44072830e-03,  1.44162391e-03,
                              1.43850474e-03,  1.43206223e-03,  1.42288027e-03,  1.41145258e-03,
                              1.39819698e-03,  1.38346732e-03,  1.36756333e-03,  1.35073892e-03,
                              1.33320907e-03,  1.31515570e-03,  1.29673255e-03,  1.27806937e-03,
                              1.25927540e-03,  1.24044238e-03,  1.22164709e-03,  1.20295353e-03,
                              1.18441475e-03,  1.16607446e-03,  1.14796836e-03,  1.13012531e-03,
                              1.11256832e-03,  1.09531543e-03,  1.07838042e-03,  1.06177345e-03,
                              1.04550162e-03,  1.02956940e-03,  1.01397909e-03,  9.98731108e-04,
                              9.83824338e-04,  9.69256355e-04,  9.55023664e-04,  9.41121883e-04,
                              9.27545908e-04,  9.14290059e-04,  9.01348191e-04,  8.88713806e-04,
                              8.76380136e-04,  8.64340221e-04,  8.52586972e-04,  8.41113225e-04,
                              8.29911787e-04,  8.18975477e-04,  8.08297155e-04,  7.97869751e-04,
                              7.87686285e-04,  7.77739889e-04,  7.68023819e-04,  7.58531467e-04,
                              7.49256372e-04,  7.40192223e-04,  7.31332869e-04,  7.22672318e-04,
                              7.14204744e-04,  7.05924482e-04,  6.97826033e-04,  6.89904062e-04,
                              6.82153393e-04,  6.74569011e-04,  6.67146061e-04,  6.59879837e-04,
                              6.52765787e-04,  6.45799506e-04,  6.38976733e-04,  6.32293347e-04,
                              6.25745361e-04,  6.19328924e-04,  6.13040310e-04,  6.06875919e-04,
                              6.00832270e-04,  5.94906000e-04,  5.89093857e-04,  5.83392700e-04,
                              5.77799490e-04,  5.72311292e-04,  5.66925268e-04,  5.61638674e-04,
                              5.56448858e-04,  5.51353254e-04,  5.46349384e-04,  5.41434848e-04,
                              5.36607327e-04,  5.31864576e-04,  5.27204424e-04,  5.22624772e-04,
                              5.18123584e-04,  5.13698895e-04,  5.09348798e-04,  5.05071449e-04,
                              5.00865063e-04])

        #Actual output
        actual = solvency2_data.smith_wilson(instrument, liqmat, rates, nrofcoup, cra, ufr, alfamin, tau, t2, output_type = "zero rates annual compounding")

        # Assert
        self.assertEqual(type(actual), type(expected), "Returned types not matching")
        self.assertTupleEqual(actual.shape, expected.shape, "Shapes not matching")
        np.testing.assert_almost_equal(actual, expected, decimal=8, err_msg="smith_wilson_brute_force output not matching")

if __name__ == '__main__':
    unittest.main()
