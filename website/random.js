async function random(a) {
    const lenresponse = await fetch('/nsanamegenerator/words/'+a+'/len.txt')
    const len = await lenresponse;
    const random = new Uint32Array(1)
    self.crypto.getRandomValues(random);
    num = Math.floor((((Number(random[0])+1)/4294967296)*len) + 0.5 )
    const response = await fetch('/nsanamegenerator/words/'+a+'/'+num+'.txt')
    const word = await response;
    return word
  }

  


