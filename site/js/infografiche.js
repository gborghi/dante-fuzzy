/* Infographic gallery. Needs infograficaData, COSMOLOGY, C_COLOR, openCantoModal, Plotly. */
(function (root) {
  const CANTICHE = ['Inferno', 'Purgatorio', 'Paradiso'];
  const COL = { Inferno: '#c0392b', Purgatorio: '#c87c2a', Paradiso: '#2471a3' };

  function jump(c, n, t) {
    if (typeof openCantoModal === 'function') openCantoModal(c, n, t || null);
  }

  function acc(title, body) {
    return `<div class="d-card el-card">
      <button type="button" class="el-acc"><div class="d-card-title">${title}</div><span class="caret">▸</span></button>
      <div class="el-body">${body}</div></div>`;
  }

  function renderCosmo(el, data) {
    const cosmos = root.COSMOLOGY || {};
    const mk = (cantica, arr, color) => `
      <div class="col-md-4">
        <div class="d-card-title" style="color:${color}">${cantica}</div>
        ${(arr || []).map(r => `
          <button type="button" class="el-locus ig-canto" data-cantica="${cantica}" data-canto="${r.cantos[0]}">
            <div class="el-ref">${r.name}</div>
            <div class="el-sn">${r.sub} · canti ${r.cantos[0]}${r.cantos.length > 1 ? '–' + r.cantos[r.cantos.length - 1] : ''}</div>
          </button>`).join('')}
      </div>`;
    el.innerHTML = `<p class="cosmo-intro">Sezione del viaggio: clicca un luogo per aprire il primo canto.</p>
      <div class="row g-2">${mk('Inferno', cosmos.Inferno, COL.Inferno)}${mk('Purgatorio', cosmos.Purgatorio, COL.Purgatorio)}${mk('Paradiso', cosmos.Paradiso, COL.Paradiso)}</div>`;
  }

  function renderTimeline(el, data) {
    el.innerHTML = `<p class="cosmo-intro">Dal Venerdì santo alla visione: giorni, guide, canti.</p>` +
      (data.timeline || []).map(s => `
        <button type="button" class="el-locus ig-canto" data-cantica="${s.cantica}" data-canto="${s.canto}">
          <div class="el-ref">${s.quando} · ${s.guide}</div>
          <div class="el-sn">${s.dove} — ${s.canti}</div>
        </button>`).join('');
  }

  function renderContrapasso(el, data) {
    el.innerHTML = `<p class="cosmo-intro">Vizio → pena → esempio. Click sulla scheda per il locus.</p>
      <div class="row g-2">${(data.contrapasso || []).map(c => `
        <div class="col-md-6">${acc(c.vizio, `
          <div><strong>Pena:</strong> ${c.pena}</div>
          <div><strong>Esempio:</strong> ${c.esempio}</div>
          <p style="color:var(--muted);margin:.4rem 0">${c.nota}</p>
          <button type="button" class="el-locus ig-canto" data-cantica="${c.cantica}" data-canto="${c.canto}" data-tercet="${c.tercet}">
            <div class="el-ref">${c.cantica} ${c.canto} · ${c.tercet}</div>
          </button>`)}</div>`).join('')}</div>`;
  }

  function renderGraph(el, data) {
    const g = data.graph || { nodes: [], edges: [] };
    const W = 720, H = 480;
    const n = g.nodes.length || 1;
    const pos = g.nodes.map((_, i) => ({
      x: W / 2 + 220 * Math.cos(2 * Math.PI * i / n),
      y: H / 2 + 180 * Math.sin(2 * Math.PI * i / n)
    }));
    const idx = Object.fromEntries(g.nodes.map((nd, i) => [nd.id, i]));
    const lines = (g.edges || []).map(e => {
      const a = pos[idx[e.a]], b = pos[idx[e.b]];
      if (!a || !b) return '';
      return `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" stroke="#4a4336" stroke-width="1"/>`;
    }).join('');
    const nodes = g.nodes.map((nd, i) => {
      const p = nd.luoghi && nd.luoghi[0];
      const first = (data.graph && false);
      return `<g class="ig-node" data-id="${nd.id}" style="cursor:pointer">
        <circle cx="${pos[i].x}" cy="${pos[i].y}" r="7" fill="${nd.vizi && nd.vizi.length ? '#c0392b' : '#5a8f4a'}"/>
        <text x="${pos[i].x + 10}" y="${pos[i].y + 4}" fill="#efe6d4" font-size="11">${nd.name}</text>
      </g>`;
    }).join('');
    el.innerHTML = `<p class="cosmo-intro">Nodi legati da vizio o virtù condivisi. Rosso = dannati/penitenti, verde = beati/guide. Click = scheda Elementi.</p>
      <svg viewBox="0 0 ${W} ${H}" style="width:100%;background:var(--vellum);border:1px solid var(--border);border-radius:6px">${lines}${nodes}</svg>`;
    el.querySelectorAll('.ig-node').forEach(n => n.addEventListener('click', () => {
      if (typeof jumpEl === 'function') jumpEl('pers', n.getAttribute('data-id'));
      const tab = document.querySelector('#mainTabs a[href="#tab-elementi"]');
      if (tab && window.bootstrap?.Tab) bootstrap.Tab.getOrCreateInstance(tab).show();
    }));
  }

  function renderFirenze(el, data) {
    const f = data.firenze || { nodi: [], archi: [] };
    el.innerHTML = `<p class="cosmo-intro">Alighieri, Donati, Bianchi e Neri — lo sfondo fiorentino del poema.</p>
      <div class="d-flex flex-wrap gap-2 mb-2">${f.nodi.map(n =>
        `<span class="el-chip ${n.ramo === 'Alighieri' ? 'good' : n.ramo === 'Donati' ? 'bad' : ''}">${n.name}</span>`
      ).join('')}</div>
      <ul style="color:var(--muted)">${f.archi.map(([a, b]) => {
        const A = f.nodi.find(x => x.id === a), B = f.nodi.find(x => x.id === b);
        return `<li>${A?.name || a} → ${B?.name || b}</li>`;
      }).join('')}</ul>`;
  }

  function renderSpeakers(el, data) {
    const max = Math.max(...(data.speakers || []).map(s => s.peso), 1);
    el.innerHTML = `<p class="cosmo-intro">Chi parla, e quanto pesa nella lettura scolastica (indice relativo, non conteggio automatico).</p>` +
      (data.speakers || []).map(s => `
        <div style="margin:.35rem 0">
          <div style="display:flex;justify-content:space-between"><strong>${s.name}</strong><span style="color:var(--muted)">${s.canti}</span></div>
          <div style="height:8px;background:var(--parch);border-radius:4px">
            <div style="height:8px;width:${100 * s.peso / max}%;background:var(--gold);border-radius:4px"></div>
          </div>
          <div style="font-size:.85rem;color:var(--muted)">${s.nota}</div>
        </div>`).join('');
  }

  function renderRosa(el) {
    const vices = ['Superbia', 'Invidia', 'Ira', 'Accidia', 'Avarizia', 'Gola', 'Lussuria'];
    const virt = ['Umiltà', 'Carità', 'Mansuetudine', 'Fortezza', 'Liberalità', 'Temperanza', 'Castità'];
    const teo = ['Fede', 'Speranza', 'Carità'];
    el.innerHTML = `<p class="cosmo-intro">Sette capitali e virtù contrarie; al centro le teologali.</p>
      <div class="row g-2">
        <div class="col-md-6"><div class="d-card-title">Vizi</div>${vices.map((v, i) =>
          `<div class="el-row bad">${v} ↔ ${virt[i]}</div>`).join('')}</div>
        <div class="col-md-6"><div class="d-card-title">Teologali</div>${teo.map(v =>
          `<div class="el-row good">${v}</div>`).join('')}</div>
      </div>`;
  }

  function renderArbitrio(el, data) {
    el.innerHTML = `<p class="cosmo-intro">Dal cielo al merto: quattro luoghi-chiave.</p>` +
      (data.arbitrio || []).map((a, i) => `
        <button type="button" class="el-locus ig-canto" data-cantica="${a.cantica}" data-canto="${a.canto}" data-tercet="${a.tercet}">
          <div class="el-ref">${i + 1}. ${a.tesi}</div>
          <div class="el-sn">${a.luogo}</div>
        </button>`).join('');
  }

  function renderGuide(el, data) {
    el.innerHTML = `<p class="cosmo-intro">Tre guide, tre potenze: ragione, rivelazione, contemplazione.</p>
      <div class="row g-2">${(data.guides || []).map(g => `
        <div class="col-md-4"><div class="d-card" style="border-top:3px solid ${g.color}">
          <div class="d-card-title">${g.name}</div>
          <div>${g.ruolo}</div>
          <div style="color:var(--muted);font-size:.9rem">${g.da} → ${g.a}</div>
          <button type="button" class="el-locus ig-canto mt-2" data-cantica="${g.canto[0]}" data-canto="${g.canto[1]}">Apri</button>
        </div></div>`).join('')}</div>`;
  }

  function renderRima(el) {
    el.innerHTML = `<p class="cosmo-intro">Terzina incatenata: ABA BCB CDC …</p>
      <div id="ig-rima" style="font-family:'IM Fell English',serif;font-size:1.25rem;line-height:1.8">
        <div data-r="A">Nel mezzo del cammin di nostra vita <span class="el-chip">A</span></div>
        <div data-r="B">mi ritrovai per una selva oscura, <span class="el-chip">B</span></div>
        <div data-r="A">ché la diritta via era smarrita. <span class="el-chip">A</span></div>
        <div data-r="B">Ahi quanto a dir qual era è cosa dura <span class="el-chip">B</span></div>
        <div data-r="C">esta selva selvaggia e aspra e forte <span class="el-chip">C</span></div>
        <div data-r="B">che nel pensier rinova la paura! <span class="el-chip">B</span></div>
      </div>`;
    const rows = el.querySelectorAll('#ig-rima [data-r]');
    let i = 0;
    if (el._rimaTimer) clearInterval(el._rimaTimer);
    el._rimaTimer = setInterval(() => {
      rows.forEach(r => r.style.opacity = '.35');
      const letter = ['A', 'B', 'A', 'B', 'C', 'B'][i % 6];
      rows.forEach(r => { if (r.getAttribute('data-r') === letter) r.style.opacity = '1'; });
      i++;
    }, 700);
  }

  function renderHeat(el, data) {
    const keys = Object.keys(data.heat || {});
    el.innerHTML = `<p class="cosmo-intro">Densità per canto. Scegli un lemma.</p>
      <select id="ig-heat-sel" class="form-select form-select-sm" style="max-width:220px;margin-bottom:.6rem">
        ${keys.map(k => `<option value="${k}">${k}</option>`).join('')}
      </select>
      <div id="ig-heat-grid"></div>`;
    const paint = (key) => {
      const grid = data.heat[key] || [];
      const max = Math.max(...grid.map(g => g.n), 1);
      const byC = {};
      CANTICHE.forEach(c => { byC[c] = grid.filter(g => g.cantica === c); });
      document.getElementById('ig-heat-grid').innerHTML = CANTICHE.map(c => `
        <div style="margin:.4rem 0">
          <div class="el-ref" style="color:${COL[c]}">${c}</div>
          <div style="display:flex;flex-wrap:wrap;gap:2px">${byC[c].map(g => {
            const a = g.n / max;
            return `<button type="button" class="ig-canto" data-cantica="${c}" data-canto="${g.canto}"
              title="${c} ${g.canto}: ${g.n}" style="width:18px;height:18px;border:0;border-radius:2px;background:rgba(232,193,90,${0.08 + a * 0.9})"></button>`;
          }).join('')}</div>
        </div>`).join('');
    };
    paint(keys[0]);
    el.querySelector('#ig-heat-sel').addEventListener('change', e => paint(e.target.value));
  }

  function renderSentiment(el, data) {
    el.innerHTML = `<p class="cosmo-intro">Sentiment netto (pos − neg) sui 100 canti.</p><div id="ig-sent-plot" style="height:320px"></div>`;
    if (!root.Plotly) return;
    const traces = CANTICHE.map(c => {
      const pts = (data.sentiment || []).filter(s => s.cantica === c);
      return { x: pts.map(p => p.canto), y: pts.map(p => p.mean), name: c, type: 'scatter', mode: 'lines',
        line: { color: COL[c], width: 2 } };
    });
    Plotly.newPlot('ig-sent-plot', traces, {
      paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
      font: { color: '#efe6d4' },
      margin: { l: 40, r: 10, t: 10, b: 40 },
      xaxis: { title: 'Canto', gridcolor: '#4a4336' },
      yaxis: { title: 'netto', gridcolor: '#4a4336', zeroline: true },
      legend: { font: { color: '#efe6d4' } }
    }, { responsive: true, displayModeBar: false });
  }

  function renderCitazioni(el) {
    const post = (root.elementiCatalog && root.elementiCatalog.posteriori) || [];
    el.innerHTML = `<p class="cosmo-intro">Dalla Commedia ai lettori: click per la terzina fonte.</p>` +
      post.map(p => acc(`${p.author} — ${p.work}`, `
        <div style="color:var(--muted)">${p.year || ''} · ${p.what || ''}</div>
        ${(p.luoghi || []).map(l => `<button type="button" class="el-locus ig-canto" data-cantica="${l.cantica}" data-canto="${l.canto}" data-tercet="${l.tercet}">
          <div class="el-ref">${l.cantica} ${l.canto} · ${l.tercet}</div>
          <div class="el-sn">${l.snippet || ''}</div></button>`).join('')}
      `)).join('');
  }

  function renderEuropa(el, data) {
    el.innerHTML = `<p class="cosmo-intro">Luoghi della ricezione (schema, non atlante).</p>
      <svg viewBox="0 0 100 100" style="width:100%;max-width:560px;background:var(--vellum);border:1px solid var(--border);border-radius:6px">
        <rect x="8" y="18" width="70" height="50" fill="none" stroke="#4a4336"/>
        ${(data.europa || []).map(p => `
          <g>
            <circle cx="${p.x}" cy="${p.y}" r="1.6" fill="#e8c15a"/>
            <text x="${p.x + 2}" y="${p.y + 1}" font-size="3.2" fill="#efe6d4">${p.city}</text>
          </g>`).join('')}
      </svg>
      <ul style="margin-top:.6rem">${(data.europa || []).map(p => `<li><strong>${p.city}</strong> — ${p.who}</li>`).join('')}</ul>`;
  }

  const PANES = {
    'ig-cosmo': renderCosmo,
    'ig-time': renderTimeline,
    'ig-contra': renderContrapasso,
    'ig-graph': renderGraph,
    'ig-firenze': renderFirenze,
    'ig-voci': renderSpeakers,
    'ig-rosa': renderRosa,
    'ig-arb': renderArbitrio,
    'ig-guide': renderGuide,
    'ig-rima': renderRima,
    'ig-heat': renderHeat,
    'ig-sent': renderSentiment,
    'ig-cit': renderCitazioni,
    'ig-eu': renderEuropa
  };

  function bindClicks(rootEl) {
    rootEl.addEventListener('click', (ev) => {
      const accBtn = ev.target.closest('.el-acc');
      if (accBtn && rootEl.contains(accBtn)) {
        const card = accBtn.closest('.el-card');
        card.classList.toggle('open');
        const caret = accBtn.querySelector('.caret');
        if (caret) caret.textContent = card.classList.contains('open') ? '▾' : '▸';
      }
      const b = ev.target.closest('.ig-canto');
      if (!b) return;
      jump(b.dataset.cantica, +b.dataset.canto, b.dataset.tercet ? +b.dataset.tercet : null);
    });
  }

  root.renderInfografiche = function (data) {
    root.infograficaData = data;
    const host = document.getElementById('tab-infografiche');
    if (!host || host.dataset.bound) {
      Object.entries(PANES).forEach(([id, fn]) => {
        const el = document.getElementById(id);
        if (el) fn(el, data);
      });
      return;
    }
    host.dataset.bound = '1';
    bindClicks(host);
    Object.entries(PANES).forEach(([id, fn]) => {
      const el = document.getElementById(id);
      if (el) fn(el, data);
    });
  };
})(typeof window !== 'undefined' ? window : globalThis);
