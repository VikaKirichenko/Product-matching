import pandas as pd

from utils import process_spec2, tokenize_lemmatize_text


def load_corpus():
    df = pd.read_csv('data/dataset_to_model.csv')
    return df

def preprocess_corpus(df_result):

    df_result = df_result.fillna("")
    features = ['title','brand','description']
    for feature in features:
        df_result[feature + '_1'] = df_result[feature + '_1'].apply(tokenize_lemmatize_text)
        df_result[feature + '_2'] = df_result[feature + '_2'].apply(tokenize_lemmatize_text)

    df_result['specification_values_1'] = df_result['specifications_1'].apply(process_spec2)
    df_result['specification_values_2'] = df_result['specifications_2'].apply(process_spec2)

    df_result['title_1'].mask(df_result['title_1'] == '', df_result['description_1'].apply(lambda x: " ".join(x.split()[:5])), inplace=True)
    df_result['title_2'].mask(df_result['title_2'] == '', df_result['description_2'].apply(lambda x: " ".join(x.split()[:5])), inplace=True)

    return df_result

def save_corpus(df_result):
    df_result.to_csv('data/dataset_to_model_preprocessed2.csv',index = False)

def main():
    df_result = load_corpus()
    print('corpus loaded')
    df_result = preprocess_corpus(df_result)
    print('corpus processed')
    save_corpus(df_result)
    print('corpus saved')


if __name__ == '__main__':
    main()
