from defusedxml.ElementTree import fromstring
import gzip
import requests
import os
import re
import datetime
from wordinfo import HURTFUL_WORDS, Entry, Synset, WordInfo, blocked, lists

startingDir = './website/words/'


def findDownloadUrl():
    # The asset name contains the release year, which is not necessarily the current year,
    # so look up the actual file name of the latest release.
    try:
        release = requests.get('https://api.github.com/repos/globalwordnet/english-wordnet/releases/latest', timeout=60)
        release.raise_for_status()
        for asset in release.json()['assets']:
            if re.fullmatch(r'english-wordnet-\d{4}\.xml\.gz', asset['name']):
                return asset['browser_download_url']
        print("No matching asset found in latest release, probing years instead")
    except requests.RequestException as e:
        print("Could not query latest release ("+str(e)+"), probing years instead")
    # Fallback: try the last few years, newest first
    for year in range(datetime.date.today().year, datetime.date.today().year - 6, -1):
        candidate = 'https://github.com/globalwordnet/english-wordnet/releases/latest/download/english-wordnet-'+str(year)+'.xml.gz'
        if requests.head(candidate, allow_redirects=True, timeout=60).ok:
            return candidate
    raise RuntimeError("Could not find a WordNet download")


def writeList(key, wordList, usable=None):
    os.makedirs(startingDir+key, exist_ok=True)
    print("Generating files for key '"+key+"' in '"+os.path.abspath(startingDir+key)+"'...")
    pos = 0
    for word in wordList:
        with open(startingDir+key+'/'+str(pos)+'.txt', 'w', encoding="utf-8") as f:
            f.write(word)
        pos = pos + 1
    with open(startingDir+key+'/len.txt', 'w') as f:
            f.write(str(pos))
    if usable is not None:
        # the first words are fit to show, the rest are slurs, plurals and the like
        with open(startingDir+key+'/usable.txt', 'w') as f:
                f.write(str(usable))


url = findDownloadUrl()
print("Downloading from '"+ url +"'")
response = requests.get(url, timeout=600)
response.raise_for_status()
download = response.content
del response
print("Download from '"+ url +"' finished")
del url
print("Decompressing ...")
xml = gzip.decompress(download).decode("utf-8")
del download
print("Parsing xml ...")
root = fromstring(xml)
del xml
print("Reading words and meanings ...")
synsets = dict()
for synset in root.iter('Synset'):
    texts = [element.text or '' for element in synset if element.tag in ('Definition', 'Example')]
    synsets[synset.get('id')] = Synset(synset.get('lexfile'), ' '.join(texts), synset.get('members', '').split(),
                                       [(relation.get('relType'), relation.get('target')) for relation in synset.iter('SynsetRelation')])
entries = list()
for entry in root.iter('LexicalEntry'):
    lemma = entry.find('Lemma')
    senses = [(sense.get('id'), sense.get('synset'),
               [(relation.get('relType'), relation.get('target')) for relation in sense.iter('SenseRelation')])
              for sense in entry.iter('Sense')]
    entries.append(Entry(lemma.get('writtenForm'), lemma.get('partOfSpeech'), lemma.find('Pronunciation') is not None, senses))
del root

print("Finding and sorting words ...")
words = dict()
for entry in entries:
    if not entry.word.isdigit() and len(entry.word) > 3:
        for key in lists(entry.word, entry.pos):
            words.setdefault(key, set())
            words[key].add(entry.word)

# Extra lists per category of the main meaning (nsgl-animal, nsgl-food, ...) and
# for moods and vulgar words (asl-mood, nsgl-vulgar), see wordinfo.py. They are
# sorted from the best known to the most obscure word, so the website can pick
# among the best known ones only. Words that may not be shown from a list come
# last, after the number of words in usable.txt: slurs, plurals and the like,
# and vulgar words except in the vulgar lists.
print("Finding categories, moods and vulgar words ...")
info = WordInfo(entries, synsets)
del entries, synsets
extraWords = dict()
for word, pos in info.senses:
    if not word.isdigit() and len(word) > 3:
        for extra in info.extra_lists(word, pos):
            for key in lists(word, pos):
                extraWords.setdefault(key+'-'+extra, list())
                extraWords[key+'-'+extra].append((word, pos))
usable = dict()
for key, value in extraWords.items():
    extra = key.split('-', 1)[1]
    value.sort(key=lambda entry: info.rank(entry[0], entry[1], extra))
    extraWords[key] = [word for word, pos in value]
    usable[key] = sum(info.is_usable(word, pos, extra) for word, pos in value)
print("For example, the best known nouns per category:")
for key in sorted(extraWords):
    if key.startswith('nsgl-') or key in ('asl-mood', 'asl-vulgar'):
        print("  "+key+": "+', '.join(extraWords[key][:12]))

# Slurs that two harmless words make up (porch + monkey), as hashes so that
# the website can pick again instead of showing one.
hurtful = {word for word, pos in info.senses if info.is_hurtful(word, pos)} | HURTFUL_WORDS
harmless = {word.lower() for word, pos in info.senses if not re.search('[ -]', word) and not info.is_hurtful(word, pos)}
blockedHashes = blocked(hurtful, harmless)
print("Blocking "+str(len(blockedHashes))+" slurs made of two harmless words")

print("Generating files ...")
os.makedirs(startingDir, exist_ok=True)
with open(startingDir+'blocked.txt', 'w') as f:
    f.write('\n'.join(blockedHashes))
for key, value in words.items():
    writeList(key, value)
for key, value in extraWords.items():
    writeList(key, value, usable[key])

print("Finished!")
