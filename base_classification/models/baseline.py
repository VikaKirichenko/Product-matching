import collections
import pickle
import time

import pandas as pd
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

from models.classifier_models import classifiers
from models.similarities import calculate_sim


def load_corpus():
    df = pd.read_csv('data/dataset_to_model_preprocessed.csv')
    return df


def vectorize_features(df_result):
    feature_combinations = ['title', 'brand',
                            'description', 'specification_values']
    count_vectorizers = {}
    words = {}
    for feature_combination in feature_combinations:
        all_left_strings = df_result[[
            'id_1', feature_combination + '_1']].copy()
        all_left_strings = all_left_strings.rename(
            columns={'id_1': 'id', feature_combination + '_1': feature_combination})
        all_right_strings = df_result[[
            'id_2', feature_combination + '_2']].copy()
        all_right_strings = all_right_strings.rename(
            columns={'id_2': 'id', feature_combination + '_2': feature_combination})
        all_unique_strings = pd.concat([all_left_strings, all_right_strings])
        all_unique_strings = all_unique_strings.drop_duplicates(subset='id')

        # learn vocabulary
        count_vectorizer = CountVectorizer(min_df=2, binary=True)
        count_vectorizer.fit(all_unique_strings[feature_combination])

        count_vectorizers[feature_combination] = count_vectorizer

        words[feature_combination] = count_vectorizer.get_feature_names_out()

        # apply binary word occurrence
        left_matrix = count_vectorizer.transform(
            df_result[feature_combination + '_1'])
        right_matrix = count_vectorizer.transform(
            df_result[feature_combination + '_2'])
        df_result[feature_combination +
                  '_wordocc_1'] = [x for x in left_matrix]
        df_result[feature_combination +
                  '_wordocc_2'] = [x for x in right_matrix]  # .toarray()

        # break
    with open('models/count_vectorizers.pickle', 'wb') as f:
        pickle.dump(count_vectorizers, f)
    return df_result


def get_sim_features_corpus(df_result):
    model_df = pd.DataFrame()
    model_df['pair_id'] = df_result['pair_id'].tolist()

    feature_combinations = ['title', 'brand',
                            'description', 'specification_values', 'price']
    for feature_combination in feature_combinations:
        print(feature_combination)
        model_df[feature_combination + ('_sim' if feature_combination not in ['price', 'brand'] else '_dist')
                 ] = df_result.apply(lambda row: calculate_sim(row, feature_combination), axis=1)
    model_df['match_type'] = df_result['match_type'].tolist()

    return model_df


def split_corpus(model_df):
    X = model_df.drop(columns=['match_type', 'pair_id'])
    y = [0 if match_type > 1 else 1 for match_type in model_df['match_type'].tolist()]

    return train_test_split(X, y, test_size=0.33, random_state=42)


def find_best_params_classifier_models(X_train, y_train):
    pos_neg = collections.Counter(y_train)
    pos_neg = round(pos_neg[0] / pos_neg[1])

    best_params = {}
    for k, v in classifiers.items():
        classifier = v['clf']
        if 'random_state' in classifier.get_params().keys():
            # потом можно сделать несколько итераций и делать разный random_state
            classifier = classifier.set_params(**{'random_state': 1})

        # add pos_neg ratio to XGBoost params
        if k == 'XGBoost':
            v['params']['scale_pos_weight'] = [1, pos_neg]
        # посм про параметр cv (не понимаю как его делать)
        model = RandomizedSearchCV(estimator=classifier, param_distributions=v['params'],
                                   random_state=42, n_jobs=4, scoring='f1', n_iter=500, pre_dispatch=8,
                                   return_train_score=True)
        start = time.time()
        model.fit(X_train, y_train)
        end = time.time()
        print((end - start)/60)

        parameters = model.best_params_

        print(k, parameters)
        best_params[k] = parameters

        if k == 'LogisticRegression' or k == 'LinearSVC':
            most_important_features = model.best_estimator_.coef_
            most_important_features = most_important_features[0]
        if k == 'RandomForest' or k == 'DecisionTree':
            most_important_features = model.best_estimator_.feature_importances_
        if k == 'NaiveBayes':
            word_importance = ''
        if k == 'XGBoost':
            most_important_features = model.best_estimator_.feature_importances_

        if k != 'NaiveBayes':
            print(most_important_features)
            # most_important_features = [abs(feat) for feat in most_important_features]
            # forest_importances = pd.Series(most_important_features, index=['title_sim','brand_dist','description_sim','specification_values_sim','price_dist'])

            # fig, ax = plt.subplots()
            # forest_importances.plot.bar(yerr=most_important_features, ax=ax)
            # ax.set_title("Feature importances using permutation on full model")
            # ax.set_ylabel("Mean accuracy decrease")
            # fig.tight_layout()
            # plt.show()

    with open('models/best_params.pickle', 'wb') as f:
        pickle.dump(best_params, f)

    return best_params


def get_best_model(best_params, X_train, X_test, y_train, y_test):

    best_model = {'name': "", 'model': "", 'f1_score': 0}

    for k, parameters in best_params.items():
        if k == 'LogisticRegression':
            learner = LogisticRegression(
                random_state=1, solver='liblinear', **parameters)
        elif k == 'NaiveBayes':
            learner = BernoulliNB()
        elif k == 'DecisionTree':
            learner = DecisionTreeClassifier(random_state=1, **parameters)
        elif k == 'LinearSVC':
            learner = LinearSVC(random_state=1, dual=False, **parameters)
        elif k == 'RandomForest':
            learner = RandomForestClassifier(
                random_state=1, n_jobs=4, **parameters)
        elif k == 'XGBoost':
            learner = xgb.XGBClassifier(random_state=1, n_jobs=4, **parameters)
        else:
            print('Learner is not a valid option')
            break
        print(k)
        model = learner
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        if f1_score(y_test, preds, average='macro') > best_model['f1_score']:
            best_model['name'] = k
            best_model['model'] = model
            best_model['f1_score'] = f1_score(y_test, preds, average='macro')

    with open('models/best_model.pickle', 'wb') as f:
        pickle.dump(best_model, f)

    return best_model


def main():
    df_result = load_corpus()
    df_result = vectorize_features(df_result)

    model_df = get_sim_features_corpus(df_result)
    model_df.to_csv('data/dataset_to_model_sim.csv', index=False)

    X_train, X_test, y_train, y_test = split_corpus(model_df)

    best_params = find_best_params_classifier_models(X_train, y_train)

    best_model = get_best_model(best_params, X_train, X_test, y_train, y_test)

    print(best_model['name'], best_model['f1_score'])


if __name__ == '__main__':
    main()
