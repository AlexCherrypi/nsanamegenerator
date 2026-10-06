// The extra word lists like nsgl-animal or asl-mood are sorted from the best
// known to the most obscure word, see generateWords.py. With top, only one of
// the first top words is picked, and never one of the slurs, plurals and the
// like at the end of these lists.
async function random(a, top) {
    const lenresponse = await fetch('/nsanamegenerator/words/'+a+'/'+(top === undefined ? 'len' : 'usable')+'.txt')
    if (!lenresponse.ok) throw new Error('Could not load word list '+a)
    const len = Math.min(Number(await lenresponse.text()), top === undefined ? Infinity : top)
    const random = new Uint32Array(1)
    self.crypto.getRandomValues(random);
    // files are numbered 0 .. len-1
    const num = Math.floor((random[0] / 4294967296) * len)
    const response = await fetch('/nsanamegenerator/words/'+a+'/'+num+'.txt')
    if (!response.ok) throw new Error('Could not load word '+num+' of '+a)
    const word = await response.text();
    return word
  }

// ?vulgar makes most names vulgar, ?nerd allows obscure words as well
const params = new URLSearchParams(location.search)
const nerd = params.has('nerd')
const vulgar = params.has('vulgar') ? 0.7 : 0.08

// chooses one of the [word list, top, weight] by weight
function choose(lists) {
    let r = Math.random() * lists.reduce((sum, list) => sum + list[2], 0)
    return lists.find(list => (r -= list[2]) < 0) || lists[lists.length - 1]
  }

// picks a word from one of the [word list, top, weight]
async function pick(lists) {
    const [list, top] = choose(lists)
    return random(list, nerd ? Infinity : top)
  }
