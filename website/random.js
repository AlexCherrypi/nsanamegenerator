// The extra word lists like nsgl-animal or asl-mood are sorted from the best
// known to the most obscure word, followed by the words that may not be shown
// from them, see generateWords.py. random(list) picks any word of a list,
// random(list, top) one of its top best known words, and random(list, top,
// true) one of the more obscure words after them.
async function random(a, top, obscure) {
    const lenresponse = await fetch('/nsanamegenerator/words/'+a+'/'+(top === undefined ? 'len' : 'usable')+'.txt')
    if (!lenresponse.ok) throw new Error('Could not load word list '+a)
    const len = Number(await lenresponse.text())
    // files are numbered 0 .. len-1
    let from = 0, to = len
    if (top !== undefined) {
        if (obscure && top < len) from = top
        else to = Math.min(top, len)
    }
    const random = new Uint32Array(1)
    self.crypto.getRandomValues(random);
    const num = from + Math.floor((random[0] / 4294967296) * (to - from))
    const response = await fetch('/nsanamegenerator/words/'+a+'/'+num+'.txt')
    if (!response.ok) throw new Error('Could not load word '+num+' of '+a)
    const word = await response.text();
    return word
  }

// Which words of a name get something special, set in the URL: ?vulgar or
// ?vulgar=1 sometimes, ?vulgar=2 at least one word, ?vulgar=3 every word.
// The same goes for ?nerd and obscure words.
function marks(flag, words) {
    const value = new URLSearchParams(location.search).get(flag)
    const level = value === null ? 0 : value === '' || isNaN(value) ? 1 : Math.min(3, Math.max(0, Math.round(value)))
    const marked = Array.from({length: words}, () => level === 3 || (level > 0 && Math.random() < 0.2))
    if (level === 2) marked[Math.floor(Math.random() * words)] = true
    return marked
  }

// chooses one of the [word list, top, weight] by weight
function choose(lists) {
    let r = Math.random() * lists.reduce((sum, list) => sum + list[2], 0)
    return lists.find(list => (r -= list[2]) < 0) || lists[lists.length - 1]
  }

// picks a word from one of the [word list, top, weight], an obscure one if asked
async function pick(lists, obscure) {
    const [list, top] = choose(lists)
    return random(list, top, obscure)
  }
