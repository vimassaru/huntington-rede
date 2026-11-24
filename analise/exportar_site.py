"""Exporta os dados do projeto para o site (site/data/dados.json) e calcula estatisticas small-world / livre de escala."""
import csv, json, random
from pathlib import Path
import networkx as nx, numpy as np, pandas as pd

AQUI = Path(__file__).parent
SITE = AQUI.parent / ("docs" if (AQUI.parent / "docs").exists() else "site")
SAIDA = AQUI / "saida"
random.seed(7); np.random.seed(7)
nos = pd.read_csv(SAIDA / "nos_metricas.csv").set_index("no")
pos = pd.read_csv(SAIDA / "posicoes_cytoscape.csv").set_index("no")
G = nx.Graph(); arestas = []
with open(AQUI / "string_htt_score700.tsv", encoding="utf-8") as f:
    for l in csv.DictReader(f, delimiter="\t"):
        G.add_edge(l["preferredName_A"], l["preferredName_B"]); arestas.append([l["preferredName_A"], l["preferredName_B"], float(l["score"])])
px = pos["x"]; py = pos["y"]
sx = (px - px.mean()) / px.std(); sy = (py - py.mean()) / py.std()
nodes = [{"id": n, "modulo": r["modulo"], "grau": int(r["grau"]), "btw": float(r["betweenness"]), "art": bool(r["ponto_articulacao"]),
          "dEf": float(r["dEficiencia_%"]), "x": float(sx[n]), "y": float(sy[n])} for n, r in nos.iterrows()]

n, m = G.number_of_nodes(), G.number_of_edges()
C, L = nx.average_clustering(G), nx.average_shortest_path_length(G)
def stats(H):
    H = H.subgraph(max(nx.connected_components(H), key=len))
    return nx.average_clustering(H), nx.average_shortest_path_length(H)
er, cfg = [], []
deg = [d for _, d in G.degree()]
for _ in range(300):
    er.append(stats(nx.gnm_random_graph(n, m)))
    H = nx.Graph(nx.configuration_model(deg)); H.remove_edges_from(nx.selfloop_edges(H)); cfg.append(stats(H))
er = np.mean(er, axis=0); cfg = np.mean(cfg, axis=0)
sw = {"n": n, "m": m, "C": C, "L": L, "C_er": er[0], "L_er": er[1], "C_cfg": cfg[0], "L_cfg": cfg[1],
      "sigma_er": (C / er[0]) / (L / er[1]), "sigma_cfg": (C / cfg[0]) / (L / cfg[1]),
      "assort": nx.degree_assortativity_coefficient(G)}
# distribuicao de graus
cont = pd.Series(deg).value_counts().sort_index()
sw["graus"] = {int(k): int(v) for k, v in cont.items()}
# ajuste de potencia (MLE discreto simplificado, kmin=1 e kmin=3) para mostrar que nao e conclusivo
for kmin in (1, 3):
    d = np.array([x for x in deg if x >= kmin]); sw[f"alfa_kmin{kmin}"] = float(1 + len(d) / np.sum(np.log(d / (kmin - 0.5))))
print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in sw.items() if k != "graus"})

rob = pd.read_csv(SAIDA / "robustez_curvas.csv"); rob.columns = ["k", "rnd_lcc", "rnd_eff", "grau_lcc", "grau_eff", "btw_lcc", "btw_eff"]
prot = pd.read_csv(SAIDA / "protecao_resultados.csv").fillna("")
out = {"nodes": nodes, "edges": arestas, "smallworld": sw, "robustez": rob.round(4).to_dict("list"),
       "protecao": prot.round(3).to_dict("records")}
(SITE / "data").mkdir(parents=True, exist_ok=True)
js = json.dumps(out, ensure_ascii=False)
(SITE / "data" / "dados.json").write_text(js, encoding="utf-8")
(SITE / "data" / "dados.js").write_text("window.DADOS = " + js + ";", encoding="utf-8")  # carrega tambem via file://
import shutil
for f in ("nos_metricas.csv", "tabela_alvos.csv", "modulos_tabela.csv", "cascata_resumo.csv", "protecao_resultados.csv", "robustez_curvas.csv"):
    shutil.copy(SAIDA / f, SITE / "data" / f)
