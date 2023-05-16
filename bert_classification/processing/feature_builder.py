class FeatureBuilder:

    def __init__(self, columns):
        self.columns = columns

    def get_X(self, dataset):
        X = '[CLS]'+ dataset[f'{self.columns[0]}_1']
        for i in range(1, len(self.columns)):
            X = X + ' ' + dataset[f'{self.columns[i]}_1']
        X = X + ' [SEP]'
        for i in range(len(self.columns)):
            X = X + ' ' + dataset[f'{self.columns[i]}_2']
        X = X + ' [SEP]'
        return X.to_list()

    def get_y(self, dataset):
        return dataset['match_type'].to_list()