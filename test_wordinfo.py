import unittest

from wordinfo import Entry, Synset, WordInfo, lists


def wordnet():
    """A tiny dictionary in the shape generateWords.py reads from WordNet."""
    synsets = {
        'animal': Synset('noun.Tops', 'a living organism', ['oewn-animal-n'], []),
        'fox': Synset('noun.animal', 'alert carnivorous mammal', ['oewn-fox-n'], [('hypernym', 'animal')]),
        'hound': Synset('noun.animal', 'a dog that hunts the fox; the fox ran, the hound followed the fox',
                        ['oewn-hound-n'], [('hypernym', 'animal')]),
        'wicopy': Synset('noun.plant', 'shrub of eastern North America', ['oewn-wicopy-n'], []),
        'day': Synset('noun.time', 'time for Earth to make a complete rotation', ['oewn-day-n'], []),
        'make': Synset('verb.creation', 'perform or carry out', ['oewn-make-v'], []),
        'heavy-n': Synset('noun.person', 'an actor who plays villainous roles', ['oewn-heavy-n'], []),
        'heavy-a': Synset('adj.all', 'of great weight', ['oewn-heavy-a'], []),
        'heavy-a2': Synset('adj.all', 'of great intensity', ['oewn-heavy-a'], []),
        'angry': Synset('adj.all', 'feeling or showing anger', ['oewn-angry-a'], []),
        'irate': Synset('adj.all', 'feeling or showing extreme anger', ['oewn-irate-a'], [('similar', 'angry')]),
        'light': Synset('adj.all', 'of comparatively little physical weight', ['oewn-light-a'], []),
        'obscenity': Synset('noun.communication', 'the quality of being obscene', ['oewn-obscenity-n'], []),
        'pastry': Synset('noun.food', 'a small open pie with a fruit filling', ['oewn-tart-n'], []),
        'tart-person': Synset('noun.person', 'a woman of loose morals', ['oewn-tart-n'], [('exemplifies', 'obscenity')]),
        'crap': Synset('noun.substance', 'obscene terms for feces', ['oewn-crap-n'], []),
        'genitalia': Synset('noun.body', 'the external sex organs', ['oewn-genitalia-n'], []),
        'penis': Synset('noun.body', 'the male organ of copulation', ['oewn-penis-n'], [('hypernym', 'genitalia')]),
        'fairy': Synset('noun.person', 'a small being, human in form', ['oewn-fairy-n'], []),
        'fairy-slur': Synset('noun.person', 'offensive term for a homosexual man', ['oewn-fairy-n'], []),
        'plonker': Synset('noun.person', 'offensive term for a person from somewhere', ['oewn-plonker-n'], []),
    }
    entries = [Entry(word, pos, pronounced, [(word + str(i), synset, []) for i, synset in enumerate(meanings)])
               for word, pos, pronounced, meanings in [
                   ('animal', 'n', True, ['animal']), ('fox', 'n', True, ['fox']), ('hound', 'n', True, ['hound']),
                   ('wicopy', 'n', False, ['wicopy']), ('day', 'n', True, ['day']), ('days', 'n', False, ['day']),
                   ('make', 'v', True, ['make']), ('making', 'n', False, ['make']),
                   ('heavy', 'n', False, ['heavy-n']), ('heavy', 'a', True, ['heavy-a', 'heavy-a2']),
                   ('angry', 'a', True, ['angry']), ('irate', 'a', True, ['irate']), ('light', 'a', True, ['light']),
                   ('obscenity', 'n', True, ['obscenity']), ('tart', 'n', True, ['pastry', 'tart-person']),
                   ('crap', 'n', True, ['crap']), ('genitalia', 'n', False, ['genitalia']),
                   ('penis', 'n', True, ['penis']), ('fairy', 'n', True, ['fairy', 'fairy-slur']),
                   ('plonker', 'n', False, ['plonker']), ('whore', 'n', False, ['tart-person']),
               ]]
    return WordInfo(entries, synsets)


class ListsTest(unittest.TestCase):

    def test_lists(self):
        self.assertEqual(lists('fox', 'n'), {'n', 'ns', 'ng', 'nl', 'nsg', 'nsl', 'nsgl'})
        self.assertEqual(lists('Bill of Rights', 'n'), {'n', 'nc', 'ng', 'nu', 'ncg', 'ncu', 'ncgu'})
        self.assertEqual(lists('well-being', 'n'), {'n', 'ns', 'nd', 'nl', 'nsd', 'nsl', 'nsdl'})


class WordInfoTest(unittest.TestCase):

    def setUp(self):
        self.info = wordnet()

    def test_category_of_main_meaning(self):
        self.assertEqual(self.info.category('fox', 'n'), 'animal')
        self.assertEqual(self.info.category('tart', 'n'), 'food')
        self.assertEqual(self.info.category('animal', 'n'), 'tops')

    def test_familiarity(self):
        # fox is mentioned in other definitions and has a pronunciation, wicopy has neither
        self.assertGreater(self.info.familiarity('fox', 'n'), self.info.familiarity('wicopy', 'n'))
        self.assertLess(self.info.rank('fox', 'n'), self.info.rank('wicopy', 'n'))

    def test_main_part_of_speech(self):
        self.assertTrue(self.info.is_main_pos('heavy', 'a'))
        self.assertFalse(self.info.is_main_pos('heavy', 'n'))

    def test_moods(self):
        self.assertTrue(self.info.is_mood('angry', 'a'))
        self.assertTrue(self.info.is_mood('irate', 'a'))   # next to angry in WordNet
        self.assertFalse(self.info.is_mood('light', 'a'))
        self.assertFalse(self.info.is_mood('fox', 'n'))

    def test_vulgar(self):
        self.assertTrue(self.info.is_vulgar('crap', 'n'))     # obscene main meaning
        self.assertTrue(self.info.is_vulgar('penis', 'n'))    # on the list of crude words
        self.assertFalse(self.info.is_vulgar('genitalia', 'n'))  # a medical term
        self.assertFalse(self.info.is_vulgar('obscenity', 'n'))  # about vulgar words, not one
        self.assertFalse(self.info.is_vulgar('tart', 'n'))    # a pastry first, obscene only on the side
        self.assertFalse(self.info.is_vulgar('fairy', 'n'))   # has a slur meaning, which is no fun
        self.assertFalse(self.info.is_vulgar('fox', 'n'))

    def test_hurtful(self):
        self.assertTrue(self.info.is_hurtful('plonker', 'n'))  # "offensive term for" a group
        self.assertTrue(self.info.is_hurtful('whore', 'n'))
        self.assertFalse(self.info.is_hurtful('fairy', 'n'))   # the main meaning is fine
        self.assertFalse(self.info.is_usable('plonker', 'n'))

    def test_inflected(self):
        self.assertTrue(self.info.is_inflected('days', 'n'))
        self.assertTrue(self.info.is_inflected('making', 'n'))
        self.assertFalse(self.info.is_inflected('day', 'n'))
        self.assertFalse(self.info.is_usable('days', 'n'))

    def test_unusable_words_come_last(self):
        words = ['plonker', 'wicopy', 'days', 'fox', 'whore', 'animal']
        ranked = sorted(words, key=lambda word: self.info.rank(word, 'n'))
        self.assertEqual(set(ranked[-3:]), {'plonker', 'days', 'whore'})
        self.assertEqual(ranked[0], 'fox')

    def test_extra_lists(self):
        self.assertEqual(self.info.extra_lists('fox', 'n'), ['animal'])
        self.assertEqual(self.info.extra_lists('irate', 'a'), ['all', 'mood'])
        self.assertEqual(self.info.extra_lists('crap', 'n'), ['substance', 'vulgar'])


if __name__ == '__main__':
    unittest.main()
