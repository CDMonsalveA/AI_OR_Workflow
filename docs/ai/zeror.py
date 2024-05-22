class ZeroR:
    """
    Zero Rule Algorithm (ZeroR)

    This algorithm is a baseline algorithm that predicts the majority class
    for all instances in the test dataset. This algorithm is useful as a
    benchmark for other algorithms and also for quick checks to see if
    classification accuracy is a problem with the problem or with the
    dataset itself.

    First published by R. Holte in 1993 in the paper "Very Simple Classification
    Rules Perform Well on Most Commonly Used Datasets" (see references).
    
    References:
        - R. Holte. Very simple classification rules perform well on most
          commonly used datasets. Machine Learning, 11:63-90, 1993.

    """