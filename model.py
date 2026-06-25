import re
from gensim.models import Word2Vec
import gensim.downloader
import numpy
import os

def clean_phrase(phrase: str) -> str:
    phrase = re.sub(r"[^a-zA-Z0-9\s]", ' ', phrase)
    special_case = {
        'keycap': 'key cap',
        'merperson': 'fish person',
        'facepalming': 'face palming',
        'paperclips': 'paper clips',
        'selfie': 'self phone picture'
    }
    for key, value in special_case.items():
        phrase = phrase.replace(key, value)
    return re.sub(r'\s+', ' ', phrase).strip().lower()

def cosine_similarity(v1, v2):
    return numpy.dot(v1, v2) / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2))

#Download model
MODEL_PATH = "/tmp/glove-wiki-gigaword-50"

if not os.path.exists(MODEL_PATH):
    model = gensim.downloader.load("glove-wiki-gigaword-50") 
    model.save(MODEL_PATH)
else:
    from gensim.models import KeyedVectors
    model = KeyedVectors.load(MODEL_PATH)
# words = [f[:-1] for f in open("./data/contexto_words_list.txt", "r").readlines()]


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