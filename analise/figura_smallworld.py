"""Figura do slide de mundo pequeno: C e L da rede real vs. redes aleatorias (valores de site/data/dados.json)."""
import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
d = json.load(open("site/data/dados.json", encoding="utf-8"))["smallworld"]
cores = ["#1F8A87", "#8a96a3", "#F58518"]
nomes = ["Rede do HTT", "Erdős–Rényi", "Mesmos graus\n(configuração)"]
fig, ax = plt.subplots(1, 2, figsize=(11, 4.6), dpi=200)
for a, vals, tit, fmt in [(ax[0], [d["C"], d["C_er"], d["C_cfg"]], "Agrupamento (C)", "{:.2f}"),
                          (ax[1], [d["L"], d["L_er"], d["L_cfg"]], "Caminho médio (L)", "{:.2f}")]:
    b = a.bar(nomes, vals, color=cores, width=.6)
    a.set_title(tit, fontsize=17, fontweight="bold", color="#14213D")
    for r, v in zip(b, vals):
        a.text(r.get_x() + r.get_width()/2, v, fmt.format(v).replace(".", ","), ha="center", va="bottom", fontsize=15, fontweight="bold")
    a.set_ylim(0, max(vals) * 1.18)
    a.tick_params(axis="x", labelsize=12.5); a.tick_params(axis="y", labelsize=12)
    a.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:g}".replace(".", ",")))
    for s in ("top", "right"): a.spines[s].set_visible(False)
fig.text(.5, .01, "Aleatórias: média de 300 redes geradas (mesmo número de nós e arestas).", ha="center", fontsize=11, color="#52606D")
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig("dados/saida/fig_smallworld.png")
print("ok")
