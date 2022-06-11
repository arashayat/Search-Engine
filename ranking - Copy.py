from lib2to3.pgen2 import token
from urllib import request
from flask import Flask
from flask import render_template
from flask import request
from PersianStemmer import PersianStemmer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import pickle
import string

app = Flask(__name__)

# initialize the stemmer
p_stemmer = PersianStemmer() # persian
e_stemmer = PorterStemmer()

with open('url_index_dic.pkl', 'rb') as f:
    url_index = pickle.load(f)    

with open('title_index_dic.pkl', 'rb') as f:
    title_index = pickle.load(f)

with open('body_index_dic.pkl', 'rb') as f:
    body_index = pickle.load(f)




@app.route("/", methods= ['GET', 'POST'])
def home(name = None):
    if request.method == 'GET':
       
        return render_template('Index.html', name = name)


    
@app.route("/results", methods= ['GET', 'POST'])
def result():
    # get the query from prev page
    query = request.args.get('sbtn')
    query = query.split()

    # check if query is in certain domain
    if query[0] == 'site:':
        host = query[1]
        ranking(' '.join(query[2:]))

    else:
        ranking(' '.join(query))

    



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



def ranking(query):
    # define the constants
    ALPHA = 9
    s_phrase = []
    BETA = 1
    s_bool = []
    GAMMA = 9
    s_title = []
    DELTA = 1
    s_body = []

    # preprocess
    try:
        token_lst = preprocess_string(query)
    except:
        token_lst = preprocess_string(str(query))


def calculate_scores(index, tokens):
    scores = {}

    # calculate bool scores
    for term in tokens:
        # if term not indexed
        if term not in index:
            continue

        # for every document in index with term in it calculate bool score
        for doc, positions in index[term][1].items():
            # if score already existing just increment
            if doc in scores:
                scores[doc][0] += len(positions)

            # if score doesn't exist
            else:
                scores[doc] = [len(positions), 0]

        
    # for every document in index with first term in it calculate phrase score
    if tokens[0] in index:
        for doc, positions in index[tokens[0]][1].items():

            # for every position of doc that term 1 exists in check full phrase
            for pos in positions:

                # if phrase exists increment score
                if(check_phrase(tokens, doc, pos, index)):
                    if doc in scores:
                        scores[doc][1] += 1
                    
                    else:
                        scores[doc] = [0, 1]

    

def check_phrase(r_tokens, doc, pos, index):
    
    # if phrase is not fully checked until the end
    # check the remaining of phrase
    if len(r_tokens) >= 2:
        # return false if term not indexed
        if r_tokens[1] not in index:
            return False
            
        # if next term exists in the document
        if doc in index[r_tokens[1]][1]:
            pass
        else:
            return False

    # if the phrase is fully matched
    else:
        return True
