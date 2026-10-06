# nsanamegenerator

[![Deploy nsanamegenerator](https://github.com/AlexCherrypi/nsanamegenerator/actions/workflows/deploy.yml/badge.svg)](https://github.com/AlexCherrypi/nsanamegenerator/actions/workflows/deploy.yml) [![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]


You might remember the old [nsanamegenerator.com](https://web.archive.org/web/20160318190656/http://www.nsanamegenerator.com/). 
In homage to that page I created this one. 

By using the data of [Open English WordNet](https://en-word.net/) (you can also find them on [Github](https://github.com/globalwordnet/english-wordnet)) I created this random word generator.

If you prefer the OG version that combined two nouns, in all caps and witout any space to seperate, visit [alexcherrypi.github.io/nsanamegenerator/og/](https://alexcherrypi.github.io/nsanamegenerator/og/).
Otherwise there currently is only this version, aka the main version [alexcherrypi.github.io/nsanamegenerator/](https://alexcherrypi.github.io/nsanamegenerator/).

Like the real codenames (EGOTISTICALGIRAFFE, IRATEMONK, MONKEYCALENDAR), the names are made of well known words: a moody adjective with an animal, a food or a thing, or two nouns of different kinds. Both pages know two extra modes:

- [?vulgar](https://alexcherrypi.github.io/nsanamegenerator/?vulgar): most names get a crude word ([OG](https://alexcherrypi.github.io/nsanamegenerator/og/?vulgar))
- [?nerd](https://alexcherrypi.github.io/nsanamegenerator/?nerd): all of WordNet, including the most obscure words ([OG](https://alexcherrypi.github.io/nsanamegenerator/og/?nerd))

## Word lists

The whole dictionary is available as word lists at `words/<list>/<number>.txt`, with the number of words in `words/<list>/len.txt`. The name of a list says what is in it, e.g. `nsgl`:

| Letter | Meaning |
|--------|---------|
| `n` / `v` / `a` / `r` | noun / verb / adjective / adverb |
| `s` / `c` | single word / combined words |
| `g` / `d` | no dash / dash |
| `l` / `u` | lower case / upper case letters |

Every list also comes with extra lists sorted from the best known to the most obscure word (see [wordinfo.py](wordinfo.py)): one per category of the word's main meaning, like `nsgl-animal`, `nsgl-food` or `nsgl-person`, and `asl-mood` for moods and `nsgl-vulgar` for crude words. Slurs and plurals come last, after the number of words in `usable.txt`.

This is just a little side project of mine, so don't expect regular updates and a lot of ongoing development.

But if you want to suggest any features or ideas, submit them by creating an issue. I don't have any templates set up yet (and maybe never will), but don't be scared by thaat. Just write your idea down and submit the issue. :-)




[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg
[nsanamegenerator](https://github.com/AlexCherrypi/nsanamegenerator/) © 2023 by [AlexCherrypi](https://github.com/AlexCherrypi/) is licensed under [CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/?ref=chooser-v1)

