from lib2to3.pgen2 import token
from random import betavariate
from urllib import request
from flask import Flask
from flask import render_template
from flask import request
from PersianStemmer import PersianStemmer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import pickle
import time
import string
import math
import pandas as pd

app = Flask(__name__)

# initialize the stemmer
p_stemmer = PersianStemmer() # persian
e_stemmer = PorterStemmer()

# define the weights for ranking
ALPHA = 15 # phrase weight
BETA = 1 # bool weight
GAMMA = 9 # title weight
DELTA =  1 # body weight

with open('url_index_dic.pkl', 'rb') as f:
    url_index = pickle.load(f)    

with open('title_index_dic.pkl', 'rb') as f:
    title_index = pickle.load(f)

with open('body_index_dic.pkl', 'rb') as f:
    body_index = pickle.load(f)

docs_data = pd.read_csv('Parsed_pages.csv', index_col=0)




@app.route("/", methods= ['GET', 'POST'])
def home(name = None):
    if request.method == 'GET':
       
        return render_template('Index.html', name = name)


    
@app.route("/results", methods= ['GET', 'POST'])
def result():
    st = time.time()
    # get the query from prev page
    query = request.args.get('sbtn')
    query = query.split()
    host = False

    # check if query is in certain domain
    if query[0] == 'site:':
        host = query[1]
        query = query[2:]

    # preprocess the query
    query = preprocess_string(str(query))
    
    # find all the results
    title_results = find_results(query, title_index, host)
    body_results = find_results(query, body_index, host)
    all_results = list(set(body_results + title_results))

    if len(all_results) == 0:
        return render_template('results.html', data = [0, 0])


    s_phrase_title = {doc:1 for doc in all_results}
    s_bool_title = s_phrase_title.copy()
    s_phrase_body = s_phrase_title.copy()
    s_bool_body = s_phrase_title.copy()

    # rank the results
    cal_scores(query, title_results, title_index, s_phrase_title, s_bool_title)     
    cal_scores(query, body_results, body_index, s_phrase_body, s_bool_body)


    s_final = {doc:cal_final_score(s_phrase_title[doc], s_bool_title[doc], s_phrase_body[doc], s_bool_body[doc]) for doc in all_results}
    s_final = [k for k, v in sorted(s_final.items(), key=lambda item: item[1], reverse=True)]

    for pos, docID in enumerate(s_final):
        doc = {}
        doc['URL'] = docs_data.loc[docID]['URL']
        doc['title'] = docs_data.loc[docID]['Title']
        doc['body'] = docs_data.loc[docID]['Body']
        s_final[pos] = doc

    s_final.insert(0, len(s_final))
    ft = time.time()
    s_final.insert(1, '{:.3f}'.format(ft - st))
    s_final.insert(0, ' '.join(query))
    
    
    # print('time spent to index pages: ', '{:.2f}'.format(ft - st))
    return render_template('results.html', data = s_final)


def preprocess_string(doc_string):

    # convert arabic to persian
    doc_string = doc_string.replace('ك', 'ک')
    doc_string = doc_string.replace('ي', 'ی')

    # Tokenize
    token_list = word_tokenize(doc_string)

    # remove punctuations
    punctuations = string.punctuation
    punctuations  += '،–'
    trans_table = str.maketrans('', '', punctuations)
    stripped_words = [word.translate(trans_table) for word in token_list]
    token_list = [str for str in stripped_words if str]
 
    # Change to lowercase.
    token_list =[word.lower() for word in token_list]

    # stem list
    token_list = [e_stemmer.stem(p_stemmer.stem(word)) for word in token_list]

    return token_list

def find_results(query, index, host):

    docs = []
    for term in query:
        # get all results for index
        if term in index:
            res = set(index[term][1].keys())
        
            # result found if term in index
            docs.append(list(res))

    # if hostname is specified
    if host != False:
        if host in url_index:
            docs.append(url_index[host])
        else:
            docs.append([])
    
    # get result if all terms and the hostname match
    if len(docs) > 0:
        return sorted(set.intersection(*map(set, docs)))
    else:
        return docs
    
def cal_scores(query, results, index, s_phrase, s_bool):
    
    # calulate bool score for each doc
    for term in query:

        for docID in results:
            # if term in document
            if docID in index[term][1]:
                s_bool[docID] += len(index[term][1][docID])

    # calculate phrase score for each doc
    for docID in results:

        # check phrase for all occurances of the first term
        for pos in index[query[0]][1][docID]:

            if is_phrase(pos,index, query, docID):
                s_phrase[docID] += 1
    
def is_phrase(pos, index, query, docID):

    # check if all terms of phrase is in doc
    for term_pos, term in enumerate(query):
        # if the term is not in the (position of first term) + (position of current term in query) 
        if (pos + term_pos) not in index[term][1][docID]:
            return False
    
    return True

def cal_final_score(ph_title, bool_title, ph_body, bool_body):
    return GAMMA*(ALPHA*math.log(ph_title) + BETA*math.log(bool_title)) + DELTA*(ALPHA*math.log(ph_body) + BETA*math.log(bool_body))