"""Importa a rede do HTT no Cytoscape (via CyREST), aplica estilo e exporta figuras.

Pre-requisitos: Cytoscape aberto, pip install py4cytoscape, e ter rodado analise_robustez.py
(gera saida/nos_metricas.csv). Saidas em saida/: cy_rede_modulos.png e cy_rede_impacto.png.
"""
import csv
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd
import py4cytoscape as p4c
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

AQUI = Path(__file__).parent
SAIDA = AQUI / "saida"

nos = pd.read_csv(SAIDA / "nos_metricas.csv")
nos = nos.rename(columns={"no": "id", "dEficiencia_%": "dEficiencia", "ponto_articulacao": "articulacao"})
nos["articulacao"] = nos["articulacao"].astype(str)
arestas = []
with open(AQUI / "string_htt_score700.tsv", encoding="utf-8") as f:
    for l in csv.DictReader(f, delimiter="\t"):
        arestas.append({"source": l["preferredName_A"], "target": l["preferredName_B"],
                        "interaction": "interage", "weight": float(l["score"])})
arestas = pd.DataFrame(arestas)

CORES = {
    "Transporte intracelular": "#4C78A8",
    "Transcrição": "#F58518",
    "Sinalização de cálcio": "#54A24B",
    "Mitocôndria/estresse oxidativo": "#E45756",
    "Apoptose": "#B279A2",
    "Autofagia": "#72B7B2",
    "Astrócitos": "#9D755D",
    "HTT": "#111111",
}

p4c.cytoscape_ping()
p4c.create_network_from_data_frames(nodes=nos, edges=arestas, title="HTT_PPI", collection="Huntington")

DEFAULTS = {
    "NODE_SHAPE": "ELLIPSE",
    "NODE_BORDER_WIDTH": 2.5,
    "NODE_BORDER_PAINT": "#FFFFFF",
    "NODE_LABEL_COLOR": "#1a1a1a",
    "NODE_LABEL_FONT_FACE": "Arial,Bold,12",
    "NODE_LABEL_POSITION": "S,N,c,0.00,2.00",
    "EDGE_STROKE_UNSELECTED_PAINT": "#9AA5B1",
    "EDGE_TRANSPARENCY": 120,
    "EDGE_WIDTH": 2.0,
    "NETWORK_BACKGROUND_PAINT": "#FFFFFF",
}


def estilo(nome, extra_map):
    p4c.create_visual_style(nome, defaults=DEFAULTS, mappings=[
        p4c.map_visual_property("node label", "name", "p"),
        p4c.map_visual_property("node label font size", "betweenness", "c", [0, 0.4], [100, 150]),
        p4c.map_visual_property("edge transparency", "weight", "c", [0.7, 1.0], [70, 190]),
    ] + extra_map)
    p4c.set_visual_style(nome)


def layout():
    p4c.layout_network("force-directed defaultSpringLength=140 defaultSpringCoefficient=0.00004 "
                       "defaultNodeMass=4 numIterations=500")


# ---------------- figura 1: modulos (cor), betweenness (tamanho), HTT em destaque
estilo("HTT_modulos", [
    p4c.map_visual_property("node fill color", "modulo", "d", list(CORES), list(CORES.values())),
    p4c.map_visual_property("node size", "betweenness", "c", [0, 0.4], [34, 105]),
])
layout()
p4c.fit_content()
time.sleep(6)  # o Cytoscape precisa terminar de redesenhar antes da exportacao
p4c.export_image(str(SAIDA / "cy_rede_modulos_raw"), type="PNG", resolution=300, zoom=200, overwrite_file=True)

# ---------------- figura 2: impacto da remocao (cor), pontos de articulacao (losango)
estilo("HTT_impacto", [
    p4c.map_visual_property("node fill color", "dEficiencia", "c", [0, 3, 12], ["#F2F2F2", "#F6B26B", "#C0392B"]),
    p4c.map_visual_property("node size", "grau", "c", [1, 18], [34, 90]),
    p4c.map_visual_property("node shape", "articulacao", "d", ["True", "False"], ["DIAMOND", "ELLIPSE"]),
    p4c.map_visual_property("node border width", "articulacao", "d", ["True", "False"], [4.0, 1.5]),
    p4c.map_visual_property("node border paint", "articulacao", "d", ["True", "False"], ["#111111", "#9AA5B1"]),
])
p4c.fit_content()
time.sleep(6)
p4c.export_image(str(SAIDA / "cy_rede_impacto_raw"), type="PNG", resolution=300, zoom=200, overwrite_file=True)

p4c.save_session(str(SAIDA / "rede_HTT.cys"))

# ---------------- legendas (matplotlib) sobre as imagens exportadas
def recorta(caminho):
    from PIL import Image, ImageChops
    im = Image.open(caminho).convert("RGB")
    fundo = Image.new("RGB", im.size, (255, 255, 255))
    caixa = ImageChops.difference(im, fundo).getbbox()
    m = 20
    return im.crop((max(caixa[0] - m, 0), max(caixa[1] - m, 0), min(caixa[2] + m, im.width), min(caixa[3] + m, im.height)))


def com_legenda(raw, saida, handles, titulo, ncol=4):
    img = recorta(SAIDA / f"{raw}.png")
    w, h = img.size
    fig = plt.figure(figsize=(9, 9 * h / w + 1.0), dpi=200)
    altura_leg = 1.0 / (9 * h / w + 1.0)
    ax = fig.add_axes([0, altura_leg, 1, 1 - altura_leg])
    ax.imshow(img)
    ax.axis("off")
    fig.legend(handles=handles, loc="lower center", ncol=ncol, frameon=False, fontsize=10.5, title=titulo,
               title_fontsize=10.5, bbox_to_anchor=(0.5, 0.0))
    fig.savefig(SAIDA / saida, dpi=200, facecolor="white")
    plt.close(fig)


com_legenda("cy_rede_modulos_raw", "cy_rede_modulos.png",
            [Patch(facecolor=c, label=m) for m, c in CORES.items()],
            "Módulo funcional (tamanho do nó proporcional à betweenness)")
com_legenda("cy_rede_impacto_raw", "cy_rede_impacto.png",
            [Patch(facecolor="#F2F2F2", edgecolor="#9AA5B1", label="perda de eficiência ≈ 0%"),
             Patch(facecolor="#F6B26B", label="≈ 3%"),
             Patch(facecolor="#C0392B", label="≥ 12%"),
             Line2D([0], [0], marker="D", color="w", markerfacecolor="white", markeredgecolor="#111111",
                    markeredgewidth=2, markersize=8, label="ponto de articulação")],
            "Impacto da remoção do nó (tamanho proporcional ao grau)")
print("figuras geradas em", SAIDA)
