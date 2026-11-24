"""Estrategia de protecao: quais nos, se protegidos (nao podem falhar), mais contem a cascata?

Mesmo modelo de cascata do analise_robustez.py (um no falha quando a fracao de vizinhos falhos >= phi).
Compara: protecao aleatoria, por maior grau, por maior betweenness e escolha gulosa (minimiza o tamanho
medio da cascata sobre todas as sementes). Saidas: saida/protecao_resultados.csv e saida/fig_protecao.png.
"""
import csv
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

AQUI = Path(__file__).parent
SAIDA = AQUI / "saida"
random.seed(42)
plt.rcParams.update({"font.size": 13, "axes.titlesize": 14, "axes.labelsize": 13, "legend.fontsize": 11})

G = nx.Graph()
with open(AQUI / "string_htt_score700.tsv", encoding="utf-8") as f:
    for l in csv.DictReader(f, delimiter="\t"):
        G.add_edge(l["preferredName_A"], l["preferredName_B"])
nos = list(G)
N = len(nos)
grau = dict(G.degree())
btw = nx.betweenness_centrality(G)


def cascata(semente, phi, protegidos):
    falhos = {semente}
    mudou = True
    while mudou:
        mudou = False
        for n in nos:
            if n in falhos or n in protegidos:
                continue
            viz = list(G[n])
            if viz and sum(v in falhos for v in viz) / len(viz) >= phi:
                falhos.add(n)
                mudou = True
    return len(falhos)


def media(phi, protegidos):
    sementes = [n for n in nos if n not in protegidos]
    return float(np.mean([cascata(s, phi, protegidos) for s in sementes]))


def gulosa(phi, k):
    escolhidos = []
    for _ in range(k):
        cand = [n for n in nos if n not in escolhidos]
        melhor = min(cand, key=lambda n: media(phi, set(escolhidos) | {n}))
        escolhidos.append(melhor)
    return escolhidos


linhas = []
ordem_grau = sorted(nos, key=lambda n: -grau[n])
ordem_btw = sorted(nos, key=lambda n: -btw[n])
KS = [0, 1, 2, 3, 4, 5]
resultado = {}
for phi in (0.2, 0.3):
    base = media(phi, set())
    g = gulosa(phi, max(KS))
    resultado[phi] = g
    for k in KS:
        rnd = np.mean([media(phi, set(random.sample(nos, k))) for _ in range(40)]) if k else base
        linhas.append({"phi": phi, "k": k, "aleatoria": rnd, "grau": media(phi, set(ordem_grau[:k])),
                       "betweenness": media(phi, set(ordem_btw[:k])), "gulosa": media(phi, set(g[:k])),
                       "gulosa_nos": " ".join(g[:k])})
df = pd.DataFrame(linhas)
df.to_csv(SAIDA / "protecao_resultados.csv", index=False)

fig, ax = plt.subplots(1, 2, figsize=(10, 4.4), sharey=False)
for a, phi in zip(ax, (0.2, 0.3)):
    d = df[df["phi"] == phi]
    a.plot(d["k"], d["aleatoria"], "o-", color="#4c78a8", label="Aleatória", lw=2)
    a.plot(d["k"], d["grau"], "s-", color="#f58518", label="Maior grau", lw=2)
    a.plot(d["k"], d["betweenness"], "^-", color="#b279a2", label="Maior betweenness", lw=2)
    a.plot(d["k"], d["gulosa"], "D-", color="#e45756", label="Escolha gulosa", lw=2.5)
    a.set(xlabel="Proteínas protegidas (k)", ylabel="Nós que falham, em média (de 66)", title=f"Limiar φ = {phi}")
    a.grid(alpha=0.3)
ax[0].legend()
fig.tight_layout()
fig.savefig(SAIDA / "fig_protecao.png", dpi=170)

pd.set_option("display.width", 200)
print(df.round(2).to_string(index=False))
