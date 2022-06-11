
from lib2to3.pgen2 import token
from pydoc import doc
from urllib import request
from flask import Flask
from flask import render_template
from flask import request
from PersianStemmer import PersianStemmer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import pickle
import string




# initialize the stemmer
p_stemmer = PersianStemmer() # persian
e_stemmer = PorterStemmer()




# load indexes
with open('url_index_dic.pkl', 'rb') as f:
    url_index = pickle.load(f)    

with open('title_index_dic.pkl', 'rb') as f:
    title_index = pickle.load(f)

with open('body_index_dic.pkl', 'rb') as f:
    body_index = pickle.load(f)


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




def find_results(query, index, host = False):

    docs = []
    for term in query:
        # get all results for index
        if term in index:
            res = set(index[term][1].keys())
        
            # result found if term in title or body
            docs.append(list(res))

    # if hostname is specified
    if host != False:
        if host in url_index:
            docs.append(url_index[host])
        else:
            docs.append([])
    
    # get result if all terms and the hostname match
    return sorted(set.intersection(*map(set, docs)))

def ranking(query, results, index):

    # define the constants
    s_phrase = {doc:0 for doc in results}
    
    s_bool = {doc:0 for doc in results}
    
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
    
    return s_bool, s_phrase


def is_phrase(pos, index, query, docID):
    # check if all terms of phrase is in doc
    for term_pos, term in enumerate(query):
        # if the term is not in the (position of first term) + (position of current term in query) 
        if (pos + term_pos) not in index[term][1][docID]:
            return False
    
    return True

                    



    

query = 'site: abu.ut.ac.ir پردیس ابوریحان دانشگاه تهران'
query = query.split()

    # check if query is in certain domain
if query[0] == 'site:':
    host = query[1]
    title_results = find_results(query[2:], title_index, host)
    s_bool_title, s_phrase_title = ranking(query[2:], title_results, title_index)

else:
    title_results = find_results(query, title_index)
    s_bool_title, s_phrase_title = ranking(query, title_results, title_index)






print(s_bool_title, s_phrase_title)