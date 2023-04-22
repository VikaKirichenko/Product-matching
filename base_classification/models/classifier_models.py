import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import PredefinedSplit, RandomizedSearchCV
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

classifiers = {'NaiveBayes':  {'clf': BernoulliNB(),
                               'params': {}},
               'XGBoost': {'clf': xgb.XGBClassifier(random_state=42, n_jobs=4),
                           'params': {"learning_rate": [0.1, 0.01, 0.001],
                                      "gamma": [0.01, 0.1, 0.3, 0.5, 1, 1.5, 2],
                                      "max_depth": [2, 4, 7, 10],
                                      "colsample_bytree": [0.3, 0.6, 0.8, 1.0],
                                      "subsample": [0.2, 0.4, 0.5, 0.6, 0.7],
                                      "reg_alpha": [0, 0.5, 1],
                                      "reg_lambda": [1, 1.5, 2, 3, 4.5],
                                      "min_child_weight": [1, 3, 5, 7],
                                      "n_estimators": [100]}},
               'RandomForest':  {'clf': RandomForestClassifier(random_state=42, n_jobs=4),
                                 'params': {'n_estimators': [100],
                                            'max_features': ['sqrt', 'log2', None],
                                            'max_depth': [2, 4, 7, 10],
                                            'min_samples_split': [2, 5, 10, 20],
                                            'min_samples_leaf': [1, 2, 4, 8],
                                            'class_weight': [None, 'balanced_subsample']
                                            }},
               'DecisionTree':  {'clf': DecisionTreeClassifier(random_state=42),
                                 'params': {'max_features': ['sqrt', 'log2', None],
                                            'max_depth': [2, 4, 7, 10],
                                            'min_samples_split': [2, 5, 10, 20],
                                            'min_samples_leaf': [1, 2, 4, 8],
                                            'class_weight': [None, 'balanced']
                                            }},
               'LinearSVC':  {'clf': LinearSVC(random_state=42, dual=False),
                              'params': {'C': [0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000],
                                         'class_weight': [None, 'balanced']}},
               'LogisticRegression': {'clf': LogisticRegression(random_state=42, solver='liblinear'),
                                      'params': {'C': [0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000],
                                                 'class_weight': [None, 'balanced']}},
               }
