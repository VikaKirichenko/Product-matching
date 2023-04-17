import re
import ast
import nltk
import re
import string

nltk.download('stopwords')
stop_words = nltk.corpus.stopwords.words('russian')

word_tokenizer = nltk.WordPunctTokenizer()

def process_data(text):
    text = text.lower().replace("/"," ").replace("+"," ").replace('смартфон',"").replace('гб','gb').strip()
    return text
    
def process_price(price):
    price = price.split("\n")[0]
    return price

def process_description(desc):
    # print(desc)
    if desc is not None:
        desc = desc.lower().replace('смартфон',"").replace('гб','gb').replace(', ',' ')
        desc = re.sub(r'[\-\:]'," ",desc)
        desc = re.sub(r'[!?"]',"",desc)
        desc = re.sub(r'\s+'," ",desc)

        tokens     = desc.split(" ") # splits the text into tokens (words)
        # еще бы хорошо все это привести в нормальную форму лемматизировать
        # remove punct and stop words from tokens
        tokens = [word for word in tokens if (word not in string.punctuation and word not in stop_words)]
        return " ".join(tokens)
    return ""

def preprocess_columns(df_all):
    df_all['title'] = df_all['title'].apply(process_data)
    df_all['brand'] = df_all['brand'].apply(process_data)
    df_all['description'] = df_all['description'].fillna("")
    df_all['description'] = df_all['description'].apply(process_description)

    # replace empty title with first 5 words in description
    df_all.loc[df_all['title'] == "", ['flag']] = 'nothing'
    df_all.loc[df_all['title'] != "", ['flag']] = 'full'
    df_all['title'].mask(df_all['title'] == '', df_all['description'].apply(lambda x: " ".join(x.split()[:5])), inplace=True)
    # end of replacing

    df_all = df_all[df_all['title'] != ""]
    df_all = df_all.drop_duplicates(subset=['title','brand','price','description'])

    return df_all

def process_spec(spec):
    all_info = {}
    spec = ast.literal_eval(spec)
    for block in spec:
        for item in spec[block]:
            if len(item) > 1:
                key = item[0].lower()
                val = item[1].lower()
                all_info[key] = val

    
    new_all_info = {}
    for info in all_info:
        if re.search(r'(модель|объем|предмета|вес|диагональ|страна|камер|емкость аккумулятора|sim|код производителя)', info.lower()):
            new_all_info[info] = all_info[info].replace('"',"")

    myKeys = list(new_all_info.keys())
    myKeys.sort()
    sorted_dict = {i: new_all_info[i] for i in myKeys}

    return str(sorted_dict)

def reduce_spec(df,column):
    df[column] = df[column].apply(process_spec)
    df.to_csv('data/all_wb_dns_smartphones_reduce_spec.csv')
    
    return df






