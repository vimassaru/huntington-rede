"""Robustez e cascata de falha na rede PPI do HTT (Huntington).

Le dados/string_htt_score700.tsv (STRING, score >= 0,7) e gera, em dados/saida/:
  nos_metricas.csv        grau, betweenness, modulo, impacto da remocao e da cascata de cada no
  robustez_curvas.csv     curvas de remocao (aleatoria x ataque por grau x por betweenness)
  cascata_resumo.csv      tamanho medio da cascata por limiar
  fig_robustez.png        curvas de robustez
  fig_cascata.png         tamanho da cascata por limiar
  fig_impacto_nos.png     impacto individual dos nos mais criticos
  tabela_alvos.csv        nos candidatos a alvo, para a discussao

Suposicoes (declarar no trabalho):
  - rede nao direcionada e nao ponderada (a pontuacao do STRING so filtra as arestas);
  - cascata: um no falha quando a fracao de vizinhos ja falhos >= limiar (phi);
    o limiar e uma suposicao nossa, por isso testamos varios valores.
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
SAIDA.mkdir(exist_ok=True)
random.seed(42)
np.random.seed(42)
plt.rcParams.update({"font.size": 13, "axes.titlesize": 14, "axes.labelsize": 13, "legend.fontsize": 11})

# ---------------------------------------------------------------- rede e modulos
G = nx.Graph()
with open(AQUI / "string_htt_score700.tsv", encoding="utf-8") as f:
    for l in csv.DictReader(f, delimiter="\t"):
        G.add_edge(l["preferredName_A"], l["preferredName_B"], score=float(l["score"]))

MODULOS = {
    "Transporte intracelular": "BMERB1 DCTN1 DCTN4 DCTN5 DCTN6 DNM1 HAP1 HIP1 KIF5A KLC4",
    "Transcrição": "BRMS1 CREBBP GSE1 HDAC1 PHF21B RCOR1 REST SAP30 SAP30L SIN3A",
    "Sinalização de cálcio": "CAMK2D DLG4 GRM1 GRM5 HOMER1 HOMER2 HOMER3 ITPR1 PLCB1 STX1A",
    "Mitocôndria/estresse oxidativo": "GABPB1 GPX5 GPX6 NRF1 PPARGC1A SOD1 SOD2 TFAM UCP3",
    "Apoptose": "BAD BAX BBC3 BCL2L2 BID CASP3 CASP9 HRK RTL10 TP53",
    "Autofagia": "ATG101 ATG14 BECN1 BECN2 MTOR NRBF2 PIK3C3 RUBCN ULK1 ULK2",
    "Astrócitos": "ALDH1L1 GJB6 KCNJ10 MLC1 SLC1A2 SLC1A3 SLC6A11 SLC6A13",
    "HTT": "HTT",
}
modulo_de = {p: m for m, ps in MODULOS.items() for p in ps.split()}
assert set(G) <= set(modulo_de), set(G) - set(modulo_de)
nx.set_node_attributes(G, modulo_de, "modulo")
N = G.number_of_nodes()


def lcc_frac(H):
    return max((len(c) for c in nx.connected_components(H)), default=0) / N


def efic(H):
    return nx.global_efficiency(H) if H.number_of_nodes() > 1 else 0.0


# ---------------------------------------------------------------- 1. metricas basicas
grau = dict(G.degree())
btw = nx.betweenness_centrality(G)
articulacao = set(nx.articulation_points(G))
print(f"nos={N} arestas={G.number_of_edges()} pontos de articulacao={sorted(articulacao)}")

# ---------------------------------------------------------------- 2. remocao sequencial
PASSOS = 25  # remover ate 25 nos (~38% da rede)


def curva(H0, ordem_fn, rep=1):
    """Maior componente (fracao de N) e eficiencia global depois de remover k nos."""
    res_l, res_e = np.zeros((rep, PASSOS + 1)), np.zeros((rep, PASSOS + 1))
    for r in range(rep):
        H = H0.copy()
        res_l[r, 0], res_e[r, 0] = lcc_frac(H), efic(H)
        for k in range(1, PASSOS + 1):
            H.remove_node(ordem_fn(H))
            res_l[r, k], res_e[r, k] = lcc_frac(H), efic(H)
    return res_l.mean(0), res_e.mean(0), res_l.std(0), res_e.std(0)


def alvo_grau(H):
    return max(H.nodes, key=lambda n: (H.degree(n), n))


def alvo_btw(H):
    b = nx.betweenness_centrality(H)
    return max(b, key=lambda n: (b[n], n))


def alvo_aleatorio(H):
    return random.choice(list(H.nodes))


curvas = {
    "Aleatória (média de 200)": curva(G, alvo_aleatorio, rep=200),
    "Ataque por grau": curva(G, alvo_grau),
    "Ataque por betweenness": curva(G, alvo_btw),
}
pd.DataFrame(
    {"k_removidos": range(PASSOS + 1)}
    | {f"{nome} | {met}": curvas[nome][i] for nome in curvas for i, met in enumerate(["LCC", "Eficiencia"])}
).to_csv(SAIDA / "robustez_curvas.csv", index=False)

fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
cores = {"Aleatória (média de 200)": "#4c78a8", "Ataque por grau": "#e45756", "Ataque por betweenness": "#f58518"}
for nome, (l, e, ls, es) in curvas.items():
    ax[0].plot(range(PASSOS + 1), l, label=nome, color=cores[nome], lw=2)
    ax[1].plot(range(PASSOS + 1), e, label=nome, color=cores[nome], lw=2)
    if "Aleatória" in nome:
        ax[0].fill_between(range(PASSOS + 1), l - ls, l + ls, color=cores[nome], alpha=0.2)
        ax[1].fill_between(range(PASSOS + 1), e - es, e + es, color=cores[nome], alpha=0.2)
ax[0].set(xlabel="Nós removidos", ylabel="Maior componente conexo (fração de 66)", title="Fragmentação")
ax[1].set(xlabel="Nós removidos", ylabel="Eficiência global", title="Perda de comunicação")
ax[0].legend()
for a in ax:
    a.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(SAIDA / "fig_robustez.png", dpi=160)
plt.close(fig)

# ---------------------------------------------------------------- 3. impacto de cada no
E0 = efic(G)
impacto = {}
for n in G:
    H = G.copy()
    H.remove_node(n)
    impacto[n] = {
        "dEficiencia_%": 100 * (E0 - efic(H)) / E0,
        "LCC_apos": lcc_frac(H) * N,
    }

# ---------------------------------------------------------------- 4. cascata por limiar
LIMIARES = [0.2, 0.3, 0.4, 0.5]


def cascata(H, semente, phi):
    falhos = {semente}
    mudou = True
    while mudou:
        mudou = False
        for n in H:
            if n in falhos:
                continue
            viz = list(H[n])
            if viz and sum(v in falhos for v in viz) / len(viz) >= phi:
                falhos.add(n)
                mudou = True
    return falhos


casc = {phi: {n: cascata(G, n, phi) for n in G} for phi in LIMIARES}
resumo = []
for phi in LIMIARES:
    tam = {n: len(casc[phi][n]) for n in G}
    hubs = [n for n, _ in sorted(grau.items(), key=lambda x: -x[1])[:5]]
    resumo.append(
        {
            "limiar_phi": phi,
            "media_todos": np.mean(list(tam.values())),
            "media_top5_grau": np.mean([tam[n] for n in hubs]),
            "maximo": max(tam.values()),
            "no_maximo": max(tam, key=tam.get),
            "sementes_que_derrubam_>50%": sum(t > N / 2 for t in tam.values()),
        }
    )
pd.DataFrame(resumo).to_csv(SAIDA / "cascata_resumo.csv", index=False)

fig, ax = plt.subplots(figsize=(5.6, 4.6))
x = np.arange(len(LIMIARES))
ax.bar(x - 0.2, [r["media_todos"] for r in resumo], 0.4, label="Média de todos os nós", color="#4c78a8")
ax.bar(x + 0.2, [r["media_top5_grau"] for r in resumo], 0.4, label="Média dos 5 maiores hubs", color="#e45756")
ax.set_xticks(x, [str(p) for p in LIMIARES])
ax.set(xlabel="Limiar φ", ylabel="Nós que falham (de 66)", title="Tamanho da cascata")
ax.legend()
ax.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(SAIDA / "fig_cascata.png", dpi=160)
plt.close(fig)

# ---------------------------------------------------------------- 5. tabela dos nos
PHI_REF = 0.3
linhas = []
for n in G:
    linhas.append(
        {
            "no": n,
            "modulo": modulo_de[n],
            "grau": grau[n],
            "betweenness": round(btw[n], 4),
            "ponto_articulacao": n in articulacao,
            "dEficiencia_%": round(impacto[n]["dEficiencia_%"], 2),
            "LCC_apos_remocao": int(impacto[n]["LCC_apos"]),
            f"cascata_phi{PHI_REF}": len(casc[PHI_REF][n]),
            f"modulos_atingidos_phi{PHI_REF}": len({modulo_de[v] for v in casc[PHI_REF][n]}),
        }
    )
df = pd.DataFrame(linhas).sort_values("dEficiencia_%", ascending=False)
df.to_csv(SAIDA / "nos_metricas.csv", index=False)

top = df.head(12).iloc[::-1]
fig, ax = plt.subplots(figsize=(5.6, 4.6))
ax.barh(top["no"], top["dEficiencia_%"], color="#e45756")
ax.set(xlabel="Perda de eficiência global (%)", title="Nós mais críticos")
ax.grid(alpha=0.3, axis="x")
fig.tight_layout()
fig.savefig(SAIDA / "fig_impacto_nos.png", dpi=160)
plt.close(fig)

# tabela de alvos: criticos pelos dois criterios (impacto e cascata)
alvos = df.sort_values(["dEficiencia_%", f"cascata_phi{PHI_REF}"], ascending=False).head(10)
alvos.to_csv(SAIDA / "tabela_alvos.csv", index=False)

print("\n== Curvas (apos remover 5 e 10 nos) ==")
for nome, (l, e, _, _) in curvas.items():
    print(f"{nome:28s} LCC k=5: {l[5]:.2f}  k=10: {l[10]:.2f} | Efic k=5: {e[5]:.3f}  k=10: {e[10]:.3f}")
print("\n== Top 10 por perda de eficiencia ==")
print(df.head(10).to_string(index=False))
print("\n== Cascata ==")
print(pd.DataFrame(resumo).to_string(index=False))


# ---------------------------------------------------------------- 6. modularidade
from networkx.algorithms import community as nxc

particao = [set(n for n in G if modulo_de[n] == m) for m in MODULOS]
Q_func = nxc.modularity(G, particao)
louvain = nxc.louvain_communities(G, seed=42)
Q_louv = nxc.modularity(G, louvain)
linhas_m = []
for m, ps in zip(MODULOS, particao):
    interno = G.subgraph(ps).number_of_edges()
    externo = sum(1 for u, v in G.edges if (u in ps) != (v in ps) and (u in ps or v in ps))
    linhas_m.append({"modulo": m, "nos": len(ps), "grau_medio": round(sum(grau[n] for n in ps) / len(ps), 1),
                     "arestas_internas": interno, "arestas_para_fora": externo,
                     "proteinas": " ".join(sorted(ps, key=lambda n: -grau[n]))})
pd.DataFrame(linhas_m).to_csv(SAIDA / "modulos_tabela.csv", index=False)
intra = sum(r["arestas_internas"] for r in linhas_m)
print(f"Modularidade Q (modulos funcionais) = {Q_func:.3f}; Louvain = {Q_louv:.3f} ({len(louvain)} comunidades)")
print(f"Arestas dentro dos modulos: {intra} de {G.number_of_edges()} ({100*intra/G.number_of_edges():.0f}%)")
print(pd.DataFrame(linhas_m).drop(columns="proteinas").to_string(index=False))

# ---------------------------------------------------------------- 7. grau x betweenness
cor_mod = {"Transporte intracelular": "#4C78A8", "Transcrição": "#F58518", "Sinalização de cálcio": "#54A24B",
           "Mitocôndria/estresse oxidativo": "#E45756", "Apoptose": "#B279A2", "Autofagia": "#72B7B2",
           "Astrócitos": "#9D755D", "HTT": "#111111"}
fig, ax = plt.subplots(1, 2, figsize=(10, 4.4), gridspec_kw={"width_ratios": [1, 1.25]})
ax[0].hist(list(grau.values()), bins=range(0, 21), color="#4C78A8", edgecolor="white")
ax[0].set(xlabel="Grau (nº de conexões)", ylabel="Nº de proteínas", title="(a) Distribuição de graus")
for n in G:
    ax[1].scatter(grau[n], btw[n], s=60, color=cor_mod[modulo_de[n]], edgecolor="white", lw=0.8, zorder=3)
for n in ["HTT", "TP53", "SLC1A2", "PPARGC1A", "HDAC1", "BECN1", "MTOR"]:
    dx, dy = {"HTT": (-1.2, 0.02), "TP53": (0.3, 0.012)}.get(n, (0.35, 0.006))
    ax[1].annotate(n, (grau[n], btw[n]), xytext=(grau[n] + dx, btw[n] + dy), fontsize=11)
ax[1].set(xlabel="Grau", ylabel="Betweenness", title="(b) Grau × betweenness")
ax[1].grid(alpha=0.3)
fig.tight_layout()
fig.savefig(SAIDA / "fig_grau.png", dpi=170)
plt.close(fig)
