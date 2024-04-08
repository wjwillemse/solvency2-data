import pandas as pd
import numpy as np
from collections import OrderedDict

CRA = 0.001
MAX_ERROR = 0.0000000001
MAX_RUNS = 20


def DiscountedValue4par2forwards(
    sum_df: float = 0,
    last_df: float = 0,
    par_rate: float = 0,
    forward_rate: float = 0,
    t_min_k: int = 0,
) -> float:
    """
    Calculates the discounted value for two-factor parallel forwards.

    Args:
        sum_df (float, optional): The sum of discount factors. Defaults to 0.
        last_df (float, optional): The last discount factor. Defaults to 0.
        par_rate (float, optional): The par rate. Defaults to 0.
        forward_rate (float, optional): The forward rate. Defaults to 0.
        t_min_k (int, optional): The difference between the two terms. Defaults to 0.

    Returns:
        float: The calculated discounted value.
    """
    disc_val_1 = sum_df * par_rate
    disc_val_2 = 0
    for i in range(1, t_min_k + 1):
        disc_val_1 += par_rate * last_df / ((1 + forward_rate) ** i)
        disc_val_2 -= i * par_rate * last_df / ((1 + forward_rate) ** (i + 1))
    disc_val_1 += last_df / ((1 + forward_rate) ** t_min_k) - 1
    disc_val_2 -= t_min_k * last_df / ((1 + forward_rate) ** (t_min_k + 1))
    return disc_val_1, disc_val_2


def FromParToForwards(
    term_struct: pd.Series(dtype="float64") = None,
    span: int = 120,
    max_runs: int = MAX_RUNS,
    max_error: float = MAX_ERROR,
):
    """
    Converts a par rate term structure to forward rates.

    Args:
        term_struct (pd.Series, optional): The par rate term structure. Defaults to None.
        span (int, optional): The span of the forward rates. Defaults to 120.
        max_runs (int, optional): The maximum number of iterations for convergence. Defaults to MAX_RUNS.
        max_error (float, optional): The maximum error for convergence. Defaults to MAX_ERROR.

    Returns:
        pd.Series: The forward rates term structure.
    """
    forwards_struct = np.zeros(span)

    sum_df = 0
    df = 1
    previous_maturity = 0
    for maturity in term_struct.keys():
        f = 0
        t_min_k = maturity - previous_maturity
        disc_val_1, disc_val_2 = DiscountedValue4par2forwards(
            sum_df, df, term_struct[maturity], f, t_min_k
        )
        k = 0
        while np.abs(disc_val_1) >= max_error and k <= max_runs:
            f = f - disc_val_1 / disc_val_2
            disc_val_1, disc_val_2 = DiscountedValue4par2forwards(
                sum_df, df, term_struct[maturity], f, t_min_k
            )
            k = k + 1
        for i in range(previous_maturity + 1, maturity + 1):
            forwards_struct[i - 1] = f
            df /= 1 + forwards_struct[i - 1]
            sum_df += df
        previous_maturity = maturity

    for i in range(term_struct.keys()[-1], span + 1):
        forwards_struct[i - 1] = forwards_struct[i - 2]

    return pd.Series(data=forwards_struct, index=range(1, span + 1), dtype="float64")


def create_swap_struct(
    rfr: pd.Series(dtype="float64") = None, additional_swaps: dict = {}
) -> pd.Series(dtype="float64"):
    """
    Creates a swap structure.

    Args:
        rfr (pd.Series, optional): The risk-free rate term structure. Defaults to None.
        additional_swaps (dict, optional): Additional swaps to be included. Defaults to {}.

    Returns:
        pd.Series: The swap structure.
    """
    swap_struct = OrderedDict()
    denom = 0
    for duration in range(1, 21):
        rate = rfr[duration]
        denom += (1 + rate) ** (-duration)
        swap_struct[duration] = (1 - (1 + rate) ** (-duration)) / denom
    for key in additional_swaps.keys():
        swap_struct[key] = additional_swaps[key] - CRA
    return pd.Series(
        index=swap_struct.keys(), data=swap_struct.values(), dtype="float64"
    )


def forwardstruct2termstruct(
    forward_struct: pd.Series(dtype="float64"),
) -> pd.Series(dtype="float64"):
    """
    Converts a forward rate structure to a term structure.

    Args:
        forward_struct (pd.Series): The forward rate structure.

    Returns:
        pd.Series: The term structure.
    """
    alt_term_struct = pd.Series(index=forward_struct.index, dtype="float64")
    alt_term_struct[1] = forward_struct[1]
    previous_forward = 1 + alt_term_struct[1]
    for i in range(2, len(forward_struct) + 1):
        alt_term_struct[i] = (previous_forward * (1 + forward_struct[i])) ** (1 / i) - 1
        previous_forward = (1 + alt_term_struct[i]) ** i
    return pd.Series(data=alt_term_struct, index=forward_struct.index, dtype="float64")
