from pathlib import Path
from typing import List, Optional, Union

import numpy as np

from frame import Frame, MissingFrame


def calculate_time_series(
    feature: str,
    frames: List[Union[Frame, MissingFrame]],
    audio_file: Path,
    pitch_gender: Optional[str] = None,
) -> List[float]:
    """
    Generate a time series of the frames values for the feature given
    """
    time_series: List[float] = []
    for frame in frames:
        frame_time_series_value = frame.calculate_feature_value(
            feature, audio_file, pitch_gender
        )
        time_series.append(frame_time_series_value)
    return time_series


def _sqrt_product_of_the_values_sum_square_distances(
    a_values_distances_to_mean: List[float], b_values_distances_to_mean: List[float]
) -> float:
    """
    TO-DO
    """
    a_values_sum_distance_square: float = np.sum(
        np.power(a_values_distances_to_mean, 2)
    )

    b_values_sum_distance_square: float = np.nansum(
        np.power(b_values_distances_to_mean, 2)
    )

    sqrt_product: float = np.sqrt(
        np.multiply(a_values_sum_distance_square, b_values_sum_distance_square)
    )
    return sqrt_product


def _lags_sum_lagged_distances_products(
    a_values_distances_to_mean: List[float],
    b_values_distances_to_mean: List[float],
    lags: int,
) -> List[float]:
    """
    TO-DO
    """
    amount_of_tama_frames = len(a_values_distances_to_mean)

    lags_sum_lagged_distances_products = []
    for lag in range(lags + 1):
        lagged_distances_products = []
        for i in range(lag, amount_of_tama_frames):
            lagged_distance_product = np.multiply(
                a_values_distances_to_mean[i], b_values_distances_to_mean[i - lag]
            )
            lagged_distances_products.append(lagged_distance_product)

        sum_lagged_distances_products = np.nan
        # Ignore lagged_distances_products if there are less than four non-missing terms
        if (
            lagged_distances_products
            or np.count_nonzero(~np.isnan(lagged_distance_product)) < 4
        ):
            sum_lagged_distances_products = np.nansum(lagged_distances_products)
        lags_sum_lagged_distances_products.append(sum_lagged_distances_products)

    return lags_sum_lagged_distances_products


def calculate_sample_correlation(
    time_series_a: List[float],
    time_series_b: List[float],
    lags: int,
) -> List[float]:
    """
    Calculate the correlations between two series as one of them is lagged

    ----
    Intuitively,
    it can be interpreted similarly to Pearson’s correlation coeffi-
    cient between a time-series and a lagged version of another one,
    which means that its value varies from −1 to 1.
    Each value returned can be interpreted as an indication
    of how much a speaker converged (diverged) in a task in
    terms of the behavior of a/p feature φ to the behavior her partner
    had h frames before, where h is the number of lags.
    """
    if not time_series_a or not time_series_b:
        raise ValueError("Time series can not be empty")

    time_series_a_mean = np.nanmean(time_series_a)
    time_series_b_mean = np.nanmean(time_series_b)

    a_values_distances_to_mean: List[float] = (
        np.array(time_series_a) - time_series_a_mean
    )
    print(f"A's distances to its mean: {a_values_distances_to_mean}")
    b_values_distances_to_mean: List[float] = (
        np.array(time_series_b) - time_series_b_mean
    )
    print(f"B's distances to its mean: {b_values_distances_to_mean}")

    sqrt_product_of_the_values_sum_square_distances: float = (
        _sqrt_product_of_the_values_sum_square_distances(
            a_values_distances_to_mean, b_values_distances_to_mean
        )
    )
    print(f"Denominator {sqrt_product_of_the_values_sum_square_distances}")
    lags_sum_lagged_distances_products: List[
        float
    ] = _lags_sum_lagged_distances_products(
        a_values_distances_to_mean, b_values_distances_to_mean, lags
    )

    print(f"Numerators: {lags_sum_lagged_distances_products}")
    return (
        np.array(lags_sum_lagged_distances_products)
        / sqrt_product_of_the_values_sum_square_distances
    )
