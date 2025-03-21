"""Colection of functions for classification tasks.

Supported models:
- One Rule (OneR)
- Naive Bayes (GaussianNB, MultinomialNB, BernoulliNB, CategoricalNB)
- Decision Tree Classifier
- Random Forest Classifier
- Linear Discriminant Analysis (LDA)
- Logistic Regression
- Support Vector Classifier (SVC)
- K-Nearest Neighbors (KNN)
-"""

# Import clasification functions

# Random Forest Classifier
from sklearn.ensemble import (
    BaggingClassifier,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    StackingClassifier,
    VotingClassifier,
)

# OneR is a simple rule-based classifier that selects the attribute that best separates the classes.
# Naive Bayes
from sklearn.naive_bayes import (
    BernoulliNB,
    CategoricalNB,
    GaussianNB,
    MultinomialNB,
)

# Decision Tree Classifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier

# Linear Discriminant Analysis (LDA)
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis

# Logistic Regression
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV

