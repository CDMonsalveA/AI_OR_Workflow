"""module with the artificial intelligence functions
    ZeroR: predict the most common class
    OneR: predict the most common class for each feature
    Naive Bayes: classfier based on Bayes Theorem
    Decision Tree: classifier based on a tree structure
    Linear Discriminant Analysis: classifier based on the \
        Fisher's linear discriminant
    Logistic Regression: classifier based on the logistic function
    Multiple Linear Regression: regression based on the linear function
    K-Nearest Neighbors: classifier for linear and non-linear data \
        based on the distance between points
    Support Vector Machine: classifier for linear and non-linear data \
        based on the distance between points
    Agglomerative Hierarchical Clustering: clustering based on the \
        distance between points
    Stepwise Optimal Hierarchical Clustering: clustering for linear and \
        non-linear data based on the distance between points
    Self-Organizing Map: clustering based on the distance between points
    Artificial Neural Network: general structure for a neural network \
        with n layers and m neurons
"""
import pandas as pd

def zero_r(train: pd.DataFrame, target: str, test=None, show_accuracy=False):
    """
    Zero Rule Algorithm for classification

    Parameters
    ----------
    train: pandas DataFrame
        training set
    target: str
        target variable
    test: pandas DataFrame
        test set, if None, returns the accuracy with the training set
    show_accuracy: bool
        if True, returns the accuracy of the prediction

    Returns
    -------
    prediction:
        prediction for the target variable
    accuracy: float
        accuracy of the prediction if show_accuracy is True
    """
    