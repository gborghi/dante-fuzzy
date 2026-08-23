/* Infographic gallery. Needs globalTercet, nlpEngine, elementiCatalog, openCantoModal. */
(function (root) {
  const CANTICHE = ['Inferno', 'Purgatorio', 'Paradiso'];
  const COL = { Inferno: '#c0392b', Purgatorio: '#c87c2a', Paradiso: '#2471a3' };

  function jump(c, n, t) {
    if (typeof openCantoModal === 'function') openCantoModal(c, +n, t != null ? +t : null);
  }

  function locBtn(c, n, t, title, sub) {
    return `<button type="button" class="el-locus ig-canto" data-cantica="${c}" data-canto="${n}" ${t != null ? `data-tercet="${t}"` : ''}>
      <div class="el-ref">${title || (c + ' ' + n)}</div>
      ${sub ? `<div class="el-sn">${sub}</div>` : ''}
    </button>`;
  }

  function renderTimeline(el, data) {
    el.innerHTML = `<p class="cosmo-intro">Dal Venerdì santo alla visione: clicca per il canto.</p>` +
      (data.timeline || []).map(s => locBtn(s.cantica, s.canto, null, `${s.quando} · ${s.guide}`, `${s.dove} — ${s.canti}`)).join('');
  }

  function renderContrapasso(el, data) {
    el.innerHTML = `<p class="cosmo-intro">Vizio → pena → esempio. Apri la scheda, poi clicca il locus.</p>
      <div class="row g-2">${(data.contrapasso || []).map(c => `
        <div class="col-md-6">
          <details class="d-card" style="margin-bottom:.45rem">
            <summary class="d-card-title" style="cursor:pointer;list-style:revert">${c.vizio}</summary>
            <div style="margin-top:.5rem">
              <div><strong>Pena:</strong> ${c.pena}</div>
              <div><strong>Esempio:</strong> ${c.esempio}</div>
              <p style="color:var(--muted);margin:.4rem 0">${c.nota}</p>
              ${locBtn(c.cantica, c.canto, c.tercet, `${c.cantica} ${c.canto} · terzina ${c.tercet}`, c.esempio)}
            </div>
          </details>
        </div>`).join('')}</div>`;
  }

  function renderGraph(el, data) {
    const g = data.graph || { nodes: [], edges: [] };
    const pers = (root.elementiCatalog && root.elementiCatalog.personaggi) || [];
    const firstLoc = (id) => (pers.find(p => p.id === id)?.luoghi || [])[0];
    el.innerHTML = `<p class="cosmo-intro">Layout fisico vis-network: trascina i nodi. Click = primo locus nella Commedia.</p>
      <div id="ig-vis" style="height:580px;border:1px solid var(--border);border-radius:6px;background:#12100c"></div>`;
    if (!root.vis || !root.vis.Network) {
      el.querySelector('#ig-vis').innerHTML = '<p style="color:var(--muted);padding:2rem">vis-network non caricato.</p>';
      return;
    }
    const nodes = new vis.DataSet(g.nodes.map(nd => {
      const damned = nd.vizi && nd.vizi.length;
      return {
        id: nd.id,
        label: nd.name,
        loc: firstLoc(nd.id),
        color: {
          background: damned ? '#7a241c' : '#2a4d28',
          border: damned ? '#e8c15a' : '#8fbc7a',
          highlight: { background: '#e8c15a', border: '#fff3c4' }
        },
        font: { color: '#efe6d4', size: 15, face: 'Cinzel, serif' },
        shape: 'dot',
        size: damned ? 18 : 16
      };
    }));
    const edges = new vis.DataSet((g.edges || []).map((e, i) => ({
      id: i, from: e.a, to: e.b,
      color: { color: 'rgba(232,193,90,.28)', highlight: '#e8c15a' },
      width: 1.2
    })));
    if (el._visNet) { try { el._visNet.destroy(); } catch (e) {} }
    const net = new vis.Network(el.querySelector('#ig-vis'), { nodes, edges }, {
      physics: {
        solver: 'barnesHut',
        barnesHut: {
          gravitationalConstant: -6500,
          springLength: 140,
          springConstant: 0.04,
          damping: 0.35,
          avoidOverlap: 0.7
        },
        stabilization: { iterations: 250 }
      },
      interaction: { dragNodes: true, dragView: true, zoomView: true, hover: true, tooltipDelay: 80 },
      nodes: { borderWidth: 2, shadow: { enabled: true, color: 'rgba(0,0,0,.45)', size: 8 } },
      edges: { smooth: { type: 'dynamic' } }
    });
    el._visNet = net;
    net.on('click', (p) => {
      if (!p.nodes.length) return;
      const nd = nodes.get(p.nodes[0]);
      if (nd && nd.loc) jump(nd.loc.cantica, nd.loc.canto, nd.loc.tercet);
    });
    const pane = document.querySelector('#mainTabs a[href="#tab-infografiche"]');
    const sub = document.querySelector('#igSub a[href="#ig-graph"]');
    const fit = () => { try { net.fit({ animation: true }); } catch (e) {} };
    if (sub) sub.addEventListener('shown.bs.tab', () => setTimeout(fit, 80));
    setTimeout(fit, 200);
  }

  function renderSchede(el, data) {
    el.innerHTML = `
      <div class="d-card-title">Firenze</div><div id="ig-box-firenze" class="mb-4"></div>
      <div class="d-card-title">Guide</div><div id="ig-box-guide" class="mb-4"></div>
      <div class="d-card-title">Rosa dei vizi e delle virtù</div><div id="ig-box-rosa" class="mb-4"></div>
      <div class="d-card-title">Terzina</div><div id="ig-box-rima"></div>`;
    renderFirenze(el.querySelector('#ig-box-firenze'), data);
    renderGuide(el.querySelector('#ig-box-guide'), data);
    renderRosa(el.querySelector('#ig-box-rosa'), data);
    renderRima(el.querySelector('#ig-box-rima'), data);
  }

  const FIRENZE_LOC = {
    cacciaguida: ['Paradiso', 15, 25],
    dante: ['Inferno', 1, 1],
    forese: ['Purgatorio', 23, 14],
    piccarda: ['Paradiso', 3, 13],
    corso: ['Purgatorio', 24, 28],
    gemma: ['Purgatorio', 23, 14],
    alighiero: ['Paradiso', 15, 25],
    bianchi: ['Paradiso', 17, 13],
    neri: ['Paradiso', 17, 13]
  };

  function renderFirenze(el, data) {
    const f = data.firenze || { nodi: [], archi: [] };
    el.innerHTML = `<p class="cosmo-intro">Click su un nome per il canto di riferimento.</p>
      <div class="d-flex flex-wrap gap-2 mb-2">${f.nodi.map(n => {
        const loc = FIRENZE_LOC[n.id];
        return loc
          ? `<button type="button" class="el-chip ig-canto ${n.ramo === 'Alighieri' ? 'good' : n.ramo === 'Donati' ? 'bad' : ''}"
               data-cantica="${loc[0]}" data-canto="${loc[1]}" data-tercet="${loc[2]}">${n.name}</button>`
          : `<span class="el-chip">${n.name}</span>`;
      }).join('')}</div>
      <ul style="color:var(--muted)">${f.archi.map(([a, b]) => {
        const A = f.nodi.find(x => x.id === a), B = f.nodi.find(x => x.id === b);
        return `<li>${A?.name || a} → ${B?.name || b}</li>`;
      }).join('')}</ul>`;
  }

  const SPEAKER_LOC = {
    'Dante pellegrino': ['Inferno', 1, 1],
    'Virgilio': ['Inferno', 1, 22],
    'Beatrice': ['Purgatorio', 30, 11],
    'Bernardo': ['Paradiso', 31, 16],
    'Francesca': ['Inferno', 5, 24],
    'Farinata': ['Inferno', 10, 8],
    'Ulisse': ['Inferno', 26, 19],
    'Ugolino': ['Inferno', 33, 1],
    'Marco Lombardo': ['Purgatorio', 16, 18],
    'Stazio': ['Purgatorio', 21, 20],
    'Cacciaguida': ['Paradiso', 15, 25],
    'Giustiniano': ['Paradiso', 6, 1],
    'Tommaso': ['Paradiso', 10, 25],
    'Pietro': ['Paradiso', 24, 10]
  };

  function renderSpeakers(el, data) {
    const max = Math.max(...(data.speakers || []).map(s => s.peso), 1);
    el.innerHTML = `<p class="cosmo-intro">Click sulla riga per il canto in cui quella voce è centrale.</p>` +
      (data.speakers || []).map(s => {
        const loc = SPEAKER_LOC[s.name];
        const inner = `<div style="display:flex;justify-content:space-between"><strong>${s.name}</strong><span style="color:var(--muted)">${s.canti}</span></div>
          <div style="height:8px;background:var(--parch);border-radius:4px;margin:.25rem 0">
            <div style="height:8px;width:${100 * s.peso / max}%;background:var(--gold);border-radius:4px"></div>
          </div>
          <div style="font-size:.85rem;color:var(--muted)">${s.nota}</div>`;
        return loc
          ? `<button type="button" class="el-locus ig-canto" data-cantica="${loc[0]}" data-canto="${loc[1]}" data-tercet="${loc[2]}" style="margin:.35rem 0">${inner}</button>`
          : `<div style="margin:.35rem 0">${inner}</div>`;
      }).join('');
  }

  function renderRosa(el) {
    const pairs = [
      ['superbia', 'Superbia', 'umilta', 'Umiltà', 'Purgatorio', 11, 1],
      ['invidia', 'Invidia', 'carita', 'Carità', 'Purgatorio', 13, 1],
      ['ira', 'Ira', 'mansuetudine', 'Mansuetudine', 'Purgatorio', 15, 1],
      ['accidia', 'Accidia', 'fortezza', 'Fortezza', 'Purgatorio', 17, 1],
      ['avarizia', 'Avarizia', 'liberalita', 'Liberalità', 'Purgatorio', 19, 1],
      ['gola', 'Gola', 'temperanza', 'Temperanza', 'Purgatorio', 23, 1],
      ['lussuria', 'Lussuria', 'castita', 'Castità', 'Purgatorio', 25, 1]
    ];
    const teo = [
      ['fede', 'Fede', 'Paradiso', 24, 1],
      ['speranza', 'Speranza', 'Paradiso', 25, 1],
      ['carita', 'Carità', 'Paradiso', 26, 1]
    ];
    el.innerHTML = `<p class="cosmo-intro">Click: apre il canto della cornice / esame.</p>
      <div class="row g-2">
        <div class="col-md-7"><div class="d-card-title">Capitali ↔ contrarie</div>
          ${pairs.map(p => `<div style="margin:.3rem 0">
            ${locBtn(p[4], p[5], p[6], p[1] + ' ↔ ' + p[3], '')}
          </div>`).join('')}
        </div>
        <div class="col-md-5"><div class="d-card-title">Teologali</div>
          ${teo.map(t => locBtn(t[2], t[3], t[4], t[1], '')).join('')}
        </div>
      </div>`;
  }

  function renderArbitrio(el, data) {
    el.innerHTML = `<p class="cosmo-intro">Dal cielo al merto: quattro luoghi-chiave.</p>` +
      (data.arbitrio || []).map((a, i) => locBtn(a.cantica, a.canto, a.tercet, `${i + 1}. ${a.tesi}`, a.luogo)).join('');
  }

  function renderGuide(el, data) {
    el.innerHTML = `<p class="cosmo-intro">Tre guide. Click sulla scheda per il canto di ingresso.</p>
      <div class="row g-2">${(data.guides || []).map(g => `
        <div class="col-md-4">${locBtn(g.canto[0], g.canto[1], null, g.name, `${g.ruolo} · ${g.da} → ${g.a}`)}</div>`).join('')}</div>`;
  }

  function renderRima(el) {
    el.innerHTML = `<p class="cosmo-intro">Terzina incatenata ABA BCB. Click su un verso: Inferno I.</p>
      <div id="ig-rima" style="font-family:'IM Fell English',serif;font-size:1.25rem;line-height:1.8">
        <button type="button" class="el-locus ig-canto" data-r="A" data-cantica="Inferno" data-canto="1" data-tercet="1">Nel mezzo del cammin di nostra vita <span class="el-chip">A</span></button>
        <button type="button" class="el-locus ig-canto" data-r="B" data-cantica="Inferno" data-canto="1" data-tercet="2">mi ritrovai per una selva oscura, <span class="el-chip">B</span></button>
        <button type="button" class="el-locus ig-canto" data-r="A" data-cantica="Inferno" data-canto="1" data-tercet="1">ché la diritta via era smarrita. <span class="el-chip">A</span></button>
        <button type="button" class="el-locus ig-canto" data-r="B" data-cantica="Inferno" data-canto="1" data-tercet="2">Ahi quanto a dir qual era è cosa dura <span class="el-chip">B</span></button>
        <button type="button" class="el-locus ig-canto" data-r="C" data-cantica="Inferno" data-canto="1" data-tercet="2">esta selva selvaggia e aspra e forte <span class="el-chip">C</span></button>
        <button type="button" class="el-locus ig-canto" data-r="B" data-cantica="Inferno" data-canto="1" data-tercet="2">che nel pensier rinova la paura! <span class="el-chip">B</span></button>
      </div>`;
    const rows = el.querySelectorAll('#ig-rima [data-r]');
    let i = 0;
    if (el._rimaTimer) clearInterval(el._rimaTimer);
    el._rimaTimer = setInterval(() => {
      rows.forEach(r => r.style.opacity = '.45');
      const letter = ['A', 'B', 'A', 'B', 'C', 'B'][i % 6];
      rows.forEach(r => { if (r.getAttribute('data-r') === letter) r.style.opacity = '1'; });
      i++;
    }, 700);
  }

  function heatGrid(term) {
    const gt = root.globalTercet || {};
    const mode = document.querySelector('input[name="algo"]:checked')?.value || 'exact';
    const counts = {};
    CANTICHE.forEach(c => {
      const max = c === 'Inferno' ? 34 : 33;
      for (let n = 1; n <= max; n++) counts[c + '_' + n] = 0;
    });
    const q = String(term || '').toLowerCase();
    if (root.SearchEngines && root.SearchEngines.ready && mode !== 'exact') {
      root.SearchEngines.search(q, { mode }).forEach(h => {
        const k = h.cantica + '_' + h.canto;
        if (k in counts) counts[k]++;
      });
    } else {
      const match = (typeof root.tercetMatchesQuery === 'function')
        ? (txt) => root.tercetMatchesQuery(txt, q)
        : (txt) => (typeof root.evalQuery === 'function' && root.parseQuery)
            ? root.evalQuery(String(txt||'').toLowerCase(), root.parseQuery(q), 0)
            : false;
      CANTICHE.forEach(c => {
        const book = gt[c] || {};
        Object.keys(book).forEach(canto => {
          const terz = book[canto] || [];
          terz.forEach(row => {
            const txt = Array.isArray(row) ? row[1] : '';
            if (match(txt)) counts[c + '_' + canto] = (counts[c + '_' + canto] || 0) + 1;
          });
        });
      });
    }
    const grid = [];
    CANTICHE.forEach(c => {
      const max = c === 'Inferno' ? 34 : 33;
      for (let n = 1; n <= max; n++) grid.push({ cantica: c, canto: n, n: counts[c + '_' + n] || 0 });
    });
    return grid;
  }

  function paintHeat(host, term) {
    if (!host) return;
    if (!term) { host.innerHTML = '<p style="color:var(--muted)">Inserisci una parola.</p>'; return; }
    let grid;
    try { grid = heatGrid(term); }
    catch (err) {
      host.innerHTML = `<p style="color:#e98a82">Errore ricerca: ${String(err.message || err)}</p>`;
      return;
    }
    const max = Math.max(...grid.map(g => g.n), 1);
    const tot = grid.reduce((s, g) => s + g.n, 0);
    const byC = {};
    CANTICHE.forEach(c => { byC[c] = grid.filter(g => g.cantica === c); });
    host.innerHTML = `<div style="color:var(--gold);margin:.3rem 0 .6rem">${tot} terzine · «${term}» (stesso motore della barra UMAP)</div>` +
      CANTICHE.map(c => `
        <div style="margin:.4rem 0">
          <div class="el-ref" style="color:${COL[c]}">${c}</div>
          <div style="display:flex;flex-wrap:wrap;gap:3px">${byC[c].map(g => {
            const a = g.n / max;
            return `<button type="button" class="ig-canto" data-cantica="${c}" data-canto="${g.canto}"
              title="${c} ${g.canto}: ${g.n}" style="width:22px;height:22px;border:0;border-radius:3px;cursor:pointer;background:rgba(232,193,90,${g.n ? 0.2 + a * 0.8 : 0.06});color:#1a1400;font-size:9px">${g.canto}</button>`;
          }).join('')}</div>
        </div>`).join('');
  }

  function renderHeat(el) {
    el.innerHTML = `<p class="cosmo-intro">Stessa ricerca della barra UMAP (stem, AND/OR, motore scelto in Algoritmo). Click sul canto per aprirlo.</p>
      <div class="d-flex gap-2 mb-2">
        <input class="el-search" id="ig-heat-q" type="search" placeholder="es. luce, giustizia AND stelle…" value="luce" style="margin:0">
        <button type="button" class="btn btn-gold btn-sm" id="ig-heat-go">Mostra</button>
      </div>
      <div id="ig-heat-grid"><p style="color:var(--muted)">Premi Mostra.</p></div>`;
    const run = () => {
      const q = (el.querySelector('#ig-heat-q')?.value || '').trim();
      paintHeat(el.querySelector('#ig-heat-grid'), q);
    };
    el.addEventListener('click', (e) => {
      if (e.target.closest('#ig-heat-go')) { e.preventDefault(); run(); }
    });
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && e.target.id === 'ig-heat-q') { e.preventDefault(); run(); }
    });
    run();
  }

  function renderCitazioni(el) {
    const post = (root.elementiCatalog && root.elementiCatalog.posteriori) || [];
    el.innerHTML = `<p class="cosmo-intro">Apri la scheda, poi clicca la terzina fonte.</p>` +
      post.map(p => `
        <details class="d-card" style="margin-bottom:.45rem">
          <summary class="d-card-title" style="cursor:pointer;list-style:revert">${p.author} — ${p.work}</summary>
          <div style="margin-top:.4rem;color:var(--muted)">${p.year || ''} · ${p.what || ''}</div>
          ${(p.luoghi || []).map(l => locBtn(l.cantica, l.canto, l.tercet, `${l.cantica} ${l.canto} · ${l.tercet}`, l.snippet || '')).join('')}
        </details>`).join('');
  }

  const EUROPA_LOC = {
    'Firenze': ['Inferno', 1, 1],
    'Ravenna': ['Paradiso', 33, 40],
    'Londra': ['Inferno', 27, 20],
    'Parigi': ['Inferno', 5, 34],
    'Dublino': ['Purgatorio', 4, 30],
    'Mosca': ['Inferno', 1, 1],
    'Buenos Aires': ['Inferno', 26, 38],
    'St. Lucia': ['Inferno', 1, 22],
    'Auschwitz': ['Inferno', 26, 38]
  };

  function renderEuropa(el, data) {
    el.innerHTML = `<p class="cosmo-intro">Click su città o riga: apre la terzina più citata da quel luogo.</p>
      <svg viewBox="0 0 100 100" style="width:100%;max-width:560px;background:var(--vellum);border:1px solid var(--border);border-radius:6px">
        <rect x="8" y="18" width="70" height="50" fill="none" stroke="#4a4336"/>
        ${(data.europa || []).map(p => {
          const loc = EUROPA_LOC[p.city];
          return `<g class="ig-canto" data-cantica="${loc ? loc[0] : 'Inferno'}" data-canto="${loc ? loc[1] : 1}" data-tercet="${loc ? loc[2] : 1}" style="cursor:pointer">
            <circle cx="${p.x}" cy="${p.y}" r="2.2" fill="#e8c15a"/>
            <text x="${p.x + 2.4}" y="${p.y + 1.2}" font-size="3.4" fill="#efe6d4">${p.city}</text>
          </g>`;
        }).join('')}
      </svg>
      <div class="mt-2">${(data.europa || []).map(p => {
        const loc = EUROPA_LOC[p.city];
        return locBtn(loc[0], loc[1], loc[2], p.city, p.who);
      }).join('')}</div>`;
  }

  const PANES = {
    'ig-time': renderTimeline,
    'ig-contra': renderContrapasso,
    'ig-graph': renderGraph,
    'ig-schede': renderSchede,
    'ig-voci': renderSpeakers,
    'ig-heat': renderHeat
  };

  function bindClicks(rootEl) {
    rootEl.addEventListener('click', (ev) => {
      const b = ev.target.closest('.ig-canto');
      if (!b || !rootEl.contains(b)) return;
      if (!b.dataset.cantica) return;
      ev.preventDefault();
      jump(b.dataset.cantica, b.dataset.canto, b.dataset.tercet);
    });
  }

  root.renderInfografiche = function (data) {
    root.infograficaData = data;
    const host = document.getElementById('tab-infografiche');
    if (!host) return;
    if (!host.dataset.bound) {
      host.dataset.bound = '1';
      bindClicks(host);
    }
    Object.entries(PANES).forEach(([id, fn]) => {
      const pane = document.getElementById(id);
      if (!pane) return;
      try { fn(pane, data); }
      catch (err) { console.error('infografica', id, err); pane.innerHTML = `<p style="color:#e98a82">${id}: ${String(err.message || err)}</p>`; }
    });
  };
})(typeof window !== 'undefined' ? window : globalThis);
