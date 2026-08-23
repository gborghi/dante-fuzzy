/** Compact Snowball-inspired Italian stemmer (noun/adj/verb suffixes). */
(function (root) {
  const V = /[aeiouàèéìíòóùú]/;
  function rv(w) {
    if (w.length < 4) return 0;
    if (!V.test(w[0])) {
      const m = w.slice(1).search(V);
      return m < 0 ? w.length : m + 2;
    }
    if (V.test(w[1])) {
      const m = w.slice(2).search(/[^aeiouàèéìíòóùú]/);
      return m < 0 ? w.length : m + 3;
    }
    const m = w.slice(2).search(V);
    return m < 0 ? w.length : m + 3;
  }
  function r1(w) {
    const m = w.search(V);
    if (m < 0) return w.length;
    const n = w.slice(m + 1).search(/[^aeiouàèéìíòóùú]/);
    return n < 0 ? w.length : m + n + 2;
  }
  function strip(w, start, suffixes) {
    for (const s of suffixes) {
      if (w.length - s.length >= start && w.endsWith(s)) return w.slice(0, -s.length);
    }
    return w;
  }
  function stemIt(raw) {
    let w = String(raw || '').toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    w = w.replace(/qu/g, 'qU');
    if (w.length < 3) return w.toLowerCase();
    const R1 = r1(w), RV = rv(w);
    const pronouns = ['glieli','gliele','gliene','gliela','glielo','sene','mene','tene',
      'cela','cele','celi','celo','cene','vela','vele','veli','velo','vene',
      'mela','mele','meli','melo','mene','tela','tele','teli','telo',
      'sela','sele','seli','selo','gli','ci','la','le','li','lo','mi','ne','si','ti','vi'];
    let prev = w;
    w = strip(w, RV, pronouns);
    if (w !== prev && /[aeiou]$/.test(w)) w = w.slice(0, -1);
    w = strip(w, R1, ['amente']);
    w = strip(w, RV, ['azione','azioni','atore','atori','atrice','atrici']);
    w = strip(w, R1, ['amente','imenti','amente','amente']);
    w = strip(w, R1, ['amente','icamente','ivamente','osamente','amente']);
    w = strip(w, R1, ['abilità','icità','ività','ità','ità']);
    w = strip(w, R1, ['icamente','abilità','icità','ivamente','osamente','amente']);
    w = strip(w, R1, ['icamente','abilità','ività','ità']);
    w = strip(w, RV, [
      'erebbe','erebbero','erebbe','eranno','erebbe',
      'iscano','iscono','iamo','iate','avano','ivano','avano',
      'ando','endo','ando','ere','are','ire',
      'ato','ata','ati','ate','uto','uta','uti','ute','ito','ita','iti','ite',
      ' evano',' evano'
    ]);
    w = strip(w, RV, [
      'erebbe','eranno','eremo','erete','erono','evamo','evate','evano',
      'iscano','iscono','iamo','iate',
      'avo','avi','ava','ammo','aste','arono','ava',
      'ivo','ivi','iva','immo','iste','irono',
      'ei','esti','è','emmo','este','erono',
      'ando','endo','ar','er','ir',
      'ato','ata','ati','ate','uto','uta','uti','ute','ito','ita','iti','ite'
    ]);
    w = strip(w, R1, [
      'azione','azioni','atore','atori','atrice','atrici',
      'logia','logie','uzione','uzioni','enza','enze',
      'amente','amente','amente',
      'amente','icamente','ivamente','osamente',
      'abile','abili','ibile','ibili','mente',
      'osa','ose','osi','oso','ica','ici','ico','ice',
      'anza','anze','iche','ichi',
      'ismo','ismi','ista','iste','isti','istà','istè','istì',
      'ico','ica','ici','ice','oso','osa','osi','ose'
    ]);
    w = strip(w, RV, ['a','e','i','o','à','è','ì','ò']);
    if (w.endsWith('ch') || w.endsWith('gh')) w = w.slice(0, -1);
    return w.replace(/qU/g, 'qu').toLowerCase();
  }
  root.stemIt = stemIt;
})(typeof window !== 'undefined' ? window : globalThis);
