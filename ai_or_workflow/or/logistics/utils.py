"""Utilities that use mainly OR-Tools."""

import numpy as np


# Function to propose a N number of clusters using operations research
def n_clusters_proposal(
    D_ij: np.ndarray,
    M: int | None,
    sample_size: float = 0.1,
    lambda_: float | None = None,
    random_seed: int = 42,
    time_limit: int = 60,
) -> tuple[int, float, str]:
    """Function that proposes a number of clusters for the division of points
    using the structure of the UFLP (Uncapacitated Facility Location Problem).
    """
    pass
