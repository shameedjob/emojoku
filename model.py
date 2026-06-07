from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from gensim.utils import simple_preprocess
import gensim.downloader
import numpy
import random
import json
import os

def cosine_similarity(v1, v2):
    return numpy.dot(v1, v2) / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2))

#Download model
MODEL_PATH = "/tmp/glove-wiki-gigaword-100/model"

os.makedirs("/tmp/glove-wiki-gigaword-100", exist_ok=True)

if not os.path.exists(MODEL_PATH):
    m = gensim.downloader.load("glove-wiki-gigaword-100")
    m.save(MODEL_PATH)
else:
    model = KeyedVectors.load(MODEL_PATH)
# words = [f[:-1] for f in open("./data/contexto_words_list.txt", "r").readlines()]

def get_similarity(a, b):
    return float(model.similarity(a, b))

def user_guess(guess, i)->str:
    return {"word": guess,
                        "answer": words[i],
                        "sim": float(model.similarity(guess, words[i])), 
                        "win": float(model.similarity(guess, words[i])==1.0)}

def guess_value(guess, hidden:str)->str:
    return {"word": guess,
                        "answer": hidden,
                        "sim": float(model.similarity(guess, hidden)), 
                        "win": float(model.similarity(guess, hidden)==1.0)}

def get_random_hidden():
    return random.choice(words)

def get_values(guess1, guess2)->str:
    v1 = model[guess1]
    v2 = model[guess2]
    v_avg = numpy.mean([v1, v2], 0)

    similarities = []
    similarities.append(float(model.similarity(guess1, chosen_word)))
    similarities.append(float(model.similarity(guess2, chosen_word)))
    similarities.append(float(cosine_similarity(v_avg, model[chosen_word])))

    # print("Avg Vector", )
    words = model.similar_by_vector(v_avg, topn=4)
    guess_average = ""
    for w in words:
        if not (w==guess1 and w==guess2):
            guess_average = w
            pass

    
    d = {"similarities": similarities, "win": guess1==chosen_word or guess2==chosen_word}
    d["guess"] = guess_average[0]

    if d["win"]:
        d["word"] = chosen_word
    return json.dumps(d)

def list_joined_sem(words:list[str], amt=5):
    vecs = numpy.mean(words, 1)
    
def subtract(subtrahend:str|numpy.ndarray, *minuends:str|numpy.ndarray):
    return calculate(add_words=[subtrahend], sub_words=list(minuends))

def add(*addends:str|numpy.ndarray):
    # print(*addends)
    return calculate(add_words=list(addends))

def calculate(add_words:list[str|numpy.ndarray] = [], sub_words:list[str|numpy.ndarray] = []):
    add_vecs = []
    sub_vecs = []

    for word_list, vec_list in [[add_words, add_vecs], [sub_words,sub_vecs]]:
        for w in word_list:
            # print(item, w)
            vec:numpy.ndarray =[]
            if type(w) is str:
                vec = model[w]
            else:
                vec = w
            vec_list.append(normalize(vec))
    
    vec = numpy.sum(add_vecs, axis=0)-numpy.sum(sub_vecs, axis=0)
    # vec = normalize(vec)
    return {'vec': vec, 'words': model.similar_by_vector(vec, topn=5), 'words_2':model.most_similar(positive=add_words, negative=sub_words)}

def normalize(v):
    return v / numpy.linalg.norm(v)

def get_word_vec(term:str)->numpy.ndarray:
    return model[term]

def get_neighborhood(term:numpy.ndarray|str, k:int):
    if type(term) is str:
        vector = model[term]
    else:
        vector = term
    
    return model.similar_by_vector(vector, topn=k)