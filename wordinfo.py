"""What the generator knows about a word besides its spelling.

WordNet has no word frequencies, but it describes every meaning of a word, and
that is enough to tell the funny words from the obscure ones:

- category:    the WordNet category of the word's main meaning (animal, food,
               person, artifact, ...). The meanings of a word are ordered from
               the most to the least common, so the first one is the main one.
- familiarity: how well known a word is. Common words show up a lot in the
               definitions and examples of other words, have many meanings and
               appear in many compounds (fox: fox terrier, flying fox, ...),
               while obscure ones don't (wicopy, haemoptysis).
- mood:        adjectives describing a mood or temper, like the ones in real
               codenames (EGOTISTICALGIRAFFE, IRATEMONK, SURLY SPAWN).
- vulgar:      crude, sexual and bathroom words (but no medical terms). They
               only show up in the vulgar lists, at the end of all others. The
               vulgar lists start with the hand-picked crude words, followed by
               the ones WordNet calls obscene, which are often milder (darn).
- hurtful:     slurs against groups of people and words about sexual
               orientation or abuse. They are no fun, so they always come last.
"""

import collections
import functools
import hashlib
import math
import re
from typing import NamedTuple


def lists(word, pos):
    """The lists a word belongs to, named after its part of speech and spelling.

    For example nsgl: noun, single word (c for combined words), no dash (d for
    dash) and lower case (u for upper case letters).
    """
    combined = 'c' if ' ' in word else 's'
    dash = 'd' if '-' in word else 'g'
    case = 'u' if any(char.isupper() for char in word) else 'l'
    return {pos, pos+combined, pos+dash, pos+case, pos+combined+dash, pos+combined+case, pos+combined+dash+case}


class Synset(NamedTuple):
    """A meaning, shared by all words that can express it."""
    lexfile: str      # e.g. noun.animal
    text: str         # definition and examples
    members: list     # ids of the lexical entries, e.g. oewn-fox-n
    relations: list   # (relType, target synset)


class Entry(NamedTuple):
    """A word of the dictionary with its meanings, most common first."""
    word: str
    pos: str
    pronounced: bool  # has a pronunciation, which only better known words have
    senses: list      # (sense id, synset id, [(relType, target sense)])


# Moods every child knows. Their WordNet neighbours (irate next to angry, smug,
# surly, petulant, ...) make up the mood adjectives.
MOOD_SEEDS = '''angry happy sad nervous proud shy jealous grumpy cheerful lazy sleepy curious greedy brave
timid lonely bored silly clumsy moody sneaky smug gloomy furious anxious friendly rude cranky paranoid
stubborn grouchy playful wistful pensive dreamy fussy surly sulky jolly grim awkward naughty cocky
bashful hungry tired restless'''.split()

# Crude words WordNet doesn't mark as obscene, and crude words for women, which
# are fine in a vulgar joke. Nouns and verbs, adjectives are listed below
# (tart is crude as a noun, but just sour as an adjective).
VULGAR_WORDS = set('''fart poop pee boob boobs booby booty butt butthole buttocks bum arse ass asshole shit
crap turd piss fuck fucker fucking bullshit horseshit dick cock prick pecker willy wiener weenie dong
schlong knob penis vagina vulva pussy snatch clit clitoris scrotum testicle testicles bollocks tits
titties nipple boner erection orgasm wank wanker dildo vibrator condom porn porno smut horny raunchy
kinky smutty randy bonk shag hump booger snot vomit puke barf diarrhea diarrhoea potty turd sperm semen
jizz cum spunk cunt twat bitch prostitute harlot strumpet trollop hussy floozy floozie tart cocotte cyprian
bawd whoreson adulteress fornicatress whore slut skank slattern cocksucker motherfucker dickhead arsehole
chickenshit dogshit shite shitter minge nookie nooky shtup bunghole fanny'''.split())
VULGAR_ADJECTIVES = set('''horny raunchy kinky smutty randy fucking shitty crappy bitchy pussy slutty sluttish
whorish shitless'''.split())

# Words WordNet calls obscene that aren't crude: they share a meaning with a
# crude word (jack and diddly-shit) or are just old-fashioned (crashing bore).
NOT_VULGAR = set('''jack diddly diddley diddlysquat shucks cuckoo goof goofball bozo fathead firecracker
illegitimate puss vernacular catty cattish rotten lousy icky crashing'''.split())

# Slurs against groups of people (by origin, sexual orientation or disability)
# and words about sexual orientation or abuse that WordNet doesn't label
# clearly. Only words whose main meaning is the slur: frog or cracker are
# fine as animal and food. The last ones are slurs made of two harmless words
# (porch + monkey), which the website must not put together, see blocked().
HURTFUL_WORDS = set('''nigger nigga nigra negro negress coon spic spick spik chink gook jap wop dago kike hymie sheeny yid
heeb wetback beaner greaser greaseball raghead towelhead sambo darky darkey darkie pickaninny
piccaninny picaninny jigaboo redskin squaw halfbreed mulatto coolie cooly chinaman honky whitey
limey kraut boche fag faggot fagot dyke queer pouf poof poofter homo lezzie lesbo tranny shemale
retard retarded spastic spaz mongoloid cripple midget homosexual heterosexual bisexual transsexual
homosexuality heterosexuality bisexuality lesbianism gayness sodomy sodomite pederasty pederast
pedophilia paedophilia pedophile paedophile zoophilia bestiality incest rape rapist molester
miscegenation yenta fagged porchmonkey sandmonkey junglebunny tarbaby cameljockey spearchucker sandnigger
slopehead slanteye zipperhead'''.split())

SLUR_DEFINITION = re.compile(
    r'\b(ethnic slur|(offensive|derogatory|disparaging|contemptuous) (term|name|word) for)\b', re.I)
# "obscene terms for feces" is vulgar, "the quality of being obscene" is not
OBSCENE_DEFINITION = re.compile(r'\b(obscene|vulgar) (terms?|words?|names?|slang|expressions?) for\b', re.I)


class WordInfo:
    """Category, familiarity, mood and vulgarity of every word of the dictionary."""

    def __init__(self, entries, synsets):
        self.synsets = synsets
        self.senses = collections.defaultdict(list)   # (word, pos) -> synsets, main meaning first
        self.sense_relations = collections.defaultdict(list)
        sense_synset = {}
        for entry in entries:
            for sense_id, synset_id, relations in entry.senses:
                self.senses[(entry.word, entry.pos)].append(synset_id)
                self.sense_relations[(entry.word, entry.pos)] += relations
                sense_synset[sense_id] = synset_id

        # Familiarity signals
        self.in_texts = collections.Counter(
            token for synset in synsets.values() for token in re.findall('[a-z]+', synset.text.lower()))
        self.in_compounds = collections.Counter(
            part for entry in entries if re.search('[ -]', entry.word)
            for part in set(re.split('[ -]+', entry.word.lower())))
        self.meanings = collections.Counter()
        for entry in entries:
            self.meanings[entry.word] += len(entry.senses)
        self.pronounced = {entry.word for entry in entries if entry.pronounced}

        # Usage labels like obscenity or ethnic_slur, on a meaning or a single sense
        def label(target):
            synset = synsets.get(sense_synset.get(target, target))
            return synset.members[0].split('-', 1)[1].rsplit('-', 1)[0] if synset and synset.members else ''
        self.labels = {synset_id: {label(target) for relation, target in synset.relations if relation == 'exemplifies'}
                       for synset_id, synset in synsets.items()}
        self.sense_labels = {key: {label(target) for relation, target in relations if relation == 'exemplifies'}
                             for key, relations in self.sense_relations.items()}

        self.hypernyms = collections.defaultdict(list)
        self.neighbours = collections.defaultdict(set)
        for synset_id, synset in synsets.items():
            for relation, target in synset.relations:
                if relation in ('hypernym', 'instance_hypernym'):
                    self.hypernyms[synset_id].append(target)
                elif relation in ('similar', 'also'):
                    self.neighbours[synset_id].add(target)
                    self.neighbours[target].add(synset_id)

        # Mood adjectives: the seeds and the words whose main meaning is next to a seed
        mood_synsets = set()
        for seed in MOOD_SEEDS:
            if self.senses.get((seed, 'a')):
                main = self.senses[(seed, 'a')][0]
                mood_synsets |= {main} | {neighbour for neighbour in self.neighbours[main]
                                          if synsets[neighbour].lexfile != 'adj.pert'}
        self.moods = {word for (word, pos), meanings in self.senses.items()
                      if pos == 'a' and meanings[0] in mood_synsets}

    def category(self, word, pos):
        """The category of the main meaning: animal, food, person, all (adjectives), ..."""
        return self.synsets[self.senses[(word, pos)][0]].lexfile.split('.')[1].lower()

    @functools.lru_cache(maxsize=None)
    def familiarity(self, word, pos):
        """A score for how well known a word is: about 0 for wicopy, 15 for fox."""
        in_texts = self.in_texts[word] + (self.in_texts[word + 's'] if pos == 'n' else 0)
        return (math.log2(1 + in_texts) + math.log2(1 + self.in_compounds[word])
                + 1.5 * math.log2(max(1, self.meanings[word])) + (word in self.pronounced))

    @functools.lru_cache(maxsize=None)
    def is_main_pos(self, word, pos):
        """Whether the word is mainly used as this part of speech (heavy is no noun)."""
        return all(len(self.senses[(word, pos)]) >= len(self.senses.get((word, other), ()))
                   for other in 'nvar')

    def is_mood(self, word, pos):
        return pos == 'a' and word in self.moods

    @functools.lru_cache(maxsize=None)
    def is_hurtful(self, word, pos):
        main = self.senses[(word, pos)][0]
        return (word.lower() in HURTFUL_WORDS or 'ethnic_slur' in self.labels[main]
                or bool(SLUR_DEFINITION.search(self.synsets[main].text)))

    def is_crude(self, word, pos):
        """Whether the word is on the hand-picked list of crude words."""
        return word.lower() in (VULGAR_ADJECTIVES if pos in ('a', 's') else VULGAR_WORDS)

    @functools.lru_cache(maxsize=None)
    def is_vulgar(self, word, pos):
        meanings = self.senses[(word, pos)]
        if self.is_hurtful(word, pos):
            return False
        if self.is_crude(word, pos):
            return True
        if word.lower() in NOT_VULGAR:
            return False
        # no slur, not even in a minor meaning (fairy)
        if any('ethnic_slur' in self.labels[synset] or SLUR_DEFINITION.search(self.synsets[synset].text)
               for synset in meanings):
            return False
        obscene = ['obscenity' in self.labels[synset] or bool(OBSCENE_DEFINITION.search(self.synsets[synset].text))
                   for synset in meanings]
        # the main or most meanings are obscene, not just one of several (seat, bottom)
        return (obscene[0] or 2 * sum(obscene) > len(obscene)
                or 'obscenity' in self.sense_labels[(word, pos)] and len(meanings) == 1)

    @functools.lru_cache(maxsize=None)
    def is_inflected(self, word, pos):
        """Plurals and gerunds like days, boxes or making, which make dull names
        (but penis is no plural of pen)."""
        return pos == 'n' and (
            word.endswith('ing') and ((word[:-3], 'v') in self.senses or (word[:-3] + 'e', 'v') in self.senses)
            or word.endswith('s') and not word.endswith('ss') and (word[:-1], 'n') in self.senses
            or word.endswith('es') and (word[:-2], 'n') in self.senses)

    def ancestors(self, synset_id):
        found, todo = set(), [synset_id]
        while todo:
            for parent in self.hypernyms[todo.pop()]:
                if parent not in found:
                    found.add(parent)
                    todo.append(parent)
        return found

    def is_usable(self, word, pos, extra=None):
        """Whether the word may be shown from an extra list: never slurs, plurals
        or gerunds, and vulgar words only from the vulgar lists."""
        return (not self.is_hurtful(word, pos) and not self.is_inflected(word, pos)
                and self.is_vulgar(word, pos) == (extra == 'vulgar'))

    def rank(self, word, pos, extra=None):
        """Sort key for an extra list: familiar words first, words that may not be shown from it last.

        The vulgar lists start with the hand-picked crude words, even if they
        are used more as a verb (whore), and the mood list with its seeds."""
        if extra == 'vulgar':
            first = self.is_crude(word, pos)
        elif extra == 'mood':
            first = word in MOOD_SEEDS
        else:
            first = self.is_main_pos(word, pos)
        return (not self.is_usable(word, pos, extra), not first, not (self.is_main_pos(word, pos) or extra == 'vulgar'),
                -self.familiarity(word, pos), word)

    def extra_lists(self, word, pos):
        """The extra lists a word belongs to: its category, and mood or vulgar."""
        extras = [self.category(word, pos)]
        if self.is_mood(word, pos):
            extras.append('mood')
        if self.is_vulgar(word, pos):
            extras.append('vulgar')
        return extras


def blocked_hash(name):
    """A short hash of a name in lower case without spaces and dashes, see blocked()."""
    return hashlib.sha256(re.sub('[ -]', '', name.lower()).encode('utf-8')).hexdigest()[:16]


def blocked(hurtful, words):
    """Hashes of the hurtful words that two harmless words can make up (porch +
    monkey), so that the website can pick again when it comes up with one of them."""
    hashes = set()
    for word in hurtful:
        lower = re.sub('[ -]', '', word.lower())
        if any(lower[:split] in words and lower[split:] in words for split in range(1, len(lower))):
            hashes.add(blocked_hash(lower))
    return sorted(hashes)
