#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `insurance_solvency2_rfr` package."""

import unittest
import numpy as np

from solvency2_rfr import solvency2_rfr

class TestSmithWilson(unittest.TestCase):

    def test_big_h(self):
        """Test of big_h function"""

        # Input
        u = 1.1
        v = 1.2

        # Expected output
        expected = np.float64(0.697710712843422)

        # Actual output
        actual = solvency2_rfr.big_h(u,v)

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
        actual = solvency2_rfr.big_g(alfa, q, nrofcoup, t2, tau)[0]

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
        actual = solvency2_rfr.big_g(alfa, q, nrofcoup, t2, tau)[1]

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
        actual = solvency2_rfr.smith_wilson(instrument, liqmat, rates, nrofcoup, cra, ufr, alfamin, tau, t2, output_type = "zero rates annual compounding")

        # Assert
        self.assertEqual(type(actual), type(expected), "Returned types not matching")
        self.assertTupleEqual(actual.shape, expected.shape, "Shapes not matching")
        np.testing.assert_almost_equal(actual, expected, decimal=8, err_msg="smith_wilson_brute_force output not matching")

if __name__ == '__main__':
    unittest.main()
