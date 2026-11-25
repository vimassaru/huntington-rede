/* Huntington como rede: explorador interativo. Tudo calculado no navegador a partir de data/dados.js */
(function () {
  const REPO = window.REPO_URL || "https://github.com/"; // ajustado no index.html apos publicar
  document.querySelectorAll("a[data-repo]").forEach(a => { const p = a.dataset.repo; a.href = REPO + (p ? (p.endsWith('/') ? '' : '/blob/main/' + p) : ''); a.target = "_blank"; a.rel = "noopener"; });
  const D = window.DADOS;
  const COR = {"Transporte intracelular":"#4C78A8","Transcrição":"#F58518","Sinalização de cálcio":"#54A24B","Mitocôndria/estresse oxidativo":"#E45756",
    "Apoptose":"#B279A2","Autofagia":"#72B7B2","Astrócitos":"#9D755D","HTT":"#111111"};
  const FIS = {
    SLC1A2:"Transportador EAAT2 dos astrócitos: retira glutamato da sinapse. Sem ele, o glutamato se acumula e entra cálcio demais no neurônio (excitotoxicidade).",
    PPARGC1A:"PGC-1α: controla a biogênese mitocondrial. Reprimido pela huntingtina mutada, leva a perda de energia (ATP).",
    HTT:"Huntingtina: proteína de andaime do transporte, da transcrição e da sobrevivência neuronal. A forma mutada é tóxica (ganho de função).",
    TP53:"Regulador central da apoptose. Maior grau da rede, mas com caminhos alternativos: sua remoção custa menos eficiência.",
    BAX:"Pró-apoptótica (família BCL-2). Como semente de cascata com φ = 0,3, derruba a rede toda e atinge 8 módulos.",
    HDAC1:"Desacetilase de histonas (repressão transcricional). Sozinha, protegida, reduz 27% da cascata a φ = 0,2.",
    DCTN1:"Subunidade da dinactina: transporte axonal retrógrado com dineína (HAP1/HTT).",
    BECN1:"Beclina 1: inicia a autofagia, que remove agregados de huntingtina.",
    MTOR:"Regulador do crescimento e freio da autofagia.",
    PLCB1:"Fosfolipase C β1: liga receptores metabotrópicos de glutamato à liberação de Ca²⁺ do retículo.",
    RUBCN:"Rubicon: regula a maturação de autofagossomos.",
    CASP3:"Caspase-3: executora final da apoptose.",
    GRM5:"Receptor metabotrópico de glutamato 5: sinaliza para cálcio via PLC/IP3.",
    SOD2:"Superóxido dismutase mitocondrial: defesa antioxidante."
  };
  const FISMOD = [
    ["Astrócitos","SLC1A2, SLC1A3","Recaptação de glutamato; falha → excitotoxicidade no estriado."],
    ["Mitocôndria/estresse oxidativo","PPARGC1A, SOD1, SOD2, TFAM","Biogênese mitocondrial e defesa antioxidante; o estriado tem alta demanda energética."],
    ["Sinalização de cálcio","GRM1, GRM5, ITPR1, PLCB1","mGluR → PLC → IP3 → Ca²⁺ do retículo; liga excitotoxicidade, mitocôndria e apoptose."],
    ["Apoptose","TP53, BAX, CASP3, CASP9","Via intrínseca da morte celular; ponto de convergência da morte neuronal."],
    ["Autofagia","BECN1, MTOR, ULK1, PIK3C3","Remoção de agregados e organelas danificadas; módulo mais denso (grau médio 9,9)."],
    ["Transcrição","HDAC1, REST, SIN3A, CREBBP","Regulação gênica; a huntingtina mutada interfere em fatores de transcrição."],
    ["Transporte intracelular","DCTN1, HAP1, KIF5A, KLC4","Transporte axonal por dineína e cinesina; suprimento de fatores tróficos."]];
  const GLOS = [
    ["Nó e aresta","Nó = proteína; aresta = interação funcional/física com pontuação STRING ≥ 0,7."],
    ["Grau e hub","Número de vizinhos. Hub é o nó muito conectado (TP53, HTT, BECN1)."],
    ["Betweenness","Fração dos caminhos mais curtos que passam pelo nó: mede o papel de ponte."],
    ["Agrupamento (clustering)","Chance de dois vizinhos de um nó também estarem ligados (0,64 aqui)."],
    ["Caminho médio e diâmetro","Passos médios entre dois nós (2,95) e o maior caminho mínimo (6)."],
    ["Small-world","Agrupamento muito maior que o aleatório com caminhos curtos. σ > 1 indica small-world."],
    ["Livre de escala","Distribuição de graus em lei de potência (poucos hubs enormes). Exige redes grandes para testar."],
    ["Modularidade (Q)","Mede se há mais arestas dentro dos grupos do que o esperado ao acaso (Q = 0,60)."],
    ["Ponto de articulação","Nó cuja remoção separa a rede: SLC1A2, PPARGC1A e HTT."],
    ["Eficiência global","Média de 1/distância entre pares de nós; cai quando os caminhos alongam ou somem."],
    ["Ataque aleatório × dirigido","Falha casual × perda de proteínas-chave. Redes com hubs toleram a primeira, não a segunda."],
    ["Cascata com limiar φ","Nó falha quando a fração φ de vizinhos já falhou; a falha se propaga a partir de uma semente."],
    ["Proteção (imunização)","Escolher k nós que não falham e medir quanto a cascata média diminui."]];

  const nodes = D.nodes, N = nodes.length, byId = new Map(nodes.map(n => [n.id, n]));
  const adj = new Map(nodes.map(n => [n.id, new Set()]));
  D.edges.forEach(([a, b]) => { adj.get(a).add(b); adj.get(b).add(a); });
  const ids = nodes.map(n => n.id);
  const f1 = (x, d = 1) => x.toLocaleString("pt-BR", {minimumFractionDigits: d, maximumFractionDigits: d});
  const pct = x => f1(100 * x, 0) + "%";
  const $ = s => document.querySelector(s);

  /* ---------- algoritmos ---------- */
  function bfs(src, removed) {
    const dist = new Map([[src, 0]]), q = [src];
    for (let i = 0; i < q.length; i++) {
      const u = q[i];
      for (const v of adj.get(u)) if (!removed.has(v) && !dist.has(v)) { dist.set(v, dist.get(u) + 1); q.push(v); }
    }
    return dist;
  }
  function lccAndEff(removed) {
    const rest = ids.filter(i => !removed.has(i)), n = rest.length;
    if (n < 2) return {lcc: n / N, eff: 0};
    let best = 0, sum = 0; const seen = new Set();
    for (const s of rest) {
      const d = bfs(s, removed);
      if (!seen.has(s)) { d.forEach((_, k) => seen.add(k)); best = Math.max(best, d.size); }
      d.forEach((v, k) => { if (k !== s) sum += 1 / v; });
    }
    return {lcc: best / N, eff: sum / (n * (n - 1))};
  }
  const EFF0 = lccAndEff(new Set()).eff;
  function cascade(seed, phi, prot) {
    const failed = new Set([seed]), rounds = [[seed]];
    for (;;) {
      const nw = [];
      for (const n of ids) {
        if (failed.has(n) || prot.has(n)) continue;
        const nb = adj.get(n); if (!nb.size) continue;
        let c = 0; nb.forEach(v => { if (failed.has(v)) c++; });
        if (c / nb.size >= phi - 1e-9) nw.push(n);
      }
      if (!nw.length) break;
      nw.forEach(n => failed.add(n)); rounds.push(nw);
    }
    return rounds;
  }
  const cascSize = (seed, phi, prot) => cascade(seed, phi, prot).reduce((a, r) => a + r.length, 0);
  function meanCascade(phi, prot) {
    const seeds = ids.filter(i => !prot.has(i)); let s = 0;
    for (const i of seeds) s += cascSize(i, phi, prot);
    return s / seeds.length;
  }
  function shuffle(a, rnd = Math.random) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
  const porGrau = ids.slice().sort((a, b) => byId.get(b).grau - byId.get(a).grau || byId.get(b).btw - byId.get(a).btw);
  const porBtw = ids.slice().sort((a, b) => byId.get(b).btw - byId.get(a).btw);
  /* ataque adaptativo (igual ao analise_robustez.py): a cada passo recalcula grau ou betweenness
     na rede que sobrou e remove o maior; empate -> maior id (mesma regra do max(key=(valor, n)) do Python) */
  function btwRest(removed) {
    const cb = new Map(ids.map(i => [i, 0]));
    for (const s of ids) {
      if (removed.has(s)) continue;
      const S = [], P = new Map(), sig = new Map([[s, 1]]), dist = new Map([[s, 0]]), q = [s];
      for (let i = 0; i < q.length; i++) {
        const v = q[i]; S.push(v);
        for (const w of adj.get(v)) {
          if (removed.has(w)) continue;
          if (!dist.has(w)) { dist.set(w, dist.get(v) + 1); q.push(w); }
          if (dist.get(w) === dist.get(v) + 1) { sig.set(w, (sig.get(w) || 0) + sig.get(v)); (P.get(w) || P.set(w, []).get(w)).push(v); }
        }
      }
      const delta = new Map();
      while (S.length) {
        const w = S.pop();
        for (const v of P.get(w) || []) delta.set(v, (delta.get(v) || 0) + sig.get(v) / sig.get(w) * (1 + (delta.get(w) || 0)));
        if (w !== s) cb.set(w, cb.get(w) + (delta.get(w) || 0));
      }
    }
    return cb;
  }
  function ordemAdaptativa(metrica) {
    const removed = new Set(), ordem = [];
    while (removed.size < N) {
      const val = metrica === "btw" ? btwRest(removed) : new Map(ids.map(i => [i, [...adj.get(i)].filter(v => !removed.has(v)).length]));
      let best = null;
      for (const i of ids) {
        if (removed.has(i)) continue;
        if (best === null || val.get(i) > val.get(best) + 1e-9 || (Math.abs(val.get(i) - val.get(best)) <= 1e-9 && i > best)) best = i;
      }
      removed.add(best); ordem.push(best);
    }
    return ordem;
  }
  const ataqueGrau = ordemAdaptativa("grau"), ataqueBtw = ordemAdaptativa("btw");
  const GULOSA = {}; D.protecao.forEach(r => { if (r.gulosa_nos) GULOSA[r.phi] = r.gulosa_nos.split(" "); });
  GULOSA[0.2] = GULOSA[0.2] || [];

  /* ---------- desenho genérico da rede ---------- */
  const PADX = 50, PADY = 40;
  const xs = d3.scaleLinear().domain(d3.extent(nodes, n => n.x)).range([PADX, 900 - PADX]);
  const ys = d3.scaleLinear().domain(d3.extent(nodes, n => n.y)).range([PADY, 620 - PADY]);
  nodes.forEach(n => { n.px = xs(n.x); n.py = ys(n.y); });
  const LABELS = new Set(["HTT","TP53","SLC1A2","PPARGC1A","HDAC1","BECN1","MTOR","BAX","DCTN1","CASP3"]);
  function makeNet(sel, cfg) {
    const svg = d3.select(sel);
    const g = svg.append("g");
    const ed = g.selectAll("line").data(D.edges).join("line").attr("class", "edge").attr("stroke-width", d => 0.8 + 1.6 * (d[2] - 0.7) / 0.3);
    const nd = g.selectAll("circle").data(nodes).join("circle").attr("class", "node").on("click", (e, d) => cfg.onClick && cfg.onClick(d));
    nd.append("title").text(d => d.id);
    const lb = g.selectAll("text").data(nodes).join("text").attr("class", "lbl").attr("text-anchor", "middle").attr("dy", -2);
    function place(anim) {
      const t = anim ? d3.transition().duration(600) : null;
      (t ? ed.transition(t) : ed).attr("x1", d => byId.get(d[0]).px).attr("y1", d => byId.get(d[0]).py).attr("x2", d => byId.get(d[1]).px).attr("y2", d => byId.get(d[1]).py);
      (t ? nd.transition(t) : nd).attr("cx", d => d.px).attr("cy", d => d.py);
    }
    function update() {
      nd.attr("r", d => cfg.r(d)).attr("fill", d => cfg.fill(d)).attr("stroke", d => cfg.stroke ? cfg.stroke(d) : "#fff")
        .attr("stroke-width", d => cfg.sw ? cfg.sw(d) : 1.5).attr("opacity", d => cfg.op ? cfg.op(d) : 1);
      ed.attr("opacity", d => cfg.eop ? cfg.eop(d) : 1);
      lb.attr("x", d => d.px).attr("y", d => d.py - cfg.r(d) - 2).text(d => (cfg.label ? cfg.label(d) : LABELS.has(d.id)) ? d.id : "")
        .attr("opacity", d => cfg.op ? cfg.op(d) : 1);
    }
    place(); update();
    return {update, place, nd, svg};
  }
  const rGrau = d => 5 + 1.1 * d.grau, rBtw = d => 5 + 38 * d.btw;

  /* ---------- números e módulos ---------- */
  const sw = D.smallworld;
  [["66", "proteínas (nós)"], ["207", "interações (arestas)"], ["0,64", "agrupamento (C)"], ["2,95", "passos médios entre proteínas"],
   ["Q = 0,60", "modularidade (7 módulos)"], ["−66%", "cascata ao proteger 5 hubs (φ = 0,2)"]].forEach(([a, b]) =>
    $("#numeros").insertAdjacentHTML("beforeend", `<div class="card"><b>${a}</b><span>${b}</span></div>`));

  /* ---------- 1. explorar ---------- */
  const modOff = new Set(); let selecionado = null;
  const legend = $("#legModulos");
  Object.entries(COR).forEach(([m, c]) => legend.insertAdjacentHTML("beforeend", `<span data-m="${m}"><i style="background:${c}"></i>${m}</span>`));
  legend.querySelectorAll("span").forEach(s => s.onclick = () => { const m = s.dataset.m; modOff.has(m) ? modOff.delete(m) : modOff.add(m); s.classList.toggle("off"); R.update(); });
  const effCol = d3.scaleLinear().domain([0, 3, 12]).range(["#F2F2F2", "#F6B26B", "#C0392B"]).clamp(true);
  const R = makeNet("#svgRede", {
    r: d => ($("#rSize").value === "btw" ? rBtw(d) : rGrau(d)),
    fill: d => ($("#rColor").value === "dEf" ? effCol(d.dEf) : COR[d.modulo]),
    stroke: d => d.id === selecionado ? "#000" : (d.art ? "#111" : "#fff"), sw: d => d.id === selecionado ? 4 : (d.art ? 3 : 1.5),
    op: d => modOff.has(d.modulo) ? 0.12 : 1, eop: d => (modOff.has(byId.get(d[0]).modulo) || modOff.has(byId.get(d[1]).modulo)) ? 0.1 : 1,
    onClick: d => { selecionado = d.id; mostraInfo(d); R.update(); }
  });
  ["#rColor", "#rSize"].forEach(s => $(s).onchange = () => R.update());
  nodes.forEach(n => $("#listaNos").insertAdjacentHTML("beforeend", `<option value="${n.id}">`));
  $("#rBusca").onchange = e => { const n = byId.get(e.target.value.trim().toUpperCase()); if (n) { selecionado = n.id; mostraInfo(n); R.update(); } };
  function mostraInfo(d) {
    const viz = [...adj.get(d.id)].sort((a, b) => byId.get(b).grau - byId.get(a).grau);
    $("#infoNo").innerHTML = `<h4>${d.id}</h4><span class="tag" style="background:${COR[d.modulo]}">${d.modulo}</span>${d.art ? '<span class="tag" style="background:#111">ponto de articulação</span>' : ""}
      <div class="kv"><span>Grau</span><b>${d.grau}</b><span>Betweenness</span><b>${f1(d.btw, 3)}</b><span>Perda de eficiência se removida</span><b>${f1(d.dEf)}%</b></div>
      <p>${FIS[d.id] || "Sem anotação resumida; veja o módulo funcional."}</p>
      <small>Vizinhos: ${viz.slice(0, 12).join(", ")}${viz.length > 12 ? "…" : ""}</small>`;
  }
  let sim = null;
  $("#rFisica").onclick = () => {
    const sn = nodes.map(n => ({id: n.id, x: n.px, y: n.py})), idx = new Map(sn.map(n => [n.id, n]));
    const ln = D.edges.map(e => ({source: idx.get(e[0]), target: idx.get(e[1])}));
    if (sim) sim.stop();
    sim = d3.forceSimulation(sn).force("link", d3.forceLink(ln).distance(55).strength(0.5)).force("charge", d3.forceManyBody().strength(-170))
      .force("center", d3.forceCenter(450, 310)).force("x", d3.forceX(450).strength(0.04)).force("y", d3.forceY(310).strength(0.06)).on("tick", () => {
        sn.forEach(s => { const n = byId.get(s.id); n.px = Math.max(30, Math.min(870, s.x)); n.py = Math.max(30, Math.min(590, s.y)); });
        syncAll(false);
      });
  };
  $("#rReset").onclick = () => { if (sim) sim.stop(); nodes.forEach(n => { n.px = xs(n.x); n.py = ys(n.y); }); syncAll(true); };
  function syncAll(anim) { [R, A, C, P].forEach(x => x && x.place(anim)); [A, C, P].forEach(x => x && x.update()); R.update(); }
  const mt = $("#tabModulos");
  mt.innerHTML = "<tr><th>Módulo</th><th>Nós</th><th>Grau médio</th><th>Arestas internas</th><th>Arestas para fora</th></tr>";
  const mods = {}; nodes.forEach(n => (mods[n.modulo] = mods[n.modulo] || []).push(n));
  const ints = {}, outs = {};
  D.edges.forEach(([a, b]) => { const ma = byId.get(a).modulo, mb = byId.get(b).modulo; if (ma === mb) ints[ma] = (ints[ma] || 0) + 1; else { outs[ma] = (outs[ma] || 0) + 1; outs[mb] = (outs[mb] || 0) + 1; } });
  Object.entries(mods).forEach(([m, l]) => mt.insertAdjacentHTML("beforeend", `<tr><td><i class="tag" style="background:${COR[m]}">&nbsp;</i>${m}</td><td>${l.length}</td><td>${f1(d3.mean(l, n => n.grau))}</td><td>${ints[m] || 0}</td><td>${outs[m] || 0}</td></tr>`));

  /* ---------- 2. ataque ---------- */
  let removidos = new Set(), ordemRand = shuffle(ids);
  function ordemAtaque() { const e = $("#aEstrat").value; return e === "grau" ? ataqueGrau : e === "btw" ? ataqueBtw : ordemRand; }
  function aplicaAtaque() {
    if ($("#aEstrat").value !== "manual") removidos = new Set(ordemAtaque().slice(0, +$("#aK").value));
    atualizaAtaque();
  }
  const A = makeNet("#svgAtaque", {
    r: rGrau, fill: d => COR[d.modulo], op: d => removidos.has(d.id) ? 0.1 : 1, eop: d => (removidos.has(d[0]) || removidos.has(d[1])) ? 0.05 : 1,
    stroke: d => removidos.has(d.id) ? "#C0392B" : "#fff",
    label: d => LABELS.has(d.id) && !removidos.has(d.id),
    onClick: d => {
      $("#aEstrat").value = "manual"; removidos.has(d.id) ? removidos.delete(d.id) : removidos.add(d.id);
      $("#aK").value = removidos.size; atualizaAtaque();
    }
  });
  function atualizaAtaque() {
    const m = lccAndEff(removidos);
    $("#aKv").textContent = removidos.size; $("#aLcc").textContent = pct(m.lcc); $("#aEff").textContent = pct(m.eff / EFF0);
    A.update(); desenhaAtaque(removidos.size, m.lcc);
  }
  $("#aK").oninput = aplicaAtaque; $("#aEstrat").onchange = () => { if ($("#aEstrat").value === "manual") removidos = new Set(); aplicaAtaque(); };
  $("#aSort").onclick = () => { ordemRand = shuffle(ids); if ($("#aEstrat").value !== "random") $("#aEstrat").value = "random"; aplicaAtaque(); };
  $("#aZera").onclick = () => { $("#aK").value = 0; removidos = new Set(); $("#aEstrat").value = "random"; atualizaAtaque(); };
  // curvas
  const KMAX = 30, curvaDet = o => { const r = [1]; for (let k = 1; k <= KMAX; k++) r.push(lccAndEff(new Set(o.slice(0, k))).lcc); return r; };
  const cG = curvaDet(ataqueGrau), cB = curvaDet(ataqueBtw);
  const cR = Array(KMAX + 1).fill(0); for (let t = 0; t < 200; t++) { const o = shuffle(ids); for (let k = 0; k <= KMAX; k++) cR[k] += (k ? lccAndEff(new Set(o.slice(0, k))).lcc : 1) / 200; }
  const chA = d3.select("#chAtaque");
  const xa = d3.scaleLinear([0, KMAX], [55, 880]), ya = d3.scaleLinear([0, 1], [275, 15]);
  function eixos(svg, x, y, xl, yl, tick = 5, fmt = d3.format(".0%")) {
    svg.append("g").attr("class", "gridline").selectAll("line").data(y.ticks(5)).join("line").attr("x1", x.range()[0]).attr("x2", x.range()[1]).attr("y1", y).attr("y2", y);
    svg.append("g").attr("class", "axis").attr("transform", `translate(0,${y.range()[0]})`).call(d3.axisBottom(x).ticks(tick));
    svg.append("g").attr("class", "axis").attr("transform", `translate(${x.range()[0]},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(fmt));
    svg.append("text").attr("class", "axis").attr("x", (x.range()[0] + x.range()[1]) / 2).attr("y", y.range()[0] + 34).attr("text-anchor", "middle").attr("fill", "var(--muted)").attr("font-size", 12).text(xl);
    svg.append("text").attr("transform", `rotate(-90)`).attr("x", -(y.range()[0] + y.range()[1]) / 2).attr("y", 14).attr("text-anchor", "middle").attr("fill", "var(--muted)").attr("font-size", 12).text(yl);
  }
  eixos(chA, xa, ya, "Nós removidos", "Rede ainda conectada (maior componente)");
  const linha = (svg, dados, x, y, cor, w = 2.5) => svg.append("path").datum(dados).attr("fill", "none").attr("stroke", cor).attr("stroke-width", w).attr("d", d3.line().x((d, i) => x(i)).y(d => y(d)));
  linha(chA, cR, xa, ya, "#8a96a3"); linha(chA, cG, xa, ya, "#F58518"); linha(chA, cB, xa, ya, "#E45756");
  [["Ao acaso (média)", "#8a96a3"], ["Maior grau", "#F58518"], ["Maior betweenness", "#E45756"]].forEach(([t, c], i) => {
    chA.append("rect").attr("x", 600).attr("y", 20 + 20 * i).attr("width", 14).attr("height", 4).attr("fill", c);
    chA.append("text").attr("x", 620).attr("y", 26 + 20 * i).attr("fill", "var(--ink)").attr("font-size", 12).text(t);
  });
  const marcaA = chA.append("circle").attr("r", 7).attr("fill", "none").attr("stroke", "var(--ink)").attr("stroke-width", 2.5);
  function desenhaAtaque(k, lcc) { marcaA.attr("cx", xa(Math.min(k, KMAX))).attr("cy", ya(lcc)); }

  /* ---------- 3. cascata ---------- */
  let cascTimer = null, falhosC = new Set(), roundAtual = new Map();
  const C = makeNet("#svgCasc", {
    r: rGrau, fill: d => falhosC.has(d.id) ? "#C0392B" : COR[d.modulo], stroke: d => d.id === $("#cSeed").value.toUpperCase() ? "#000" : "#fff",
    sw: d => d.id === $("#cSeed").value.toUpperCase() ? 4 : 1.5, op: d => falhosC.has(d.id) || !falhosC.size ? 1 : 0.55,
    label: d => LABELS.has(d.id) || falhosC.has(d.id) && falhosC.size < 14, onClick: d => { $("#cSeed").value = d.id; rodaCascata(); }
  });
  function phiC() { return +$("#cPhi").value; }
  function rodaCascata() {
    if (cascTimer) clearInterval(cascTimer);
    const seed = $("#cSeed").value.trim().toUpperCase(); if (!byId.has(seed)) return;
    $("#cSeed").value = seed; $("#cPhiV").textContent = f1(phiC(), 2);
    const rounds = cascade(seed, phiC(), new Set()), total = rounds.reduce((a, r) => a + r.length, 0);
    falhosC = new Set(); let i = 0; $("#cTam").textContent = "0";
    const mods = new Set(rounds.flat().map(n => byId.get(n).modulo)); mods.delete("HTT");
    cascTimer = setInterval(() => {
      if (i >= rounds.length) { clearInterval(cascTimer); return; }
      rounds[i].forEach(n => falhosC.add(n)); $("#cTam").textContent = falhosC.size; C.update(); i++;
    }, 650);
    $("#cMod").textContent = new Set(rounds.flat().map(n => byId.get(n).modulo)).size;
    const med = meanCascade(phiC(), new Set()); $("#cMed").textContent = f1(med);
    $("#cTexto").textContent = `Começando por ${seed}, ${total} de ${N} proteínas falham em ${rounds.length} rodada(s). Para comparar, uma semente típica derruba ${f1(med)}.`;
  }
  $("#cRun").onclick = rodaCascata;
  $("#cPhi").oninput = () => { $("#cPhiV").textContent = f1(phiC(), 2); rodaCascata(); };
  $("#cSeed").onchange = rodaCascata;
  $("#cWorst").onclick = () => { let b = null, bv = -1; ids.forEach(i => { const v = cascSize(i, phiC(), new Set()); if (v > bv) { bv = v; b = i; } }); $("#cSeed").value = b; rodaCascata(); };
  // curva de fragilidade
  const phis = d3.range(0.1, 0.65, 0.05), medPhi = phis.map(p => meanCascade(+p.toFixed(2), new Set()));
  const chP = d3.select("#chPhi"), xp = d3.scaleLinear([0.1, 0.6], [55, 880]), yp = d3.scaleLinear([0, d3.max(medPhi) * 1.1], [255, 15]);
  eixos(chP, xp, yp, "Limiar φ", "Nós que falham, em média", 6, d3.format("d"));
  chP.append("path").datum(medPhi).attr("fill", "none").attr("stroke", "#1F8A87").attr("stroke-width", 3).attr("d", d3.line().x((d, i) => xp(phis[i])).y(d => yp(d)));
  chP.selectAll("circle").data(medPhi).join("circle").attr("cx", (d, i) => xp(phis[i])).attr("cy", d => yp(d)).attr("r", 4).attr("fill", "#1F8A87");

  /* ---------- 4. proteção ---------- */
  let prot = new Set(), randCache = {};
  function phiP() { return +$("#pPhi").value; }
  function protegidosPorEstrategia() {
    const e = $("#pEstrat").value, k = +$("#pK").value;
    if (e === "grau") return new Set(porGrau.slice(0, k)); if (e === "btw") return new Set(porBtw.slice(0, k));
    if (e === "gulosa") return new Set((GULOSA[phiP().toFixed(1)] || GULOSA[0.2]).slice(0, k));
    if (e === "random") return new Set(shuffle(ids).slice(0, k)); return prot;
  }
  const P = makeNet("#svgProt", {
    r: rGrau, fill: d => prot.has(d.id) ? "#1F8A87" : COR[d.modulo], stroke: d => prot.has(d.id) ? "#0b4f4d" : "#fff", sw: d => prot.has(d.id) ? 4 : 1.5,
    label: d => LABELS.has(d.id) || prot.has(d.id), onClick: d => { $("#pEstrat").value = "manual"; prot.has(d.id) ? prot.delete(d.id) : prot.add(d.id); $("#pK").value = Math.min(10, prot.size); calcProt(true); }
  });
  function calcProt(manual) {
    $("#pPhiV").textContent = f1(phiP(), 2); $("#pKv").textContent = manual ? prot.size : $("#pK").value;
    if (!manual) prot = protegidosPorEstrategia();
    const base = meanCascade(phiP(), new Set()), agora = meanCascade(phiP(), prot);
    $("#pBase").textContent = f1(base); $("#pAgora").textContent = f1(agora); $("#pRed").textContent = base ? "−" + pct((base - agora) / base) : "–";
    $("#pLista").textContent = prot.size ? "Protegidas: " + [...prot].join(", ") + "." : "Nenhuma proteína protegida.";
    P.update();
  }
  ["#pPhi", "#pK", "#pEstrat"].forEach(s => $(s).oninput = () => { if (s === "#pEstrat" && $(s).value === "manual") { calcProt(true); return; } calcProt(false); desenhaProt(); });
  $("#pLimpa").onclick = () => { prot = new Set(); $("#pEstrat").value = "manual"; $("#pK").value = 0; calcProt(true); };
  const chPr = d3.select("#chProt"), xq = d3.scaleLinear([0, 10], [55, 880]), yq = d3.scaleLinear([0, 1], [290, 15]);
  function desenhaProt() {
    chPr.selectAll("*").remove();
    const phi = phiP(), base = meanCascade(phi, new Set());
    const est = {grau: k => new Set(porGrau.slice(0, k)), btw: k => new Set(porBtw.slice(0, k)), gulosa: k => new Set((GULOSA[phi.toFixed(1)] || GULOSA[0.2]).slice(0, k))};
    const res = {};
    Object.entries(est).forEach(([n, f]) => res[n] = d3.range(0, 11).map(k => (n === "gulosa" && !GULOSA[phi.toFixed(1)] && k > 0) ? null : 1 - meanCascade(phi, f(k)) / base));
    const key = phi.toFixed(2);
    randCache[key] = randCache[key] || d3.range(0, 11).map(k => { if (!k) return 0; let s = 0; for (let t = 0; t < 12; t++) s += meanCascade(phi, new Set(shuffle(ids).slice(0, k))); return 1 - s / 12 / base; });
    res.random = randCache[key];
    eixos(chPr, xq, yq, "Proteínas protegidas (k)", "Redução da cascata média", 10);
    [["random", "Aleatória", "#4c78a8"], ["grau", "Maior grau", "#F58518"], ["btw", "Maior betweenness", "#b279a2"], ["gulosa", "Escolha gulosa", "#E45756"]].forEach(([k, t, c], i) => {
      const dd = res[k].map((v, j) => [j, v]).filter(d => d[1] !== null);
      chPr.append("path").datum(dd).attr("fill", "none").attr("stroke", c).attr("stroke-width", 2.8).attr("d", d3.line().x(d => xq(d[0])).y(d => yq(Math.max(0, d[1]))));
      chPr.selectAll(".p" + k).data(dd).join("circle").attr("cx", d => xq(d[0])).attr("cy", d => yq(Math.max(0, d[1]))).attr("r", 3.5).attr("fill", c);
      chPr.append("rect").attr("x", 620).attr("y", 185 + 20 * i).attr("width", 14).attr("height", 4).attr("fill", c);
      chPr.append("text").attr("x", 640).attr("y", 191 + 20 * i).attr("fill", "var(--ink)").attr("font-size", 12).text(t);
    });
  }

  /* ---------- 5. small-world ---------- */
  const swT = $("#swTabela");
  swT.innerHTML = `<table><tr><th></th><th>Rede do HTT</th><th>Aleatória (Erdős–Rényi)</th><th>Mesmos graus (config.)</th></tr>
    <tr><td>Agrupamento C</td><td><b>${f1(sw.C, 3)}</b></td><td>${f1(sw.C_er, 3)}</td><td>${f1(sw.C_cfg, 3)}</td></tr>
    <tr><td>Caminho médio L</td><td><b>${f1(sw.L, 2)}</b></td><td>${f1(sw.L_er, 2)}</td><td>${f1(sw.L_cfg, 2)}</td></tr>
    <tr><td>σ = (C/C<sub>r</sub>)/(L/L<sub>r</sub>)</td><td></td><td><b>${f1(sw.sigma_er, 1)}</b></td><td><b>${f1(sw.sigma_cfg, 1)}</b></td></tr></table>`;
  $("#swSigma").textContent = `C é ${f1(sw.C / sw.C_er, 1)}× maior que o aleatório e L é só ${f1(100 * (sw.L / sw.L_er - 1), 0)}% maior; σ ≈ ${f1(sw.sigma_er, 1)} (vs. Erdős–Rényi) e ${f1(sw.sigma_cfg, 1)} (vs. mesmos graus), ambos > 1.`;
  $("#swEscala").innerHTML = `Há hubs (grau máximo 18, média ${f1(2 * sw.m / sw.n, 1)}), mas a cauda é curta. O expoente da lei de potência varia com o grau mínimo escolhido (α ≈ ${f1(sw.alfa_kmin1, 1)} com k ≥ 1; ≈ ${f1(sw.alfa_kmin3, 1)} com k ≥ 3), então <b>não afirmamos</b> que a rede é livre de escala. A assortatividade é ${f1(sw.assort, 2)}.`;
  function desenhaGrau() {
    const svg = d3.select("#chGrau"); svg.selectAll("*").remove();
    const log = $("#dLog").checked, ks = Object.keys(sw.graus).map(Number), dados = ks.map(k => [k, sw.graus[k] / sw.n]);
    const mean = 2 * sw.m / sw.n, pois = k => Math.exp(-mean + k * Math.log(mean) - d3.sum(d3.range(1, k + 1), j => Math.log(j)));
    const x = (log ? d3.scaleLog([1, 20], [50, 430]) : d3.scaleLinear([0, 20], [50, 430])), y = (log ? d3.scaleLog([0.01, 0.4], [250, 15]) : d3.scaleLinear([0, 0.2], [250, 15]));
    svg.append("g").attr("class", "axis").attr("transform", "translate(0,250)").call(d3.axisBottom(x).ticks(6, log ? "d" : undefined));
    svg.append("g").attr("class", "axis").attr("transform", "translate(50,0)").call(d3.axisLeft(y).ticks(5, log ? "~g" : "~%"));
    svg.append("text").attr("x", 240).attr("y", 288).attr("text-anchor", "middle").attr("fill", "var(--muted)").attr("font-size", 12).text("Grau k");
    svg.append("text").attr("x", 55).attr("y", 12).attr("fill", "var(--muted)").attr("font-size", 12).text("P(k)");
    const ps = d3.range(1, 21).map(k => [k, pois(k)]);
    svg.append("path").datum(ps).attr("fill", "none").attr("stroke", "#8a96a3").attr("stroke-width", 2).attr("stroke-dasharray", "5 4").attr("d", d3.line().x(d => x(d[0])).y(d => y(Math.max(d[1], 0.0101))));
    svg.selectAll("circle").data(dados).join("circle").attr("cx", d => x(d[0])).attr("cy", d => y(d[1])).attr("r", 5).attr("fill", "#1F8A87");
    svg.append("text").attr("x", 300).attr("y", 30).attr("fill", "#1F8A87").attr("font-size", 12).text("● rede do HTT");
    svg.append("text").attr("x", 300).attr("y", 46).attr("fill", "var(--muted)").attr("font-size", 12).text("-- Poisson (aleatória)");
  }
  $("#dLog").onchange = desenhaGrau; desenhaGrau();

  // Watts-Strogatz
  function wsGraph(n, k, p, rnd) {
    const a = Array.from({length: n}, () => new Set());
    for (let i = 0; i < n; i++) for (let j = 1; j <= k / 2; j++) { const t = (i + j) % n; a[i].add(t); a[t].add(i); }
    for (let i = 0; i < n; i++) for (let j = 1; j <= k / 2; j++) {
      const t = (i + j) % n; if (rnd() < p && a[i].has(t)) {
        let u; do { u = Math.floor(rnd() * n); } while (u === i || a[i].has(u));
        a[i].delete(t); a[t].delete(i); a[i].add(u); a[u].add(i);
      }
    }
    return a;
  }
  function wsMetrics(a) {
    const n = a.length; let C = 0;
    a.forEach((s, i) => { const v = [...s]; if (v.length < 2) return; let c = 0; for (let x = 0; x < v.length; x++) for (let y = x + 1; y < v.length; y++) if (a[v[x]].has(v[y])) c++; C += 2 * c / (v.length * (v.length - 1)); });
    let L = 0, cnt = 0;
    for (let s = 0; s < n; s++) { const d = new Array(n).fill(-1); d[s] = 0; const q = [s]; for (let i = 0; i < q.length; i++) for (const v of a[q[i]]) if (d[v] < 0) { d[v] = d[q[i]] + 1; q.push(v); } for (let t = 0; t < n; t++) if (t !== s && d[t] > 0) { L += d[t]; cnt++; } }
    return {C: C / n, L: L / cnt};
  }
  const mulberry = s => () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const m0 = wsMetrics(wsGraph(100, 6, 0, Math.random));
  const pGrid = d3.range(0, 15).map(i => 0.001 * Math.pow(1000, i / 14));
  const curva = pGrid.map(p => { let c = 0, l = 0; for (let r = 0; r < 8; r++) { const m = wsMetrics(wsGraph(100, 6, p, mulberry(1000 + r))); c += m.C / 8; l += m.L / 8; } return [p, c / m0.C, l / m0.L]; });
  const chW = d3.select("#chWS"), xw = d3.scaleLog([0.001, 1], [50, 440]), yw = d3.scaleLinear([0, 1.05], [290, 15]);
  chW.append("g").attr("class", "axis").attr("transform", "translate(0,290)").call(d3.axisBottom(xw).ticks(3, "~g"));
  chW.append("g").attr("class", "axis").attr("transform", "translate(50,0)").call(d3.axisLeft(yw).ticks(5, ".0%"));
  chW.append("text").attr("x", 245).attr("y", 330).attr("text-anchor", "middle").attr("fill", "var(--muted)").attr("font-size", 12).text("p (probabilidade de religação)");
  [[1, "#E45756", "C(p)/C(0) agrupamento"], [2, "#4c78a8", "L(p)/L(0) caminho médio"]].forEach(([c, cor, t], i) => {
    chW.append("path").datum(curva).attr("fill", "none").attr("stroke", cor).attr("stroke-width", 2.8).attr("d", d3.line().x(d => xw(d[0])).y(d => yw(d[c])));
    chW.selectAll(".w" + c).data(curva).join("circle").attr("cx", d => xw(d[0])).attr("cy", d => yw(d[c])).attr("r", 3.2).attr("fill", cor);
    chW.append("text").attr("x", 230).attr("y", 30 + 16 * i).attr("fill", cor).attr("font-size", 12).text("● " + t);
  });
  const marcaW = chW.append("line").attr("y1", 15).attr("y2", 290).attr("stroke", "var(--ink)").attr("stroke-dasharray", "4 3");
  const svgW = d3.select("#svgWS");
  function desenhaWS() {
    const v = +$("#wsP").value, p = v === 0 ? 0 : 0.001 * Math.pow(1000, v / 100);
    $("#wsPv").textContent = f1(p, 3);
    const n = 30, a = wsGraph(n, 4, p, mulberry(11)), R = 175, c = 210;
    svgW.selectAll("*").remove();
    const pos = i => [c + R * Math.cos(2 * Math.PI * i / n - Math.PI / 2), c + R * Math.sin(2 * Math.PI * i / n - Math.PI / 2)];
    for (let i = 0; i < n; i++) for (const j of a[i]) if (j > i) { const [x1, y1] = pos(i), [x2, y2] = pos(j), curto = Math.min((j - i + n) % n, (i - j + n) % n) <= 2;
      svgW.append("line").attr("x1", x1).attr("y1", y1).attr("x2", x2).attr("y2", y2).attr("stroke", curto ? "#8a96a3" : "#E45756").attr("stroke-width", curto ? 1.2 : 2).attr("opacity", curto ? 0.7 : 0.9); }
    for (let i = 0; i < n; i++) { const [x, y] = pos(i); svgW.append("circle").attr("cx", x).attr("cy", y).attr("r", 5).attr("fill", "#1F8A87"); }
    const m = wsMetrics(wsGraph(100, 6, p, mulberry(2024)));
    $("#wsC").textContent = pct(m.C / m0.C); $("#wsL").textContent = pct(m.L / m0.L); marcaW.attr("x1", xw(Math.max(p, 0.001))).attr("x2", xw(Math.max(p, 0.001)));
  }
  $("#wsP").oninput = desenhaWS; desenhaWS();

  /* ---------- conceitos ---------- */
  GLOS.forEach(([t, d]) => $("#glossario").insertAdjacentHTML("beforeend", `<div class="term"><b>${t}</b><small>${d}</small></div>`));
  $("#tabFis").innerHTML = "<tr><th>Módulo</th><th>Proteínas-chave</th><th>Fisiologia</th></tr>" + FISMOD.map(([m, p, f]) => `<tr><td><i class="tag" style="background:${COR[m]}">&nbsp;</i>${m}</td><td>${p}</td><td>${f}</td></tr>`).join("");

  /* ---------- inicialização ---------- */
  atualizaAtaque(); calcProt(false); desenhaProt(); rodaCascata();
  const secs = [...document.querySelectorAll("main section")], links = [...document.querySelectorAll("#nav a")];
  addEventListener("scroll", () => { let cur = secs[0].id; secs.forEach(s => { if (s.getBoundingClientRect().top < 120) cur = s.id; }); links.forEach(a => a.classList.toggle("on", a.getAttribute("href") === "#" + cur)); }, {passive: true});
})();
