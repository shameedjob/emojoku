import numpy
import json
import model

def cosine_similarity(v1, v2):
    return numpy.dot(v1, v2) / (numpy.linalg.norm(v1) * numpy.linalg.norm(v2))

emoji_map = {}
emoji_names = {}
with open('emoji.json', 'r') as file:
    js_dict = json.load(file)
    for emoji in js_dict:
        vecs = []
        try:
            cleaned = model.clean_phrase(emoji["name"])
            for w in cleaned.split(" "):
                vecs.append(model.model[w])
            output = model.calculate(add_words=vecs)
            emoji_map[emoji["char"]] = output['vec']
            emoji_names[emoji["char"]] = cleaned
        except:
            print(cleaned, emoji['char'])
            continue

def get_emoji_from_line(line):
    vecs = []
    for w in line.split(' '):
        try:
            vecs.append(model.model[w])
        except:
            continue
    if len(vecs) < 0:
        return None
    v = vecs[0]
    # if len
    for x in vecs[1:]:
        v = v+x
    # merged = numpy.sum(vecs, axis=1)
    vec_output = model.calculate(add_words=[v])['vec']
    emojis = []
    for e in emoji_map:
        emojis.append([
            model.cosine_similarity(emoji_map[e], vec_output),
            e
        ])
    emojis = sorted(emojis, reverse= True, key=lambda x:x[0])

    return emojis[0][1]


