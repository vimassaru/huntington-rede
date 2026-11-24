"""Desenha a rede do HTT com o layout calculado no Cytoscape (saida/posicoes_cytoscape.csv),
com rotulos legiveis no tamanho do relatorio. Saidas: saida/rede_modulos.png e saida/rede_impacto.png."""
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from adjustText import adjust_text
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

AQUI = Path(__file__).parent
SAIDA = AQUI / "saida"
nos = pd.read_csv(SAIDA / "nos_metricas.csv").set_index("no")
pos = pd.read_csv(SAIDA / "posicoes_cytoscape.csv").set_index("no")
G = nx.Graph()
with open(AQUI / "string_htt_score700.tsv", encoding="utf-8") as f:
    for l in csv.DictReader(f, delimiter="\t"):
        G.add_edge(l["preferredName_A"], l["preferredName_B"], score=float(l["score"]))
P = {n: (pos.loc[n, "x"], -pos.loc[n, "y"]) for n in G}  # o eixo y do Cytoscape cresce para baixo

CORES = {"Transporte intracelular": "#4C78A8", "Transcrição": "#F58518", "Sinalização de cálcio": "#54A24B",
         "Mitocôndria/estresse oxidativo": "#E45756", "Apoptose": "#B279A2", "Autofagia": "#72B7B2",
         "Astrócitos": "#9D755D", "HTT": "#111111"}
DESTAQUE = {"HTT", "TP53", "SLC1A2", "PPARGC1A", "HDAC1", "BECN1", "MTOR"}


def desenha(saida, cor_fn, tam_fn, forma_fn, handles, titulo, ncol, figsize=(9, 9.2)):
    fig, ax = plt.subplots(figsize=figsize)
    for u, v, d in G.edges(data=True):
        ax.plot([P[u][0], P[v][0]], [P[u][1], P[v][1]], color="#8A96A3", lw=0.8 + 1.2 * (d["score"] - 0.7) / 0.3,
                alpha=0.35, zorder=1)
    for n in G:
        marc = forma_fn(n)
        ax.scatter(*P[n], s=tam_fn(n), color=cor_fn(n), marker=marc[0], edgecolor=marc[1], linewidth=marc[2],
                   zorder=3)
    textos = [ax.text(P[n][0], P[n][1], n, fontsize=11 if n in DESTAQUE else 9, fontweight="bold" if n in DESTAQUE
                      else "normal", color="#111", zorder=5) for n in G if n != "HTT"]
    ax.text(*P["HTT"], "HTT", fontsize=12, fontweight="bold", color="white" if cor_fn("HTT") == "#111111" else "#111",
            ha="center", va="center", zorder=6)
    outros = [n for n in G if n != "HTT"]
    adjust_text(textos, x=[P[n][0] for n in outros], y=[P[n][1] for n in outros], ax=ax, expand=(1.15, 1.3),
                arrowprops=dict(arrowstyle="-", color="#999", lw=0.5), time_lim=6)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.legend(handles=handles, loc="lower center", ncol=ncol, frameon=False, fontsize=10.5, title=titulo,
               title_fontsize=10.5)
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    fig.savefig(SAIDA / saida, dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


# figura 1: modulos (cor) e betweenness (tamanho)
desenha("rede_modulos.png", lambda n: CORES[nos.loc[n, "modulo"]],
        lambda n: 90 + 2600 * nos.loc[n, "betweenness"], lambda n: ("o", "white", 1.2),
        [Patch(facecolor=c, label=m) for m, c in CORES.items()],
        "Módulo funcional (tamanho do nó proporcional à betweenness)", 3)

# figura 2: impacto da remocao (cor) e pontos de articulacao (losango)
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("imp", ["#F2F2F2", "#F6B26B", "#C0392B"])
norm = matplotlib.colors.Normalize(0, 12)
desenha("rede_impacto.png", lambda n: cmap(norm(nos.loc[n, "dEficiencia_%"])),
        lambda n: 120 + 18 * nos.loc[n, "grau"] ** 1.35,
        lambda n: ("D", "#111", 2.2) if bool(nos.loc[n, "ponto_articulacao"]) else ("o", "#9AA5B1", 1.0),
        [Patch(facecolor="#F2F2F2", edgecolor="#9AA5B1", label="perda de eficiência ≈ 0%"),
         Patch(facecolor="#F6B26B", label="≈ 6%"), Patch(facecolor="#C0392B", label="≥ 12%"),
         Line2D([0], [0], marker="D", color="w", markerfacecolor="white", markeredgecolor="#111",
                markeredgewidth=2, markersize=9, label="ponto de articulação")],
        "Impacto da remoção do nó (tamanho proporcional ao grau)", 2)

# versao em paisagem (layout girado 90 graus) para os slides
P = {n: (-y, x) for n, (x, y) in P.items()}
HAND_M = [Patch(facecolor=c, label=m) for m, c in CORES.items()]
desenha("rede_modulos_h.png", lambda n: CORES[nos.loc[n, "modulo"]], lambda n: 90 + 2600 * nos.loc[n, "betweenness"],
        lambda n: ("o", "white", 1.2), HAND_M, "Módulo funcional (tamanho do nó proporcional à betweenness)", 4, figsize=(12, 8))
desenha("rede_impacto_h.png", lambda n: cmap(norm(nos.loc[n, "dEficiencia_%"])), lambda n: 120 + 18 * nos.loc[n, "grau"] ** 1.35,
        lambda n: ("D", "#111", 2.2) if bool(nos.loc[n, "ponto_articulacao"]) else ("o", "#9AA5B1", 1.0),
        [Patch(facecolor="#F2F2F2", edgecolor="#9AA5B1", label="perda de eficiência ≈ 0%"),
         Patch(facecolor="#F6B26B", label="≈ 6%"), Patch(facecolor="#C0392B", label="≥ 12%"),
         Line2D([0], [0], marker="D", color="w", markerfacecolor="white", markeredgecolor="#111",
                markeredgewidth=2, markersize=9, label="ponto de articulação")],
        "Impacto da remoção do nó (tamanho proporcional ao grau)", 4, figsize=(12, 8))
print("ok")
