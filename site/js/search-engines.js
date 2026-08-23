/* Search modes 1–6. Relies on nlpEngine, parseQuery, evalQuery, elementiCatalog. */
(function (root) {
  const CANTICHE = ['Inferno', 'Purgatorio', 'Paradiso'];

  function tokens(text) {
    return String(text || '').toLowerCase()
      .replace(/[''`]/g, "'")
      .replace(/[^\w\sàáèéìíòóùú]/g, ' ')
      .split(/\s+/)
      .map(w => w.replace(/^'+|'+$/g, ''))
      .filter(w => w.length > 1);
  }
  function stem(w) {
    return (typeof stemIt === 'function') ? stemIt(w) : w;
  }
  function lev(a, b) {
    if (a === b) return 0;
    const m = a.length, n = b.length;
    if (!m) return n; if (!n) return m;
    const dp = new Array(n + 1);
    for (let j = 0; j <= n; j++) dp[j] = j;
    for (let i = 1; i <= m; i++) {
      let prev = dp[0]; dp[0] = i;
      for (let j = 1; j <= n; j++) {
        const tmp = dp[j];
        dp[j] = a[i - 1] === b[j - 1] ? prev : 1 + Math.min(prev, dp[j], dp[j - 1]);
        prev = tmp;
      }
    }
    return dp[n];
  }

  const SE = {
    mode: 'exact',
    thesaurus: {},
    docs: [],
    vocab: [],
    idf: new Map(),
    ready: false,

    init(tercetMap, thesaurus) {
      this.thesaurus = thesaurus || {};
      this.docs = [];
      const df = new Map();
      for (const [cantica, canti] of Object.entries(tercetMap || {})) {
        for (const [canto, terz] of Object.entries(canti)) {
          for (const [tz, txt] of terz) {
            const surf = tokens(txt);
            const stems = surf.map(stem);
            const tf = new Map();
            stems.forEach(s => tf.set(s, (tf.get(s) || 0) + 1));
            for (const s of tf.keys()) df.set(s, (df.get(s) || 0) + 1);
            this.docs.push({
              cantica, canto: +canto, tercet: +tz, text: txt,
              surf, stems, tf, len: stems.length || 1
            });
          }
        }
      }
      const N = this.docs.length || 1;
      this.idf = new Map();
      for (const [w, d] of df) this.idf.set(w, Math.log(1 + (N - d + 0.5) / (d + 0.5)));
      this.avgLen = this.docs.reduce((s, d) => s + d.len, 0) / N;
      this.vocab = [...df.keys()];
      this.ready = true;
    },

    expandTerms(terms) {
      const out = new Set();
      for (const t of terms) {
        out.add(t);
        const stemT = stem(t);
        out.add(stemT);
        const extras = this.thesaurus[t] || this.thesaurus[stemT] || [];
        extras.forEach(x => { out.add(x.toLowerCase()); out.add(stem(x)); });
      }
      return [...out];
    },

    queryTerms(q) {
      return tokens(q).filter(w => !['and', 'or', 'not'].includes(w));
    },

    matchExact(q, doc) {
      const cond = parseQuery(q);
      return evalQuery((doc.text || '').toLowerCase(), cond, 0);
    },

    matchTypo(q, doc, maxD) {
      const terms = this.queryTerms(q);
      if (!terms.length) return false;
      return terms.every(t => {
        const st = stem(t);
        if (doc.stems.includes(st) || doc.surf.includes(t)) return true;
        const lim = maxD != null ? maxD : (t.length <= 4 ? 1 : 2);
        return doc.surf.some(w => Math.abs(w.length - t.length) <= lim && lev(w, t) <= lim);
      });
    },

    scoreBM25(q, doc) {
      const terms = this.queryTerms(q).map(stem);
      const k1 = 1.5, b = 0.75;
      let s = 0;
      for (const t of terms) {
        const f = doc.tf.get(t) || 0;
        if (!f) continue;
        const idf = this.idf.get(t) || 0;
        s += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * doc.len / (this.avgLen || 1)));
      }
      return s;
    },

    matchFacet(doc, facet) {
      if (!facet) return true;
      if (facet.cantica && facet.cantica !== 'all' && doc.cantica !== facet.cantica) return false;
      if (!facet.personaggio && !facet.vizio) return true;
      const el = root.elementiCatalog;
      if (!el) return true;
      const hit = (arr) => (arr || []).some(loc =>
        loc.cantica === doc.cantica && +loc.canto === +doc.canto &&
        (loc.tercet == null || +loc.tercet === +doc.tercet));
      if (facet.personaggio) {
        const p = (el.personaggi || []).find(x => x.id === facet.personaggio);
        if (p && !hit(p.luoghi)) return false;
      }
      if (facet.vizio) {
        const v = (el.vizi || []).find(x => x.id === facet.vizio);
        if (v && !hit(v.luoghi)) return false;
      }
      return true;
    },

    scoreConcept(q, doc) {
      // Cosine on stemmed TF-IDF (no model download).
      const qst = this.expandTerms(this.queryTerms(q)).map(stem);
      const qtf = new Map();
      qst.forEach(s => qtf.set(s, (qtf.get(s) || 0) + 1));
      let dot = 0, nq = 0, nd = 0;
      for (const [w, f] of qtf) {
        const qw = f * (this.idf.get(w) || 0);
        nq += qw * qw;
        const dw = (doc.tf.get(w) || 0) * (this.idf.get(w) || 0);
        dot += qw * dw;
      }
      for (const [w, f] of doc.tf) {
        const dw = f * (this.idf.get(w) || 0);
        nd += dw * dw;
      }
      const den = Math.sqrt(nq) * Math.sqrt(nd);
      return den ? dot / den : 0;
    },

    search(q, opts) {
      if (!this.ready || !q) return [];
      const mode = (opts && opts.mode) || this.mode || 'exact';
      const facet = opts && opts.facet;
      const minScore = mode === 'bm25' ? 0.01 : (mode === 'concept' ? 0.08 : 0);
      const scored = [];
      for (const doc of this.docs) {
        if (!this.matchFacet(doc, facet)) continue;
        let ok = false, score = 0;
        if (mode === 'exact' || mode === 'expand') {
          const qq = mode === 'expand'
            ? this.expandTerms(this.queryTerms(q)).join(' or ')
            : q;
          ok = this.matchExact(qq, doc) || (mode === 'expand' && this.matchExact(q, doc));
          score = ok ? 1 : 0;
        } else if (mode === 'typo') {
          ok = this.matchTypo(q, doc);
          score = ok ? 1 : 0;
        } else if (mode === 'bm25') {
          score = this.scoreBM25(q, doc);
          ok = score > minScore;
        } else if (mode === 'facet') {
          ok = this.matchExact(q, doc) || !this.queryTerms(q).length;
          score = ok ? 1 : 0;
        } else if (mode === 'concept') {
          score = this.scoreConcept(q, doc);
          ok = score > minScore;
        }
        if (ok) scored.push({ ...doc, score });
      }
      scored.sort((a, b) => b.score - a.score);
      return scored;
    }
  };

  root.SearchEngines = SE;
})(typeof window !== 'undefined' ? window : globalThis);
