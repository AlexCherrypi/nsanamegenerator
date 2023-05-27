from defusedxml.minidom import parseString
import gzip 
import requests
from random import randint
import os

startingDir = './words/'


url = 'https://en-word.net/static/english-wordnet-2022.xml.gz'
download = requests.get(url).content
del url
xml = gzip.decompress(download).decode("utf-8")
del download
file = parseString(xml)
del xml
lemmas = file.getElementsByTagName('Lemma')
del file
words = dict()

for lemma in lemmas:
    pos  = lemma.getAttribute('partOfSpeech')
    word = lemma.getAttribute('writtenForm')
    if not word.isdigit() and len(word) > 2:
        words.setdefault(pos,set())
        words[pos].add(word)
        name = pos
        if ' ' in word:
            name = name+'c'
            words.setdefault(pos+'c',set()) # c for combined 
            words[pos+'c'].add(word)
        else: 
            name = name+'s'
            words.setdefault(pos+'s',set()) # s for single 
            words[pos+'s'].add(word)

        if '-' in word:
            name = name+'d'
            words.setdefault(pos+'d',set()) # d for dash
            words[pos+'d'].add(word)

        if any(char.isupper() for char in word):
            name = name+'u'
            words.setdefault(pos+'u',set()) # u for upper 
            words[pos+'u'].add(word)
        else: 
            name = name+'l'
            words.setdefault(pos+'l',set()) # l for lower 
            words[pos+'l'].add(word)

        words.setdefault(name,set()) # combined
        words[name].add(word)
del lemmas

for  key, value in words.items():
    if not os.path.exists(startingDir+key):
        os.makedirs(startingDir+key, exist_ok=True)
        pos = 0
        for word in words[key]:
            with open(startingDir+key+'/'+str(pos)+'.txt', 'w') as f:
                f.write(word)
            pos = pos + 1

