from sklearn.metrics import jaccard_score
from sklearn.metrics.pairwise import cosine_similarity


def damerau_levenshtein_distance(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1, lenstr1+1):
        d[(i, -1)] = i+1
    for j in range(-1, lenstr2+1):
        d[(-1, j)] = j+1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i-1, j)] + 1,  # deletion
                d[(i, j-1)] + 1,  # insertion
                d[(i-1, j-1)] + cost,  # substitution
            )
            if i and j and s1[i] == s2[j-1] and s1[i-1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i-2, j-2] + cost)  # transposition

    return d[lenstr1-1, lenstr2-1]


def calculate_sim(row, feature_combination):
    if feature_combination in ['title']:
        return jaccard_score(row[feature_combination+'_wordocc_1'], row[feature_combination+'_wordocc_2'], average='weighted')
    elif feature_combination == 'brand':
        return damerau_levenshtein_distance(row['brand_1'], row['brand_2'])
    elif feature_combination in ['description', 'specification_values']:
        # print(row[feature_combination + '_wordocc_2'])
        similarities = cosine_similarity(
            row[feature_combination + '_wordocc_1'],
            row[feature_combination + '_wordocc_2'])
        return similarities[0][0]
    elif feature_combination == 'price':
        return abs(float(row[feature_combination+'_1']) - float(row[feature_combination+'_2']))/max(float(row[feature_combination+'_1']), float(row[feature_combination+'_2']))
