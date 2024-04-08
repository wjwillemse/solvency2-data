import numpy as np
from numpy.linalg import inv


def big_h(u: np.array, v: np.array) -> np.array:
    """
    Calculates the big h-function according to specification 139.

    Args:
        u (np.array): Input array for u.
        v (np.array): Input array for v.

    Returns:
        np.array: Output array containing the result of the big h-function.

    Example:
        >>> import numpy as np
        >>> u = np.array([1, 2, 3])
        >>> v = np.array([2, 3, 4])
        >>> big_h(u, v)
        array([-0.06544022, -0.57483282, -1.0       ])

    """
    left = (u + v + np.exp(-u - v)) / 2
    diff = np.abs(u - v)
    right = (diff + np.exp(-diff)) / 2
    return left - right


def big_g(alfa: float, q: np.array, nrofcoup: float, t2: float, tau: float) -> np.array:
    """
    Calculates the big g-function according to specification 156.

    Args:
        alfa (float): Alfa value.
        q (np.array): Input array for q.
        nrofcoup (float): Number of coupons.
        t2 (float): T2 value.
        tau (float): Tau value.

    Returns:
        np.array: Output array containing the result of the big g-function.

    Example:
        >>> import numpy as np
        >>> alfa = 0.1
        >>> q = np.array([[0.1, 0.2], [0.3, 0.4]])
        >>> nrofcoup = 10
        >>> t2 = 5
        >>> tau = 0.2
        >>> big_g(alfa, q, nrofcoup, t2, tau)
        (array([[0.9833673]]), array([[-0.07812712],
               [-0.30490089]]))
    """
    n, m = q.shape
    # construct m*m h-matrix
    h = np.fromfunction(
        lambda i, j: big_h(alfa * (i + 1) / nrofcoup, alfa * (j + 1) / nrofcoup), (m, m)
    )
    # Solving b according to 156 of specs, note: p = 1 by construction
    res_1 = np.array([1 - np.sum(q[i]) for i in range(n)]).reshape((n, 1))
    # b = ((Q'HQ)^(-1))(1-Q'1) according to 156 of the specs
    b = np.matmul(inv(np.matmul(np.matmul(q, h), q.T)), res_1)
    # gamma variable is used to store Qb according to 156 of specs
    gamma = np.matmul(q.T, b)
    res_2 = sum(gamma[i, 0] * (i + 1) / nrofcoup for i in range(0, m))
    res_3 = sum(gamma[i, 0] * np.sinh(alfa * (i + 1) / nrofcoup) for i in range(0, m))
    kappa = (1 + alfa * res_2) / res_3
    return (alfa / np.abs(1 - kappa * np.exp(t2 * alfa)) - tau, gamma)


def optimal_alfa(
    alfa: float, q: float, nrofcoup: float, t2: float, tau: float, precision: float
) -> tuple:
    """
    Finds the optimal alfa value based on the given parameters and precision.

    Args:
        alfa (float): Initial alfa value.
        q (float): Input value for q.
        nrofcoup (float): Number of coupons.
        t2 (float): T2 value.
        tau (float): Tau value.
        precision (float): Precision level for finding the optimal alfa.

    Returns:
        tuple: A tuple containing the optimal alfa value and the corresponding gamma value.

    Example:
        >>> alfa = 0.1
        >>> q = 0.2
        >>> nrofcoup = 10
        >>> t2 = 5
        >>> tau = 0.2
        >>> precision = 0.01
        >>> optimal_alfa(alfa, q, nrofcoup, t2, tau, precision)
        (0.09999999999999999, array([[-0.07812712],
               [-0.30490089]]))
    """
    new_alfa, gamma = big_g(alfa, q, nrofcoup, t2, tau)
    if new_alfa > 0:
        # scanning for the optimal alfa is based on the scan-procedure taken
        # from Eiopa matlab production code in each for-next loop the next
        # optimal alfa decimal is scanned for, starting with an stepsize
        # of 0.1 (first decimal) followed by the a next decimal through
        # stepsize = stepsize/10
        stepsize = 0.1
        #        for alfa in range(alfamin + stepsize, 20, stepsize):
        for i in range(0, 200):
            alfa = alfa + stepsize + i / 10
            new_alfa, gamma = big_g(alfa, q, nrofcoup, t2, tau)
            if new_alfa <= 0:
                break
        for i in range(0, precision - 1):
            alfa = alfa - stepsize
            for i in range(1, 11):
                alfa = alfa + stepsize / 10
                new_alfa, gamma = big_g(alfa, q, nrofcoup, t2, tau)
                if new_alfa <= 0:
                    break
            stepsize = stepsize / 10
    return (alfa, gamma)


def q_matrix(
    instrument: str,
    n: int,
    m: int,
    liquid_maturities: int,
    RatesIn: np.array,
    nrofcoup: float,
    cra: float,
    log_ufr: float,
):
    """
    Constructs the Q matrix based on the provided instrument and parameters.

    Note: Prices of all instruments are set to 1 by construction.
    Hence 1: if Instrument = Zero then for Zero i there is only one pay-off
    of (1+r(i))^u(i) at time u(i).
    Hence 2: if Instrument = Swap or Bond then for Swap/Bond i there are
    pay-offs of r(i)/nrofcoup at time 1/nrofcoup, 2/nrofcoup, ...
    u(i)-1/nrofcoup plus a final pay-off of 1+r(i)/nrofcoup at time u(i).

    Args:
        instrument (str): Type of financial instrument.
        n (int): Number of rows for the Q matrix.
        m (int): Number of columns for the Q matrix.
        liquid_maturities (int): Liquid maturities.
        RatesIn (np.array): Input array for RatesIn.
        nrofcoup (float): Number of coupons.
        cra (float): CRA value.
        log_ufr (float): Log UFR value.

    Returns:
        np.array: The Q matrix.

    Example:
        >>> instrument = "Zero"
        >>> n = 5
        >>> m = 10
        >>> liquid_maturities = [1, 2, 3, 4, 5]
        >>> RatesIn = np.array([0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065])
        >>> nrofcoup = 2
        >>> cra = 0.01
        >>> log_ufr = 0.05
        >>> q_matrix(instrument, n, m, liquid_maturities, RatesIn, nrofcoup, cra, log_ufr)
        array([[0.98212276, 0.96306662, 0.9434712 , 0.92329604, 0.90249446,
                0.88101278, 0.85879177, 0.83576508, 0.81185891, 0.78699164],
               [0.96147922, 0.92493439, 0.89089811, 0.85915296, 0.8294894 ,
                0.80171838, 0.7756698 , 0.75118792, 0.7281295 , 0.70636475],
               [0.94115884, 0.88886852, 0.84156022, 0.79889855, 0.76055566,
                0.72622884, 0.6956359 , 0.66851953, 0.64464666, 0.6238033 ],
               [0.92115253, 0.85321133, 0.79353918, 0.74081822, 0.69373509,
                0.65182761, 0.61455512, 0.58132809, 0.55153767, 0.52460095],
               [0.90145167, 0.81806971, 0.74818245, 0.68630865, 0.6314886 ,
                0.58232972, 0.53795468, 0.497996  , 0.4623893 , 0.43049448]])
    """
    q = np.zeros([n, m])
    if instrument == "Zero":
        for i, u in enumerate(liquid_maturities):
            q[i, u - 1] = np.exp(-log_ufr * u) * np.power(1 + RatesIn[u] - cra, u)
    #    elif instrument == "Swap" or instrument == "Bond":
    # not yet correct
    #        for i in range(0, n):
    #            for j in range(1, u[i] * nrofcoup - 1):
    #                q[i, j] = np.exp(-log_ufr * j / nrofcoup) * (r[i] - cra)
    #                               / nrofcoup
    #            q[i, j] = np.exp(-log_ufr * j / nrofcoup) * (1 + (r[i] - cra)
    #                               / nrofcoup)
    return q


def smith_wilson(
    instrument: str = "Zero",
    liquid_maturities: list = [],
    RatesIn: dict = {},
    nrofcoup: int = 1,
    cra: float = 0,
    ufr: float = 0,
    min_alfa: float = 0.05,
    tau: float = 1,
    T2: int = 60,
    precision: int = 6,
    method: str = "brute_force",
    output_type: str = "zero rates annual compounding",
):
    """
    Calculates Smith-Wilson parameters and returns output based on the specified parameters.

    Note: Prices of all instruments are set to 1 by construction.
    Hence 1: if Instrument = Zero then for Zero i there is only one pay-off
    of (1+r(i))^u(i) at time u(i).
    Hence 2: if Instrument = Swap or Bond then for Swap/Bond i there are
    pay-offs of r(i)/nrofcoup at time 1/nrofcoup, 2/nrofcoup, ...
    u(i)-1/nrofcoup plus a final pay-off of 1+r(i)/nrofcoup at time u(i).

    Args:
        instrument (str): Type of financial instrument. Default is "Zero".
        liquid_maturities (list): Liquid maturities.
        RatesIn (dict): Input dictionary for RatesIn.
        nrofcoup (int): Number of Coupon Payments per Year. Default is 1.
        cra (float): Credit Risk Adjustment in basispoints. Default is 0.
        ufr (float): Ultimate Forward Rate annual compounded (perunage). Default is 0.
        min_alfa (float): Minimum value for alfa. Default is 0.05.
        tau (float): Tau value. Default is 1.
        T2 (int): Convergence Maturity. Default is 60.
        precision (int): Precision value. Default is 6.
        method (str): Calculation method. Default is "brute_force".
        output_type (str): Type of output. Default is "zero rates annual compounding".

    Returns:
        output: Calculated output based on the specified parameters.

    Example:
        >>> instrument = "Zero"
        >>> liquid_maturities = [1, 2, 3, 4, 5]
        >>> RatesIn = {0: 0.02, 1: 0.025, 2: 0.03, 3: 0.035, 4: 0.04, 5: 0.045}
        >>> nrofcoup = 2
        >>> cra = 0.01
        >>> ufr = 0.05
        >>> min_alfa = 0.05
        >>> tau = 1
        >>> T2 = 60
        >>> precision = 6
        >>> method = "brute_force"
        >>> output_type = "zero rates annual compounding"
        >>> smith_wilson(instrument, liquid_maturities, RatesIn, nrofcoup, cra, ufr, min_alfa, tau, T2, precision, method, output_type)
        array([0.        , 0.01984642, 0.04040711, 0.06171705, 0.08381221,
               0.10672926, 0.13050535, 0.15517806, 0.18078504, 0.20736481,
               0.23495648, 0.26360038, 0.29333873, 0.3242144 , 0.35627157,
               0.3895553 , 0.42411294, 0.4599934 , 0.49724737, 0.53592752,
               0.57608986, 0.61779295, 0.66109833, 0.70607181, 0.75278461,
               0.80131366, 0.85174183, 0.90415729, 0.95865366, 1.01533039,
               1.0742924 , 1.13564943, 1.19951555, 1.26601055, 1.33526045,
               1.40739786, 1.48256135, 1.5608958 , 1.6425528 , 1.72769014,
               1.81647324, 1.90907556, 2.00567914, 2.10647707, 2.21167306,
               2.32148215, 2.43613139, 2.55586064, 2.68092039, 2.81157657,
               2.94810739, 3.09080731, 3.23998602, 3.39596949, 3.559099  ,
               3.72973118, 3.90823814, 4.09500861, 4.29045285, 4.49400082,
               4.70510529, 4.92324198, 5.14791281, 5.37864303, 5.61498852,
               5.85652901, 6.10287445, 6.35366537, 6.6085712 , 6.86728774,
               7.12954064, 7.395082  , 7.66368905, 7.93516083, 8.20931788,
               8.48599994, 8.76506649, 9.04639664, 9.329887  , 9.61545067,
               9.90301596, 10.19252555, 10.48393262, 10.77720086, 11.07230382,
               11.36922416, 11.66795383, 11.96849432, 12.27085209, 12.57503994,
               12.88007745, 13.18599135, 13.49281377, 13.80058263, 14.109341  ,
               14.41913647, 14.73002158, 15.04205535, 15.35530365, 15.66983964,
               15.98574325, 16.30310069, 16.62199494, 16.94251238, 17.2647438 ,
               17.5887832 , 17.91472858, 18.24268076, 18.5727421 , 18.90502131,
               19.23963426, 19.57670285, 19.9163558 , 20.25872748, 20.60395864,
               20.95219615, 21.30359381, 21.65831201, 22.01651854, 22.3783874 ])
    """
    assert (
        instrument == "Zero" and nrofcoup == 1
    ), "instrument is zero bond, but with nrofcoup unequal to 1."
    assert method == "brute_force", "Only brute force method is implemented."
    assert instrument == "Zero", "No other instruments implemented yet."

    # the number of liquid rates
    n = len(liquid_maturities)
    # nrofcoup * maximum liquid maturity
    m = nrofcoup * max(liquid_maturities)

    log_ufr = np.log(1 + ufr)
    tau = tau / 10000
    cra = cra / 10000

    # Q' matrix according to 146 of specs;
    q = q_matrix(instrument, n, m, liquid_maturities, RatesIn, nrofcoup, cra, log_ufr)

    # Determine optimal alfa with corresponding gamma
    if method == "brute_force":
        alfa, gamma = optimal_alfa(min_alfa, q, nrofcoup, T2, tau, precision)
    alfa = np.round(alfa, 6)

    # Now the SW-present value function according to 154 of the specs can be
    # calculated: p(v)=exp(-lnUFR*v)*(1+H(v,u)*Qb)
    # The G(v,u) matrix for maturities v = 1 to 121 according to 142 of the
    # technical specs (Note: maturity 121 will not be used; see later)
    g = np.fromfunction(
        lambda i, j: np.where(
            j / nrofcoup > i,
            alfa * (1 - np.exp(-alfa * j / nrofcoup) * np.cosh(alfa * i)),
            alfa * np.exp(-alfa * i) * np.sinh(alfa * j / nrofcoup),
        ),
        (121, m),
    )

    # The H(v,u) matrix for maturities v = 1 to 121 according to 139
    # of the technical specs
    # h[i, j] = big_h(alfa * i, alfa * (j+1) / nrofcoup) -> strange,
    # is different from earlier def
    h = np.fromfunction(
        lambda i, j: big_h(alfa * i / nrofcoup, alfa * (j + 1) / nrofcoup), (122, m)
    )

    # First a temporary discount-vector will be used to store the in-between
    # result H(v,u)*Qb = #(v,u)*gamma (see 154 of the specs)
    temptempdiscount = np.matmul(h, gamma)
    # Calculating G(v,u)*Qb according to 158 of the specs
    temptempintensity = np.matmul(g, gamma)

    tempdiscount = np.zeros(121)
    tempintensity = np.zeros(121)
    for i in range(0, 121):
        tempdiscount[i] = temptempdiscount[i][0]
        tempintensity[i] = temptempintensity[i][0]

    # calculating (1'-exp(-alfa*u'))Qb as subresult for 160 of specs
    res1 = sum(
        (1 - np.exp(-alfa * (i + 1) / nrofcoup)) * gamma[i, 0] for i in range(0, m)
    )

    # yield intensities
    yldintensity = np.zeros(121)
    yldintensity[0] = log_ufr - alfa * res1  # calculating 160 of the specs
    # calculating 158 of the specs for maturity 1 year
    yldintensity[1:] = log_ufr - np.log(1 + tempdiscount[1:]) / np.arange(1, 121)

    # forward intensities # calculating 158 of the specs for higher maturities
    fwintensity = np.zeros(121)
    fwintensity[0] = log_ufr - alfa * res1  # calculating 160 of the specs
    fwintensity[1:] = log_ufr - tempintensity[1:] / (1 + tempdiscount[1:])

    # discount rates
    discount = np.zeros(121)
    discount[0] = 1
    discount[1:] = np.exp(-log_ufr * np.arange(1, 121)) * (1 + tempdiscount[1:])

    # forward rates annual compounding
    forwardac = np.zeros(121)
    forwardac[0] = 0
    forwardac[1:] = discount[:-1] / discount[1:] - 1

    # zero rates annual compounding
    zeroac = np.zeros(121)
    zeroac[0] = 0
    zeroac[1:] = np.power(discount[1:], -1 / np.arange(1, 121)) - 1

    if output_type == "zero rates annual compounding":
        output = zeroac
    elif output_type == "forward rate annual compounding":
        output = forwardac
    elif output_type == "discount rates":
        output = discount
    elif output_type == "forward intensities":
        output = fwintensity
    elif output_type == "yield intensities":
        output = yldintensity
    elif output_type == "alfa":
        output = alfa

    return output
