from defusedxml.minidom import parseString
import gzip 
import requests
import os
import re
import datetime

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
file = parseString(xml)
del xml
print("Finding Lemmas ...")
lemmas = file.getElementsByTagName('Lemma')
del file
words = dict()

print("Finding and sorting words ...")
for lemma in lemmas:
    pos  = lemma.getAttribute('partOfSpeech')
    word = lemma.getAttribute('writtenForm')
    if not word.isdigit() and len(word) > 3:
        words.setdefault(pos,set())
        words[pos].add(word)
        name = pos
        name2 = pos
        if ' ' in word:
            name = name +'c'
            name2 = name2 +'c'
            words.setdefault(pos+'c',set()) # c for combined 
            words[pos+'c'].add(word)
        else: 
            name = name +'s'
            name2 = name2 +'s'
            words.setdefault(pos+'s',set()) # s for single 
            words[pos+'s'].add(word)

        if '-' in word:
            name = name +'d'
            words.setdefault(pos+'d',set()) # d for dash
            words[pos+'d'].add(word)
        else: 
            name = name +'g'
            words.setdefault(pos+'g',set()) # g for no dash 
            words[pos+'g'].add(word)

        words.setdefault(name,set()) # combined
        words[name].add(word)

        if any(char.isupper() for char in word):
            name = name +'u'
            name2 = name2 +'u'
            words.setdefault(pos+'u',set()) # u for upper 
            words[pos+'u'].add(word)
        else: 
            name = name +'l'
            name2 = name2 +'l'
            words.setdefault(pos+'l',set()) # l for lower 
            words[pos+'l'].add(word)

        words.setdefault(name,set()) # combined
        words[name].add(word)
        words.setdefault(name2,set()) # combined
        words[name2].add(word)
del lemmas

print("Generating files ...")
for  key, value in words.items():
    os.makedirs(startingDir+key, exist_ok=True)
    print("Generating files for key '"+key+"' in '"+os.path.abspath(startingDir+key)+"'...")
    pos = 0
    for word in words[key]:
        with open(startingDir+key+'/'+str(pos)+'.txt', 'w', encoding="utf-8") as f:
            f.write(word)
        pos = pos + 1
    with open(startingDir+key+'/len.txt', 'w') as f:
            f.write(str(pos))

print("Finished!")

